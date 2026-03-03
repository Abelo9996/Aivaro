"""Notion MCP Server — pages, databases, blocks, search."""
from app.mcp_servers.base import BaseMCPServer


class NotionMCPServer(BaseMCPServer):
    provider = "notion"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.notion_service import NotionService
        self.svc = NotionService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("notion_create_page", "Create a page in a Notion database.", {
            "type": "object",
            "properties": {
                "database_id": {"type": "string", "description": "Notion database ID"},
                "properties": {"type": "object", "description": "Property name-value pairs"},
                "content": {"type": "string", "description": "Page body content (markdown-like)"},
            },
            "required": ["database_id", "properties"],
        }, self._create_page)

        self._register("notion_update_page", "Update properties of a Notion page.", {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Notion page ID"},
                "properties": {"type": "object", "description": "Property name-value pairs to update"},
            },
            "required": ["page_id", "properties"],
        }, self._update_page)

        self._register("notion_get_page", "Get a Notion page by ID.", {
            "type": "object",
            "properties": {
                "page_id": {"type": "string"},
            },
            "required": ["page_id"],
        }, self._get_page)

        self._register("notion_archive_page", "Archive (soft-delete) a Notion page.", {
            "type": "object",
            "properties": {
                "page_id": {"type": "string"},
            },
            "required": ["page_id"],
        }, self._archive_page)

        self._register("notion_query_database", "Query records from a Notion database.", {
            "type": "object",
            "properties": {
                "database_id": {"type": "string"},
                "filter": {"type": "object", "description": "Notion filter object"},
                "page_size": {"type": "integer", "default": 100},
            },
            "required": ["database_id"],
        }, self._query_database)

        self._register("notion_search", "Search across Notion pages and databases.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "filter_type": {"type": "string", "description": "Filter by object type: page or database"},
            },
            "required": ["query"],
        }, self._search)

        self._register("notion_list_databases", "List all databases the integration has access to.", {
            "type": "object", "properties": {},
        }, self._list_databases)

        self._register("notion_get_database", "Get database details including schema/properties.", {
            "type": "object",
            "properties": {
                "database_id": {"type": "string"},
            },
            "required": ["database_id"],
        }, self._get_database)

        self._register("notion_append_blocks", "Append content blocks to a page.", {
            "type": "object",
            "properties": {
                "page_id": {"type": "string", "description": "Page ID to append to"},
                "content": {"type": "string", "description": "Text content to append as paragraph blocks"},
            },
            "required": ["page_id", "content"],
        }, self._append_blocks)

        self._register("notion_get_block_children", "Get child blocks (content) of a page or block.", {
            "type": "object",
            "properties": {
                "block_id": {"type": "string", "description": "Page or block ID"},
            },
            "required": ["block_id"],
        }, self._get_block_children)

        self._register("notion_list_users", "List all users in the Notion workspace.", {
            "type": "object", "properties": {},
        }, self._list_users)

    # ── Handlers ───────────────────────────────────────────────

    async def _create_page(self, database_id: str, properties: dict, content: str = "") -> dict:
        result = await self.svc.create_page(database_id, properties, content=content)
        return result

    async def _update_page(self, page_id: str, properties: dict) -> dict:
        result = await self.svc.update_page(page_id, properties)
        return result

    async def _get_page(self, page_id: str) -> dict:
        result = await self.svc.get_page(page_id)
        return {"page": result}

    async def _archive_page(self, page_id: str) -> dict:
        result = await self.svc.archive_page(page_id)
        return {"archived": True, "page_id": page_id}

    async def _query_database(self, database_id: str, filter: dict = None, page_size: int = 100) -> dict:
        result = await self.svc.query_database(database_id, filter=filter, page_size=page_size)
        return result

    async def _search(self, query: str, filter_type: str = None) -> dict:
        result = await self.svc.search(query, filter_type=filter_type)
        return result

    async def _list_databases(self) -> dict:
        result = await self.svc.list_databases()
        return {"databases": result, "count": len(result)}

    async def _get_database(self, database_id: str) -> dict:
        result = await self.svc.get_database(database_id)
        return {"database": result}

    async def _append_blocks(self, page_id: str, content: str) -> dict:
        blocks = [self.svc.create_paragraph_block(content)]
        result = await self.svc.append_block_children(page_id, blocks)
        return {"appended": True, "page_id": page_id}

    async def _get_block_children(self, block_id: str) -> dict:
        result = await self.svc.get_block_children(block_id)
        return {"blocks": result}

    async def _list_users(self) -> dict:
        result = await self.svc.list_users()
        return {"users": result, "count": len(result)}

    async def close(self):
        await self.svc.close()
