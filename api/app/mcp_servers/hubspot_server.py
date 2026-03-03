"""HubSpot MCP Server — contacts, companies, deals, tickets, pipelines."""
from app.mcp_servers.base import BaseMCPServer


class HubSpotMCPServer(BaseMCPServer):
    provider = "hubspot"

    def __init__(self, access_token: str):
        super().__init__()
        from app.services.integrations.hubspot_service import HubSpotService
        self.svc = HubSpotService(access_token=access_token)
        self._register_tools()

    def _register_tools(self):
        # ── Contacts ──
        self._register("hubspot_create_contact", "Create a HubSpot contact.", {
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "firstname": {"type": "string"},
                "lastname": {"type": "string"},
                "phone": {"type": "string"},
                "company": {"type": "string"},
            },
            "required": ["email"],
        }, self._create_contact)

        self._register("hubspot_update_contact", "Update a HubSpot contact.", {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string"},
                "properties": {"type": "object", "description": "Properties to update"},
            },
            "required": ["contact_id", "properties"],
        }, self._update_contact)

        self._register("hubspot_get_contact", "Get a HubSpot contact by ID.", {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string"},
            },
            "required": ["contact_id"],
        }, self._get_contact)

        self._register("hubspot_search_contacts", "Search HubSpot contacts.", {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query (name, email, etc.)"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        }, self._search_contacts)

        self._register("hubspot_list_contacts", "List HubSpot contacts.", {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 50},
            },
        }, self._list_contacts)

        self._register("hubspot_delete_contact", "Delete a HubSpot contact.", {
            "type": "object",
            "properties": {"contact_id": {"type": "string"}},
            "required": ["contact_id"],
        }, self._delete_contact)

        # ── Companies ──
        self._register("hubspot_create_company", "Create a HubSpot company.", {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "domain": {"type": "string"},
                "industry": {"type": "string"},
                "phone": {"type": "string"},
            },
            "required": ["name"],
        }, self._create_company)

        self._register("hubspot_update_company", "Update a HubSpot company.", {
            "type": "object",
            "properties": {
                "company_id": {"type": "string"},
                "properties": {"type": "object"},
            },
            "required": ["company_id", "properties"],
        }, self._update_company)

        self._register("hubspot_get_company", "Get a HubSpot company by ID.", {
            "type": "object",
            "properties": {"company_id": {"type": "string"}},
            "required": ["company_id"],
        }, self._get_company)

        self._register("hubspot_search_companies", "Search HubSpot companies.", {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        }, self._search_companies)

        # ── Deals ──
        self._register("hubspot_create_deal", "Create a HubSpot deal.", {
            "type": "object",
            "properties": {
                "dealname": {"type": "string"},
                "amount": {"type": "string"},
                "dealstage": {"type": "string"},
                "pipeline": {"type": "string"},
                "closedate": {"type": "string", "description": "ISO date"},
            },
            "required": ["dealname"],
        }, self._create_deal)

        self._register("hubspot_update_deal", "Update a HubSpot deal.", {
            "type": "object",
            "properties": {
                "deal_id": {"type": "string"},
                "properties": {"type": "object"},
            },
            "required": ["deal_id", "properties"],
        }, self._update_deal)

        self._register("hubspot_get_deal", "Get a HubSpot deal by ID.", {
            "type": "object",
            "properties": {"deal_id": {"type": "string"}},
            "required": ["deal_id"],
        }, self._get_deal)

        self._register("hubspot_search_deals", "Search HubSpot deals.", {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        }, self._search_deals)

        self._register("hubspot_list_deals", "List HubSpot deals.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_deals)

        # ── Tickets ──
        self._register("hubspot_create_ticket", "Create a HubSpot support ticket.", {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "content": {"type": "string"},
                "hs_pipeline": {"type": "string"},
                "hs_pipeline_stage": {"type": "string"},
            },
            "required": ["subject"],
        }, self._create_ticket)

        self._register("hubspot_update_ticket", "Update a HubSpot ticket.", {
            "type": "object",
            "properties": {
                "ticket_id": {"type": "string"},
                "properties": {"type": "object"},
            },
            "required": ["ticket_id", "properties"],
        }, self._update_ticket)

        self._register("hubspot_get_ticket", "Get a HubSpot ticket by ID.", {
            "type": "object",
            "properties": {"ticket_id": {"type": "string"}},
            "required": ["ticket_id"],
        }, self._get_ticket)

        self._register("hubspot_list_tickets", "List HubSpot tickets.", {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 50}},
        }, self._list_tickets)

        # ── Associations ──
        self._register("hubspot_create_association", "Associate two HubSpot objects (e.g. contact to deal).", {
            "type": "object",
            "properties": {
                "from_type": {"type": "string", "description": "e.g. contacts, deals, companies"},
                "from_id": {"type": "string"},
                "to_type": {"type": "string"},
                "to_id": {"type": "string"},
                "association_type": {"type": "string", "description": "e.g. contact_to_deal"},
            },
            "required": ["from_type", "from_id", "to_type", "to_id", "association_type"],
        }, self._create_association)

        # ── Pipelines ──
        self._register("hubspot_list_pipelines", "List deal or ticket pipelines.", {
            "type": "object",
            "properties": {
                "object_type": {"type": "string", "default": "deals", "description": "deals or tickets"},
            },
        }, self._list_pipelines)

        # ── Owners ──
        self._register("hubspot_list_owners", "List HubSpot owners (sales reps).", {
            "type": "object", "properties": {},
        }, self._list_owners)

    # ── Handlers ───────────────────────────────────────────────

    async def _create_contact(self, email: str, firstname: str = "", lastname: str = "",
                              phone: str = "", company: str = "") -> dict:
        props = {"email": email}
        if firstname: props["firstname"] = firstname
        if lastname: props["lastname"] = lastname
        if phone: props["phone"] = phone
        if company: props["company"] = company
        return await self.svc.create_contact(props)

    async def _update_contact(self, contact_id: str, properties: dict) -> dict:
        return await self.svc.update_contact(contact_id, properties)

    async def _get_contact(self, contact_id: str) -> dict:
        return await self.svc.get_contact(contact_id)

    async def _search_contacts(self, query: str, limit: int = 10) -> dict:
        results = await self.svc.search_contacts(query, limit)
        return {"contacts": results, "count": len(results)}

    async def _list_contacts(self, limit: int = 50) -> dict:
        results = await self.svc.list_contacts(limit)
        return {"contacts": results, "count": len(results)}

    async def _delete_contact(self, contact_id: str) -> dict:
        await self.svc.delete_contact(contact_id)
        return {"deleted": True, "contact_id": contact_id}

    async def _create_company(self, name: str, domain: str = "", industry: str = "", phone: str = "") -> dict:
        props = {"name": name}
        if domain: props["domain"] = domain
        if industry: props["industry"] = industry
        if phone: props["phone"] = phone
        return await self.svc.create_company(props)

    async def _update_company(self, company_id: str, properties: dict) -> dict:
        return await self.svc.update_company(company_id, properties)

    async def _get_company(self, company_id: str) -> dict:
        return await self.svc.get_company(company_id)

    async def _search_companies(self, query: str, limit: int = 10) -> dict:
        results = await self.svc.search_companies(query, limit)
        return {"companies": results, "count": len(results)}

    async def _create_deal(self, dealname: str, amount: str = "", dealstage: str = "",
                           pipeline: str = "", closedate: str = "") -> dict:
        props = {"dealname": dealname}
        if amount: props["amount"] = amount
        if dealstage: props["dealstage"] = dealstage
        if pipeline: props["pipeline"] = pipeline
        if closedate: props["closedate"] = closedate
        return await self.svc.create_deal(props)

    async def _update_deal(self, deal_id: str, properties: dict) -> dict:
        return await self.svc.update_deal(deal_id, properties)

    async def _get_deal(self, deal_id: str) -> dict:
        return await self.svc.get_deal(deal_id)

    async def _search_deals(self, query: str, limit: int = 10) -> dict:
        results = await self.svc.search_deals(query, limit)
        return {"deals": results, "count": len(results)}

    async def _list_deals(self, limit: int = 50) -> dict:
        results = await self.svc.list_deals(limit)
        return {"deals": results, "count": len(results)}

    async def _create_ticket(self, subject: str, content: str = "", hs_pipeline: str = "",
                             hs_pipeline_stage: str = "") -> dict:
        props = {"subject": subject}
        if content: props["content"] = content
        if hs_pipeline: props["hs_pipeline"] = hs_pipeline
        if hs_pipeline_stage: props["hs_pipeline_stage"] = hs_pipeline_stage
        return await self.svc.create_ticket(props)

    async def _update_ticket(self, ticket_id: str, properties: dict) -> dict:
        return await self.svc.update_ticket(ticket_id, properties)

    async def _get_ticket(self, ticket_id: str) -> dict:
        return await self.svc.get_ticket(ticket_id)

    async def _list_tickets(self, limit: int = 50) -> dict:
        results = await self.svc.list_tickets(limit)
        return {"tickets": results, "count": len(results)}

    async def _create_association(self, from_type: str, from_id: str, to_type: str,
                                  to_id: str, association_type: str) -> dict:
        await self.svc.create_association(from_type, from_id, to_type, to_id, association_type)
        return {"associated": True}

    async def _list_pipelines(self, object_type: str = "deals") -> dict:
        results = await self.svc.list_pipelines(object_type)
        return {"pipelines": results, "count": len(results)}

    async def _list_owners(self) -> dict:
        results = await self.svc.list_owners()
        return {"owners": results, "count": len(results)}

    async def close(self):
        await self.svc.close()
