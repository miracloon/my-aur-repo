"""Read and update the small set of scalar fields owned by package automation."""

import re
from pathlib import Path

from packaging.version import InvalidVersion, Version

from .models import PackageVersion

# `_tag` and `_source_url` carry the resolved upstream release identity. The
# updater writes them so recipes never re-derive tag prefixes or asset names.
RELEASE_SCALARS = ("_tag", "_source_url")

_ASSIGNMENT = re.compile(
    rf"^(?P<key>pkgname|pkgver|pkgrel|{'|'.join(RELEASE_SCALARS)})="
    r"(?P<quote>['\"]?)(?P<value>[^'\"\s]+)(?P=quote)$",
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


def update_release(path: Path, *, version: str, tag: str, asset_url: str) -> bool:
    """Write the resolved upstream release identity into a PKGBUILD.

    Every release scalar the recipe declares is refreshed; a package that does
    not consume one keeps no dead field.
    """
    values = read_scalars(path)
    current = values["pkgver"]
    text = path.read_text(encoding="utf-8")
    updated = text
    if current != version:
        try:
            if Version(version) <= Version(current):
                raise PkgbuildError(f"upstream version regression: {version} <= {current}")
        except InvalidVersion as error:
            raise PkgbuildError(f"github_release version is not comparable: {version}") from error
        updated = _replace_scalar(updated, "pkgver", version)
        updated = _replace_scalar(updated, "pkgrel", "1")

    for key, value in (("_tag", tag), ("_source_url", asset_url)):
        if key in values and values[key] != value:
            updated = _replace_scalar(updated, key, value)

    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True
