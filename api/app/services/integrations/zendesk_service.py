"""Zendesk Integration Service — tickets, users."""
import httpx
from typing import Optional, Any
import base64


class ZendeskService:
    """Service for Zendesk REST API v2."""

    def __init__(self, subdomain: str, email: str, api_token: str):
        self.base_url = f"https://{subdomain}.zendesk.com/api/v2"
        self._auth = base64.b64encode(f"{email}/token:{api_token}".encode()).decode()
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

    async def create_ticket(self, subject: str, description: str, priority: str = "normal",
                            requester_email: str = None, tags: list = None) -> dict:
        ticket = {"subject": subject, "description": description, "priority": priority}
        if requester_email: ticket["requester"] = {"email": requester_email}
        if tags: ticket["tags"] = tags
        result = await self._request("POST", "/tickets.json", json={"ticket": ticket})
        return result.get("ticket", result)

    async def update_ticket(self, ticket_id: int, **fields) -> dict:
        result = await self._request("PUT", f"/tickets/{ticket_id}.json", json={"ticket": fields})
        return result.get("ticket", result)

    async def get_ticket(self, ticket_id: int) -> dict:
        result = await self._request("GET", f"/tickets/{ticket_id}.json")
        return result.get("ticket", result)

    async def list_tickets(self, status: str = None, limit: int = 50) -> list:
        params = {"per_page": min(limit, 100)}
        if status: params["status"] = status
        result = await self._request("GET", "/tickets.json", params=params)
        return result.get("tickets", [])

    async def add_comment(self, ticket_id: int, body: str, public: bool = True) -> dict:
        comment = {"body": body, "public": public}
        result = await self._request("PUT", f"/tickets/{ticket_id}.json",
                                     json={"ticket": {"comment": comment}})
        return result.get("ticket", result)

    async def search_tickets(self, query: str) -> list:
        result = await self._request("GET", "/search.json", params={"query": f"type:ticket {query}"})
        return result.get("results", [])

    async def list_users(self, limit: int = 50) -> list:
        result = await self._request("GET", "/users.json", params={"per_page": min(limit, 100)})
        return result.get("users", [])

    async def create_user(self, name: str, email: str, role: str = "end-user") -> dict:
        result = await self._request("POST", "/users.json",
                                     json={"user": {"name": name, "email": email, "role": role}})
        return result.get("user", result)
