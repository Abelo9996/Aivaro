"""Notion MCP Server — pages, databases, search."""
from app.mcp_servers.base import BaseMCPServer


class NotionMCPServer(BaseMCPServer):
    provider = "notion"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.notion_service import NotionService
        self.svc = NotionService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register(
            "notion_create_page",
            "Create a page in a Notion database.",
            {
                "type": "object",
                "properties": {
                    "database_id": {"type": "string", "description": "Notion database ID"},
                    "properties": {"type": "object", "description": "Page properties (field-value pairs)"},
                    "content": {"type": "string", "description": "Page body content (markdown-ish)"},
                },
                "required": ["database_id", "properties"],
            },
            self._create_page,
        )
        self._register(
            "notion_update_page",
            "Update a Notion page's properties.",
            {
                "type": "object",
                "properties": {
                    "page_id": {"type": "string", "description": "Notion page ID"},
                    "properties": {"type": "object", "description": "Properties to update"},
                },
                "required": ["page_id", "properties"],
            },
            self._update_page,
        )
        self._register(
            "notion_query_database",
            "Query a Notion database with optional filter.",
            {
                "type": "object",
                "properties": {
                    "database_id": {"type": "string"},
                    "filter": {"type": "object", "description": "Notion filter object"},
                    "page_size": {"type": "integer", "default": 100},
                },
                "required": ["database_id"],
            },
            self._query_database,
        )
        self._register(
            "notion_search",
            "Search across all Notion pages and databases.",
            {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                },
                "required": ["query"],
            },
            self._search,
        )
        self._register(
            "notion_get_page",
            "Get a Notion page by ID.",
            {
                "type": "object",
                "properties": {
                    "page_id": {"type": "string"},
                },
                "required": ["page_id"],
            },
            self._get_page,
        )
        self._register(
            "notion_list_databases",
            "List all Notion databases the user has access to.",
            {"type": "object", "properties": {}},
            self._list_databases,
        )

    async def _create_page(self, database_id: str, properties: dict, content: str = "") -> dict:
        # Build blocks from content if provided
        children = []
        if content:
            children = [self.svc.create_paragraph_block(content)]
        result = await self.svc.create_page(database_id=database_id, properties=properties, children=children)
        return {"page_created": True, "page_id": result.get("id"), "url": result.get("url")}

    async def _update_page(self, page_id: str, properties: dict) -> dict:
        result = await self.svc.update_page(page_id=page_id, properties=properties)
        return {"page_updated": True, "page_id": page_id}

    async def _query_database(self, database_id: str, filter: dict = None, page_size: int = 100) -> dict:
        results = await self.svc.query_database(database_id=database_id, filter=filter, page_size=page_size)
        return {"results": results.get("results", []), "count": len(results.get("results", []))}

    async def _search(self, query: str) -> dict:
        results = await self.svc.search(query=query)
        return {"results": results.get("results", []), "count": len(results.get("results", []))}

    async def _get_page(self, page_id: str) -> dict:
        page = await self.svc.get_page(page_id=page_id)
        return {"page": page}

    async def _list_databases(self) -> dict:
        databases = await self.svc.list_databases()
        return {"databases": databases, "count": len(databases)}

    async def close(self):
        await self.svc.close()
