"""
HubSpot Integration Service — CRM contacts, companies, deals, tickets.
"""
import httpx
from typing import Optional, List, Any


class HubSpotService:
    """Service for interacting with HubSpot CRM API v3."""

    BASE_URL = "https://api.hubapi.com"

    def __init__(self, access_token: str):
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        client = await self._get_client()
        url = f"{self.BASE_URL}{path}"
        resp = await client.request(method, url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()

    # ── Contacts ───────────────────────────────────────────────

    async def create_contact(self, properties: dict) -> dict:
        return await self._request("POST", "/crm/v3/objects/contacts", json={"properties": properties})

    async def update_contact(self, contact_id: str, properties: dict) -> dict:
        return await self._request("PATCH", f"/crm/v3/objects/contacts/{contact_id}", json={"properties": properties})

    async def get_contact(self, contact_id: str, properties: list = None) -> dict:
        params = {}
        if properties:
            params["properties"] = ",".join(properties)
        return await self._request("GET", f"/crm/v3/objects/contacts/{contact_id}", params=params)

    async def search_contacts(self, query: str, limit: int = 10) -> list:
        body = {
            "query": query,
            "limit": limit,
        }
        result = await self._request("POST", "/crm/v3/objects/contacts/search", json=body)
        return result.get("results", [])

    async def list_contacts(self, limit: int = 50, properties: list = None) -> list:
        params = {"limit": limit}
        if properties:
            params["properties"] = ",".join(properties)
        result = await self._request("GET", "/crm/v3/objects/contacts", params=params)
        return result.get("results", [])

    async def delete_contact(self, contact_id: str) -> dict:
        return await self._request("DELETE", f"/crm/v3/objects/contacts/{contact_id}")

    # ── Companies ──────────────────────────────────────────────

    async def create_company(self, properties: dict) -> dict:
        return await self._request("POST", "/crm/v3/objects/companies", json={"properties": properties})

    async def update_company(self, company_id: str, properties: dict) -> dict:
        return await self._request("PATCH", f"/crm/v3/objects/companies/{company_id}", json={"properties": properties})

    async def get_company(self, company_id: str) -> dict:
        return await self._request("GET", f"/crm/v3/objects/companies/{company_id}")

    async def search_companies(self, query: str, limit: int = 10) -> list:
        result = await self._request("POST", "/crm/v3/objects/companies/search", json={"query": query, "limit": limit})
        return result.get("results", [])

    async def list_companies(self, limit: int = 50) -> list:
        result = await self._request("GET", "/crm/v3/objects/companies", params={"limit": limit})
        return result.get("results", [])

    # ── Deals ──────────────────────────────────────────────────

    async def create_deal(self, properties: dict) -> dict:
        return await self._request("POST", "/crm/v3/objects/deals", json={"properties": properties})

    async def update_deal(self, deal_id: str, properties: dict) -> dict:
        return await self._request("PATCH", f"/crm/v3/objects/deals/{deal_id}", json={"properties": properties})

    async def get_deal(self, deal_id: str) -> dict:
        return await self._request("GET", f"/crm/v3/objects/deals/{deal_id}")

    async def search_deals(self, query: str, limit: int = 10) -> list:
        result = await self._request("POST", "/crm/v3/objects/deals/search", json={"query": query, "limit": limit})
        return result.get("results", [])

    async def list_deals(self, limit: int = 50) -> list:
        result = await self._request("GET", "/crm/v3/objects/deals", params={"limit": limit})
        return result.get("results", [])

    # ── Tickets ────────────────────────────────────────────────

    async def create_ticket(self, properties: dict) -> dict:
        return await self._request("POST", "/crm/v3/objects/tickets", json={"properties": properties})

    async def update_ticket(self, ticket_id: str, properties: dict) -> dict:
        return await self._request("PATCH", f"/crm/v3/objects/tickets/{ticket_id}", json={"properties": properties})

    async def get_ticket(self, ticket_id: str) -> dict:
        return await self._request("GET", f"/crm/v3/objects/tickets/{ticket_id}")

    async def list_tickets(self, limit: int = 50) -> list:
        result = await self._request("GET", "/crm/v3/objects/tickets", params={"limit": limit})
        return result.get("results", [])

    # ── Associations ───────────────────────────────────────────

    async def create_association(self, from_type: str, from_id: str, to_type: str, to_id: str, assoc_type: str) -> dict:
        return await self._request(
            "PUT",
            f"/crm/v3/objects/{from_type}/{from_id}/associations/{to_type}/{to_id}/{assoc_type}",
        )

    async def list_associations(self, object_type: str, object_id: str, to_type: str) -> list:
        result = await self._request("GET", f"/crm/v3/objects/{object_type}/{object_id}/associations/{to_type}")
        return result.get("results", [])

    # ── Pipelines ──────────────────────────────────────────────

    async def list_pipelines(self, object_type: str = "deals") -> list:
        result = await self._request("GET", f"/crm/v3/pipelines/{object_type}")
        return result.get("results", [])

    async def get_pipeline_stages(self, pipeline_id: str, object_type: str = "deals") -> list:
        result = await self._request("GET", f"/crm/v3/pipelines/{object_type}/{pipeline_id}/stages")
        return result.get("results", [])

    # ── Owners ─────────────────────────────────────────────────

    async def list_owners(self) -> list:
        result = await self._request("GET", "/crm/v3/owners")
        return result.get("results", [])

    async def get_owner_by_email(self, email: str) -> Optional[dict]:
        owners = await self.list_owners()
        for o in owners:
            if o.get("email") == email:
                return o
        return None
