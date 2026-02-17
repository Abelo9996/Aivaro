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

        # ========== SLACK INTEGRATIONS ==========
        {
            "name": "Slack Team Notifications",
            "icon": "💬",
            "description": "Send automated notifications to Slack channels for important events.",
            "summary": "Keep your team in the loop with automatic Slack alerts for leads, sales, and more.",
            "category": "Team Communication",
            "business_types": ["service", "agency", "saas", "startup"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When event occurs",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Post to Slack channel",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "channel": "#general",
                        "text": "🔔 *{{event_type}}*\n\n{{event_details}}\n\nTriggered at {{timestamp}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log notification",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Notification Log",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Event", "value": "{{event_type}}"},
                            {"name": "Channel", "value": "#general"},
                            {"name": "Status", "value": "Sent"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "slack-1"},
                {"id": "e2", "source": "slack-1", "target": "sheet-1"}
            ]
        },
        {
            "name": "Slack Deal Alerts",
            "icon": "🎉",
            "description": "Celebrate closed deals with automatic Slack announcements.",
            "summary": "When a deal closes, notify your team in Slack and track the win.",
            "category": "Team Communication",
            "business_types": ["service", "agency", "saas", "sales"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When deal is closed",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Announce in sales channel",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "channel": "#sales-wins",
                        "text": "🎉 *DEAL CLOSED!*\n\n💰 *{{deal_name}}* - ${{deal_value}}\n👤 Closed by: {{sales_rep}}\n📅 Date: {{close_date}}\n\nCongrats to the team! 🚀"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log to wins tracker",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Closed Deals",
                        "columns": [
                            {"name": "Date", "value": "{{close_date}}"},
                            {"name": "Deal", "value": "{{deal_name}}"},
                            {"name": "Value", "value": "{{deal_value}}"},
                            {"name": "Rep", "value": "{{sales_rep}}"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "slack-1"},
                {"id": "e2", "source": "slack-1", "target": "sheet-1"}
            ]
        },

        # ========== NOTION INTEGRATIONS ==========
        {
            "name": "Notion Task Manager",
            "icon": "📝",
            "description": "Automatically create and organize tasks in Notion databases.",
            "summary": "When tasks are submitted, add them to your Notion database with full details.",
            "category": "Productivity",
            "business_types": ["service", "agency", "saas", "startup"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When task is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "notion-1",
                    "type": "notion_create_page",
                    "label": "Create Notion task",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "database_id": "{{notion_database_id}}",
                        "title": "{{task_title}}",
                        "properties": {
                            "Status": "To Do",
                            "Priority": "{{priority}}",
                            "Due Date": "{{due_date}}",
                            "Assignee": "{{assignee}}"
                        }
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify team",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#tasks",
                        "text": "📝 New task created: *{{task_title}}*\nAssigned to: {{assignee}}\nDue: {{due_date}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "notion-1"},
                {"id": "e2", "source": "notion-1", "target": "slack-1"}
            ]
        },
        {
            "name": "Notion Meeting Notes",
            "icon": "📋",
            "description": "Log meeting notes to a Notion database with attendees and action items.",
            "summary": "After each meeting, automatically create a Notion page with notes and next steps.",
            "category": "Productivity",
            "business_types": ["service", "agency", "saas", "startup"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When meeting ends",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "notion-1",
                    "type": "notion_create_page",
                    "label": "Create meeting notes",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "database_id": "{{meetings_database_id}}",
                        "title": "{{meeting_title}} - {{meeting_date}}",
                        "properties": {
                            "Date": "{{meeting_date}}",
                            "Attendees": "{{attendees}}",
                            "Type": "{{meeting_type}}"
                        }
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notion-2",
                    "type": "notion_add_block",
                    "label": "Add notes content",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "page_id": "{{notion_page_id}}",
                        "content": "## Summary\n{{summary}}\n\n## Action Items\n{{action_items}}\n\n## Notes\n{{detailed_notes}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send notes to attendees",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "to": "{{attendee_emails}}",
                        "subject": "Meeting Notes: {{meeting_title}}",
                        "body": "Hi team,\n\nHere are the notes from today's meeting:\n\n{{summary}}\n\n**Action Items:**\n{{action_items}}\n\nFull notes: {{notion_link}}\n\nThanks!\n{{organizer_name}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "notion-1"},
                {"id": "e2", "source": "notion-1", "target": "notion-2"},
                {"id": "e3", "source": "notion-2", "target": "email-1"}
            ]
        },

        # ========== AIRTABLE INTEGRATIONS ==========
        {
            "name": "Airtable CRM Pipeline",
            "icon": "🗃️",
            "description": "Manage your sales pipeline in Airtable with automatic lead tracking.",
            "summary": "When leads come in, automatically add them to Airtable and track through stages.",
            "category": "Lead Generation",
            "business_types": ["service", "agency", "saas", "sales"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When lead is captured",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "airtable-1",
                    "type": "airtable_create_record",
                    "label": "Add to Airtable CRM",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "base_id": "{{airtable_base_id}}",
                        "table_name": "Leads",
                        "fields": {
                            "Name": "{{lead_name}}",
                            "Email": "{{lead_email}}",
                            "Phone": "{{lead_phone}}",
                            "Source": "{{lead_source}}",
                            "Stage": "New Lead",
                            "Created": "{{today}}"
                        }
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send welcome email",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{lead_email}}",
                        "subject": "Thanks for reaching out, {{lead_name}}!",
                        "body": "Hi {{lead_name}},\n\nThanks for your interest! I'll be in touch within 24 hours.\n\nBest,\n{{owner_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify sales team",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "channel": "#leads",
                        "text": "🎯 New lead: *{{lead_name}}* ({{lead_email}})\nSource: {{lead_source}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "airtable-1"},
                {"id": "e2", "source": "airtable-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "slack-1"}
            ]
        },
        {
            "name": "Airtable Project Tracker",
            "icon": "📊",
            "description": "Track project milestones and updates in Airtable with team notifications.",
            "summary": "When project status changes, update Airtable and notify stakeholders.",
            "category": "Operations",
            "business_types": ["service", "agency", "startup"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When project is updated",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "airtable-1",
                    "type": "airtable_update_record",
                    "label": "Update project in Airtable",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "base_id": "{{airtable_base_id}}",
                        "table_name": "Projects",
                        "record_id": "{{project_record_id}}",
                        "fields": {
                            "Status": "{{new_status}}",
                            "Last Updated": "{{today}}",
                            "Progress": "{{progress_percentage}}"
                        }
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify project channel",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#projects",
                        "text": "📊 *Project Update*\n\n*{{project_name}}* is now {{new_status}}\nProgress: {{progress_percentage}}%\nUpdated by: {{updated_by}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "airtable-1"},
                {"id": "e2", "source": "airtable-1", "target": "slack-1"}
            ]
        },

        # ========== CALENDLY INTEGRATIONS ==========
        {
            "name": "Calendly Booking Automation",
            "icon": "📅",
            "description": "Automate your meeting workflow when someone books via Calendly.",
            "summary": "When a Calendly booking is made, log it, notify your team, and prep for the meeting.",
            "category": "Bookings",
            "business_types": ["service", "coaching", "agency", "consulting"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_webhook",
                    "label": "When Calendly booking is made",
                    "position": {"x": 250, "y": 50},
                    "parameters": {
                        "webhook_type": "calendly"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "airtable-1",
                    "type": "airtable_create_record",
                    "label": "Log to meetings database",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "base_id": "{{airtable_base_id}}",
                        "table_name": "Meetings",
                        "fields": {
                            "Invitee Name": "{{invitee_name}}",
                            "Email": "{{invitee_email}}",
                            "Event Type": "{{event_type}}",
                            "Scheduled Time": "{{scheduled_time}}",
                            "Status": "Scheduled"
                        }
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify team",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#meetings",
                        "text": "📅 New booking!\n\n*{{event_type}}* with {{invitee_name}}\n📧 {{invitee_email}}\n⏰ {{scheduled_time}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notion-1",
                    "type": "notion_create_page",
                    "label": "Create meeting prep doc",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "database_id": "{{meetings_database_id}}",
                        "title": "Meeting Prep: {{invitee_name}}",
                        "properties": {
                            "Date": "{{scheduled_time}}",
                            "Type": "{{event_type}}",
                            "Status": "Prep Needed"
                        }
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "airtable-1"},
                {"id": "e2", "source": "airtable-1", "target": "slack-1"},
                {"id": "e3", "source": "slack-1", "target": "notion-1"}
            ]
        },

        # ========== MAILCHIMP INTEGRATIONS ==========
        {
            "name": "Mailchimp Subscriber Workflow",
            "icon": "📧",
            "description": "Add new subscribers to Mailchimp with tags and welcome sequences.",
            "summary": "When someone subscribes, add them to Mailchimp, tag them, and trigger welcome sequence.",
            "category": "Marketing",
            "business_types": ["coaching", "creator", "agency", "saas", "ecommerce"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When subscriber signs up",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "mailchimp-1",
                    "type": "mailchimp_add_member",
                    "label": "Add to Mailchimp audience",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "audience_id": "{{mailchimp_audience_id}}",
                        "email": "{{subscriber_email}}",
                        "merge_fields": {
                            "FNAME": "{{first_name}}",
                            "LNAME": "{{last_name}}"
                        },
                        "status": "subscribed"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "mailchimp-2",
                    "type": "mailchimp_add_tags",
                    "label": "Add subscriber tags",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "audience_id": "{{mailchimp_audience_id}}",
                        "email": "{{subscriber_email}}",
                        "tags": ["{{signup_source}}", "New Subscriber", "{{interest}}"]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify team",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "channel": "#subscribers",
                        "text": "📧 New subscriber: *{{first_name}} {{last_name}}*\n📬 {{subscriber_email}}\n🏷️ Source: {{signup_source}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "mailchimp-1"},
                {"id": "e2", "source": "mailchimp-1", "target": "mailchimp-2"},
                {"id": "e3", "source": "mailchimp-2", "target": "slack-1"}
            ]
        },

        # ========== TWILIO SMS INTEGRATIONS ==========
        {
            "name": "SMS Appointment Reminders",
            "icon": "📱",
            "description": "Send SMS reminders before appointments to reduce no-shows.",
            "summary": "Automatically text clients 24 hours and 1 hour before their appointments.",
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
                    "id": "twilio-1",
                    "type": "twilio_send_sms",
                    "label": "Send 24-hour SMS reminder",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_phone}}",
                        "body": "Hi {{customer_name}}! Reminder: Your appointment is tomorrow at {{appointment_time}}. Reply CONFIRM to confirm or RESCHEDULE if you need to change. - {{business_name}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log SMS sent",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "SMS Log",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Phone", "value": "{{customer_phone}}"},
                            {"name": "Type", "value": "24-Hour Reminder"},
                            {"name": "Status", "value": "Sent"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "twilio-1"},
                {"id": "e2", "source": "twilio-1", "target": "sheet-1"}
            ]
        },
        {
            "name": "SMS Order Notifications",
            "icon": "📦",
            "description": "Send SMS updates to customers about their order status.",
            "summary": "When order status changes, text the customer with updates.",
            "category": "E-Commerce",
            "business_types": ["ecommerce", "retail", "resale"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When order status changes",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "twilio-1",
                    "type": "twilio_send_sms",
                    "label": "Send status SMS",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_phone}}",
                        "body": "Hi {{customer_name}}! Order #{{order_id}} update: {{order_status}}. {{status_details}} Track: {{tracking_link}} - {{business_name}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log notification",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Order Updates",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Order ID", "value": "{{order_id}}"},
                            {"name": "Status", "value": "{{order_status}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Notified", "value": "SMS"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "twilio-1"},
                {"id": "e2", "source": "twilio-1", "target": "sheet-1"}
            ]
        },
        {
            "name": "WhatsApp Customer Support",
            "icon": "💬",
            "description": "Send WhatsApp messages for customer support and follow-ups.",
            "summary": "Reach customers on WhatsApp for support tickets and follow-ups.",
            "category": "Customer Support",
            "business_types": ["service", "ecommerce", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When support needed",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "twilio-1",
                    "type": "twilio_send_whatsapp",
                    "label": "Send WhatsApp message",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_whatsapp}}",
                        "body": "Hi {{customer_name}}! Thanks for reaching out. {{support_message}} - {{agent_name}}, {{business_name}} Support"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "airtable-1",
                    "type": "airtable_create_record",
                    "label": "Log support interaction",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "base_id": "{{airtable_base_id}}",
                        "table_name": "Support Log",
                        "fields": {
                            "Date": "{{today}}",
                            "Customer": "{{customer_name}}",
                            "Channel": "WhatsApp",
                            "Message": "{{support_message}}",
                            "Agent": "{{agent_name}}"
                        }
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "twilio-1"},
                {"id": "e2", "source": "twilio-1", "target": "airtable-1"}
            ]
        },

        # ========== DISCORD INTEGRATIONS ==========
        {
            "name": "Discord Community Alerts",
            "icon": "🎮",
            "description": "Send automated announcements to your Discord server.",
            "summary": "Notify your Discord community about new content, events, or updates.",
            "category": "Team Communication",
            "business_types": ["creator", "saas", "startup", "gaming"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When announcement is ready",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "discord-1",
                    "type": "discord_send_message",
                    "label": "Post to Discord channel",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "channel_id": "{{discord_channel_id}}",
                        "content": "📢 **{{announcement_title}}**\n\n{{announcement_body}}\n\n{{call_to_action}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log announcement",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Announcements",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Title", "value": "{{announcement_title}}"},
                            {"name": "Platform", "value": "Discord"},
                            {"name": "Channel", "value": "{{discord_channel_id}}"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "discord-1"},
                {"id": "e2", "source": "discord-1", "target": "sheet-1"}
            ]
        },

        # ========== GITHUB INTEGRATIONS ==========
        {
            "name": "GitHub Issue Automation",
            "icon": "🐙",
            "description": "Automatically create GitHub issues from bug reports or feature requests.",
            "summary": "When a bug or feature request comes in, create a GitHub issue and notify the team.",
            "category": "Developer Tools",
            "business_types": ["saas", "startup", "tech"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When bug report is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "github-1",
                    "type": "github_create_issue",
                    "label": "Create GitHub issue",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "repo": "{{github_repo}}",
                        "title": "[{{issue_type}}] {{issue_title}}",
                        "body": "## Description\n{{issue_description}}\n\n## Steps to Reproduce\n{{steps}}\n\n## Expected Behavior\n{{expected}}\n\n## Reported By\n{{reporter_name}} ({{reporter_email}})",
                        "labels": ["{{issue_type}}", "triage"]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify dev team",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#dev",
                        "text": "🐛 New {{issue_type}} reported: *{{issue_title}}*\n\nReported by: {{reporter_name}}\nGitHub: {{github_issue_link}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Confirm to reporter",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "to": "{{reporter_email}}",
                        "subject": "We received your {{issue_type}} report",
                        "body": "Hi {{reporter_name}},\n\nThanks for reporting this {{issue_type}}. We've logged it and our team will look into it.\n\nIssue: {{issue_title}}\n\nWe'll update you when there's progress.\n\nBest,\n{{business_name}} Team"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "github-1"},
                {"id": "e2", "source": "github-1", "target": "slack-1"},
                {"id": "e3", "source": "slack-1", "target": "email-1"}
            ]
        },

        # ========== ASANA/TRELLO PROJECT MANAGEMENT ==========
        {
            "name": "Asana Task Automation",
            "icon": "✅",
            "description": "Create and manage tasks in Asana from form submissions.",
            "summary": "When requests come in, create Asana tasks with full details and notify assignees.",
            "category": "Productivity",
            "business_types": ["service", "agency", "startup"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When request is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "asana-1",
                    "type": "asana_create_task",
                    "label": "Create Asana task",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "project_id": "{{asana_project_id}}",
                        "name": "{{task_name}}",
                        "notes": "{{task_description}}\n\nSubmitted by: {{requester_name}}",
                        "due_date": "{{due_date}}",
                        "assignee": "{{assignee_email}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify assignee",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#tasks",
                        "text": "✅ New task assigned!\n\n*{{task_name}}*\nAssigned to: <@{{assignee_slack_id}}>\nDue: {{due_date}}\n\nAsana: {{asana_task_link}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "asana-1"},
                {"id": "e2", "source": "asana-1", "target": "slack-1"}
            ]
        },
        {
            "name": "Trello Board Automation",
            "icon": "📋",
            "description": "Automatically create Trello cards for new projects or tasks.",
            "summary": "When new work comes in, create Trello cards and keep your board organized.",
            "category": "Productivity",
            "business_types": ["service", "agency", "freelance"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When project starts",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "trello-1",
                    "type": "trello_create_card",
                    "label": "Create Trello card",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "list_id": "{{trello_list_id}}",
                        "name": "{{project_name}}",
                        "desc": "Client: {{client_name}}\nDeadline: {{deadline}}\n\n{{project_details}}",
                        "due": "{{deadline}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Confirm card created",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "📋 Trello card created: {{project_name}} for {{client_name}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "trello-1"},
                {"id": "e2", "source": "trello-1", "target": "notify-1"}
            ]
        },

        # ========== LINEAR/JIRA ISSUE TRACKING ==========
        {
            "name": "Linear Sprint Automation",
            "icon": "🔄",
            "description": "Create Linear issues from customer feedback or feature requests.",
            "summary": "When feedback comes in, create Linear issues and track in your sprint.",
            "category": "Developer Tools",
            "business_types": ["saas", "startup", "tech"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When feedback is received",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "linear-1",
                    "type": "linear_create_issue",
                    "label": "Create Linear issue",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "team_id": "{{linear_team_id}}",
                        "title": "{{issue_title}}",
                        "description": "{{issue_description}}\n\n---\nFeedback from: {{customer_name}}",
                        "priority": "{{priority}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify product team",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#product",
                        "text": "🔄 New issue from customer feedback:\n\n*{{issue_title}}*\nPriority: {{priority}}\nFrom: {{customer_name}}\n\nLinear: {{linear_issue_link}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "linear-1"},
                {"id": "e2", "source": "linear-1", "target": "slack-1"}
            ]
        },
        {
            "name": "Jira Ticket Workflow",
            "icon": "🎫",
            "description": "Create and track Jira tickets from support requests.",
            "summary": "When support requests come in, create Jira tickets and track resolution.",
            "category": "Developer Tools",
            "business_types": ["saas", "enterprise", "tech"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When support request arrives",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "jira-1",
                    "type": "jira_create_issue",
                    "label": "Create Jira ticket",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "project_key": "{{jira_project_key}}",
                        "summary": "{{ticket_title}}",
                        "description": "{{ticket_description}}\n\nReported by: {{customer_name}} ({{customer_email}})",
                        "issue_type": "{{issue_type}}",
                        "priority": "{{priority}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Confirm to customer",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Support Ticket Created - {{jira_ticket_key}}",
                        "body": "Hi {{customer_name}},\n\nWe've received your request and created ticket {{jira_ticket_key}}.\n\nWe'll be in touch within {{sla_time}}.\n\nBest,\n{{business_name}} Support"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "jira-1"},
                {"id": "e2", "source": "jira-1", "target": "email-1"}
            ]
        },

        # ========== ZENDESK/INTERCOM SUPPORT ==========
        {
            "name": "Zendesk Ticket Automation",
            "icon": "🎫",
            "description": "Create Zendesk tickets from website forms and notify agents.",
            "summary": "When support requests come in, create Zendesk tickets and route to the right team.",
            "category": "Customer Support",
            "business_types": ["saas", "ecommerce", "enterprise"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When support form submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "zendesk-1",
                    "type": "zendesk_create_ticket",
                    "label": "Create Zendesk ticket",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "subject": "{{ticket_subject}}",
                        "description": "{{ticket_description}}",
                        "requester_email": "{{customer_email}}",
                        "requester_name": "{{customer_name}}",
                        "priority": "{{priority}}",
                        "tags": ["{{category}}", "web-form"]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Alert support team",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#support",
                        "text": "🎫 New Zendesk ticket:\n\n*{{ticket_subject}}*\nFrom: {{customer_name}}\nPriority: {{priority}}\n\nZendesk: {{zendesk_ticket_link}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "zendesk-1"},
                {"id": "e2", "source": "zendesk-1", "target": "slack-1"}
            ]
        },
        {
            "name": "Intercom Chat Follow-up",
            "icon": "💬",
            "description": "Follow up with customers after Intercom chat conversations.",
            "summary": "After chat conversations, send follow-up emails and log interactions.",
            "category": "Customer Support",
            "business_types": ["saas", "ecommerce", "startup"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_webhook",
                    "label": "When Intercom chat ends",
                    "position": {"x": 250, "y": 50},
                    "parameters": {
                        "webhook_type": "intercom"
                    },
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
                    "label": "Send follow-up email",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Following up on our chat",
                        "body": "Hi {{customer_name}},\n\nThanks for chatting with us today! I wanted to follow up and make sure your question was fully answered.\n\nHere's a summary of what we discussed:\n{{chat_summary}}\n\nIf you have any other questions, just reply to this email or start another chat.\n\nBest,\n{{agent_name}}\n{{business_name}} Support"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "airtable-1",
                    "type": "airtable_create_record",
                    "label": "Log conversation",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "base_id": "{{airtable_base_id}}",
                        "table_name": "Support Conversations",
                        "fields": {
                            "Date": "{{today}}",
                            "Customer": "{{customer_name}}",
                            "Channel": "Intercom Chat",
                            "Summary": "{{chat_summary}}",
                            "Agent": "{{agent_name}}",
                            "Follow-up Sent": "Yes"
                        }
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "delay-1"},
                {"id": "e2", "source": "delay-1", "target": "email-1"},
                {"id": "e3", "source": "email-1", "target": "airtable-1"}
            ]
        },

        # ========== HUBSPOT/SALESFORCE CRM ==========
        {
            "name": "HubSpot Lead Sync",
            "icon": "🧲",
            "description": "Sync new leads to HubSpot CRM with automatic deal creation.",
            "summary": "When leads come in, create HubSpot contacts and deals automatically.",
            "category": "Lead Generation",
            "business_types": ["service", "agency", "saas", "sales"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When lead is captured",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "hubspot-1",
                    "type": "hubspot_create_contact",
                    "label": "Create HubSpot contact",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "email": "{{lead_email}}",
                        "firstname": "{{first_name}}",
                        "lastname": "{{last_name}}",
                        "phone": "{{phone}}",
                        "company": "{{company}}",
                        "lead_source": "{{source}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "hubspot-2",
                    "type": "hubspot_create_deal",
                    "label": "Create HubSpot deal",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "dealname": "{{company}} - {{service}}",
                        "pipeline": "default",
                        "dealstage": "qualifiedtobuy",
                        "amount": "{{estimated_value}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify sales team",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "channel": "#sales",
                        "text": "🧲 New HubSpot lead!\n\n*{{first_name}} {{last_name}}* at {{company}}\n📧 {{lead_email}}\n💰 Est. value: ${{estimated_value}}\n\nHubSpot: {{hubspot_contact_link}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "hubspot-1"},
                {"id": "e2", "source": "hubspot-1", "target": "hubspot-2"},
                {"id": "e3", "source": "hubspot-2", "target": "slack-1"}
            ]
        },
        {
            "name": "Salesforce Opportunity Tracker",
            "icon": "☁️",
            "description": "Track sales opportunities in Salesforce with stage notifications.",
            "summary": "When deals move through stages, update Salesforce and notify stakeholders.",
            "category": "Lead Generation",
            "business_types": ["enterprise", "saas", "sales"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When opportunity is updated",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "salesforce-1",
                    "type": "salesforce_update_opportunity",
                    "label": "Update Salesforce opportunity",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "opportunity_id": "{{sf_opportunity_id}}",
                        "stage": "{{new_stage}}",
                        "amount": "{{deal_amount}}",
                        "close_date": "{{expected_close}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Notify team of stage change",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "channel": "#sales",
                        "text": "☁️ Salesforce opportunity update:\n\n*{{opportunity_name}}* moved to *{{new_stage}}*\n💰 Amount: ${{deal_amount}}\n📅 Expected close: {{expected_close}}\n\nOwner: {{opportunity_owner}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Update stakeholders",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "to": "{{stakeholder_emails}}",
                        "subject": "Deal Update: {{opportunity_name}}",
                        "body": "Hi team,\n\nQuick update on {{opportunity_name}}:\n\n📊 Stage: {{new_stage}}\n💰 Amount: ${{deal_amount}}\n📅 Expected close: {{expected_close}}\n\nNext steps: {{next_steps}}\n\nBest,\n{{sales_rep}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "salesforce-1"},
                {"id": "e2", "source": "salesforce-1", "target": "slack-1"},
                {"id": "e3", "source": "slack-1", "target": "email-1"}
            ]
        },

        # ========== STRIPE PAYMENT INTEGRATIONS ==========
        {
            "name": "Stripe Payment Notifications",
            "icon": "💳",
            "description": "Get notified when Stripe payments are received and log transactions.",
            "summary": "When payments come through Stripe, notify your team and track revenue.",
            "category": "Invoicing",
            "business_types": ["saas", "ecommerce", "service"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_webhook",
                    "label": "When Stripe payment received",
                    "position": {"x": 250, "y": 50},
                    "parameters": {
                        "webhook_type": "stripe"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "slack-1",
                    "type": "slack_send_message",
                    "label": "Celebrate payment",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "channel": "#revenue",
                        "text": "💳 *Payment received!*\n\n💰 Amount: ${{amount}}\n👤 Customer: {{customer_name}}\n📧 Email: {{customer_email}}\n📝 Description: {{description}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "airtable-1",
                    "type": "airtable_create_record",
                    "label": "Log to revenue tracker",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "base_id": "{{airtable_base_id}}",
                        "table_name": "Revenue",
                        "fields": {
                            "Date": "{{today}}",
                            "Amount": "{{amount}}",
                            "Customer": "{{customer_name}}",
                            "Description": "{{description}}",
                            "Stripe ID": "{{stripe_payment_id}}"
                        }
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send receipt",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Receipt for your payment - ${{amount}}",
                        "body": "Hi {{customer_name}},\n\nThank you for your payment!\n\n💰 Amount: ${{amount}}\n📝 Description: {{description}}\n🔢 Transaction ID: {{stripe_payment_id}}\n\nIf you have any questions, just reply to this email.\n\nBest,\n{{business_name}}"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "slack-1"},
                {"id": "e2", "source": "slack-1", "target": "airtable-1"},
                {"id": "e3", "source": "airtable-1", "target": "email-1"}
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
