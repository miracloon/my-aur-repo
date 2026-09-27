"""Load and strictly validate the root registry and per-package declarations."""

import json
import re
import tomllib
from pathlib import Path

from jsonschema import Draft202012Validator

from .models import MonitorConfig, PackageConfig
from .pkgbuild import read_scalars

_PACKAGE_NAME = re.compile(r"^[a-z0-9][a-z0-9@._+\-]*$")


class ConfigError(ValueError):
    """Raised when repository declarations violate their schema or cross-file contract."""


def repository_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "registry/packages.toml").is_file():
            return candidate
    raise ConfigError("could not locate repository root containing registry/packages.toml")


def load_registry(root: Path) -> dict[str, bool]:
    path = root / "registry/packages.toml"
    with path.open("rb") as handle:
        data = tomllib.load(handle)
    if set(data) != {"schema", "packages"} or data["schema"] != 1:
        raise ConfigError(f"{path}: expected only schema=1 and [packages]")
    packages = data["packages"]
    if not isinstance(packages, dict):
        raise ConfigError(f"{path}: [packages] must be a table")
    for name, enabled in packages.items():
        if not _PACKAGE_NAME.fullmatch(name) or not isinstance(enabled, bool):
            raise ConfigError(f"{path}: invalid package entry {name!r}={enabled!r}")
    return packages


def load_package(root: Path, name: str) -> PackageConfig:
    directory = root / "packages" / name
    declaration = directory / "package.toml"
    pkgbuild = directory / "PKGBUILD"
    if not declaration.is_file() or not pkgbuild.is_file():
        raise ConfigError(f"{name}: package.toml and PKGBUILD are both required")

    with declaration.open("rb") as handle:
        data = tomllib.load(handle)
    schema_path = root / "schemas/package-v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(data),
        key=lambda item: list(item.path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ConfigError(f"{declaration}: {details}")

    scalars = read_scalars(pkgbuild)
    if scalars["pkgname"] != name:
        raise ConfigError(f"{pkgbuild}: pkgname={scalars['pkgname']} does not match {name}")

    monitor = data["monitor"]
    return PackageConfig(
        name=name,
        directory=directory,
        monitor=MonitorConfig(
            type=monitor["type"],
            repository=monitor["repository"],
            prerelease=monitor["prerelease"],
            asset=monitor["asset"],
        ),
    )


def enabled_packages(root: Path, selected: str | None = None) -> list[PackageConfig]:
    registry = load_registry(root)
    if selected:
        if selected not in registry:
            raise ConfigError(f"package is not registered: {selected}")
        if not registry[selected]:
            raise ConfigError(f"package is disabled: {selected}")
        names = [selected]
    else:
        names = sorted(name for name, enabled in registry.items() if enabled)
    return [load_package(root, name) for name in names]
