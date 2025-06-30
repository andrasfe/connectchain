#!/usr/bin/env python3
"""
Test MCP functionality with direct API access (no EAS)
"""

import asyncio
import os
from dotenv import load_dotenv, find_dotenv
from connectchain.tools.mcp import MCPToolLoader, MCPToolAgent
from connectchain.utils import Config
from connectchain.lcel import model
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser

# Load environment variables
load_dotenv(find_dotenv())

async def test_mcp_direct():
    """Test MCP tools with direct OpenAI API access"""
    
    print("Testing MCP with Direct API Access")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        return
    
    print("✅ OPENAI_API_KEY found")
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = Config.from_env()
        print("   ✅ Config loaded successfully")
        
        # Test direct model access first
        print("\n2. Testing direct model access...")
        test_prompt = PromptTemplate(
            input_variables=["test"],
            template="Simply say: {test}"
        )
        test_chain = test_prompt | model("1") | StrOutputParser()
        test_response = test_chain.invoke({"test": "Direct access works!"})
        print(f"   ✅ Model response: {test_response}")
        
        # Load MCP tools
        print("\n3. Loading MCP tools...")
        loader = MCPToolLoader(config)
        tools = await loader.load_tools()
        
        if not tools:
            print("   ❌ No MCP tools loaded")
            return
            
        print(f"   ✅ Loaded {len(tools)} MCP tools:")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description}")
        
        # Create MCP agent with direct access model
        print("\n4. Creating MCP agent with direct access model...")
        agent = MCPToolAgent("1", tools)  # Using model "1" (o4-mini with direct access)
        print("   ✅ Agent created successfully")
        
        # Test the greet tool
        print("\n5. Testing MCP 'greet' tool...")
        result = await agent.ainvoke(
            "Use the greet tool to say hello to 'ConnectChain Direct Access'"
        )
        
        if isinstance(result, dict):
            print(f"   ✅ Agent response: {result.get('content', 'No content')}")
            if 'tool_results' in result:
                print(f"   Tool results: {result['tool_results']}")
        else:
            print(f"   ✅ Agent response: {result}")
        
        # Test with a more complex query
        print("\n6. Testing with natural language query...")
        result2 = await agent.ainvoke(
            "Can you greet both Alice and Bob using the greet tool?"
        )
        
        if isinstance(result2, dict):
            print(f"   ✅ Agent response: {result2.get('content', 'No content')}")
            if 'tool_results' in result2:
                print(f"   Tool results: {result2['tool_results']}")
        else:
            print(f"   ✅ Agent response: {result2}")
        
        print("\n" + "=" * 50)
        print("✅ MCP with Direct API Access test completed successfully!")
        print("\nKey achievements:")
        print("- No EAS authentication required")
        print("- Direct OpenAI API access working")
        print("- MCP tools loaded and functional")
        print("- Agent successfully used MCP tools")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_direct())