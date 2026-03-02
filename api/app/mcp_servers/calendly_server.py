"""Calendly MCP Server — events, scheduling links."""
from app.mcp_servers.base import BaseMCPServer


class CalendlyMCPServer(BaseMCPServer):
    provider = "calendly"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.calendly_service import CalendlyService
        self.svc = CalendlyService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register(
            "calendly_list_events",
            "List scheduled Calendly events.",
            {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (active, canceled)", "default": "active"},
                    "count": {"type": "integer", "default": 20},
                    "min_start_time": {"type": "string", "description": "ISO 8601 start time filter"},
                    "max_start_time": {"type": "string", "description": "ISO 8601 end time filter"},
                },
            },
            self._list_events,
        )
        self._register(
            "calendly_get_event",
            "Get details of a specific Calendly event.",
            {
                "type": "object",
                "properties": {
                    "event_uuid": {"type": "string", "description": "Calendly event UUID"},
                },
                "required": ["event_uuid"],
            },
            self._get_event,
        )
        self._register(
            "calendly_cancel_event",
            "Cancel a scheduled Calendly event.",
            {
                "type": "object",
                "properties": {
                    "event_uuid": {"type": "string", "description": "Calendly event UUID"},
                    "reason": {"type": "string", "description": "Cancellation reason"},
                },
                "required": ["event_uuid"],
            },
            self._cancel_event,
        )
        self._register(
            "calendly_create_link",
            "Create a single-use Calendly scheduling link.",
            {
                "type": "object",
                "properties": {
                    "event_type_uuid": {"type": "string", "description": "Event type UUID (auto-detects if omitted)"},
                    "max_event_count": {"type": "integer", "default": 1},
                },
            },
            self._create_link,
        )
        self._register(
            "calendly_list_event_types",
            "List available Calendly event types.",
            {"type": "object", "properties": {}},
            self._list_event_types,
        )

    async def _list_events(self, status: str = "active", count: int = 20,
                           min_start_time: str = None, max_start_time: str = None) -> dict:
        user_uri = await self.svc.get_user_uri()
        events = await self.svc.list_scheduled_events(
            user_uri=user_uri, status=status, count=count,
            min_start_time=min_start_time, max_start_time=max_start_time,
        )
        formatted = [self.svc.format_event_for_display(e) for e in events.get("collection", [])]
        return {"calendly_events": formatted, "calendly_count": len(formatted)}

    async def _get_event(self, event_uuid: str) -> dict:
        event = await self.svc.get_scheduled_event(event_uuid)
        return {"event": self.svc.format_event_for_display(event.get("resource", event))}

    async def _cancel_event(self, event_uuid: str, reason: str = "") -> dict:
        await self.svc.cancel_scheduled_event(event_uuid, reason=reason)
        return {"cancelled": True, "event_uuid": event_uuid}

    async def _create_link(self, event_type_uuid: str = None, max_event_count: int = 1) -> dict:
        if not event_type_uuid:
            # Auto-detect first event type
            user_uri = await self.svc.get_user_uri()
            event_types = await self.svc.list_event_types(user_uri=user_uri)
            collection = event_types.get("collection", [])
            if collection:
                event_type_uuid = self.svc.extract_uuid_from_uri(collection[0].get("uri", ""))
        if not event_type_uuid:
            return {"error": "No event types found. Create one in Calendly first."}
        result = await self.svc.create_scheduling_link(event_type_uuid=event_type_uuid, max_event_count=max_event_count)
        booking_url = result.get("resource", {}).get("booking_url", "")
        return {"calendly_link": booking_url, "calendly_link_created": True}

    async def _list_event_types(self) -> dict:
        user_uri = await self.svc.get_user_uri()
        result = await self.svc.list_event_types(user_uri=user_uri)
        event_types = result.get("collection", [])
        return {
            "event_types": [{"name": et.get("name"), "uuid": self.svc.extract_uuid_from_uri(et.get("uri", "")),
                             "duration": et.get("duration"), "active": et.get("active")} for et in event_types],
            "count": len(event_types),
        }

    async def close(self):
        await self.svc.close()
