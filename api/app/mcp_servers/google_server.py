"""Google MCP Server — Gmail, Calendar, Drive, Sheets tools."""
from app.mcp_servers.base import BaseMCPServer


class GoogleMCPServer(BaseMCPServer):
    provider = "google"

    def __init__(self, access_token: str, refresh_token: str = None):
        super().__init__()
        from app.services.integrations.google_service import GoogleService
        self.svc = GoogleService(access_token=access_token, refresh_token=refresh_token)
        self._register_tools()

    def _register_tools(self):
        # ── Gmail ──────────────────────────────────────────────
        self._register("send_email", "Send an email via Gmail.", {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject"},
                "body": {"type": "string", "description": "Email body (plain text)"},
            },
            "required": ["to", "subject", "body"],
        }, self._send_email)

        self._register("gmail_list_messages", "List recent Gmail messages. Optionally filter by query.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Gmail search query (e.g. 'from:john subject:invoice')"},
                "max_results": {"type": "integer", "description": "Max messages to return", "default": 10},
            },
        }, self._gmail_list_messages)

        self._register("gmail_get_message", "Get full details of a specific Gmail message by ID.", {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "Gmail message ID"},
            },
            "required": ["message_id"],
        }, self._gmail_get_message)

        self._register("gmail_search", "Search Gmail messages with advanced query syntax.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Gmail search query (e.g. 'from:john after:2024/01/01 has:attachment')"},
                "max_results": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        }, self._gmail_search)

        # ── Calendar ───────────────────────────────────────────
        self._register("google_calendar_create", "Create a Google Calendar event.", {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title"},
                "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                "time": {"type": "string", "description": "Start time (HH:MM, 24h)"},
                "duration_hours": {"type": "number", "description": "Duration in hours", "default": 1},
                "description": {"type": "string", "description": "Event description"},
                "attendees": {"type": "array", "items": {"type": "string"}, "description": "Attendee email addresses"},
                "timezone": {"type": "string", "description": "Timezone (e.g. America/Los_Angeles)"},
            },
            "required": ["title", "date", "time"],
        }, self._calendar_create)

        self._register("google_calendar_list", "List upcoming Google Calendar events.", {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "default": 10},
                "time_min": {"type": "string", "description": "Start of time range (ISO 8601)"},
                "time_max": {"type": "string", "description": "End of time range (ISO 8601)"},
            },
        }, self._calendar_list)

        self._register("google_calendar_delete", "Delete a Google Calendar event by ID.", {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Calendar event ID"},
            },
            "required": ["event_id"],
        }, self._calendar_delete)

        self._register("google_calendar_list_calendars", "List all calendars the user has access to.", {
            "type": "object", "properties": {},
        }, self._calendar_list_calendars)

        # ── Drive ──────────────────────────────────────────────
        self._register("google_drive_list", "List files in Google Drive.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Drive search query"},
                "max_results": {"type": "integer", "default": 10},
            },
        }, self._drive_list)

        # ── Sheets ─────────────────────────────────────────────
        self._register("append_row", "Append a row to a Google Sheet.", {
            "type": "object",
            "properties": {
                "spreadsheet_name": {"type": "string", "description": "Spreadsheet name or ID"},
                "values": {"type": "object", "description": "Column-value pairs to append"},
                "sheet_name": {"type": "string", "description": "Sheet tab name", "default": "Sheet1"},
            },
            "required": ["spreadsheet_name", "values"],
        }, self._append_row)

        self._register("google_sheets_read", "Read rows from a Google Sheet.", {
            "type": "object",
            "properties": {
                "spreadsheet_id": {"type": "string", "description": "Spreadsheet ID"},
                "range": {"type": "string", "description": "Range (e.g. Sheet1!A1:Z100)", "default": "Sheet1"},
            },
            "required": ["spreadsheet_id"],
        }, self._sheets_read)

        self._register("google_sheets_create", "Create a new Google Spreadsheet.", {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Spreadsheet title"},
            },
            "required": ["title"],
        }, self._sheets_create)

        self._register("google_sheets_find", "Find a spreadsheet by name.", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Spreadsheet name to search for"},
            },
            "required": ["name"],
        }, self._sheets_find)

        self._register("google_sheets_list", "List all spreadsheets in Google Drive.", {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "default": 20},
            },
        }, self._sheets_list)

    # ── Handlers ───────────────────────────────────────────────

    async def _send_email(self, to: str, subject: str, body: str) -> dict:
        result = await self.svc.send_email(to, subject, body)
        return {"email_sent": True, "email_to": to, "email_subject": subject, "message_id": result.get("id")}

    async def _gmail_list_messages(self, query: str = "", max_results: int = 10) -> dict:
        messages = await self.svc.list_messages(query=query, max_results=max_results)
        return {"messages": messages, "count": len(messages)}

    async def _gmail_get_message(self, message_id: str) -> dict:
        msg = await self.svc.get_message(message_id)
        return {"message": msg}

    async def _gmail_search(self, query: str, max_results: int = 20) -> dict:
        messages = await self.svc.list_messages(query=query, max_results=max_results)
        return {"messages": messages, "count": len(messages)}

    async def _calendar_create(self, title: str, date: str, time: str, duration_hours: float = 1,
                               description: str = "", attendees: list = None, timezone: str = "America/Los_Angeles") -> dict:
        from datetime import datetime as dt, timedelta
        start_str = f"{date}T{time}:00"
        start = dt.fromisoformat(start_str)
        end = start + timedelta(hours=duration_hours)
        event = await self.svc.create_event(
            title=title, start_time=start.isoformat(), end_time=end.isoformat(),
            description=description, attendees=attendees or [], timezone=timezone,
        )
        return {
            "calendar_event_id": event.get("id"), "calendar_event_url": event.get("htmlLink"),
            "event_title": title, "event_start": start.isoformat(), "event_end": end.isoformat(),
        }

    async def _calendar_list(self, max_results: int = 10, time_min: str = None, time_max: str = None) -> dict:
        events = await self.svc.list_events(max_results=max_results, time_min=time_min, time_max=time_max)
        return {"events": events, "count": len(events)}

    async def _calendar_delete(self, event_id: str) -> dict:
        await self.svc.delete_event(event_id)
        return {"deleted": True, "event_id": event_id}

    async def _calendar_list_calendars(self) -> dict:
        calendars = await self.svc.list_calendars()
        return {"calendars": calendars, "count": len(calendars)}

    async def _drive_list(self, query: str = "", max_results: int = 10) -> dict:
        files = await self.svc.list_spreadsheets(query=query, max_results=max_results)
        return {"files": files, "count": len(files)}

    async def _append_row(self, spreadsheet_name: str, values: dict, sheet_name: str = "Sheet1") -> dict:
        spreadsheet = await self.svc.find_or_create_spreadsheet(spreadsheet_name)
        sid = spreadsheet["spreadsheetId"]
        await self.svc.append_row_with_schema(sid, values, sheet_name=sheet_name)
        return {"row_appended": True, "spreadsheet_id": sid, "spreadsheet_name": spreadsheet_name}

    async def _sheets_read(self, spreadsheet_id: str, range: str = "Sheet1") -> dict:
        values = await self.svc.get_sheet_values(spreadsheet_id, range)
        return {"values": values, "row_count": len(values) if values else 0}

    async def _sheets_create(self, title: str) -> dict:
        result = await self.svc.create_spreadsheet(title)
        return {"spreadsheet_id": result.get("spreadsheetId"), "url": result.get("spreadsheetUrl"), "title": title}

    async def _sheets_find(self, name: str) -> dict:
        result = await self.svc.find_spreadsheet_by_name(name)
        return {"found": result is not None, "spreadsheet": result}

    async def _sheets_list(self, max_results: int = 20) -> dict:
        sheets = await self.svc.list_spreadsheets(max_results=max_results)
        return {"spreadsheets": sheets, "count": len(sheets)}

    async def close(self):
        await self.svc.close()
