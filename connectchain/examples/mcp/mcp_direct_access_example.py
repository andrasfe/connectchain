# Copyright 2023 American Express Travel Related Services Company, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except
# in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under
# the License.
"""
MCP Direct Access Example

This example demonstrates using MCP tools with ConnectChain's direct API access,
bypassing the need for Enterprise Auth Service (EAS) authentication.
"""

import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from connectchain.tools.mcp import MCPToolLoader, MCPToolAgent
from connectchain.utils import Config
from connectchain.lcel import model

# Load environment variables
load_dotenv(find_dotenv())


async def main():
    """Demonstrate MCP tool integration with direct API access."""

    print("MCP Direct Access Example")
    print("=" * 50)

    # Check for required API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key in the .env file")
        return

    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = Config.from_env()
        print("   ✅ Config loaded successfully")

        # Test direct model access
        print("\n2. Testing direct model access (no EAS)...")
        test_prompt = PromptTemplate(
            input_variables=["message"], template="Echo this message: {message}"
        )
        test_chain = test_prompt | model("1") | StrOutputParser()
        test_response = test_chain.invoke({"message": "Direct API access is working!"})
        print(f"   Model response: {test_response}")

        # Load MCP tools
        print("\n3. Loading MCP tools...")
        loader = MCPToolLoader(config)
        tools = await loader.load_tools()

        if not tools:
            print("   No MCP tools loaded.")
            print("   Please ensure MCP servers are configured in config.yml")
            print("   Example configuration:")
            print(
                """
mcp:
    servers:
        example:
            command: python
            args: ["examples/mcp/simple_mcp_server.py"]
            transport: stdio
"""
            )
            return

        print(f"   Loaded {len(tools)} MCP tools:")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description}")

        # Create MCP agent
        print("\n4. Creating MCP agent with direct access model...")
        agent = MCPToolAgent("1", tools)  # Using model "1" configured for direct access
        print("   Agent created successfully")

        # Example 1: Simple greeting
        print("\n5. Example 1: Simple greeting")
        result = await agent.ainvoke("Use the greet tool to say hello to 'ConnectChain User'")
        print_result(result)

        # Example 2: Calculation
        print("\n6. Example 2: Performing calculations")
        result = await agent.ainvoke("Use the calculate tool to multiply 15 by 7")
        print_result(result)

        # Example 3: Get server information
        print("\n7. Example 3: Getting server information")
        result = await agent.ainvoke("Use the get_info tool to tell me about this MCP server")
        print_result(result)

        # Example 4: Complex request
        print("\n8. Example 4: Complex multi-tool request")
        result = await agent.ainvoke(
            "First greet 'Alice', then calculate 100 divided by 4, "
            "and finally get the server information"
        )
        print_result(result)

        print("\n" + "=" * 50)
        print(" MCP Direct Access Example completed successfully!")
        print("\nKey takeaways:")
        print("- Direct API access eliminates need for EAS authentication")
        print("- MCP tools integrate seamlessly with direct access")
        print("- Multiple providers can be configured without enterprise setup")

        # Clean up
        await loader.close()

    except Exception as e:
        print(f"\n Error: {e}")
        import traceback

        traceback.print_exc()


def print_result(result):
    """Pretty print the agent result."""
    if isinstance(result, dict):
        if "content" in result and result["content"]:
            print(f"   Agent response: {result['content']}")
        if "tool_results" in result and result["tool_results"]:
            print("   Tool results:")
            for tool_result in result["tool_results"]:
                print(
                    f"      - {tool_result['tool']}: {tool_result.get('result', tool_result.get('error'))}"
                )
    else:
        print(f"   Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
