import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models import Template


def seed_templates():
    db = SessionLocal()
    
    templates = [
        # ========== LEAD GENERATION & SALES ==========
        {
            "name": "Lead Capture & Follow-Up",
            "icon": "🎯",
            "description": "Capture new leads and automatically send a welcome email with follow-up sequence.",
            "summary": "When someone fills out your lead form, Aivaro welcomes them and follows up until they respond.",
            "category": "Lead Generation",
            "business_types": ["service", "agency", "saas", "coaching"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When lead form is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to CRM spreadsheet",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Leads CRM",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Name", "value": "{{name}}"},
                            {"name": "Email", "value": "{{email}}"},
                            {"name": "Phone", "value": "{{phone}}"},
                            {"name": "Source", "value": "{{source}}"},
                            {"name": "Status", "value": "New"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send welcome email",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Thanks for reaching out, {{name}}!",
                        "body": "Hi {{name}},\n\nThanks for your interest! I'm excited to learn more about how I can help you.\n\nI'll be in touch within 24 hours to schedule a quick call.\n\nIn the meantime, feel free to reply to this email with any questions.\n\nBest,\n{{owner_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify me of new lead",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "message": "🎯 New lead: {{name}} ({{email}}) from {{source}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait 2 days",
                    "position": {"x": 250, "y": 650},
                    "parameters": {"duration": 2, "unit": "days"},
                    "requiresApproval": False
                },
                {
                    "id": "email-2",
                    "type": "send_email",
                    "label": "Send follow-up",
                    "position": {"x": 250, "y": 800},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Quick follow-up, {{name}}",
                        "body": "Hi {{name}},\n\nJust wanted to follow up on my previous email. I'd love to hop on a quick 15-minute call to learn about your needs.\n\nWould any of these times work for you?\n\nLooking forward to connecting!\n\nBest,\n{{owner_name}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "notify-1"},
                {"id": "e4", "source": "notify-1", "target": "delay-1"},
                {"id": "e5", "source": "delay-1", "target": "email-2"}
            ]
        },
        {
            "name": "Sales Pipeline Tracker",
            "icon": "📊",
            "description": "Track every sale from initial contact to close with automatic logging.",
            "summary": "Log sales activities and get notified at each stage of your pipeline.",
            "category": "Lead Generation",
            "business_types": ["service", "agency", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When deal is updated",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log to pipeline",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Sales Pipeline",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Deal", "value": "{{deal_name}}"},
                            {"name": "Stage", "value": "{{stage}}"},
                            {"name": "Value", "value": "{{deal_value}}"},
                            {"name": "Notes", "value": "{{notes}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify of update",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "📊 Deal updated: {{deal_name}} moved to {{stage}} (${{deal_value}})"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "notify-1"}
            ]
        },

        # ========== BOOKING & APPOINTMENTS ==========
        {
            "name": "Appointment Booking & Deposit",
            "icon": "📅",
            "description": "Collect bookings, request deposits, and send automatic reminders.",
            "summary": "When someone books, Aivaro requests a deposit and sends reminders before their appointment.",
            "category": "Bookings",
            "business_types": ["service", "coaching", "beauty", "wellness"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When booking is made",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send booking confirmation",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Booking Confirmed - {{service}} on {{date}}",
                        "body": "Hi {{name}},\n\n✅ Your booking is confirmed!\n\n📅 Date: {{date}}\n⏰ Time: {{time}}\n📍 Location: {{location}}\n💰 Deposit: ${{deposit_amount}}\n\nTo secure your spot, please pay your deposit here: {{payment_link}}\n\nSee you soon!\n{{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to bookings sheet",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Bookings",
                        "columns": [
                            {"name": "Date", "value": "{{date}}"},
                            {"name": "Time", "value": "{{time}}"},
                            {"name": "Client", "value": "{{name}}"},
                            {"name": "Service", "value": "{{service}}"},
                            {"name": "Deposit", "value": "Pending"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify me",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "message": "📅 New booking: {{name}} for {{service}} on {{date}} at {{time}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "notify-1"}
            ]
        },
        {
            "name": "No-Show Prevention",
            "icon": "⏰",
            "description": "Send automated reminders 24 hours and 1 hour before appointments.",
            "summary": "Reduce no-shows with automatic email and notification reminders.",
            "category": "Bookings",
            "business_types": ["service", "coaching", "beauty", "wellness", "medical"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "Day before appointment",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send 24-hour reminder",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Reminder: Your appointment tomorrow",
                        "body": "Hi {{customer_name}},\n\n⏰ Just a friendly reminder about your appointment tomorrow!\n\n📅 {{appointment_date}}\n⏰ {{appointment_time}}\n📍 {{location}}\n\nIf you need to reschedule, please let us know ASAP.\n\nSee you soon!\n{{business_name}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Confirm reminder sent",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "✅ Reminder sent to {{customer_name}} for tomorrow's appointment"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "notify-1"}
            ]
        },

        # ========== CLIENT ONBOARDING ==========
        {
            "name": "New Client Welcome Sequence",
            "icon": "👋",
            "description": "Automatically onboard new clients with a welcome email series.",
            "summary": "When you add a new client, Aivaro sends a personalized welcome sequence.",
            "category": "Client Onboarding",
            "business_types": ["service", "agency", "saas", "coaching"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When new client is added",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send welcome email",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Welcome to {{business_name}}, {{name}}! 🎉",
                        "body": "Hi {{name}},\n\nWelcome aboard! I'm thrilled to have you as a client.\n\nHere's what happens next:\n\n1️⃣ I'll send you an onboarding questionnaire\n2️⃣ We'll schedule our kickoff call\n3️⃣ You'll get access to your client portal\n\nIf you have any questions, just reply to this email.\n\nExcited to work together!\n{{owner_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to client list",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Clients",
                        "columns": [
                            {"name": "Start Date", "value": "{{today}}"},
                            {"name": "Name", "value": "{{name}}"},
                            {"name": "Email", "value": "{{email}}"},
                            {"name": "Package", "value": "{{package}}"},
                            {"name": "Status", "value": "Onboarding"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait 1 day",
                    "position": {"x": 250, "y": 500},
                    "parameters": {"duration": 1, "unit": "days"},
                    "requiresApproval": False
                },
                {
                    "id": "email-2",
                    "type": "send_email",
                    "label": "Send onboarding questionnaire",
                    "position": {"x": 250, "y": 650},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Quick questionnaire to get started",
                        "body": "Hi {{name}},\n\nTo make sure I deliver the best results for you, please take 5 minutes to fill out this questionnaire:\n\n{{questionnaire_link}}\n\nThis helps me understand your goals, preferences, and expectations.\n\nTalk soon!\n{{owner_name}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "delay-1"},
                {"id": "e4", "source": "delay-1", "target": "email-2"}
            ]
        },

        # ========== INVOICING & PAYMENTS ==========
        {
            "name": "Invoice & Payment Reminder",
            "icon": "💰",
            "description": "Send invoices and automatic payment reminders for overdue accounts.",
            "summary": "When an invoice is due, Aivaro sends reminders until payment is received.",
            "category": "Invoicing",
            "business_types": ["service", "agency", "freelance"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When invoice is created",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send invoice",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{client_email}}",
                        "subject": "Invoice #{{invoice_number}} from {{business_name}}",
                        "body": "Hi {{client_name}},\n\nPlease find your invoice attached.\n\n📄 Invoice #{{invoice_number}}\n💰 Amount: ${{amount}}\n📅 Due Date: {{due_date}}\n\nPay online: {{payment_link}}\n\nThank you for your business!\n{{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log invoice",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Invoices",
                        "columns": [
                            {"name": "Invoice #", "value": "{{invoice_number}}"},
                            {"name": "Client", "value": "{{client_name}}"},
                            {"name": "Amount", "value": "{{amount}}"},
                            {"name": "Due Date", "value": "{{due_date}}"},
                            {"name": "Status", "value": "Sent"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait until due date + 3 days",
                    "position": {"x": 250, "y": 500},
                    "parameters": {"duration": 3, "unit": "days"},
                    "requiresApproval": False
                },
                {
                    "id": "email-2",
                    "type": "send_email",
                    "label": "Send payment reminder",
                    "position": {"x": 250, "y": 650},
                    "parameters": {
                        "to": "{{client_email}}",
                        "subject": "Friendly reminder: Invoice #{{invoice_number}} is overdue",
                        "body": "Hi {{client_name}},\n\nJust a friendly reminder that invoice #{{invoice_number}} for ${{amount}} is now past due.\n\nPay online: {{payment_link}}\n\nIf you've already paid, please disregard this message.\n\nQuestions? Just reply to this email.\n\nThank you,\n{{business_name}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "delay-1"},
                {"id": "e4", "source": "delay-1", "target": "email-2"}
            ]
        },
        {
            "name": "Refund Request Handler",
            "icon": "🔄",
            "description": "Process refund requests with your approval before sending confirmation.",
            "summary": "When a refund is requested, Aivaro notifies you for approval then confirms to the customer.",
            "category": "Invoicing",
            "business_types": ["service", "ecommerce", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When refund is requested",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Alert me",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "message": "🔄 Refund requested: ${{amount}} from {{customer_name}} - Reason: {{reason}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send refund confirmation",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Your refund has been processed",
                        "body": "Hi {{customer_name}},\n\nYour refund of ${{amount}} has been processed.\n\nIt should appear in your account within 5-10 business days.\n\nWe're sorry to see you go. If there's anything we could have done better, please let us know.\n\nBest,\n{{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log refund",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "spreadsheet": "Refunds",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Amount", "value": "{{amount}}"},
                            {"name": "Reason", "value": "{{reason}}"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "notify-1"},
                {"id": "e2", "source": "notify-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "sheet-1"}
            ]
        },

        # ========== E-COMMERCE ==========
        {
            "name": "Order Confirmation & Tracking",
            "icon": "📦",
            "description": "Send order confirmations and shipping updates automatically.",
            "summary": "When an order is placed, Aivaro confirms it and keeps customers updated.",
            "category": "E-Commerce",
            "business_types": ["ecommerce", "retail", "resale"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When order is placed",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send order confirmation",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Order Confirmed! #{{order_id}}",
                        "body": "Hi {{customer_name}},\n\n🎉 Thanks for your order!\n\n📦 Order #{{order_id}}\n💰 Total: ${{total}}\n📍 Shipping to: {{shipping_address}}\n\nWe'll notify you when it ships.\n\nTrack your order: {{tracking_link}}\n\nThank you for shopping with us!\n{{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to orders",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Orders",
                        "columns": [
                            {"name": "Order ID", "value": "{{order_id}}"},
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Email", "value": "{{customer_email}}"},
                            {"name": "Total", "value": "{{total}}"},
                            {"name": "Status", "value": "Processing"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify me",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "message": "📦 New order #{{order_id}} - ${{total}} from {{customer_name}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "notify-1"}
            ]
        },
        {
            "name": "Abandoned Cart Recovery",
            "icon": "🛒",
            "description": "Recover lost sales with automatic abandoned cart email reminders.",
            "summary": "When a cart is abandoned, Aivaro sends a reminder to bring them back.",
            "category": "E-Commerce",
            "business_types": ["ecommerce", "retail"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When cart is abandoned",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait 1 hour",
                    "position": {"x": 250, "y": 200},
                    "parameters": {"duration": 1, "unit": "hours"},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send cart reminder",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "You left something behind! 🛒",
                        "body": "Hi {{customer_name}},\n\nLooks like you left some items in your cart!\n\n{{cart_items}}\n\n💰 Total: ${{cart_total}}\n\nComplete your order: {{checkout_link}}\n\nNeed help? Just reply to this email.\n\n{{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "delay-2",
                    "type": "delay",
                    "label": "Wait 24 hours",
                    "position": {"x": 250, "y": 500},
                    "parameters": {"duration": 24, "unit": "hours"},
                    "requiresApproval": False
                },
                {
                    "id": "email-2",
                    "type": "send_email",
                    "label": "Send discount offer",
                    "position": {"x": 250, "y": 650},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "10% off to complete your order!",
                        "body": "Hi {{customer_name}},\n\nWe really want you to have these items! Here's 10% off your order:\n\n🎁 Use code: COMEBACK10\n\nYour cart:\n{{cart_items}}\n\nComplete your order: {{checkout_link}}\n\nOffer expires in 24 hours!\n\n{{business_name}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "delay-1"},
                {"id": "e2", "source": "delay-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "delay-2"},
                {"id": "e4", "source": "delay-2", "target": "email-2"}
            ]
        },

        # ========== CUSTOMER SUPPORT ==========
        {
            "name": "Support Ticket Handler",
            "icon": "🎫",
            "description": "Log support requests and send automatic acknowledgment emails.",
            "summary": "When a support ticket comes in, Aivaro acknowledges it and logs it for tracking.",
            "category": "Customer Support",
            "business_types": ["service", "saas", "ecommerce"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When ticket is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send acknowledgment",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "We received your request - Ticket #{{ticket_id}}",
                        "body": "Hi {{customer_name}},\n\nThanks for reaching out! We've received your support request.\n\n🎫 Ticket #{{ticket_id}}\n📋 Subject: {{subject}}\n\nOur team will respond within 24 hours.\n\nIn the meantime, check our FAQ: {{faq_link}}\n\nBest,\n{{business_name}} Support"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log ticket",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Support Tickets",
                        "columns": [
                            {"name": "Ticket #", "value": "{{ticket_id}}"},
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Email", "value": "{{customer_email}}"},
                            {"name": "Subject", "value": "{{subject}}"},
                            {"name": "Status", "value": "Open"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Alert support team",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "message": "🎫 New ticket #{{ticket_id}} from {{customer_name}}: {{subject}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "notify-1"}
            ]
        },
        {
            "name": "Customer Feedback Collection",
            "icon": "⭐",
            "description": "Automatically request feedback after service completion.",
            "summary": "After a service is completed, Aivaro asks for feedback and logs responses.",
            "category": "Customer Support",
            "business_types": ["service", "coaching", "agency"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When service is completed",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait 1 day",
                    "position": {"x": 250, "y": 200},
                    "parameters": {"duration": 1, "unit": "days"},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Request feedback",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "How did we do? ⭐",
                        "body": "Hi {{customer_name}},\n\nThank you for choosing us!\n\nWe'd love to hear about your experience. It only takes 30 seconds:\n\n⭐ Leave a review: {{review_link}}\n\nYour feedback helps us improve and helps others find us.\n\nThank you!\n{{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Log feedback request",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "message": "⭐ Feedback request sent to {{customer_name}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "delay-1"},
                {"id": "e2", "source": "delay-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "notify-1"}
            ]
        },

        # ========== REPORTS & ANALYTICS ==========
        {
            "name": "Weekly Business Summary",
            "icon": "📈",
            "description": "Get a weekly email with your key business metrics.",
            "summary": "Every week, Aivaro compiles your numbers and sends you a summary report.",
            "category": "Reports",
            "business_types": ["service", "agency", "saas", "ecommerce"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "Run weekly",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send weekly report",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{owner_email}}",
                        "subject": "📈 Your Weekly Business Summary",
                        "body": "Hey {{owner_name}},\n\nHere's your weekly snapshot:\n\n💰 Revenue: ${{revenue}}\n👥 New Leads: {{new_leads}}\n🎯 Conversion Rate: {{conversion_rate}}%\n📅 Appointments: {{appointments}}\n⭐ Avg Rating: {{avg_rating}}\n\nTop wins this week:\n{{wins}}\n\nAreas to focus:\n{{focus_areas}}\n\nKeep crushing it! 🚀"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"}
            ]
        },
        {
            "name": "Daily Sales Tracker",
            "icon": "💵",
            "description": "Log every sale and get daily notifications of your performance.",
            "summary": "Track all sales automatically and get notified of your progress.",
            "category": "Reports",
            "business_types": ["retail", "ecommerce", "service"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When sale is made",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log to sales sheet",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Daily Sales",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Time", "value": "{{time}}"},
                            {"name": "Item", "value": "{{item}}"},
                            {"name": "Amount", "value": "{{amount}}"},
                            {"name": "Customer", "value": "{{customer}}"},
                            {"name": "Payment Method", "value": "{{payment_method}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Celebrate the sale",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "💵 Sale! {{item}} for ${{amount}} - Daily total: ${{daily_total}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "notify-1"}
            ]
        },

        # ========== SOCIAL MEDIA & CONTENT ==========
        {
            "name": "Content Publishing Tracker",
            "icon": "📱",
            "description": "Track your content calendar and get reminders to post.",
            "summary": "Log all your content and never miss a posting schedule.",
            "category": "Marketing",
            "business_types": ["agency", "coaching", "creator"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When content is scheduled",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to content calendar",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Content Calendar",
                        "columns": [
                            {"name": "Scheduled Date", "value": "{{scheduled_date}}"},
                            {"name": "Platform", "value": "{{platform}}"},
                            {"name": "Content Type", "value": "{{content_type}}"},
                            {"name": "Caption", "value": "{{caption}}"},
                            {"name": "Status", "value": "Scheduled"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Confirm scheduled",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "📱 Content scheduled for {{platform}} on {{scheduled_date}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "notify-1"}
            ]
        },
        {
            "name": "Newsletter Subscriber Welcome",
            "icon": "📧",
            "description": "Welcome new newsletter subscribers with a personalized email.",
            "summary": "When someone subscribes, Aivaro sends a welcome email with your best content.",
            "category": "Marketing",
            "business_types": ["coaching", "creator", "agency", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When someone subscribes",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send welcome email",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Welcome to {{newsletter_name}}! 🎉",
                        "body": "Hey {{name}}!\n\nThanks for subscribing to {{newsletter_name}}!\n\nHere's what you can expect:\n📬 {{frequency}} emails with {{topic}}\n🎁 Exclusive tips and insights\n🚀 First access to new content\n\nTo get started, check out my most popular posts:\n{{popular_posts}}\n\nHit reply and tell me - what's your biggest challenge right now?\n\n{{owner_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to subscriber list",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Newsletter Subscribers",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Name", "value": "{{name}}"},
                            {"name": "Email", "value": "{{email}}"},
                            {"name": "Source", "value": "{{source}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Celebrate new subscriber",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "message": "📧 New subscriber: {{name}} ({{email}})"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"},
                {"id": "e3", "source": "sheet-1", "target": "notify-1"}
            ]
        },

        # ========== OPERATIONS ==========
        {
            "name": "Inventory Alert System",
            "icon": "📋",
            "description": "Get notified when inventory is running low.",
            "summary": "Track stock levels and get alerts before you run out.",
            "category": "Operations",
            "business_types": ["retail", "ecommerce", "resale"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When inventory is updated",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log inventory change",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Inventory Log",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Item", "value": "{{item}}"},
                            {"name": "Change", "value": "{{change}}"},
                            {"name": "New Qty", "value": "{{new_quantity}}"},
                            {"name": "Reason", "value": "{{reason}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Alert if low stock",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "📋 Inventory alert: {{item}} is now at {{new_quantity}} units"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "notify-1"}
            ]
        },
        {
            "name": "Expense Tracker",
            "icon": "🧾",
            "description": "Log all business expenses for easy bookkeeping.",
            "summary": "Track expenses automatically and keep your books organized.",
            "category": "Operations",
            "business_types": ["service", "agency", "freelance"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When expense is recorded",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log expense",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Expenses",
                        "columns": [
                            {"name": "Date", "value": "{{date}}"},
                            {"name": "Category", "value": "{{category}}"},
                            {"name": "Description", "value": "{{description}}"},
                            {"name": "Amount", "value": "{{amount}}"},
                            {"name": "Receipt", "value": "{{receipt_link}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Confirm logged",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "🧾 Expense logged: ${{amount}} for {{category}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "sheet-1"},
                {"id": "e2", "source": "sheet-1", "target": "notify-1"}
            ]
        }
    ]
    
    # Clear existing templates
    db.query(Template).delete()
    
    # Add new templates
    for template_data in templates:
        template = Template(**template_data)
        db.add(template)
    
    db.commit()
    db.close()
    
    print(f"Seeded {len(templates)} templates successfully!")


if __name__ == "__main__":
    seed_templates()
