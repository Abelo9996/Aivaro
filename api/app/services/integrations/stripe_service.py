"""
Stripe Service - Handles Stripe API integration for payments, invoices, and customers.
"""
import stripe
from typing import Optional, Any
from datetime import datetime


class StripeService:
    """Service for interacting with Stripe API."""
    
    def __init__(self, api_key: str):
        """
        Initialize with Stripe API key.
        
        Args:
            api_key: Stripe secret key (sk_live_... or sk_test_...)
        """
        self.api_key = api_key
        stripe.api_key = api_key
    
    async def get_or_create_customer(
        self, 
        email: str, 
        name: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Get existing customer by email or create a new one.
        
        Args:
            email: Customer email address
            name: Optional customer name
            metadata: Optional metadata dict
            
        Returns:
            Customer object
        """
        try:
            # Search for existing customer
            customers = stripe.Customer.search(
                query=f'email:"{email}"',
                limit=1
            )
            
            if customers.data:
                return {
                    "success": True,
                    "customer": customers.data[0],
                    "created": False,
                    "customer_id": customers.data[0].id
                }
            
            # Create new customer
            customer_data = {"email": email}
            if name:
                customer_data["name"] = name
            if metadata:
                customer_data["metadata"] = metadata
                
            customer = stripe.Customer.create(**customer_data)
            
            return {
                "success": True,
                "customer": customer,
                "created": True,
                "customer_id": customer.id
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "customer": None,
                "customer_id": None
            }
    
    async def create_invoice(
        self,
        customer_id: str,
        items: list[dict],
        description: Optional[str] = None,
        due_days: int = 30,
        auto_send: bool = False,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Create an invoice for a customer.
        
        Args:
            customer_id: Stripe customer ID
            items: List of items with 'description', 'amount' (in cents), and optional 'quantity'
            description: Invoice description/memo
            due_days: Days until due (default 30)
            auto_send: Whether to automatically send the invoice
            metadata: Optional metadata dict
            
        Returns:
            Invoice object with URL
        """
        try:
            # Create invoice items first
            for item in items:
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    amount=int(item.get("amount", 0)),  # Amount in cents
                    currency=item.get("currency", "usd"),
                    description=item.get("description", "Item"),
                    quantity=item.get("quantity", 1)
                )
            
            # Create the invoice
            invoice_data = {
                "customer": customer_id,
                "collection_method": "send_invoice",
                "days_until_due": due_days,
                "auto_advance": True,  # Auto-finalize
            }
            
            if description:
                invoice_data["description"] = description
            if metadata:
                invoice_data["metadata"] = metadata
                
            invoice = stripe.Invoice.create(**invoice_data)
            
            # Finalize the invoice
            invoice = stripe.Invoice.finalize_invoice(invoice.id)
            
            # Optionally send it
            if auto_send:
                invoice = stripe.Invoice.send_invoice(invoice.id)
            
            return {
                "success": True,
                "invoice": invoice,
                "invoice_id": invoice.id,
                "invoice_url": invoice.hosted_invoice_url,
                "invoice_pdf": invoice.invoice_pdf,
                "amount_due": invoice.amount_due,
                "status": invoice.status,
                "sent": auto_send
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "invoice": None,
                "invoice_id": None,
                "invoice_url": None
            }
    
    async def send_invoice(self, invoice_id: str) -> dict:
        """
        Send an existing invoice to the customer.
        
        Args:
            invoice_id: Stripe invoice ID
            
        Returns:
            Updated invoice object
        """
        try:
            invoice = stripe.Invoice.send_invoice(invoice_id)
            
            return {
                "success": True,
                "invoice": invoice,
                "invoice_id": invoice.id,
                "invoice_url": invoice.hosted_invoice_url,
                "status": invoice.status
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "invoice": None
            }
    
    async def create_payment_link(
        self,
        items: list[dict],
        metadata: Optional[dict] = None,
        after_completion_message: Optional[str] = None
    ) -> dict:
        """
        Create a Stripe Payment Link for one-time payments.
        
        Args:
            items: List of items with 'name', 'amount' (in cents), and optional 'quantity'
            metadata: Optional metadata dict
            after_completion_message: Message to show after payment
            
        Returns:
            Payment link URL
        """
        try:
            # Create price objects for each item
            line_items = []
            for item in items:
                price = stripe.Price.create(
                    unit_amount=int(item.get("amount", 0)),
                    currency=item.get("currency", "usd"),
                    product_data={
                        "name": item.get("name", item.get("description", "Item"))
                    }
                )
                line_items.append({
                    "price": price.id,
                    "quantity": item.get("quantity", 1)
                })
            
            # Create payment link
            link_data = {
                "line_items": line_items,
            }
            
            if metadata:
                link_data["metadata"] = metadata
            
            # Note: after_completion custom_message requires Stripe API version 2023-10-16+
            # For compatibility, we'll use hosted_confirmation instead
            if after_completion_message:
                link_data["after_completion"] = {
                    "type": "hosted_confirmation",
                    "hosted_confirmation": {
                        "custom_message": after_completion_message
                    }
                }
            
            payment_link = stripe.PaymentLink.create(**link_data)
            
            return {
                "success": True,
                "payment_link": payment_link,
                "url": payment_link.url,
                "payment_link_id": payment_link.id
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "url": None,
                "payment_link": None
            }
    
    async def get_invoice(self, invoice_id: str) -> dict:
        """
        Get invoice details.
        
        Args:
            invoice_id: Stripe invoice ID
            
        Returns:
            Invoice object
        """
        try:
            invoice = stripe.Invoice.retrieve(invoice_id)
            
            return {
                "success": True,
                "invoice": invoice,
                "invoice_id": invoice.id,
                "status": invoice.status,
                "amount_due": invoice.amount_due,
                "amount_paid": invoice.amount_paid,
                "invoice_url": invoice.hosted_invoice_url,
                "paid": invoice.paid
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "invoice": None
            }
    
    async def list_invoices(
        self, 
        customer_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10
    ) -> dict:
        """
        List invoices, optionally filtered by customer or status.
        
        Args:
            customer_id: Optional customer ID to filter by
            status: Optional status filter (draft, open, paid, void, uncollectible)
            limit: Maximum number of invoices to return
            
        Returns:
            List of invoices
        """
        try:
            params = {"limit": limit}
            if customer_id:
                params["customer"] = customer_id
            if status:
                params["status"] = status
                
            invoices = stripe.Invoice.list(**params)
            
            return {
                "success": True,
                "invoices": invoices.data,
                "count": len(invoices.data)
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "invoices": []
            }
    
    async def create_checkout_session(
        self,
        items: list[dict],
        success_url: str,
        cancel_url: str,
        mode: str = "payment",
        customer_email: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Create a Stripe Checkout Session for payment.
        
        Args:
            items: List of items with 'name', 'amount' (in cents), and optional 'quantity'
            success_url: URL to redirect to on success
            cancel_url: URL to redirect to on cancel
            mode: 'payment' for one-time, 'subscription' for recurring
            customer_email: Optional customer email to prefill
            metadata: Optional metadata dict
            
        Returns:
            Checkout session with URL
        """
        try:
            # Create line items
            line_items = []
            for item in items:
                line_items.append({
                    "price_data": {
                        "currency": item.get("currency", "usd"),
                        "unit_amount": int(item.get("amount", 0)),
                        "product_data": {
                            "name": item.get("name", item.get("description", "Item"))
                        }
                    },
                    "quantity": item.get("quantity", 1)
                })
            
            session_data = {
                "line_items": line_items,
                "mode": mode,
                "success_url": success_url,
                "cancel_url": cancel_url,
            }
            
            if customer_email:
                session_data["customer_email"] = customer_email
            if metadata:
                session_data["metadata"] = metadata
            
            session = stripe.checkout.Session.create(**session_data)
            
            return {
                "success": True,
                "session": session,
                "session_id": session.id,
                "url": session.url
            }
            
        except stripe.error.StripeError as e:
            return {
                "success": False,
                "error": str(e),
                "session": None,
                "url": None
            }
    
    async def close(self):
        """Cleanup (no persistent connections to close for Stripe)."""
        pass
