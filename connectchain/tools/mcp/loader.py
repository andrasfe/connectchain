"""MCP tool loader."""

from typing import List, Optional, cast

from langchain.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from ...utils.config import Config


class MCPToolLoader:
    """Load MCP tools from configured servers."""

    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[MultiServerMCPClient] = None

    async def load_tools(self, server_names: Optional[List[str]] = None) -> List[BaseTool]:
        """Load tools from MCP servers configured in the YAML file."""
        mcp_config = self.config.data.get("mcp", {})
        servers = mcp_config.get("servers", {})

        if not servers:
            return []

        # Filter servers if specific names requested
        if server_names:
            servers = {k: v for k, v in servers.items() if k in server_names}

        # Pass server configs directly to MultiServerMCPClient
        self.client = MultiServerMCPClient(servers)
        tools = await self.client.get_tools()
        return cast(List[BaseTool], tools)

    async def close(self) -> None:
        """Clean up MCP client connections."""
        if self.client:
            self.client = None
