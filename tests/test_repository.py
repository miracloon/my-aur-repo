import pytest
from conftest import REPOSITORY, FakeGitHub, SyntheticRepository, make_release

from my_aur.repository import close_failure, discover_work, report_failures


def test_unpublished_package_is_discovered(
    synthetic_repository: SyntheticRepository, fake_github: FakeGitHub
):
    synthetic_repository.add_package("demo-bin", pkgver="1.0.0")
    synthetic_repository.add_package(
        "other-bin", pkgver="2.0.0", repository="other/project", asset="Other-{version}.zip"
    )
    fake_github.releases = {
        "owner/project": make_release("1.1.0"),
        "other/project": make_release("2.0.0", asset="Other-2.0.0.zip"),
    }

    result = discover_work(synthetic_repository.root, REPOSITORY, fake_github)

    assert result.failures == []
    assert [item["package"] for item in result.work] == ["demo-bin", "other-bin"]
    assert result.work[0]["expected"] == "demo-bin-1.1.0-1-x86_64.pkg.tar.zst"
    assert result.work[1]["expected"] == "other-bin-2.0.0-1-x86_64.pkg.tar.zst"


def test_published_package_is_skipped(
    synthetic_repository: SyntheticRepository, fake_github: FakeGitHub
):
    synthetic_repository.add_package("demo-bin", pkgver="1.0.0")
    fake_github.releases = {"owner/project": make_release("1.1.0")}
    fake_github.published = {"demo-bin-1.1.0-1-x86_64.pkg.tar.zst"}

    result = discover_work(synthetic_repository.root, REPOSITORY, fake_github)

    assert result.work == []
    assert result.failures == []


def test_unchanged_upstream_version_keeps_pkgrel(
    synthetic_repository: SyntheticRepository, fake_github: FakeGitHub
):
    synthetic_repository.add_package("demo-bin", pkgver="1.2.0", pkgrel="3")
    fake_github.releases = {"owner/project": make_release("1.2.0")}

    result = discover_work(synthetic_repository.root, REPOSITORY, fake_github)

    assert result.work[0]["pkgrel"] == "3"
    assert result.work[0]["expected"] == "demo-bin-1.2.0-3-x86_64.pkg.tar.zst"


def test_upstream_regression_freezes_only_that_package(
    synthetic_repository: SyntheticRepository, fake_github: FakeGitHub
):
    synthetic_repository.add_package("demo-bin", pkgver="2.0.0")
    synthetic_repository.add_package(
        "other-bin", pkgver="2.0.0", repository="other/project", asset="Other-{version}.zip"
    )
    fake_github.releases = {
        "owner/project": make_release("1.0.0"),
        "other/project": make_release("2.1.0", asset="Other-2.1.0.zip"),
    }

    result = discover_work(synthetic_repository.root, REPOSITORY, fake_github)

    assert [item["package"] for item in result.work] == ["other-bin"]
    assert len(result.failures) == 1
    failure = result.failures[0]
    assert failure["package"] == "demo-bin"
    assert failure["stage"] == "discover"
    assert failure["version"] == "1.0.0"  # upstream version, not the declared one
    assert "upstream regression 1.0.0 < 2.0.0" in failure["message"]


def test_monitor_failure_is_isolated(
    synthetic_repository: SyntheticRepository, fake_github: FakeGitHub
):
    synthetic_repository.add_package("demo-bin", pkgver="1.0.0")
    synthetic_repository.add_package(
        "other-bin", pkgver="2.0.0", repository="other/project", asset="Other-{version}.zip"
    )
    fake_github.releases = {
        "owner/project": make_release("1.1.0", asset="Demo-1.1.0-windows.zip"),
        "other/project": make_release("2.1.0", asset="Other-2.1.0.zip"),
    }

    result = discover_work(synthetic_repository.root, REPOSITORY, fake_github)

    assert [item["package"] for item in result.work] == ["other-bin"]
    assert [failure["package"] for failure in result.failures] == ["demo-bin"]
    assert "expected exactly one asset" in result.failures[0]["message"]


def test_report_failures_keeps_one_issue_per_package(fake_github: FakeGitHub):
    failures = [
        {
            "package": "demo-bin",
            "version": "1.1.0",
            "stage": "discover",
            "message": "upstream regression",
        }
    ]
    report_failures(fake_github, REPOSITORY, failures, "https://example.invalid/run/1")
    report_failures(fake_github, REPOSITORY, failures, "https://example.invalid/run/2")

    assert len(fake_github.issue_list) == 1
    issue = fake_github.issue_list[0]
    assert issue["title"] == "[package failure] demo-bin"
    assert issue["state"] == "open"
    assert "https://example.invalid/run/2" in issue["body"]
    assert "upstream regression" in issue["body"]

    close_failure(fake_github, REPOSITORY, "demo-bin")
    assert fake_github.issue_list[0]["state"] == "closed"


@pytest.mark.parametrize("stage", ["discover", "build-and-validate"])
def test_failure_issue_records_stage(fake_github: FakeGitHub, stage: str):
    report_failures(
        fake_github,
        REPOSITORY,
        [{"package": "demo-bin", "version": "1.1.0", "stage": stage, "message": "boom"}],
        "https://example.invalid/run/1",
    )
    assert f"`{stage}`" in fake_github.issue_list[0]["body"]
