"""
Airtable Service - Integration for Airtable API.
Supports bases, tables, records CRUD operations.
"""
import httpx
from typing import Optional, Any


class AirtableService:
    """Airtable API integration service."""
    
    BASE_URL = "https://api.airtable.com/v0"
    META_URL = "https://api.airtable.com/v0/meta"
    
    def __init__(self, access_token: str):
        """
        Initialize Airtable service with OAuth access token or personal access token.
        
        Args:
            access_token: OAuth access token or personal access token
        """
        self.access_token = access_token
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def headers(self) -> dict:
        """Get headers for Airtable API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers=self.headers,
                timeout=30.0,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    async def _request(
        self,
        method: str,
        url: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make a request to Airtable API."""
        client = await self._get_client()
        response = await client.request(
            method=method,
            url=url,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Base Operations ==========
    
    async def list_bases(self) -> list[dict]:
        """
        List all bases the user has access to.
        
        Returns:
            List of base objects with id, name, and permissionLevel
        """
        result = await self._request("GET", f"{self.META_URL}/bases")
        return result.get("bases", [])
    
    async def get_base_schema(self, base_id: str) -> dict:
        """
        Get the schema of a base including all tables and fields.
        
        Args:
            base_id: The ID of the base
            
        Returns:
            Base schema with tables array
        """
        return await self._request("GET", f"{self.META_URL}/bases/{base_id}/tables")
    
    # ========== Record Operations ==========
    
    async def list_records(
        self,
        base_id: str,
        table_name: str,
        view: Optional[str] = None,
        max_records: Optional[int] = None,
        page_size: int = 100,
        offset: Optional[str] = None,
        filter_formula: Optional[str] = None,
        sort: Optional[list[dict]] = None,
        fields: Optional[list[str]] = None,
    ) -> dict:
        """
        List records from a table.
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            view: View name or ID to filter by
            max_records: Maximum number of records to return
            page_size: Number of records per page (max 100)
            offset: Pagination offset
            filter_formula: Airtable formula to filter records
            sort: List of sort objects [{"field": "Name", "direction": "asc"}]
            fields: List of field names to return
            
        Returns:
            Records with pagination info
        """
        params = {"pageSize": min(page_size, 100)}
        
        if view:
            params["view"] = view
        if max_records:
            params["maxRecords"] = max_records
        if offset:
            params["offset"] = offset
        if filter_formula:
            params["filterByFormula"] = filter_formula
        if fields:
            params["fields[]"] = fields
        if sort:
            for i, s in enumerate(sort):
                params[f"sort[{i}][field]"] = s["field"]
                params[f"sort[{i}][direction]"] = s.get("direction", "asc")
        
        return await self._request(
            "GET",
            f"{self.BASE_URL}/{base_id}/{table_name}",
            params=params,
        )
    
    async def get_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
    ) -> dict:
        """
        Get a single record by ID.
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            record_id: The ID of the record
            
        Returns:
            Record object
        """
        return await self._request(
            "GET",
            f"{self.BASE_URL}/{base_id}/{table_name}/{record_id}",
        )
    
    async def create_record(
        self,
        base_id: str,
        table_name: str,
        fields: dict[str, Any],
        typecast: bool = False,
    ) -> dict:
        """
        Create a new record in a table.
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            fields: Field values for the record
            typecast: Whether to auto-convert field values
            
        Returns:
            Created record object
        """
        body = {"fields": fields}
        if typecast:
            body["typecast"] = True
        
        return await self._request(
            "POST",
            f"{self.BASE_URL}/{base_id}/{table_name}",
            json=body,
        )
    
    async def create_records(
        self,
        base_id: str,
        table_name: str,
        records: list[dict[str, Any]],
        typecast: bool = False,
    ) -> dict:
        """
        Create multiple records in a table (max 10 per request).
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            records: List of field dictionaries
            typecast: Whether to auto-convert field values
            
        Returns:
            Created records
        """
        body = {
            "records": [{"fields": r} for r in records],
        }
        if typecast:
            body["typecast"] = True
        
        return await self._request(
            "POST",
            f"{self.BASE_URL}/{base_id}/{table_name}",
            json=body,
        )
    
    async def update_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
        fields: dict[str, Any],
        typecast: bool = False,
    ) -> dict:
        """
        Update a record (partial update - only specified fields).
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            record_id: The ID of the record
            fields: Fields to update
            typecast: Whether to auto-convert field values
            
        Returns:
            Updated record object
        """
        body = {"fields": fields}
        if typecast:
            body["typecast"] = True
        
        return await self._request(
            "PATCH",
            f"{self.BASE_URL}/{base_id}/{table_name}/{record_id}",
            json=body,
        )
    
    async def update_records(
        self,
        base_id: str,
        table_name: str,
        records: list[dict],
        typecast: bool = False,
    ) -> dict:
        """
        Update multiple records (max 10 per request).
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            records: List of {"id": "...", "fields": {...}}
            typecast: Whether to auto-convert field values
            
        Returns:
            Updated records
        """
        body = {"records": records}
        if typecast:
            body["typecast"] = True
        
        return await self._request(
            "PATCH",
            f"{self.BASE_URL}/{base_id}/{table_name}",
            json=body,
        )
    
    async def delete_record(
        self,
        base_id: str,
        table_name: str,
        record_id: str,
    ) -> dict:
        """
        Delete a record.
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            record_id: The ID of the record
            
        Returns:
            Deleted record info
        """
        return await self._request(
            "DELETE",
            f"{self.BASE_URL}/{base_id}/{table_name}/{record_id}",
        )
    
    async def delete_records(
        self,
        base_id: str,
        table_name: str,
        record_ids: list[str],
    ) -> dict:
        """
        Delete multiple records (max 10 per request).
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            record_ids: List of record IDs to delete
            
        Returns:
            Deleted records info
        """
        params = {"records[]": record_ids}
        return await self._request(
            "DELETE",
            f"{self.BASE_URL}/{base_id}/{table_name}",
            params=params,
        )
    
    # ========== Search & Filter Helpers ==========
    
    async def find_records_by_field(
        self,
        base_id: str,
        table_name: str,
        field_name: str,
        value: Any,
        max_records: int = 100,
    ) -> list[dict]:
        """
        Find records where a field matches a value.
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            field_name: The field to search
            value: The value to match
            max_records: Maximum records to return
            
        Returns:
            List of matching records
        """
        # Escape single quotes in value
        if isinstance(value, str):
            escaped_value = value.replace("'", "\\'")
            formula = f"{{{field_name}}} = '{escaped_value}'"
        else:
            formula = f"{{{field_name}}} = {value}"
        
        result = await self.list_records(
            base_id=base_id,
            table_name=table_name,
            filter_formula=formula,
            max_records=max_records,
        )
        return result.get("records", [])
    
    async def get_all_records(
        self,
        base_id: str,
        table_name: str,
        view: Optional[str] = None,
        filter_formula: Optional[str] = None,
    ) -> list[dict]:
        """
        Get all records from a table, handling pagination.
        
        Args:
            base_id: The ID of the base
            table_name: The name or ID of the table
            view: Optional view to filter by
            filter_formula: Optional filter formula
            
        Returns:
            All records from the table
        """
        all_records = []
        offset = None
        
        while True:
            result = await self.list_records(
                base_id=base_id,
                table_name=table_name,
                view=view,
                filter_formula=filter_formula,
                offset=offset,
            )
            
            all_records.extend(result.get("records", []))
            offset = result.get("offset")
            
            if not offset:
                break
        
        return all_records
    
    # ========== Helper Methods ==========
    
    @staticmethod
    def extract_field_value(record: dict, field_name: str, default: Any = None) -> Any:
        """Extract a field value from a record."""
        return record.get("fields", {}).get(field_name, default)
    
    @staticmethod
    def format_record_for_display(record: dict) -> dict:
        """Format a record for display with id and fields flattened."""
        return {
            "id": record.get("id"),
            "createdTime": record.get("createdTime"),
            **record.get("fields", {}),
        }
