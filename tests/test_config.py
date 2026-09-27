from pathlib import Path

import pytest

from my_aur.config import ConfigError, enabled_packages, load_registry

ROOT = Path(__file__).parents[1]


def test_real_repository_declarations_are_valid():
    packages = enabled_packages(ROOT)
    assert [package.name for package in packages] == ["mrrss-bin"]
    assert packages[0].monitor.repository == "DevXDojo/MrRSS"


def test_selected_package_must_be_enabled(tmp_path):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/packages.toml").write_text(
        "schema = 1\n[packages]\nfoo-bin = false\n", encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="disabled"):
        enabled_packages(tmp_path, "foo-bin")


def test_registry_rejects_unknown_top_level_field(tmp_path):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/packages.toml").write_text(
        "schema = 1\nunknown = true\n[packages]\n", encoding="utf-8"
    )
    with pytest.raises(ConfigError, match="expected only"):
        load_registry(tmp_path)
