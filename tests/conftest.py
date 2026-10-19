"""Hermetic test doubles.

Tests must never bind to the real registry, the real package set or the real
upstream versions. The daily automation rewrites ``packages/<name>/PKGBUILD``,
so any test that reads those files turns every upstream bump into a red
scheduled run. Build a synthetic repository under ``tmp_path`` instead.
"""

import shutil
from pathlib import Path
from typing import Any

import pytest

REAL_ROOT = Path(__file__).parents[1]
REPOSITORY = "miracloon/my-aur-repo"
REPOSITORY_TAG = "repository-x86_64"
DEFAULT_ASSET = "Demo-{version}-linux-amd64.tar.gz"


def make_release(version: str, asset: str | None = None) -> dict[str, Any]:
    """Stable upstream release carrying exactly the asset the monitor expects."""
    name = asset or f"Demo-{version}-linux-amd64.tar.gz"
    return {
        "tag_name": f"v{version}",
        "draft": False,
        "prerelease": False,
        "assets": [
            {
                "name": name,
                "browser_download_url": f"https://example.invalid/{name}",
                "digest": "sha256:0000",
            }
        ],
    }


class SyntheticRepository:
    """A throwaway repository root that satisfies the real declaration contract."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.packages: dict[str, bool] = {}
        shutil.copytree(REAL_ROOT / "schemas", root / "schemas")
        (root / "registry").mkdir(parents=True, exist_ok=True)

    def add_package(
        self,
        name: str,
        *,
        pkgver: str = "1.0.0",
        pkgrel: str = "1",
        repository: str = "owner/project",
        asset: str = DEFAULT_ASSET,
        enabled: bool = True,
    ) -> Path:
        directory = self.root / "packages" / name
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "PKGBUILD").write_text(
            f"pkgname={name}\npkgver={pkgver}\npkgrel={pkgrel}\nsource=()\n",
            encoding="utf-8",
        )
        (directory / "package.toml").write_text(
            "schema = 1\n\n[monitor]\n"
            'type = "github_release"\n'
            f'repository = "{repository}"\n'
            "prerelease = false\n"
            f'asset = "{asset}"\n',
            encoding="utf-8",
        )
        self.packages[name] = enabled
        lines = ["schema = 1", "", "[packages]"]
        lines.extend(f"{entry} = {str(flag).lower()}" for entry, flag in self.packages.items())
        (self.root / "registry/packages.toml").write_text("\n".join(lines) + "\n", encoding="utf-8")
        return directory


class FakeGitHub:
    """GitHub stub covering repository assets, upstream releases and failure issues."""

    def __init__(
        self,
        releases: dict[str, dict[str, Any]] | None = None,
        published: tuple[str, ...] = (),
    ) -> None:
        self.releases = releases or {}
        self.published = set(published)
        self.issue_list: list[dict[str, Any]] = []

    def release(self, repository: str, tag: str) -> dict[str, Any] | None:
        assert repository == REPOSITORY
        assert tag == REPOSITORY_TAG
        return {"assets": [{"name": name} for name in sorted(self.published)]}

    def latest_release(self, repository: str) -> dict[str, Any]:
        return self.releases[repository]

    def issues(self, repository: str, state: str = "all") -> list[dict[str, Any]]:
        assert repository == REPOSITORY
        return self.issue_list

    def create_issue(self, repository: str, title: str, body: str) -> dict[str, Any]:
        issue = {
            "number": len(self.issue_list) + 1,
            "title": title,
            "body": body,
            "state": "open",
        }
        self.issue_list.append(issue)
        return issue

    def update_issue(
        self,
        repository: str,
        number: int,
        *,
        body: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        issue = next(item for item in self.issue_list if item["number"] == number)
        if body is not None:
            issue["body"] = body
        if state is not None:
            issue["state"] = state
        return issue


@pytest.fixture
def synthetic_repository(tmp_path: Path) -> SyntheticRepository:
    return SyntheticRepository(tmp_path)


@pytest.fixture
def fake_github() -> FakeGitHub:
    return FakeGitHub()
