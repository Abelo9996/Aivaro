"""SendGrid MCP Server — transactional email, templates, contacts."""
from app.mcp_servers.base import BaseMCPServer


class SendGridMCPServer(BaseMCPServer):
    provider = "sendgrid"

    def __init__(self, api_key: str):
        super().__init__()
        from app.services.integrations.sendgrid_service import SendGridService
        self.svc = SendGridService(api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("sendgrid_send_email", "Send an email via SendGrid.", {
            "type": "object",
            "properties": {
                "to": {"type": "string"}, "from_email": {"type": "string"},
                "subject": {"type": "string"},
                "html_content": {"type": "string"}, "text_content": {"type": "string"},
                "from_name": {"type": "string"},
            },
            "required": ["to", "from_email", "subject"],
        }, self._send_email)

        self._register("sendgrid_send_template", "Send a dynamic template email via SendGrid.", {
            "type": "object",
            "properties": {
                "to": {"type": "string"}, "from_email": {"type": "string"},
                "template_id": {"type": "string"},
                "dynamic_data": {"type": "object", "description": "Template variables"},
                "from_name": {"type": "string"},
            },
            "required": ["to", "from_email", "template_id"],
        }, self._send_template)

        self._register("sendgrid_add_contact", "Add a contact to SendGrid marketing.", {
            "type": "object",
            "properties": {
                "email": {"type": "string"}, "first_name": {"type": "string"},
                "last_name": {"type": "string"},
            },
            "required": ["email"],
        }, self._add_contact)

        self._register("sendgrid_search_contacts", "Search SendGrid contacts.", {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "SGQL query"}},
            "required": ["query"],
        }, self._search_contacts)

        self._register("sendgrid_list_contacts", "List SendGrid contacts.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_contacts)

        self._register("sendgrid_list_templates", "List SendGrid dynamic templates.", {
            "type": "object", "properties": {},
        }, self._list_templates)

    async def _send_email(self, to: str, from_email: str, subject: str, html_content: str = "",
                          text_content: str = "", from_name: str = "") -> dict:
        await self.svc.send_email(to, from_email, subject, html_content, text_content, from_name)
        return {"sent": True, "to": to, "subject": subject}

    async def _send_template(self, to: str, from_email: str, template_id: str,
                             dynamic_data: dict = None, from_name: str = "") -> dict:
        await self.svc.send_template_email(to, from_email, template_id, dynamic_data, from_name)
        return {"sent": True, "to": to, "template_id": template_id}

    async def _add_contact(self, email: str, first_name: str = "", last_name: str = "") -> dict:
        result = await self.svc.add_contact(email, first_name, last_name)
        return {"added": True, "email": email}

    async def _search_contacts(self, query: str) -> dict:
        contacts = await self.svc.search_contacts(query)
        return {"contacts": contacts, "count": len(contacts)}

    async def _list_contacts(self, limit: int = 50) -> dict:
        contacts = await self.svc.list_contacts(limit)
        return {"contacts": contacts, "count": len(contacts)}

    async def _list_templates(self) -> dict:
        templates = await self.svc.list_templates()
        return {"templates": templates, "count": len(templates)}

    async def close(self):
        await self.svc.close()
