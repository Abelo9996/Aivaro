"""Mailchimp MCP Server — subscribers, campaigns, audiences."""
from app.mcp_servers.base import BaseMCPServer


class MailchimpMCPServer(BaseMCPServer):
    provider = "mailchimp"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.mailchimp_service import MailchimpService
        self.svc = MailchimpService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register(
            "mailchimp_add_subscriber",
            "Add a subscriber to a Mailchimp audience.",
            {
                "type": "object",
                "properties": {
                    "list_id": {"type": "string", "description": "Audience/list ID"},
                    "email": {"type": "string", "description": "Subscriber email"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "status": {"type": "string", "default": "subscribed", "description": "subscribed, unsubscribed, pending"},
                },
                "required": ["list_id", "email"],
            },
            self._add_subscriber,
        )
        self._register(
            "mailchimp_update_subscriber",
            "Update a subscriber's info.",
            {
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "email": {"type": "string"},
                    "first_name": {"type": "string"},
                    "last_name": {"type": "string"},
                    "status": {"type": "string"},
                },
                "required": ["list_id", "email"],
            },
            self._update_subscriber,
        )
        self._register(
            "mailchimp_add_tags",
            "Add tags to a subscriber.",
            {
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "email": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags to add"},
                },
                "required": ["list_id", "email", "tags"],
            },
            self._add_tags,
        )
        self._register(
            "mailchimp_send_campaign",
            "Create and send a Mailchimp email campaign.",
            {
                "type": "object",
                "properties": {
                    "list_id": {"type": "string", "description": "Audience to send to"},
                    "subject": {"type": "string"},
                    "from_name": {"type": "string"},
                    "from_email": {"type": "string"},
                    "html_content": {"type": "string", "description": "HTML email content"},
                },
                "required": ["list_id", "subject", "from_name", "from_email", "html_content"],
            },
            self._send_campaign,
        )
        self._register(
            "mailchimp_list_audiences",
            "List Mailchimp audiences/lists.",
            {"type": "object", "properties": {}},
            self._list_audiences,
        )
        self._register(
            "mailchimp_list_subscribers",
            "List subscribers in an audience.",
            {
                "type": "object",
                "properties": {
                    "list_id": {"type": "string"},
                    "count": {"type": "integer", "default": 100},
                    "status": {"type": "string", "description": "Filter by status"},
                },
                "required": ["list_id"],
            },
            self._list_subscribers,
        )
        self._register(
            "mailchimp_list_campaigns",
            "List Mailchimp campaigns.",
            {
                "type": "object",
                "properties": {
                    "count": {"type": "integer", "default": 20},
                    "status": {"type": "string", "description": "Filter by status (save, paused, schedule, sending, sent)"},
                },
            },
            self._list_campaigns,
        )

    async def _add_subscriber(self, list_id: str, email: str, first_name: str = "", last_name: str = "", status: str = "subscribed") -> dict:
        merge_fields = {}
        if first_name:
            merge_fields["FNAME"] = first_name
        if last_name:
            merge_fields["LNAME"] = last_name
        result = await self.svc.add_member(list_id, email, status=status, merge_fields=merge_fields)
        return {"subscriber_added": True, "email": email, "id": result.get("id")}

    async def _update_subscriber(self, list_id: str, email: str, first_name: str = None, last_name: str = None, status: str = None) -> dict:
        merge_fields = {}
        if first_name:
            merge_fields["FNAME"] = first_name
        if last_name:
            merge_fields["LNAME"] = last_name
        kwargs = {}
        if merge_fields:
            kwargs["merge_fields"] = merge_fields
        if status:
            kwargs["status"] = status
        result = await self.svc.update_member(list_id, email, **kwargs)
        return {"subscriber_updated": True, "email": email}

    async def _add_tags(self, list_id: str, email: str, tags: list) -> dict:
        await self.svc.add_tags_to_member(list_id, email, tags)
        return {"tags_added": True, "email": email, "tags": tags}

    async def _send_campaign(self, list_id: str, subject: str, from_name: str, from_email: str, html_content: str) -> dict:
        campaign = await self.svc.create_campaign(
            list_id=list_id,
            subject=subject,
            from_name=from_name,
            reply_to=from_email,
        )
        campaign_id = campaign.get("id")
        await self.svc.set_campaign_content(campaign_id, html=html_content)
        await self.svc.send_campaign(campaign_id)
        return {"campaign_sent": True, "campaign_id": campaign_id}

    async def _list_audiences(self) -> dict:
        audiences = await self.svc.list_audiences()
        lists = audiences.get("lists", [])
        return {"audiences": [{"id": a.get("id"), "name": a.get("name"), "member_count": a.get("stats", {}).get("member_count")} for a in lists], "count": len(lists)}

    async def _list_subscribers(self, list_id: str, count: int = 100, status: str = None) -> dict:
        members = await self.svc.list_members(list_id, count=count, status=status)
        member_list = members.get("members", [])
        return {"subscribers": [self.svc.format_member_for_display(m) for m in member_list], "count": len(member_list)}

    async def _list_campaigns(self, count: int = 20, status: str = None) -> dict:
        campaigns = await self.svc.list_campaigns(count=count, status=status)
        campaign_list = campaigns.get("campaigns", [])
        return {"campaigns": [{"id": c.get("id"), "title": c.get("settings", {}).get("title"), "status": c.get("status")} for c in campaign_list], "count": len(campaign_list)}

    async def close(self):
        await self.svc.close()
