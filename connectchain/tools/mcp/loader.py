"""Load MCP tools from configured servers."""

import logging
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
        # Get servers from config
        servers = self.config.get_mcp_servers()

        if not servers:
            logging.getLogger(__name__).warning(
                "No servers found for tool loading. Check MCP configuration."
            )
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
