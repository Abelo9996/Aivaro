"""
Monday.com Integration Service — boards, items, updates.
"""
import httpx
from typing import Optional, Any


class MondayService:
    """Service for Monday.com GraphQL API."""

    BASE_URL = "https://api.monday.com/v2"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _gql(self, query: str, variables: dict = None) -> dict:
        client = await self._get_client()
        body = {"query": query}
        if variables: body["variables"] = variables
        resp = await client.post(self.BASE_URL, json=body,
                                 headers={"Authorization": self.api_key, "Content-Type": "application/json"})
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise Exception(data["errors"][0].get("message", str(data["errors"])))
        return data.get("data", {})

    async def list_boards(self, limit: int = 50) -> list:
        result = await self._gql(f"{{ boards(limit: {limit}) {{ id name state board_kind }} }}")
        return result.get("boards", [])

    async def get_board(self, board_id: str) -> dict:
        result = await self._gql(f'{{ boards(ids: [{board_id}]) {{ id name columns {{ id title type }} groups {{ id title }} }} }}')
        boards = result.get("boards", [])
        return boards[0] if boards else {}

    async def create_item(self, board_id: str, item_name: str, group_id: str = None,
                          column_values: dict = None) -> dict:
        import json
        cols = json.dumps(json.dumps(column_values)) if column_values else '"{}"'
        group_part = f', group_id: "{group_id}"' if group_id else ""
        query = f'mutation {{ create_item(board_id: {board_id}, item_name: "{item_name}"{group_part}, column_values: {cols}) {{ id name }} }}'
        result = await self._gql(query)
        return result.get("create_item", {})

    async def get_items(self, board_id: str, limit: int = 50) -> list:
        result = await self._gql(f'{{ boards(ids: [{board_id}]) {{ items_page(limit: {limit}) {{ items {{ id name column_values {{ id text value }} }} }} }} }}')
        boards = result.get("boards", [])
        if boards:
            return boards[0].get("items_page", {}).get("items", [])
        return []

    async def update_item_name(self, board_id: str, item_id: str, new_name: str) -> dict:
        import json
        result = await self._gql(f'mutation {{ change_simple_column_value(board_id: {board_id}, item_id: {item_id}, column_id: "name", value: {json.dumps(new_name)}) {{ id name }} }}')
        return result.get("change_simple_column_value", {})

    async def update_column_values(self, board_id: str, item_id: str, column_values: dict) -> dict:
        import json
        cols = json.dumps(json.dumps(column_values))
        result = await self._gql(f'mutation {{ change_multiple_column_values(board_id: {board_id}, item_id: {item_id}, column_values: {cols}) {{ id name }} }}')
        return result.get("change_multiple_column_values", {})

    async def create_update(self, item_id: str, body: str) -> dict:
        import json
        result = await self._gql(f'mutation {{ create_update(item_id: {item_id}, body: {json.dumps(body)}) {{ id body }} }}')
        return result.get("create_update", {})

    async def create_group(self, board_id: str, group_name: str) -> dict:
        import json
        result = await self._gql(f'mutation {{ create_group(board_id: {board_id}, group_name: {json.dumps(group_name)}) {{ id title }} }}')
        return result.get("create_group", {})

    async def delete_item(self, item_id: str) -> dict:
        result = await self._gql(f'mutation {{ delete_item(item_id: {item_id}) {{ id }} }}')
        return result.get("delete_item", {})
