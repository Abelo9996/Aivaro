"""Telegram MCP Server — messaging, photos, webhooks."""
from app.mcp_servers.base import BaseMCPServer


class TelegramMCPServer(BaseMCPServer):
    provider = "telegram"

    def __init__(self, bot_token: str):
        super().__init__()
        from app.services.integrations.telegram_service import TelegramService
        self.svc = TelegramService(bot_token=bot_token)
        self._register_tools()

    def _register_tools(self):
        self._register("telegram_send_message", "Send a text message via Telegram bot.", {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "Chat ID or @channel username"},
                "text": {"type": "string", "description": "Message text"},
                "parse_mode": {"type": "string", "description": "Parse mode: HTML, Markdown, or MarkdownV2"},
                "disable_notification": {"type": "boolean", "description": "Send silently", "default": False},
            },
            "required": ["chat_id", "text"],
        }, self._send_message)

        self._register("telegram_send_photo", "Send a photo via Telegram bot.", {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "Chat ID or @channel username"},
                "photo": {"type": "string", "description": "Photo URL or file_id"},
                "caption": {"type": "string", "description": "Photo caption"},
            },
            "required": ["chat_id", "photo"],
        }, self._send_photo)

        self._register("telegram_send_document", "Send a document via Telegram bot.", {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "Chat ID or @channel username"},
                "document": {"type": "string", "description": "Document URL or file_id"},
                "caption": {"type": "string", "description": "Document caption"},
            },
            "required": ["chat_id", "document"],
        }, self._send_document)

        self._register("telegram_get_updates", "Get incoming updates (messages) for the bot.", {
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "description": "Update offset to start from"},
                "limit": {"type": "integer", "description": "Max updates to retrieve", "default": 100},
            },
        }, self._get_updates)

        self._register("telegram_get_chat", "Get info about a chat.", {
            "type": "object",
            "properties": {
                "chat_id": {"type": "string", "description": "Chat ID or @channel username"},
            },
            "required": ["chat_id"],
        }, self._get_chat)

        self._register("telegram_set_webhook", "Set a webhook URL for receiving updates.", {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "HTTPS URL for webhook"},
                "secret_token": {"type": "string", "description": "Secret token for webhook verification"},
            },
            "required": ["url"],
        }, self._set_webhook)

        self._register("telegram_delete_webhook", "Remove the current webhook.", {
            "type": "object", "properties": {},
        }, self._delete_webhook)

        self._register("telegram_get_me", "Get bot info (username, name, id).", {
            "type": "object", "properties": {},
        }, self._get_me)

    async def _send_message(self, chat_id: str, text: str, parse_mode: str = None,
                            disable_notification: bool = False) -> dict:
        result = await self.svc.send_message(chat_id, text, parse_mode, disable_notification)
        return {"sent": True, "message_id": result.get("message_id"), "chat_id": chat_id}

    async def _send_photo(self, chat_id: str, photo: str, caption: str = "") -> dict:
        result = await self.svc.send_photo(chat_id, photo, caption)
        return {"sent": True, "message_id": result.get("message_id")}

    async def _send_document(self, chat_id: str, document: str, caption: str = "") -> dict:
        result = await self.svc.send_document(chat_id, document, caption)
        return {"sent": True, "message_id": result.get("message_id")}

    async def _get_updates(self, offset: int = None, limit: int = 100) -> dict:
        updates = await self.svc.get_updates(offset, limit)
        return {"updates": updates, "count": len(updates)}

    async def _get_chat(self, chat_id: str) -> dict:
        return await self.svc.get_chat(chat_id)

    async def _set_webhook(self, url: str, secret_token: str = None) -> dict:
        await self.svc.set_webhook(url, secret_token)
        return {"webhook_set": True, "url": url}

    async def _delete_webhook(self) -> dict:
        await self.svc.delete_webhook()
        return {"webhook_deleted": True}

    async def _get_me(self) -> dict:
        return await self.svc.get_me()

    async def close(self):
        await self.svc.close()
