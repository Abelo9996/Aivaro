"""
MCP Servers for Aivaro integrations.

Each server wraps an existing integration service class and exposes
its methods as MCP-compatible tools with proper JSON schemas.

Can be used:
1. In-process via MCPToolRegistry (direct Python calls, no transport overhead)
2. Via MCP stdio/SSE transport for external MCP clients (future)
"""
