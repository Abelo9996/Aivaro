"""
Node Executor - Executes individual workflow nodes using real integrations.
"""
from typing import Any, Optional
from datetime import datetime, timedelta
import asyncio
import json

from app.utils.timezone import now_local, parse_datetime, format_iso, get_default_timezone


class NodeExecutor:
    """Executes workflow nodes with real or mock integrations."""
    
    def __init__(self, connections: Optional[dict] = None):
        """
        Initialize with user's connections.
        connections should be a dict like:
        {
            "google": {"access_token": "...", "refresh_token": "..."},
            "slack": {"access_token": "..."},
        }
        """
        self.connections = connections or {}
        self._google_service = None
        self._slack_service = None
    
    async def get_google_service(self):
        """Get or create Google service instance."""
        if self._google_service is None and "google" in self.connections:
            from app.services.integrations.google_service import GoogleService
            creds = self.connections["google"]
            self._google_service = GoogleService(
                access_token=creds.get("access_token"),
                refresh_token=creds.get("refresh_token"),
            )
        return self._google_service
    
    async def get_slack_service(self):
        """Get or create Slack service instance."""
        if self._slack_service is None and "slack" in self.connections:
            from app.services.integrations.slack_service import SlackService
            creds = self.connections["slack"]
            self._slack_service = SlackService(
                access_token=creds.get("access_token"),
            )
        return self._slack_service
    
    async def get_stripe_service(self):
        """Get or create Stripe service instance."""
        if not hasattr(self, '_stripe_service'):
            self._stripe_service = None
        if self._stripe_service is None and "stripe" in self.connections:
            from app.services.integrations.stripe_service import StripeService
            creds = self.connections["stripe"]
            # Stripe uses API key authentication
            api_key = creds.get("api_key") or creds.get("access_token")
            if api_key:
                self._stripe_service = StripeService(api_key=api_key)
        return self._stripe_service
    
    async def get_notion_service(self):
        """Get or create Notion service instance."""
        if not hasattr(self, '_notion_service'):
            self._notion_service = None
        if self._notion_service is None and "notion" in self.connections:
            from app.services.integrations.notion_service import NotionService
            creds = self.connections["notion"]
            access_token = creds.get("access_token")
            if access_token:
                self._notion_service = NotionService(access_token=access_token)
        return self._notion_service
    
    async def get_airtable_service(self):
        """Get or create Airtable service instance."""
        if not hasattr(self, '_airtable_service'):
            self._airtable_service = None
        if self._airtable_service is None and "airtable" in self.connections:
            from app.services.integrations.airtable_service import AirtableService
            creds = self.connections["airtable"]
            access_token = creds.get("access_token")
            if access_token:
                self._airtable_service = AirtableService(access_token=access_token)
        return self._airtable_service
    
    async def get_calendly_service(self):
        """Get or create Calendly service instance."""
        if not hasattr(self, '_calendly_service'):
            self._calendly_service = None
        if self._calendly_service is None and "calendly" in self.connections:
            from app.services.integrations.calendly_service import CalendlyService
            creds = self.connections["calendly"]
            access_token = creds.get("access_token")
            if access_token:
                self._calendly_service = CalendlyService(access_token=access_token)
        return self._calendly_service
    
    async def get_mailchimp_service(self):
        """Get or create Mailchimp service instance."""
        if not hasattr(self, '_mailchimp_service'):
            self._mailchimp_service = None
        if self._mailchimp_service is None and "mailchimp" in self.connections:
            from app.services.integrations.mailchimp_service import MailchimpService
            creds = self.connections["mailchimp"]
            access_token = creds.get("access_token")
            server_prefix = creds.get("server_prefix", "us1")
            if access_token:
                self._mailchimp_service = MailchimpService(
                    access_token=access_token,
                    server_prefix=server_prefix,
                )
        return self._mailchimp_service
    
    async def get_twilio_service(self):
        """Get or create Twilio service instance."""
        if not hasattr(self, '_twilio_service'):
            self._twilio_service = None
        if self._twilio_service is None and "twilio" in self.connections:
            from app.services.integrations.twilio_service import TwilioService
            creds = self.connections["twilio"]
            account_sid = creds.get("account_sid")
            auth_token = creds.get("auth_token")
            phone_number = creds.get("phone_number")
            if account_sid and auth_token:
                self._twilio_service = TwilioService(
                    account_sid=account_sid,
                    auth_token=auth_token,
                    default_from=phone_number,
                )
        return self._twilio_service
    
    async def close(self):
        """Close all service connections."""
        if self._google_service:
            await self._google_service.close()
        if self._slack_service:
            await self._slack_service.close()
        if hasattr(self, '_stripe_service') and self._stripe_service:
            await self._stripe_service.close()
        if hasattr(self, '_notion_service') and self._notion_service:
            await self._notion_service.close()
        if hasattr(self, '_airtable_service') and self._airtable_service:
            await self._airtable_service.close()
        if hasattr(self, '_calendly_service') and self._calendly_service:
            await self._calendly_service.close()
        if hasattr(self, '_mailchimp_service') and self._mailchimp_service:
            await self._mailchimp_service.close()
        if hasattr(self, '_twilio_service') and self._twilio_service:
            await self._twilio_service.close()
    
    async def execute(
        self,
        node_type: str,
        parameters: dict[str, Any],
        input_data: dict[str, Any],
        is_test: bool = False
    ) -> dict[str, Any]:
        """Execute a single node and return results."""
        executors = {
            "start_manual": self._execute_start,
            "start_form": self._execute_start,
            "start_webhook": self._execute_start,
            "start_schedule": self._execute_start,
            "start_email": self._execute_start,
            "send_email": self._execute_send_email,
            "ai_reply": self._execute_ai_reply,
            "ai_summarize": self._execute_ai_summarize,
            "ai_extract": self._execute_ai_extract,
            "append_row": self._execute_append_row,
            "read_sheet": self._execute_read_sheet,
            "delay": self._execute_delay,
            "send_notification": self._execute_notification,
            "send_slack": self._execute_send_slack,
            "http_request": self._execute_http_request,
            "condition": self._execute_condition,
            "transform": self._execute_transform,
            # Google Calendar
            "google_calendar_create": self._execute_google_calendar_create,
            "google_calendar_list": self._execute_google_calendar_list,
            # Google Gmail read
            "gmail_list_messages": self._execute_gmail_list_messages,
            "gmail_get_message": self._execute_gmail_get_message,
            # Stripe integrations
            "stripe_create_invoice": self._execute_stripe_create_invoice,
            "stripe_send_invoice": self._execute_stripe_send_invoice,
            "stripe_create_payment_link": self._execute_stripe_create_payment_link,
            "stripe_get_customer": self._execute_stripe_get_customer,
            "stripe_check_payment": self._execute_stripe_check_payment,
            # Notion integrations
            "notion_create_page": self._execute_notion_create_page,
            "notion_update_page": self._execute_notion_update_page,
            "notion_query_database": self._execute_notion_query_database,
            "notion_search": self._execute_notion_search,
            # Airtable integrations
            "airtable_create_record": self._execute_airtable_create_record,
            "airtable_update_record": self._execute_airtable_update_record,
            "airtable_list_records": self._execute_airtable_list_records,
            "airtable_find_record": self._execute_airtable_find_record,
            # Calendly integrations
            "calendly_list_events": self._execute_calendly_list_events,
            "calendly_get_event": self._execute_calendly_get_event,
            "calendly_cancel_event": self._execute_calendly_cancel_event,
            "calendly_create_link": self._execute_calendly_create_link,
            # Mailchimp integrations
            "mailchimp_add_subscriber": self._execute_mailchimp_add_subscriber,
            "mailchimp_update_subscriber": self._execute_mailchimp_update_subscriber,
            "mailchimp_add_tags": self._execute_mailchimp_add_tags,
            "mailchimp_send_campaign": self._execute_mailchimp_send_campaign,
            # Twilio integrations
            "twilio_send_sms": self._execute_twilio_send_sms,
            "twilio_send_whatsapp": self._execute_twilio_send_whatsapp,
            "twilio_make_call": self._execute_twilio_make_call,
            # Standalone approval gate
            "approval": self._execute_approval_gate,
        }
        
        executor = executors.get(node_type, self._execute_default)
        return await executor(parameters, input_data, is_test)
    
    async def _execute_start(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Start node just passes through data."""
        return {
            "success": True,
            "output": input_data,
            "logs": f"[{datetime.utcnow().isoformat()}] Workflow started\n"
        }
    
    async def _execute_send_email(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send email via Gmail API or SMTP."""
        to = params.get("to", input_data.get("email", ""))
        subject = params.get("subject", "No subject")
        body = params.get("body", "")
        
        # Interpolate variables
        subject = _interpolate(subject, input_data)
        body = _interpolate(body, input_data)
        to = _interpolate(to, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending email\n"
        logs += f"  To: {to}\n"
        logs += f"  Subject: {subject}\n"
        
        if is_test:
            logs += "  Email NOT sent (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "email_sent": False, "email_to": to, "email_subject": subject},
                "logs": logs
            }
        
        # Try Gmail API first
        google = await self.get_google_service()
        if google:
            try:
                result = await google.send_email(to, subject, body)
                logs += f"  ✅ Email sent via Gmail (ID: {result.get('id', 'unknown')})\n"
                return {
                    "success": True,
                    "output": {**input_data, "email_sent": True, "email_to": to, "email_subject": subject, "message_id": result.get("id")},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ⚠️ Gmail failed: {str(e)}\n"
        
        # Fallback to SMTP if configured
        from app.services.integrations.email_service import EmailService
        email_service = EmailService()
        if email_service.is_configured:
            try:
                email_service.send_email(to, subject, body)
                logs += "  ✅ Email sent via SMTP\n"
                return {
                    "success": True,
                    "output": {**input_data, "email_sent": True, "email_to": to, "email_subject": subject},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ⚠️ SMTP failed: {str(e)}\n"
        
        # Mock mode - no real email provider
        logs += "  ⚠️ No email provider configured - email simulated\n"
        return {
            "success": True,
            "output": {**input_data, "email_sent": True, "email_to": to, "email_subject": subject, "simulated": True},
            "logs": logs
        }
    
    async def _execute_ai_reply(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Generate an AI-powered reply to an email."""
        from app.config import get_settings
        settings = get_settings()
        
        tone = params.get("tone", "professional")
        context = params.get("context", "Reply helpfully to this email")
        
        # Get email content from input data
        email_from = input_data.get("from", "Unknown sender")
        email_subject = input_data.get("subject", "No subject")
        email_snippet = input_data.get("snippet", "")
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Generating AI reply\n"
        logs += f"  Original email from: {email_from}\n"
        logs += f"  Subject: {email_subject}\n"
        logs += f"  Tone: {tone}\n"
        
        if is_test:
            ai_response = f"[TEST MODE] This would be an AI-generated {tone} reply to the email about '{email_subject}'."
            logs += "  AI response NOT generated (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "ai_response": ai_response},
                "logs": logs
            }
        
        # Generate AI response using OpenAI
        if settings.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=settings.openai_api_key)
                
                # Build knowledge context
                knowledge_ctx = input_data.get("__knowledge_context", "")
                knowledge_section = ""
                if knowledge_ctx:
                    knowledge_section = f"\n\nIMPORTANT BUSINESS CONTEXT (use this to personalize your reply):\n{knowledge_ctx}"
                
                system_prompt = f"""You are an email assistant for a business owner. Generate a {tone} reply to the following email.
Keep the response concise, helpful, and appropriate for the context: {context}
Do not include a subject line, just the email body.
Sign off appropriately but don't include the sender's name (it will be added automatically).{knowledge_section}"""
                
                user_prompt = f"""Email from: {email_from}
Subject: {email_subject}
Content: {email_snippet}

Generate a {tone} reply:"""
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                ai_response = response.choices[0].message.content.strip()
                logs += f"  ✅ AI response generated ({len(ai_response)} chars)\n"
                
                return {
                    "success": True,
                    "output": {**input_data, "ai_response": ai_response},
                    "logs": logs
                }
                
            except Exception as e:
                logs += f"  ❌ AI generation failed: {str(e)}\n"
                ai_response = f"Thank you for your email regarding '{email_subject}'. I'll get back to you shortly."
        else:
            logs += "  ⚠️ OpenAI not configured - using default response\n"
            ai_response = f"Thank you for your email regarding '{email_subject}'. I've received your message and will respond soon."
        
        return {
            "success": True,
            "output": {**input_data, "ai_response": ai_response},
            "logs": logs
        }
    
    async def _execute_ai_summarize(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Use AI to summarize or analyze data."""
        from app.config import get_settings
        settings = get_settings()
        
        source = params.get("source", "the provided data")
        format_type = params.get("format", "paragraph")
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Generating AI summary\n"
        logs += f"  Source: {source}\n"
        logs += f"  Format: {format_type}\n"
        
        if is_test:
            summary = f"[TEST MODE] This would be an AI-generated summary of {source}."
            return {
                "success": True,
                "output": {**input_data, "summary": summary},
                "logs": logs
            }
        
        if settings.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=settings.openai_api_key)
                
                format_instruction = "bullet points" if format_type == "bullet_points" else "a concise paragraph"
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": f"Summarize the following data in {format_instruction}. Be concise and highlight key points."},
                        {"role": "user", "content": f"Data to summarize:\n{json.dumps(input_data, indent=2, default=str)}"}
                    ],
                    temperature=0.5,
                    max_tokens=500
                )
                
                summary = response.choices[0].message.content.strip()
                logs += f"  ✅ Summary generated\n"
                
                return {
                    "success": True,
                    "output": {**input_data, "summary": summary},
                    "logs": logs
                }
                
            except Exception as e:
                logs += f"  ❌ AI summarization failed: {str(e)}\n"
        
        logs += "  ⚠️ Using fallback summary\n"
        return {
            "success": True,
            "output": {**input_data, "summary": f"Summary of {source}: Data processed successfully."},
            "logs": logs
        }

    async def _execute_ai_extract(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Use AI to extract structured data from text (e.g., email body)."""
        from app.config import get_settings
        settings = get_settings()
        
        fields_to_extract = params.get("fields", "name, email, date, time")
        context = params.get("context", "Extract the requested fields from the text.")
        
        # Get the text to extract from - could be email snippet, body, or other text
        text_content = input_data.get("snippet", "") or input_data.get("body", "") or input_data.get("text", "")
        subject = input_data.get("subject", "")
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Extracting data with AI\n"
        logs += f"  Fields: {fields_to_extract}\n"
        logs += f"  Text length: {len(text_content)} chars\n"
        
        if is_test:
            # Generate mock extracted data for test mode
            mock_data = {}
            for field in fields_to_extract.split(","):
                field = field.strip()
                if "date" in field.lower():
                    mock_data[field] = "2026-02-15"
                elif "time" in field.lower():
                    mock_data[field] = "10:00"
                elif "email" in field.lower():
                    mock_data[field] = "customer@example.com"
                elif "name" in field.lower():
                    mock_data[field] = "John Doe"
                elif "phone" in field.lower():
                    mock_data[field] = "(555) 123-4567"
                else:
                    mock_data[field] = f"[extracted_{field}]"
            
            logs += f"  [TEST MODE] Mock extracted data: {mock_data}\n"
            return {
                "success": True,
                "output": {**input_data, **mock_data},
                "logs": logs
            }
        
        if settings.openai_api_key:
            try:
                import openai
                client = openai.OpenAI(api_key=settings.openai_api_key)
                
                system_prompt = f"""You are a data extraction assistant. Extract the following fields from the provided text:
{fields_to_extract}

Instructions: {context}

Return your response as a valid JSON object with the field names as keys. 
For dates, use YYYY-MM-DD format. For times, use HH:MM format (24-hour).
IMPORTANT: If no timezone is mentioned, assume Pacific Time (America/Los_Angeles).
If a field cannot be found, use null or a reasonable default.
Return ONLY the JSON object, no explanation."""

                user_prompt = f"""Subject: {subject}

Content:
{text_content}

Extract: {fields_to_extract}"""

                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )
                
                extracted_text = response.choices[0].message.content.strip()
                
                # Parse JSON response
                # Handle markdown code blocks if present
                if extracted_text.startswith("```"):
                    extracted_text = extracted_text.split("```")[1]
                    if extracted_text.startswith("json"):
                        extracted_text = extracted_text[4:]
                
                extracted_data = json.loads(extracted_text.strip())
                
                logs += f"  ✅ Data extracted: {list(extracted_data.keys())}\n"
                
                return {
                    "success": True,
                    "output": {**input_data, **extracted_data},
                    "logs": logs
                }
                
            except json.JSONDecodeError as e:
                logs += f"  ❌ Failed to parse AI response as JSON: {str(e)}\n"
                logs += f"  Raw response: {extracted_text[:200]}\n"
            except Exception as e:
                logs += f"  ❌ AI extraction failed: {str(e)}\n"
        else:
            logs += "  ⚠️ OpenAI not configured\n"
        
        # Fallback - return empty extracted fields
        logs += "  ⚠️ Using fallback extraction (empty values)\n"
        fallback_data = {}
        for field in fields_to_extract.split(","):
            field = field.strip()
            fallback_data[field] = ""
        
        return {
            "success": True,
            "output": {**input_data, **fallback_data},
            "logs": logs
        }

    async def _execute_append_row(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Append row to Google Sheets, matching the sheet's column schema."""
        spreadsheet = params.get("spreadsheet", "Untitled Spreadsheet")
        spreadsheet_id = params.get("spreadsheet_id")
        sheet_name = params.get("sheet_name", "Sheet1")
        columns = params.get("columns", [])
        use_schema = params.get("use_schema", True)  # Default to schema-aware appending
        
        # Build row data dict for schema-aware appending
        row_data_dict = {}
        row_data_list = []
        
        if columns and len(columns) > 0:
            # Use explicitly specified columns
            for col in columns:
                col_name = col.get("name", col.get("header", f"Column{len(row_data_list)+1}"))
                value = _interpolate(str(col.get("value", "")), input_data)
                row_data_dict[col_name] = value
                row_data_list.append(value)
        else:
            # Auto-build data dict from input_data for schema matching
            # Use multiple key variations so the schema matcher can find them
            # The key names should match common spreadsheet column headers
            
            # Get values with fallbacks
            customer_name = input_data.get("customer_name") or input_data.get("name") or ""
            customer_email = input_data.get("customer_email") or input_data.get("email") or ""
            pickup_date = input_data.get("pickup_date") or input_data.get("date") or input_data.get("today") or ""
            pickup_time = input_data.get("pickup_time") or input_data.get("time") or ""
            customer_phone = input_data.get("customer_phone") or input_data.get("phone") or ""
            pickup_type = input_data.get("pickup_type") or input_data.get("service") or input_data.get("service_type") or ""
            status = input_data.get("status") or "Pending"
            payment_url = input_data.get("payment_url") or input_data.get("payment_link_url") or input_data.get("payment_link") or ""
            notes = input_data.get("notes") or input_data.get("description") or ""
            amount = input_data.get("amount") or input_data.get("price") or ""
            
            # Include all variations of key names for maximum compatibility
            row_data_dict = {
                # Exact match keys (for headers like "Customer Name", "Pickup Date")
                "customer_name": customer_name,
                "customer_email": customer_email,
                "pickup_date": pickup_date,
                "pickup_time": pickup_time,
                "customer_phone": customer_phone,
                "pickup_type": pickup_type,
                "status": status,
                "payment_url": payment_url,
                # Alternate key names
                "name": customer_name,
                "email": customer_email,
                "date": pickup_date,
                "time": pickup_time,
                "phone": customer_phone,
                "service": pickup_type,
                "payment_link_url": payment_url,
                "payment_link": payment_url,
                "link": payment_url,
                "notes": notes,
                "amount": amount,
                "today": input_data.get("today", ""),
            }
            
            # Also include all raw input_data for any custom columns
            for k, v in input_data.items():
                if isinstance(v, (str, int, float, bool)) and k not in row_data_dict:
                    row_data_dict[k] = str(v) if v else ""
            
            # Build fallback list (for non-schema mode)
            auto_fields = [pickup_date, pickup_time, customer_name, customer_email, customer_phone, pickup_type, status, payment_url, notes]
            row_data_list = [v for v in auto_fields if v]
            
            if not row_data_list:
                row_data_list = [
                    datetime.utcnow().strftime("%Y-%m-%d %H:%M"),
                    input_data.get("name", ""),
                    input_data.get("email", ""),
                    "Auto-logged"
                ]
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Adding row to spreadsheet\n"
        logs += f"  Spreadsheet: {spreadsheet}\n"
        logs += f"  Sheet: {sheet_name}\n"
        logs += f"  Use schema matching: {use_schema}\n"
        logs += f"  Data keys: {[k for k in row_data_dict.keys() if row_data_dict[k]]}\n"
        
        if is_test:
            logs += "  Row NOT added (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "row_added": False, "spreadsheet": spreadsheet, "row_data": row_data_list},
                "logs": logs
            }
        
        google = await self.get_google_service()
        if google:
            try:
                # Find or create spreadsheet by name
                if not spreadsheet_id:
                    spreadsheet_id = await google.find_or_create_spreadsheet(spreadsheet)
                    logs += f"  Found/created spreadsheet ID: {spreadsheet_id}\n"
                
                # Use schema-aware appending (matches column headers)
                if use_schema:
                    logs += "  Using schema-aware append (matching column headers)\n"
                    result = await google.append_row_with_schema(spreadsheet_id, row_data_dict, sheet_name)
                else:
                    result = await google.append_row(spreadsheet_id, row_data_list, sheet_name)
                
                logs += f"  ✅ Row added successfully\n"
                return {
                    "success": True,
                    "output": {**input_data, "row_added": True, "spreadsheet": spreadsheet, "spreadsheet_id": spreadsheet_id, "row_data": row_data_dict if use_schema else row_data_list},
                    "logs": logs
                }
            except Exception as e:
                logs += f"  ❌ Failed: {str(e)}\n"
                return {
                    "success": False,
                    "output": input_data,
                    "logs": logs,
                    "error": str(e)
                }
        
        # No Google connection - simulate
        logs += "  ⚠️ Google Sheets not connected - row simulated\n"
        return {
            "success": True,
            "output": {**input_data, "row_added": True, "spreadsheet": spreadsheet, "row_data": row_data_dict if use_schema else row_data_list, "simulated": True},
            "logs": logs
        }

    async def _execute_read_sheet(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Read data from Google Sheets."""
        spreadsheet_id = params.get("spreadsheet_id")
        spreadsheet_name = params.get("spreadsheet") or params.get("spreadsheet_name")
        range_name = params.get("range", "Sheet1!A1:Z1000")  # Increased default range
        
        logs = f"[{datetime.utcnow().isoformat()}] Reading from spreadsheet\n"
        logs += f"  Spreadsheet ID/Name: {spreadsheet_id or spreadsheet_name}\n"
        logs += f"  Range: {range_name}\n"
        
        if is_test:
            logs += "  Sheet NOT read (test mode) - returning mock data\n"
            mock_data = [
                ["Header1", "Header2", "Header3"],
                ["Row1Val1", "Row1Val2", "Row1Val3"],
                ["Row2Val1", "Row2Val2", "Row2Val3"],
            ]
            return {
                "success": True,
                "output": {
                    **input_data, 
                    "sheet_data": mock_data, 
                    "row_count": len(mock_data),
                    "_spreadsheet_snapshot": {
                        "name": spreadsheet_name or spreadsheet_id,
                        "data": mock_data,
                        "headers": mock_data[0] if mock_data else [],
                        "row_count": len(mock_data),
                        "read_at": datetime.utcnow().isoformat()
                    }
                },
                "logs": logs
            }
        
        google = await self.get_google_service()
        if not google:
            logs += "  ❌ Google Sheets not connected - please connect Google in Settings\n"
            return {"success": False, "output": input_data, "logs": logs, "error": "Google Sheets not connected"}
        
        # Detect if spreadsheet_id is actually a name (not a real Google Sheets ID).
        # Real IDs are ~44 chars of alphanumeric, hyphens, underscores. Names have spaces, dots, or are short.
        import re
        _looks_like_id = spreadsheet_id and len(spreadsheet_id) >= 25 and bool(re.match(r'^[a-zA-Z0-9_-]+$', spreadsheet_id))
        
        if spreadsheet_id and not _looks_like_id:
            # This is likely a name, not an ID - try to find it
            logs += f"  Looking up spreadsheet by name: '{spreadsheet_id}'\n"
            try:
                found_id = await google.find_spreadsheet_by_name(spreadsheet_id)
                if found_id:
                    logs += f"  Found spreadsheet ID: {found_id}\n"
                    spreadsheet_id = found_id
                else:
                    logs += f"  ❌ Could not find spreadsheet named '{spreadsheet_id}'. Please provide the actual Google Sheets ID from the URL.\n"
                    return {"success": False, "output": input_data, "logs": logs, "error": f"Spreadsheet '{spreadsheet_id}' not found. Use the spreadsheet ID from the URL instead."}
            except Exception as e:
                logs += f"  ❌ Error looking up spreadsheet: {str(e)}\n"
        
        # If no spreadsheet_id but we have a name, try to find by name
        if not spreadsheet_id and spreadsheet_name:
            logs += f"  Looking up spreadsheet by name: '{spreadsheet_name}'\n"
            try:
                found_id = await google.find_spreadsheet_by_name(spreadsheet_name)
                if found_id:
                    logs += f"  Found spreadsheet ID: {found_id}\n"
                    spreadsheet_id = found_id
                else:
                    logs += f"  ❌ Could not find spreadsheet named '{spreadsheet_name}'.\n"
            except Exception as e:
                logs += f"  ❌ Error looking up spreadsheet: {str(e)}\n"
        
        if not spreadsheet_id:
            logs += "  ❌ No spreadsheet ID provided\n"
            return {"success": False, "output": input_data, "logs": logs, "error": "No spreadsheet ID provided"}
        
        try:
            values = await google.get_sheet_values(spreadsheet_id, range_name)
            logs += f"  ✅ Read {len(values)} rows\n"
            
            # Store full spreadsheet snapshot for chat context
            headers = values[0] if values else []
            spreadsheet_snapshot = {
                "spreadsheet_id": spreadsheet_id,
                "name": spreadsheet_name or spreadsheet_id,
                "data": values,
                "headers": headers,
                "row_count": len(values),
                "column_count": len(headers),
                "read_at": datetime.utcnow().isoformat()
            }
            
            return {
                "success": True,
                "output": {
                    **input_data, 
                    "sheet_data": values, 
                    "row_count": len(values),
                    "_spreadsheet_snapshot": spreadsheet_snapshot
                },
                "logs": logs
            }
        except Exception as e:
            error_msg = str(e)
            logs += f"  ❌ Failed: {error_msg}\n"
            
            # Add helpful tips
            if "404" in error_msg or "not found" in error_msg.lower():
                logs += "  💡 Tip: Make sure to use the actual Spreadsheet ID from the URL (the long string after /d/)\n"
                logs += "     Example URL: https://docs.google.com/spreadsheets/d/1BxiMVs0XRA.../edit\n"
                logs += "     The ID would be: 1BxiMVs0XRA...\n"
            
            return {"success": False, "output": input_data, "logs": logs, "error": error_msg}
    
    async def _execute_send_slack(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send message to Slack."""
        channel = params.get("channel", "#general")
        message = params.get("message", "")
        
        message = _interpolate(message, input_data)
        channel = _interpolate(channel, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending Slack message\n"
        logs += f"  Channel: {channel}\n"
        logs += f"  Message: {message[:100]}{'...' if len(message) > 100 else ''}\n"
        
        if is_test:
            logs += "  Message NOT sent (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "slack_sent": False, "channel": channel},
                "logs": logs
            }
        
        slack = await self.get_slack_service()
        if slack:
            try:
                # Find channel by name
                channel_info = await slack.find_channel_by_name(channel)
                channel_id = channel_info["id"] if channel_info else channel
                
                result = await slack.send_message(channel_id, message)
                logs += f"  ✅ Message sent (ts: {result.get('ts', 'unknown')})\n"
                return {
                    "success": True,
                    "output": {**input_data, "slack_sent": True, "channel": channel, "message_ts": result.get("ts")},
                    "logs": logs
                }
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"[Slack] Failed to send message to {channel}: {e}")
                logs += f"  ❌ Failed: {str(e)}\n"
                return {"success": False, "output": input_data, "logs": logs, "error": str(e)}
        
        logs += "  ⚠️ Slack not connected - message simulated\n"
        return {
            "success": True,
            "output": {**input_data, "slack_sent": True, "channel": channel, "simulated": True},
            "logs": logs
        }
    
    async def _execute_delay(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Wait for a specified duration."""
        duration = params.get("duration", 60)
        unit = params.get("unit", "seconds")
        
        # Convert to seconds
        multipliers = {"seconds": 1, "minutes": 60, "hours": 3600, "days": 86400}
        seconds = duration * multipliers.get(unit, 1)
        
        logs = f"[{datetime.utcnow().isoformat()}] Delay step\n"
        logs += f"  Duration: {duration} {unit}\n"
        
        if is_test or seconds > 300:  # Skip delays > 5 mins in any case
            logs += f"  Skipped delay ({'test mode' if is_test else 'too long'})\n"
        else:
            logs += f"  Waiting {seconds} seconds...\n"
            await asyncio.sleep(seconds)
            logs += f"  Done waiting\n"
        
        return {"success": True, "output": input_data, "logs": logs}
    
    async def _execute_notification(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send a notification (internal)."""
        message = params.get("message", "Notification")
        message = _interpolate(message, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Notification\n"
        logs += f"  Message: {message}\n"
        logs += "  ✅ Notification logged\n"
        
        return {
            "success": True,
            "output": {**input_data, "notification_sent": True, "notification_message": message},
            "logs": logs
        }
    
    async def _execute_http_request(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Make an HTTP request."""
        import httpx
        
        method = params.get("method", "GET").upper()
        url = params.get("url", "")
        headers = params.get("headers", {})
        body = params.get("body")
        
        url = _interpolate(url, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}HTTP Request\n"
        logs += f"  Method: {method}\n"
        logs += f"  URL: {url}\n"
        
        if is_test:
            logs += "  Request NOT made (test mode)\n"
            return {"success": True, "output": input_data, "logs": logs}
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(method, url, headers=headers, json=body if body else None)
                logs += f"  Status: {response.status_code}\n"
                
                try:
                    response_data = response.json()
                except:
                    response_data = response.text
                
                return {
                    "success": response.status_code < 400,
                    "output": {**input_data, "http_response": response_data, "http_status": response.status_code},
                    "logs": logs
                }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "output": input_data, "logs": logs, "error": str(e)}
    
    async def _execute_condition(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Evaluate a condition."""
        field = params.get("field", "")
        operator = params.get("operator", "equals")
        value = params.get("value", "")
        
        field_value = input_data.get(field, "")
        value = _interpolate(str(value), input_data)
        
        result = False
        if operator == "equals":
            result = str(field_value) == str(value)
        elif operator == "not_equals":
            result = str(field_value) != str(value)
        elif operator == "contains":
            result = str(value) in str(field_value)
        elif operator == "greater_than":
            result = float(field_value) > float(value)
        elif operator == "less_than":
            result = float(field_value) < float(value)
        elif operator == "is_empty":
            result = not field_value
        elif operator == "is_not_empty":
            result = bool(field_value)
        
        logs = f"[{datetime.utcnow().isoformat()}] Condition check\n"
        logs += f"  {field} {operator} {value}\n"
        logs += f"  Result: {result}\n"
        
        return {
            "success": True,
            "output": {**input_data, "condition_result": result},
            "logs": logs,
            "branch": "true" if result else "false"
        }
    
    async def _execute_transform(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Transform data."""
        transforms = params.get("transforms", [])
        output = dict(input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Transforming data\n"
        
        for t in transforms:
            target = t.get("target")
            source = t.get("source")
            operation = t.get("operation", "copy")
            
            if source and target:
                value = input_data.get(source, "")
                
                if operation == "copy":
                    output[target] = value
                elif operation == "uppercase":
                    output[target] = str(value).upper()
                elif operation == "lowercase":
                    output[target] = str(value).lower()
                elif operation == "trim":
                    output[target] = str(value).strip()
                elif operation == "template":
                    template = t.get("template", "")
                    output[target] = _interpolate(template, input_data)
                
                logs += f"  {target} = {output[target]}\n"
        
        return {"success": True, "output": output, "logs": logs}
    
    # ==================== STRIPE EXECUTORS ====================
    
    async def _execute_stripe_get_customer(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Get or create a Stripe customer."""
        email = _interpolate(params.get("email", input_data.get("email", "")), input_data)
        name = _interpolate(params.get("name", input_data.get("name", "")), input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Getting/creating Stripe customer\n"
        logs += f"  Email: {email}\n"
        
        if is_test:
            # Simulate in test mode
            logs += f"  [TEST MODE] Would look up or create customer for: {email}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "customer_id": "cus_test123",
                    "customer_email": email,
                    "customer_created": False
                },
                "logs": logs
            }
        
        stripe_service = await self.get_stripe_service()
        if not stripe_service:
            return {
                "success": False,
                "error": "Stripe not connected. Please connect your Stripe account.",
                "output": input_data,
                "logs": logs + "  ERROR: No Stripe connection found\n"
            }
        
        result = await stripe_service.get_or_create_customer(email=email, name=name)
        
        if result["success"]:
            logs += f"  Customer ID: {result['customer_id']}\n"
            logs += f"  Created new: {result['created']}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "customer_id": result["customer_id"],
                    "customer_email": email,
                    "customer_created": result["created"]
                },
                "logs": logs
            }
        else:
            logs += f"  ERROR: {result['error']}\n"
            return {
                "success": False,
                "error": result["error"],
                "output": input_data,
                "logs": logs
            }
    
    async def _execute_stripe_create_invoice(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create and optionally send a Stripe invoice."""
        customer_id = _interpolate(params.get("customer_id", input_data.get("customer_id", "")), input_data)
        customer_email = _interpolate(params.get("customer_email", input_data.get("email", "")), input_data)
        
        # Get items from params or create from amount
        items = params.get("items", [])
        if not items:
            # Create single item from amount parameter
            amount = params.get("amount", input_data.get("amount", 0))
            if isinstance(amount, str):
                amount = float(amount.replace("$", "").replace(",", ""))
            amount_cents = int(float(amount) * 100)  # Convert to cents
            
            items = [{
                "description": _interpolate(params.get("description", "Invoice"), input_data),
                "amount": amount_cents,
                "quantity": 1
            }]
        else:
            # Process items with interpolation
            items = [
                {
                    "description": _interpolate(item.get("description", "Item"), input_data),
                    "amount": int(float(item.get("amount", 0)) * 100) if isinstance(item.get("amount"), (int, float, str)) else 0,
                    "quantity": item.get("quantity", 1)
                }
                for item in items
            ]
        
        description = _interpolate(params.get("memo", params.get("description", "")), input_data)
        due_days = params.get("due_days", 30)
        auto_send = params.get("auto_send", True)
        
        logs = f"[{datetime.utcnow().isoformat()}] Creating Stripe invoice\n"
        logs += f"  Customer: {customer_id or customer_email}\n"
        logs += f"  Items: {len(items)}\n"
        logs += f"  Auto-send: {auto_send}\n"
        
        if is_test:
            total_amount = sum(item.get("amount", 0) for item in items)
            logs += f"  [TEST MODE] Would create invoice for ${total_amount/100:.2f}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "invoice_id": "inv_test123",
                    "invoice_url": "https://invoice.stripe.com/test/inv_test123",
                    "invoice_amount": total_amount,
                    "invoice_status": "sent" if auto_send else "draft"
                },
                "logs": logs
            }
        
        stripe_service = await self.get_stripe_service()
        if not stripe_service:
            return {
                "success": False,
                "error": "Stripe not connected. Please connect your Stripe account.",
                "output": input_data,
                "logs": logs + "  ERROR: No Stripe connection found\n"
            }
        
        # If no customer_id, try to get/create by email
        if not customer_id and customer_email:
            customer_result = await stripe_service.get_or_create_customer(email=customer_email)
            if customer_result["success"]:
                customer_id = customer_result["customer_id"]
            else:
                return {
                    "success": False,
                    "error": f"Failed to find/create customer: {customer_result['error']}",
                    "output": input_data,
                    "logs": logs + f"  ERROR: {customer_result['error']}\n"
                }
        
        result = await stripe_service.create_invoice(
            customer_id=customer_id,
            items=items,
            description=description,
            due_days=due_days,
            auto_send=auto_send
        )
        
        if result["success"]:
            logs += f"  Invoice ID: {result['invoice_id']}\n"
            logs += f"  Invoice URL: {result['invoice_url']}\n"
            logs += f"  Status: {result['status']}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "invoice_id": result["invoice_id"],
                    "invoice_url": result["invoice_url"],
                    "invoice_pdf": result.get("invoice_pdf"),
                    "invoice_amount": result["amount_due"],
                    "invoice_status": result["status"]
                },
                "logs": logs
            }
        else:
            logs += f"  ERROR: {result['error']}\n"
            return {
                "success": False,
                "error": result["error"],
                "output": input_data,
                "logs": logs
            }
    
    async def _execute_stripe_send_invoice(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send an existing Stripe invoice."""
        invoice_id = _interpolate(params.get("invoice_id", input_data.get("invoice_id", "")), input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Sending Stripe invoice\n"
        logs += f"  Invoice ID: {invoice_id}\n"
        
        if not invoice_id:
            return {
                "success": False,
                "error": "No invoice_id provided",
                "output": input_data,
                "logs": logs + "  ERROR: Missing invoice_id\n"
            }
        
        if is_test:
            logs += f"  [TEST MODE] Would send invoice: {invoice_id}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "invoice_sent": True,
                    "invoice_status": "sent"
                },
                "logs": logs
            }
        
        stripe_service = await self.get_stripe_service()
        if not stripe_service:
            return {
                "success": False,
                "error": "Stripe not connected. Please connect your Stripe account.",
                "output": input_data,
                "logs": logs + "  ERROR: No Stripe connection found\n"
            }
        
        result = await stripe_service.send_invoice(invoice_id)
        
        if result["success"]:
            logs += f"  Sent successfully\n"
            logs += f"  Status: {result['status']}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "invoice_sent": True,
                    "invoice_status": result["status"],
                    "invoice_url": result["invoice_url"]
                },
                "logs": logs
            }
        else:
            logs += f"  ERROR: {result['error']}\n"
            return {
                "success": False,
                "error": result["error"],
                "output": input_data,
                "logs": logs
            }
    
    async def _execute_stripe_create_payment_link(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create a Stripe payment link."""
        # Get items from params or create from amount
        items = params.get("items", [])
        if not items:
            # Create single item from amount parameter
            amount = params.get("amount", input_data.get("amount", 0))
            if isinstance(amount, str):
                amount = float(amount.replace("$", "").replace(",", ""))
            amount_cents = int(float(amount) * 100)  # Convert to cents
            
            items = [{
                "name": _interpolate(params.get("product_name", params.get("description", "Payment")), input_data),
                "amount": amount_cents,
                "quantity": 1
            }]
        else:
            # Process items with interpolation
            items = [
                {
                    "name": _interpolate(item.get("name", item.get("description", "Item")), input_data),
                    "amount": int(float(item.get("amount", 0)) * 100) if isinstance(item.get("amount"), (int, float, str)) else 0,
                    "quantity": item.get("quantity", 1)
                }
                for item in items
            ]
        
        message = _interpolate(params.get("success_message", "Thank you for your payment!"), input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Creating Stripe payment link\n"
        logs += f"  Items: {len(items)}\n"
        
        if is_test:
            total_amount = sum(item.get("amount", 0) for item in items)
            logs += f"  [TEST MODE] Would create payment link for ${total_amount/100:.2f}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "payment_link_url": "https://buy.stripe.com/test_123",
                    "payment_link_id": "plink_test123",
                    "payment_amount": total_amount
                },
                "logs": logs
            }
        
        stripe_service = await self.get_stripe_service()
        if not stripe_service:
            return {
                "success": False,
                "error": "Stripe not connected. Please connect your Stripe account.",
                "output": input_data,
                "logs": logs + "  ERROR: No Stripe connection found\n"
            }
        
        result = await stripe_service.create_payment_link(
            items=items,
            after_completion_message=message
        )
        
        if result["success"]:
            logs += f"  Payment Link: {result['url']}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "payment_link_url": result["url"],
                    "payment_link_id": result["payment_link_id"]
                },
                "logs": logs
            }
        else:
            logs += f"  ERROR: {result['error']}\n"
            return {
                "success": False,
                "error": result["error"],
                "output": input_data,
                "logs": logs
            }
    
    async def _execute_stripe_check_payment(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Check if a payment has been made (for deposit verification)."""
        payment_link_id = _interpolate(params.get("payment_link_id", input_data.get("payment_link_id", "")), input_data)
        customer_email = _interpolate(params.get("customer_email", input_data.get("email", "")), input_data)
        invoice_id = _interpolate(params.get("invoice_id", input_data.get("invoice_id", "")), input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Checking payment status\n"
        
        if is_test:
            logs += f"  [TEST MODE] Would check payment for: {payment_link_id or invoice_id or customer_email}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "payment_status": "paid",
                    "deposit_paid": True,
                    "amount_paid": 2000  # $20.00 in cents
                },
                "logs": logs
            }
        
        stripe_service = await self.get_stripe_service()
        if not stripe_service:
            return {
                "success": False,
                "error": "Stripe not connected. Please connect your Stripe account.",
                "output": input_data,
                "logs": logs + "  ERROR: No Stripe connection found\n"
            }
        
        # Check invoice if we have an invoice_id
        if invoice_id:
            logs += f"  Checking invoice: {invoice_id}\n"
            result = await stripe_service.get_invoice(invoice_id)
            if result["success"]:
                is_paid = result.get("paid", False)
                logs += f"  Invoice status: {result['status']}\n"
                logs += f"  Paid: {is_paid}\n"
                return {
                    "success": True,
                    "output": {
                        **input_data,
                        "payment_status": result["status"],
                        "deposit_paid": is_paid,
                        "amount_paid": result.get("amount_paid", 0),
                        "amount_due": result.get("amount_due", 0)
                    },
                    "logs": logs
                }
        
        # Otherwise, check recent payments for customer
        if customer_email:
            logs += f"  Checking payments for customer: {customer_email}\n"
            # Get customer by email, then check their invoices
            customer_result = await stripe_service.get_or_create_customer(email=customer_email)
            if customer_result["success"]:
                customer_id = customer_result["customer_id"]
                invoices = await stripe_service.list_invoices(customer_id=customer_id, status="paid", limit=5)
                if invoices.get("success") and invoices.get("count", 0) > 0:
                    latest = invoices["invoices"][0]
                    logs += f"  Found {invoices['count']} paid invoices\n"
                    return {
                        "success": True,
                        "output": {
                            **input_data,
                            "payment_status": "paid",
                            "deposit_paid": True,
                            "amount_paid": latest.get("amount_paid", 0)
                        },
                        "logs": logs
                    }
        
        logs += f"  No paid invoices found\n"
        return {
            "success": True,
            "output": {
                **input_data,
                "payment_status": "unpaid",
                "deposit_paid": False,
                "amount_paid": 0
            },
            "logs": logs
        }
    
    # ==================== GOOGLE CALENDAR EXECUTORS ====================
    
    async def _execute_google_calendar_create(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create a Google Calendar event."""
        title = _interpolate(params.get("title", "New Event"), input_data)
        date = _interpolate(params.get("date", ""), input_data)
        start_time = _interpolate(params.get("start_time", "10:00"), input_data)
        duration = params.get("duration", 1)  # hours
        description = _interpolate(params.get("description", ""), input_data)
        location = _interpolate(params.get("location", ""), input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] Creating calendar event\n"
        logs += f"  Title: {title}\n"
        logs += f"  Date: {date}\n"
        logs += f"  Time: {start_time}\n"
        logs += f"  Duration: {duration}h\n"
        
        # Build datetime strings with timezone awareness (Pacific Time default)
        tz = get_default_timezone()
        try:
            if date and start_time:
                # Parse date and time - assume Pacific Time if no timezone specified
                try:
                    # Try parsing with our timezone-aware parser
                    start_dt = parse_datetime(date, start_time)
                except:
                    # Fallback to basic parsing
                    start_dt = datetime.fromisoformat(f"{date}T{start_time}:00")
                    # Add Pacific timezone if naive
                    if start_dt.tzinfo is None:
                        try:
                            import pytz
                            start_dt = tz.localize(start_dt)
                        except:
                            pass
                
                end_dt = start_dt + timedelta(hours=float(duration))
                start_iso = start_dt.isoformat()
                end_iso = end_dt.isoformat()
                logs += f"  Timezone: Pacific Time (America/Los_Angeles)\n"
            else:
                # Default to tomorrow at the specified time in Pacific
                local_now = now_local()
                tomorrow = local_now + timedelta(days=1)
                start_dt = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
                end_dt = start_dt + timedelta(hours=float(duration))
                start_iso = start_dt.isoformat()
                end_iso = end_dt.isoformat()
                logs += f"  Using default: tomorrow at 10:00 AM Pacific\n"
        except Exception as e:
            logs += f"  Warning: Could not parse date/time, using defaults: {e}\n"
            local_now = now_local()
            start_dt = local_now + timedelta(days=1)
            start_dt = start_dt.replace(hour=10, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(hours=1)
            start_iso = start_dt.isoformat()
            end_iso = end_dt.isoformat()
        
        if is_test:
            logs += f"  [TEST MODE] Would create calendar event: {title}\n"
            logs += f"  Start: {start_iso}\n"
            logs += f"  End: {end_iso}\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "calendar_event_id": "event_test123",
                    "calendar_event_url": "https://calendar.google.com/event?eid=test123",
                    "event_title": title,
                    "event_start": start_iso,
                    "event_end": end_iso
                },
                "logs": logs
            }
        
        google = await self.get_google_service()
        if not google:
            logs += "  ⚠️ Google Calendar not connected - event simulated\n"
            return {
                "success": True,
                "output": {
                    **input_data,
                    "calendar_event_id": "simulated_event",
                    "event_title": title,
                    "event_start": start_iso,
                    "event_end": end_iso,
                    "simulated": True
                },
                "logs": logs
            }
        
        try:
            result = await google.create_event(
                summary=title,
                start_time=start_iso,
                end_time=end_iso,
                description=description
            )
            
            event_id = result.get("id", "")
            event_link = result.get("htmlLink", "")
            
            logs += f"  ✅ Event created\n"
            logs += f"  Event ID: {event_id}\n"
            logs += f"  Link: {event_link}\n"
            
            return {
                "success": True,
                "output": {
                    **input_data,
                    "calendar_event_id": event_id,
                    "calendar_event_url": event_link,
                    "event_title": title,
                    "event_start": start_iso,
                    "event_end": end_iso
                },
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed to create event: {str(e)}\n"
            return {
                "success": False,
                "error": str(e),
                "output": input_data,
                "logs": logs
            }

    # ==================== GOOGLE CALENDAR LIST ====================

    async def _execute_google_calendar_list(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """List upcoming Google Calendar events."""
        time_min = params.get("time_min", "")
        time_max = params.get("time_max", "")
        max_results = params.get("max_results", 20)
        calendar_id = params.get("calendar_id", "primary")

        logs = f"[{datetime.utcnow().isoformat()}] Listing calendar events\n"
        logs += f"  Calendar: {calendar_id}\n"
        if time_min: logs += f"  From: {time_min}\n"
        if time_max: logs += f"  Until: {time_max}\n"

        if is_test:
            logs += "  [TEST] Returning mock events\n"
            mock_events = [
                {"id": "evt1", "summary": "Team Meeting", "start": "2026-02-27T10:00:00", "end": "2026-02-27T11:00:00", "attendees": ["alice@example.com"]},
                {"id": "evt2", "summary": "Client Call - John", "start": "2026-02-27T14:00:00", "end": "2026-02-27T15:00:00", "attendees": ["john@example.com"]},
            ]
            return {
                "success": True,
                "output": {**input_data, "calendar_events": mock_events, "event_count": len(mock_events)},
                "logs": logs,
            }

        google = await self.get_google_service()
        if not google:
            logs += "  Google not connected\n"
            return {"success": False, "output": input_data, "logs": logs, "error": "Google not connected"}

        try:
            events = await google.list_events(
                calendar_id=calendar_id,
                time_min=time_min or None,
                time_max=time_max or None,
                max_results=max_results,
            )
            simplified = []
            for e in events:
                start = e.get("start", {})
                end = e.get("end", {})
                simplified.append({
                    "id": e.get("id"),
                    "summary": e.get("summary", "(No title)"),
                    "start": start.get("dateTime", start.get("date", "")),
                    "end": end.get("dateTime", end.get("date", "")),
                    "location": e.get("location", ""),
                    "attendees": [a.get("email", "") for a in e.get("attendees", [])],
                    "status": e.get("status", ""),
                })
            logs += f"  Found {len(simplified)} events\n"
            return {
                "success": True,
                "output": {**input_data, "calendar_events": simplified, "event_count": len(simplified)},
                "logs": logs,
            }
        except Exception as e:
            logs += f"  Error: {str(e)}\n"
            return {"success": False, "output": input_data, "logs": logs, "error": str(e)}

    # ==================== GMAIL READ ====================

    async def _execute_gmail_list_messages(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """List recent Gmail messages."""
        query = params.get("query", "")
        max_results = params.get("max_results", 10)

        logs = f"[{datetime.utcnow().isoformat()}] Listing Gmail messages\n"
        if query: logs += f"  Query: {query}\n"
        logs += f"  Max results: {max_results}\n"

        if is_test:
            logs += "  [TEST] Returning mock messages\n"
            mock = [
                {"id": "msg1", "from": "john@example.com", "subject": "Re: Appointment", "snippet": "Yes I can make it at 2pm", "date": "2026-02-26T10:00:00"},
                {"id": "msg2", "from": "jane@example.com", "subject": "Invoice question", "snippet": "Can you send me the invoice again?", "date": "2026-02-26T09:00:00"},
            ]
            return {
                "success": True,
                "output": {**input_data, "emails": mock, "email_count": len(mock)},
                "logs": logs,
            }

        google = await self.get_google_service()
        if not google:
            logs += "  Google not connected\n"
            return {"success": False, "output": input_data, "logs": logs, "error": "Google not connected"}

        try:
            messages = await google.list_messages(query=query, max_results=max_results)
            logs += f"  Found {len(messages)} messages\n"
            return {
                "success": True,
                "output": {**input_data, "emails": messages, "email_count": len(messages)},
                "logs": logs,
            }
        except Exception as e:
            logs += f"  Error: {str(e)}\n"
            return {"success": False, "output": input_data, "logs": logs, "error": str(e)}

    async def _execute_gmail_get_message(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Get a specific Gmail message by ID."""
        message_id = params.get("message_id", "")

        logs = f"[{datetime.utcnow().isoformat()}] Getting Gmail message {message_id}\n"

        if is_test:
            logs += "  [TEST] Returning mock message\n"
            return {
                "success": True,
                "output": {**input_data, "email": {"id": message_id, "from": "test@example.com", "subject": "Test", "body": "Test email body", "date": "2026-02-26T10:00:00"}},
                "logs": logs,
            }

        google = await self.get_google_service()
        if not google:
            return {"success": False, "output": input_data, "logs": logs + "  Google not connected\n", "error": "Google not connected"}

        try:
            message = await google.get_message(message_id)
            return {
                "success": True,
                "output": {**input_data, "email": message},
                "logs": logs + "  Message retrieved\n",
            }
        except Exception as e:
            return {"success": False, "output": input_data, "logs": logs + f"  Error: {str(e)}\n", "error": str(e)}

    # ========== Notion Node Executors ==========
    
    async def _execute_notion_create_page(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create a new page in a Notion database."""
        database_id = params.get("database_id", "")
        properties = params.get("properties", {})
        content = params.get("content", "")
        
        # Interpolate variables
        database_id = _interpolate(database_id, input_data)
        for key, value in properties.items():
            if isinstance(value, str):
                properties[key] = _interpolate(value, input_data)
        content = _interpolate(content, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Creating Notion page\n"
        logs += f"  Database: {database_id}\n"
        logs += f"  Properties: {list(properties.keys())}\n"
        
        if is_test:
            logs += "  Page NOT created (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "notion_page_id": "test-page-id", "notion_created": False},
                "logs": logs
            }
        
        notion = await self.get_notion_service()
        if not notion:
            logs += "  ⚠️ Notion not connected\n"
            return {
                "success": False,
                "error": "Notion not connected",
                "output": input_data,
                "logs": logs
            }
        
        try:
            # Build Notion properties format
            notion_properties = {}
            for key, value in properties.items():
                # Auto-detect property type based on value
                if isinstance(value, bool):
                    notion_properties[key] = notion.create_checkbox_property(value)
                elif isinstance(value, (int, float)):
                    notion_properties[key] = notion.create_number_property(value)
                elif key.lower() == "title" or key.lower() == "name":
                    notion_properties[key] = notion.create_title_property(str(value))
                else:
                    notion_properties[key] = notion.create_rich_text_property(str(value))
            
            # Create children blocks if content is provided
            children = None
            if content:
                children = [notion.create_paragraph_block(content)]
            
            result = await notion.create_page(database_id, notion_properties, children)
            page_id = result.get("id", "")
            page_url = result.get("url", "")
            
            logs += f"  ✅ Page created (ID: {page_id})\n"
            return {
                "success": True,
                "output": {**input_data, "notion_page_id": page_id, "notion_page_url": page_url, "notion_created": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_notion_update_page(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Update properties of a Notion page."""
        page_id = params.get("page_id", input_data.get("notion_page_id", ""))
        properties = params.get("properties", {})
        
        page_id = _interpolate(page_id, input_data)
        for key, value in properties.items():
            if isinstance(value, str):
                properties[key] = _interpolate(value, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Updating Notion page\n"
        logs += f"  Page ID: {page_id}\n"
        
        if is_test:
            logs += "  Page NOT updated (test mode)\n"
            return {"success": True, "output": {**input_data, "notion_updated": False}, "logs": logs}
        
        notion = await self.get_notion_service()
        if not notion:
            logs += "  ⚠️ Notion not connected\n"
            return {"success": False, "error": "Notion not connected", "output": input_data, "logs": logs}
        
        try:
            # Build Notion properties format
            notion_properties = {}
            for key, value in properties.items():
                if isinstance(value, bool):
                    notion_properties[key] = notion.create_checkbox_property(value)
                elif isinstance(value, (int, float)):
                    notion_properties[key] = notion.create_number_property(value)
                else:
                    notion_properties[key] = notion.create_rich_text_property(str(value))
            
            result = await notion.update_page(page_id, notion_properties)
            logs += f"  ✅ Page updated\n"
            return {"success": True, "output": {**input_data, "notion_updated": True}, "logs": logs}
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_notion_query_database(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Query records from a Notion database."""
        database_id = params.get("database_id", "")
        filter_json = params.get("filter", None)
        page_size = params.get("page_size", 100)
        
        database_id = _interpolate(database_id, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Querying Notion database\n"
        logs += f"  Database: {database_id}\n"
        
        if is_test:
            logs += "  Database NOT queried (test mode)\n"
            return {"success": True, "output": {**input_data, "notion_results": [], "notion_count": 0}, "logs": logs}
        
        notion = await self.get_notion_service()
        if not notion:
            logs += "  ⚠️ Notion not connected\n"
            return {"success": False, "error": "Notion not connected", "output": input_data, "logs": logs}
        
        try:
            result = await notion.query_database(database_id, filter=filter_json, page_size=page_size)
            results = result.get("results", [])
            count = len(results)
            logs += f"  ✅ Retrieved {count} records\n"
            return {
                "success": True,
                "output": {**input_data, "notion_results": results, "notion_count": count},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_notion_search(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Search across Notion pages and databases."""
        query = params.get("query", "")
        filter_type = params.get("filter_type", None)  # "page" or "database"
        
        query = _interpolate(query, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Searching Notion\n"
        logs += f"  Query: {query}\n"
        
        if is_test:
            logs += "  Search NOT performed (test mode)\n"
            return {"success": True, "output": {**input_data, "notion_results": [], "notion_count": 0}, "logs": logs}
        
        notion = await self.get_notion_service()
        if not notion:
            logs += "  ⚠️ Notion not connected\n"
            return {"success": False, "error": "Notion not connected", "output": input_data, "logs": logs}
        
        try:
            results = await notion.search(query, filter_type=filter_type)
            count = len(results)
            logs += f"  ✅ Found {count} results\n"
            return {
                "success": True,
                "output": {**input_data, "notion_results": results, "notion_count": count},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    # ========== Airtable Node Executors ==========
    
    async def _execute_airtable_create_record(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create a new record in an Airtable table."""
        base_id = params.get("base_id", "")
        table_name = params.get("table_name", "")
        fields = params.get("fields", {})
        
        base_id = _interpolate(base_id, input_data)
        table_name = _interpolate(table_name, input_data)
        for key, value in fields.items():
            if isinstance(value, str):
                fields[key] = _interpolate(value, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Creating Airtable record\n"
        logs += f"  Base: {base_id}, Table: {table_name}\n"
        logs += f"  Fields: {list(fields.keys())}\n"
        
        if is_test:
            logs += "  Record NOT created (test mode)\n"
            return {
                "success": True,
                "output": {**input_data, "airtable_record_id": "test-record-id", "airtable_created": False},
                "logs": logs
            }
        
        airtable = await self.get_airtable_service()
        if not airtable:
            logs += "  ⚠️ Airtable not connected\n"
            return {"success": False, "error": "Airtable not connected", "output": input_data, "logs": logs}
        
        try:
            result = await airtable.create_record(base_id, table_name, fields, typecast=True)
            record_id = result.get("id", "")
            logs += f"  ✅ Record created (ID: {record_id})\n"
            return {
                "success": True,
                "output": {**input_data, "airtable_record_id": record_id, "airtable_record": result, "airtable_created": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_airtable_update_record(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Update an existing Airtable record."""
        base_id = params.get("base_id", "")
        table_name = params.get("table_name", "")
        record_id = params.get("record_id", input_data.get("airtable_record_id", ""))
        fields = params.get("fields", {})
        
        base_id = _interpolate(base_id, input_data)
        table_name = _interpolate(table_name, input_data)
        record_id = _interpolate(record_id, input_data)
        for key, value in fields.items():
            if isinstance(value, str):
                fields[key] = _interpolate(value, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Updating Airtable record\n"
        logs += f"  Record: {record_id}\n"
        
        if is_test:
            logs += "  Record NOT updated (test mode)\n"
            return {"success": True, "output": {**input_data, "airtable_updated": False}, "logs": logs}
        
        airtable = await self.get_airtable_service()
        if not airtable:
            logs += "  ⚠️ Airtable not connected\n"
            return {"success": False, "error": "Airtable not connected", "output": input_data, "logs": logs}
        
        try:
            result = await airtable.update_record(base_id, table_name, record_id, fields, typecast=True)
            logs += f"  ✅ Record updated\n"
            return {
                "success": True,
                "output": {**input_data, "airtable_record": result, "airtable_updated": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_airtable_list_records(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """List records from an Airtable table."""
        base_id = params.get("base_id", "")
        table_name = params.get("table_name", "")
        view = params.get("view", None)
        filter_formula = params.get("filter_formula", None)
        max_records = params.get("max_records", 100)
        
        base_id = _interpolate(base_id, input_data)
        table_name = _interpolate(table_name, input_data)
        if filter_formula:
            filter_formula = _interpolate(filter_formula, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Listing Airtable records\n"
        logs += f"  Base: {base_id}, Table: {table_name}\n"
        
        if is_test:
            logs += "  Records NOT fetched (test mode)\n"
            return {"success": True, "output": {**input_data, "airtable_records": [], "airtable_count": 0}, "logs": logs}
        
        airtable = await self.get_airtable_service()
        if not airtable:
            logs += "  ⚠️ Airtable not connected\n"
            return {"success": False, "error": "Airtable not connected", "output": input_data, "logs": logs}
        
        try:
            result = await airtable.list_records(
                base_id, table_name,
                view=view,
                filter_formula=filter_formula,
                max_records=max_records
            )
            records = result.get("records", [])
            count = len(records)
            logs += f"  ✅ Retrieved {count} records\n"
            return {
                "success": True,
                "output": {**input_data, "airtable_records": records, "airtable_count": count},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_airtable_find_record(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Find records by field value in Airtable."""
        base_id = params.get("base_id", "")
        table_name = params.get("table_name", "")
        field_name = params.get("field_name", "")
        field_value = params.get("field_value", "")
        
        base_id = _interpolate(base_id, input_data)
        table_name = _interpolate(table_name, input_data)
        field_name = _interpolate(field_name, input_data)
        field_value = _interpolate(field_value, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Finding Airtable record\n"
        logs += f"  Find where {field_name} = {field_value}\n"
        
        if is_test:
            logs += "  Search NOT performed (test mode)\n"
            return {"success": True, "output": {**input_data, "airtable_record": None, "airtable_found": False}, "logs": logs}
        
        airtable = await self.get_airtable_service()
        if not airtable:
            logs += "  ⚠️ Airtable not connected\n"
            return {"success": False, "error": "Airtable not connected", "output": input_data, "logs": logs}
        
        try:
            records = await airtable.find_records_by_field(base_id, table_name, field_name, field_value, max_records=1)
            if records:
                record = records[0]
                logs += f"  ✅ Found record (ID: {record.get('id')})\n"
                return {
                    "success": True,
                    "output": {**input_data, "airtable_record": record, "airtable_record_id": record.get("id"), "airtable_found": True},
                    "logs": logs
                }
            else:
                logs += "  ⚠️ No matching record found\n"
                return {
                    "success": True,
                    "output": {**input_data, "airtable_record": None, "airtable_found": False},
                    "logs": logs
                }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    # ========== Calendly Node Executors ==========
    
    async def _execute_calendly_list_events(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """List scheduled events from Calendly."""
        status = params.get("status", "active")  # active or canceled
        min_start_time = params.get("min_start_time", None)
        max_start_time = params.get("max_start_time", None)
        count = params.get("count", 20)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Listing Calendly events\n"
        logs += f"  Status: {status}, Count: {count}\n"
        
        if is_test:
            logs += "  Events NOT fetched (test mode)\n"
            return {"success": True, "output": {**input_data, "calendly_events": [], "calendly_count": 0}, "logs": logs}
        
        calendly = await self.get_calendly_service()
        if not calendly:
            logs += "  ⚠️ Calendly not connected\n"
            return {"success": False, "error": "Calendly not connected", "output": input_data, "logs": logs}
        
        try:
            result = await calendly.list_scheduled_events(
                status=status,
                min_start_time=min_start_time,
                max_start_time=max_start_time,
                count=count
            )
            events = result.get("collection", [])
            formatted_events = [calendly.format_event_for_display(e) for e in events]
            count = len(formatted_events)
            logs += f"  ✅ Retrieved {count} events\n"
            return {
                "success": True,
                "output": {**input_data, "calendly_events": formatted_events, "calendly_count": count},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_calendly_get_event(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Get details of a specific Calendly event."""
        event_uuid = params.get("event_uuid", input_data.get("calendly_event_uuid", ""))
        event_uuid = _interpolate(event_uuid, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Getting Calendly event\n"
        logs += f"  Event UUID: {event_uuid}\n"
        
        if is_test:
            logs += "  Event NOT fetched (test mode)\n"
            return {"success": True, "output": {**input_data, "calendly_event": None}, "logs": logs}
        
        calendly = await self.get_calendly_service()
        if not calendly:
            logs += "  ⚠️ Calendly not connected\n"
            return {"success": False, "error": "Calendly not connected", "output": input_data, "logs": logs}
        
        try:
            event = await calendly.get_scheduled_event(event_uuid)
            # Also get invitees
            invitees_result = await calendly.list_event_invitees(event_uuid)
            invitees = [calendly.format_invitee_for_display(i) for i in invitees_result.get("collection", [])]
            
            formatted_event = calendly.format_event_for_display(event)
            formatted_event["invitees"] = invitees
            
            logs += f"  ✅ Event retrieved with {len(invitees)} invitee(s)\n"
            return {
                "success": True,
                "output": {**input_data, "calendly_event": formatted_event},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_calendly_cancel_event(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Cancel a scheduled Calendly event."""
        event_uuid = params.get("event_uuid", input_data.get("calendly_event_uuid", ""))
        reason = params.get("reason", "")
        
        event_uuid = _interpolate(event_uuid, input_data)
        reason = _interpolate(reason, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Canceling Calendly event\n"
        logs += f"  Event UUID: {event_uuid}\n"
        
        if is_test:
            logs += "  Event NOT canceled (test mode)\n"
            return {"success": True, "output": {**input_data, "calendly_canceled": False}, "logs": logs}
        
        calendly = await self.get_calendly_service()
        if not calendly:
            logs += "  ⚠️ Calendly not connected\n"
            return {"success": False, "error": "Calendly not connected", "output": input_data, "logs": logs}
        
        try:
            await calendly.cancel_scheduled_event(event_uuid, reason=reason or None)
            logs += f"  ✅ Event canceled\n"
            return {
                "success": True,
                "output": {**input_data, "calendly_canceled": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_calendly_create_link(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create a single-use scheduling link."""
        event_type_uuid = params.get("event_type_uuid", "")
        max_event_count = params.get("max_event_count", 1)
        
        event_type_uuid = _interpolate(event_type_uuid, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Creating Calendly scheduling link\n"
        logs += f"  Event Type UUID: {event_type_uuid}\n"
        
        if is_test:
            logs += "  Link NOT created (test mode)\n"
            return {"success": True, "output": {**input_data, "calendly_link": "https://calendly.com/test-link", "calendly_link_created": False}, "logs": logs}
        
        calendly = await self.get_calendly_service()
        if not calendly:
            logs += "  ⚠️ Calendly not connected\n"
            return {"success": False, "error": "Calendly not connected", "output": input_data, "logs": logs}
        
        try:
            # Build full event type URI
            event_type_uri = f"https://api.calendly.com/event_types/{event_type_uuid}"
            result = await calendly.create_scheduling_link(event_type_uri, max_event_count)
            booking_url = result.get("resource", {}).get("booking_url", "")
            logs += f"  ✅ Scheduling link created: {booking_url}\n"
            return {
                "success": True,
                "output": {**input_data, "calendly_link": booking_url, "calendly_link_created": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    # ========== Mailchimp Node Executors ==========
    
    async def _execute_mailchimp_add_subscriber(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Add a subscriber to a Mailchimp audience."""
        list_id = params.get("list_id", "")
        email = params.get("email", input_data.get("email", ""))
        first_name = params.get("first_name", input_data.get("first_name", ""))
        last_name = params.get("last_name", input_data.get("last_name", ""))
        status = params.get("status", "subscribed")
        tags = params.get("tags", [])
        
        list_id = _interpolate(list_id, input_data)
        email = _interpolate(email, input_data)
        first_name = _interpolate(first_name, input_data)
        last_name = _interpolate(last_name, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Adding Mailchimp subscriber\n"
        logs += f"  Email: {email}\n"
        logs += f"  List: {list_id}\n"
        
        if is_test:
            logs += "  Subscriber NOT added (test mode)\n"
            return {"success": True, "output": {**input_data, "mailchimp_subscribed": False}, "logs": logs}
        
        mailchimp = await self.get_mailchimp_service()
        if not mailchimp:
            logs += "  ⚠️ Mailchimp not connected\n"
            return {"success": False, "error": "Mailchimp not connected", "output": input_data, "logs": logs}
        
        try:
            merge_fields = {}
            if first_name:
                merge_fields["FNAME"] = first_name
            if last_name:
                merge_fields["LNAME"] = last_name
            
            result = await mailchimp.add_or_update_member(
                list_id=list_id,
                email=email,
                status=status,
                merge_fields=merge_fields if merge_fields else None
            )
            
            # Add tags if specified
            if tags:
                await mailchimp.add_tags_to_member(list_id, email, tags)
            
            logs += f"  ✅ Subscriber added/updated\n"
            return {
                "success": True,
                "output": {**input_data, "mailchimp_subscribed": True, "mailchimp_member": mailchimp.format_member_for_display(result)},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_mailchimp_update_subscriber(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Update an existing Mailchimp subscriber."""
        list_id = params.get("list_id", "")
        email = params.get("email", input_data.get("email", ""))
        status = params.get("status", None)
        merge_fields = params.get("merge_fields", {})
        
        list_id = _interpolate(list_id, input_data)
        email = _interpolate(email, input_data)
        for key, value in merge_fields.items():
            if isinstance(value, str):
                merge_fields[key] = _interpolate(value, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Updating Mailchimp subscriber\n"
        logs += f"  Email: {email}\n"
        
        if is_test:
            logs += "  Subscriber NOT updated (test mode)\n"
            return {"success": True, "output": {**input_data, "mailchimp_updated": False}, "logs": logs}
        
        mailchimp = await self.get_mailchimp_service()
        if not mailchimp:
            logs += "  ⚠️ Mailchimp not connected\n"
            return {"success": False, "error": "Mailchimp not connected", "output": input_data, "logs": logs}
        
        try:
            result = await mailchimp.update_member(
                list_id=list_id,
                email=email,
                status=status,
                merge_fields=merge_fields if merge_fields else None
            )
            logs += f"  ✅ Subscriber updated\n"
            return {
                "success": True,
                "output": {**input_data, "mailchimp_updated": True, "mailchimp_member": mailchimp.format_member_for_display(result)},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_mailchimp_add_tags(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Add tags to a Mailchimp subscriber."""
        list_id = params.get("list_id", "")
        email = params.get("email", input_data.get("email", ""))
        tags = params.get("tags", [])
        
        list_id = _interpolate(list_id, input_data)
        email = _interpolate(email, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Adding Mailchimp tags\n"
        logs += f"  Email: {email}\n"
        logs += f"  Tags: {tags}\n"
        
        if is_test:
            logs += "  Tags NOT added (test mode)\n"
            return {"success": True, "output": {**input_data, "mailchimp_tags_added": False}, "logs": logs}
        
        mailchimp = await self.get_mailchimp_service()
        if not mailchimp:
            logs += "  ⚠️ Mailchimp not connected\n"
            return {"success": False, "error": "Mailchimp not connected", "output": input_data, "logs": logs}
        
        try:
            await mailchimp.add_tags_to_member(list_id, email, tags)
            logs += f"  ✅ Tags added\n"
            return {
                "success": True,
                "output": {**input_data, "mailchimp_tags_added": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_mailchimp_send_campaign(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Create and send a Mailchimp campaign."""
        list_id = params.get("list_id", "")
        subject = params.get("subject", "")
        from_name = params.get("from_name", "")
        reply_to = params.get("reply_to", "")
        html_content = params.get("html_content", "")
        
        list_id = _interpolate(list_id, input_data)
        subject = _interpolate(subject, input_data)
        from_name = _interpolate(from_name, input_data)
        reply_to = _interpolate(reply_to, input_data)
        html_content = _interpolate(html_content, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending Mailchimp campaign\n"
        logs += f"  Subject: {subject}\n"
        logs += f"  List: {list_id}\n"
        
        if is_test:
            logs += "  Campaign NOT sent (test mode)\n"
            return {"success": True, "output": {**input_data, "mailchimp_campaign_sent": False}, "logs": logs}
        
        mailchimp = await self.get_mailchimp_service()
        if not mailchimp:
            logs += "  ⚠️ Mailchimp not connected\n"
            return {"success": False, "error": "Mailchimp not connected", "output": input_data, "logs": logs}
        
        try:
            # Create campaign
            campaign = await mailchimp.create_campaign(
                list_id=list_id,
                subject=subject,
                from_name=from_name,
                reply_to=reply_to
            )
            campaign_id = campaign.get("id", "")
            
            # Set content
            await mailchimp.set_campaign_content(campaign_id, html_content)
            
            # Send campaign
            await mailchimp.send_campaign(campaign_id)
            
            logs += f"  ✅ Campaign sent (ID: {campaign_id})\n"
            return {
                "success": True,
                "output": {**input_data, "mailchimp_campaign_id": campaign_id, "mailchimp_campaign_sent": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    # ========== Twilio Node Executors ==========
    
    async def _execute_twilio_send_sms(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send an SMS message via Twilio."""
        to = params.get("to", input_data.get("phone", ""))
        body = params.get("body", "")
        from_number = params.get("from_number", None)
        
        to = _interpolate(to, input_data)
        body = _interpolate(body, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending SMS via Twilio\n"
        logs += f"  To: {to}\n"
        logs += f"  Body: {body[:50]}{'...' if len(body) > 50 else ''}\n"
        
        if is_test:
            logs += "  SMS NOT sent (test mode)\n"
            return {"success": True, "output": {**input_data, "twilio_sms_sent": False}, "logs": logs}
        
        twilio = await self.get_twilio_service()
        if not twilio:
            logs += "  ⚠️ Twilio not connected\n"
            return {"success": False, "error": "Twilio not connected", "output": input_data, "logs": logs}
        
        try:
            # Format phone number
            formatted_to = twilio.format_phone_number(to)
            result = await twilio.send_sms(to=formatted_to, body=body, from_number=from_number)
            message_sid = result.get("sid", "")
            status = result.get("status", "")
            logs += f"  ✅ SMS sent (SID: {message_sid}, Status: {status})\n"
            return {
                "success": True,
                "output": {**input_data, "twilio_message_sid": message_sid, "twilio_sms_sent": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_twilio_send_whatsapp(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Send a WhatsApp message via Twilio."""
        to = params.get("to", input_data.get("phone", ""))
        body = params.get("body", "")
        media_url = params.get("media_url", None)
        
        to = _interpolate(to, input_data)
        body = _interpolate(body, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Sending WhatsApp via Twilio\n"
        logs += f"  To: {to}\n"
        logs += f"  Body: {body[:50]}{'...' if len(body) > 50 else ''}\n"
        
        if is_test:
            logs += "  WhatsApp NOT sent (test mode)\n"
            return {"success": True, "output": {**input_data, "twilio_whatsapp_sent": False}, "logs": logs}
        
        twilio = await self.get_twilio_service()
        if not twilio:
            logs += "  ⚠️ Twilio not connected\n"
            return {"success": False, "error": "Twilio not connected", "output": input_data, "logs": logs}
        
        try:
            formatted_to = twilio.format_phone_number(to)
            result = await twilio.send_whatsapp(to=formatted_to, body=body, media_url=media_url)
            message_sid = result.get("sid", "")
            status = result.get("status", "")
            logs += f"  ✅ WhatsApp sent (SID: {message_sid}, Status: {status})\n"
            return {
                "success": True,
                "output": {**input_data, "twilio_message_sid": message_sid, "twilio_whatsapp_sent": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}
    
    async def _execute_twilio_make_call(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Make a phone call via Twilio."""
        to = params.get("to", input_data.get("phone", ""))
        message = params.get("message", "")
        twiml_url = params.get("twiml_url", None)
        
        to = _interpolate(to, input_data)
        message = _interpolate(message, input_data)
        
        logs = f"[{datetime.utcnow().isoformat()}] {'[TEST] ' if is_test else ''}Making call via Twilio\n"
        logs += f"  To: {to}\n"
        
        if is_test:
            logs += "  Call NOT made (test mode)\n"
            return {"success": True, "output": {**input_data, "twilio_call_made": False}, "logs": logs}
        
        twilio = await self.get_twilio_service()
        if not twilio:
            logs += "  ⚠️ Twilio not connected\n"
            return {"success": False, "error": "Twilio not connected", "output": input_data, "logs": logs}
        
        try:
            formatted_to = twilio.format_phone_number(to)
            
            # Use TwiML URL if provided, otherwise create simple say TwiML
            if twiml_url:
                result = await twilio.make_call(to=formatted_to, twiml_url=twiml_url)
            else:
                twiml = twilio.create_say_twiml(message)
                result = await twilio.make_call(to=formatted_to, twiml=twiml)
            
            call_sid = result.get("sid", "")
            status = result.get("status", "")
            logs += f"  ✅ Call initiated (SID: {call_sid}, Status: {status})\n"
            return {
                "success": True,
                "output": {**input_data, "twilio_call_sid": call_sid, "twilio_call_made": True},
                "logs": logs
            }
        except Exception as e:
            logs += f"  ❌ Failed: {str(e)}\n"
            return {"success": False, "error": str(e), "output": input_data, "logs": logs}

    async def _execute_approval_gate(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Standalone approval node — signals the runner to pause for approval.
        
        The actual pause happens in workflow_runner._execute_from_node which checks
        requiresApproval. This node always has requiresApproval=True forced on it.
        If somehow reached without the flag, we still return a marker.
        """
        message = params.get("message", "This action requires your approval before proceeding.")
        logs = f"[{datetime.utcnow().isoformat()}] Approval gate reached\n"
        logs += f"  Message: {message}\n"
        
        if is_test:
            logs += "  [TEST] Auto-approved in test mode\n"
            return {"success": True, "output": {**input_data, "approval_status": "auto_approved"}, "logs": logs}
        
        # Normal execution: this node always has requiresApproval=True,
        # so the runner will create an approval before we even get here.
        # But just in case, return success to pass through.
        return {"success": True, "output": {**input_data, "approval_status": "approved"}, "logs": logs}

    async def _execute_default(self, params: dict, input_data: dict, is_test: bool) -> dict:
        """Default executor for unknown node types."""
        logs = f"[{datetime.utcnow().isoformat()}] Unknown node type\n"
        logs += f"  Parameters: {params}\n"
        return {"success": True, "output": input_data, "logs": logs}


def _interpolate(template: str, data: dict) -> str:
    """Replace {{variable}} with values from data."""
    if not template:
        return template
    result = template
    for key, value in data.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


# Backward compatibility - sync wrapper
def execute_node(
    node_type: str,
    parameters: dict[str, Any],
    input_data: dict[str, Any],
    is_test: bool = False,
    connections: Optional[dict] = None
) -> dict[str, Any]:
    """Execute a single node (sync wrapper for backward compatibility)."""
    executor = NodeExecutor(connections)
    
    # Check if we're already in an async context
    try:
        loop = asyncio.get_running_loop()
        # We're in an async context - use nest_asyncio or run in thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(_run_executor_sync, executor, node_type, parameters, input_data, is_test)
            return future.result()
    except RuntimeError:
        # No running loop - create a new one
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(
                executor.execute(node_type, parameters, input_data, is_test)
            )
            return result
        finally:
            loop.run_until_complete(executor.close())
            loop.close()


def _run_executor_sync(executor, node_type, parameters, input_data, is_test):
    """Run executor in a new event loop (for use in thread pool)."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(
            executor.execute(node_type, parameters, input_data, is_test)
        )
        return result
    finally:
        loop.run_until_complete(executor.close())
        loop.close()
