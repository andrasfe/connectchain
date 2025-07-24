"""Example of using MCP tools with connectchain."""

import asyncio

from dotenv import load_dotenv

from connectchain.tools.mcp import MCPToolAgent, MCPToolLoader
from connectchain.utils.config import Config

# Load environment variables
load_dotenv()


async def main():
    """Demonstrate MCP tool integration."""
    # Load configuration
    config = Config.from_env()

    # Initialize MCP tool loader
    mcp_loader = MCPToolLoader(config)

    # Load tools from configured MCP servers
    # Assumes config.yaml has mcp.servers configured
    tools = await mcp_loader.load_tools()

    if not tools:
        print("No MCP tools loaded. Please configure MCP servers in config.yaml")
        print("Example configuration:")
        print(
            """
mcp:
  servers:
    math_tools:
      command: "python"
      args: ["path/to/math_server.py"]
      transport: "stdio"
"""
        )
        return

    print(f"Loaded {len(tools)} MCP tools")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

    # Create MCP agent with tools
    agent = MCPToolAgent("1", tools)

    # Example queries
    queries = [
        "Use the calculate tool to multiply 25 by 4",
        "Use the calculate tool to add 150 and 375",
        "Use the greet tool to say hello to MCP User",
        "Use the get_info tool to get server information",
    ]

    for query in queries:
        print(f"\nQuery: {query}")
        result = await agent.ainvoke(query)
        if isinstance(result, dict):
            if "content" in result:
                print(f"Response: {result['content']}")
            if "tool_results" in result:
                for tool_result in result["tool_results"]:
                    print(
                        f"Tool result ({tool_result['tool']}): {tool_result.get('result', tool_result.get('error'))}"
                    )
        else:
            print(f"Result: {result}")

    # Clean up
    await mcp_loader.close()


if __name__ == "__main__":
    asyncio.run(main())
