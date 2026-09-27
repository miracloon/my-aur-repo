from pathlib import Path

import pytest

from my_aur.pkgbuild import PkgbuildError, read_scalars, read_version, update_upstream_version


def write_pkgbuild(path: Path, version: str = "1.2.3", release: str = "4") -> None:
    path.write_text(
        f"pkgname=demo-bin\npkgver={version}\npkgrel={release}\nsource=()\n",
        encoding="utf-8",
    )


def test_read_scalars_and_version(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    assert read_scalars(path)["pkgname"] == "demo-bin"
    assert read_version(path).full == "1.2.3-4"


def test_new_upstream_version_resets_pkgrel(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    assert update_upstream_version(path, "1.3.0") is True
    assert read_version(path).full == "1.3.0-1"


def test_same_version_is_unchanged(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    before = path.read_text(encoding="utf-8")
    assert update_upstream_version(path, "1.2.3") is False
    assert path.read_text(encoding="utf-8") == before


def test_version_regression_is_rejected(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    with pytest.raises(PkgbuildError, match="regression"):
        update_upstream_version(path, "1.2.2")
