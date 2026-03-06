"""Trello Integration Service — boards, lists, cards."""
import httpx
from typing import Optional, Any


class TrelloService:
    """Service for Trello REST API."""

    BASE_URL = "https://api.trello.com/1"

    def __init__(self, api_key: str, api_token: str):
        self.api_key = api_key
        self.api_token = api_token
        self._client = None

    @property
    def auth_params(self) -> dict:
        return {"key": self.api_key, "token": self.api_token}

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
        merged = {**self.auth_params, **(params or {})}
        resp = await client.request(method, f"{self.BASE_URL}{path}", params=merged, **kwargs)
        resp.raise_for_status()
        return resp.json() if resp.content and resp.status_code != 204 else {}

    async def list_boards(self) -> list:
        return await self._request("GET", "/members/me/boards", params={"fields": "name,url,closed"})

    async def list_lists(self, board_id: str) -> list:
        return await self._request("GET", f"/boards/{board_id}/lists")

    async def list_cards(self, list_id: str) -> list:
        return await self._request("GET", f"/lists/{list_id}/cards")

    async def create_card(self, list_id: str, name: str, desc: str = "", due: str = None) -> dict:
        params = {"idList": list_id, "name": name}
        if desc: params["desc"] = desc
        if due: params["due"] = due
        return await self._request("POST", "/cards", params=params)

    async def update_card(self, card_id: str, **fields) -> dict:
        return await self._request("PUT", f"/cards/{card_id}", params=fields)

    async def move_card(self, card_id: str, list_id: str) -> dict:
        return await self._request("PUT", f"/cards/{card_id}", params={"idList": list_id})

    async def add_comment(self, card_id: str, text: str) -> dict:
        return await self._request("POST", f"/cards/{card_id}/actions/comments", params={"text": text})

    async def delete_card(self, card_id: str) -> dict:
        return await self._request("DELETE", f"/cards/{card_id}")

    async def create_list(self, board_id: str, name: str) -> dict:
        return await self._request("POST", "/lists", params={"idBoard": board_id, "name": name})
