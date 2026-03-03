"""Airtable MCP Server — records, bases, tables."""
from app.mcp_servers.base import BaseMCPServer


class AirtableMCPServer(BaseMCPServer):
    provider = "airtable"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.airtable_service import AirtableService
        self.svc = AirtableService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("airtable_create_record", "Create a record in an Airtable table.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string", "description": "Airtable base ID (e.g. appXXX)"},
                "table_name": {"type": "string", "description": "Table name"},
                "fields": {"type": "object", "description": "Field name-value pairs"},
            },
            "required": ["base_id", "table_name", "fields"],
        }, self._create_record)

        self._register("airtable_create_records", "Create multiple records in an Airtable table.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
                "table_name": {"type": "string"},
                "records": {"type": "array", "items": {"type": "object"}, "description": "Array of field objects"},
            },
            "required": ["base_id", "table_name", "records"],
        }, self._create_records)

        self._register("airtable_update_record", "Update a record in an Airtable table.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
                "table_name": {"type": "string"},
                "record_id": {"type": "string", "description": "Record ID (e.g. recXXX)"},
                "fields": {"type": "object", "description": "Field name-value pairs to update"},
            },
            "required": ["base_id", "table_name", "record_id", "fields"],
        }, self._update_record)

        self._register("airtable_delete_record", "Delete a record from an Airtable table.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
                "table_name": {"type": "string"},
                "record_id": {"type": "string"},
            },
            "required": ["base_id", "table_name", "record_id"],
        }, self._delete_record)

        self._register("airtable_get_record", "Get a single record by ID.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
                "table_name": {"type": "string"},
                "record_id": {"type": "string"},
            },
            "required": ["base_id", "table_name", "record_id"],
        }, self._get_record)

        self._register("airtable_find_record", "Find records by matching a field value.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
                "table_name": {"type": "string"},
                "field_name": {"type": "string", "description": "Field to search"},
                "field_value": {"type": "string", "description": "Value to match"},
            },
            "required": ["base_id", "table_name", "field_name", "field_value"],
        }, self._find_record)

        self._register("airtable_list_records", "List records from an Airtable table.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
                "table_name": {"type": "string"},
                "max_records": {"type": "integer", "default": 100},
                "formula": {"type": "string", "description": "Airtable formula filter"},
            },
            "required": ["base_id", "table_name"],
        }, self._list_records)

        self._register("airtable_list_bases", "List all accessible Airtable bases.", {
            "type": "object", "properties": {},
        }, self._list_bases)

        self._register("airtable_get_base_schema", "Get the schema (tables and fields) of a base.", {
            "type": "object",
            "properties": {
                "base_id": {"type": "string"},
            },
            "required": ["base_id"],
        }, self._get_base_schema)

    # ── Handlers ───────────────────────────────────────────────

    async def _create_record(self, base_id: str, table_name: str, fields: dict) -> dict:
        result = await self.svc.create_record(base_id, table_name, fields)
        return result

    async def _create_records(self, base_id: str, table_name: str, records: list) -> dict:
        result = await self.svc.create_records(base_id, table_name, records)
        return {"records": result, "count": len(result)}

    async def _update_record(self, base_id: str, table_name: str, record_id: str, fields: dict) -> dict:
        result = await self.svc.update_record(base_id, table_name, record_id, fields)
        return result

    async def _delete_record(self, base_id: str, table_name: str, record_id: str) -> dict:
        result = await self.svc.delete_record(base_id, table_name, record_id)
        return {"deleted": True, "record_id": record_id}

    async def _get_record(self, base_id: str, table_name: str, record_id: str) -> dict:
        result = await self.svc.get_record(base_id, table_name, record_id)
        return {"record": result}

    async def _find_record(self, base_id: str, table_name: str, field_name: str, field_value: str) -> dict:
        records = await self.svc.find_records_by_field(base_id, table_name, field_name, field_value)
        return {"records": records, "count": len(records), "found": len(records) > 0}

    async def _list_records(self, base_id: str, table_name: str, max_records: int = 100, formula: str = None) -> dict:
        records = await self.svc.list_records(base_id, table_name, max_records=max_records, formula=formula)
        return {"records": records, "count": len(records)}

    async def _list_bases(self) -> dict:
        bases = await self.svc.list_bases()
        return {"bases": bases, "count": len(bases)}

    async def _get_base_schema(self, base_id: str) -> dict:
        schema = await self.svc.get_base_schema(base_id)
        return {"schema": schema}

    async def close(self):
        await self.svc.close()
