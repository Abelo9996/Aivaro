"""WhatsApp Business MCP Server — messages, templates, media."""
from app.mcp_servers.base import BaseMCPServer


class WhatsAppMCPServer(BaseMCPServer):
    provider = "whatsapp"

    def __init__(self, access_token: str, phone_number_id: str):
        super().__init__()
        from app.services.integrations.whatsapp_service import WhatsAppService
        self.svc = WhatsAppService(access_token=access_token, phone_number_id=phone_number_id)
        self._register_tools()

    def _register_tools(self):
        self._register("whatsapp_send_message", "Send a WhatsApp text message.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient phone (E.164 format)"},
                "body": {"type": "string"},
            },
            "required": ["to", "body"],
        }, self._send_text)

        self._register("whatsapp_send_template", "Send a WhatsApp template message.", {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "template_name": {"type": "string"},
                "language_code": {"type": "string", "default": "en_US"},
                "components": {"type": "array", "items": {"type": "object"}, "description": "Template variable components"},
            },
            "required": ["to", "template_name"],
        }, self._send_template)

        self._register("whatsapp_send_media", "Send a media message (image, video, document) via WhatsApp.", {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "media_type": {"type": "string", "description": "image, video, document, audio"},
                "media_url": {"type": "string"},
                "caption": {"type": "string"},
            },
            "required": ["to", "media_type", "media_url"],
        }, self._send_media)

        self._register("whatsapp_mark_read", "Mark a WhatsApp message as read.", {
            "type": "object",
            "properties": {"message_id": {"type": "string"}},
            "required": ["message_id"],
        }, self._mark_read)

    async def _send_text(self, to: str, body: str) -> dict:
        result = await self.svc.send_text(to, body)
        return {"sent": True, "to": to, **result}

    async def _send_template(self, to: str, template_name: str, language_code: str = "en_US",
                             components: list = None) -> dict:
        result = await self.svc.send_template(to, template_name, language_code, components)
        return {"sent": True, "to": to, "template": template_name, **result}

    async def _send_media(self, to: str, media_type: str, media_url: str, caption: str = "") -> dict:
        result = await self.svc.send_media(to, media_type, media_url=media_url, caption=caption)
        return {"sent": True, "to": to, **result}

    async def _mark_read(self, message_id: str) -> dict:
        await self.svc.mark_as_read(message_id)
        return {"marked_read": True}

    async def close(self):
        await self.svc.close()
