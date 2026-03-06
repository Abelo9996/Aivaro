"""Twitch MCP Server — users, streams, channels, clips."""
from app.mcp_servers.base import BaseMCPServer


class TwitchMCPServer(BaseMCPServer):
    provider = "twitch"

    def __init__(self, client_id: str, access_token: str):
        super().__init__()
        from app.services.integrations.twitch_service import TwitchService
        self.svc = TwitchService(client_id=client_id, access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("twitch_get_user", "Get a Twitch user by login name or ID.", {
            "type": "object",
            "properties": {
                "login": {"type": "string", "description": "Twitch username"},
                "user_id": {"type": "string", "description": "Twitch user ID"},
            },
        }, self._get_user)

        self._register("twitch_get_streams", "Get live streams, optionally filtered.", {
            "type": "object",
            "properties": {
                "game_id": {"type": "string", "description": "Filter by game ID"},
                "user_login": {"type": "string", "description": "Filter by streamer username"},
                "limit": {"type": "integer", "default": 20},
            },
        }, self._get_streams)

        self._register("twitch_get_channel", "Get channel info for a broadcaster.", {
            "type": "object",
            "properties": {"broadcaster_id": {"type": "string", "description": "Broadcaster user ID"}},
            "required": ["broadcaster_id"],
        }, self._get_channel)

        self._register("twitch_search_channels", "Search for Twitch channels.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        }, self._search_channels)

        self._register("twitch_get_clips", "Get clips for a broadcaster.", {
            "type": "object",
            "properties": {
                "broadcaster_id": {"type": "string", "description": "Broadcaster user ID"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["broadcaster_id"],
        }, self._get_clips)

        self._register("twitch_create_clip", "Create a clip from a live stream.", {
            "type": "object",
            "properties": {"broadcaster_id": {"type": "string", "description": "Broadcaster user ID"}},
            "required": ["broadcaster_id"],
        }, self._create_clip)

        self._register("twitch_get_subscribers", "Get subscribers for a channel.", {
            "type": "object",
            "properties": {
                "broadcaster_id": {"type": "string", "description": "Broadcaster user ID"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["broadcaster_id"],
        }, self._get_subscribers)

    async def _get_user(self, login: str = None, user_id: str = None) -> dict:
        return await self.svc.get_user(login, user_id)

    async def _get_streams(self, game_id: str = None, user_login: str = None, limit: int = 20) -> dict:
        streams = await self.svc.get_streams(game_id, user_login, limit)
        return {"streams": streams, "count": len(streams)}

    async def _get_channel(self, broadcaster_id: str) -> dict:
        return await self.svc.get_channel(broadcaster_id)

    async def _search_channels(self, query: str, limit: int = 20) -> dict:
        channels = await self.svc.search_channels(query, limit)
        return {"channels": channels, "count": len(channels)}

    async def _get_clips(self, broadcaster_id: str, limit: int = 20) -> dict:
        clips = await self.svc.get_clips(broadcaster_id, limit)
        return {"clips": clips, "count": len(clips)}

    async def _create_clip(self, broadcaster_id: str) -> dict:
        return await self.svc.create_clip(broadcaster_id)

    async def _get_subscribers(self, broadcaster_id: str, limit: int = 20) -> dict:
        subs = await self.svc.get_subscribers(broadcaster_id, limit)
        return {"subscribers": subs, "count": len(subs)}

    async def close(self):
        await self.svc.close()
