"""
MCP Tool Registry — Central dispatcher for all MCP integration servers.

Creates MCP servers based on user's active connections and routes tool calls.
"""
import logging
from typing import Any, Optional
from sqlalchemy.orm import Session

from app.mcp_servers.base import BaseMCPServer

logger = logging.getLogger(__name__)


# Maps connection provider names to (ServerClass, credential_extractor) tuples
def _google_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.google_server import GoogleMCPServer
    return GoogleMCPServer(
        access_token=creds.get("access_token", ""),
        refresh_token=creds.get("refresh_token", ""),
    )


def _slack_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.slack_server import SlackMCPServer
    return SlackMCPServer(access_token=creds.get("access_token", ""))


def _stripe_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.stripe_server import StripeMCPServer
    api_key = creds.get("api_key") or creds.get("access_token", "")
    return StripeMCPServer(api_key=api_key)


def _twilio_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.twilio_server import TwilioMCPServer
    return TwilioMCPServer(
        account_sid=creds.get("account_sid", ""),
        auth_token=creds.get("auth_token", ""),
        phone_number=creds.get("phone_number"),
    )


def _airtable_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.airtable_server import AirtableMCPServer
    return AirtableMCPServer(access_token=creds.get("access_token", ""))


def _notion_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.notion_server import NotionMCPServer
    return NotionMCPServer(access_token=creds.get("access_token", ""))


def _calendly_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.calendly_server import CalendlyMCPServer
    return CalendlyMCPServer(access_token=creds.get("access_token", ""))


def _mailchimp_factory(creds: dict) -> BaseMCPServer:
    from app.mcp_servers.mailchimp_server import MailchimpMCPServer
    return MailchimpMCPServer(access_token=creds.get("access_token", ""))


SERVER_FACTORIES = {
    "google": _google_factory,
    "slack": _slack_factory,
    "stripe": _stripe_factory,
    "twilio": _twilio_factory,
    "airtable": _airtable_factory,
    "notion": _notion_factory,
    "calendly": _calendly_factory,
    "mailchimp": _mailchimp_factory,
}


class MCPToolRegistry:
    """
    Manages MCP servers for a user's active connections.
    
    Usage:
        registry = MCPToolRegistry(connections)
        tools = registry.list_all_tools()           # OpenAI function format
        result = await registry.call_tool("send_email", {...})
    """

    def __init__(self, connections: dict):
        self.servers: dict[str, BaseMCPServer] = {}
        self._tool_to_server: dict[str, BaseMCPServer] = {}
        self._init_servers(connections)

    def _init_servers(self, connections: dict):
        """Spin up MCP servers for each active connection."""
        for provider, creds in connections.items():
            factory = SERVER_FACTORIES.get(provider)
            if factory and creds:
                try:
                    server = factory(creds)
                    self.servers[provider] = server
                    # Build tool→server index for fast routing
                    for tool_name in server.list_tool_names():
                        self._tool_to_server[tool_name] = server
                    logger.info(f"[MCP] Initialized {provider} server with {len(server.list_tool_names())} tools")
                except Exception as e:
                    logger.error(f"[MCP] Failed to initialize {provider} server: {e}")

    def list_all_tools(self) -> list[dict]:
        """Return all available tools in OpenAI function-calling format."""
        tools = []
        for server in self.servers.values():
            tools.extend(server.list_tools())
        return tools

    def list_all_tool_names(self) -> list[str]:
        """Return flat list of all tool names."""
        return list(self._tool_to_server.keys())

    def get_provider_for_tool(self, tool_name: str) -> Optional[str]:
        """Return the provider name for a tool."""
        server = self._tool_to_server.get(tool_name)
        return server.provider if server else None

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._tool_to_server

    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Route a tool call to the correct MCP server."""
        server = self._tool_to_server.get(tool_name)
        if not server:
            return {"error": f"Unknown tool: {tool_name}. Available: {self.list_all_tool_names()}"}
        return await server.call_tool(tool_name, arguments)

    def get_tools_for_provider(self, provider: str) -> list[dict]:
        """Get tools for a specific provider."""
        server = self.servers.get(provider)
        return server.list_tools() if server else []

    @property
    def connected_providers(self) -> list[str]:
        return list(self.servers.keys())

    async def close(self):
        """Cleanup all servers."""
        for server in self.servers.values():
            try:
                await server.close()
            except Exception:
                pass
