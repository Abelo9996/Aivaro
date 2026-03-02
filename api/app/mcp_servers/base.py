"""
Base MCP server wrapper for Aivaro integrations.

Provides a lightweight in-process tool registry that's MCP-compatible
without requiring transport overhead for internal use.
"""
import json
import logging
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


class ToolDef:
    """A tool definition with schema and handler."""
    __slots__ = ("name", "description", "input_schema", "handler")

    def __init__(self, name: str, description: str, input_schema: dict, handler: Callable[..., Awaitable[dict]]):
        self.name = name
        self.description = description
        self.input_schema = input_schema
        self.handler = handler


class BaseMCPServer:
    """
    Base class for Aivaro MCP integration servers.

    Subclasses register tools in __init__ via self._register().
    The registry (MCPToolRegistry) calls list_tools() and call_tool().
    """

    provider: str = "unknown"  # e.g. "google", "slack", "stripe"

    def __init__(self):
        self._tools: dict[str, ToolDef] = {}

    def _register(self, name: str, description: str, input_schema: dict, handler: Callable[..., Awaitable[dict]]):
        """Register a tool."""
        self._tools[name] = ToolDef(name, description, input_schema, handler)

    def list_tools(self) -> list[dict]:
        """Return tool definitions in OpenAI-compatible format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.input_schema,
                },
            }
            for t in self._tools.values()
        ]

    def list_tool_names(self) -> list[str]:
        return list(self._tools.keys())

    async def call_tool(self, name: str, arguments: dict) -> dict:
        """Execute a tool by name. Returns dict with result or error."""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Unknown tool: {name}"}
        try:
            result = await tool.handler(**arguments)
            return result
        except TypeError as e:
            logger.error(f"[MCP:{self.provider}] Tool {name} param error: {e}")
            return {"error": f"Invalid parameters for {name}: {e}"}
        except Exception as e:
            logger.error(f"[MCP:{self.provider}] Tool {name} failed: {e}", exc_info=True)
            return {"error": str(e)}

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    async def close(self):
        """Cleanup resources."""
        pass
