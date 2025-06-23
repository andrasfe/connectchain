"""MCP tool loader with enterprise configuration support."""

from typing import Any, Dict, List, Optional, cast

from langchain.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

from ...utils.config import Config


class MCPToolLoader:
    """Load MCP tools from configured servers with enterprise settings."""

    def __init__(self, config: Config):
        self.config = config
        self.client: Optional[MultiServerMCPClient] = None

    async def load_tools(self, server_names: Optional[List[str]] = None) -> List[BaseTool]:
        """Load tools from specified MCP servers or all configured servers."""
        mcp_config = self.config.data.get("mcp", {})
        servers = mcp_config.get("servers", {})

        if not servers:
            # No MCP servers configured
            return []

        # Filter servers if specific names requested
        if server_names:
            servers = {k: v for k, v in servers.items() if k in server_names}

        # Apply enterprise settings to each server
        server_configs = {}
        for name, server_config in servers.items():
            server_configs[name] = self._apply_enterprise_settings(name, server_config)

        # Initialize client and get tools
        self.client = MultiServerMCPClient(server_configs)
        tools = await self.client.get_tools()
        # Loaded tools from MCP servers
        return cast(List[BaseTool], tools)

    def _apply_enterprise_settings(
        self, name: str, server_config: Dict[str, Any]  # pylint: disable=unused-argument
    ) -> Dict[str, Any]:
        """Apply proxy, auth, and cert settings from main config."""
        config = server_config.copy()

        # Apply proxy if configured
        if self.config.proxy and "env" not in config:
            config["env"] = config.get("env", {})
            config["env"]["HTTP_PROXY"] = self.config.proxy
            config["env"]["HTTPS_PROXY"] = self.config.proxy

        # Apply auth token if EAS is configured
        if self.config.eas and server_config.get("auth", {}).get("type") == "bearer":
            # Token would be fetched from SessionMap in real usage
            config["env"] = config.get("env", {})
            config["env"]["MCP_AUTH_TOKEN"] = "${EAS_TOKEN}"

        # Apply cert if configured
        if self.config.cert and server_config.get("transport") == "streamable-http":
            config["env"] = config.get("env", {})
            config["env"]["SSL_CERT_FILE"] = self.config.cert

        return config

    async def close(self) -> None:
        """Clean up MCP client connections."""
        if self.client:
            # MultiServerMCPClient handles cleanup internally
            self.client = None
