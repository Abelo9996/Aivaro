"""Monday.com MCP Server — boards, items, groups, updates."""
from app.mcp_servers.base import BaseMCPServer


class MondayMCPServer(BaseMCPServer):
    provider = "monday"

    def __init__(self, api_key: str):
        super().__init__()
        from app.services.integrations.monday_service import MondayService
        self.svc = MondayService(api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("monday_list_boards", "List Monday.com boards.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_boards)

        self._register("monday_get_board", "Get a Monday.com board with columns and groups.", {
            "type": "object",
            "properties": {"board_id": {"type": "string"}},
            "required": ["board_id"],
        }, self._get_board)

        self._register("monday_create_item", "Create an item on a Monday.com board.", {
            "type": "object",
            "properties": {
                "board_id": {"type": "string"}, "item_name": {"type": "string"},
                "group_id": {"type": "string"},
                "column_values": {"type": "object", "description": "Column ID to value mapping"},
            },
            "required": ["board_id", "item_name"],
        }, self._create_item)

        self._register("monday_get_items", "Get items from a Monday.com board.", {
            "type": "object",
            "properties": {
                "board_id": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["board_id"],
        }, self._get_items)

        self._register("monday_update_item_name", "Rename a Monday.com item.", {
            "type": "object",
            "properties": {
                "board_id": {"type": "string"}, "item_id": {"type": "string"},
                "new_name": {"type": "string"},
            },
            "required": ["board_id", "item_id", "new_name"],
        }, self._update_item_name)

        self._register("monday_update_column_values", "Update column values for a Monday.com item.", {
            "type": "object",
            "properties": {
                "board_id": {"type": "string"}, "item_id": {"type": "string"},
                "column_values": {"type": "object"},
            },
            "required": ["board_id", "item_id", "column_values"],
        }, self._update_column_values)

        self._register("monday_create_update", "Post an update/comment on a Monday.com item.", {
            "type": "object",
            "properties": {
                "item_id": {"type": "string"}, "body": {"type": "string"},
            },
            "required": ["item_id", "body"],
        }, self._create_update)

        self._register("monday_create_group", "Create a group on a Monday.com board.", {
            "type": "object",
            "properties": {
                "board_id": {"type": "string"}, "group_name": {"type": "string"},
            },
            "required": ["board_id", "group_name"],
        }, self._create_group)

        self._register("monday_delete_item", "Delete a Monday.com item.", {
            "type": "object",
            "properties": {"item_id": {"type": "string"}},
            "required": ["item_id"],
        }, self._delete_item)

    async def _list_boards(self, limit: int = 50) -> dict:
        boards = await self.svc.list_boards(limit)
        return {"boards": boards, "count": len(boards)}

    async def _get_board(self, board_id: str) -> dict:
        return await self.svc.get_board(board_id)

    async def _create_item(self, board_id: str, item_name: str, group_id: str = None,
                           column_values: dict = None) -> dict:
        return await self.svc.create_item(board_id, item_name, group_id, column_values)

    async def _get_items(self, board_id: str, limit: int = 50) -> dict:
        items = await self.svc.get_items(board_id, limit)
        return {"items": items, "count": len(items)}

    async def _update_item_name(self, board_id: str, item_id: str, new_name: str) -> dict:
        return await self.svc.update_item_name(board_id, item_id, new_name)

    async def _update_column_values(self, board_id: str, item_id: str, column_values: dict) -> dict:
        return await self.svc.update_column_values(board_id, item_id, column_values)

    async def _create_update(self, item_id: str, body: str) -> dict:
        return await self.svc.create_update(item_id, body)

    async def _create_group(self, board_id: str, group_name: str) -> dict:
        return await self.svc.create_group(board_id, group_name)

    async def _delete_item(self, item_id: str) -> dict:
        await self.svc.delete_item(item_id)
        return {"deleted": True}

    async def close(self):
        await self.svc.close()
