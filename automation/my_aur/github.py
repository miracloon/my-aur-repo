"""Small GitHub REST client backed by the authenticated GitHub CLI."""

import json
import os
import subprocess
from typing import Any


class GitHubError(RuntimeError):
    """Raised for unexpected GitHub API responses."""


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        allow_404: bool = False,
    ) -> Any:
        command = ["gh", "api", "--method", method, path]
        body = None
        if payload is not None:
            command.extend(["--input", "-"])
            body = json.dumps(payload)
        environment = os.environ.copy()
        if self.token:
            environment["GH_TOKEN"] = self.token
        result = subprocess.run(
            command,
            input=body,
            text=True,
            capture_output=True,
            env=environment,
            check=False,
        )
        if result.returncode != 0:
            if allow_404 and "HTTP 404" in result.stderr:
                return None
            raise GitHubError(
                f"GitHub API {method} {path} failed: {result.stderr.strip()}"
            )
        output = result.stdout.strip()
        return None if not output else json.loads(output)

    def latest_release(self, repository: str) -> dict[str, Any]:
        return self.request("GET", f"/repos/{repository}/releases/latest")

    def release(self, repository: str, tag: str) -> dict[str, Any] | None:
        return self.request(
            "GET", f"/repos/{repository}/releases/tags/{tag}", allow_404=True
        )

    def delete_asset(self, repository: str, asset_id: int) -> None:
        self.request("DELETE", f"/repos/{repository}/releases/assets/{asset_id}")

    def issues(self, repository: str, state: str = "all") -> list[dict[str, Any]]:
        return self.request("GET", f"/repos/{repository}/issues?state={state}&per_page=100")

    def create_issue(self, repository: str, title: str, body: str) -> dict[str, Any]:
        return self.request("POST", f"/repos/{repository}/issues", {"title": title, "body": body})

    def update_issue(
        self,
        repository: str,
        number: int,
        *,
        body: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        values = {"body": body, "state": state}
        payload = {key: value for key, value in values.items() if value}
        return self.request("PATCH", f"/repos/{repository}/issues/{number}", payload)
