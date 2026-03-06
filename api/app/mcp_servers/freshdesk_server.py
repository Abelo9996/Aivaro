"""Freshdesk MCP Server — tickets, contacts, agents, notes."""
from app.mcp_servers.base import BaseMCPServer


class FreshdeskMCPServer(BaseMCPServer):
    provider = "freshdesk"

    def __init__(self, domain: str, api_key: str):
        super().__init__()
        from app.services.integrations.freshdesk_service import FreshdeskService
        self.svc = FreshdeskService(domain=domain, api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("freshdesk_list_tickets", "List Freshdesk tickets.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 30}},
        }, self._list_tickets)

        self._register("freshdesk_get_ticket", "Get a Freshdesk ticket by ID.", {
            "type": "object",
            "properties": {"ticket_id": {"type": "integer", "description": "Ticket ID"}},
            "required": ["ticket_id"],
        }, self._get_ticket)

        self._register("freshdesk_create_ticket", "Create a Freshdesk support ticket.", {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Ticket subject"},
                "description": {"type": "string", "description": "Ticket description (HTML)"},
                "email": {"type": "string", "description": "Requester email"},
                "priority": {"type": "integer", "description": "1=Low, 2=Medium, 3=High, 4=Urgent", "default": 1},
                "status": {"type": "integer", "description": "2=Open, 3=Pending, 4=Resolved, 5=Closed", "default": 2},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
            },
            "required": ["subject", "description", "email"],
        }, self._create_ticket)

        self._register("freshdesk_update_ticket", "Update a Freshdesk ticket.", {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer", "description": "Ticket ID"},
                "status": {"type": "integer", "description": "2=Open, 3=Pending, 4=Resolved, 5=Closed"},
                "priority": {"type": "integer", "description": "1=Low, 2=Medium, 3=High, 4=Urgent"},
                "subject": {"type": "string"},
            },
            "required": ["ticket_id"],
        }, self._update_ticket)

        self._register("freshdesk_add_note", "Add a note to a Freshdesk ticket.", {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer", "description": "Ticket ID"},
                "body": {"type": "string", "description": "Note content (HTML)"},
                "private": {"type": "boolean", "description": "Private note (internal)", "default": True},
            },
            "required": ["ticket_id", "body"],
        }, self._add_note)

        self._register("freshdesk_list_contacts", "List Freshdesk contacts.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 30}},
        }, self._list_contacts)

        self._register("freshdesk_create_contact", "Create a Freshdesk contact.", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Contact name"},
                "email": {"type": "string", "description": "Contact email"},
                "phone": {"type": "string", "description": "Phone number"},
            },
            "required": ["name", "email"],
        }, self._create_contact)

        self._register("freshdesk_list_agents", "List Freshdesk agents.", {
            "type": "object", "properties": {},
        }, self._list_agents)

    async def _list_tickets(self, limit: int = 30) -> dict:
        tickets = await self.svc.list_tickets(limit)
        return {"tickets": tickets, "count": len(tickets)}

    async def _get_ticket(self, ticket_id: int) -> dict:
        return await self.svc.get_ticket(ticket_id)

    async def _create_ticket(self, subject: str, description: str, email: str,
                             priority: int = 1, status: int = 2, tags: list = None) -> dict:
        return await self.svc.create_ticket(subject, description, email, priority, status, tags)

    async def _update_ticket(self, ticket_id: int, **fields) -> dict:
        return await self.svc.update_ticket(ticket_id, **fields)

    async def _add_note(self, ticket_id: int, body: str, private: bool = True) -> dict:
        return await self.svc.add_note(ticket_id, body, private)

    async def _list_contacts(self, limit: int = 30) -> dict:
        contacts = await self.svc.list_contacts(limit)
        return {"contacts": contacts, "count": len(contacts)}

    async def _create_contact(self, name: str, email: str, phone: str = None) -> dict:
        return await self.svc.create_contact(name, email, phone)

    async def _list_agents(self) -> dict:
        agents = await self.svc.list_agents()
        return {"agents": agents, "count": len(agents)}

    async def close(self):
        await self.svc.close()
