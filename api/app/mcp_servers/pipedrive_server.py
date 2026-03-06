"""Pipedrive MCP Server — deals, persons, activities, notes."""
from app.mcp_servers.base import BaseMCPServer


class PipedriveMCPServer(BaseMCPServer):
    provider = "pipedrive"

    def __init__(self, api_token: str):
        super().__init__()
        from app.services.integrations.pipedrive_service import PipedriveService
        self.svc = PipedriveService(api_token=api_token)
        self._register_tools()

    def _register_tools(self):
        self._register("pipedrive_list_deals", "List deals in Pipedrive.", {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter: open, won, lost, deleted", "default": "open"},
                "limit": {"type": "integer", "default": 50},
            },
        }, self._list_deals)

        self._register("pipedrive_get_deal", "Get details of a Pipedrive deal.", {
            "type": "object",
            "properties": {"deal_id": {"type": "integer", "description": "Deal ID"}},
            "required": ["deal_id"],
        }, self._get_deal)

        self._register("pipedrive_create_deal", "Create a new deal in Pipedrive.", {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Deal title"},
                "value": {"type": "number", "description": "Deal value"},
                "currency": {"type": "string", "description": "Currency code (e.g. USD)"},
                "person_id": {"type": "integer", "description": "Associated person ID"},
                "stage_id": {"type": "integer", "description": "Pipeline stage ID"},
            },
            "required": ["title"],
        }, self._create_deal)

        self._register("pipedrive_update_deal", "Update a Pipedrive deal.", {
            "type": "object",
            "properties": {
                "deal_id": {"type": "integer", "description": "Deal ID"},
                "title": {"type": "string"}, "value": {"type": "number"},
                "status": {"type": "string", "description": "open, won, lost, deleted"},
            },
            "required": ["deal_id"],
        }, self._update_deal)

        self._register("pipedrive_list_persons", "List persons (contacts) in Pipedrive.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_persons)

        self._register("pipedrive_create_person", "Create a person in Pipedrive.", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Full name"},
                "email": {"type": "string", "description": "Email address"},
                "phone": {"type": "string", "description": "Phone number"},
            },
            "required": ["name"],
        }, self._create_person)

        self._register("pipedrive_update_person", "Update a person in Pipedrive.", {
            "type": "object",
            "properties": {
                "person_id": {"type": "integer", "description": "Person ID"},
                "name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"},
            },
            "required": ["person_id"],
        }, self._update_person)

        self._register("pipedrive_create_activity", "Create an activity in Pipedrive.", {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Activity subject"},
                "type": {"type": "string", "description": "Activity type (call, meeting, task, etc.)", "default": "call"},
                "deal_id": {"type": "integer", "description": "Associated deal ID"},
                "person_id": {"type": "integer", "description": "Associated person ID"},
                "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                "note": {"type": "string", "description": "Activity note"},
            },
            "required": ["subject"],
        }, self._create_activity)

        self._register("pipedrive_list_activities", "List activities in Pipedrive.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_activities)

        self._register("pipedrive_create_note", "Create a note in Pipedrive.", {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Note content (HTML allowed)"},
                "deal_id": {"type": "integer", "description": "Attach to deal"},
                "person_id": {"type": "integer", "description": "Attach to person"},
            },
            "required": ["content"],
        }, self._create_note)

    async def _list_deals(self, status: str = "open", limit: int = 50) -> dict:
        deals = await self.svc.list_deals(status, limit)
        return {"deals": deals, "count": len(deals)}

    async def _get_deal(self, deal_id: int) -> dict:
        return await self.svc.get_deal(deal_id)

    async def _create_deal(self, title: str, value: float = None, currency: str = None,
                           person_id: int = None, stage_id: int = None) -> dict:
        return await self.svc.create_deal(title, value, currency, person_id, stage_id)

    async def _update_deal(self, deal_id: int, **fields) -> dict:
        return await self.svc.update_deal(deal_id, **fields)

    async def _list_persons(self, limit: int = 50) -> dict:
        persons = await self.svc.list_persons(limit)
        return {"persons": persons, "count": len(persons)}

    async def _create_person(self, name: str, email: str = None, phone: str = None) -> dict:
        return await self.svc.create_person(name, email, phone)

    async def _update_person(self, person_id: int, **fields) -> dict:
        return await self.svc.update_person(person_id, **fields)

    async def _create_activity(self, subject: str, type: str = "call", deal_id: int = None,
                               person_id: int = None, due_date: str = None, note: str = None) -> dict:
        return await self.svc.create_activity(subject, type, deal_id, person_id, due_date, note)

    async def _list_activities(self, limit: int = 50) -> dict:
        activities = await self.svc.list_activities(limit)
        return {"activities": activities, "count": len(activities)}

    async def _create_note(self, content: str, deal_id: int = None, person_id: int = None) -> dict:
        return await self.svc.create_note(content, deal_id, person_id)

    async def close(self):
        await self.svc.close()
