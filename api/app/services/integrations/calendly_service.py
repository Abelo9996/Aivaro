"""
Calendly Service - Integration for Calendly API.
Supports event types, scheduled events, and invitees.
"""
import httpx
from typing import Optional
from datetime import datetime


class CalendlyService:
    """Calendly API integration service."""
    
    BASE_URL = "https://api.calendly.com"
    
    def __init__(self, access_token: str):
        """
        Initialize Calendly service with OAuth access token.
        
        Args:
            access_token: OAuth access token from Calendly authorization
        """
        self.access_token = access_token
        self._client: Optional[httpx.AsyncClient] = None
        self._current_user: Optional[dict] = None
    
    @property
    def headers(self) -> dict:
        """Get headers for Calendly API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
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
        """Make a request to Calendly API."""
        client = await self._get_client()
        response = await client.request(
            method=method,
            url=endpoint,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json()
    
    # ========== User Operations ==========
    
    async def get_current_user(self) -> dict:
        """
        Get the current authenticated user.
        
        Returns:
            User resource object
        """
        if self._current_user is None:
            result = await self._request("GET", "/users/me")
            self._current_user = result.get("resource", {})
        return self._current_user
    
    async def get_user_uri(self) -> str:
        """Get the current user's URI for API calls."""
        user = await self.get_current_user()
        return user.get("uri", "")
    
    async def get_organization_uri(self) -> str:
        """Get the current user's organization URI."""
        user = await self.get_current_user()
        return user.get("current_organization", "")
    
    # ========== Event Type Operations ==========
    
    async def list_event_types(
        self,
        active: Optional[bool] = True,
        count: int = 20,
        page_token: Optional[str] = None,
    ) -> dict:
        """
        List event types for the authenticated user.
        
        Args:
            active: Filter by active status
            count: Number of results per page
            page_token: Token for pagination
            
        Returns:
            Event types collection
        """
        user_uri = await self.get_user_uri()
        params = {
            "user": user_uri,
            "count": count,
        }
        if active is not None:
            params["active"] = str(active).lower()
        if page_token:
            params["page_token"] = page_token
        
        return await self._request("GET", "/event_types", params=params)
    
    async def get_event_type(self, event_type_uuid: str) -> dict:
        """
        Get a specific event type.
        
        Args:
            event_type_uuid: The UUID of the event type
            
        Returns:
            Event type resource
        """
        result = await self._request("GET", f"/event_types/{event_type_uuid}")
        return result.get("resource", {})
    
    # ========== Scheduled Events Operations ==========
    
    async def list_scheduled_events(
        self,
        status: Optional[str] = None,
        min_start_time: Optional[str] = None,
        max_start_time: Optional[str] = None,
        count: int = 20,
        page_token: Optional[str] = None,
        sort: str = "start_time:asc",
    ) -> dict:
        """
        List scheduled events for the authenticated user.
        
        Args:
            status: "active" or "canceled"
            min_start_time: ISO 8601 datetime for minimum start time
            max_start_time: ISO 8601 datetime for maximum start time
            count: Number of results per page
            page_token: Token for pagination
            sort: Sort order (start_time:asc or start_time:desc)
            
        Returns:
            Scheduled events collection
        """
        user_uri = await self.get_user_uri()
        params = {
            "user": user_uri,
            "count": count,
            "sort": sort,
        }
        if status:
            params["status"] = status
        if min_start_time:
            params["min_start_time"] = min_start_time
        if max_start_time:
            params["max_start_time"] = max_start_time
        if page_token:
            params["page_token"] = page_token
        
        return await self._request("GET", "/scheduled_events", params=params)
    
    async def get_scheduled_event(self, event_uuid: str) -> dict:
        """
        Get a specific scheduled event.
        
        Args:
            event_uuid: The UUID of the scheduled event
            
        Returns:
            Scheduled event resource
        """
        result = await self._request("GET", f"/scheduled_events/{event_uuid}")
        return result.get("resource", {})
    
    async def cancel_scheduled_event(
        self,
        event_uuid: str,
        reason: Optional[str] = None,
    ) -> dict:
        """
        Cancel a scheduled event.
        
        Args:
            event_uuid: The UUID of the event to cancel
            reason: Optional cancellation reason
            
        Returns:
            Cancellation result
        """
        body = {}
        if reason:
            body["reason"] = reason
        
        return await self._request(
            "POST",
            f"/scheduled_events/{event_uuid}/cancellation",
            json=body,
        )
    
    # ========== Invitee Operations ==========
    
    async def list_event_invitees(
        self,
        event_uuid: str,
        status: Optional[str] = None,
        count: int = 20,
        page_token: Optional[str] = None,
    ) -> dict:
        """
        List invitees for a scheduled event.
        
        Args:
            event_uuid: The UUID of the scheduled event
            status: "active" or "canceled"
            count: Number of results per page
            page_token: Token for pagination
            
        Returns:
            Invitees collection
        """
        params = {"count": count}
        if status:
            params["status"] = status
        if page_token:
            params["page_token"] = page_token
        
        return await self._request(
            "GET",
            f"/scheduled_events/{event_uuid}/invitees",
            params=params,
        )
    
    async def get_invitee(self, invitee_uuid: str) -> dict:
        """
        Get a specific invitee.
        
        Args:
            invitee_uuid: The UUID of the invitee
            
        Returns:
            Invitee resource
        """
        result = await self._request("GET", f"/invitees/{invitee_uuid}")
        return result.get("resource", {})
    
    # ========== Scheduling Links ==========
    
    async def create_scheduling_link(
        self,
        event_type_uri: str,
        max_event_count: int = 1,
    ) -> dict:
        """
        Create a single-use scheduling link.
        
        Args:
            event_type_uri: The URI of the event type
            max_event_count: Maximum number of events that can be scheduled
            
        Returns:
            Scheduling link resource
        """
        return await self._request(
            "POST",
            "/scheduling_links",
            json={
                "owner": event_type_uri,
                "owner_type": "EventType",
                "max_event_count": max_event_count,
            },
        )
    
    # ========== Availability ==========
    
    async def get_user_availability_schedules(self) -> dict:
        """
        Get availability schedules for the current user.
        
        Returns:
            Availability schedules collection
        """
        user_uri = await self.get_user_uri()
        return await self._request(
            "GET",
            "/user_availability_schedules",
            params={"user": user_uri},
        )
    
    async def get_user_busy_times(
        self,
        start_time: str,
        end_time: str,
    ) -> dict:
        """
        Get busy time slots for the current user.
        
        Args:
            start_time: ISO 8601 datetime for start of range
            end_time: ISO 8601 datetime for end of range
            
        Returns:
            Busy times collection
        """
        user_uri = await self.get_user_uri()
        return await self._request(
            "GET",
            "/user_busy_times",
            params={
                "user": user_uri,
                "start_time": start_time,
                "end_time": end_time,
            },
        )
    
    # ========== Webhooks ==========
    
    async def list_webhook_subscriptions(
        self,
        scope: str = "user",
    ) -> dict:
        """
        List webhook subscriptions.
        
        Args:
            scope: "user" or "organization"
            
        Returns:
            Webhook subscriptions collection
        """
        if scope == "organization":
            org_uri = await self.get_organization_uri()
            params = {"organization": org_uri, "scope": scope}
        else:
            user_uri = await self.get_user_uri()
            params = {"user": user_uri, "scope": scope}
        
        return await self._request("GET", "/webhook_subscriptions", params=params)
    
    async def create_webhook_subscription(
        self,
        url: str,
        events: list[str],
        scope: str = "user",
        signing_key: Optional[str] = None,
    ) -> dict:
        """
        Create a webhook subscription.
        
        Args:
            url: The URL to receive webhook events
            events: List of event types (e.g., ["invitee.created", "invitee.canceled"])
            scope: "user" or "organization"
            signing_key: Optional key for webhook signature verification
            
        Returns:
            Created webhook subscription
        """
        if scope == "organization":
            org_uri = await self.get_organization_uri()
            body = {"organization": org_uri, "scope": scope}
        else:
            user_uri = await self.get_user_uri()
            body = {"user": user_uri, "scope": scope}
        
        body.update({
            "url": url,
            "events": events,
        })
        if signing_key:
            body["signing_key"] = signing_key
        
        return await self._request("POST", "/webhook_subscriptions", json=body)
    
    async def delete_webhook_subscription(self, webhook_uuid: str) -> None:
        """
        Delete a webhook subscription.
        
        Args:
            webhook_uuid: The UUID of the webhook subscription
        """
        client = await self._get_client()
        response = await client.delete(f"/webhook_subscriptions/{webhook_uuid}")
        response.raise_for_status()
    
    # ========== Helper Methods ==========
    
    @staticmethod
    def extract_uuid_from_uri(uri: str) -> str:
        """Extract the UUID from a Calendly URI."""
        return uri.split("/")[-1]
    
    @staticmethod
    def format_event_for_display(event: dict) -> dict:
        """Format an event for display."""
        return {
            "uuid": CalendlyService.extract_uuid_from_uri(event.get("uri", "")),
            "name": event.get("name"),
            "status": event.get("status"),
            "start_time": event.get("start_time"),
            "end_time": event.get("end_time"),
            "location": event.get("location", {}).get("location"),
            "event_type": CalendlyService.extract_uuid_from_uri(
                event.get("event_type", "")
            ),
        }
    
    @staticmethod
    def format_invitee_for_display(invitee: dict) -> dict:
        """Format an invitee for display."""
        return {
            "uuid": CalendlyService.extract_uuid_from_uri(invitee.get("uri", "")),
            "name": invitee.get("name"),
            "email": invitee.get("email"),
            "status": invitee.get("status"),
            "timezone": invitee.get("timezone"),
            "created_at": invitee.get("created_at"),
        }
