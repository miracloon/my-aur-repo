"""Read and update the small set of scalar fields owned by package automation."""

import re
from pathlib import Path

from packaging.version import InvalidVersion, Version

from .models import PackageVersion

_ASSIGNMENT = re.compile(
    r"^(?P<key>pkgname|pkgver|pkgrel)=(?P<quote>['\"]?)(?P<value>[^'\"\s]+)(?P=quote)$",
    re.MULTILINE,
)


class PkgbuildError(ValueError):
    """Raised when a PKGBUILD does not satisfy the automation contract."""


def read_scalars(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    values = {match.group("key"): match.group("value") for match in _ASSIGNMENT.finditer(text)}
    missing = {"pkgname", "pkgver", "pkgrel"} - values.keys()
    if missing:
        raise PkgbuildError(f"{path}: missing scalar assignments: {', '.join(sorted(missing))}")
    return values


def read_version(path: Path) -> PackageVersion:
    values = read_scalars(path)
    return PackageVersion(pkgver=values["pkgver"], pkgrel=values["pkgrel"])


def _replace_scalar(text: str, key: str, value: str) -> str:
    pattern = re.compile(rf"^{key}=.*$", re.MULTILINE)
    updated, count = pattern.subn(f"{key}={value}", text, count=1)
    if count != 1:
        raise PkgbuildError(f"expected one {key}= assignment, found {count}")
    return updated


def update_upstream_version(path: Path, target: str) -> bool:
    values = read_scalars(path)
    current = values["pkgver"]
    if current == target:
        return False
    try:
        if Version(target) <= Version(current):
            raise PkgbuildError(f"upstream version regression: {target} <= {current}")
    except InvalidVersion as error:
        raise PkgbuildError(f"github_release version is not comparable: {target}") from error

    text = path.read_text(encoding="utf-8")
    text = _replace_scalar(text, "pkgver", target)
    text = _replace_scalar(text, "pkgrel", "1")
    path.write_text(text, encoding="utf-8")
    return True
