"""Asana Integration Service — tasks, projects, workspaces."""
import httpx
from typing import Optional, Any


class AsanaService:
    """Service for Asana REST API."""

    BASE_URL = "https://app.asana.com/api/1.0"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}

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
        data = resp.json() if resp.content and resp.status_code != 204 else {}
        return data.get("data", data)

    async def list_workspaces(self) -> list:
        return await self._request("GET", "/workspaces")

    async def list_projects(self, workspace_gid: str) -> list:
        return await self._request("GET", "/projects", params={"workspace": workspace_gid})

    async def create_project(self, workspace_gid: str, name: str, notes: str = "") -> dict:
        body = {"data": {"workspace": workspace_gid, "name": name}}
        if notes: body["data"]["notes"] = notes
        return await self._request("POST", "/projects", json=body)

    async def list_tasks(self, project_gid: str) -> list:
        return await self._request("GET", f"/projects/{project_gid}/tasks",
                                   params={"opt_fields": "name,completed,due_on,assignee.name"})

    async def get_task(self, task_gid: str) -> dict:
        return await self._request("GET", f"/tasks/{task_gid}")

    async def create_task(self, project_gid: str, name: str, notes: str = "",
                          assignee: str = None, due_on: str = None) -> dict:
        body = {"data": {"projects": [project_gid], "name": name}}
        if notes: body["data"]["notes"] = notes
        if assignee: body["data"]["assignee"] = assignee
        if due_on: body["data"]["due_on"] = due_on
        return await self._request("POST", "/tasks", json=body)

    async def update_task(self, task_gid: str, **fields) -> dict:
        return await self._request("PUT", f"/tasks/{task_gid}", json={"data": fields})

    async def add_comment(self, task_gid: str, text: str) -> dict:
        return await self._request("POST", f"/tasks/{task_gid}/stories", json={"data": {"text": text}})
