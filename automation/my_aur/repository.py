"""Read release assets, select build work, prune history and maintain package failure issues."""

from dataclasses import asdict
from typing import Any

from packaging.version import InvalidVersion, Version

from .config import enabled_packages
from .github import GitHubClient
from .monitor import resolve_release
from .pkgbuild import PkgbuildError, read_version

REPOSITORY_TAG = "repository-x86_64"


def release_assets(github: GitHubClient, repository: str) -> list[dict[str, Any]]:
    release = github.release(repository, REPOSITORY_TAG)
    return [] if release is None else release.get("assets", [])


def discover_work(
    root,
    repository: str,
    github: GitHubClient,
    selected: str | None = None,
) -> list[dict]:
    published = {asset["name"] for asset in release_assets(github, repository)}
    work: list[dict] = []
    for package in enabled_packages(root, selected):
        upstream = resolve_release(package, github)
        current = read_version(package.directory / "PKGBUILD")
        try:
            upstream_version = Version(upstream.version)
            current_version = Version(current.pkgver)
        except InvalidVersion as error:
            raise PkgbuildError(f"{package.name}: release versions must be comparable") from error
        if upstream_version < current_version:
            raise PkgbuildError(
                f"{package.name}: upstream regression {upstream.version} < {current.pkgver}"
            )
        pkgrel = "1" if upstream_version > current_version else current.pkgrel
        expected = f"{package.name}-{upstream.version}-{pkgrel}-x86_64.pkg.tar.zst"
        if expected not in published:
            item = asdict(upstream)
            item.update({"package": package.name, "pkgrel": pkgrel, "expected": expected})
            work.append(item)
    return work


def _failure_issue(issues: list[dict[str, Any]], package: str) -> dict[str, Any] | None:
    title = f"[package failure] {package}"
    return next(
        (
            issue
            for issue in issues
            if issue.get("title") == title and "pull_request" not in issue
        ),
        None,
    )


def report_failure(
    github: GitHubClient,
    repository: str,
    package: str,
    version: str,
    stage: str,
    run_url: str,
) -> None:
    title = f"[package failure] {package}"
    body = (
        f"## Automated package failure\n\n"
        f"- Package: `{package}`\n"
        f"- Upstream version: `{version}`\n"
        f"- Failed stage: `{stage}`\n"
        f"- Actions run: {run_url}\n\n"
        "The previously published package remains available. This issue is updated on recurrence "
        "and closed automatically after a successful publication.\n"
    )
    issue = _failure_issue(github.issues(repository), package)
    if issue is None:
        github.create_issue(repository, title, body)
    else:
        github.update_issue(repository, issue["number"], body=body, state="open")


def close_failure(github: GitHubClient, repository: str, package: str) -> None:
    issue = _failure_issue(github.issues(repository), package)
    if issue is not None and issue.get("state") == "open":
        github.update_issue(repository, issue["number"], state="closed")


def prune_old_assets(root, github: GitHubClient, repository: str, keep: int = 2) -> list[str]:
    assets = release_assets(github, repository)
    deleted: list[str] = []
    for package in enabled_packages(root):
        prefix = f"{package.name}-"
        suffix = "-x86_64.pkg.tar.zst"
        versions: list[tuple[Version, int, dict[str, Any]]] = []
        for asset in assets:
            name = asset["name"]
            if not (name.startswith(prefix) and name.endswith(suffix)):
                continue
            raw = name[len(prefix) : -len(suffix)]
            try:
                pkgver, pkgrel = raw.rsplit("-", 1)
                versions.append((Version(pkgver), int(pkgrel), asset))
            except (ValueError, InvalidVersion):
                continue
        versions.sort(key=lambda item: (item[0], item[1]), reverse=True)
        for _, _, asset in versions[keep:]:
            github.delete_asset(repository, asset["id"])
            deleted.append(asset["name"])
    return deleted
