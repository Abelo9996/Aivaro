"""Discord MCP Server — messages, channels, members, roles."""
from app.mcp_servers.base import BaseMCPServer


class DiscordMCPServer(BaseMCPServer):
    provider = "discord"

    def __init__(self, bot_token: str, guild_id: str = None):
        super().__init__()
        from app.services.integrations.discord_service import DiscordService
        self.svc = DiscordService(bot_token=bot_token)
        self.guild_id = guild_id  # default guild for convenience
        self._register_tools()

    def _register_tools(self):
        # ── Messages ──
        self._register("discord_send_message", "Send a message to a Discord channel.", {
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "content": {"type": "string"},
            },
            "required": ["channel_id", "content"],
        }, self._send_message)

        self._register("discord_get_messages", "Get recent messages from a Discord channel.", {
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["channel_id"],
        }, self._get_messages)

        self._register("discord_delete_message", "Delete a Discord message.", {
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "message_id": {"type": "string"},
            },
            "required": ["channel_id", "message_id"],
        }, self._delete_message)

        self._register("discord_add_reaction", "Add an emoji reaction to a Discord message.", {
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "message_id": {"type": "string"},
                "emoji": {"type": "string", "description": "Unicode emoji or custom emoji string"},
            },
            "required": ["channel_id", "message_id", "emoji"],
        }, self._add_reaction)

        # ── Channels ──
        self._register("discord_create_channel", "Create a Discord channel in a guild.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string", "description": "Guild/server ID (uses default if omitted)"},
                "name": {"type": "string"},
                "type": {"type": "integer", "description": "0=text, 2=voice, 4=category, 13=stage", "default": 0},
                "topic": {"type": "string"},
            },
            "required": ["name"],
        }, self._create_channel)

        self._register("discord_delete_channel", "Delete a Discord channel.", {
            "type": "object",
            "properties": {"channel_id": {"type": "string"}},
            "required": ["channel_id"],
        }, self._delete_channel)

        self._register("discord_list_channels", "List channels in a Discord guild.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string", "description": "Guild ID (uses default if omitted)"},
            },
        }, self._list_channels)

        self._register("discord_rename_channel", "Rename a Discord channel.", {
            "type": "object",
            "properties": {
                "channel_id": {"type": "string"},
                "name": {"type": "string"},
                "topic": {"type": "string"},
            },
            "required": ["channel_id"],
        }, self._rename_channel)

        # ── Members ──
        self._register("discord_get_member", "Get a Discord guild member.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
                "user_id": {"type": "string"},
            },
            "required": ["user_id"],
        }, self._get_member)

        self._register("discord_list_members", "List members of a Discord guild.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
                "limit": {"type": "integer", "default": 100},
            },
        }, self._list_members)

        self._register("discord_kick_member", "Kick a member from a Discord guild.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
                "user_id": {"type": "string"},
            },
            "required": ["user_id"],
        }, self._kick_member)

        self._register("discord_ban_member", "Ban a member from a Discord guild.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
                "user_id": {"type": "string"},
                "reason": {"type": "string"},
            },
            "required": ["user_id"],
        }, self._ban_member)

        # ── Roles ──
        self._register("discord_add_role", "Add a role to a guild member.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
                "user_id": {"type": "string"},
                "role_id": {"type": "string"},
            },
            "required": ["user_id", "role_id"],
        }, self._add_role)

        self._register("discord_remove_role", "Remove a role from a guild member.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
                "user_id": {"type": "string"},
                "role_id": {"type": "string"},
            },
            "required": ["user_id", "role_id"],
        }, self._remove_role)

        self._register("discord_list_roles", "List roles in a Discord guild.", {
            "type": "object",
            "properties": {
                "guild_id": {"type": "string"},
            },
        }, self._list_roles)

    # ── Handlers ───────────────────────────────────────────────

    def _gid(self, guild_id: str = None) -> str:
        return guild_id or self.guild_id or ""

    async def _send_message(self, channel_id: str, content: str) -> dict:
        return await self.svc.send_message(channel_id, content)

    async def _get_messages(self, channel_id: str, limit: int = 50) -> dict:
        msgs = await self.svc.get_channel_messages(channel_id, limit)
        return {"messages": msgs, "count": len(msgs)}

    async def _delete_message(self, channel_id: str, message_id: str) -> dict:
        await self.svc.delete_message(channel_id, message_id)
        return {"deleted": True}

    async def _add_reaction(self, channel_id: str, message_id: str, emoji: str) -> dict:
        await self.svc.add_reaction(channel_id, message_id, emoji)
        return {"reaction_added": True}

    async def _create_channel(self, name: str, guild_id: str = None, type: int = 0, topic: str = "") -> dict:
        return await self.svc.create_channel(self._gid(guild_id), name, type, topic)

    async def _delete_channel(self, channel_id: str) -> dict:
        await self.svc.delete_channel(channel_id)
        return {"deleted": True}

    async def _list_channels(self, guild_id: str = None) -> dict:
        channels = await self.svc.list_guild_channels(self._gid(guild_id))
        return {"channels": channels, "count": len(channels)}

    async def _rename_channel(self, channel_id: str, name: str = None, topic: str = None) -> dict:
        return await self.svc.modify_channel(channel_id, name, topic)

    async def _get_member(self, user_id: str, guild_id: str = None) -> dict:
        return await self.svc.get_member(self._gid(guild_id), user_id)

    async def _list_members(self, guild_id: str = None, limit: int = 100) -> dict:
        members = await self.svc.list_members(self._gid(guild_id), limit)
        return {"members": members, "count": len(members)}

    async def _kick_member(self, user_id: str, guild_id: str = None) -> dict:
        await self.svc.kick_member(self._gid(guild_id), user_id)
        return {"kicked": True}

    async def _ban_member(self, user_id: str, guild_id: str = None, reason: str = "") -> dict:
        await self.svc.ban_member(self._gid(guild_id), user_id, reason)
        return {"banned": True}

    async def _add_role(self, user_id: str, role_id: str, guild_id: str = None) -> dict:
        await self.svc.add_role(self._gid(guild_id), user_id, role_id)
        return {"role_added": True}

    async def _remove_role(self, user_id: str, role_id: str, guild_id: str = None) -> dict:
        await self.svc.remove_role(self._gid(guild_id), user_id, role_id)
        return {"role_removed": True}

    async def _list_roles(self, guild_id: str = None) -> dict:
        roles = await self.svc.list_roles(self._gid(guild_id))
        return {"roles": roles, "count": len(roles)}

    async def close(self):
        await self.svc.close()
