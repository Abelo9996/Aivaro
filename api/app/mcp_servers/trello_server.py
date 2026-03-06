"""Trello MCP Server — boards, lists, cards."""
from app.mcp_servers.base import BaseMCPServer


class TrelloMCPServer(BaseMCPServer):
    provider = "trello"

    def __init__(self, api_key: str, api_token: str):
        super().__init__()
        from app.services.integrations.trello_service import TrelloService
        self.svc = TrelloService(api_key=api_key, api_token=api_token)
        self._register_tools()

    def _register_tools(self):
        self._register("trello_list_boards", "List all Trello boards for the authenticated user.", {
            "type": "object", "properties": {},
        }, self._list_boards)

        self._register("trello_list_lists", "List all lists on a Trello board.", {
            "type": "object",
            "properties": {"board_id": {"type": "string", "description": "Trello board ID"}},
            "required": ["board_id"],
        }, self._list_lists)

        self._register("trello_list_cards", "List all cards in a Trello list.", {
            "type": "object",
            "properties": {"list_id": {"type": "string", "description": "Trello list ID"}},
            "required": ["list_id"],
        }, self._list_cards)

        self._register("trello_create_card", "Create a new card on a Trello list.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string", "description": "List ID to add card to"},
                "name": {"type": "string", "description": "Card title"},
                "desc": {"type": "string", "description": "Card description"},
                "due": {"type": "string", "description": "Due date (ISO 8601)"},
            },
            "required": ["list_id", "name"],
        }, self._create_card)

        self._register("trello_update_card", "Update a Trello card.", {
            "type": "object",
            "properties": {
                "card_id": {"type": "string", "description": "Card ID"},
                "name": {"type": "string", "description": "New card title"},
                "desc": {"type": "string", "description": "New description"},
                "closed": {"type": "boolean", "description": "Archive the card"},
            },
            "required": ["card_id"],
        }, self._update_card)

        self._register("trello_move_card", "Move a Trello card to a different list.", {
            "type": "object",
            "properties": {
                "card_id": {"type": "string", "description": "Card ID"},
                "list_id": {"type": "string", "description": "Destination list ID"},
            },
            "required": ["card_id", "list_id"],
        }, self._move_card)

        self._register("trello_add_comment", "Add a comment to a Trello card.", {
            "type": "object",
            "properties": {
                "card_id": {"type": "string", "description": "Card ID"},
                "text": {"type": "string", "description": "Comment text"},
            },
            "required": ["card_id", "text"],
        }, self._add_comment)

        self._register("trello_delete_card", "Delete a Trello card.", {
            "type": "object",
            "properties": {"card_id": {"type": "string", "description": "Card ID"}},
            "required": ["card_id"],
        }, self._delete_card)

        self._register("trello_create_list", "Create a new list on a Trello board.", {
            "type": "object",
            "properties": {
                "board_id": {"type": "string", "description": "Board ID"},
                "name": {"type": "string", "description": "List name"},
            },
            "required": ["board_id", "name"],
        }, self._create_list)

    async def _list_boards(self) -> dict:
        boards = await self.svc.list_boards()
        return {"boards": boards, "count": len(boards)}

    async def _list_lists(self, board_id: str) -> dict:
        lists = await self.svc.list_lists(board_id)
        return {"lists": lists, "count": len(lists)}

    async def _list_cards(self, list_id: str) -> dict:
        cards = await self.svc.list_cards(list_id)
        return {"cards": cards, "count": len(cards)}

    async def _create_card(self, list_id: str, name: str, desc: str = "", due: str = None) -> dict:
        return await self.svc.create_card(list_id, name, desc, due)

    async def _update_card(self, card_id: str, **fields) -> dict:
        return await self.svc.update_card(card_id, **fields)

    async def _move_card(self, card_id: str, list_id: str) -> dict:
        return await self.svc.move_card(card_id, list_id)

    async def _add_comment(self, card_id: str, text: str) -> dict:
        return await self.svc.add_comment(card_id, text)

    async def _delete_card(self, card_id: str) -> dict:
        await self.svc.delete_card(card_id)
        return {"deleted": True, "card_id": card_id}

    async def _create_list(self, board_id: str, name: str) -> dict:
        return await self.svc.create_list(board_id, name)

    async def close(self):
        await self.svc.close()
