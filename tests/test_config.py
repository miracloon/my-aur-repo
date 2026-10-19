from pathlib import Path

import pytest
from conftest import REAL_ROOT

from my_aur.config import ConfigError, enabled_packages, load_registry


def test_real_repository_declarations_are_valid():
    """Assert invariants of the real registry, never its concrete package set.

    Package names and versions change whenever automation follows upstream, so
    pinning them here would turn routine version bumps into red CI runs.
    """
    packages = enabled_packages(REAL_ROOT)
    assert packages, "at least one package must stay enabled"
    assert [package.name for package in packages] == sorted(package.name for package in packages)
    for package in packages:
        assert package.directory.name == package.name
        assert package.monitor.type == "github_release"
        assert "/" in package.monitor.repository
        assert "{version}" in package.monitor.asset or package.monitor.asset
        assert package.monitor.prerelease is False


def test_registry_and_package_declarations_agree():
    registry = load_registry(REAL_ROOT)
    enabled = {name for name, flag in registry.items() if flag}
    assert {package.name for package in enabled_packages(REAL_ROOT)} == enabled


def test_selected_package_must_be_enabled(synthetic_repository):
    synthetic_repository.add_package("foo-bin", enabled=False)
    with pytest.raises(ConfigError, match="disabled"):
        enabled_packages(synthetic_repository.root, "foo-bin")


def test_unregistered_selection_is_rejected(synthetic_repository):
    synthetic_repository.add_package("foo-bin")
    with pytest.raises(ConfigError, match="not registered"):
        enabled_packages(synthetic_repository.root, "missing-bin")


def test_pkgname_must_match_directory(synthetic_repository, tmp_path: Path):
    directory = synthetic_repository.add_package("foo-bin")
    (directory / "PKGBUILD").write_text(
        "pkgname=other-bin\npkgver=1.0.0\npkgrel=1\n", encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="does not match"):
        enabled_packages(synthetic_repository.root, "foo-bin")


def test_registry_rejects_unknown_top_level_field(tmp_path):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/packages.toml").write_text(
        "schema = 1\nunknown = true\n[packages]\n", encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="expected only"):
        load_registry(tmp_path)
