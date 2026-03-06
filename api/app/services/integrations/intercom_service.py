"""Intercom Integration Service — contacts, conversations, tags."""
import httpx
from typing import Optional, Any


class IntercomService:
    """Service for Intercom REST API."""

    BASE_URL = "https://api.intercom.io"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json",
                "Intercom-Version": "2.11"}

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

    async def list_contacts(self, limit: int = 50) -> list:
        result = await self._request("POST", "/contacts/search",
                                     json={"query": {"operator": "AND", "value": []},
                                           "pagination": {"per_page": limit}})
        return result.get("data", [])

    async def create_contact(self, role: str = "user", email: str = None, name: str = None,
                             phone: str = None, external_id: str = None) -> dict:
        body = {"role": role}
        if email: body["email"] = email
        if name: body["name"] = name
        if phone: body["phone"] = phone
        if external_id: body["external_id"] = external_id
        return await self._request("POST", "/contacts", json=body)

    async def update_contact(self, contact_id: str, **fields) -> dict:
        return await self._request("PUT", f"/contacts/{contact_id}", json=fields)

    async def search_contacts(self, field: str, value: str) -> list:
        query = {"query": {"field": field, "operator": "=", "value": value}}
        result = await self._request("POST", "/contacts/search", json=query)
        return result.get("data", [])

    async def list_conversations(self, limit: int = 20) -> list:
        result = await self._request("GET", "/conversations", params={"per_page": limit})
        return result.get("conversations", [])

    async def create_conversation(self, from_contact_id: str, body: str) -> dict:
        return await self._request("POST", "/conversations", json={
            "from": {"type": "contact", "id": from_contact_id}, "body": body
        })

    async def reply_to_conversation(self, conversation_id: str, body: str,
                                    admin_id: str = None, message_type: str = "comment") -> dict:
        payload = {"body": body, "message_type": message_type, "type": "admin"}
        if admin_id: payload["admin_id"] = admin_id
        return await self._request("POST", f"/conversations/{conversation_id}/reply", json=payload)

    async def tag_contact(self, contact_id: str, tag_id: str) -> dict:
        return await self._request("POST", f"/contacts/{contact_id}/tags", json={"id": tag_id})

    async def create_note(self, contact_id: str, body: str, admin_id: str = None) -> dict:
        payload = {"body": body}
        if admin_id: payload["admin_id"] = admin_id
        return await self._request("POST", f"/contacts/{contact_id}/notes", json=payload)
