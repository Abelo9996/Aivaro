"""
WhatsApp Business Integration Service — Cloud API messages, templates, contacts.
"""
import httpx
from typing import Optional, Any


class WhatsAppService:
    """Service for WhatsApp Business Cloud API (Meta)."""

    BASE_URL = "https://graph.facebook.com/v18.0"

    def __init__(self, access_token: str, phone_number_id: str):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
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
        return resp.json() if resp.content else {}

    async def send_text(self, to: str, body: str) -> dict:
        return await self._request("POST", f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp", "to": to,
            "type": "text", "text": {"body": body},
        })

    async def send_template(self, to: str, template_name: str, language_code: str = "en_US",
                            components: list = None) -> dict:
        template = {"name": template_name, "language": {"code": language_code}}
        if components: template["components"] = components
        return await self._request("POST", f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp", "to": to,
            "type": "template", "template": template,
        })

    async def send_media(self, to: str, media_type: str, media_url: str = None,
                         media_id: str = None, caption: str = "") -> dict:
        media_obj = {}
        if media_url: media_obj["link"] = media_url
        if media_id: media_obj["id"] = media_id
        if caption: media_obj["caption"] = caption
        return await self._request("POST", f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp", "to": to,
            "type": media_type, media_type: media_obj,
        })

    async def mark_as_read(self, message_id: str) -> dict:
        return await self._request("POST", f"/{self.phone_number_id}/messages", json={
            "messaging_product": "whatsapp", "status": "read", "message_id": message_id,
        })

    async def get_media_url(self, media_id: str) -> dict:
        return await self._request("GET", f"/{media_id}")

    async def get_phone_number_info(self) -> dict:
        return await self._request("GET", f"/{self.phone_number_id}")

    async def list_templates(self, business_id: str) -> list:
        result = await self._request("GET", f"/{business_id}/message_templates")
        return result.get("data", [])
