"""
Discord Integration Service — messages, channels, members, roles.
"""
import httpx
from typing import Optional, List, Any


class DiscordService:
    """Service for interacting with Discord Bot API v10."""

    BASE_URL = "https://discord.com/api/v10"

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        client = await self._get_client()
        url = f"{self.BASE_URL}{path}"
        resp = await client.request(method, url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()

    # ── Messages ───────────────────────────────────────────────

    async def send_message(self, channel_id: str, content: str, embeds: list = None) -> dict:
        body = {"content": content}
        if embeds: body["embeds"] = embeds
        return await self._request("POST", f"/channels/{channel_id}/messages", json=body)

    async def get_message(self, channel_id: str, message_id: str) -> dict:
        return await self._request("GET", f"/channels/{channel_id}/messages/{message_id}")

    async def delete_message(self, channel_id: str, message_id: str) -> dict:
        return await self._request("DELETE", f"/channels/{channel_id}/messages/{message_id}")

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> list:
        return await self._request("GET", f"/channels/{channel_id}/messages", params={"limit": limit})

    async def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> dict:
        # emoji must be URL-encoded for custom emoji
        return await self._request("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me")

    # ── Channels ───────────────────────────────────────────────

    async def create_channel(self, guild_id: str, name: str, channel_type: int = 0, topic: str = "",
                             parent_id: str = None) -> dict:
        body = {"name": name, "type": channel_type}
        if topic: body["topic"] = topic
        if parent_id: body["parent_id"] = parent_id
        return await self._request("POST", f"/guilds/{guild_id}/channels", json=body)

    async def delete_channel(self, channel_id: str) -> dict:
        return await self._request("DELETE", f"/channels/{channel_id}")

    async def get_channel(self, channel_id: str) -> dict:
        return await self._request("GET", f"/channels/{channel_id}")

    async def list_guild_channels(self, guild_id: str) -> list:
        return await self._request("GET", f"/guilds/{guild_id}/channels")

    async def modify_channel(self, channel_id: str, name: str = None, topic: str = None) -> dict:
        body = {}
        if name: body["name"] = name
        if topic is not None: body["topic"] = topic
        return await self._request("PATCH", f"/channels/{channel_id}", json=body)

    # ── Guild Members ──────────────────────────────────────────

    async def get_member(self, guild_id: str, user_id: str) -> dict:
        return await self._request("GET", f"/guilds/{guild_id}/members/{user_id}")

    async def list_members(self, guild_id: str, limit: int = 100) -> list:
        return await self._request("GET", f"/guilds/{guild_id}/members", params={"limit": limit})

    async def kick_member(self, guild_id: str, user_id: str) -> dict:
        return await self._request("DELETE", f"/guilds/{guild_id}/members/{user_id}")

    async def ban_member(self, guild_id: str, user_id: str, reason: str = "") -> dict:
        body = {}
        if reason:
            body["reason"] = reason
        return await self._request("PUT", f"/guilds/{guild_id}/bans/{user_id}", json=body)

    async def unban_member(self, guild_id: str, user_id: str) -> dict:
        return await self._request("DELETE", f"/guilds/{guild_id}/bans/{user_id}")

    # ── Roles ──────────────────────────────────────────────────

    async def add_role(self, guild_id: str, user_id: str, role_id: str) -> dict:
        return await self._request("PUT", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}")

    async def remove_role(self, guild_id: str, user_id: str, role_id: str) -> dict:
        return await self._request("DELETE", f"/guilds/{guild_id}/members/{user_id}/roles/{role_id}")

    async def list_roles(self, guild_id: str) -> list:
        return await self._request("GET", f"/guilds/{guild_id}/roles")

    async def create_role(self, guild_id: str, name: str, color: int = 0, permissions: str = "0") -> dict:
        return await self._request("POST", f"/guilds/{guild_id}/roles",
                                   json={"name": name, "color": color, "permissions": permissions})

    async def delete_role(self, guild_id: str, role_id: str) -> dict:
        return await self._request("DELETE", f"/guilds/{guild_id}/roles/{role_id}")

    # ── Guild Info ─────────────────────────────────────────────

    async def get_guild(self, guild_id: str) -> dict:
        return await self._request("GET", f"/guilds/{guild_id}")
