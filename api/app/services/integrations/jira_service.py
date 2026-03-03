"""
Jira Cloud Integration Service — issues, projects, comments, search.
"""
import httpx
from typing import Optional, Any


class JiraService:
    """Service for Jira Cloud REST API v3."""

    def __init__(self, domain: str, email: str, api_token: str):
        self.base_url = f"https://{domain}/rest/api/3" if not domain.startswith("http") else f"{domain}/rest/api/3"
        self.email = email
        self.api_token = api_token
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0, auth=(self.email, self.api_token))
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        client = await self._get_client()
        url = f"{self.base_url}{path}"
        resp = await client.request(method, url, headers={"Content-Type": "application/json"}, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.status_code != 204 else {}

    async def create_issue(self, project_key: str, summary: str, issue_type: str = "Task",
                           description: str = "", priority: str = None, assignee_id: str = None,
                           labels: list = None) -> dict:
        fields = {
            "project": {"key": project_key},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": description}]}
            ]}
        if priority: fields["priority"] = {"name": priority}
        if assignee_id: fields["assignee"] = {"accountId": assignee_id}
        if labels: fields["labels"] = labels
        return await self._request("POST", "/issue", json={"fields": fields})

    async def get_issue(self, issue_key: str) -> dict:
        return await self._request("GET", f"/issue/{issue_key}")

    async def update_issue(self, issue_key: str, fields: dict) -> dict:
        return await self._request("PUT", f"/issue/{issue_key}", json={"fields": fields})

    async def delete_issue(self, issue_key: str) -> dict:
        return await self._request("DELETE", f"/issue/{issue_key}")

    async def search_issues(self, jql: str, max_results: int = 50) -> list:
        result = await self._request("POST", "/search", json={"jql": jql, "maxResults": max_results})
        return result.get("issues", [])

    async def add_comment(self, issue_key: str, body: str) -> dict:
        comment_body = {"type": "doc", "version": 1, "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": body}]}
        ]}
        return await self._request("POST", f"/issue/{issue_key}/comment", json={"body": comment_body})

    async def list_comments(self, issue_key: str) -> list:
        result = await self._request("GET", f"/issue/{issue_key}/comment")
        return result.get("comments", [])

    async def assign_issue(self, issue_key: str, account_id: str) -> dict:
        return await self._request("PUT", f"/issue/{issue_key}/assignee", json={"accountId": account_id})

    async def transition_issue(self, issue_key: str, transition_id: str) -> dict:
        return await self._request("POST", f"/issue/{issue_key}/transitions", json={"transition": {"id": transition_id}})

    async def get_transitions(self, issue_key: str) -> list:
        result = await self._request("GET", f"/issue/{issue_key}/transitions")
        return result.get("transitions", [])

    async def list_projects(self) -> list:
        return await self._request("GET", "/project")

    async def get_project(self, project_key: str) -> dict:
        return await self._request("GET", f"/project/{project_key}")

    async def search_users(self, query: str) -> list:
        return await self._request("GET", "/user/search", params={"query": query})

    async def add_watcher(self, issue_key: str, account_id: str) -> dict:
        return await self._request("POST", f"/issue/{issue_key}/watchers", json=account_id)

    async def link_issues(self, inward_key: str, outward_key: str, link_type: str = "Relates") -> dict:
        return await self._request("POST", "/issueLink", json={
            "type": {"name": link_type},
            "inwardIssue": {"key": inward_key},
            "outwardIssue": {"key": outward_key},
        })
