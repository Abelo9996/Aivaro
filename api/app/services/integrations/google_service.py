"""
Google Services Integration - Sheets, Gmail, Calendar
"""
import httpx
from typing import Optional, List, Any
from datetime import datetime


class GoogleService:
    """Service for interacting with Google APIs."""
    
    BASE_SHEETS_URL = "https://sheets.googleapis.com/v4/spreadsheets"
    BASE_GMAIL_URL = "https://gmail.googleapis.com/gmail/v1/users/me"
    BASE_CALENDAR_URL = "https://www.googleapis.com/calendar/v3"
    
    def __init__(self, access_token: str, refresh_token: Optional[str] = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self._client = None
    
    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # ==================== Google Sheets ====================
    
    async def list_spreadsheets(self) -> List[dict]:
        """List user's spreadsheets via Google Drive API."""
        client = await self._get_client()
        response = await client.get(
            "https://www.googleapis.com/drive/v3/files",
            params={
                "q": "mimeType='application/vnd.google-apps.spreadsheet'",
                "fields": "files(id,name,modifiedTime)",
                "orderBy": "modifiedTime desc",
                "pageSize": 50,
            },
            headers=self.headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("files", [])
        else:
            raise Exception(f"Failed to list spreadsheets: {response.text}")
    
    async def find_spreadsheet_by_name(self, name: str) -> Optional[str]:
        """Find a spreadsheet by name and return its ID."""
        client = await self._get_client()
        # Search for spreadsheet by name
        response = await client.get(
            "https://www.googleapis.com/drive/v3/files",
            params={
                "q": f"mimeType='application/vnd.google-apps.spreadsheet' and name contains '{name}'",
                "fields": "files(id,name)",
                "pageSize": 10,
            },
            headers=self.headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            files = data.get("files", [])
            # Exact match first
            for f in files:
                if f["name"].lower() == name.lower():
                    return f["id"]
            # Partial match
            if files:
                return files[0]["id"]
            return None
        else:
            raise Exception(f"Failed to search spreadsheets: {response.text}")

    async def get_spreadsheet(self, spreadsheet_id: str) -> dict:
        """Get spreadsheet metadata."""
        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_SHEETS_URL}/{spreadsheet_id}",
            headers=self.headers,
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get spreadsheet: {response.text}")
    
    async def get_sheet_values(
        self, 
        spreadsheet_id: str, 
        range_name: str = "Sheet1"
    ) -> List[List[Any]]:
        """Get values from a spreadsheet range."""
        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_SHEETS_URL}/{spreadsheet_id}/values/{range_name}",
            headers=self.headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("values", [])
        else:
            raise Exception(f"Failed to get sheet values: {response.text}")
    
    async def append_row(
        self, 
        spreadsheet_id: str, 
        values: List[Any],
        sheet_name: str = "Sheet1"
    ) -> dict:
        """Append a row to a spreadsheet."""
        client = await self._get_client()
        response = await client.post(
            f"{self.BASE_SHEETS_URL}/{spreadsheet_id}/values/{sheet_name}:append",
            params={
                "valueInputOption": "USER_ENTERED",
                "insertDataOption": "INSERT_ROWS",
            },
            headers=self.headers,
            json={
                "values": [values]
            },
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to append row: {response.text}")
    
    async def create_spreadsheet(self, title: str) -> dict:
        """Create a new spreadsheet."""
        client = await self._get_client()
        response = await client.post(
            self.BASE_SHEETS_URL,
            headers=self.headers,
            json={
                "properties": {"title": title}
            },
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create spreadsheet: {response.text}")
    
    async def find_or_create_spreadsheet(self, name: str) -> str:
        """Find a spreadsheet by name or create it if not found."""
        spreadsheets = await self.list_spreadsheets()
        
        for sheet in spreadsheets:
            if sheet.get("name", "").lower() == name.lower():
                return sheet["id"]
        
        # Create new spreadsheet
        result = await self.create_spreadsheet(name)
        return result["spreadsheetId"]
    
    # ==================== Gmail ====================
    
    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> dict:
        """Send an email via Gmail API."""
        import base64
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Create message
        if html:
            message = MIMEMultipart("alternative")
            message.attach(MIMEText(body, "plain"))
            message.attach(MIMEText(body, "html"))
        else:
            message = MIMEText(body)
        
        message["to"] = to
        message["subject"] = subject
        
        # Encode message
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        client = await self._get_client()
        response = await client.post(
            f"{self.BASE_GMAIL_URL}/messages/send",
            headers=self.headers,
            json={"raw": raw},
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send email: {response.text}")
    
    async def list_messages(
        self, 
        query: str = "", 
        max_results: int = 10
    ) -> List[dict]:
        """List Gmail messages."""
        client = await self._get_client()
        params = {"maxResults": max_results}
        if query:
            params["q"] = query
        
        response = await client.get(
            f"{self.BASE_GMAIL_URL}/messages",
            params=params,
            headers=self.headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("messages", [])
        else:
            raise Exception(f"Failed to list messages: {response.text}")
    
    async def get_message(self, message_id: str) -> dict:
        """Get a specific Gmail message."""
        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_GMAIL_URL}/messages/{message_id}",
            params={"format": "full"},
            headers=self.headers,
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get message: {response.text}")
    
    # ==================== Calendar ====================
    
    async def list_calendars(self) -> List[dict]:
        """List user's calendars."""
        client = await self._get_client()
        response = await client.get(
            f"{self.BASE_CALENDAR_URL}/users/me/calendarList",
            headers=self.headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            raise Exception(f"Failed to list calendars: {response.text}")
    
    async def list_events(
        self, 
        calendar_id: str = "primary",
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        max_results: int = 10
    ) -> List[dict]:
        """List calendar events."""
        client = await self._get_client()
        params = {
            "maxResults": max_results,
            "singleEvents": True,
            "orderBy": "startTime",
        }
        
        if time_min:
            params["timeMin"] = time_min
        else:
            params["timeMin"] = datetime.utcnow().isoformat() + "Z"
        
        if time_max:
            params["timeMax"] = time_max
        
        response = await client.get(
            f"{self.BASE_CALENDAR_URL}/calendars/{calendar_id}/events",
            params=params,
            headers=self.headers,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("items", [])
        else:
            raise Exception(f"Failed to list events: {response.text}")
    
    async def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        description: str = "",
        calendar_id: str = "primary",
        attendees: Optional[List[str]] = None
    ) -> dict:
        """Create a calendar event."""
        client = await self._get_client()
        
        event_data = {
            "summary": summary,
            "description": description,
            "start": {"dateTime": start_time, "timeZone": "UTC"},
            "end": {"dateTime": end_time, "timeZone": "UTC"},
        }
        
        if attendees:
            event_data["attendees"] = [{"email": email} for email in attendees]
        
        response = await client.post(
            f"{self.BASE_CALENDAR_URL}/calendars/{calendar_id}/events",
            headers=self.headers,
            json=event_data,
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to create event: {response.text}")
