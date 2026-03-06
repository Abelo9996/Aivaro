"""Webflow MCP Server — sites, collections, CMS items."""
from app.mcp_servers.base import BaseMCPServer


class WebflowMCPServer(BaseMCPServer):
    provider = "webflow"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.webflow_service import WebflowService
        self.svc = WebflowService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("webflow_list_sites", "List all Webflow sites.", {
            "type": "object", "properties": {},
        }, self._list_sites)

        self._register("webflow_list_collections", "List CMS collections for a Webflow site.", {
            "type": "object",
            "properties": {"site_id": {"type": "string", "description": "Webflow site ID"}},
            "required": ["site_id"],
        }, self._list_collections)

        self._register("webflow_list_items", "List items in a Webflow CMS collection.", {
            "type": "object",
            "properties": {
                "collection_id": {"type": "string", "description": "Collection ID"},
                "limit": {"type": "integer", "default": 100},
            },
            "required": ["collection_id"],
        }, self._list_items)

        self._register("webflow_create_item", "Create a CMS item in a Webflow collection.", {
            "type": "object",
            "properties": {
                "collection_id": {"type": "string", "description": "Collection ID"},
                "fields": {"type": "object", "description": "Field data (name, slug, etc.)"},
                "is_draft": {"type": "boolean", "description": "Create as draft", "default": False},
            },
            "required": ["collection_id", "fields"],
        }, self._create_item)

        self._register("webflow_update_item", "Update a CMS item in a Webflow collection.", {
            "type": "object",
            "properties": {
                "collection_id": {"type": "string", "description": "Collection ID"},
                "item_id": {"type": "string", "description": "Item ID"},
                "fields": {"type": "object", "description": "Fields to update"},
            },
            "required": ["collection_id", "item_id", "fields"],
        }, self._update_item)

        self._register("webflow_delete_item", "Delete a CMS item from a Webflow collection.", {
            "type": "object",
            "properties": {
                "collection_id": {"type": "string", "description": "Collection ID"},
                "item_id": {"type": "string", "description": "Item ID"},
            },
            "required": ["collection_id", "item_id"],
        }, self._delete_item)

        self._register("webflow_publish_site", "Publish a Webflow site.", {
            "type": "object",
            "properties": {"site_id": {"type": "string", "description": "Site ID"}},
            "required": ["site_id"],
        }, self._publish_site)

    async def _list_sites(self) -> dict:
        sites = await self.svc.list_sites()
        return {"sites": sites, "count": len(sites)}

    async def _list_collections(self, site_id: str) -> dict:
        colls = await self.svc.list_collections(site_id)
        return {"collections": colls, "count": len(colls)}

    async def _list_items(self, collection_id: str, limit: int = 100) -> dict:
        items = await self.svc.list_items(collection_id, limit)
        return {"items": items, "count": len(items)}

    async def _create_item(self, collection_id: str, fields: dict, is_draft: bool = False) -> dict:
        return await self.svc.create_item(collection_id, fields, is_draft)

    async def _update_item(self, collection_id: str, item_id: str, fields: dict) -> dict:
        return await self.svc.update_item(collection_id, item_id, fields)

    async def _delete_item(self, collection_id: str, item_id: str) -> dict:
        await self.svc.delete_item(collection_id, item_id)
        return {"deleted": True, "item_id": item_id}

    async def _publish_site(self, site_id: str) -> dict:
        return await self.svc.publish_site(site_id)

    async def close(self):
        await self.svc.close()
