"""
Comprehensive MCP Server test suite.

Tests every integration's:
1. Server instantiation (no crash on init)
2. Tool registration (all tools have valid schemas)
3. JSON Schema completeness (type, properties, required fields)
4. Handler signatures match schema parameters
5. Tool name uniqueness across all servers
6. BaseMCPServer interface compliance
"""
import pytest
import inspect
import json
from typing import get_type_hints

from app.mcp_servers.base import BaseMCPServer

# ── Server imports & factory configs ──────────────────────────

SERVERS = {
    "google": {
        "module": "app.mcp_servers.google_server",
        "class": "GoogleMCPServer",
        "kwargs": {"access_token": "test-token", "refresh_token": "test-refresh"},
    },
    "slack": {
        "module": "app.mcp_servers.slack_server",
        "class": "SlackMCPServer",
        "kwargs": {"access_token": "xoxb-test"},
    },
    "stripe": {
        "module": "app.mcp_servers.stripe_server",
        "class": "StripeMCPServer",
        "kwargs": {"api_key": "sk_test_fake"},
    },
    "twilio": {
        "module": "app.mcp_servers.twilio_server",
        "class": "TwilioMCPServer",
        "kwargs": {"account_sid": "AC_test", "auth_token": "test", "phone_number": "+1234567890"},
    },
    "airtable": {
        "module": "app.mcp_servers.airtable_server",
        "class": "AirtableMCPServer",
        "kwargs": {"access_token": "pat_test"},
    },
    "notion": {
        "module": "app.mcp_servers.notion_server",
        "class": "NotionMCPServer",
        "kwargs": {"access_token": "secret_test"},
    },
    "calendly": {
        "module": "app.mcp_servers.calendly_server",
        "class": "CalendlyMCPServer",
        "kwargs": {"access_token": "test-token"},
    },
    "mailchimp": {
        "module": "app.mcp_servers.mailchimp_server",
        "class": "MailchimpMCPServer",
        "kwargs": {"access_token": "test-us21"},
    },
    "hubspot": {
        "module": "app.mcp_servers.hubspot_server",
        "class": "HubSpotMCPServer",
        "kwargs": {"access_token": "pat-test"},
    },
    "shopify": {
        "module": "app.mcp_servers.shopify_server",
        "class": "ShopifyMCPServer",
        "kwargs": {"shop_domain": "test.myshopify.com", "access_token": "shpat_test"},
    },
    "discord": {
        "module": "app.mcp_servers.discord_server",
        "class": "DiscordMCPServer",
        "kwargs": {"bot_token": "test-bot-token", "guild_id": "123456"},
    },
    "jira": {
        "module": "app.mcp_servers.jira_server",
        "class": "JiraMCPServer",
        "kwargs": {"domain": "test.atlassian.net", "email": "test@test.com", "api_token": "test"},
    },
    "github": {
        "module": "app.mcp_servers.github_server",
        "class": "GitHubMCPServer",
        "kwargs": {"access_token": "ghp_test"},
    },
    "linear": {
        "module": "app.mcp_servers.linear_server",
        "class": "LinearMCPServer",
        "kwargs": {"api_key": "lin_api_test"},
    },
    "monday": {
        "module": "app.mcp_servers.monday_server",
        "class": "MondayMCPServer",
        "kwargs": {"api_key": "test-key"},
    },
    "sendgrid": {
        "module": "app.mcp_servers.sendgrid_server",
        "class": "SendGridMCPServer",
        "kwargs": {"api_key": "SG.test"},
    },
    "whatsapp": {
        "module": "app.mcp_servers.whatsapp_server",
        "class": "WhatsAppMCPServer",
        "kwargs": {"access_token": "test", "phone_number_id": "123"},
    },
    "brevo": {
        "module": "app.mcp_servers.brevo",
        "class": "BrevoMCPServer",
        "kwargs": {"creds": {"api_key": "xkeysib-test", "sender_email": "test@test.com"}},
        "factory_style": True,
    },
    "telegram": {
        "module": "app.mcp_servers.telegram_server",
        "class": "TelegramMCPServer",
        "kwargs": {"bot_token": "123:ABC-test"},
    },
    "typeform": {
        "module": "app.mcp_servers.typeform_server",
        "class": "TypeformMCPServer",
        "kwargs": {"access_token": "tfp_test"},
    },
    "asana": {
        "module": "app.mcp_servers.asana_server",
        "class": "AsanaMCPServer",
        "kwargs": {"access_token": "test-pat"},
    },
    "trello": {
        "module": "app.mcp_servers.trello_server",
        "class": "TrelloMCPServer",
        "kwargs": {"api_key": "test-key", "api_token": "test-token"},
    },
    "clickup": {
        "module": "app.mcp_servers.clickup_server",
        "class": "ClickUpMCPServer",
        "kwargs": {"api_key": "pk_test"},
    },
    "pipedrive": {
        "module": "app.mcp_servers.pipedrive_server",
        "class": "PipedriveMCPServer",
        "kwargs": {"api_token": "test-token"},
    },
    "zendesk": {
        "module": "app.mcp_servers.zendesk_server",
        "class": "ZendeskMCPServer",
        "kwargs": {"subdomain": "test", "email": "test@test.com", "api_token": "test"},
    },
    "intercom": {
        "module": "app.mcp_servers.intercom_server",
        "class": "IntercomMCPServer",
        "kwargs": {"access_token": "test-token"},
    },
    "freshdesk": {
        "module": "app.mcp_servers.freshdesk_server",
        "class": "FreshdeskMCPServer",
        "kwargs": {"domain": "testco", "api_key": "test-key"},
    },
    "supabase": {
        "module": "app.mcp_servers.supabase_server",
        "class": "SupabaseMCPServer",
        "kwargs": {"url": "https://test.supabase.co", "api_key": "test-anon-key"},
    },
    "webflow": {
        "module": "app.mcp_servers.webflow_server",
        "class": "WebflowMCPServer",
        "kwargs": {"access_token": "test-token"},
    },
    "twitch": {
        "module": "app.mcp_servers.twitch_server",
        "class": "TwitchMCPServer",
        "kwargs": {"client_id": "test-id", "access_token": "test-token"},
    },
    "zoom": {
        "module": "app.mcp_servers.zoom_server",
        "class": "ZoomMCPServer",
        "kwargs": {"access_token": "test-token"},
    },
}

VALID_JSON_SCHEMA_TYPES = {"string", "integer", "number", "boolean", "array", "object", "null"}


def _create_server(config: dict) -> BaseMCPServer:
    """Import and instantiate a server from config."""
    import importlib
    mod = importlib.import_module(config["module"])
    cls = getattr(mod, config["class"])
    if config.get("factory_style"):
        return cls(config["kwargs"]["creds"])
    return cls(**config["kwargs"])


# ── Fixtures ──────────────────────────────────────────────────

@pytest.fixture(params=list(SERVERS.keys()), ids=list(SERVERS.keys()))
def server_config(request):
    return request.param, SERVERS[request.param]


@pytest.fixture
def server(server_config):
    name, config = server_config
    return _create_server(config)


# ── Tests ─────────────────────────────────────────────────────

class TestServerInstantiation:
    """Test that all servers can be created without errors."""

    def test_creates_without_error(self, server):
        assert server is not None

    def test_is_base_mcp_server(self, server):
        assert isinstance(server, BaseMCPServer)

    def test_has_provider(self, server):
        assert hasattr(server, "provider")
        assert isinstance(server.provider, str)
        assert len(server.provider) > 0

    def test_has_tools(self, server):
        tools = server.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0, f"{server.provider} has no tools registered"


class TestToolRegistration:
    """Test that all tools have valid schemas and handlers."""

    def test_tool_format(self, server):
        """Every tool must be in OpenAI function format."""
        for tool in server.list_tools():
            assert tool["type"] == "function", f"Tool type must be 'function'"
            func = tool["function"]
            assert "name" in func, "Tool missing 'name'"
            assert "description" in func, f"Tool {func.get('name')} missing 'description'"
            assert "parameters" in func, f"Tool {func.get('name')} missing 'parameters'"
            assert len(func["description"]) > 0, f"Tool {func['name']} has empty description"

    def test_tool_names_are_strings(self, server):
        for name in server.list_tool_names():
            assert isinstance(name, str)
            assert len(name) > 0

    def test_tool_names_match_list(self, server):
        """list_tools() and list_tool_names() must be consistent."""
        names_from_tools = {t["function"]["name"] for t in server.list_tools()}
        names_from_list = set(server.list_tool_names())
        assert names_from_tools == names_from_list

    def test_has_tool_consistency(self, server):
        """has_tool() must agree with list_tool_names()."""
        for name in server.list_tool_names():
            assert server.has_tool(name), f"has_tool('{name}') returned False"
        assert not server.has_tool("__nonexistent_tool__")


class TestJSONSchemas:
    """Test that every tool's input_schema is valid JSON Schema."""

    def test_schema_is_object_type(self, server):
        for tool in server.list_tools():
            schema = tool["function"]["parameters"]
            name = tool["function"]["name"]
            assert schema.get("type") == "object", f"{name}: schema type must be 'object', got {schema.get('type')}"

    def test_schema_has_properties(self, server):
        for tool in server.list_tools():
            schema = tool["function"]["parameters"]
            name = tool["function"]["name"]
            assert "properties" in schema, f"{name}: schema missing 'properties'"
            assert isinstance(schema["properties"], dict), f"{name}: properties must be dict"

    def test_property_types_are_valid(self, server):
        for tool in server.list_tools():
            schema = tool["function"]["parameters"]
            name = tool["function"]["name"]
            for prop_name, prop_def in schema["properties"].items():
                if "type" in prop_def:
                    assert prop_def["type"] in VALID_JSON_SCHEMA_TYPES, \
                        f"{name}.{prop_name}: invalid type '{prop_def['type']}'"

    def test_required_fields_exist_in_properties(self, server):
        for tool in server.list_tools():
            schema = tool["function"]["parameters"]
            name = tool["function"]["name"]
            required = schema.get("required", [])
            props = set(schema["properties"].keys())
            for req in required:
                assert req in props, f"{name}: required field '{req}' not in properties"

    def test_properties_have_descriptions(self, server):
        """Every property should have a description (warning-level, not hard fail for now)."""
        warnings = []
        for tool in server.list_tools():
            schema = tool["function"]["parameters"]
            name = tool["function"]["name"]
            for prop_name, prop_def in schema["properties"].items():
                if "description" not in prop_def and "default" not in prop_def:
                    warnings.append(f"{name}.{prop_name}")
        # Soft check — print warnings but don't fail
        if warnings:
            print(f"\n[WARN] {server.provider}: Properties without descriptions: {warnings}")


class TestHandlerSignatures:
    """Test that handler signatures accept the schema's required params."""

    def test_required_params_in_handler(self, server):
        """Every required schema param must be accepted by the handler."""
        for tool_def in server._tools.values():
            schema = tool_def.input_schema
            handler = tool_def.handler
            sig = inspect.signature(handler)
            handler_params = set(sig.parameters.keys()) - {"self", "kwargs"}

            required = set(schema.get("required", []))
            schema_params = set(schema.get("properties", {}).keys())

            # Required params must exist in handler (or handler must accept **kwargs)
            has_kwargs = any(
                p.kind == inspect.Parameter.VAR_KEYWORD
                for p in sig.parameters.values()
            )
            if not has_kwargs:
                missing = required - handler_params
                assert not missing, \
                    f"{tool_def.name}: required params {missing} not in handler signature {handler_params}"

    def test_handler_is_async(self, server):
        """All handlers must be async."""
        for tool_def in server._tools.values():
            assert inspect.iscoroutinefunction(tool_def.handler), \
                f"{tool_def.name}: handler must be async"


class TestGlobalUniqueness:
    """Test tool name uniqueness across ALL servers."""

    def test_no_duplicate_tool_names_within_server(self):
        """Each server's tools must have unique names."""
        for provider, config in SERVERS.items():
            server = _create_server(config)
            names = server.list_tool_names()
            dupes = [n for n in names if names.count(n) > 1]
            assert not dupes, f"{provider}: duplicate tool names: {set(dupes)}"

    def test_no_cross_server_collisions(self):
        """Tool names must not collide across different providers."""
        seen = {}  # tool_name -> provider
        collisions = []
        for provider, config in SERVERS.items():
            server = _create_server(config)
            for name in server.list_tool_names():
                if name in seen:
                    collisions.append(f"'{name}' in both {seen[name]} and {provider}")
                seen[name] = provider
        assert not collisions, f"Tool name collisions: {collisions}"


class TestToolCounts:
    """Verify minimum expected tool counts per provider."""

    EXPECTED_MIN_TOOLS = {
        "google": 10, "slack": 8, "stripe": 6, "twilio": 6,
        "airtable": 6, "notion": 8, "calendly": 5, "mailchimp": 10,
        "hubspot": 15, "shopify": 12, "discord": 10, "jira": 8,
        "github": 10, "linear": 7, "monday": 6, "sendgrid": 5,
        "whatsapp": 3, "brevo": 10,
        # New integrations
        "telegram": 7, "typeform": 4, "asana": 7, "trello": 8,
        "clickup": 9, "pipedrive": 9, "zendesk": 7, "intercom": 8,
        "freshdesk": 7, "supabase": 5, "webflow": 6, "twitch": 6,
        "zoom": 6,
    }

    def test_minimum_tool_count(self):
        for provider, config in SERVERS.items():
            server = _create_server(config)
            count = len(server.list_tool_names())
            expected = self.EXPECTED_MIN_TOOLS.get(provider, 1)
            assert count >= expected, \
                f"{provider}: expected >= {expected} tools, got {count}. Tools: {server.list_tool_names()}"


class TestRegistryIntegration:
    """Test that the MCPToolRegistry works with all providers."""

    def test_registry_creates_all_servers(self):
        from app.mcp_servers.registry import MCPToolRegistry
        # Simulate connections dict with test creds
        connections = {}
        for provider, config in SERVERS.items():
            if config.get("factory_style"):
                connections[provider] = config["kwargs"]["creds"]
            else:
                connections[provider] = config["kwargs"]

        registry = MCPToolRegistry(connections)

        # All providers should be initialized
        assert len(registry.connected_providers) == len(SERVERS), \
            f"Expected {len(SERVERS)} providers, got {len(registry.connected_providers)}. " \
            f"Missing: {set(SERVERS.keys()) - set(registry.connected_providers)}"

    def test_registry_tool_routing(self):
        from app.mcp_servers.registry import MCPToolRegistry
        connections = {}
        for provider, config in SERVERS.items():
            if config.get("factory_style"):
                connections[provider] = config["kwargs"]["creds"]
            else:
                connections[provider] = config["kwargs"]

        registry = MCPToolRegistry(connections)

        # Every tool should route to its provider
        for provider in registry.connected_providers:
            tools = registry.get_tools_for_provider(provider)
            for tool in tools:
                name = tool["function"]["name"]
                assert registry.has_tool(name), f"Registry missing tool {name}"
                assert registry.get_provider_for_tool(name) == provider

    def test_total_tool_count(self):
        from app.mcp_servers.registry import MCPToolRegistry
        connections = {}
        for provider, config in SERVERS.items():
            if config.get("factory_style"):
                connections[provider] = config["kwargs"]["creds"]
            else:
                connections[provider] = config["kwargs"]

        registry = MCPToolRegistry(connections)
        total = len(registry.list_all_tool_names())
        print(f"\n[INFO] Total tools across all {len(SERVERS)} providers: {total}")
        # We had 212 before adding 13 new providers. Each adds 5-10 tools.
        assert total >= 300, f"Expected >= 300 total tools, got {total}"
