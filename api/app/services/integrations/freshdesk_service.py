"""Freshdesk Integration Service — tickets, contacts, agents."""
import httpx
from typing import Optional, Any
import base64


class FreshdeskService:
    """Service for Freshdesk REST API v2."""

    def __init__(self, domain: str, api_key: str):
        self.base_url = f"https://{domain}.freshdesk.com/api/v2"
        self._auth = base64.b64encode(f"{api_key}:X".encode()).decode()
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Basic {self._auth}", "Content-Type": "application/json"}

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

    async def create_ticket(self, subject: str, description: str, email: str,
                            priority: int = 1, status: int = 2) -> dict:
        return await self._request("POST", "/tickets", json={
            "subject": subject, "description": description, "email": email,
            "priority": priority, "status": status
        })

    async def update_ticket(self, ticket_id: int, **fields) -> dict:
        return await self._request("PUT", f"/tickets/{ticket_id}", json=fields)

    async def get_ticket(self, ticket_id: int) -> dict:
        return await self._request("GET", f"/tickets/{ticket_id}")

    async def list_tickets(self, limit: int = 30) -> list:
        return await self._request("GET", "/tickets", params={"per_page": min(limit, 100)})

    async def add_note(self, ticket_id: int, body: str, private: bool = True) -> dict:
        return await self._request("POST", f"/tickets/{ticket_id}/notes",
                                   json={"body": body, "private": private})

    async def create_contact(self, name: str, email: str, phone: str = None) -> dict:
        body = {"name": name, "email": email}
        if phone: body["phone"] = phone
        return await self._request("POST", "/contacts", json=body)

    async def list_contacts(self, limit: int = 30) -> list:
        return await self._request("GET", "/contacts", params={"per_page": min(limit, 100)})

    async def list_agents(self) -> list:
        return await self._request("GET", "/agents")
