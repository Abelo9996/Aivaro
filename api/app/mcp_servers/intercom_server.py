"""Intercom MCP Server — contacts, conversations, tags, notes."""
from app.mcp_servers.base import BaseMCPServer


class IntercomMCPServer(BaseMCPServer):
    provider = "intercom"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.intercom_service import IntercomService
        self.svc = IntercomService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("intercom_list_contacts", "List Intercom contacts.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_contacts)

        self._register("intercom_create_contact", "Create an Intercom contact.", {
            "type": "object",
            "properties": {
                "role": {"type": "string", "description": "user or lead", "default": "user"},
                "email": {"type": "string", "description": "Email address"},
                "name": {"type": "string", "description": "Full name"},
                "phone": {"type": "string", "description": "Phone number"},
                "external_id": {"type": "string", "description": "Your external ID"},
            },
            "required": ["email"],
        }, self._create_contact)

        self._register("intercom_update_contact", "Update an Intercom contact.", {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string", "description": "Intercom contact ID"},
                "name": {"type": "string"}, "email": {"type": "string"}, "phone": {"type": "string"},
            },
            "required": ["contact_id"],
        }, self._update_contact)

        self._register("intercom_search_contacts", "Search Intercom contacts by field.", {
            "type": "object",
            "properties": {
                "field": {"type": "string", "description": "Field to search (email, name, etc.)"},
                "value": {"type": "string", "description": "Value to match"},
            },
            "required": ["field", "value"],
        }, self._search_contacts)

        self._register("intercom_list_conversations", "List Intercom conversations.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 20}},
        }, self._list_conversations)

        self._register("intercom_create_conversation", "Start a new Intercom conversation from a contact.", {
            "type": "object",
            "properties": {
                "from_contact_id": {"type": "string", "description": "Contact ID initiating conversation"},
                "body": {"type": "string", "description": "Message body"},
            },
            "required": ["from_contact_id", "body"],
        }, self._create_conversation)

        self._register("intercom_reply_to_conversation", "Reply to an Intercom conversation.", {
            "type": "object",
            "properties": {
                "conversation_id": {"type": "string", "description": "Conversation ID"},
                "body": {"type": "string", "description": "Reply body"},
                "admin_id": {"type": "string", "description": "Admin ID sending the reply"},
                "message_type": {"type": "string", "description": "comment or note", "default": "comment"},
            },
            "required": ["conversation_id", "body"],
        }, self._reply_to_conversation)

        self._register("intercom_tag_contact", "Tag an Intercom contact.", {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string", "description": "Contact ID"},
                "tag_id": {"type": "string", "description": "Tag ID"},
            },
            "required": ["contact_id", "tag_id"],
        }, self._tag_contact)

        self._register("intercom_create_note", "Add a note to an Intercom contact.", {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string", "description": "Contact ID"},
                "body": {"type": "string", "description": "Note body"},
                "admin_id": {"type": "string", "description": "Admin ID"},
            },
            "required": ["contact_id", "body"],
        }, self._create_note)

    async def _list_contacts(self, limit: int = 50) -> dict:
        contacts = await self.svc.list_contacts(limit)
        return {"contacts": contacts, "count": len(contacts)}

    async def _create_contact(self, email: str, role: str = "user", name: str = None,
                              phone: str = None, external_id: str = None) -> dict:
        return await self.svc.create_contact(role, email, name, phone, external_id)

    async def _update_contact(self, contact_id: str, **fields) -> dict:
        return await self.svc.update_contact(contact_id, **fields)

    async def _search_contacts(self, field: str, value: str) -> dict:
        contacts = await self.svc.search_contacts(field, value)
        return {"contacts": contacts, "count": len(contacts)}

    async def _list_conversations(self, limit: int = 20) -> dict:
        convos = await self.svc.list_conversations(limit)
        return {"conversations": convos, "count": len(convos)}

    async def _create_conversation(self, from_contact_id: str, body: str) -> dict:
        return await self.svc.create_conversation(from_contact_id, body)

    async def _reply_to_conversation(self, conversation_id: str, body: str,
                                     admin_id: str = None, message_type: str = "comment") -> dict:
        return await self.svc.reply_to_conversation(conversation_id, body, admin_id, message_type)

    async def _tag_contact(self, contact_id: str, tag_id: str) -> dict:
        return await self.svc.tag_contact(contact_id, tag_id)

    async def _create_note(self, contact_id: str, body: str, admin_id: str = None) -> dict:
        return await self.svc.create_note(contact_id, body, admin_id)

    async def close(self):
        await self.svc.close()
