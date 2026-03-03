"""Slack MCP Server — messaging, channels, users, reactions."""
from app.mcp_servers.base import BaseMCPServer


class SlackMCPServer(BaseMCPServer):
    provider = "slack"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.slack_service import SlackService
        self.svc = SlackService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("send_slack", "Send a message to a Slack channel.", {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel name (e.g. #general) or ID"},
                "message": {"type": "string", "description": "Message text (supports Slack markdown)"},
            },
            "required": ["channel", "message"],
        }, self._send_message)

        self._register("slack_send_dm", "Send a direct message to a Slack user by email.", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "User's email address"},
                "message": {"type": "string", "description": "Message text"},
            },
            "required": ["email", "message"],
        }, self._send_dm)

        self._register("slack_list_channels", "List Slack channels.", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 100},
            },
        }, self._list_channels)

        self._register("slack_list_users", "List Slack workspace users.", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 100},
            },
        }, self._list_users)

        self._register("slack_read_history", "Read recent messages from a Slack channel.", {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel name or ID"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["channel"],
        }, self._read_history)

        self._register("slack_find_user_by_email", "Find a Slack user by email address.", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "User email address"},
            },
            "required": ["email"],
        }, self._find_user_by_email)

        self._register("slack_get_channel_info", "Get information about a Slack channel.", {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel name or ID"},
            },
            "required": ["channel"],
        }, self._get_channel_info)

        self._register("slack_add_reaction", "Add an emoji reaction to a message.", {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel ID"},
                "timestamp": {"type": "string", "description": "Message timestamp"},
                "emoji": {"type": "string", "description": "Emoji name (without colons, e.g. 'thumbsup')"},
            },
            "required": ["channel", "timestamp", "emoji"],
        }, self._add_reaction)

        self._register("slack_update_message", "Update an existing Slack message.", {
            "type": "object",
            "properties": {
                "channel": {"type": "string", "description": "Channel ID"},
                "timestamp": {"type": "string", "description": "Message timestamp to update"},
                "message": {"type": "string", "description": "New message text"},
            },
            "required": ["channel", "timestamp", "message"],
        }, self._update_message)

        self._register("slack_find_channel", "Find a Slack channel by name.", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Channel name (without #)"},
            },
            "required": ["name"],
        }, self._find_channel)

        self._register("slack_get_user_info", "Get detailed info about a Slack user.", {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Slack user ID"},
            },
            "required": ["user_id"],
        }, self._get_user_info)

    # ── Handlers ───────────────────────────────────────────────

    async def _send_message(self, channel: str, message: str) -> dict:
        ch_id = channel.lstrip("#")
        if not ch_id.startswith("C"):
            ch = await self.svc.find_channel_by_name(ch_id)
            ch_id = ch["id"] if ch else ch_id
        result = await self.svc.send_message(ch_id, message)
        return {"message_sent": True, "channel": channel, "ts": result.get("ts")}

    async def _send_dm(self, email: str, message: str) -> dict:
        result = await self.svc.send_dm(email, message)
        return {"dm_sent": True, "email": email, "ts": result.get("ts")}

    async def _list_channels(self, limit: int = 100) -> dict:
        channels = await self.svc.list_channels(limit=limit)
        return {"channels": channels, "count": len(channels)}

    async def _list_users(self, limit: int = 100) -> dict:
        users = await self.svc.list_users(limit=limit)
        return {"users": users, "count": len(users)}

    async def _read_history(self, channel: str, limit: int = 20) -> dict:
        ch_id = channel.lstrip("#")
        if not ch_id.startswith("C"):
            ch = await self.svc.find_channel_by_name(ch_id)
            ch_id = ch["id"] if ch else ch_id
        messages = await self.svc.get_channel_history(ch_id, limit=limit)
        return {"messages": messages, "count": len(messages)}

    async def _find_user_by_email(self, email: str) -> dict:
        user = await self.svc.find_user_by_email(email)
        return {"user": user, "found": user is not None}

    async def _get_channel_info(self, channel: str) -> dict:
        ch_id = channel.lstrip("#")
        if not ch_id.startswith("C"):
            ch = await self.svc.find_channel_by_name(ch_id)
            ch_id = ch["id"] if ch else ch_id
        info = await self.svc.get_channel_info(ch_id)
        return {"channel": info}

    async def _add_reaction(self, channel: str, timestamp: str, emoji: str) -> dict:
        await self.svc.add_reaction(channel, timestamp, emoji)
        return {"reaction_added": True, "emoji": emoji}

    async def _update_message(self, channel: str, timestamp: str, message: str) -> dict:
        result = await self.svc.update_message(channel, timestamp, message)
        return {"message_updated": True, "ts": result.get("ts")}

    async def _find_channel(self, name: str) -> dict:
        ch = await self.svc.find_channel_by_name(name)
        return {"channel": ch, "found": ch is not None}

    async def _get_user_info(self, user_id: str) -> dict:
        info = await self.svc.get_user_info(user_id)
        return {"user": info}

    async def close(self):
        await self.svc.close()
