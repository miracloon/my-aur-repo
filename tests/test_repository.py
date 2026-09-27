from pathlib import Path

from my_aur.repository import discover_work


class FakeGitHub:
    def __init__(self, published=()):
        self.published = published

    def release(self, repository, tag):
        assert repository == "miracloon/my-aur-repo"
        assert tag == "repository-x86_64"
        return {"assets": [{"name": name} for name in self.published]}

    def latest_release(self, repository):
        assert repository == "DevXDojo/MrRSS"
        return {
            "tag_name": "v1.3.38",
            "draft": False,
            "prerelease": False,
            "assets": [
                {
                    "name": "MrRSS-1.3.38-linux-amd64.tar.gz",
                    "browser_download_url": "https://example.invalid/mrrss.tar.gz",
                    "digest": "sha256:fba2",
                }
            ],
        }


ROOT = Path(__file__).parents[1]
PACKAGE_FILE = "mrrss-bin-1.3.38-1-x86_64.pkg.tar.zst"


def test_unpublished_package_is_discovered():
    work = discover_work(ROOT, "miracloon/my-aur-repo", FakeGitHub())
    assert [item["package"] for item in work] == ["mrrss-bin"]
    assert work[0]["expected"] == PACKAGE_FILE


def test_published_package_is_skipped():
    assert discover_work(
        ROOT, "miracloon/my-aur-repo", FakeGitHub([PACKAGE_FILE])
    ) == []
