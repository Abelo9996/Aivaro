import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.models import Template


def seed_templates():
    db = SessionLocal()
    
    templates = [
        {
            "title": "Booking → Deposit → Reminders",
            "description": "Collect bookings, request deposits, and send reminders automatically.",
            "summary": "When a booking form is submitted, Aivaro will request a deposit and send reminder emails.",
            "category": "Bookings",
            "business_types": ["service", "agency"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When booking form is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send deposit request",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Deposit Required for Your Booking",
                        "body": "Hi {{name}},\n\nThank you for your booking on {{booking_date}}!\n\nTo secure your spot, please pay a deposit of ${{deposit_amount}}.\n\nPay here: {{payment_link}}"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait 24 hours",
                    "position": {"x": 250, "y": 350},
                    "parameters": {"duration": 24, "unit": "hours"},
                    "requiresApproval": False
                },
                {
                    "id": "email-2",
                    "type": "send_email",
                    "label": "Send reminder if unpaid",
                    "position": {"x": 250, "y": 500},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Reminder: Deposit Still Needed",
                        "body": "Hi {{name}},\n\nJust a friendly reminder that we haven't received your deposit yet.\n\nPlease pay to confirm your booking."
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "delay-1"},
                {"id": "e3", "source": "delay-1", "target": "email-2"}
            ]
        },
        {
            "title": "New Lead → Follow Up Until Booked",
            "description": "Automatically follow up with new leads until they book or respond.",
            "summary": "When a new lead comes in, Aivaro will send a series of follow-up emails.",
            "category": "Sales",
            "business_types": ["service", "agency", "saas"],
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
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send welcome email",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Thanks for reaching out!",
                        "body": "Hi {{name}},\n\nThanks for your interest! I'd love to help you.\n\nCan we schedule a quick call?"
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to leads spreadsheet",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Leads",
                        "columns": [
                            {"name": "Name", "value": "{{name}}"},
                            {"name": "Email", "value": "{{email}}"},
                            {"name": "Source", "value": "{{source}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "delay-1",
                    "type": "delay",
                    "label": "Wait 3 days",
                    "position": {"x": 250, "y": 500},
                    "parameters": {"duration": 3, "unit": "days"},
                    "requiresApproval": False
                },
                {
                    "id": "email-2",
                    "type": "send_email",
                    "label": "Send follow-up",
                    "position": {"x": 250, "y": 650},
                    "parameters": {
                        "to": "{{email}}",
                        "subject": "Quick follow-up",
                        "body": "Hi {{name}},\n\nJust following up on my previous email. Still interested in chatting?"
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
            "title": "Daily Sales Log",
            "description": "Log your daily sales to a spreadsheet automatically.",
            "summary": "When you record a sale, Aivaro will add it to your sales spreadsheet.",
            "category": "Sales",
            "business_types": ["resale", "service"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When sale is recorded",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to sales log",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Daily Sales",
                        "columns": [
                            {"name": "Date", "value": "{{date}}"},
                            {"name": "Item", "value": "{{item}}"},
                            {"name": "Amount", "value": "{{amount}}"},
                            {"name": "Customer", "value": "{{customer}}"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Notify sale recorded",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "Sale recorded: {{item}} for ${{amount}}"
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
            "title": "Weekly Profit Summary Email",
            "description": "Get a weekly email with your profit summary.",
            "summary": "Every week, Aivaro will compile your numbers and send you a summary.",
            "category": "Reports",
            "business_types": ["service", "resale", "agency", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "Run weekly (or manually)",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send weekly summary",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{owner_email}}",
                        "subject": "Your Weekly Profit Summary",
                        "body": "Here's your weekly summary:\n\nRevenue: ${{revenue}}\nExpenses: ${{expenses}}\nProfit: ${{profit}}\n\nGreat work this week!"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"}
            ]
        },
        {
            "title": "Overdue Invoice Follow-up",
            "description": "Automatically send reminders for overdue invoices.",
            "summary": "When an invoice is overdue, Aivaro will send a polite reminder email.",
            "category": "Billing",
            "business_types": ["service", "agency", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "When invoice is marked overdue",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send payment reminder",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Payment Reminder - Invoice #{{invoice_id}}",
                        "body": "Hi {{customer_name}},\n\nThis is a friendly reminder that invoice #{{invoice_id}} for ${{amount}} is now overdue.\n\nPlease arrange payment at your earliest convenience."
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log reminder sent",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Payment Reminders",
                        "columns": [
                            {"name": "Date", "value": "{{today}}"},
                            {"name": "Invoice", "value": "{{invoice_id}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Amount", "value": "{{amount}}"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"}
            ]
        },
        {
            "title": "Daily Schedule Summary",
            "description": "Get a daily email with your schedule for the day.",
            "summary": "Every morning, Aivaro will send you a summary of your day's appointments.",
            "category": "Productivity",
            "business_types": ["service", "agency"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "Run daily (or manually)",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send daily schedule",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{owner_email}}",
                        "subject": "Your Schedule for Today",
                        "body": "Good morning!\n\nHere's your schedule for today:\n\n{{schedule_summary}}\n\nHave a productive day!"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"}
            ]
        },
        {
            "title": "Customer Dispute Intake → Response Draft",
            "description": "Collect customer disputes and draft responses for your review.",
            "summary": "When a customer submits a dispute, Aivaro will create a response draft for you.",
            "category": "Support",
            "business_types": ["service", "resale", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_form",
                    "label": "When dispute is submitted",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log dispute",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "spreadsheet": "Customer Disputes",
                        "columns": [
                            {"name": "Date", "value": "{{date}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Issue", "value": "{{issue}}"},
                            {"name": "Status", "value": "Pending"}
                        ]
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Alert you to review",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "New dispute from {{customer_name}}: {{issue}}"
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
            "title": "Refund Request → Approval",
            "description": "Process refund requests with your approval.",
            "summary": "When a refund is requested, Aivaro will ask for your approval before processing.",
            "category": "Billing",
            "business_types": ["service", "resale", "saas"],
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
                    "label": "Notify you of refund request",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "message": "Refund requested: ${{amount}} from {{customer_name}}"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Process refund confirmation",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Your Refund Has Been Processed",
                        "body": "Hi {{customer_name}},\n\nYour refund of ${{amount}} has been processed. It should appear in your account within 5-7 business days.\n\nSorry to see you go!"
                    },
                    "requiresApproval": True
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "notify-1"},
                {"id": "e2", "source": "notify-1", "target": "email-1"}
            ]
        },
        {
            "title": "New Order → Receipt → Spreadsheet Log",
            "description": "Automatically send receipts and log orders.",
            "summary": "When a new order comes in, Aivaro will send a receipt and add it to your orders spreadsheet.",
            "category": "Sales",
            "business_types": ["resale", "service"],
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
                    "label": "Send order receipt",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Order Confirmation #{{order_id}}",
                        "body": "Hi {{customer_name}},\n\nThank you for your order!\n\nOrder #{{order_id}}\nTotal: ${{amount}}\n\nWe'll notify you when it ships."
                    },
                    "requiresApproval": True
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Add to orders spreadsheet",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Orders",
                        "columns": [
                            {"name": "Order ID", "value": "{{order_id}}"},
                            {"name": "Date", "value": "{{date}}"},
                            {"name": "Customer", "value": "{{customer_name}}"},
                            {"name": "Amount", "value": "{{amount}}"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "sheet-1"}
            ]
        },
        {
            "title": "Inventory Manifest → Summarize → Tasks",
            "description": "Process inventory and create tasks for low stock items.",
            "summary": "When you update inventory, Aivaro will check for low stock and create reorder tasks.",
            "category": "Operations",
            "business_types": ["resale"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "When you run inventory check",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Summarize inventory status",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "message": "Inventory check complete. {{low_stock_count}} items need reordering."
                    },
                    "requiresApproval": False
                },
                {
                    "id": "sheet-1",
                    "type": "append_row",
                    "label": "Log reorder tasks",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "spreadsheet": "Reorder Tasks",
                        "columns": [
                            {"name": "Date", "value": "{{date}}"},
                            {"name": "Items", "value": "{{low_stock_items}}"},
                            {"name": "Status", "value": "Pending"}
                        ]
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "notify-1"},
                {"id": "e2", "source": "notify-1", "target": "sheet-1"}
            ]
        },
        {
            "title": "Weekly KPI Report",
            "description": "Get a weekly report with your key performance indicators.",
            "summary": "Every week, Aivaro will compile your KPIs and send you a report.",
            "category": "Reports",
            "business_types": ["service", "agency", "saas"],
            "nodes": [
                {
                    "id": "start-1",
                    "type": "start_manual",
                    "label": "Run weekly (or manually)",
                    "position": {"x": 250, "y": 50},
                    "parameters": {},
                    "requiresApproval": False
                },
                {
                    "id": "email-1",
                    "type": "send_email",
                    "label": "Send KPI report",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{owner_email}}",
                        "subject": "Weekly KPI Report",
                        "body": "Weekly KPI Summary:\n\n📈 Revenue: ${{revenue}}\n👥 New Customers: {{new_customers}}\n⭐ Satisfaction: {{satisfaction_score}}\n📅 Appointments: {{appointments}}\n\nKeep up the great work!"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"}
            ]
        },
        {
            "title": "No-Show Prevention Reminders",
            "description": "Send reminders to reduce appointment no-shows.",
            "summary": "Before each appointment, Aivaro will send reminder emails and texts.",
            "category": "Bookings",
            "business_types": ["service"],
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
                    "label": "Send appointment reminder",
                    "position": {"x": 250, "y": 200},
                    "parameters": {
                        "to": "{{customer_email}}",
                        "subject": "Reminder: Your Appointment Tomorrow",
                        "body": "Hi {{customer_name}},\n\nJust a reminder that you have an appointment tomorrow:\n\n📅 {{appointment_date}} at {{appointment_time}}\n📍 {{location}}\n\nSee you then!"
                    },
                    "requiresApproval": False
                },
                {
                    "id": "notify-1",
                    "type": "send_notification",
                    "label": "Send SMS reminder",
                    "position": {"x": 250, "y": 350},
                    "parameters": {
                        "message": "Reminder: Appointment tomorrow at {{appointment_time}} with {{customer_name}}"
                    },
                    "requiresApproval": False
                }
            ],
            "edges": [
                {"id": "e1", "source": "start-1", "target": "email-1"},
                {"id": "e2", "source": "email-1", "target": "notify-1"}
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
