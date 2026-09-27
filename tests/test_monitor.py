from pathlib import Path

import pytest

from my_aur.models import MonitorConfig, PackageConfig
from my_aur.monitor import MonitorError, normalize_release_version, resolve_release


class FakeGitHub:
    def __init__(self, release):
        self._release = release

    def latest_release(self, repository):
        assert repository == "owner/project"
        return self._release


def package() -> PackageConfig:
    return PackageConfig(
        name="demo-bin",
        directory=Path("packages/demo-bin"),
        monitor=MonitorConfig(
            type="github_release",
            repository="owner/project",
            prerelease=False,
            asset="Demo-{version}-linux-amd64.tar.gz",
        ),
    )


def release(tag="v1.2.3", assets=None, prerelease=False):
    return {
        "tag_name": tag,
        "draft": False,
        "prerelease": prerelease,
        "assets": assets
        or [
            {
                "name": "Demo-1.2.3-linux-amd64.tar.gz",
                "browser_download_url": "https://example.invalid/demo.tar.gz",
                "digest": "sha256:abc",
            }
        ],
    }


def test_normalize_release_version():
    assert normalize_release_version("v1.2.3") == "1.2.3"
    assert normalize_release_version("1.2.3-stable") == "1.2.3_stable"


def test_resolve_stable_release_asset():
    identity = resolve_release(package(), FakeGitHub(release()))
    assert identity.version == "1.2.3"
    assert identity.asset_name == "Demo-1.2.3-linux-amd64.tar.gz"
    assert identity.digest == "sha256:abc"


def test_missing_asset_fails_explicitly():
    with pytest.raises(MonitorError, match="found 0"):
        resolve_release(package(), FakeGitHub(release(assets=[{"name": "other"}])))


def test_prerelease_is_not_accepted():
    with pytest.raises(MonitorError, match="not eligible"):
        resolve_release(package(), FakeGitHub(release(prerelease=True)))
