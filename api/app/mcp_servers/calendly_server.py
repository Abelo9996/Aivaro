"""Calendly MCP Server — events, scheduling, availability."""
from app.mcp_servers.base import BaseMCPServer


class CalendlyMCPServer(BaseMCPServer):
    provider = "calendly"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.calendly_service import CalendlyService
        self.svc = CalendlyService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("calendly_list_events", "List scheduled Calendly events.", {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter: active or canceled"},
                "count": {"type": "integer", "default": 20},
                "min_start_time": {"type": "string", "description": "ISO datetime filter start"},
                "max_start_time": {"type": "string", "description": "ISO datetime filter end"},
            },
        }, self._list_events)

        self._register("calendly_get_event", "Get details of a specific Calendly event.", {
            "type": "object",
            "properties": {
                "event_uuid": {"type": "string", "description": "Calendly event UUID"},
            },
            "required": ["event_uuid"],
        }, self._get_event)

        self._register("calendly_cancel_event", "Cancel a scheduled Calendly event.", {
            "type": "object",
            "properties": {
                "event_uuid": {"type": "string", "description": "Calendly event UUID"},
                "reason": {"type": "string", "description": "Cancellation reason"},
            },
            "required": ["event_uuid"],
        }, self._cancel_event)

        self._register("calendly_create_link", "Create a single-use scheduling link.", {
            "type": "object",
            "properties": {
                "event_type_uuid": {"type": "string", "description": "Event type UUID"},
                "max_event_count": {"type": "integer", "default": 1},
            },
            "required": ["event_type_uuid"],
        }, self._create_link)

        self._register("calendly_list_event_types", "List available Calendly event types.", {
            "type": "object",
            "properties": {
                "active": {"type": "boolean", "description": "Filter by active status", "default": True},
            },
        }, self._list_event_types)

        self._register("calendly_list_invitees", "List invitees of a specific event.", {
            "type": "object",
            "properties": {
                "event_uuid": {"type": "string"},
                "count": {"type": "integer", "default": 50},
            },
            "required": ["event_uuid"],
        }, self._list_invitees)

        self._register("calendly_get_availability", "Get availability schedules.", {
            "type": "object", "properties": {},
        }, self._get_availability)

        self._register("calendly_get_busy_times", "Get busy time slots for a date range.", {
            "type": "object",
            "properties": {
                "start_time": {"type": "string", "description": "ISO start datetime"},
                "end_time": {"type": "string", "description": "ISO end datetime"},
            },
            "required": ["start_time", "end_time"],
        }, self._get_busy_times)

    # ── Handlers ───────────────────────────────────────────────

    async def _list_events(self, status: str = "active", count: int = 20,
                           min_start_time: str = None, max_start_time: str = None) -> dict:
        events = await self.svc.list_scheduled_events(
            status=status, count=count,
            min_start_time=min_start_time, max_start_time=max_start_time,
        )
        return {"events": events, "count": len(events)}

    async def _get_event(self, event_uuid: str) -> dict:
        event = await self.svc.get_scheduled_event(event_uuid)
        return {"event": event}

    async def _cancel_event(self, event_uuid: str, reason: str = "") -> dict:
        result = await self.svc.cancel_scheduled_event(event_uuid, reason=reason)
        return {"canceled": True, "event_uuid": event_uuid}

    async def _create_link(self, event_type_uuid: str, max_event_count: int = 1) -> dict:
        result = await self.svc.create_scheduling_link(event_type_uuid, max_event_count=max_event_count)
        return result

    async def _list_event_types(self, active: bool = True) -> dict:
        event_types = await self.svc.list_event_types(active=active)
        return {"event_types": event_types, "count": len(event_types)}

    async def _list_invitees(self, event_uuid: str, count: int = 50) -> dict:
        invitees = await self.svc.list_event_invitees(event_uuid, count=count)
        return {"invitees": invitees, "count": len(invitees)}

    async def _get_availability(self) -> dict:
        schedules = await self.svc.get_user_availability_schedules()
        return {"schedules": schedules}

    async def _get_busy_times(self, start_time: str, end_time: str) -> dict:
        busy = await self.svc.get_user_busy_times(start_time, end_time)
        return {"busy_times": busy}

    async def close(self):
        await self.svc.close()
