"""
Notion Service - Integration for Notion API.
Supports databases, pages, and search functionality.
"""
import httpx
from typing import Optional, Any


class NotionService:
    """Notion API integration service."""
    
    BASE_URL = "https://api.notion.com/v1"
    NOTION_VERSION = "2022-06-28"
    
    def __init__(self, access_token: str):
        """
        Initialize Notion service with OAuth access token.
        
        Args:
            access_token: OAuth access token from Notion authorization
        """
        self.access_token = access_token
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def headers(self) -> dict:
        """Get headers for Notion API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Notion-Version": self.NOTION_VERSION,
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
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
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make a request to Notion API."""
        client = await self._get_client()
        response = await client.request(
            method=method,
            url=endpoint,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    
    # ========== Database Operations ==========
    
    async def list_databases(self) -> list[dict]:
        """
        List all databases the integration has access to.
        
        Returns:
            List of database objects
        """
        result = await self._request(
            "POST",
            "/search",
            json={
                "filter": {"property": "object", "value": "database"},
                "page_size": 100,
            },
        )
        return result.get("results", [])
    
    async def get_database(self, database_id: str) -> dict:
        """
        Get database metadata.
        
        Args:
            database_id: The ID of the database
            
        Returns:
            Database object with properties schema
        """
        return await self._request("GET", f"/databases/{database_id}")
    
    async def query_database(
        self,
        database_id: str,
        filter: Optional[dict] = None,
        sorts: Optional[list] = None,
        page_size: int = 100,
        start_cursor: Optional[str] = None,
    ) -> dict:
        """
        Query a database with optional filters and sorting.
        
        Args:
            database_id: The ID of the database to query
            filter: Notion filter object
            sorts: List of sort objects
            page_size: Number of results per page (max 100)
            start_cursor: Cursor for pagination
            
        Returns:
            Query results with pages
        """
        body = {"page_size": page_size}
        if filter:
            body["filter"] = filter
        if sorts:
            body["sorts"] = sorts
        if start_cursor:
            body["start_cursor"] = start_cursor
        
        return await self._request("POST", f"/databases/{database_id}/query", json=body)
    
    # ========== Page Operations ==========
    
    async def create_page(
        self,
        parent_database_id: str,
        properties: dict[str, Any],
        children: Optional[list] = None,
    ) -> dict:
        """
        Create a new page in a database.
        
        Args:
            parent_database_id: The database to add the page to
            properties: Page properties matching database schema
            children: Optional list of block children (content)
            
        Returns:
            Created page object
        """
        body = {
            "parent": {"database_id": parent_database_id},
            "properties": properties,
        }
        if children:
            body["children"] = children
        
        return await self._request("POST", "/pages", json=body)
    
    async def get_page(self, page_id: str) -> dict:
        """
        Get a page by ID.
        
        Args:
            page_id: The ID of the page
            
        Returns:
            Page object with properties
        """
        return await self._request("GET", f"/pages/{page_id}")
    
    async def update_page(
        self,
        page_id: str,
        properties: dict[str, Any],
    ) -> dict:
        """
        Update page properties.
        
        Args:
            page_id: The ID of the page to update
            properties: Properties to update
            
        Returns:
            Updated page object
        """
        return await self._request(
            "PATCH",
            f"/pages/{page_id}",
            json={"properties": properties},
        )
    
    async def archive_page(self, page_id: str) -> dict:
        """
        Archive (soft delete) a page.
        
        Args:
            page_id: The ID of the page to archive
            
        Returns:
            Archived page object
        """
        return await self._request(
            "PATCH",
            f"/pages/{page_id}",
            json={"archived": True},
        )
    
    # ========== Block Operations ==========
    
    async def get_block_children(
        self,
        block_id: str,
        page_size: int = 100,
        start_cursor: Optional[str] = None,
    ) -> dict:
        """
        Get children blocks of a page or block.
        
        Args:
            block_id: The ID of the parent block or page
            page_size: Number of results per page
            start_cursor: Cursor for pagination
            
        Returns:
            Block children with pagination
        """
        params = {"page_size": page_size}
        if start_cursor:
            params["start_cursor"] = start_cursor
        
        return await self._request(
            "GET",
            f"/blocks/{block_id}/children",
            params=params,
        )
    
    async def append_block_children(
        self,
        block_id: str,
        children: list[dict],
    ) -> dict:
        """
        Append blocks to a page or block.
        
        Args:
            block_id: The parent block or page ID
            children: List of block objects to append
            
        Returns:
            Appended blocks
        """
        return await self._request(
            "PATCH",
            f"/blocks/{block_id}/children",
            json={"children": children},
        )
    
    # ========== Search ==========
    
    async def search(
        self,
        query: str,
        filter_type: Optional[str] = None,
        page_size: int = 100,
    ) -> list[dict]:
        """
        Search across all pages and databases.
        
        Args:
            query: Search query string
            filter_type: "page" or "database" to filter results
            page_size: Number of results
            
        Returns:
            List of matching pages/databases
        """
        body = {"query": query, "page_size": page_size}
        if filter_type:
            body["filter"] = {"property": "object", "value": filter_type}
        
        result = await self._request("POST", "/search", json=body)
        return result.get("results", [])
    
    # ========== User Operations ==========
    
    async def list_users(self) -> list[dict]:
        """
        List all users in the workspace.
        
        Returns:
            List of user objects
        """
        result = await self._request("GET", "/users")
        return result.get("results", [])
    
    async def get_me(self) -> dict:
        """
        Get the current bot user.
        
        Returns:
            Bot user object
        """
        return await self._request("GET", "/users/me")
    
    # ========== Helper Methods ==========
    
    @staticmethod
    def create_title_property(text: str) -> dict:
        """Create a title property value."""
        return {"title": [{"text": {"content": text}}]}
    
    @staticmethod
    def create_rich_text_property(text: str) -> dict:
        """Create a rich text property value."""
        return {"rich_text": [{"text": {"content": text}}]}
    
    @staticmethod
    def create_number_property(value: float) -> dict:
        """Create a number property value."""
        return {"number": value}
    
    @staticmethod
    def create_select_property(option: str) -> dict:
        """Create a select property value."""
        return {"select": {"name": option}}
    
    @staticmethod
    def create_multi_select_property(options: list[str]) -> dict:
        """Create a multi-select property value."""
        return {"multi_select": [{"name": opt} for opt in options]}
    
    @staticmethod
    def create_date_property(start: str, end: Optional[str] = None) -> dict:
        """Create a date property value."""
        date = {"start": start}
        if end:
            date["end"] = end
        return {"date": date}
    
    @staticmethod
    def create_checkbox_property(checked: bool) -> dict:
        """Create a checkbox property value."""
        return {"checkbox": checked}
    
    @staticmethod
    def create_url_property(url: str) -> dict:
        """Create a URL property value."""
        return {"url": url}
    
    @staticmethod
    def create_email_property(email: str) -> dict:
        """Create an email property value."""
        return {"email": email}
    
    @staticmethod
    def create_phone_property(phone: str) -> dict:
        """Create a phone property value."""
        return {"phone_number": phone}
    
    @staticmethod
    def create_paragraph_block(text: str) -> dict:
        """Create a paragraph block."""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }
    
    @staticmethod
    def create_heading_block(text: str, level: int = 1) -> dict:
        """Create a heading block (level 1, 2, or 3)."""
        heading_type = f"heading_{min(max(level, 1), 3)}"
        return {
            "object": "block",
            "type": heading_type,
            heading_type: {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }
    
    @staticmethod
    def create_bulleted_list_block(text: str) -> dict:
        """Create a bulleted list item block."""
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{"type": "text", "text": {"content": text}}]
            },
        }
    
    @staticmethod
    def create_todo_block(text: str, checked: bool = False) -> dict:
        """Create a to-do block."""
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": [{"type": "text", "text": {"content": text}}],
                "checked": checked,
            },
        }
