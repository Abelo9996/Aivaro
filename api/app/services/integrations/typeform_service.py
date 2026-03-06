"""Typeform Integration Service — forms, responses."""
import httpx
from typing import Optional, Any


class TypeformService:
    """Service for Typeform API."""

    BASE_URL = "https://api.typeform.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}"}

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

    async def list_forms(self, page_size: int = 25) -> list:
        result = await self._request("GET", "/forms", params={"page_size": page_size})
        return result.get("items", [])

    async def get_form(self, form_id: str) -> dict:
        return await self._request("GET", f"/forms/{form_id}")

    async def get_responses(self, form_id: str, page_size: int = 25) -> list:
        result = await self._request("GET", f"/forms/{form_id}/responses", params={"page_size": page_size})
        return result.get("items", [])

    async def create_form(self, title: str, fields: list = None) -> dict:
        body = {"title": title}
        if fields: body["fields"] = fields
        return await self._request("POST", "/forms", json=body)

    async def delete_form(self, form_id: str) -> dict:
        return await self._request("DELETE", f"/forms/{form_id}")
