"""Slack MCP Server — messaging, channels, DMs."""
from app.mcp_servers.base import BaseMCPServer


class SlackMCPServer(BaseMCPServer):
    provider = "slack"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.slack_service import SlackService
        self.svc = SlackService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register(
            "send_slack",
            "Send a message to a Slack channel.",
            {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel name (e.g. #general) or ID"},
                    "message": {"type": "string", "description": "Message text"},
                },
                "required": ["channel", "message"],
            },
            self._send_message,
        )
        self._register(
            "slack_send_dm",
            "Send a direct message to a Slack user by email.",
            {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "User's email address"},
                    "message": {"type": "string", "description": "Message text"},
                },
                "required": ["email", "message"],
            },
            self._send_dm,
        )
        self._register(
            "slack_list_channels",
            "List Slack channels.",
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100},
                },
            },
            self._list_channels,
        )
        self._register(
            "slack_read_history",
            "Read recent messages from a Slack channel.",
            {
                "type": "object",
                "properties": {
                    "channel": {"type": "string", "description": "Channel name or ID"},
                    "limit": {"type": "integer", "default": 20},
                },
                "required": ["channel"],
            },
            self._read_history,
        )
        self._register(
            "slack_list_users",
            "List Slack workspace users.",
            {
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "default": 100},
                },
            },
            self._list_users,
        )

    async def _send_message(self, channel: str, message: str) -> dict:
        channel_info = await self.svc.find_channel_by_name(channel)
        channel_id = channel_info["id"] if channel_info else channel
        result = await self.svc.send_message(channel_id, message)
        return {"slack_sent": True, "channel": channel, "message_ts": result.get("ts")}

    async def _send_dm(self, email: str, message: str) -> dict:
        user = await self.svc.find_user_by_email(email)
        if not user:
            return {"error": f"No Slack user found for email: {email}"}
        dm = await self.svc.open_dm(user["id"])
        result = await self.svc.send_message(dm["channel"]["id"], message)
        return {"slack_dm_sent": True, "user_email": email, "message_ts": result.get("ts")}

    async def _list_channels(self, limit: int = 100) -> dict:
        channels = await self.svc.list_channels(limit=limit)
        return {"channels": [{"name": c.get("name"), "id": c.get("id")} for c in channels], "count": len(channels)}

    async def _read_history(self, channel: str, limit: int = 20) -> dict:
        channel_info = await self.svc.find_channel_by_name(channel)
        channel_id = channel_info["id"] if channel_info else channel
        messages = await self.svc.get_channel_history(channel_id, limit=limit)
        return {"messages": messages, "count": len(messages)}

    async def _list_users(self, limit: int = 100) -> dict:
        users = await self.svc.list_users(limit=limit)
        return {"users": [{"name": u.get("real_name", u.get("name")), "email": u.get("profile", {}).get("email"), "id": u.get("id")} for u in users], "count": len(users)}

    async def close(self):
        await self.svc.close()
