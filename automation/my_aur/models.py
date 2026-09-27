"""Shared immutable data models for package declarations and release state."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MonitorConfig:
    type: str
    repository: str
    prerelease: bool
    asset: str


@dataclass(frozen=True)
class PackageConfig:
    name: str
    directory: Path
    monitor: MonitorConfig


@dataclass(frozen=True)
class ReleaseIdentity:
    version: str
    tag: str
    asset_name: str
    asset_url: str
    digest: str | None


@dataclass(frozen=True)
class PackageVersion:
    pkgver: str
    pkgrel: str

    @property
    def full(self) -> str:
        return f"{self.pkgver}-{self.pkgrel}"

    def filename(self, package: str, architecture: str = "x86_64") -> str:
        return f"{package}-{self.full}-{architecture}.pkg.tar.zst"
