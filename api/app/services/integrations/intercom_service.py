"""Intercom Integration Service — contacts, conversations, tags."""
import httpx
from typing import Optional, Any


class IntercomService:
    """Service for Intercom REST API v2."""

    BASE_URL = "https://api.intercom.io"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json",
                "Intercom-Version": "2.10"}

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
        result = await self._request("GET", "/contacts", params={"per_page": limit})
        return result.get("data", [])

    async def create_contact(self, email: str, name: str = None, role: str = "user",
                             phone: str = None, custom_attributes: dict = None) -> dict:
        body = {"email": email, "role": role}
        if name: body["name"] = name
        if phone: body["phone"] = phone
        if custom_attributes: body["custom_attributes"] = custom_attributes
        return await self._request("POST", "/contacts", json=body)

    async def update_contact(self, contact_id: str, **fields) -> dict:
        return await self._request("PUT", f"/contacts/{contact_id}", json=fields)

    async def search_contacts(self, query: str, field: str = "email") -> list:
        body = {"query": {"field": field, "operator": "=", "value": query}}
        result = await self._request("POST", "/contacts/search", json=body)
        return result.get("data", [])

    async def list_conversations(self, limit: int = 20) -> list:
        result = await self._request("GET", "/conversations", params={"per_page": limit})
        return result.get("conversations", [])

    async def create_conversation(self, from_email: str, body: str) -> dict:
        payload = {"from": {"type": "user", "email": from_email}, "body": body}
        return await self._request("POST", "/conversations", json=payload)

    async def reply_to_conversation(self, conversation_id: str, body: str, message_type: str = "comment",
                                    admin_id: str = None) -> dict:
        payload = {"message_type": message_type, "body": body, "type": "admin"}
        if admin_id: payload["admin_id"] = admin_id
        return await self._request("POST", f"/conversations/{conversation_id}/reply", json=payload)

    async def tag_contact(self, contact_id: str, tag_name: str) -> dict:
        # First find or create tag
        tags = await self._request("GET", "/tags")
        tag_id = None
        for t in tags.get("data", []):
            if t["name"] == tag_name:
                tag_id = t["id"]
                break
        if not tag_id:
            tag = await self._request("POST", "/tags", json={"name": tag_name})
            tag_id = tag["id"]
        return await self._request("POST", f"/contacts/{contact_id}/tags", json={"id": tag_id})

    async def create_note(self, contact_id: str, body: str, admin_id: str = None) -> dict:
        payload = {"body": body}
        if admin_id: payload["admin_id"] = admin_id
        return await self._request("POST", f"/contacts/{contact_id}/notes", json=payload)
