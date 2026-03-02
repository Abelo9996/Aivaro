"""Airtable MCP Server — records, bases."""
from app.mcp_servers.base import BaseMCPServer


class AirtableMCPServer(BaseMCPServer):
    provider = "airtable"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.airtable_service import AirtableService
        self.svc = AirtableService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register(
            "airtable_create_record",
            "Create a record in an Airtable base/table.",
            {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string", "description": "Airtable base ID"},
                    "table_name": {"type": "string", "description": "Table name"},
                    "fields": {"type": "object", "description": "Field-value pairs"},
                },
                "required": ["base_id", "table_name", "fields"],
            },
            self._create_record,
        )
        self._register(
            "airtable_update_record",
            "Update an existing Airtable record.",
            {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string"},
                    "table_name": {"type": "string"},
                    "record_id": {"type": "string", "description": "Record ID to update"},
                    "fields": {"type": "object", "description": "Fields to update"},
                },
                "required": ["base_id", "table_name", "record_id", "fields"],
            },
            self._update_record,
        )
        self._register(
            "airtable_list_records",
            "List records from an Airtable table.",
            {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string"},
                    "table_name": {"type": "string"},
                    "max_records": {"type": "integer", "default": 100},
                    "filter_formula": {"type": "string", "description": "Airtable filter formula"},
                },
                "required": ["base_id", "table_name"],
            },
            self._list_records,
        )
        self._register(
            "airtable_find_record",
            "Find records matching a field value.",
            {
                "type": "object",
                "properties": {
                    "base_id": {"type": "string"},
                    "table_name": {"type": "string"},
                    "field_name": {"type": "string", "description": "Field to search"},
                    "field_value": {"type": "string", "description": "Value to match"},
                },
                "required": ["base_id", "table_name", "field_name", "field_value"],
            },
            self._find_record,
        )
        self._register(
            "airtable_list_bases",
            "List all Airtable bases the user has access to.",
            {"type": "object", "properties": {}},
            self._list_bases,
        )

    async def _create_record(self, base_id: str, table_name: str, fields: dict) -> dict:
        result = await self.svc.create_record(base_id, table_name, fields)
        return {"record_created": True, "record_id": result.get("id"), "fields": result.get("fields")}

    async def _update_record(self, base_id: str, table_name: str, record_id: str, fields: dict) -> dict:
        result = await self.svc.update_record(base_id, table_name, record_id, fields)
        return {"record_updated": True, "record_id": record_id, "fields": result.get("fields")}

    async def _list_records(self, base_id: str, table_name: str, max_records: int = 100, filter_formula: str = None) -> dict:
        records = await self.svc.list_records(base_id, table_name, max_records=max_records, filter_by_formula=filter_formula)
        return {"records": records, "count": len(records)}

    async def _find_record(self, base_id: str, table_name: str, field_name: str, field_value: str) -> dict:
        records = await self.svc.find_records_by_field(base_id, table_name, field_name, field_value)
        return {"records": records, "count": len(records), "found": len(records) > 0}

    async def _list_bases(self) -> dict:
        bases = await self.svc.list_bases()
        return {"bases": bases, "count": len(bases)}

    async def close(self):
        await self.svc.close()
