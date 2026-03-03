"""Twilio MCP Server — SMS, WhatsApp, voice calls, phone lookup."""
from app.mcp_servers.base import BaseMCPServer


class TwilioMCPServer(BaseMCPServer):
    provider = "twilio"

    def __init__(self, account_sid: str, auth_token: str, phone_number: str = None):
        super().__init__()
        from app.services.integrations.twilio_service import TwilioService
        self.svc = TwilioService(account_sid=account_sid, auth_token=auth_token, default_from=phone_number)
        self.phone_number = phone_number
        self._register_tools()

    def _register_tools(self):
        self._register("twilio_send_sms", "Send an SMS message.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient phone number (E.164 format)"},
                "body": {"type": "string", "description": "Message text"},
            },
            "required": ["to", "body"],
        }, self._send_sms)

        self._register("twilio_send_whatsapp", "Send a WhatsApp message.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient phone number (E.164)"},
                "body": {"type": "string", "description": "Message text"},
                "media_url": {"type": "string", "description": "URL of media to attach"},
            },
            "required": ["to", "body"],
        }, self._send_whatsapp)

        self._register("twilio_make_call", "Make an outbound phone call with text-to-speech.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient phone number (E.164)"},
                "message": {"type": "string", "description": "Text-to-speech message"},
            },
            "required": ["to", "message"],
        }, self._make_call)

        self._register("twilio_list_messages", "List recent SMS/MMS messages.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Filter by recipient number"},
                "from_number": {"type": "string", "description": "Filter by sender number"},
                "limit": {"type": "integer", "default": 20},
            },
        }, self._list_messages)

        self._register("twilio_list_calls", "List recent phone calls.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Filter by recipient number"},
                "from_number": {"type": "string", "description": "Filter by caller number"},
                "limit": {"type": "integer", "default": 20},
            },
        }, self._list_calls)

        self._register("twilio_get_message", "Get details of a specific SMS message.", {
            "type": "object",
            "properties": {
                "message_sid": {"type": "string", "description": "Twilio message SID"},
            },
            "required": ["message_sid"],
        }, self._get_message)

        self._register("twilio_get_call", "Get details of a specific phone call.", {
            "type": "object",
            "properties": {
                "call_sid": {"type": "string", "description": "Twilio call SID"},
            },
            "required": ["call_sid"],
        }, self._get_call)

        self._register("twilio_lookup_phone", "Look up information about a phone number.", {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string", "description": "Phone number to look up"},
            },
            "required": ["phone_number"],
        }, self._lookup_phone)

        self._register("twilio_list_phone_numbers", "List phone numbers in the Twilio account.", {
            "type": "object", "properties": {},
        }, self._list_phone_numbers)

    # ── Handlers ───────────────────────────────────────────────

    async def _send_sms(self, to: str, body: str) -> dict:
        result = await self.svc.send_sms(to, body)
        return result

    async def _send_whatsapp(self, to: str, body: str, media_url: str = None) -> dict:
        result = await self.svc.send_whatsapp(to, body, media_url=media_url)
        return result

    async def _make_call(self, to: str, message: str) -> dict:
        result = await self.svc.make_call(to, message)
        return result

    async def _list_messages(self, to: str = None, from_number: str = None, limit: int = 20) -> dict:
        result = await self.svc.list_messages(to=to, from_number=from_number, limit=limit)
        return {"messages": result, "count": len(result)}

    async def _list_calls(self, to: str = None, from_number: str = None, limit: int = 20) -> dict:
        result = await self.svc.list_calls(to=to, from_number=from_number, limit=limit)
        return {"calls": result, "count": len(result)}

    async def _get_message(self, message_sid: str) -> dict:
        result = await self.svc.get_message(message_sid)
        return {"message": result}

    async def _get_call(self, call_sid: str) -> dict:
        result = await self.svc.get_call(call_sid)
        return {"call": result}

    async def _lookup_phone(self, phone_number: str) -> dict:
        result = await self.svc.lookup_phone_number(phone_number)
        return {"lookup": result}

    async def _list_phone_numbers(self) -> dict:
        result = await self.svc.list_phone_numbers()
        return {"phone_numbers": result, "count": len(result)}

    async def close(self):
        await self.svc.close()
