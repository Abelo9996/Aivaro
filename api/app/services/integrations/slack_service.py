"""
Slack Integration Service
"""
import httpx
from typing import Optional, List, Any


class SlackService:
    """Service for interacting with Slack API."""
    
    BASE_URL = "https://slack.com/api"
    
    def __init__(self, access_token: str):
        self.access_token = access_token
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
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> dict:
        """Make a request to Slack API."""
        client = await self._get_client()
        url = f"{self.BASE_URL}/{endpoint}"
        
        response = await client.request(
            method,
            url,
            headers=self.headers,
            **kwargs
        )
        
        data = response.json()
        if not data.get("ok"):
            error = data.get("error", "Unknown error")
            needed = data.get("needed", "")
            provided = data.get("provided", "")
            detail = f"Slack API error: {error}"
            if needed:
                detail += f" (needed scope: {needed}, provided: {provided})"
            raise Exception(detail)
        
        return data
    
    # ==================== Channels ====================
    
    async def list_channels(self, exclude_archived: bool = True) -> List[dict]:
        """List all public channels."""
        data = await self._request(
            "GET",
            "conversations.list",
            params={
                "exclude_archived": exclude_archived,
                "types": "public_channel,private_channel",
                "limit": 100,
            }
        )
        return data.get("channels", [])
    
    async def get_channel_info(self, channel_id: str) -> dict:
        """Get info about a channel."""
        data = await self._request(
            "GET",
            "conversations.info",
            params={"channel": channel_id}
        )
        return data.get("channel", {})
    
    async def find_channel_by_name(self, name: str) -> Optional[dict]:
        """Find a channel by name."""
        channels = await self.list_channels()
        name = name.lstrip("#").lower()
        
        for channel in channels:
            if channel.get("name", "").lower() == name:
                return channel
        
        return None
    
    # ==================== Messages ====================
    
    async def send_message(
        self,
        channel: str,
        text: str,
        blocks: Optional[List[dict]] = None,
        thread_ts: Optional[str] = None,
    ) -> dict:
        """Send a message to a channel."""
        payload = {
            "channel": channel,
            "text": text,
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        if thread_ts:
            payload["thread_ts"] = thread_ts
        
        data = await self._request("POST", "chat.postMessage", json=payload)
        return data
    
    async def update_message(
        self,
        channel: str,
        ts: str,
        text: str,
        blocks: Optional[List[dict]] = None,
    ) -> dict:
        """Update an existing message."""
        payload = {
            "channel": channel,
            "ts": ts,
            "text": text,
        }
        
        if blocks:
            payload["blocks"] = blocks
        
        data = await self._request("POST", "chat.update", json=payload)
        return data
    
    async def get_channel_history(
        self,
        channel: str,
        limit: int = 10,
        oldest: Optional[str] = None,
        latest: Optional[str] = None,
    ) -> List[dict]:
        """Get message history from a channel."""
        params = {
            "channel": channel,
            "limit": limit,
        }
        
        if oldest:
            params["oldest"] = oldest
        if latest:
            params["latest"] = latest
        
        data = await self._request("GET", "conversations.history", params=params)
        return data.get("messages", [])
    
    # ==================== Users ====================
    
    async def list_users(self) -> List[dict]:
        """List all users in the workspace."""
        data = await self._request("GET", "users.list")
        return data.get("members", [])
    
    async def get_user_info(self, user_id: str) -> dict:
        """Get info about a user."""
        data = await self._request(
            "GET",
            "users.info",
            params={"user": user_id}
        )
        return data.get("user", {})
    
    async def find_user_by_email(self, email: str) -> Optional[dict]:
        """Find a user by email."""
        try:
            data = await self._request(
                "GET",
                "users.lookupByEmail",
                params={"email": email}
            )
            return data.get("user")
        except Exception:
            return None
    
    # ==================== Direct Messages ====================
    
    async def open_dm(self, user_id: str) -> str:
        """Open a DM channel with a user and return channel ID."""
        data = await self._request(
            "POST",
            "conversations.open",
            json={"users": user_id}
        )
        return data.get("channel", {}).get("id")
    
    async def send_dm(self, user_id: str, text: str) -> dict:
        """Send a direct message to a user."""
        channel_id = await self.open_dm(user_id)
        return await self.send_message(channel_id, text)
    
    # ==================== Reactions ====================
    
    async def add_reaction(
        self,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> dict:
        """Add a reaction to a message."""
        data = await self._request(
            "POST",
            "reactions.add",
            json={
                "channel": channel,
                "timestamp": timestamp,
                "name": emoji.strip(":"),
            }
        )
        return data
    
    # ==================== Rich Messages ====================
    
    @staticmethod
    def create_blocks(
        text: str,
        header: Optional[str] = None,
        fields: Optional[List[tuple]] = None,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
    ) -> List[dict]:
        """Create Slack Block Kit blocks for rich formatting."""
        blocks = []
        
        if header:
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header,
                    "emoji": True
                }
            })
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": text
            }
        })
        
        if fields:
            field_blocks = []
            for label, value in fields:
                field_blocks.append({
                    "type": "mrkdwn",
                    "text": f"*{label}*\n{value}"
                })
            
            blocks.append({
                "type": "section",
                "fields": field_blocks
            })
        
        if button_text and button_url:
            blocks.append({
                "type": "actions",
                "elements": [{
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": button_text,
                        "emoji": True
                    },
                    "url": button_url,
                    "action_id": "button_click"
                }]
            })
        
        return blocks
