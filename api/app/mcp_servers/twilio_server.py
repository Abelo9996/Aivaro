"""Twilio MCP Server — SMS, WhatsApp, voice calls."""
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
        self._register(
            "twilio_send_sms",
            "Send an SMS text message.",
            {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Phone number (e.g. +15551234567)"},
                    "body": {"type": "string", "description": "SMS message text"},
                },
                "required": ["to", "body"],
            },
            self._send_sms,
        )
        self._register(
            "twilio_send_whatsapp",
            "Send a WhatsApp message.",
            {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Phone number"},
                    "body": {"type": "string", "description": "Message text"},
                },
                "required": ["to", "body"],
            },
            self._send_whatsapp,
        )
        self._register(
            "twilio_make_call",
            "Make a phone call with a text-to-speech message.",
            {
                "type": "object",
                "properties": {
                    "to": {"type": "string", "description": "Phone number to call"},
                    "message": {"type": "string", "description": "Message to speak"},
                },
                "required": ["to", "message"],
            },
            self._make_call,
        )
        self._register(
            "twilio_list_messages",
            "List recent SMS messages.",
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                    "to": {"type": "string", "description": "Filter by recipient"},
                    "from_number": {"type": "string", "description": "Filter by sender"},
                },
            },
            self._list_messages,
        )
        self._register(
            "twilio_list_calls",
            "List recent phone calls.",
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 20},
                },
            },
            self._list_calls,
        )

    async def _send_sms(self, to: str, body: str) -> dict:
        result = await self.svc.send_sms(to=to, body=body)
        return {"sms_sent": True, "to": to, "sid": result.get("sid"), "status": result.get("status")}

    async def _send_whatsapp(self, to: str, body: str) -> dict:
        result = await self.svc.send_whatsapp(to=to, body=body)
        return {"whatsapp_sent": True, "to": to, "sid": result.get("sid"), "status": result.get("status")}

    async def _make_call(self, to: str, message: str) -> dict:
        twiml = self.svc.create_say_twiml(message)
        result = await self.svc.make_call(to=to, twiml=twiml)
        return {"call_made": True, "to": to, "sid": result.get("sid"), "status": result.get("status")}

    async def _list_messages(self, limit: int = 20, to: str = None, from_number: str = None) -> dict:
        messages = await self.svc.list_messages(limit=limit, to=to, from_=from_number)
        return {"messages": messages, "count": len(messages)}

    async def _list_calls(self, limit: int = 20) -> dict:
        calls = await self.svc.list_calls(limit=limit)
        return {"calls": calls, "count": len(calls)}

    async def close(self):
        await self.svc.close()
