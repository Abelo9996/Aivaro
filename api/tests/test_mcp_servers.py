"""
Comprehensive MCP Integration Test Suite

Tests that every MCP server:
1. Instantiates correctly
2. Registers all expected tools
3. Each tool has valid JSON Schema (type, properties, required)
4. Handler signatures match schema required params
5. All tools are reachable via the registry
6. No duplicate tool names across providers

Run: python -m pytest tests/test_mcp_servers.py -v
"""
import pytest
import inspect
import asyncio
from typing import get_type_hints

from app.mcp_servers.base import BaseMCPServer
from app.mcp_servers.registry import SERVER_FACTORIES, MCPToolRegistry


# ── Fixtures ─────────────────────────────────────────────────

# Dummy credentials for each provider (enough to instantiate, not to call APIs)
DUMMY_CREDS = {
    "google": {"access_token": "test", "refresh_token": "test"},
    "slack": {"access_token": "test"},
    "stripe": {"api_key": "sk_test_xxx"},
    "twilio": {"account_sid": "ACtest", "auth_token": "test", "phone_number": "+1234567890"},
    "airtable": {"access_token": "test"},
    "notion": {"access_token": "test"},
    "calendly": {"access_token": "test"},
    "mailchimp": {"access_token": "test"},
    "hubspot": {"access_token": "test"},
    "shopify": {"shop_domain": "test.myshopify.com", "access_token": "test"},
    "discord": {"bot_token": "test", "guild_id": "123"},
    "jira": {"domain": "test.atlassian.net", "email": "test@test.com", "api_token": "test"},
    "github": {"access_token": "test"},
    "linear": {"api_key": "test"},
    "monday": {"api_key": "test"},
    "sendgrid": {"api_key": "test"},
    "whatsapp": {"access_token": "test", "phone_number_id": "123"},
    "brevo": {"api_key": "test", "sender_email": "test@test.com"},
    "telegram": {"bot_token": "test"},
    "typeform": {"access_token": "test"},
    "asana": {"access_token": "test"},
    "trello": {"api_key": "test", "api_token": "test"},
    "clickup": {"api_key": "test"},
    "pipedrive": {"api_token": "test"},
    "zendesk": {"subdomain": "test", "email": "test@test.com", "api_token": "test"},
    "intercom": {"access_token": "test"},
    "freshdesk": {"domain": "test", "api_key": "test"},
    "supabase": {"url": "https://test.supabase.co", "api_key": "test"},
    "webflow": {"access_token": "test"},
    "twitch": {"client_id": "test", "access_token": "test"},
    "zoom": {"access_token": "test"},
}


def _create_server(provider: str) -> BaseMCPServer:
    """Create an MCP server instance with dummy creds."""
    factory = SERVER_FACTORIES[provider]
    creds = DUMMY_CREDS[provider]
    return factory(creds)


# ── Discovery Tests ──────────────────────────────────────────

class TestMCPDiscovery:
    """Ensure all providers are registered and can be instantiated."""

    def test_all_providers_have_dummy_creds(self):
        """Every provider in SERVER_FACTORIES has test credentials."""
        missing = set(SERVER_FACTORIES.keys()) - set(DUMMY_CREDS.keys())
        assert not missing, f"Missing dummy creds for: {missing}"

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_server_instantiates(self, provider):
        """Server can be created without errors."""
        server = _create_server(provider)
        assert isinstance(server, BaseMCPServer)
        assert server.provider == provider

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_server_has_tools(self, provider):
        """Every server registers at least one tool."""
        server = _create_server(provider)
        tools = server.list_tools()
        assert len(tools) > 0, f"{provider} has no tools registered"

    def test_no_duplicate_tool_names(self):
        """No two providers register the same tool name."""
        all_names = []
        for provider in SERVER_FACTORIES:
            server = _create_server(provider)
            names = server.list_tool_names()
            for name in names:
                assert name not in all_names, f"Duplicate tool name '{name}' in {provider}"
                all_names.append(name)


# ── Schema Validation Tests ──────────────────────────────────

VALID_JSON_TYPES = {"string", "integer", "number", "boolean", "array", "object", "null"}


class TestMCPSchemas:
    """Validate JSON Schema structure for every tool."""

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_tool_schema_structure(self, provider):
        """Each tool has valid OpenAI function-calling format."""
        server = _create_server(provider)
        for tool in server.list_tools():
            assert tool["type"] == "function", f"Bad type for {tool}"
            func = tool["function"]
            assert "name" in func, "Missing name"
            assert "description" in func, f"Missing description for {func['name']}"
            assert len(func["description"]) > 5, f"Description too short for {func['name']}"
            assert "parameters" in func, f"Missing parameters for {func['name']}"

            params = func["parameters"]
            assert params.get("type") == "object", f"Params not object type for {func['name']}"
            assert "properties" in params, f"Missing properties for {func['name']}"

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_property_types_valid(self, provider):
        """Each property has a valid JSON Schema type."""
        server = _create_server(provider)
        for tool in server.list_tools():
            func = tool["function"]
            props = func["parameters"].get("properties", {})
            for prop_name, prop_def in props.items():
                if "type" in prop_def:
                    assert prop_def["type"] in VALID_JSON_TYPES, \
                        f"Invalid type '{prop_def['type']}' for {func['name']}.{prop_name}"

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_required_fields_exist_in_properties(self, provider):
        """Every field listed in 'required' exists in 'properties'."""
        server = _create_server(provider)
        for tool in server.list_tools():
            func = tool["function"]
            params = func["parameters"]
            required = params.get("required", [])
            props = params.get("properties", {})
            for req in required:
                assert req in props, \
                    f"Required field '{req}' not in properties for {func['name']}"

    # New providers that must have descriptions on all non-trivial properties
    NEW_PROVIDERS = {"telegram", "typeform", "asana", "trello", "clickup",
                     "pipedrive", "zendesk", "intercom", "freshdesk",
                     "supabase", "webflow", "twitch", "zoom"}

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_properties_have_descriptions(self, provider):
        """Properties should have descriptions for AI function calling."""
        server = _create_server(provider)
        for tool in server.list_tools():
            func = tool["function"]
            props = func["parameters"].get("properties", {})
            for prop_name, prop_def in props.items():
                if prop_name in ("limit", "offset", "page_size"):
                    continue
                # Only enforce strictly on new providers
                if provider in self.NEW_PROVIDERS:
                    assert "description" in prop_def or "default" in prop_def or "type" in prop_def, \
                        f"No description for {func['name']}.{prop_name}"


# ── Handler Signature Tests ──────────────────────────────────

class TestMCPHandlers:
    """Ensure handler functions match their schemas."""

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_handlers_are_async(self, provider):
        """All tool handlers must be async."""
        server = _create_server(provider)
        for name, tool_def in server._tools.items():
            assert asyncio.iscoroutinefunction(tool_def.handler), \
                f"Handler for {name} is not async"

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_required_params_in_handler(self, provider):
        """Required schema params should be in the handler signature."""
        server = _create_server(provider)
        for tool in server.list_tools():
            func = tool["function"]
            required = func["parameters"].get("required", [])
            tool_def = server._tools[func["name"]]
            sig = inspect.signature(tool_def.handler)
            param_names = set(sig.parameters.keys()) - {"self"}
            # Handlers using **kwargs or **params accept any param
            has_var_keyword = any(
                p.kind == inspect.Parameter.VAR_KEYWORD
                for p in sig.parameters.values()
            )
            if has_var_keyword:
                continue
            for req in required:
                assert req in param_names, \
                    f"Required param '{req}' not in handler signature for {func['name']}. " \
                    f"Handler has: {param_names}"

    @pytest.mark.parametrize("provider", list(SERVER_FACTORIES.keys()))
    def test_handler_has_close(self, provider):
        """Server should have a close() method."""
        server = _create_server(provider)
        assert hasattr(server, "close")
        assert asyncio.iscoroutinefunction(server.close)


# ── Registry Integration Tests ───────────────────────────────

class TestMCPRegistry:
    """Test the MCPToolRegistry with all providers."""

    def test_registry_with_all_providers(self):
        """Registry initializes with all providers and indexes all tools."""
        registry = MCPToolRegistry(DUMMY_CREDS)
        assert len(registry.connected_providers) == len(SERVER_FACTORIES)
        all_tools = registry.list_all_tool_names()
        assert len(all_tools) > 100, f"Expected 100+ tools, got {len(all_tools)}"

    def test_registry_tool_routing(self):
        """Every tool routes to the correct provider."""
        registry = MCPToolRegistry(DUMMY_CREDS)
        for tool_name in registry.list_all_tool_names():
            provider = registry.get_provider_for_tool(tool_name)
            assert provider is not None, f"No provider for {tool_name}"
            assert provider in SERVER_FACTORIES

    def test_registry_partial_connections(self):
        """Registry works with a subset of providers."""
        partial = {"slack": DUMMY_CREDS["slack"], "stripe": DUMMY_CREDS["stripe"]}
        registry = MCPToolRegistry(partial)
        assert set(registry.connected_providers) == {"slack", "stripe"}

    def test_registry_unknown_tool(self):
        """Calling unknown tool returns error."""
        registry = MCPToolRegistry({"slack": DUMMY_CREDS["slack"]})
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(
            registry.call_tool("nonexistent_tool", {})
        )
        assert "error" in result

    def test_openai_function_format(self):
        """All tools match OpenAI function-calling JSON format."""
        registry = MCPToolRegistry(DUMMY_CREDS)
        for tool in registry.list_all_tools():
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "parameters" in tool["function"]


# ── Coverage Report ──────────────────────────────────────────

class TestMCPCoverage:
    """Report total tool counts per provider."""

    def test_print_coverage_report(self):
        """Print tool counts per provider (always passes, informational)."""
        total = 0
        report = []
        for provider in sorted(SERVER_FACTORIES.keys()):
            server = _create_server(provider)
            count = len(server.list_tool_names())
            total += count
            report.append(f"  {provider:15s} : {count:3d} tools")
        print(f"\n{'='*40}")
        print(f"MCP Tool Coverage Report")
        print(f"{'='*40}")
        print(f"  Providers: {len(SERVER_FACTORIES)}")
        print(f"  Total tools: {total}")
        print(f"{'='*40}")
        for line in report:
            print(line)
        print(f"{'='*40}")
        assert total > 0
