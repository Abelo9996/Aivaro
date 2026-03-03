"""Stripe MCP Server — payments, invoices, customers, subscriptions."""
from app.mcp_servers.base import BaseMCPServer


class StripeMCPServer(BaseMCPServer):
    provider = "stripe"

    def __init__(self, api_key: str):
        super().__init__()
        from app.services.integrations.stripe_service import StripeService
        self.svc = StripeService(api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register("stripe_create_invoice", "Create a Stripe invoice.", {
            "type": "object",
            "properties": {
                "customer_email": {"type": "string", "description": "Customer email"},
                "amount": {"type": "number", "description": "Amount in dollars"},
                "description": {"type": "string", "description": "Line item description"},
                "due_days": {"type": "integer", "description": "Days until due", "default": 30},
                "auto_send": {"type": "boolean", "description": "Auto-send after creation", "default": False},
            },
            "required": ["customer_email", "amount", "description"],
        }, self._create_invoice)

        self._register("stripe_send_invoice", "Send/finalize an existing Stripe invoice.", {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "string", "description": "Stripe invoice ID"},
            },
            "required": ["invoice_id"],
        }, self._send_invoice)

        self._register("stripe_create_payment_link", "Create a Stripe payment link.", {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount in dollars"},
                "product_name": {"type": "string", "description": "Product/service name"},
                "success_message": {"type": "string", "description": "Success page message"},
            },
            "required": ["amount", "product_name"],
        }, self._create_payment_link)

        self._register("stripe_get_customer", "Get or create a Stripe customer by email.", {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer email"},
                "name": {"type": "string", "description": "Customer name"},
            },
            "required": ["email"],
        }, self._get_customer)

        self._register("stripe_check_payment", "Check if a payment was made for an invoice or payment link.", {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "string", "description": "Invoice ID to check"},
            },
            "required": ["invoice_id"],
        }, self._check_payment)

        self._register("stripe_list_invoices", "List recent Stripe invoices.", {
            "type": "object",
            "properties": {
                "customer_email": {"type": "string", "description": "Filter by customer email"},
                "status": {"type": "string", "description": "Filter by status (draft, open, paid, void)"},
                "limit": {"type": "integer", "default": 20},
            },
        }, self._list_invoices)

        self._register("stripe_get_invoice", "Get details of a specific Stripe invoice.", {
            "type": "object",
            "properties": {
                "invoice_id": {"type": "string", "description": "Stripe invoice ID"},
            },
            "required": ["invoice_id"],
        }, self._get_invoice)

        self._register("stripe_create_checkout_session", "Create a Stripe Checkout session (hosted payment page).", {
            "type": "object",
            "properties": {
                "amount": {"type": "number", "description": "Amount in dollars"},
                "product_name": {"type": "string", "description": "Product/service name"},
                "success_url": {"type": "string", "description": "URL to redirect after success"},
                "cancel_url": {"type": "string", "description": "URL to redirect on cancel"},
                "customer_email": {"type": "string", "description": "Pre-fill customer email"},
            },
            "required": ["amount", "product_name"],
        }, self._create_checkout)

    # ── Handlers ───────────────────────────────────────────────

    async def _create_invoice(self, customer_email: str, amount: float, description: str,
                              due_days: int = 30, auto_send: bool = False) -> dict:
        result = await self.svc.create_invoice(
            customer_email=customer_email, amount=amount, description=description,
            due_days=due_days, auto_send=auto_send,
        )
        return result

    async def _send_invoice(self, invoice_id: str) -> dict:
        result = await self.svc.send_invoice(invoice_id)
        return result

    async def _create_payment_link(self, amount: float, product_name: str, success_message: str = "") -> dict:
        result = await self.svc.create_payment_link(
            amount=amount, product_name=product_name, success_message=success_message,
        )
        return result

    async def _get_customer(self, email: str, name: str = "") -> dict:
        result = await self.svc.get_or_create_customer(email=email, name=name)
        return result

    async def _check_payment(self, invoice_id: str) -> dict:
        result = await self.svc.get_invoice(invoice_id)
        return {"invoice_id": invoice_id, "status": result.get("status"), "paid": result.get("status") == "paid", "amount_due": result.get("amount_due")}

    async def _list_invoices(self, customer_email: str = None, status: str = None, limit: int = 20) -> dict:
        result = await self.svc.list_invoices(customer_email=customer_email, status=status, limit=limit)
        return {"invoices": result, "count": len(result)}

    async def _get_invoice(self, invoice_id: str) -> dict:
        result = await self.svc.get_invoice(invoice_id)
        return {"invoice": result}

    async def _create_checkout(self, amount: float, product_name: str, success_url: str = None,
                               cancel_url: str = None, customer_email: str = None) -> dict:
        result = await self.svc.create_checkout_session(
            amount=amount, product_name=product_name,
            success_url=success_url, cancel_url=cancel_url, customer_email=customer_email,
        )
        return result

    async def close(self):
        await self.svc.close()
