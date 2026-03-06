"""Twitch Integration Service — streams, channels, clips."""
import httpx
from typing import Optional, Any


class TwitchService:
    """Service for Twitch Helix API."""

    BASE_URL = "https://api.twitch.tv/helix"

    def __init__(self, client_id: str, access_token: str):
        self.client_id = client_id
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Client-Id": self.client_id, "Authorization": f"Bearer {self.access_token}"}

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

    async def get_user(self, login: str = None, user_id: str = None) -> dict:
        params = {}
        if login: params["login"] = login
        if user_id: params["id"] = user_id
        result = await self._request("GET", "/users", params=params)
        data = result.get("data", [])
        return data[0] if data else {}

    async def get_streams(self, user_login: str = None, game_id: str = None, limit: int = 20) -> list:
        params = {"first": limit}
        if user_login: params["user_login"] = user_login
        if game_id: params["game_id"] = game_id
        result = await self._request("GET", "/streams", params=params)
        return result.get("data", [])

    async def get_channel(self, broadcaster_id: str) -> dict:
        result = await self._request("GET", "/channels", params={"broadcaster_id": broadcaster_id})
        data = result.get("data", [])
        return data[0] if data else {}

    async def search_channels(self, query: str, limit: int = 20) -> list:
        result = await self._request("GET", "/search/channels", params={"query": query, "first": limit})
        return result.get("data", [])

    async def get_clips(self, broadcaster_id: str, limit: int = 20) -> list:
        result = await self._request("GET", "/clips", params={"broadcaster_id": broadcaster_id, "first": limit})
        return result.get("data", [])

    async def create_clip(self, broadcaster_id: str) -> dict:
        result = await self._request("POST", "/clips", params={"broadcaster_id": broadcaster_id})
        data = result.get("data", [])
        return data[0] if data else {}

    async def get_subscribers(self, broadcaster_id: str, limit: int = 20) -> list:
        result = await self._request("GET", "/subscriptions",
                                     params={"broadcaster_id": broadcaster_id, "first": limit})
        return result.get("data", [])
