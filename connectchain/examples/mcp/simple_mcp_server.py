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
Simple MCP Server Example

This server demonstrates a basic MCP tool that can be used with ConnectChain.
Note: This example requires the 'fastmcp' package to be installed separately.
"""

try:
    from fastmcp import FastMCP
except ImportError:
    print("Error: fastmcp is not installed.")
    print("Please install it with: pip install fastmcp")
    import sys
    sys.exit(1)

import sys
import os

# Initialize the MCP server
mcp = FastMCP("ConnectChain Example MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Return a greeting for the given name."""
    return f"Hello, {name}! Welcome to ConnectChain with MCP."

@mcp.tool
def calculate(operation: str, a: float, b: float) -> float:
    """
    Perform a calculation on two numbers.
    
    Args:
        operation: The operation to perform (add, subtract, multiply, divide)
        a: The first number
        b: The second number
        
    Returns:
        The result of the calculation
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return f"Error: Unknown operation '{operation}'. Use: add, subtract, multiply, or divide"
    
    result = operations[operation](a, b)
    return result

@mcp.tool
def get_info() -> dict:
    """Get information about this MCP server."""
    return {
        "name": "ConnectChain Example MCP Server",
        "version": "1.0.0",
        "tools": ["greet", "calculate", "get_info"],
        "description": "A simple MCP server demonstrating integration with ConnectChain"
    }

if __name__ == "__main__":
    # Server can run in different transport modes
    transport = "stdio"  # Default transport
    port = 8080
    path = None
    
    # Check for command line arguments or environment variables
    if "--http" in sys.argv or os.environ.get("MCP_TRANSPORT") == "http":
        transport = "http"
        port = int(os.environ.get("MCP_PORT", "8080"))
        path = "/mcp"
        print(f"Starting MCP server in HTTP mode on port {port}")
        mcp.run(transport=transport, port=port, path=path)
    elif "--sse" in sys.argv or os.environ.get("MCP_TRANSPORT") == "sse":
        transport = "sse"
        port = int(os.environ.get("MCP_PORT", "8080"))
        print(f"Starting MCP server in SSE mode on port {port}")
        mcp.run(transport=transport, port=port, path="/sse")
    else:
        # Default stdio transport for ConnectChain integration
        mcp.run(transport=transport)