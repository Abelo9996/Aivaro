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
                "filters": {"type": "object", "description": "Column filters as {column: value} for exact match"},
            },
            "required": ["table"],
        }, self._list_rows)

        self._register("supabase_get_row", "Get a single row from a Supabase table by ID.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "id_column": {"type": "string", "description": "ID column name", "default": "id"},
                "id_value": {"type": "string", "description": "ID value"},
            },
            "required": ["table", "id_value"],
        }, self._get_row)

        self._register("supabase_insert_row", "Insert a row into a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "data": {"type": "object", "description": "Row data as {column: value}"},
            },
            "required": ["table", "data"],
        }, self._insert_row)

        self._register("supabase_update_row", "Update a row in a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "id_column": {"type": "string", "description": "ID column name", "default": "id"},
                "id_value": {"type": "string", "description": "ID value of row to update"},
                "data": {"type": "object", "description": "Fields to update as {column: value}"},
            },
            "required": ["table", "id_value", "data"],
        }, self._update_row)

        self._register("supabase_delete_row", "Delete a row from a Supabase table.", {
            "type": "object",
            "properties": {
                "table": {"type": "string", "description": "Table name"},
                "id_column": {"type": "string", "description": "ID column name", "default": "id"},
                "id_value": {"type": "string", "description": "ID value of row to delete"},
            },
            "required": ["table", "id_value"],
        }, self._delete_row)

        self._register("supabase_rpc", "Call a Supabase stored procedure (RPC function).", {
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

    async def _get_row(self, table: str, id_value: str, id_column: str = "id") -> dict:
        return await self.svc.get_row(table, id_column, id_value)

    async def _insert_row(self, table: str, data: dict) -> dict:
        return await self.svc.insert_row(table, data)

    async def _update_row(self, table: str, id_value: str, data: dict, id_column: str = "id") -> dict:
        return await self.svc.update_row(table, id_column, id_value, data)

    async def _delete_row(self, table: str, id_value: str, id_column: str = "id") -> dict:
        return await self.svc.delete_row(table, id_column, id_value)

    async def _rpc_call(self, function_name: str, params: dict = None) -> dict:
        result = await self.svc.rpc_call(function_name, params)
        return {"result": result}

    async def close(self):
        await self.svc.close()
