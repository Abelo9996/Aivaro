"""Supabase Integration Service — database CRUD, RPC."""
import httpx
from typing import Optional, Any


class SupabaseService:
    """Service for Supabase REST API (PostgREST)."""

    def __init__(self, url: str, api_key: str):
        self.base_url = f"{url.rstrip('/')}/rest/v1"
        self.api_key = api_key
        self._client = None

    @property
    def headers(self) -> dict:
        return {"apikey": self.api_key, "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json", "Prefer": "return=representation"}

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
        resp = await client.request(method, f"{self.base_url}{path}", headers=self.headers, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content and resp.status_code != 204 else {}

    async def list_rows(self, table: str, limit: int = 50, offset: int = 0,
                        select: str = "*", filters: dict = None) -> list:
        params = {"select": select, "limit": limit, "offset": offset}
        if filters:
            for k, v in filters.items():
                params[k] = f"eq.{v}"
        return await self._request("GET", f"/{table}", params=params)

    async def get_row(self, table: str, column: str, value: str) -> list:
        return await self._request("GET", f"/{table}", params={"select": "*", column: f"eq.{value}"})

    async def insert_row(self, table: str, data: dict) -> list:
        return await self._request("POST", f"/{table}", json=data)

    async def update_row(self, table: str, column: str, value: str, data: dict) -> list:
        return await self._request("PATCH", f"/{table}", params={column: f"eq.{value}"}, json=data)

    async def delete_row(self, table: str, column: str, value: str) -> list:
        return await self._request("DELETE", f"/{table}", params={column: f"eq.{value}"})

    async def rpc_call(self, function_name: str, params: dict = None) -> Any:
        return await self._request("POST", f"/rpc/{function_name}", json=params or {})
