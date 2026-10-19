"""Read release assets, select build work, prune history and maintain package failure issues."""

from dataclasses import asdict, dataclass, field
from typing import Any

from packaging.version import InvalidVersion, Version

from .config import enabled_packages
from .github import GitHubClient, GitHubError
from .monitor import MonitorError, resolve_release
from .pkgbuild import PkgbuildError, read_version

REPOSITORY_TAG = "repository-x86_64"
DISCOVER_STAGE = "discover"


@dataclass
class DiscoverResult:
    """Per-package outcome of discovery: buildable work plus isolated failures."""

    work: list[dict[str, Any]] = field(default_factory=list)
    failures: list[dict[str, str]] = field(default_factory=list)


def release_assets(github: GitHubClient, repository: str) -> list[dict[str, Any]]:
    release = github.release(repository, REPOSITORY_TAG)
    return [] if release is None else release.get("assets", [])


class PackageFailure(Exception):
    """A single package's discovery failure, carrying the version worth reporting."""

    def __init__(self, package: str, version: str, message: str) -> None:
        super().__init__(message)
        self.package = package
        self.version = version
        self.message = message


def _resolve_work(package, published: set[str], github: GitHubClient) -> dict[str, Any] | None:
    """Return the matrix entry for one package, or None when already published."""
    upstream = resolve_release(package, github)
    current = read_version(package.directory / "PKGBUILD")
    try:
        upstream_version = Version(upstream.version)
        current_version = Version(current.pkgver)
    except InvalidVersion as error:
        raise PackageFailure(
            package.name, upstream.version, f"{package.name}: release versions must be comparable"
        ) from error
    if upstream_version < current_version:
        raise PackageFailure(
            package.name,
            upstream.version,
            f"{package.name}: upstream regression {upstream.version} < {current.pkgver}",
        )
    pkgrel = "1" if upstream_version > current_version else current.pkgrel
    expected = f"{package.name}-{upstream.version}-{pkgrel}-x86_64.pkg.tar.zst"
    if expected in published:
        return None
    item = asdict(upstream)
    item.update({"package": package.name, "pkgrel": pkgrel, "expected": expected})
    return item


def _declared_version(package) -> str:
    try:
        return read_version(package.directory / "PKGBUILD").pkgver
    except PkgbuildError:
        return "unknown"


def discover_work(
    root,
    repository: str,
    github: GitHubClient,
    selected: str | None = None,
) -> DiscoverResult:
    """Select build work, isolating one package's failure from every other package."""
    published = {asset["name"] for asset in release_assets(github, repository)}
    result = DiscoverResult()
    for package in enabled_packages(root, selected):
        try:
            item = _resolve_work(package, published, github)
        except PackageFailure as failure:
            result.failures.append(
                {
                    "package": failure.package,
                    "version": failure.version,
                    "stage": DISCOVER_STAGE,
                    "message": failure.message,
                }
            )
            continue
        except (MonitorError, PkgbuildError, GitHubError) as error:
            result.failures.append(
                {
                    "package": package.name,
                    "version": _declared_version(package),
                    "stage": DISCOVER_STAGE,
                    "message": str(error),
                }
            )
            continue
        if item is not None:
            result.work.append(item)
    return result


def _failure_issue(issues: list[dict[str, Any]], package: str) -> dict[str, Any] | None:
    title = f"[package failure] {package}"
    return next(
        (issue for issue in issues if issue.get("title") == title and "pull_request" not in issue),
        None,
    )


def _failure_body(failure: dict[str, str], run_url: str) -> str:
    return (
        f"## Automated package failure\n\n"
        f"- Package: `{failure['package']}`\n"
        f"- Upstream version: `{failure['version']}`\n"
        f"- Failed stage: `{failure['stage']}`\n"
        f"- Actions run: {run_url}\n"
        f"- Reason: {failure['message']}\n\n"
        "The previously published package remains available. This issue is updated on recurrence "
        "and closed automatically after a successful publication.\n"
    )


def report_failures(
    github: GitHubClient,
    repository: str,
    failures: list[dict[str, str]],
    run_url: str,
) -> None:
    """Open or refresh exactly one failure issue per failed package."""
    if not failures:
        return
    issues = github.issues(repository)
    for failure in failures:
        package = failure["package"]
        body = _failure_body(failure, run_url)
        issue = _failure_issue(issues, package)
        if issue is None:
            github.create_issue(repository, f"[package failure] {package}", body)
        else:
            github.update_issue(repository, issue["number"], body=body, state="open")


def report_failure(
    github: GitHubClient,
    repository: str,
    package: str,
    version: str,
    stage: str,
    run_url: str,
    message: str = "see the Actions run for details",
) -> None:
    report_failures(
        github,
        repository,
        [{"package": package, "version": version, "stage": stage, "message": message}],
        run_url,
    )


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
