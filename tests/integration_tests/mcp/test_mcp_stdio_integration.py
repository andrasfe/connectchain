"""Integration test for MCP stdio communication."""

import asyncio
import sys
from pathlib import Path

import pytest

# Add parent directory to path to import connectchain
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from connectchain.utils.config import Config
from connectchain.tools.mcp.loader import MCPToolLoader


@pytest.mark.asyncio
async def test_mcp_stdio_integration():
    """Test MCP integration with a mock server via stdio."""
    # Use config file in the same directory
    config_path = Path(__file__).parent / 'test_config.yaml'
    
    # Load config
    config = Config(str(config_path))
    
    # Update the command and args with actual paths
    config.data['mcp']['servers']['mock_server']['command'] = sys.executable
    config.data['mcp']['servers']['mock_server']['args'] = [
        str(Path(__file__).parent / 'mock_mcp_server.py')
    ]
    
    # Initialize MCP loader
    mcp_loader = MCPToolLoader(config)
    
    # Load tools from mock server
    tools = await mcp_loader.load_tools(['mock_server'])
    
    # Verify we got the expected tool
    assert len(tools) == 1
    assert tools[0].name == "add_numbers"
    assert tools[0].description == "Add two numbers together"
    
    # Test tool execution
    result = await tools[0].ainvoke({"a": 5, "b": 3})
    assert "The sum of 5 and 3 is 8" in result
    
    # Cleanup
    await mcp_loader.close()


if __name__ == "__main__":
    # Run the test directly
    asyncio.run(test_mcp_stdio_integration())
    print("Integration test passed!")