"""Supabase MCP Server — database CRUD, RPC."""
from app.mcp_servers.base import BaseMCPServer


class SupabaseMCPServer(BaseMCPServer):
    provider = "supabase"

    def __init__(self, url: str, api_key: str):
        super().__init__()
        from app.services.integrations.supabase_service import SupabaseService
        self.svc = SupabaseService(url=url, api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("supabase_list_rows", "List rows from a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "limit": {"type": "integer", "default": 50},
                "offset": {"type": "integer", "default": 0},
                "select": {"type": "string", "description": "Columns to select (PostgREST syntax)", "default": "*"},
                "filters": {"type": "object", "description": "Column=value equality filters"},
            },
            "required": ["table"],
        }, self._list_rows)

        self._register("supabase_get_row", "Get rows by column value from a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "column": {"type": "string", "description": "Column to filter on"},
                "value": {"type": "string", "description": "Value to match"},
            },
            "required": ["table", "column", "value"],
        }, self._get_row)

        self._register("supabase_insert_row", "Insert a row into a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "data": {"type": "object", "description": "Row data as key-value pairs"},
            },
            "required": ["table", "data"],
        }, self._insert_row)

        self._register("supabase_update_row", "Update rows in a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "column": {"type": "string", "description": "Filter column"},
                "value": {"type": "string", "description": "Filter value (equality match)"},
                "data": {"type": "object", "description": "Fields to update"},
            },
            "required": ["table", "column", "value", "data"],
        }, self._update_row)

        self._register("supabase_delete_row", "Delete rows from a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "column": {"type": "string", "description": "Filter column"},
                "value": {"type": "string", "description": "Filter value (equality match)"},
            },
            "required": ["table", "column", "value"],
        }, self._delete_row)

        self._register("supabase_rpc", "Call a Supabase/PostgreSQL stored function (RPC).", {
            "type": "object",
            "properties": {
                "function_name": {"type": "string", "description": "Function name"},
                "params": {"type": "object", "description": "Function parameters"},
            },
            "required": ["function_name"],
        }, self._rpc_call)

    async def _list_rows(self, table: str, limit: int = 50, offset: int = 0,
                         select: str = "*", filters: dict = None) -> dict:
        rows = await self.svc.list_rows(table, limit, offset, select, filters)
        return {"rows": rows, "count": len(rows)}

    async def _get_row(self, table: str, column: str, value: str) -> dict:
        rows = await self.svc.get_row(table, column, value)
        return {"rows": rows, "count": len(rows)}

    async def _insert_row(self, table: str, data: dict) -> dict:
        result = await self.svc.insert_row(table, data)
        return {"inserted": result}

    async def _update_row(self, table: str, column: str, value: str, data: dict) -> dict:
        result = await self.svc.update_row(table, column, value, data)
        return {"updated": result}

    async def _delete_row(self, table: str, column: str, value: str) -> dict:
        result = await self.svc.delete_row(table, column, value)
        return {"deleted": result}

    async def _rpc_call(self, function_name: str, params: dict = None) -> dict:
        result = await self.svc.rpc_call(function_name, params)
        return {"result": result}

    async def close(self):
        await self.svc.close()
