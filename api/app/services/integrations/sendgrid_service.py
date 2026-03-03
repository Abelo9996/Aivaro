"""
SendGrid Integration Service — transactional email, contacts.
"""
import httpx
from typing import Optional, Any


class SendGridService:
    """Service for SendGrid v3 API."""

    BASE_URL = "https://api.sendgrid.com/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    @property
    def headers(self) -> dict:
        return {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

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

    async def send_email(self, to: str, from_email: str, subject: str, html_content: str = "",
                         text_content: str = "", from_name: str = "") -> dict:
        body = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": from_email},
            "subject": subject,
            "content": [],
        }
        if from_name: body["from"]["name"] = from_name
        if text_content: body["content"].append({"type": "text/plain", "value": text_content})
        if html_content: body["content"].append({"type": "text/html", "value": html_content})
        if not body["content"]:
            body["content"].append({"type": "text/plain", "value": ""})
        return await self._request("POST", "/mail/send", json=body)

    async def send_template_email(self, to: str, from_email: str, template_id: str,
                                  dynamic_data: dict = None, from_name: str = "") -> dict:
        body = {
            "personalizations": [{"to": [{"email": to}], "dynamic_template_data": dynamic_data or {}}],
            "from": {"email": from_email},
            "template_id": template_id,
        }
        if from_name: body["from"]["name"] = from_name
        return await self._request("POST", "/mail/send", json=body)

    async def add_contact(self, email: str, first_name: str = "", last_name: str = "",
                          custom_fields: dict = None) -> dict:
        contact = {"email": email}
        if first_name: contact["first_name"] = first_name
        if last_name: contact["last_name"] = last_name
        if custom_fields: contact["custom_fields"] = custom_fields
        return await self._request("PUT", "/marketing/contacts", json={"contacts": [contact]})

    async def search_contacts(self, query: str) -> list:
        result = await self._request("POST", "/marketing/contacts/search", json={"query": query})
        return result.get("result", [])

    async def list_contacts(self, limit: int = 50) -> list:
        result = await self._request("GET", "/marketing/contacts", params={"page_size": limit})
        return result.get("result", [])

    async def delete_contacts(self, ids: list) -> dict:
        return await self._request("DELETE", "/marketing/contacts", params={"ids": ",".join(ids)})

    async def list_templates(self) -> list:
        result = await self._request("GET", "/templates", params={"generations": "dynamic"})
        return result.get("templates", [])

    async def get_template(self, template_id: str) -> dict:
        return await self._request("GET", f"/templates/{template_id}")
