"""ClickUp Integration Service — tasks, lists, spaces."""
import httpx
from typing import Optional, Any


class ClickUpService:
    """Service for ClickUp API v2."""

    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": self.api_key, "Content-Type": "application/json"}

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
        resp = await client.request(method, f"{self.BASE_URL}{path}", headers=self.headers, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content and resp.status_code != 204 else {}

    async def list_workspaces(self) -> list:
        result = await self._request("GET", "/team")
        return result.get("teams", [])

    async def list_spaces(self, team_id: str) -> list:
        result = await self._request("GET", f"/team/{team_id}/space")
        return result.get("spaces", [])

    async def list_folders(self, space_id: str) -> list:
        result = await self._request("GET", f"/space/{space_id}/folder")
        return result.get("folders", [])

    async def list_lists(self, folder_id: str) -> list:
        result = await self._request("GET", f"/folder/{folder_id}/list")
        return result.get("lists", [])

    async def list_tasks(self, list_id: str) -> list:
        result = await self._request("GET", f"/list/{list_id}/task")
        return result.get("tasks", [])

    async def get_task(self, task_id: str) -> dict:
        return await self._request("GET", f"/task/{task_id}")

    async def create_task(self, list_id: str, name: str, description: str = "",
                          assignees: list = None, due_date: int = None, priority: int = None) -> dict:
        body = {"name": name}
        if description: body["description"] = description
        if assignees: body["assignees"] = assignees
        if due_date: body["due_date"] = due_date
        if priority is not None: body["priority"] = priority
        return await self._request("POST", f"/list/{list_id}/task", json=body)

    async def update_task(self, task_id: str, **fields) -> dict:
        return await self._request("PUT", f"/task/{task_id}", json=fields)

    async def delete_task(self, task_id: str) -> dict:
        return await self._request("DELETE", f"/task/{task_id}")

    async def add_comment(self, task_id: str, comment_text: str) -> dict:
        return await self._request("POST", f"/task/{task_id}/comment", json={"comment_text": comment_text})
