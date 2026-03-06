"""Zendesk MCP Server — tickets, users, search."""
from app.mcp_servers.base import BaseMCPServer


class ZendeskMCPServer(BaseMCPServer):
    provider = "zendesk"

    def __init__(self, subdomain: str, email: str, api_token: str):
        super().__init__()
        from app.services.integrations.zendesk_service import ZendeskService
        self.svc = ZendeskService(subdomain=subdomain, email=email, api_token=api_token)
        self._register_tools()

    def _register_tools(self):
        self._register("zendesk_create_ticket", "Create a Zendesk support ticket.", {
            "type": "object",
            "properties": {
                "subject": {"type": "string", "description": "Ticket subject"},
                "description": {"type": "string", "description": "Ticket description"},
                "priority": {"type": "string", "description": "low, normal, high, urgent", "default": "normal"},
                "requester_email": {"type": "string", "description": "Requester email"},
                "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags"},
            },
            "required": ["subject", "description"],
        }, self._create_ticket)

        self._register("zendesk_update_ticket", "Update a Zendesk ticket.", {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer", "description": "Ticket ID"},
                "status": {"type": "string", "description": "new, open, pending, hold, solved, closed"},
                "priority": {"type": "string", "description": "low, normal, high, urgent"},
                "assignee_id": {"type": "integer", "description": "Assignee user ID"},
            },
            "required": ["ticket_id"],
        }, self._update_ticket)

        self._register("zendesk_get_ticket", "Get details of a Zendesk ticket.", {
            "type": "object",
            "properties": {"ticket_id": {"type": "integer", "description": "Ticket ID"}},
            "required": ["ticket_id"],
        }, self._get_ticket)

        self._register("zendesk_list_tickets", "List Zendesk tickets.", {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status"},
                "limit": {"type": "integer", "default": 50},
            },
        }, self._list_tickets)

        self._register("zendesk_add_comment", "Add a comment to a Zendesk ticket.", {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "integer", "description": "Ticket ID"},
                "body": {"type": "string", "description": "Comment body"},
                "public": {"type": "boolean", "description": "Public or internal note", "default": True},
            },
            "required": ["ticket_id", "body"],
        }, self._add_comment)

        self._register("zendesk_search_tickets", "Search Zendesk tickets.", {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search query"}},
            "required": ["query"],
        }, self._search_tickets)

        self._register("zendesk_list_users", "List Zendesk users.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_users)

        self._register("zendesk_create_user", "Create a Zendesk user.", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"},
                "role": {"type": "string", "description": "end-user, agent, admin", "default": "end-user"},
            },
            "required": ["name", "email"],
        }, self._create_user)

    async def _create_ticket(self, subject: str, description: str, priority: str = "normal",
                             requester_email: str = None, tags: list = None) -> dict:
        return await self.svc.create_ticket(subject, description, priority, requester_email, tags)

    async def _update_ticket(self, ticket_id: int, **fields) -> dict:
        return await self.svc.update_ticket(ticket_id, **fields)

    async def _get_ticket(self, ticket_id: int) -> dict:
        return await self.svc.get_ticket(ticket_id)

    async def _list_tickets(self, status: str = None, limit: int = 50) -> dict:
        tickets = await self.svc.list_tickets(status, limit)
        return {"tickets": tickets, "count": len(tickets)}

    async def _add_comment(self, ticket_id: int, body: str, public: bool = True) -> dict:
        return await self.svc.add_comment(ticket_id, body, public)

    async def _search_tickets(self, query: str) -> dict:
        results = await self.svc.search_tickets(query)
        return {"results": results, "count": len(results)}

    async def _list_users(self, limit: int = 50) -> dict:
        users = await self.svc.list_users(limit)
        return {"users": users, "count": len(users)}

    async def _create_user(self, name: str, email: str, role: str = "end-user") -> dict:
        return await self.svc.create_user(name, email, role)

    async def close(self):
        await self.svc.close()
