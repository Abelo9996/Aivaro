"""Pipedrive Integration Service — deals, persons, activities."""
import httpx
from typing import Optional, Any


class PipedriveService:
    """Service for Pipedrive REST API."""

    BASE_URL = "https://api.pipedrive.com/v1"

    def __init__(self, api_token: str):
        self.api_token = api_token
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, params: dict = None, **kwargs) -> Any:
        client = await self._get_client()
        merged = {"api_token": self.api_token, **(params or {})}
        resp = await client.request(method, f"{self.BASE_URL}{path}", params=merged, **kwargs)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise Exception(data.get("error", "Pipedrive API error"))
        return data.get("data")

    async def list_deals(self, status: str = "open", limit: int = 50) -> list:
        result = await self._request("GET", "/deals", params={"status": status, "limit": limit})
        return result or []

    async def get_deal(self, deal_id: int) -> dict:
        return await self._request("GET", f"/deals/{deal_id}")

    async def create_deal(self, title: str, value: float = None, currency: str = None,
                          person_id: int = None, stage_id: int = None) -> dict:
        body = {"title": title}
        if value is not None: body["value"] = value
        if currency: body["currency"] = currency
        if person_id: body["person_id"] = person_id
        if stage_id: body["stage_id"] = stage_id
        return await self._request("POST", "/deals", json=body)

    async def update_deal(self, deal_id: int, **fields) -> dict:
        return await self._request("PUT", f"/deals/{deal_id}", json=fields)

    async def list_persons(self, limit: int = 50) -> list:
        result = await self._request("GET", "/persons", params={"limit": limit})
        return result or []

    async def create_person(self, name: str, email: str = None, phone: str = None) -> dict:
        body = {"name": name}
        if email: body["email"] = [{"value": email, "primary": True}]
        if phone: body["phone"] = [{"value": phone, "primary": True}]
        return await self._request("POST", "/persons", json=body)

    async def update_person(self, person_id: int, **fields) -> dict:
        return await self._request("PUT", f"/persons/{person_id}", json=fields)

    async def list_activities(self, limit: int = 50) -> list:
        result = await self._request("GET", "/activities", params={"limit": limit})
        return result or []

    async def create_activity(self, subject: str, type: str = "call", deal_id: int = None,
                              person_id: int = None, due_date: str = None, note: str = None) -> dict:
        body = {"subject": subject, "type": type}
        if deal_id: body["deal_id"] = deal_id
        if person_id: body["person_id"] = person_id
        if due_date: body["due_date"] = due_date
        if note: body["note"] = note
        return await self._request("POST", "/activities", json=body)

    async def create_note(self, content: str, deal_id: int = None, person_id: int = None) -> dict:
        body = {"content": content}
        if deal_id: body["deal_id"] = deal_id
        if person_id: body["person_id"] = person_id
        return await self._request("POST", "/notes", json=body)
