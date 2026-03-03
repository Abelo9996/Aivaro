"""Mailchimp MCP Server — audiences, subscribers, campaigns, tags."""
from app.mcp_servers.base import BaseMCPServer


class MailchimpMCPServer(BaseMCPServer):
    provider = "mailchimp"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.mailchimp_service import MailchimpService
        self.svc = MailchimpService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        self._register("mailchimp_add_subscriber", "Add or update a subscriber to a Mailchimp audience.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string", "description": "Audience/list ID"},
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "status": {"type": "string", "description": "subscribed, unsubscribed, pending, cleaned", "default": "subscribed"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["list_id", "email"],
        }, self._add_subscriber)

        self._register("mailchimp_update_subscriber", "Update an existing subscriber's info.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "status": {"type": "string"},
            },
            "required": ["list_id", "email"],
        }, self._update_subscriber)

        self._register("mailchimp_get_subscriber", "Get subscriber details by email.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["list_id", "email"],
        }, self._get_subscriber)

        self._register("mailchimp_archive_subscriber", "Archive (remove) a subscriber from an audience.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["list_id", "email"],
        }, self._archive_subscriber)

        self._register("mailchimp_add_tags", "Add tags to a subscriber.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "email": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["list_id", "email", "tags"],
        }, self._add_tags)

        self._register("mailchimp_remove_tags", "Remove tags from a subscriber.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "email": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["list_id", "email", "tags"],
        }, self._remove_tags)

        self._register("mailchimp_send_campaign", "Create and send an email campaign.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "subject": {"type": "string"},
                "from_name": {"type": "string"},
                "reply_to": {"type": "string"},
                "html_content": {"type": "string", "description": "HTML email body"},
            },
            "required": ["list_id", "subject", "from_name", "reply_to", "html_content"],
        }, self._send_campaign)

        self._register("mailchimp_create_campaign", "Create a campaign draft (without sending).", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "subject": {"type": "string"},
                "from_name": {"type": "string"},
                "reply_to": {"type": "string"},
            },
            "required": ["list_id", "subject", "from_name", "reply_to"],
        }, self._create_campaign)

        self._register("mailchimp_list_audiences", "List all Mailchimp audiences.", {
            "type": "object", "properties": {},
        }, self._list_audiences)

        self._register("mailchimp_list_subscribers", "List subscribers in an audience.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
                "status": {"type": "string", "description": "Filter: subscribed, unsubscribed, cleaned, pending"},
                "count": {"type": "integer", "default": 50},
            },
            "required": ["list_id"],
        }, self._list_subscribers)

        self._register("mailchimp_list_campaigns", "List email campaigns.", {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter: save, paused, schedule, sending, sent"},
                "count": {"type": "integer", "default": 20},
            },
        }, self._list_campaigns)

        self._register("mailchimp_get_campaign_report", "Get performance report for a campaign.", {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
            },
            "required": ["campaign_id"],
        }, self._get_campaign_report)

        self._register("mailchimp_list_tags", "List all tags for an audience.", {
            "type": "object",
            "properties": {
                "list_id": {"type": "string"},
            },
            "required": ["list_id"],
        }, self._list_tags)

        self._register("mailchimp_create_audience", "Create a new Mailchimp audience.", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Audience name"},
                "company": {"type": "string"},
                "from_name": {"type": "string"},
                "from_email": {"type": "string"},
                "permission_reminder": {"type": "string", "default": "You signed up on our website."},
            },
            "required": ["name", "from_name", "from_email"],
        }, self._create_audience)

    # ── Handlers ───────────────────────────────────────────────

    async def _add_subscriber(self, list_id: str, email: str, first_name: str = "",
                              last_name: str = "", status: str = "subscribed", tags: list = None) -> dict:
        merge_fields = {}
        if first_name: merge_fields["FNAME"] = first_name
        if last_name: merge_fields["LNAME"] = last_name
        result = await self.svc.add_or_update_member(list_id, email, status=status,
                                                      merge_fields=merge_fields, tags=tags)
        return result

    async def _update_subscriber(self, list_id: str, email: str, first_name: str = None,
                                 last_name: str = None, status: str = None) -> dict:
        merge_fields = {}
        if first_name: merge_fields["FNAME"] = first_name
        if last_name: merge_fields["LNAME"] = last_name
        result = await self.svc.update_member(list_id, email, status=status, merge_fields=merge_fields or None)
        return result

    async def _get_subscriber(self, list_id: str, email: str) -> dict:
        result = await self.svc.get_member(list_id, email)
        return {"subscriber": result}

    async def _archive_subscriber(self, list_id: str, email: str) -> dict:
        await self.svc.archive_member(list_id, email)
        return {"archived": True, "email": email}

    async def _add_tags(self, list_id: str, email: str, tags: list) -> dict:
        await self.svc.add_tags_to_member(list_id, email, tags)
        return {"tags_added": tags, "email": email}

    async def _remove_tags(self, list_id: str, email: str, tags: list) -> dict:
        await self.svc.remove_tags_from_member(list_id, email, tags)
        return {"tags_removed": tags, "email": email}

    async def _send_campaign(self, list_id: str, subject: str, from_name: str,
                             reply_to: str, html_content: str) -> dict:
        result = await self.svc.send_campaign(list_id, subject, from_name, reply_to, html_content)
        return result

    async def _create_campaign(self, list_id: str, subject: str, from_name: str, reply_to: str) -> dict:
        result = await self.svc.create_campaign(list_id, subject, from_name, reply_to)
        return result

    async def _list_audiences(self) -> dict:
        result = await self.svc.list_audiences()
        return {"audiences": result, "count": len(result)}

    async def _list_subscribers(self, list_id: str, status: str = None, count: int = 50) -> dict:
        result = await self.svc.list_members(list_id, status=status, count=count)
        return {"subscribers": result, "count": len(result)}

    async def _list_campaigns(self, status: str = None, count: int = 20) -> dict:
        result = await self.svc.list_campaigns(status=status, count=count)
        return {"campaigns": result, "count": len(result)}

    async def _get_campaign_report(self, campaign_id: str) -> dict:
        result = await self.svc.get_campaign(campaign_id)
        return {"report": result}

    async def _list_tags(self, list_id: str) -> dict:
        result = await self.svc.list_tags(list_id)
        return {"tags": result, "count": len(result)}

    async def _create_audience(self, name: str, from_name: str, from_email: str,
                               company: str = "", permission_reminder: str = "You signed up on our website.") -> dict:
        result = await self.svc.create_audience(name=name, from_name=from_name, from_email=from_email,
                                                 company=company, permission_reminder=permission_reminder)
        return result

    async def close(self):
        await self.svc.close()
