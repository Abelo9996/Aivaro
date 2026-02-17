"""
Mailchimp Service - Integration for Mailchimp Marketing API.
Supports audiences, campaigns, members, and automation.
"""
import httpx
from typing import Optional, Any
import hashlib


class MailchimpService:
    """Mailchimp Marketing API integration service."""
    
    def __init__(self, access_token: str, server_prefix: str = "us1"):
        """
        Initialize Mailchimp service with OAuth access token.
        
        Args:
            access_token: OAuth access token from Mailchimp authorization
            server_prefix: The Mailchimp server prefix (e.g., "us1", "us2")
        """
        self.access_token = access_token
        self.server_prefix = server_prefix
        self.base_url = f"https://{server_prefix}.api.mailchimp.com/3.0"
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def headers(self) -> dict:
        """Get headers for Mailchimp API requests."""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
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
        """Make a request to Mailchimp API."""
        client = await self._get_client()
        response = await client.request(
            method=method,
            url=endpoint,
            json=json,
            params=params,
        )
        response.raise_for_status()
        return response.json() if response.content else {}
    
    @staticmethod
    def get_subscriber_hash(email: str) -> str:
        """Get MD5 hash of lowercase email for subscriber operations."""
        return hashlib.md5(email.lower().encode()).hexdigest()
    
    # ========== Account Operations ==========
    
    async def get_account_info(self) -> dict:
        """
        Get information about the authenticated account.
        
        Returns:
            Account information including server prefix
        """
        return await self._request("GET", "/")
    
    # ========== Audience (List) Operations ==========
    
    async def list_audiences(
        self,
        count: int = 10,
        offset: int = 0,
    ) -> dict:
        """
        List all audiences (lists) in the account.
        
        Args:
            count: Number of results to return
            offset: Pagination offset
            
        Returns:
            Audiences collection
        """
        return await self._request(
            "GET",
            "/lists",
            params={"count": count, "offset": offset},
        )
    
    async def get_audience(self, list_id: str) -> dict:
        """
        Get information about a specific audience.
        
        Args:
            list_id: The ID of the audience
            
        Returns:
            Audience details
        """
        return await self._request("GET", f"/lists/{list_id}")
    
    async def create_audience(
        self,
        name: str,
        company: str,
        address1: str,
        city: str,
        state: str,
        zip: str,
        country: str,
        from_name: str,
        from_email: str,
        subject: str,
        permission_reminder: str,
    ) -> dict:
        """
        Create a new audience.
        
        Args:
            name: The name of the audience
            company: Company name for CAN-SPAM compliance
            address1: Street address
            city: City
            state: State
            zip: Zip code
            country: Country (2-letter code)
            from_name: Default from name for campaigns
            from_email: Default from email
            subject: Default subject line
            permission_reminder: Permission reminder text
            
        Returns:
            Created audience
        """
        return await self._request(
            "POST",
            "/lists",
            json={
                "name": name,
                "contact": {
                    "company": company,
                    "address1": address1,
                    "city": city,
                    "state": state,
                    "zip": zip,
                    "country": country,
                },
                "permission_reminder": permission_reminder,
                "campaign_defaults": {
                    "from_name": from_name,
                    "from_email": from_email,
                    "subject": subject,
                    "language": "en",
                },
                "email_type_option": True,
            },
        )
    
    # ========== Member (Subscriber) Operations ==========
    
    async def list_members(
        self,
        list_id: str,
        status: Optional[str] = None,
        count: int = 10,
        offset: int = 0,
    ) -> dict:
        """
        List members of an audience.
        
        Args:
            list_id: The ID of the audience
            status: Filter by status (subscribed, unsubscribed, cleaned, pending)
            count: Number of results
            offset: Pagination offset
            
        Returns:
            Members collection
        """
        params = {"count": count, "offset": offset}
        if status:
            params["status"] = status
        
        return await self._request(
            "GET",
            f"/lists/{list_id}/members",
            params=params,
        )
    
    async def get_member(
        self,
        list_id: str,
        email: str,
    ) -> dict:
        """
        Get a specific member by email.
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
            
        Returns:
            Member details
        """
        subscriber_hash = self.get_subscriber_hash(email)
        return await self._request(
            "GET",
            f"/lists/{list_id}/members/{subscriber_hash}",
        )
    
    async def add_member(
        self,
        list_id: str,
        email: str,
        status: str = "subscribed",
        merge_fields: Optional[dict] = None,
        tags: Optional[list[str]] = None,
    ) -> dict:
        """
        Add a new member to an audience.
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
            status: Subscription status (subscribed, pending, unsubscribed)
            merge_fields: Custom field values (e.g., {"FNAME": "John", "LNAME": "Doe"})
            tags: List of tag names to apply
            
        Returns:
            Created member
        """
        body = {
            "email_address": email,
            "status": status,
        }
        if merge_fields:
            body["merge_fields"] = merge_fields
        if tags:
            body["tags"] = tags
        
        return await self._request(
            "POST",
            f"/lists/{list_id}/members",
            json=body,
        )
    
    async def update_member(
        self,
        list_id: str,
        email: str,
        status: Optional[str] = None,
        merge_fields: Optional[dict] = None,
    ) -> dict:
        """
        Update a member's information.
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
            status: New subscription status
            merge_fields: Fields to update
            
        Returns:
            Updated member
        """
        subscriber_hash = self.get_subscriber_hash(email)
        body = {}
        if status:
            body["status"] = status
        if merge_fields:
            body["merge_fields"] = merge_fields
        
        return await self._request(
            "PATCH",
            f"/lists/{list_id}/members/{subscriber_hash}",
            json=body,
        )
    
    async def add_or_update_member(
        self,
        list_id: str,
        email: str,
        status: str = "subscribed",
        merge_fields: Optional[dict] = None,
    ) -> dict:
        """
        Add a new member or update existing (upsert).
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
            status: Subscription status
            merge_fields: Custom field values
            
        Returns:
            Member record
        """
        subscriber_hash = self.get_subscriber_hash(email)
        body = {
            "email_address": email,
            "status_if_new": status,
        }
        if merge_fields:
            body["merge_fields"] = merge_fields
        
        return await self._request(
            "PUT",
            f"/lists/{list_id}/members/{subscriber_hash}",
            json=body,
        )
    
    async def archive_member(
        self,
        list_id: str,
        email: str,
    ) -> None:
        """
        Archive (remove) a member from an audience.
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
        """
        subscriber_hash = self.get_subscriber_hash(email)
        client = await self._get_client()
        response = await client.delete(f"/lists/{list_id}/members/{subscriber_hash}")
        response.raise_for_status()
    
    # ========== Tag Operations ==========
    
    async def list_tags(self, list_id: str) -> dict:
        """
        List all tags for an audience.
        
        Args:
            list_id: The ID of the audience
            
        Returns:
            Tags collection
        """
        return await self._request("GET", f"/lists/{list_id}/tag-search")
    
    async def add_tags_to_member(
        self,
        list_id: str,
        email: str,
        tags: list[str],
    ) -> None:
        """
        Add tags to a member.
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
            tags: List of tag names to add
        """
        subscriber_hash = self.get_subscriber_hash(email)
        await self._request(
            "POST",
            f"/lists/{list_id}/members/{subscriber_hash}/tags",
            json={
                "tags": [{"name": tag, "status": "active"} for tag in tags]
            },
        )
    
    async def remove_tags_from_member(
        self,
        list_id: str,
        email: str,
        tags: list[str],
    ) -> None:
        """
        Remove tags from a member.
        
        Args:
            list_id: The ID of the audience
            email: The member's email address
            tags: List of tag names to remove
        """
        subscriber_hash = self.get_subscriber_hash(email)
        await self._request(
            "POST",
            f"/lists/{list_id}/members/{subscriber_hash}/tags",
            json={
                "tags": [{"name": tag, "status": "inactive"} for tag in tags]
            },
        )
    
    # ========== Campaign Operations ==========
    
    async def list_campaigns(
        self,
        status: Optional[str] = None,
        count: int = 10,
        offset: int = 0,
    ) -> dict:
        """
        List campaigns.
        
        Args:
            status: Filter by status (save, paused, schedule, sending, sent)
            count: Number of results
            offset: Pagination offset
            
        Returns:
            Campaigns collection
        """
        params = {"count": count, "offset": offset}
        if status:
            params["status"] = status
        
        return await self._request("GET", "/campaigns", params=params)
    
    async def get_campaign(self, campaign_id: str) -> dict:
        """
        Get a specific campaign.
        
        Args:
            campaign_id: The ID of the campaign
            
        Returns:
            Campaign details
        """
        return await self._request("GET", f"/campaigns/{campaign_id}")
    
    async def create_campaign(
        self,
        list_id: str,
        subject: str,
        from_name: str,
        reply_to: str,
        campaign_type: str = "regular",
        title: Optional[str] = None,
    ) -> dict:
        """
        Create a new campaign.
        
        Args:
            list_id: The ID of the audience
            subject: Email subject line
            from_name: From name
            reply_to: Reply-to email address
            campaign_type: Type of campaign (regular, plaintext, rss, variate)
            title: Internal campaign title
            
        Returns:
            Created campaign
        """
        return await self._request(
            "POST",
            "/campaigns",
            json={
                "type": campaign_type,
                "recipients": {"list_id": list_id},
                "settings": {
                    "subject_line": subject,
                    "title": title or subject,
                    "from_name": from_name,
                    "reply_to": reply_to,
                },
            },
        )
    
    async def set_campaign_content(
        self,
        campaign_id: str,
        html: str,
        plain_text: Optional[str] = None,
    ) -> dict:
        """
        Set the content of a campaign.
        
        Args:
            campaign_id: The ID of the campaign
            html: HTML content
            plain_text: Optional plain text version
            
        Returns:
            Updated campaign content
        """
        body = {"html": html}
        if plain_text:
            body["plain_text"] = plain_text
        
        return await self._request(
            "PUT",
            f"/campaigns/{campaign_id}/content",
            json=body,
        )
    
    async def send_campaign(self, campaign_id: str) -> None:
        """
        Send a campaign immediately.
        
        Args:
            campaign_id: The ID of the campaign
        """
        client = await self._get_client()
        response = await client.post(f"/campaigns/{campaign_id}/actions/send")
        response.raise_for_status()
    
    async def schedule_campaign(
        self,
        campaign_id: str,
        schedule_time: str,
    ) -> None:
        """
        Schedule a campaign for sending.
        
        Args:
            campaign_id: The ID of the campaign
            schedule_time: ISO 8601 datetime for sending
        """
        await self._request(
            "POST",
            f"/campaigns/{campaign_id}/actions/schedule",
            json={"schedule_time": schedule_time},
        )
    
    # ========== Template Operations ==========
    
    async def list_templates(
        self,
        template_type: Optional[str] = None,
        count: int = 10,
        offset: int = 0,
    ) -> dict:
        """
        List email templates.
        
        Args:
            template_type: Filter by type (user, base, gallery)
            count: Number of results
            offset: Pagination offset
            
        Returns:
            Templates collection
        """
        params = {"count": count, "offset": offset}
        if template_type:
            params["type"] = template_type
        
        return await self._request("GET", "/templates", params=params)
    
    async def get_template(self, template_id: str) -> dict:
        """
        Get a specific template.
        
        Args:
            template_id: The ID of the template
            
        Returns:
            Template details with HTML
        """
        return await self._request("GET", f"/templates/{template_id}")
    
    # ========== Helper Methods ==========
    
    @staticmethod
    def format_member_for_display(member: dict) -> dict:
        """Format a member for display."""
        return {
            "email": member.get("email_address"),
            "status": member.get("status"),
            "first_name": member.get("merge_fields", {}).get("FNAME"),
            "last_name": member.get("merge_fields", {}).get("LNAME"),
            "tags": [t.get("name") for t in member.get("tags", [])],
            "subscribed_at": member.get("timestamp_signup"),
        }
