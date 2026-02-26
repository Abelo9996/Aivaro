import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models import Template


def seed_templates():
    db = SessionLocal()

    templates = [
        # ========== BOOKING & APPOINTMENTS ==========
        {
            "name": "Booking & Deposit Collection",
            "icon": "📅",
            "description": "Collect bookings, request deposits via Stripe, add to Google Calendar, and send confirmation emails.",
            "summary": "When someone books, Aivaro creates a calendar event, generates a deposit link, and sends a confirmation email.",
            "category": "Bookings",
            "business_types": ["service", "coaching", "beauty", "wellness", "resale", "contractor"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When booking form is submitted", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "cal-1", "type": "google_calendar_create", "label": "Create calendar event", "position": {"x": 250, "y": 200}, "parameters": {"title": "{{service}} - {{name}}", "date": "{{date}}", "start_time": "{{time}}", "duration": 1, "description": "Client: {{name}}\nEmail: {{email}}\nPhone: {{phone}}", "location": "{{location}}"}, "requiresApproval": False},
                {"id": "stripe-1", "type": "stripe_create_payment_link", "label": "Create deposit link", "position": {"x": 250, "y": 350}, "parameters": {"amount": 50, "product_name": "Booking Deposit - {{service}}", "success_message": "Thank you! Your appointment is confirmed."}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send confirmation with payment link", "position": {"x": 250, "y": 500}, "parameters": {"to": "{{email}}", "subject": "Booking Confirmed - {{service}} on {{date}}", "body": "Hi {{name}},\n\n✅ Your booking is confirmed!\n\n📅 Date: {{date}} at {{time}}\n📍 Location: {{location}}\n💰 Deposit: $50\n\nPlease pay your deposit to secure your spot: {{payment_link}}\n\nSee you soon!\n{{business_name}}"}, "requiresApproval": True},
                {"id": "sheet-1", "type": "append_row", "label": "Log to bookings spreadsheet", "position": {"x": 250, "y": 650}, "parameters": {"spreadsheet": "Bookings", "sheet_name": "Sheet1", "columns": [{"name": "Date", "value": "{{date}}"}, {"name": "Time", "value": "{{time}}"}, {"name": "Client", "value": "{{name}}"}, {"name": "Email", "value": "{{email}}"}, {"name": "Service", "value": "{{service}}"}, {"name": "Deposit", "value": "Pending"}]}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "cal-1"},
                {"id": "e2", "source": "cal-1", "target": "stripe-1"},
                {"id": "e3", "source": "stripe-1", "target": "email-1"},
                {"id": "e4", "source": "email-1", "target": "sheet-1"},
            ]
        },
        {
            "name": "Appointment Reminder",
            "icon": "⏰",
            "description": "Send automated reminder emails before appointments to reduce no-shows.",
            "summary": "Send a reminder email before each appointment to keep no-shows low.",
            "category": "Bookings",
            "business_types": ["service", "coaching", "beauty", "wellness", "medical", "contractor", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_manual", "label": "Run for upcoming appointments", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send reminder email", "position": {"x": 250, "y": 200}, "parameters": {"to": "{{customer_email}}", "subject": "Reminder: Your appointment is tomorrow", "body": "Hi {{customer_name}},\n\n⏰ Friendly reminder about your appointment tomorrow!\n\n📅 {{appointment_date}} at {{appointment_time}}\n📍 {{location}}\n\nIf you need to reschedule, please reply to this email ASAP.\n\nSee you soon!\n{{business_name}}"}, "requiresApproval": False},
                {"id": "notify-1", "type": "send_notification", "label": "Confirm reminder sent", "position": {"x": 250, "y": 350}, "parameters": {"message": "✅ Reminder sent to {{customer_name}} for {{appointment_date}}"}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "notify-1"},
            ]
        },

        # ========== LEAD GENERATION ==========
        {
            "name": "Lead Capture & Follow-Up",
            "icon": "🎯",
            "description": "Capture leads from a form, log to spreadsheet, send welcome email, and follow up in 2 days.",
            "summary": "When someone fills out your lead form, Aivaro logs them, sends a welcome email, and follows up automatically.",
            "category": "Lead Generation",
            "business_types": ["service", "agency", "saas", "coaching", "contractor", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When lead form is submitted", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "sheet-1", "type": "append_row", "label": "Add to leads spreadsheet", "position": {"x": 250, "y": 200}, "parameters": {"spreadsheet": "Leads", "sheet_name": "Sheet1", "columns": [{"name": "Date", "value": "{{today}}"}, {"name": "Name", "value": "{{name}}"}, {"name": "Email", "value": "{{email}}"}, {"name": "Phone", "value": "{{phone}}"}, {"name": "Source", "value": "{{source}}"}, {"name": "Status", "value": "New"}]}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send welcome email", "position": {"x": 250, "y": 350}, "parameters": {"to": "{{email}}", "subject": "Thanks for reaching out, {{name}}!", "body": "Hi {{name}},\n\nThanks for your interest! I'll be in touch within 24 hours to learn about your needs.\n\nFeel free to reply to this email with any questions.\n\nBest,\n{{owner_name}}"}, "requiresApproval": True},
                {"id": "notify-1", "type": "send_notification", "label": "Notify me of new lead", "position": {"x": 250, "y": 500}, "parameters": {"message": "🎯 New lead: {{name}} ({{email}}) from {{source}}"}, "requiresApproval": False},
                {"id": "delay-1", "type": "delay", "label": "Wait 2 days", "position": {"x": 250, "y": 650}, "parameters": {"duration": 2, "unit": "days"}, "requiresApproval": False},
                {"id": "email-2", "type": "send_email", "label": "Send follow-up email", "position": {"x": 250, "y": 800}, "parameters": {"to": "{{email}}", "subject": "Quick follow-up, {{name}}", "body": "Hi {{name}},\n\nJust following up on my earlier email. I'd love to hop on a quick call to learn about your needs.\n\nWould any time this week work?\n\nBest,\n{{owner_name}}"}, "requiresApproval": True},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "notify-1"},
                {"id": "e4", "source": "notify-1", "target": "delay-1"},
                {"id": "e5", "source": "delay-1", "target": "email-2"},
            ]
        },

        # ========== INVOICING & PAYMENTS ==========
        {
            "name": "Invoice & Payment Reminder",
            "icon": "💰",
            "description": "Send invoices via email, log to spreadsheet, and follow up on overdue payments.",
            "summary": "When you create an invoice, Aivaro sends it, logs it, and reminds the client if they don't pay.",
            "category": "Invoicing",
            "business_types": ["service", "agency", "freelance", "contractor", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When invoice is created", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "stripe-1", "type": "stripe_create_invoice", "label": "Create Stripe invoice", "position": {"x": 250, "y": 200}, "parameters": {"customer_email": "{{client_email}}", "amount": "{{amount}}", "description": "{{description}}", "due_days": 30, "auto_send": "true"}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send invoice email", "position": {"x": 250, "y": 350}, "parameters": {"to": "{{client_email}}", "subject": "Invoice from {{business_name}} - ${{amount}}", "body": "Hi {{client_name}},\n\n📄 Here's your invoice for ${{amount}}.\n📅 Due: {{due_date}}\n\nPay online: {{invoice_url}}\n\nThank you!\n{{business_name}}"}, "requiresApproval": True},
                {"id": "sheet-1", "type": "append_row", "label": "Log to invoices spreadsheet", "position": {"x": 250, "y": 500}, "parameters": {"spreadsheet": "Invoices", "sheet_name": "Sheet1", "columns": [{"name": "Date", "value": "{{today}}"}, {"name": "Client", "value": "{{client_name}}"}, {"name": "Amount", "value": "{{amount}}"}, {"name": "Due Date", "value": "{{due_date}}"}, {"name": "Status", "value": "Sent"}]}, "requiresApproval": False},
                {"id": "delay-1", "type": "delay", "label": "Wait 3 days after due date", "position": {"x": 250, "y": 650}, "parameters": {"duration": 3, "unit": "days"}, "requiresApproval": False},
                {"id": "email-2", "type": "send_email", "label": "Send payment reminder", "position": {"x": 250, "y": 800}, "parameters": {"to": "{{client_email}}", "subject": "Friendly reminder: Invoice overdue", "body": "Hi {{client_name}},\n\nJust a reminder that your invoice for ${{amount}} is past due.\n\nPay online: {{invoice_url}}\n\nIf you've already paid, please disregard.\n\nThank you,\n{{business_name}}"}, "requiresApproval": True},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "stripe-1"},
                {"id": "e2", "source": "stripe-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "sheet-1"},
                {"id": "e4", "source": "sheet-1", "target": "delay-1"},
                {"id": "e5", "source": "delay-1", "target": "email-2"},
            ]
        },

        # ========== CLIENT ONBOARDING ==========
        {
            "name": "New Client Welcome Sequence",
            "icon": "👋",
            "description": "Welcome new clients with a personalized email, log them, and send onboarding info the next day.",
            "summary": "When you add a new client, Aivaro sends a welcome email and follows up with onboarding materials.",
            "category": "Client Onboarding",
            "business_types": ["service", "agency", "saas", "coaching", "contractor"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When new client is added", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send welcome email", "position": {"x": 250, "y": 200}, "parameters": {"to": "{{email}}", "subject": "Welcome to {{business_name}}, {{name}}! 🎉", "body": "Hi {{name}},\n\nWelcome aboard! I'm thrilled to have you as a client.\n\nHere's what happens next:\n1. I'll send you an onboarding questionnaire\n2. We'll schedule our kickoff call\n3. You'll get access to everything you need\n\nIf you have questions, just reply here.\n\nExcited to work together!\n{{owner_name}}"}, "requiresApproval": True},
                {"id": "sheet-1", "type": "append_row", "label": "Add to client list", "position": {"x": 250, "y": 350}, "parameters": {"spreadsheet": "Clients", "sheet_name": "Sheet1", "columns": [{"name": "Start Date", "value": "{{today}}"}, {"name": "Name", "value": "{{name}}"}, {"name": "Email", "value": "{{email}}"}, {"name": "Package", "value": "{{package}}"}, {"name": "Status", "value": "Onboarding"}]}, "requiresApproval": False},
                {"id": "delay-1", "type": "delay", "label": "Wait 1 day", "position": {"x": 250, "y": 500}, "parameters": {"duration": 1, "unit": "days"}, "requiresApproval": False},
                {"id": "email-2", "type": "send_email", "label": "Send onboarding materials", "position": {"x": 250, "y": 650}, "parameters": {"to": "{{email}}", "subject": "Getting started - here's what you need", "body": "Hi {{name}},\n\nHere's everything you need to get started:\n\n📋 Onboarding form: {{onboarding_link}}\n📅 Book your kickoff call: {{booking_link}}\n\nPlease complete these within the next few days so we can hit the ground running.\n\nTalk soon!\n{{owner_name}}"}, "requiresApproval": True},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "delay-1"},
                {"id": "e4", "source": "delay-1", "target": "email-2"},
            ]
        },

        # ========== E-COMMERCE & RESALE ==========
        {
            "name": "Order Confirmation & Tracking",
            "icon": "📦",
            "description": "Send order confirmations, log to spreadsheet, and notify yourself of new orders.",
            "summary": "When an order is placed, Aivaro confirms it to the customer and logs it for you.",
            "category": "E-Commerce",
            "business_types": ["ecommerce", "retail", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When order is placed", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send order confirmation", "position": {"x": 250, "y": 200}, "parameters": {"to": "{{customer_email}}", "subject": "Order Confirmed! #{{order_id}}", "body": "Hi {{customer_name}},\n\n🎉 Thanks for your order!\n\n📦 Order #{{order_id}}\n💰 Total: ${{total}}\n📍 Shipping to: {{shipping_address}}\n\nWe'll notify you when it ships.\n\nThank you!\n{{business_name}}"}, "requiresApproval": True},
                {"id": "sheet-1", "type": "append_row", "label": "Log order", "position": {"x": 250, "y": 350}, "parameters": {"spreadsheet": "Orders", "sheet_name": "Sheet1", "columns": [{"name": "Order ID", "value": "{{order_id}}"}, {"name": "Date", "value": "{{today}}"}, {"name": "Customer", "value": "{{customer_name}}"}, {"name": "Total", "value": "{{total}}"}, {"name": "Status", "value": "Processing"}]}, "requiresApproval": False},
                {"id": "notify-1", "type": "send_notification", "label": "Notify me", "position": {"x": 250, "y": 500}, "parameters": {"message": "📦 New order #{{order_id}} - ${{total}} from {{customer_name}}"}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "notify-1"},
            ]
        },

        # ========== CUSTOMER SUPPORT ==========
        {
            "name": "Support Ticket Handler",
            "icon": "🎫",
            "description": "Log support requests, send acknowledgment emails, and notify you instantly.",
            "summary": "When a support request comes in, Aivaro acknowledges it and logs it for tracking.",
            "category": "Customer Support",
            "business_types": ["service", "saas", "ecommerce", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When ticket is submitted", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send acknowledgment", "position": {"x": 250, "y": 200}, "parameters": {"to": "{{customer_email}}", "subject": "We received your request", "body": "Hi {{customer_name}},\n\nThanks for reaching out! We've received your request and will respond within 24 hours.\n\n📋 Subject: {{subject}}\n\nBest,\n{{business_name}} Support"}, "requiresApproval": False},
                {"id": "sheet-1", "type": "append_row", "label": "Log ticket", "position": {"x": 250, "y": 350}, "parameters": {"spreadsheet": "Support Tickets", "sheet_name": "Sheet1", "columns": [{"name": "Date", "value": "{{today}}"}, {"name": "Customer", "value": "{{customer_name}}"}, {"name": "Email", "value": "{{customer_email}}"}, {"name": "Subject", "value": "{{subject}}"}, {"name": "Status", "value": "Open"}]}, "requiresApproval": False},
                {"id": "notify-1", "type": "send_notification", "label": "Alert me", "position": {"x": 250, "y": 500}, "parameters": {"message": "🎫 New ticket from {{customer_name}}: {{subject}}"}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "notify-1"},
            ]
        },
        {
            "name": "Feedback & Review Request",
            "icon": "⭐",
            "description": "Request feedback after completing a service, with a delayed follow-up.",
            "summary": "After a job is done, Aivaro asks for a review and follows up if they haven't responded.",
            "category": "Customer Support",
            "business_types": ["service", "coaching", "contractor", "beauty", "wellness", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When service is completed", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "delay-1", "type": "delay", "label": "Wait 1 day", "position": {"x": 250, "y": 200}, "parameters": {"duration": 1, "unit": "days"}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Request feedback", "position": {"x": 250, "y": 350}, "parameters": {"to": "{{customer_email}}", "subject": "How did we do? ⭐", "body": "Hi {{customer_name}},\n\nThank you for choosing us!\n\nWe'd love to hear about your experience. It takes 30 seconds:\n\n⭐ Leave a review: {{review_link}}\n\nYour feedback helps us improve and helps others find us.\n\nThank you!\n{{business_name}}"}, "requiresApproval": True},
                {"id": "sheet-1", "type": "append_row", "label": "Log feedback request", "position": {"x": 250, "y": 500}, "parameters": {"spreadsheet": "Feedback", "sheet_name": "Sheet1", "columns": [{"name": "Date", "value": "{{today}}"}, {"name": "Customer", "value": "{{customer_name}}"}, {"name": "Service", "value": "{{service}}"}, {"name": "Requested", "value": "Yes"}]}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "delay-1"},
                {"id": "e2", "source": "delay-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "sheet-1"},
            ]
        },

        # ========== EMAIL AUTOMATION ==========
        {
            "name": "Email Auto-Reply",
            "icon": "📧",
            "description": "Automatically reply to incoming emails matching specific criteria using AI.",
            "summary": "When you receive an email matching your filters, Aivaro drafts and sends an AI reply.",
            "category": "Email",
            "business_types": ["service", "agency", "saas", "coaching", "freelance"],
            "nodes": [
                {"id": "start-1", "type": "start_email", "label": "When matching email arrives", "position": {"x": 250, "y": 50}, "parameters": {"subject": "inquiry", "from": ""}, "requiresApproval": False},
                {"id": "ai-1", "type": "ai_reply", "label": "Generate AI reply", "position": {"x": 250, "y": 200}, "parameters": {"context": "Reply professionally to this inquiry. Mention our services and suggest scheduling a call.", "tone": "professional"}, "requiresApproval": False},
                {"id": "email-1", "type": "send_email", "label": "Send reply", "position": {"x": 250, "y": 350}, "parameters": {"to": "{{from}}", "subject": "Re: {{subject}}", "body": "{{ai_response}}"}, "requiresApproval": True},
                {"id": "notify-1", "type": "send_notification", "label": "Notify me", "position": {"x": 250, "y": 500}, "parameters": {"message": "📧 Auto-replied to {{from}}: {{subject}}"}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "ai-1"},
                {"id": "e2", "source": "ai-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "notify-1"},
            ]
        },

        # ========== REPORTS ==========
        {
            "name": "Daily Sales Tracker",
            "icon": "💵",
            "description": "Log every sale to a spreadsheet and get instant notifications.",
            "summary": "When a sale is made, Aivaro logs it and sends you a notification.",
            "category": "Reports",
            "business_types": ["retail", "ecommerce", "service", "resale"],
            "nodes": [
                {"id": "start-1", "type": "start_form", "label": "When sale is made", "position": {"x": 250, "y": 50}, "parameters": {}, "requiresApproval": False},
                {"id": "sheet-1", "type": "append_row", "label": "Log to sales sheet", "position": {"x": 250, "y": 200}, "parameters": {"spreadsheet": "Daily Sales", "sheet_name": "Sheet1", "columns": [{"name": "Date", "value": "{{today}}"}, {"name": "Item", "value": "{{item}}"}, {"name": "Amount", "value": "{{amount}}"}, {"name": "Customer", "value": "{{customer}}"}, {"name": "Payment", "value": "{{payment_method}}"}]}, "requiresApproval": False},
                {"id": "notify-1", "type": "send_notification", "label": "Celebrate the sale", "position": {"x": 250, "y": 350}, "parameters": {"message": "💵 Sale! {{item}} for ${{amount}}"}, "requiresApproval": False},
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "notify-1"},
            ]
        },
    ]

    # Clear existing templates and re-seed
    db.query(Template).delete()

    for t in templates:
        template = Template(
            name=t["name"],
            icon=t.get("icon", "⚡"),
            description=t.get("description", ""),
            summary=t.get("summary", ""),
            category=t.get("category", ""),
            business_types=t.get("business_types", []),
            nodes=t.get("nodes", []),
            edges=t.get("edges", []),
        )
        db.add(template)

    db.commit()
    print(f"Seeded {len(templates)} templates")
    db.close()


if __name__ == "__main__":
    seed_templates()
