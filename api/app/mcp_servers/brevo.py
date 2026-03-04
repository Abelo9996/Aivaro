"""
Brevo MCP Server - Email, SMS, WhatsApp, Contacts, Campaigns
API docs: https://developers.brevo.com/reference
Auth: API key via api-key header
"""
from typing import Any
from .base import BaseMCPServer


class BrevoMCPServer(BaseMCPServer):
    provider = "brevo"
    BASE_URL = "https://api.brevo.com/v3"

    def __init__(self, credentials: dict):
        super().__init__()
        raw_key = credentials.get("api_key") or credentials.get("access_token") or ""
        self.api_key = raw_key.strip()
        print(f"[Brevo.__init__] cred_keys={list(credentials.keys())} api_key_len={len(self.api_key)} prefix={self.api_key[:12] if self.api_key else 'EMPTY'}")
        if not self.api_key:
            import logging
            logging.getLogger(__name__).warning(
                f"[Brevo] No api_key found in credentials. Keys present: {list(credentials.keys())}"
            )

        # ===== Transactional Email =====
        self._register("brevo_send_transactional_email", "Send a transactional email via Brevo", {
            "type": "object",
            "properties": {
                "sender_email": {"type": "string", "description": "Sender email address"},
                "sender_name": {"type": "string", "description": "Sender name"},
                "to_email": {"type": "string", "description": "Recipient email address"},
                "to_name": {"type": "string", "description": "Recipient name (optional)"},
                "subject": {"type": "string", "description": "Email subject"},
                "html_content": {"type": "string", "description": "HTML body (optional)"},
                "text_content": {"type": "string", "description": "Plain text body (optional)"},
            },
            "required": ["sender_email", "to_email", "subject"],
        }, self._send_email)

        self._register("brevo_list_transactional_emails", "Get list of transactional emails with filters", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Filter by recipient email (optional)"},
                "limit": {"type": "integer", "description": "Number of results (default 50, max 500)"},
                "offset": {"type": "integer", "description": "Pagination offset (default 0)"},
            },
        }, self._list_emails)

        # ===== SMS =====
        self._register("brevo_send_sms", "Send a transactional SMS via Brevo", {
            "type": "object",
            "properties": {
                "sender": {"type": "string", "description": "Sender name (max 11 chars) or phone number"},
                "recipient": {"type": "string", "description": "Recipient phone number (with country code)"},
                "content": {"type": "string", "description": "SMS content"},
            },
            "required": ["sender", "recipient", "content"],
        }, self._send_sms)

        self._register("brevo_list_sms_events", "Get SMS activity events", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of results (default 50)"},
                "phone_number": {"type": "string", "description": "Filter by phone number (optional)"},
            },
        }, self._list_sms_events)

        # ===== WhatsApp =====
        self._register("brevo_send_whatsapp", "Send a WhatsApp message via Brevo", {
            "type": "object",
            "properties": {
                "sender_number": {"type": "string", "description": "WhatsApp sender number"},
                "recipient_number": {"type": "string", "description": "Recipient WhatsApp number (with country code)"},
                "template_name": {"type": "string", "description": "Approved WhatsApp template name"},
                "template_language": {"type": "string", "description": "Template language (e.g. en)"},
            },
            "required": ["sender_number", "recipient_number", "template_name"],
        }, self._send_whatsapp)

        # ===== Contacts =====
        self._register("brevo_create_contact", "Create a new contact in Brevo", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Contact email address"},
                "first_name": {"type": "string", "description": "First name (optional)"},
                "last_name": {"type": "string", "description": "Last name (optional)"},
                "phone": {"type": "string", "description": "Phone number (optional)"},
                "list_ids": {"type": "string", "description": "Comma-separated list IDs to add contact to (optional)"},
            },
            "required": ["email"],
        }, self._create_contact)

        self._register("brevo_update_contact", "Update an existing contact in Brevo", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Contact email to update"},
                "first_name": {"type": "string", "description": "Updated first name (optional)"},
                "last_name": {"type": "string", "description": "Updated last name (optional)"},
                "phone": {"type": "string", "description": "Updated phone (optional)"},
                "list_ids": {"type": "string", "description": "Comma-separated list IDs (optional)"},
            },
            "required": ["email"],
        }, self._update_contact)

        self._register("brevo_get_contact", "Get contact details by email", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Contact email address"},
            },
            "required": ["email"],
        }, self._get_contact)

        self._register("brevo_list_contacts", "Get all contacts with pagination", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of results (default 50, max 1000)"},
                "offset": {"type": "integer", "description": "Pagination offset (default 0)"},
            },
        }, self._list_contacts)

        self._register("brevo_delete_contact", "Delete a contact by email", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Contact email to delete"},
            },
            "required": ["email"],
        }, self._delete_contact)

        # ===== Contact Lists =====
        self._register("brevo_list_folders", "Get all contact list folders", {
            "type": "object", "properties": {},
        }, self._list_folders)

        self._register("brevo_list_lists", "Get all contact lists", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Number of results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset (default 0)"},
            },
        }, self._list_lists)

        self._register("brevo_create_list", "Create a new contact list", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "List name"},
                "folder_id": {"type": "string", "description": "Folder ID to put the list in"},
            },
            "required": ["name", "folder_id"],
        }, self._create_list)

        # ===== Email Campaigns =====
        self._register("brevo_create_email_campaign", "Create an email campaign in Brevo", {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Campaign name"},
                "subject": {"type": "string", "description": "Email subject"},
                "sender_email": {"type": "string", "description": "Sender email"},
                "sender_name": {"type": "string", "description": "Sender name"},
                "html_content": {"type": "string", "description": "HTML body content"},
                "list_ids": {"type": "string", "description": "Comma-separated list IDs to send to"},
                "scheduled_at": {"type": "string", "description": "ISO datetime to schedule (optional)"},
            },
            "required": ["name", "subject", "sender_email", "html_content", "list_ids"],
        }, self._create_campaign)

        self._register("brevo_list_email_campaigns", "Get all email campaigns", {
            "type": "object",
            "properties": {
                "status": {"type": "string", "description": "Filter by status: draft, sent, queued, etc. (optional)"},
                "limit": {"type": "integer", "description": "Number of results (default 50)"},
                "offset": {"type": "integer", "description": "Pagination offset (default 0)"},
            },
        }, self._list_campaigns)

        self._register("brevo_send_campaign_now", "Send an existing draft campaign immediately", {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID to send"},
            },
            "required": ["campaign_id"],
        }, self._send_campaign)

    @property
    def headers(self) -> dict:
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    # ===== Handlers =====
    async def _send_email(self, **params) -> dict:
        import logging
        logging.getLogger(__name__).info(
            f"[Brevo] Sending email, api_key length={len(self.api_key)}, "
            f"prefix={self.api_key[:12] if self.api_key else 'EMPTY'}..."
        )
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

    async def _list_emails(self, **params) -> dict:
        query = {"limit": int(params.get("limit", 50)), "offset": int(params.get("offset", 0))}
        if params.get("email"):
            query["email"] = params["email"]
        return await self._get("/smtp/emails", params=query)

    async def _send_sms(self, **params) -> dict:
        return await self._post("/transactionalSMS/sms", json={
            "sender": params["sender"],
            "recipient": params["recipient"],
            "content": params["content"],
            "type": "transactional",
        })

    async def _list_sms_events(self, **params) -> dict:
        query = {"limit": int(params.get("limit", 50))}
        if params.get("phone_number"):
            query["phoneNumber"] = params["phone_number"]
        return await self._get("/transactionalSMS/statistics/events", params=query)

    async def _send_whatsapp(self, **params) -> dict:
        return await self._post("/whatsapp/sendMessage", json={
            "senderNumber": params["sender_number"],
            "recipientNumber": params["recipient_number"],
            "templateName": params["template_name"],
            "templateLanguage": params.get("template_language", "en"),
        })

    async def _create_contact(self, **params) -> dict:
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

    async def _update_contact(self, **params) -> dict:
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

    async def _get_contact(self, **params) -> dict:
        return await self._get(f"/contacts/{params['email']}")

    async def _list_contacts(self, **params) -> dict:
        return await self._get("/contacts", params={
            "limit": int(params.get("limit", 50)),
            "offset": int(params.get("offset", 0)),
        })

    async def _delete_contact(self, **params) -> dict:
        return await self._delete(f"/contacts/{params['email']}")

    async def _list_folders(self, **params) -> dict:
        return await self._get("/contacts/folders", params={"limit": 50, "offset": 0})

    async def _list_lists(self, **params) -> dict:
        return await self._get("/contacts/lists", params={
            "limit": int(params.get("limit", 50)),
            "offset": int(params.get("offset", 0)),
        })

    async def _create_list(self, **params) -> dict:
        return await self._post("/contacts/lists", json={
            "name": params["name"],
            "folderId": int(params["folder_id"]),
        })

    async def _create_campaign(self, **params) -> dict:
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

    async def _list_campaigns(self, **params) -> dict:
        query = {"limit": int(params.get("limit", 50)), "offset": int(params.get("offset", 0))}
        if params.get("status"):
            query["status"] = params["status"]
        return await self._get("/emailCampaigns", params=query)

    async def _send_campaign(self, **params) -> dict:
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
            print(f"[Brevo._post] url={self.BASE_URL}{path} api_key_len={len(self.api_key)} key_repr_start={repr(self.api_key[:20])} key_repr_end={repr(self.api_key[-10:])}")
            resp = await client.post(f"{self.BASE_URL}{path}", headers=self.headers, json=json)
            if resp.status_code == 401:
                print(f"[Brevo._post] 401 response body: {resp.text[:500]}")
                print(f"[Brevo._post] Request headers sent: api-key length={len(self.headers.get('api-key',''))}")
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

