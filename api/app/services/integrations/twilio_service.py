"""
Twilio Service - Integration for Twilio API.
Supports SMS, voice calls, and WhatsApp messaging.
"""
import httpx
from typing import Optional
from base64 import b64encode


class TwilioService:
    """Twilio API integration service."""
    
    BASE_URL = "https://api.twilio.com/2010-04-01"
    
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        default_from: Optional[str] = None,
    ):
        """
        Initialize Twilio service with account credentials.
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            default_from: Default phone number to send from
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.default_from = default_from
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def headers(self) -> dict:
        """Get headers for Twilio API requests."""
        credentials = b64encode(
            f"{self.account_sid}:{self.auth_token}".encode()
        ).decode()
        return {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
    
    @property
    def api_base(self) -> str:
        """Get the base URL for account-specific endpoints."""
        return f"{self.BASE_URL}/Accounts/{self.account_sid}"
    
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
        endpoint: str,
        data: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> dict:
        """Make a request to Twilio API."""
        client = await self._get_client()
        response = await client.request(
            method=method,
            url=f"{self.api_base}{endpoint}",
            data=data,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    
    # ========== SMS Operations ==========
    
    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
        status_callback: Optional[str] = None,
        media_url: Optional[list[str]] = None,
    ) -> dict:
        """
        Send an SMS message.
        
        Args:
            to: The recipient phone number (E.164 format)
            body: The message text (max 1600 chars)
            from_number: The sender phone number (defaults to default_from)
            status_callback: URL for status webhooks
            media_url: List of media URLs for MMS
            
        Returns:
            Message resource
        """
        data = {
            "To": to,
            "Body": body,
            "From": from_number or self.default_from,
        }
        if status_callback:
            data["StatusCallback"] = status_callback
        if media_url:
            for i, url in enumerate(media_url):
                data[f"MediaUrl{i}"] = url
        
        return await self._request("POST", "/Messages.json", data=data)
    
    async def get_message(self, message_sid: str) -> dict:
        """
        Get details of a specific message.
        
        Args:
            message_sid: The SID of the message
            
        Returns:
            Message resource
        """
        return await self._request("GET", f"/Messages/{message_sid}.json")
    
    async def list_messages(
        self,
        to: Optional[str] = None,
        from_number: Optional[str] = None,
        date_sent: Optional[str] = None,
        page_size: int = 50,
    ) -> dict:
        """
        List messages.
        
        Args:
            to: Filter by recipient
            from_number: Filter by sender
            date_sent: Filter by date (YYYY-MM-DD)
            page_size: Number of results per page
            
        Returns:
            Messages collection
        """
        params = {"PageSize": page_size}
        if to:
            params["To"] = to
        if from_number:
            params["From"] = from_number
        if date_sent:
            params["DateSent"] = date_sent
        
        return await self._request("GET", "/Messages.json", params=params)
    
    # ========== WhatsApp Operations ==========
    
    async def send_whatsapp(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None,
        media_url: Optional[str] = None,
    ) -> dict:
        """
        Send a WhatsApp message.
        
        Args:
            to: The recipient phone number (E.164 format, without whatsapp: prefix)
            body: The message text
            from_number: The sender WhatsApp number (without whatsapp: prefix)
            media_url: Optional media URL
            
        Returns:
            Message resource
        """
        # Format WhatsApp numbers
        to_wa = f"whatsapp:{to}" if not to.startswith("whatsapp:") else to
        from_wa = from_number or self.default_from
        if from_wa and not from_wa.startswith("whatsapp:"):
            from_wa = f"whatsapp:{from_wa}"
        
        data = {
            "To": to_wa,
            "Body": body,
            "From": from_wa,
        }
        if media_url:
            data["MediaUrl"] = media_url
        
        return await self._request("POST", "/Messages.json", data=data)
    
    # ========== Voice Call Operations ==========
    
    async def make_call(
        self,
        to: str,
        twiml_url: Optional[str] = None,
        twiml: Optional[str] = None,
        from_number: Optional[str] = None,
        status_callback: Optional[str] = None,
        record: bool = False,
    ) -> dict:
        """
        Initiate an outbound voice call.
        
        Args:
            to: The recipient phone number (E.164 format)
            twiml_url: URL returning TwiML instructions
            twiml: Inline TwiML instructions
            from_number: The caller ID phone number
            status_callback: URL for call status webhooks
            record: Whether to record the call
            
        Returns:
            Call resource
        """
        data = {
            "To": to,
            "From": from_number or self.default_from,
        }
        
        if twiml_url:
            data["Url"] = twiml_url
        elif twiml:
            data["Twiml"] = twiml
        else:
            raise ValueError("Either twiml_url or twiml must be provided")
        
        if status_callback:
            data["StatusCallback"] = status_callback
        if record:
            data["Record"] = "true"
        
        return await self._request("POST", "/Calls.json", data=data)
    
    async def get_call(self, call_sid: str) -> dict:
        """
        Get details of a specific call.
        
        Args:
            call_sid: The SID of the call
            
        Returns:
            Call resource
        """
        return await self._request("GET", f"/Calls/{call_sid}.json")
    
    async def list_calls(
        self,
        to: Optional[str] = None,
        from_number: Optional[str] = None,
        status: Optional[str] = None,
        page_size: int = 50,
    ) -> dict:
        """
        List calls.
        
        Args:
            to: Filter by recipient
            from_number: Filter by caller
            status: Filter by status (queued, ringing, in-progress, completed, etc.)
            page_size: Number of results per page
            
        Returns:
            Calls collection
        """
        params = {"PageSize": page_size}
        if to:
            params["To"] = to
        if from_number:
            params["From"] = from_number
        if status:
            params["Status"] = status
        
        return await self._request("GET", "/Calls.json", params=params)
    
    async def update_call(
        self,
        call_sid: str,
        twiml_url: Optional[str] = None,
        twiml: Optional[str] = None,
        status: Optional[str] = None,
    ) -> dict:
        """
        Update an in-progress call.
        
        Args:
            call_sid: The SID of the call
            twiml_url: New TwiML URL
            twiml: Inline TwiML
            status: New status (canceled, completed)
            
        Returns:
            Updated call resource
        """
        data = {}
        if twiml_url:
            data["Url"] = twiml_url
        if twiml:
            data["Twiml"] = twiml
        if status:
            data["Status"] = status
        
        return await self._request("POST", f"/Calls/{call_sid}.json", data=data)
    
    # ========== Phone Number Operations ==========
    
    async def list_phone_numbers(
        self,
        phone_number: Optional[str] = None,
        friendly_name: Optional[str] = None,
    ) -> dict:
        """
        List phone numbers owned by the account.
        
        Args:
            phone_number: Filter by phone number
            friendly_name: Filter by friendly name
            
        Returns:
            Phone numbers collection
        """
        params = {}
        if phone_number:
            params["PhoneNumber"] = phone_number
        if friendly_name:
            params["FriendlyName"] = friendly_name
        
        return await self._request(
            "GET",
            "/IncomingPhoneNumbers.json",
            params=params,
        )
    
    async def get_phone_number(self, phone_number_sid: str) -> dict:
        """
        Get details of a specific phone number.
        
        Args:
            phone_number_sid: The SID of the phone number
            
        Returns:
            Phone number resource
        """
        return await self._request(
            "GET",
            f"/IncomingPhoneNumbers/{phone_number_sid}.json",
        )
    
    # ========== Lookup Operations ==========
    
    async def lookup_phone_number(
        self,
        phone_number: str,
        type_: Optional[list[str]] = None,
    ) -> dict:
        """
        Look up information about a phone number.
        
        Args:
            phone_number: The phone number to look up
            type_: Types of info to return (carrier, caller-name)
            
        Returns:
            Phone number lookup result
        """
        client = await self._get_client()
        url = f"https://lookups.twilio.com/v1/PhoneNumbers/{phone_number}"
        params = {}
        if type_:
            params["Type"] = type_
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    # ========== Account Operations ==========
    
    async def get_account_info(self) -> dict:
        """
        Get information about the current account.
        
        Returns:
            Account resource
        """
        return await self._request("GET", ".json")
    
    async def get_usage_records(
        self,
        category: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict:
        """
        Get usage records for the account.
        
        Args:
            category: Filter by usage category (sms, calls, etc.)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Usage records collection
        """
        params = {}
        if category:
            params["Category"] = category
        if start_date:
            params["StartDate"] = start_date
        if end_date:
            params["EndDate"] = end_date
        
        return await self._request(
            "GET",
            "/Usage/Records.json",
            params=params,
        )
    
    # ========== Helper Methods ==========
    
    @staticmethod
    def format_phone_number(number: str, country_code: str = "1") -> str:
        """
        Format a phone number to E.164 format.
        
        Args:
            number: The phone number (various formats)
            country_code: Default country code if not present
            
        Returns:
            E.164 formatted number
        """
        # Remove common characters
        cleaned = "".join(c for c in number if c.isdigit() or c == "+")
        
        if cleaned.startswith("+"):
            return cleaned
        elif cleaned.startswith("1") and len(cleaned) == 11:
            return f"+{cleaned}"
        elif len(cleaned) == 10:
            return f"+{country_code}{cleaned}"
        else:
            return f"+{cleaned}"
    
    @staticmethod
    def format_message_for_display(message: dict) -> dict:
        """Format a message for display."""
        return {
            "sid": message.get("sid"),
            "from": message.get("from"),
            "to": message.get("to"),
            "body": message.get("body"),
            "status": message.get("status"),
            "direction": message.get("direction"),
            "date_sent": message.get("date_sent"),
            "price": message.get("price"),
            "error_code": message.get("error_code"),
            "error_message": message.get("error_message"),
        }
    
    @staticmethod
    def format_call_for_display(call: dict) -> dict:
        """Format a call for display."""
        return {
            "sid": call.get("sid"),
            "from": call.get("from"),
            "to": call.get("to"),
            "status": call.get("status"),
            "direction": call.get("direction"),
            "duration": call.get("duration"),
            "start_time": call.get("start_time"),
            "end_time": call.get("end_time"),
            "price": call.get("price"),
        }
    
    @staticmethod
    def create_say_twiml(
        message: str,
        voice: str = "alice",
        language: str = "en-US",
    ) -> str:
        """
        Create TwiML for a simple voice message.
        
        Args:
            message: The text to speak
            voice: The voice to use (alice, man, woman)
            language: The language code
            
        Returns:
            TwiML string
        """
        return f'<Response><Say voice="{voice}" language="{language}">{message}</Say></Response>'
    
    @staticmethod
    def create_play_twiml(url: str) -> str:
        """
        Create TwiML to play an audio file.
        
        Args:
            url: The URL of the audio file
            
        Returns:
            TwiML string
        """
        return f'<Response><Play>{url}</Play></Response>'
