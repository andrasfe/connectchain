"""Tests for MCPToolLoader."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from connectchain.utils.config import Config

# Skip tests if langchain-mcp-adapters not installed
pytest.importorskip("langchain_mcp_adapters")
from connectchain.tools.mcp.loader import MCPToolLoader


class TestMCPToolLoader:
    """Test cases for MCPToolLoader."""

    @pytest.fixture
    def mock_config(self):
        """Create mock config with MCP settings."""
        config = Mock(spec=Config)
        config.data = {
            "mcp": {
                "servers": {
                    "math_tools": {
                        "command": "python",
                        "args": ["math_server.py"],
                        "transport": "stdio",
                    },
                    "web_tools": {
                        "url": "https://example.com",
                        "transport": "streamable-http",
                        "auth": {"type": "bearer"},
                    },
                }
            }
        }
        config.proxy = "http://proxy.company.com:8080"
        config.eas = "https://eas.company.com"
        config.cert = "/path/to/cert.pem"
        return config

    @pytest.mark.asyncio
    async def test_load_all_tools(self, mock_config):
        """Test loading tools from all configured servers."""
        with patch("connectchain.tools.mcp.loader.MultiServerMCPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_tools = AsyncMock(
                return_value=[Mock(name="add"), Mock(name="multiply")]
            )
            mock_client_class.return_value = mock_client

            loader = MCPToolLoader(mock_config)
            tools = await loader.load_tools()

            assert len(tools) == 2
            assert mock_client_class.called
            assert mock_client.get_tools.called

    @pytest.mark.asyncio
    async def test_load_specific_tools(self, mock_config):
        """Test loading tools from specific servers."""
        with patch("connectchain.tools.mcp.loader.MultiServerMCPClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.get_tools = AsyncMock(return_value=[Mock(name="add")])
            mock_client_class.return_value = mock_client

            loader = MCPToolLoader(mock_config)
            tools = await loader.load_tools(["math_tools"])

            # Check that only math_tools was passed to client
            call_args = mock_client_class.call_args[0][0]
            assert "math_tools" in call_args
            assert "web_tools" not in call_args


    @pytest.mark.asyncio
    async def test_no_servers_configured(self):
        """Test behavior when no MCP servers are configured."""
        config = Mock(spec=Config)
        config.data = {}

        loader = MCPToolLoader(config)
        tools = await loader.load_tools()

        assert tools == []

    @pytest.mark.asyncio
    async def test_close(self, mock_config):
        """Test cleanup of MCP client."""
        loader = MCPToolLoader(mock_config)
        loader.client = Mock()

        await loader.close()
        assert loader.client is None
