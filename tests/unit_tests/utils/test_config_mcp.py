"""Tests for MCP-related Config methods."""

import tempfile

import pytest
import yaml

from connectchain.utils.config import Config


class TestConfigMCP:
    """Test cases for MCP configuration methods."""

    @pytest.fixture
    def config_with_mcp(self):
        """Create a config file with MCP settings."""
        config_data = {
            "mcp": {
                "servers": {
                    "math_tools": {
                        "command": "python",
                        "args": ["math_server.py"],
                        "transport": "stdio",
                    },
                    "web_tools": {"url": "https://example.com", "transport": "streamable-http"},
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config = Config(f.name)

        return config

    @pytest.fixture
    def config_without_mcp(self):
        """Create a config file without MCP settings."""
        config_data = {"models": {"1": {"provider": "openai", "type": "chat"}}}

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config = Config(f.name)

        return config

    def test_get_mcp_servers_with_servers(self, config_with_mcp):
        """Test getting MCP servers when they exist."""
        servers = config_with_mcp.mcp.servers

        assert len(servers.data) == 2
        assert "math_tools" in servers.data
        assert "web_tools" in servers.data
        assert servers.data["math_tools"]["command"] == "python"
        assert servers.data["web_tools"]["transport"] == "streamable-http"

    def test_get_mcp_servers_without_servers(self, config_without_mcp):
        """Test getting MCP servers when none exist."""
        try:
            servers = config_without_mcp.mcp.servers
            assert False, "Should have raised KeyError"
        except KeyError:
            # Expected behavior when mcp section doesn't exist
            pass

    def test_get_mcp_servers_partial_config(self):
        """Test getting MCP servers with partial config."""
        config_data = {
            "mcp": {
                # No servers key
            }
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config = Config(f.name)

        servers = config.mcp.servers
        assert servers is None
