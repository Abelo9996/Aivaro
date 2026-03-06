"""Webflow Integration Service — sites, collections, items."""
import httpx
from typing import Optional, Any


class WebflowService:
    """Service for Webflow API v2."""

    BASE_URL = "https://api.webflow.com/v2"

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

    async def list_sites(self) -> list:
        result = await self._request("GET", "/sites")
        return result.get("sites", [])

    async def list_collections(self, site_id: str) -> list:
        result = await self._request("GET", f"/sites/{site_id}/collections")
        return result.get("collections", [])

    async def list_items(self, collection_id: str, limit: int = 100, offset: int = 0) -> list:
        result = await self._request("GET", f"/collections/{collection_id}/items",
                                     params={"limit": limit, "offset": offset})
        return result.get("items", [])

    async def create_item(self, collection_id: str, fields: dict, is_draft: bool = False) -> dict:
        body = {"fieldData": fields, "isDraft": is_draft}
        return await self._request("POST", f"/collections/{collection_id}/items", json=body)

    async def update_item(self, collection_id: str, item_id: str, fields: dict) -> dict:
        return await self._request("PATCH", f"/collections/{collection_id}/items/{item_id}",
                                   json={"fieldData": fields})

    async def delete_item(self, collection_id: str, item_id: str) -> dict:
        return await self._request("DELETE", f"/collections/{collection_id}/items/{item_id}")

    async def publish_site(self, site_id: str, domains: list = None) -> dict:
        body = {}
        if domains: body["customDomains"] = domains
        return await self._request("POST", f"/sites/{site_id}/publish", json=body)
