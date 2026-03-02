"""Stripe MCP Server — invoices, payments, customers."""
from app.mcp_servers.base import BaseMCPServer


class StripeMCPServer(BaseMCPServer):
    provider = "stripe"

    def __init__(self, api_key: str):
        super().__init__()
        from app.services.integrations.stripe_service import StripeService
        self.svc = StripeService(api_key=api_key)
        self._register_tools()

    def _register_tools(self):
        self._register(
            "stripe_create_invoice",
            "Create a Stripe invoice for a customer.",
            {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string", "description": "Customer email"},
                    "customer_name": {"type": "string", "description": "Customer name"},
                    "amount": {"type": "number", "description": "Amount in dollars"},
                    "description": {"type": "string", "description": "Invoice line item description"},
                    "currency": {"type": "string", "default": "usd"},
                },
                "required": ["customer_email", "amount"],
            },
            self._create_invoice,
        )
        self._register(
            "stripe_send_invoice",
            "Finalize and send an existing Stripe invoice.",
            {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Stripe invoice ID"},
                },
                "required": ["invoice_id"],
            },
            self._send_invoice,
        )
        self._register(
            "stripe_create_payment_link",
            "Create a Stripe payment link.",
            {
                "type": "object",
                "properties": {
                    "amount": {"type": "number", "description": "Amount in dollars"},
                    "description": {"type": "string", "description": "What the payment is for"},
                    "currency": {"type": "string", "default": "usd"},
                },
                "required": ["amount"],
            },
            self._create_payment_link,
        )
        self._register(
            "stripe_get_customer",
            "Look up a Stripe customer by email.",
            {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Customer email"},
                },
                "required": ["email"],
            },
            self._get_customer,
        )
        self._register(
            "stripe_check_payment",
            "Check if a Stripe invoice has been paid.",
            {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Stripe invoice ID"},
                },
                "required": ["invoice_id"],
            },
            self._check_payment,
        )
        self._register(
            "stripe_list_invoices",
            "List recent Stripe invoices.",
            {
                "type": "object",
                "properties": {
                    "customer_email": {"type": "string", "description": "Filter by customer email"},
                    "status": {"type": "string", "description": "Filter by status (draft, open, paid, void)"},
                    "limit": {"type": "integer", "default": 10},
                },
            },
            self._list_invoices,
        )

    async def _create_invoice(self, customer_email: str, amount: float, customer_name: str = "",
                              description: str = "Service", currency: str = "usd") -> dict:
        customer = await self.svc.get_or_create_customer(customer_email, name=customer_name)
        invoice = await self.svc.create_invoice(
            customer_id=customer["id"],
            amount=int(amount * 100),  # Convert to cents
            description=description,
            currency=currency,
        )
        return {
            "invoice_id": invoice.get("id"),
            "invoice_url": invoice.get("hosted_invoice_url"),
            "amount": amount,
            "customer_email": customer_email,
            "status": invoice.get("status"),
        }

    async def _send_invoice(self, invoice_id: str) -> dict:
        result = await self.svc.send_invoice(invoice_id)
        return {"invoice_sent": True, "invoice_id": invoice_id, "status": result.get("status")}

    async def _create_payment_link(self, amount: float, description: str = "Payment", currency: str = "usd") -> dict:
        link = await self.svc.create_payment_link(
            amount=int(amount * 100),
            description=description,
            currency=currency,
        )
        return {
            "payment_link_url": link.get("url"),
            "payment_link_id": link.get("id"),
            "amount": amount,
        }

    async def _get_customer(self, email: str) -> dict:
        customer = await self.svc.get_or_create_customer(email)
        return {"customer_id": customer.get("id"), "customer_email": email, "customer_name": customer.get("name")}

    async def _check_payment(self, invoice_id: str) -> dict:
        invoice = await self.svc.get_invoice(invoice_id)
        return {
            "invoice_id": invoice_id,
            "status": invoice.get("status"),
            "paid": invoice.get("status") == "paid",
            "amount_due": invoice.get("amount_due", 0) / 100,
            "amount_paid": invoice.get("amount_paid", 0) / 100,
        }

    async def _list_invoices(self, customer_email: str = None, status: str = None, limit: int = 10) -> dict:
        invoices = await self.svc.list_invoices(customer_email=customer_email, status=status, limit=limit)
        return {"invoices": invoices, "count": len(invoices)}

    async def close(self):
        await self.svc.close()
