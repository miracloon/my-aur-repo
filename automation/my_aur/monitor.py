"""Resolve supported upstream monitors into immutable release identities."""

import re

from .github import GitHubClient
from .models import PackageConfig, ReleaseIdentity


class MonitorError(RuntimeError):
    """Raised when upstream metadata cannot produce an unambiguous package input."""


def normalize_release_version(tag: str) -> str:
    version = tag[1:] if tag.startswith("v") else tag
    version = version.replace("-", "_")
    if not re.fullmatch(r"[0-9][A-Za-z0-9._+]*", version):
        raise MonitorError(f"unsupported stable release version: {tag!r}")
    return version


def resolve_release(package: PackageConfig, github: GitHubClient) -> ReleaseIdentity:
    if package.monitor.type != "github_release":
        raise MonitorError(f"unsupported monitor type: {package.monitor.type}")
    release = github.latest_release(package.monitor.repository)
    if release.get("draft") or (release.get("prerelease") and not package.monitor.prerelease):
        raise MonitorError(f"latest release is not eligible: {release.get('tag_name')}")

    tag = release["tag_name"]
    version = normalize_release_version(tag)
    expected_asset = package.monitor.asset.format(version=version, tag=tag)
    matches = [asset for asset in release.get("assets", []) if asset["name"] == expected_asset]
    if len(matches) != 1:
        raise MonitorError(
            f"{package.name}: expected exactly one asset {expected_asset!r}, found {len(matches)}"
        )
    asset = matches[0]
    return ReleaseIdentity(
        version=version,
        tag=tag,
        asset_name=asset["name"],
        asset_url=asset["browser_download_url"],
        digest=asset.get("digest"),
    )
