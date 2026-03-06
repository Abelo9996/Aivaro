"""Typeform MCP Server — forms, responses."""
from app.mcp_servers.base import BaseMCPServer


class TypeformMCPServer(BaseMCPServer):
    provider = "typeform"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.typeform_service import TypeformService
        self.svc = TypeformService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("typeform_list_forms", "List all Typeform forms.", {
            "type": "object",
            "properties": {
                "page_size": {"type": "integer", "description": "Number of forms to return", "default": 25},
            },
        }, self._list_forms)

        self._register("typeform_get_form", "Get details of a Typeform form.", {
            "type": "object",
            "properties": {
                "form_id": {"type": "string", "description": "Typeform form ID"},
            },
            "required": ["form_id"],
        }, self._get_form)

        self._register("typeform_get_responses", "Get responses for a Typeform form.", {
            "type": "object",
            "properties": {
                "form_id": {"type": "string", "description": "Typeform form ID"},
                "page_size": {"type": "integer", "description": "Number of responses to return", "default": 25},
            },
            "required": ["form_id"],
        }, self._get_responses)

        self._register("typeform_create_form", "Create a new Typeform form.", {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Form title"},
                "fields": {"type": "array", "description": "Form field definitions", "items": {"type": "object"}},
            },
            "required": ["title"],
        }, self._create_form)

        self._register("typeform_delete_form", "Delete a Typeform form.", {
            "type": "object",
            "properties": {
                "form_id": {"type": "string", "description": "Typeform form ID"},
            },
            "required": ["form_id"],
        }, self._delete_form)

    async def _list_forms(self, page_size: int = 25) -> dict:
        forms = await self.svc.list_forms(page_size)
        return {"forms": forms, "count": len(forms)}

    async def _get_form(self, form_id: str) -> dict:
        return await self.svc.get_form(form_id)

    async def _get_responses(self, form_id: str, page_size: int = 25) -> dict:
        responses = await self.svc.get_responses(form_id, page_size)
        return {"responses": responses, "count": len(responses)}

    async def _create_form(self, title: str, fields: list = None) -> dict:
        return await self.svc.create_form(title, fields)

    async def _delete_form(self, form_id: str) -> dict:
        await self.svc.delete_form(form_id)
        return {"deleted": True, "form_id": form_id}

    async def close(self):
        await self.svc.close()
