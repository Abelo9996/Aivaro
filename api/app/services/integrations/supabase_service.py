"""Supabase Integration Service — CRUD via PostgREST."""
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
        return resp.json() if resp.content and resp.status_code not in (204,) else {}

    async def list_rows(self, table: str, limit: int = 50, offset: int = 0,
                        select: str = "*", filters: dict = None) -> list:
        params = {"select": select, "limit": limit, "offset": offset}
        if filters:
            for k, v in filters.items():
                params[k] = f"eq.{v}"
        result = await self._request("GET", f"/{table}", params=params)
        return result if isinstance(result, list) else []

    async def get_row(self, table: str, id_column: str, id_value: str) -> dict:
        params = {"select": "*", id_column: f"eq.{id_value}", "limit": 1}
        result = await self._request("GET", f"/{table}", params=params)
        return result[0] if result else {}

    async def insert_row(self, table: str, data: dict) -> dict:
        result = await self._request("POST", f"/{table}", json=data)
        return result[0] if isinstance(result, list) and result else result

    async def update_row(self, table: str, id_column: str, id_value: str, data: dict) -> dict:
        params = {id_column: f"eq.{id_value}"}
        result = await self._request("PATCH", f"/{table}", params=params, json=data)
        return result[0] if isinstance(result, list) and result else result

    async def delete_row(self, table: str, id_column: str, id_value: str) -> dict:
        params = {id_column: f"eq.{id_value}"}
        await self._request("DELETE", f"/{table}", params=params)
        return {"deleted": True}

    async def rpc_call(self, function_name: str, params: dict = None) -> Any:
        client = await self._get_client()
        resp = await client.post(f"{self.base_url.replace('/rest/v1', '')}/rest/v1/rpc/{function_name}",
                                 headers=self.headers, json=params or {})
        resp.raise_for_status()
        return resp.json() if resp.content else {}
