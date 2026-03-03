"""
Brevo MCP Server - Email, SMS, WhatsApp, Contacts, Campaigns
API docs: https://developers.brevo.com/reference
Auth: API key via api-key header
"""
from typing import Any
from .base import BaseMCPServer


class BrevoMCPServer(BaseMCPServer):
    BASE_URL = "https://api.brevo.com/v3"

    def __init__(self, credentials: dict):
        super().__init__()
        self.api_key = credentials.get("api_key", "")

    @property
    def headers(self) -> dict:
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_tools(self) -> list[dict]:
        return [
            # ===== Transactional Email =====
            {
                "name": "brevo_send_transactional_email",
                "description": "Send a transactional email via Brevo",
                "parameters": {
                    "sender_email": "Sender email address",
                    "sender_name": "Sender name",
                    "to_email": "Recipient email address",
                    "to_name": "Recipient name (optional)",
                    "subject": "Email subject",
                    "html_content": "HTML body (optional)",
                    "text_content": "Plain text body (optional)",
                },
            },
            {
                "name": "brevo_list_transactional_emails",
                "description": "Get list of transactional emails with filters",
                "parameters": {
                    "email": "Filter by recipient email (optional)",
                    "limit": "Number of results (default 50, max 500)",
                    "offset": "Pagination offset (default 0)",
                },
            },
            # ===== SMS =====
            {
                "name": "brevo_send_sms",
                "description": "Send a transactional SMS via Brevo",
                "parameters": {
                    "sender": "Sender name (max 11 chars) or phone number",
                    "recipient": "Recipient phone number (with country code, e.g. +1234567890)",
                    "content": "SMS content",
                },
            },
            {
                "name": "brevo_list_sms_events",
                "description": "Get SMS activity events",
                "parameters": {
                    "limit": "Number of results (default 50)",
                    "phone_number": "Filter by phone number (optional)",
                },
            },
            # ===== WhatsApp =====
            {
                "name": "brevo_send_whatsapp",
                "description": "Send a WhatsApp message via Brevo",
                "parameters": {
                    "sender_number": "WhatsApp sender number",
                    "recipient_number": "Recipient WhatsApp number (with country code)",
                    "template_name": "Approved WhatsApp template name",
                    "template_language": "Template language (e.g. en)",
                },
            },
            # ===== Contacts =====
            {
                "name": "brevo_create_contact",
                "description": "Create a new contact in Brevo",
                "parameters": {
                    "email": "Contact email address",
                    "first_name": "First name (optional)",
                    "last_name": "Last name (optional)",
                    "phone": "Phone number (optional)",
                    "list_ids": "Comma-separated list IDs to add contact to (optional)",
                },
            },
            {
                "name": "brevo_update_contact",
                "description": "Update an existing contact in Brevo",
                "parameters": {
                    "email": "Contact email to update",
                    "first_name": "Updated first name (optional)",
                    "last_name": "Updated last name (optional)",
                    "phone": "Updated phone (optional)",
                    "list_ids": "Comma-separated list IDs (optional)",
                },
            },
            {
                "name": "brevo_get_contact",
                "description": "Get contact details by email",
                "parameters": {
                    "email": "Contact email address",
                },
            },
            {
                "name": "brevo_list_contacts",
                "description": "Get all contacts with pagination",
                "parameters": {
                    "limit": "Number of results (default 50, max 1000)",
                    "offset": "Pagination offset (default 0)",
                },
            },
            {
                "name": "brevo_delete_contact",
                "description": "Delete a contact by email",
                "parameters": {
                    "email": "Contact email to delete",
                },
            },
            # ===== Contact Lists =====
            {
                "name": "brevo_list_folders",
                "description": "Get all contact list folders",
                "parameters": {},
            },
            {
                "name": "brevo_list_lists",
                "description": "Get all contact lists",
                "parameters": {
                    "limit": "Number of results (default 50)",
                    "offset": "Pagination offset (default 0)",
                },
            },
            {
                "name": "brevo_create_list",
                "description": "Create a new contact list",
                "parameters": {
                    "name": "List name",
                    "folder_id": "Folder ID to put the list in",
                },
            },
            # ===== Email Campaigns =====
            {
                "name": "brevo_create_email_campaign",
                "description": "Create an email campaign in Brevo",
                "parameters": {
                    "name": "Campaign name",
                    "subject": "Email subject",
                    "sender_email": "Sender email",
                    "sender_name": "Sender name",
                    "html_content": "HTML body content",
                    "list_ids": "Comma-separated list IDs to send to",
                    "scheduled_at": "ISO datetime to schedule (optional, sends immediately if omitted)",
                },
            },
            {
                "name": "brevo_list_email_campaigns",
                "description": "Get all email campaigns",
                "parameters": {
                    "status": "Filter by status: draft, sent, queued, etc. (optional)",
                    "limit": "Number of results (default 50)",
                    "offset": "Pagination offset (default 0)",
                },
            },
            {
                "name": "brevo_send_campaign_now",
                "description": "Send an existing draft campaign immediately",
                "parameters": {
                    "campaign_id": "Campaign ID to send",
                },
            },
        ]

    async def call_tool(self, tool_name: str, params: dict) -> Any:
        method_map = {
            "brevo_send_transactional_email": self._send_email,
            "brevo_list_transactional_emails": self._list_emails,
            "brevo_send_sms": self._send_sms,
            "brevo_list_sms_events": self._list_sms_events,
            "brevo_send_whatsapp": self._send_whatsapp,
            "brevo_create_contact": self._create_contact,
            "brevo_update_contact": self._update_contact,
            "brevo_get_contact": self._get_contact,
            "brevo_list_contacts": self._list_contacts,
            "brevo_delete_contact": self._delete_contact,
            "brevo_list_folders": self._list_folders,
            "brevo_list_lists": self._list_lists,
            "brevo_create_list": self._create_list,
            "brevo_create_email_campaign": self._create_campaign,
            "brevo_list_email_campaigns": self._list_campaigns,
            "brevo_send_campaign_now": self._send_campaign,
        }
        handler = method_map.get(tool_name)
        if not handler:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await handler(params)

    async def _send_email(self, params: dict) -> dict:
        to = [{"email": params["to_email"]}]
        if params.get("to_name"):
            to[0]["name"] = params["to_name"]
        body = {
            "sender": {"email": params["sender_email"], "name": params.get("sender_name", params["sender_email"])},
            "to": to,
            "subject": params["subject"],
        }
        if params.get("html_content"):
            body["htmlContent"] = params["html_content"]
        if params.get("text_content"):
            body["textContent"] = params["text_content"]
        return await self._post("/smtp/email", json=body)

    async def _list_emails(self, params: dict) -> dict:
        query = {"limit": int(params.get("limit", 50)), "offset": int(params.get("offset", 0))}
        if params.get("email"):
            query["email"] = params["email"]
        return await self._get("/smtp/emails", params=query)

    async def _send_sms(self, params: dict) -> dict:
        return await self._post("/transactionalSMS/sms", json={
            "sender": params["sender"],
            "recipient": params["recipient"],
            "content": params["content"],
            "type": "transactional",
        })

    async def _list_sms_events(self, params: dict) -> dict:
        query = {"limit": int(params.get("limit", 50))}
        if params.get("phone_number"):
            query["phoneNumber"] = params["phone_number"]
        return await self._get("/transactionalSMS/statistics/events", params=query)

    async def _send_whatsapp(self, params: dict) -> dict:
        return await self._post("/whatsapp/sendMessage", json={
            "senderNumber": params["sender_number"],
            "recipientNumber": params["recipient_number"],
            "templateName": params["template_name"],
            "templateLanguage": params.get("template_language", "en"),
        })

    async def _create_contact(self, params: dict) -> dict:
        body: dict = {"email": params["email"], "attributes": {}}
        if params.get("first_name"):
            body["attributes"]["FIRSTNAME"] = params["first_name"]
        if params.get("last_name"):
            body["attributes"]["LASTNAME"] = params["last_name"]
        if params.get("phone"):
            body["attributes"]["SMS"] = params["phone"]
        if params.get("list_ids"):
            body["listIds"] = [int(x.strip()) for x in str(params["list_ids"]).split(",")]
        return await self._post("/contacts", json=body)

    async def _update_contact(self, params: dict) -> dict:
        email = params["email"]
        body: dict = {"attributes": {}}
        if params.get("first_name"):
            body["attributes"]["FIRSTNAME"] = params["first_name"]
        if params.get("last_name"):
            body["attributes"]["LASTNAME"] = params["last_name"]
        if params.get("phone"):
            body["attributes"]["SMS"] = params["phone"]
        if params.get("list_ids"):
            body["listIds"] = [int(x.strip()) for x in str(params["list_ids"]).split(",")]
        return await self._put(f"/contacts/{email}", json=body)

    async def _get_contact(self, params: dict) -> dict:
        return await self._get(f"/contacts/{params['email']}")

    async def _list_contacts(self, params: dict) -> dict:
        return await self._get("/contacts", params={
            "limit": int(params.get("limit", 50)),
            "offset": int(params.get("offset", 0)),
        })

    async def _delete_contact(self, params: dict) -> dict:
        return await self._delete(f"/contacts/{params['email']}")

    async def _list_folders(self, params: dict) -> dict:
        return await self._get("/contacts/folders", params={"limit": 50, "offset": 0})

    async def _list_lists(self, params: dict) -> dict:
        return await self._get("/contacts/lists", params={
            "limit": int(params.get("limit", 50)),
            "offset": int(params.get("offset", 0)),
        })

    async def _create_list(self, params: dict) -> dict:
        return await self._post("/contacts/lists", json={
            "name": params["name"],
            "folderId": int(params["folder_id"]),
        })

    async def _create_campaign(self, params: dict) -> dict:
        body = {
            "name": params["name"],
            "subject": params["subject"],
            "sender": {"email": params["sender_email"], "name": params.get("sender_name", params["sender_email"])},
            "htmlContent": params["html_content"],
            "recipients": {"listIds": [int(x.strip()) for x in str(params["list_ids"]).split(",")]},
        }
        if params.get("scheduled_at"):
            body["scheduledAt"] = params["scheduled_at"]
        return await self._post("/emailCampaigns", json=body)

    async def _list_campaigns(self, params: dict) -> dict:
        query = {"limit": int(params.get("limit", 50)), "offset": int(params.get("offset", 0))}
        if params.get("status"):
            query["status"] = params["status"]
        return await self._get("/emailCampaigns", params=query)

    async def _send_campaign(self, params: dict) -> dict:
        return await self._post(f"/emailCampaigns/{params['campaign_id']}/sendNow")

    # ===== HTTP helpers =====
    async def _get(self, path: str, params: dict = None) -> dict:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{self.BASE_URL}{path}", headers=self.headers, params=params)
            resp.raise_for_status()
            return resp.json() if resp.text else {"status": "ok"}

    async def _post(self, path: str, json: dict = None) -> dict:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.BASE_URL}{path}", headers=self.headers, json=json)
            resp.raise_for_status()
            return resp.json() if resp.text else {"status": "ok"}

    async def _put(self, path: str, json: dict = None) -> dict:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.put(f"{self.BASE_URL}{path}", headers=self.headers, json=json)
            resp.raise_for_status()
            return resp.json() if resp.text else {"status": "ok"}

    async def _delete(self, path: str) -> dict:
        import httpx
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.delete(f"{self.BASE_URL}{path}", headers=self.headers)
            resp.raise_for_status()
            return {"status": "deleted"}
