"""Command-line boundary for CI orchestration."""

import argparse
import json
import os
from pathlib import Path

from .config import enabled_packages, repository_root
from .github import GitHubClient
from .pkgbuild import update_upstream_version
from .repository import close_failure, discover_work, prune_old_assets, report_failure


def _repository(value: str | None) -> str:
    repository = value or os.environ.get("GITHUB_REPOSITORY")
    if not repository:
        raise SystemExit("GITHUB_REPOSITORY or --repository is required")
    return repository


def command_validate(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    packages = enabled_packages(root, args.package)
    print(json.dumps({"valid": [package.name for package in packages]}))
    return 0


def command_discover(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    work = discover_work(root, _repository(args.repository), GitHubClient(), args.package)
    print(json.dumps({"include": work}, separators=(",", ":")))
    return 0


def command_prepare(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    package = enabled_packages(root, args.package)[0]
    changed = update_upstream_version(package.directory / "PKGBUILD", args.version)
    print(json.dumps({"package": package.name, "version_changed": changed}))
    return 0


def command_report_failure(args: argparse.Namespace) -> int:
    report_failure(
        GitHubClient(),
        _repository(args.repository),
        args.package,
        args.version,
        args.stage,
        args.run_url,
    )
    return 0


def command_close_failure(args: argparse.Namespace) -> int:
    close_failure(GitHubClient(), _repository(args.repository), args.package)
    return 0


def command_prune(args: argparse.Namespace) -> int:
    root = repository_root(args.root)
    deleted = prune_old_assets(root, GitHubClient(), _repository(args.repository), args.keep)
    print(json.dumps({"deleted": deleted}))
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(prog="my-aur")
    result.add_argument("--root", type=Path)
    subparsers = result.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--package")
    validate.set_defaults(func=command_validate)

    discover = subparsers.add_parser("discover")
    discover.add_argument("--package")
    discover.add_argument("--repository")
    discover.set_defaults(func=command_discover)

    prepare = subparsers.add_parser("prepare")
    prepare.add_argument("--package", required=True)
    prepare.add_argument("--version", required=True)
    prepare.set_defaults(func=command_prepare)

    failure = subparsers.add_parser("report-failure")
    failure.add_argument("--package", required=True)
    failure.add_argument("--version", required=True)
    failure.add_argument("--stage", required=True)
    failure.add_argument("--run-url", required=True)
    failure.add_argument("--repository")
    failure.set_defaults(func=command_report_failure)

    close = subparsers.add_parser("close-failure")
    close.add_argument("--package", required=True)
    close.add_argument("--repository")
    close.set_defaults(func=command_close_failure)

    prune = subparsers.add_parser("prune")
    prune.add_argument("--repository")
    prune.add_argument("--keep", type=int, default=2)
    prune.set_defaults(func=command_prune)
    return result


def main() -> int:
    args = parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
