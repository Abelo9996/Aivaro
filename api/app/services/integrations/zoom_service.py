"""Zoom Integration Service — meetings, recordings, users."""
import httpx
from typing import Optional, Any


class ZoomService:
    """Service for Zoom REST API v2."""

    BASE_URL = "https://api.zoom.us/v2"

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
        return resp.json() if resp.content and resp.status_code != 204 else {}

    async def list_users(self, page_size: int = 30) -> list:
        result = await self._request("GET", "/users", params={"page_size": page_size})
        return result.get("users", [])

    async def list_meetings(self, user_id: str = "me", type: str = "scheduled") -> list:
        result = await self._request("GET", f"/users/{user_id}/meetings", params={"type": type})
        return result.get("meetings", [])

    async def create_meeting(self, topic: str, start_time: str = None, duration: int = 60,
                             timezone: str = None, agenda: str = None, user_id: str = "me",
                             type: int = 2) -> dict:
        body = {"topic": topic, "type": type, "duration": duration}
        if start_time: body["start_time"] = start_time
        if timezone: body["timezone"] = timezone
        if agenda: body["agenda"] = agenda
        return await self._request("POST", f"/users/{user_id}/meetings", json=body)

    async def get_meeting(self, meeting_id: int) -> dict:
        return await self._request("GET", f"/meetings/{meeting_id}")

    async def update_meeting(self, meeting_id: int, **fields) -> dict:
        return await self._request("PATCH", f"/meetings/{meeting_id}", json=fields)

    async def delete_meeting(self, meeting_id: int) -> dict:
        return await self._request("DELETE", f"/meetings/{meeting_id}")

    async def list_recordings(self, user_id: str = "me", from_date: str = None, to_date: str = None) -> list:
        params = {}
        if from_date: params["from"] = from_date
        if to_date: params["to"] = to_date
        result = await self._request("GET", f"/users/{user_id}/recordings", params=params)
        return result.get("meetings", [])
