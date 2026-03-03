"""Shopify MCP Server — products, orders, customers, inventory."""
from app.mcp_servers.base import BaseMCPServer


class ShopifyMCPServer(BaseMCPServer):
    provider = "shopify"

    def __init__(self, shop_domain: str, access_token: str):
        super().__init__()
        from app.services.integrations.shopify_service import ShopifyService
        self.svc = ShopifyService(shop_domain=shop_domain, access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        # ── Products ──
        self._register("shopify_create_product", "Create a Shopify product.", {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "body_html": {"type": "string", "description": "Product description HTML"},
                "vendor": {"type": "string"},
                "product_type": {"type": "string"},
                "tags": {"type": "string", "description": "Comma-separated tags"},
                "price": {"type": "string", "description": "Default variant price"},
            },
            "required": ["title"],
        }, self._create_product)

        self._register("shopify_get_product", "Get a Shopify product by ID.", {
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
        }, self._get_product)

        self._register("shopify_list_products", "List Shopify products.", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "collection_id": {"type": "string"},
            },
        }, self._list_products)

        self._register("shopify_update_product", "Update a Shopify product.", {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "title": {"type": "string"},
                "body_html": {"type": "string"},
                "vendor": {"type": "string"},
                "tags": {"type": "string"},
            },
            "required": ["product_id"],
        }, self._update_product)

        self._register("shopify_delete_product", "Delete a Shopify product.", {
            "type": "object",
            "properties": {"product_id": {"type": "string"}},
            "required": ["product_id"],
        }, self._delete_product)

        # ── Orders ──
        self._register("shopify_list_orders", "List Shopify orders.", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
                "status": {"type": "string", "description": "open, closed, cancelled, any", "default": "any"},
                "financial_status": {"type": "string", "description": "paid, unpaid, refunded, etc."},
            },
        }, self._list_orders)

        self._register("shopify_get_order", "Get a Shopify order by ID.", {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        }, self._get_order)

        self._register("shopify_cancel_order", "Cancel a Shopify order.", {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "reason": {"type": "string", "default": "other"},
            },
            "required": ["order_id"],
        }, self._cancel_order)

        self._register("shopify_close_order", "Close a Shopify order.", {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        }, self._close_order)

        self._register("shopify_create_order", "Create a Shopify order.", {
            "type": "object",
            "properties": {
                "line_items": {"type": "array", "items": {"type": "object"}, "description": "Array of {variant_id, quantity}"},
                "email": {"type": "string"},
                "note": {"type": "string"},
                "financial_status": {"type": "string", "default": "pending"},
            },
            "required": ["line_items"],
        }, self._create_order)

        # ── Customers ──
        self._register("shopify_create_customer", "Create a Shopify customer.", {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "phone": {"type": "string"},
                "tags": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["email"],
        }, self._create_customer)

        self._register("shopify_get_customer", "Get a Shopify customer by ID.", {
            "type": "object",
            "properties": {"customer_id": {"type": "string"}},
            "required": ["customer_id"],
        }, self._get_customer)

        self._register("shopify_list_customers", "List Shopify customers.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_customers)

        self._register("shopify_search_customers", "Search Shopify customers.", {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "Search by name, email, etc."}},
            "required": ["query"],
        }, self._search_customers)

        self._register("shopify_update_customer", "Update a Shopify customer.", {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "email": {"type": "string"},
                "first_name": {"type": "string"},
                "last_name": {"type": "string"},
                "tags": {"type": "string"},
                "note": {"type": "string"},
            },
            "required": ["customer_id"],
        }, self._update_customer)

        self._register("shopify_get_customer_orders", "Get orders for a specific customer.", {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
            },
            "required": ["customer_id"],
        }, self._get_customer_orders)

        # ── Inventory ──
        self._register("shopify_list_locations", "List Shopify store locations.", {
            "type": "object", "properties": {},
        }, self._list_locations)

        self._register("shopify_adjust_inventory", "Adjust inventory level for a product variant.", {
            "type": "object",
            "properties": {
                "inventory_item_id": {"type": "string"},
                "location_id": {"type": "string"},
                "adjustment": {"type": "integer", "description": "Positive to add, negative to subtract"},
            },
            "required": ["inventory_item_id", "location_id", "adjustment"],
        }, self._adjust_inventory)

        # ── Fulfillments ──
        self._register("shopify_list_fulfillments", "List fulfillments for an order.", {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        }, self._list_fulfillments)

    # ── Handlers ───────────────────────────────────────────────

    async def _create_product(self, title: str, body_html: str = "", vendor: str = "",
                              product_type: str = "", tags: str = "", price: str = None) -> dict:
        variants = [{"price": price}] if price else None
        return await self.svc.create_product(title, body_html, vendor, product_type, tags, variants)

    async def _get_product(self, product_id: str) -> dict:
        return await self.svc.get_product(product_id)

    async def _list_products(self, limit: int = 50, collection_id: str = None) -> dict:
        products = await self.svc.list_products(limit, collection_id)
        return {"products": products, "count": len(products)}

    async def _update_product(self, product_id: str, **kwargs) -> dict:
        updates = {k: v for k, v in kwargs.items() if v is not None and k != "product_id"}
        return await self.svc.update_product(product_id, updates)

    async def _delete_product(self, product_id: str) -> dict:
        await self.svc.delete_product(product_id)
        return {"deleted": True, "product_id": product_id}

    async def _list_orders(self, limit: int = 50, status: str = "any", financial_status: str = None) -> dict:
        orders = await self.svc.list_orders(limit, status, financial_status)
        return {"orders": orders, "count": len(orders)}

    async def _get_order(self, order_id: str) -> dict:
        return await self.svc.get_order(order_id)

    async def _cancel_order(self, order_id: str, reason: str = "other") -> dict:
        return await self.svc.cancel_order(order_id, reason)

    async def _close_order(self, order_id: str) -> dict:
        return await self.svc.close_order(order_id)

    async def _create_order(self, line_items: list, email: str = None, note: str = "",
                            financial_status: str = "pending") -> dict:
        return await self.svc.create_order(line_items, email=email, note=note, financial_status=financial_status)

    async def _create_customer(self, email: str, first_name: str = "", last_name: str = "",
                               phone: str = "", tags: str = "", note: str = "") -> dict:
        return await self.svc.create_customer(email, first_name, last_name, phone, tags, note)

    async def _get_customer(self, customer_id: str) -> dict:
        return await self.svc.get_customer(customer_id)

    async def _list_customers(self, limit: int = 50) -> dict:
        customers = await self.svc.list_customers(limit)
        return {"customers": customers, "count": len(customers)}

    async def _search_customers(self, query: str) -> dict:
        customers = await self.svc.search_customers(query)
        return {"customers": customers, "count": len(customers)}

    async def _update_customer(self, customer_id: str, **kwargs) -> dict:
        updates = {k: v for k, v in kwargs.items() if v is not None and k != "customer_id"}
        return await self.svc.update_customer(customer_id, updates)

    async def _get_customer_orders(self, customer_id: str, limit: int = 50) -> dict:
        orders = await self.svc.get_customer_orders(customer_id, limit)
        return {"orders": orders, "count": len(orders)}

    async def _list_locations(self) -> dict:
        locations = await self.svc.list_locations()
        return {"locations": locations, "count": len(locations)}

    async def _adjust_inventory(self, inventory_item_id: str, location_id: str, adjustment: int) -> dict:
        return await self.svc.adjust_inventory(inventory_item_id, location_id, adjustment)

    async def _list_fulfillments(self, order_id: str) -> dict:
        fulfillments = await self.svc.list_fulfillments(order_id)
        return {"fulfillments": fulfillments, "count": len(fulfillments)}

    async def close(self):
        await self.svc.close()
