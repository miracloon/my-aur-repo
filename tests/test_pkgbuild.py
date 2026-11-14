from pathlib import Path

import pytest

from my_aur.pkgbuild import PkgbuildError, read_scalars, read_version, update_release

TAG = "v1.3.0"
ASSET_URL = "https://example.invalid/demo-1.3.0-linux-amd64.tar.gz"


def write_pkgbuild(
    path: Path,
    version: str = "1.2.3",
    release: str = "4",
    release_identity: bool = True,
) -> None:
    identity = f"_tag={TAG}\n_source_url={ASSET_URL}\n" if release_identity else ""
    path.write_text(
        f"pkgname=demo-bin\npkgver={version}\npkgrel={release}\n{identity}source=()\n",
        encoding="utf-8",
    )


def test_read_scalars_and_version(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    scalars = read_scalars(path)
    assert scalars["pkgname"] == "demo-bin"
    assert scalars["_source_url"] == ASSET_URL
    assert read_version(path).full == "1.2.3-4"


def test_new_upstream_version_resets_pkgrel_and_identity(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    assert (
        update_release(
            path,
            version="1.3.0",
            tag="v1.3.0",
            asset_url="https://example.invalid/demo-1.3.0-linux-amd64.tar.gz",
        )
        is True
    )
    assert read_version(path).full == "1.3.0-1"
    assert read_scalars(path)["_tag"] == "v1.3.0"


def test_same_release_is_unchanged(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    before = path.read_text(encoding="utf-8")
    assert update_release(path, version="1.2.3", tag=TAG, asset_url=ASSET_URL) is False
    assert path.read_text(encoding="utf-8") == before


def test_moved_asset_refreshes_identity_without_touching_pkgrel(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    moved = "https://example.invalid/demo-1.2.3-linux-amd64.deb"
    assert update_release(path, version="1.2.3", tag=TAG, asset_url=moved) is True
    assert read_scalars(path)["_source_url"] == moved
    assert read_version(path).full == "1.2.3-4"


def test_undeclared_identity_is_not_added(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path, release_identity=False)
    assert update_release(path, version="1.3.0", tag=TAG, asset_url=ASSET_URL) is True
    assert set(read_scalars(path)) == {"pkgname", "pkgver", "pkgrel"}


def test_version_regression_is_rejected(tmp_path):
    path = tmp_path / "PKGBUILD"
    write_pkgbuild(path)
    with pytest.raises(PkgbuildError, match="regression"):
        update_release(path, version="1.2.2", tag=TAG, asset_url=ASSET_URL)
