"""
GitHub Integration Service — repos, issues, PRs, comments.
"""
import httpx
from typing import Optional, Any


class GitHubService:
    """Service for GitHub REST API v3."""

    BASE_URL = "https://api.github.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        client = await self._get_client()
        url = f"{self.BASE_URL}{path}"
        resp = await client.request(method, url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.status_code != 204 else {}

    # Issues
    async def create_issue(self, owner: str, repo: str, title: str, body: str = "",
                           labels: list = None, assignees: list = None) -> dict:
        data = {"title": title}
        if body: data["body"] = body
        if labels: data["labels"] = labels
        if assignees: data["assignees"] = assignees
        return await self._request("POST", f"/repos/{owner}/{repo}/issues", json=data)

    async def get_issue(self, owner: str, repo: str, issue_number: int) -> dict:
        return await self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")

    async def update_issue(self, owner: str, repo: str, issue_number: int, **kwargs) -> dict:
        return await self._request("PATCH", f"/repos/{owner}/{repo}/issues/{issue_number}", json=kwargs)

    async def list_issues(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> list:
        return await self._request("GET", f"/repos/{owner}/{repo}/issues",
                                   params={"state": state, "per_page": limit})

    async def search_issues(self, query: str, limit: int = 30) -> list:
        result = await self._request("GET", "/search/issues", params={"q": query, "per_page": limit})
        return result.get("items", [])

    async def add_labels(self, owner: str, repo: str, issue_number: int, labels: list) -> list:
        return await self._request("POST", f"/repos/{owner}/{repo}/issues/{issue_number}/labels", json={"labels": labels})

    async def lock_issue(self, owner: str, repo: str, issue_number: int, reason: str = "resolved") -> dict:
        return await self._request("PUT", f"/repos/{owner}/{repo}/issues/{issue_number}/lock",
                                   json={"lock_reason": reason})

    async def unlock_issue(self, owner: str, repo: str, issue_number: int) -> dict:
        return await self._request("DELETE", f"/repos/{owner}/{repo}/issues/{issue_number}/lock")

    # Comments
    async def create_comment(self, owner: str, repo: str, issue_number: int, body: str) -> dict:
        return await self._request("POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", json={"body": body})

    async def list_comments(self, owner: str, repo: str, issue_number: int) -> list:
        return await self._request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}/comments")

    # Pull Requests
    async def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str,
                                  body: str = "", draft: bool = False) -> dict:
        return await self._request("POST", f"/repos/{owner}/{repo}/pulls",
                                   json={"title": title, "head": head, "base": base, "body": body, "draft": draft})

    async def list_pull_requests(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> list:
        return await self._request("GET", f"/repos/{owner}/{repo}/pulls",
                                   params={"state": state, "per_page": limit})

    # Branches
    async def create_branch(self, owner: str, repo: str, branch_name: str, from_sha: str) -> dict:
        return await self._request("POST", f"/repos/{owner}/{repo}/git/refs",
                                   json={"ref": f"refs/heads/{branch_name}", "sha": from_sha})

    async def list_branches(self, owner: str, repo: str, limit: int = 30) -> list:
        return await self._request("GET", f"/repos/{owner}/{repo}/branches", params={"per_page": limit})

    async def get_branch(self, owner: str, repo: str, branch: str) -> dict:
        return await self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")

    # Repos
    async def list_repos(self, limit: int = 30) -> list:
        return await self._request("GET", "/user/repos", params={"per_page": limit, "sort": "updated"})

    async def get_repo(self, owner: str, repo: str) -> dict:
        return await self._request("GET", f"/repos/{owner}/{repo}")

    # User
    async def get_user(self, username: str = None) -> dict:
        return await self._request("GET", f"/users/{username}" if username else "/user")
