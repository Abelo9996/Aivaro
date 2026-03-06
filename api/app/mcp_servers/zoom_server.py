"""Zoom MCP Server — meetings, recordings, users."""
from app.mcp_servers.base import BaseMCPServer


class ZoomMCPServer(BaseMCPServer):
    provider = "zoom"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.zoom_service import ZoomService
        self.svc = ZoomService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("zoom_list_meetings", "List scheduled Zoom meetings.", {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "User ID or 'me'", "default": "me"},
                "type": {"type": "string", "description": "scheduled, live, upcoming", "default": "scheduled"},
            },
        }, self._list_meetings)

        self._register("zoom_create_meeting", "Create a Zoom meeting.", {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "description": "Meeting topic/title"},
                "start_time": {"type": "string", "description": "Start time (ISO 8601, e.g. 2026-03-10T10:00:00Z)"},
                "duration": {"type": "integer", "description": "Duration in minutes", "default": 60},
                "timezone": {"type": "string", "description": "Timezone (e.g. America/Los_Angeles)"},
                "agenda": {"type": "string", "description": "Meeting agenda/description"},
                "user_id": {"type": "string", "description": "Host user ID or 'me'", "default": "me"},
            },
            "required": ["topic"],
        }, self._create_meeting)

        self._register("zoom_get_meeting", "Get details of a Zoom meeting.", {
            "type": "object",
            "properties": {"meeting_id": {"type": "integer", "description": "Meeting ID"}},
            "required": ["meeting_id"],
        }, self._get_meeting)

        self._register("zoom_update_meeting", "Update a Zoom meeting.", {
            "type": "object",
            "properties": {
                "meeting_id": {"type": "integer", "description": "Meeting ID"},
                "topic": {"type": "string"}, "start_time": {"type": "string"},
                "duration": {"type": "integer"}, "agenda": {"type": "string"},
            },
            "required": ["meeting_id"],
        }, self._update_meeting)

        self._register("zoom_delete_meeting", "Delete/cancel a Zoom meeting.", {
            "type": "object",
            "properties": {"meeting_id": {"type": "integer", "description": "Meeting ID"}},
            "required": ["meeting_id"],
        }, self._delete_meeting)

        self._register("zoom_list_recordings", "List Zoom cloud recordings.", {
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "default": "me"},
                "from_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                "to_date": {"type": "string", "description": "End date (YYYY-MM-DD)"},
            },
        }, self._list_recordings)

        self._register("zoom_list_users", "List Zoom users in the account.", {
            "type": "object",
            "properties": {"page_size": {"type": "integer", "default": 30}},
        }, self._list_users)

    async def _list_meetings(self, user_id: str = "me", type: str = "scheduled") -> dict:
        meetings = await self.svc.list_meetings(user_id, type)
        return {"meetings": meetings, "count": len(meetings)}

    async def _create_meeting(self, topic: str, start_time: str = None, duration: int = 60,
                              timezone: str = None, agenda: str = None, user_id: str = "me") -> dict:
        return await self.svc.create_meeting(topic, start_time, duration, timezone, agenda, user_id)

    async def _get_meeting(self, meeting_id: int) -> dict:
        return await self.svc.get_meeting(meeting_id)

    async def _update_meeting(self, meeting_id: int, **fields) -> dict:
        return await self.svc.update_meeting(meeting_id, **fields)

    async def _delete_meeting(self, meeting_id: int) -> dict:
        await self.svc.delete_meeting(meeting_id)
        return {"deleted": True, "meeting_id": meeting_id}

    async def _list_recordings(self, user_id: str = "me", from_date: str = None, to_date: str = None) -> dict:
        recordings = await self.svc.list_recordings(user_id, from_date, to_date)
        return {"recordings": recordings, "count": len(recordings)}

    async def _list_users(self, page_size: int = 30) -> dict:
        users = await self.svc.list_users(page_size)
        return {"users": users, "count": len(users)}

    async def close(self):
        await self.svc.close()
