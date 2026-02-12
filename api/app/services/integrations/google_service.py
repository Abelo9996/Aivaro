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
    
    async def get_header_row(
        self,
        spreadsheet_id: str,
        sheet_name: str = "Sheet1"
    ) -> List[str]:
        """Get the header row (first row) from a spreadsheet."""
        try:
            values = await self.get_sheet_values(spreadsheet_id, f"{sheet_name}!A1:ZZ1")
            if values and len(values) > 0:
                return [str(h).strip() for h in values[0]]
            return []
        except Exception as e:
            print(f"[GoogleService] Failed to get header row: {e}")
            return []
    
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
    
    async def append_row_with_schema(
        self,
        spreadsheet_id: str,
        data: dict,
        sheet_name: str = "Sheet1"
    ) -> dict:
        """Append a row matching the spreadsheet's column schema.
        
        This reads the header row first, then orders the data values
        to match the column positions in the sheet.
        """
        # Get the header row to understand column order
        headers = await self.get_header_row(spreadsheet_id, sheet_name)
        
        print(f"[GoogleService] Sheet headers: {headers}")
        print(f"[GoogleService] Input data keys: {list(data.keys())}")
        
        if not headers:
            # No headers found - just append the values as a list
            values = list(data.values()) if isinstance(data, dict) else data
            return await self.append_row(spreadsheet_id, values, sheet_name)
        
        # Normalize header for matching: "Customer Name" -> "customer_name", "customer name", etc.
        def normalize(s: str) -> str:
            return s.lower().replace(" ", "_").replace("-", "_")
        
        # Map from normalized header to possible data keys
        # Format: "normalized_header": ["possible_data_key1", "possible_data_key2", ...]
        header_to_data_keys = {
            "customer_name": ["customer_name", "name", "client_name", "full_name", "customer"],
            "customer_email": ["customer_email", "email", "client_email", "user_email"],
            "pickup_date": ["pickup_date", "date", "appointment_date", "booking_date", "event_date", "today"],
            "pickup_time": ["pickup_time", "time", "appointment_time", "booking_time", "event_time", "start_time"],
            "customer_phone": ["customer_phone", "phone", "phone_number", "mobile", "cell", "tel"],
            "pickup_type": ["pickup_type", "service", "service_type", "type", "service_name"],
            "status": ["status", "booking_status", "payment_status", "state"],
            "payment_url": ["payment_url", "payment_link_url", "payment_link", "link", "url"],
            "notes": ["notes", "description", "comments", "message", "details"],
            "amount": ["amount", "price", "cost", "total", "fee", "payment_amount"],
            "date": ["date", "pickup_date", "appointment_date", "booking_date", "today"],
            "time": ["time", "pickup_time", "appointment_time", "booking_time"],
            "name": ["name", "customer_name", "client_name", "full_name"],
            "email": ["email", "customer_email", "client_email", "user_email"],
            "phone": ["phone", "customer_phone", "phone_number", "mobile"],
            "service": ["service", "pickup_type", "service_type", "type"],
            "link": ["link", "payment_url", "payment_link_url", "payment_link", "url"],
        }
        
        # Build row matching header order
        row_values = []
        for header in headers:
            value = ""
            normalized_header = normalize(header)
            
            # 1. Try exact match with original header
            if header in data and data[header]:
                value = data[header]
            
            # 2. Try normalized header as key
            if not value and normalized_header in data and data[normalized_header]:
                value = data[normalized_header]
            
            # 3. Try case-insensitive match on all keys
            if not value:
                header_lower = header.lower()
                for key, val in data.items():
                    if key.lower() == header_lower or normalize(key) == normalized_header:
                        if val:
                            value = val
                            break
            
            # 4. Try alias mapping
            if not value and normalized_header in header_to_data_keys:
                for possible_key in header_to_data_keys[normalized_header]:
                    if possible_key in data and data[possible_key]:
                        value = data[possible_key]
                        break
                    # Also try case-insensitive
                    for key, val in data.items():
                        if key.lower() == possible_key.lower() and val:
                            value = val
                            break
                    if value:
                        break
            
            row_values.append(str(value) if value else "")
        
        print(f"[GoogleService] Appending row with schema-matched columns: {headers}")
        print(f"[GoogleService] Row values: {row_values}")
        
        return await self.append_row(spreadsheet_id, row_values, sheet_name)
    
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
