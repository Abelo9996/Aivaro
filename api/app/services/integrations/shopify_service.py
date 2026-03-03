"""
Shopify Integration Service — products, orders, customers, inventory.
"""
import httpx
from typing import Optional, List, Any


class ShopifyService:
    """Service for interacting with Shopify Admin API (2024-01)."""

    def __init__(self, shop_domain: str, access_token: str):
        """
        Args:
            shop_domain: e.g. 'mystore.myshopify.com'
            access_token: Shopify Admin API access token
        """
        self.shop_domain = shop_domain.rstrip("/")
        if not self.shop_domain.startswith("https://"):
            self.base_url = f"https://{self.shop_domain}/admin/api/2024-01"
        else:
            self.base_url = f"{self.shop_domain}/admin/api/2024-01"
        self.access_token = access_token
        self._client = None

    @property
    def headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        client = await self._get_client()
        url = f"{self.base_url}{path}"
        resp = await client.request(method, url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()

    # ── Products ───────────────────────────────────────────────

    async def create_product(self, title: str, body_html: str = "", vendor: str = "",
                             product_type: str = "", tags: str = "", variants: list = None) -> dict:
        product = {"title": title}
        if body_html: product["body_html"] = body_html
        if vendor: product["vendor"] = vendor
        if product_type: product["product_type"] = product_type
        if tags: product["tags"] = tags
        if variants: product["variants"] = variants
        result = await self._request("POST", "/products.json", json={"product": product})
        return result.get("product", result)

    async def get_product(self, product_id: str) -> dict:
        result = await self._request("GET", f"/products/{product_id}.json")
        return result.get("product", result)

    async def list_products(self, limit: int = 50, collection_id: str = None) -> list:
        params = {"limit": limit}
        if collection_id: params["collection_id"] = collection_id
        result = await self._request("GET", "/products.json", params=params)
        return result.get("products", [])

    async def update_product(self, product_id: str, updates: dict) -> dict:
        updates["id"] = product_id
        result = await self._request("PUT", f"/products/{product_id}.json", json={"product": updates})
        return result.get("product", result)

    async def delete_product(self, product_id: str) -> dict:
        return await self._request("DELETE", f"/products/{product_id}.json")

    # ── Orders ─────────────────────────────────────────────────

    async def list_orders(self, limit: int = 50, status: str = "any", financial_status: str = None) -> list:
        params = {"limit": limit, "status": status}
        if financial_status: params["financial_status"] = financial_status
        result = await self._request("GET", "/orders.json", params=params)
        return result.get("orders", [])

    async def get_order(self, order_id: str) -> dict:
        result = await self._request("GET", f"/orders/{order_id}.json")
        return result.get("order", result)

    async def cancel_order(self, order_id: str, reason: str = "other") -> dict:
        result = await self._request("POST", f"/orders/{order_id}/cancel.json", json={"reason": reason})
        return result.get("order", result)

    async def close_order(self, order_id: str) -> dict:
        result = await self._request("POST", f"/orders/{order_id}/close.json")
        return result.get("order", result)

    async def create_order(self, line_items: list, customer: dict = None, email: str = None,
                           financial_status: str = "pending", note: str = "") -> dict:
        order = {"line_items": line_items, "financial_status": financial_status}
        if customer: order["customer"] = customer
        if email: order["email"] = email
        if note: order["note"] = note
        result = await self._request("POST", "/orders.json", json={"order": order})
        return result.get("order", result)

    # ── Customers ──────────────────────────────────────────────

    async def create_customer(self, email: str, first_name: str = "", last_name: str = "",
                              phone: str = "", tags: str = "", note: str = "") -> dict:
        customer = {"email": email}
        if first_name: customer["first_name"] = first_name
        if last_name: customer["last_name"] = last_name
        if phone: customer["phone"] = phone
        if tags: customer["tags"] = tags
        if note: customer["note"] = note
        result = await self._request("POST", "/customers.json", json={"customer": customer})
        return result.get("customer", result)

    async def get_customer(self, customer_id: str) -> dict:
        result = await self._request("GET", f"/customers/{customer_id}.json")
        return result.get("customer", result)

    async def list_customers(self, limit: int = 50) -> list:
        result = await self._request("GET", "/customers.json", params={"limit": limit})
        return result.get("customers", [])

    async def search_customers(self, query: str) -> list:
        result = await self._request("GET", "/customers/search.json", params={"query": query})
        return result.get("customers", [])

    async def update_customer(self, customer_id: str, updates: dict) -> dict:
        updates["id"] = customer_id
        result = await self._request("PUT", f"/customers/{customer_id}.json", json={"customer": updates})
        return result.get("customer", result)

    async def get_customer_orders(self, customer_id: str, limit: int = 50) -> list:
        result = await self._request("GET", f"/customers/{customer_id}/orders.json", params={"limit": limit})
        return result.get("orders", [])

    # ── Inventory ──────────────────────────────────────────────

    async def list_locations(self) -> list:
        result = await self._request("GET", "/locations.json")
        return result.get("locations", [])

    async def adjust_inventory(self, inventory_item_id: str, location_id: str, adjustment: int) -> dict:
        body = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available_adjustment": adjustment,
        }
        result = await self._request("POST", "/inventory_levels/adjust.json", json=body)
        return result.get("inventory_level", result)

    # ── Fulfillments ───────────────────────────────────────────

    async def list_fulfillments(self, order_id: str) -> list:
        result = await self._request("GET", f"/orders/{order_id}/fulfillments.json")
        return result.get("fulfillments", [])

    async def get_fulfillment(self, order_id: str, fulfillment_id: str) -> dict:
        result = await self._request("GET", f"/orders/{order_id}/fulfillments/{fulfillment_id}.json")
        return result.get("fulfillment", result)
