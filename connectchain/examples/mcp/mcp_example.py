"""Example of using MCP tools with connectchain."""

import asyncio
from connectchain.utils.config import Config
from connectchain.tools.mcp import MCPToolLoader, MCPToolAgent
from connectchain.chains import ValidPromptTemplate
from connectchain.lcel import LCELLogger


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
        print("""
mcp:
  servers:
    math_tools:
      command: "python"
      args: ["path/to/math_server.py"]
      transport: "stdio"
""")
        return
    
    print(f"Loaded {len(tools)} MCP tools")
    
    # Create MCP agent with tools
    agent = MCPToolAgent("1", tools)
    
    # Build LCEL chain
    chain = (
        ValidPromptTemplate(template="{query}")
        | agent
        | LCELLogger()
    )
    
    # Example queries
    queries = [
        "What is 25 multiplied by 4?",
        "Calculate the sum of 150 and 375",
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        result = await chain.ainvoke({"query": query})
        print(f"Result: {result}")
    
    # Clean up
    await mcp_loader.close()


if __name__ == "__main__":
    asyncio.run(main())