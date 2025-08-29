# MCP (Model Context Protocol) Examples

This directory contains examples demonstrating how to use MCP tools with ConnectChain, including both the MCP server implementation and client usage with direct API access.

## Overview

MCP (Model Context Protocol) allows you to create tools that can be used by language models. ConnectChain provides seamless integration with MCP servers, and with direct API access, you can use MCP tools without requiring Enterprise Auth Service (EAS) authentication.

## Files in this Directory

1. **`simple_mcp_server.py`** - A simple MCP server implementation with example tools
2. **`mcp_direct_access_example.py`** - Example showing how to use MCP tools with direct API access
3. **`example.config.yml`** - Example configuration file for ConnectChain with MCP

## Prerequisites

Install ConnectChain with examples dependencies:
```bash
pip install connectchain[examples]
```

For examples and configuration details, see the MCP tool README.md

## Quick Start

### 1. Set up your environment

Create a `.env` file in your project root:
```env
# Required for direct API access
OPENAI_API_KEY=your-openai-api-key-here

# Path to your configuration file
CONFIG_PATH=./config.yml
```

### 2. Configure ConnectChain

Copy the `example.config.yml` to your project root as `config.yml`:
```bash
cp examples/mcp/example.config.yml config.yml
```

Update the MCP server path if needed:
```yaml
mcp:
    servers:
        example:
            command: python
            args: ["examples/mcp/simple_mcp_server.py"]
            transport: stdio
```

### 3. Run the example

```bash
python examples/mcp/mcp_example.py
```

#### Direct API Access

The example demonstrates ConnectChain's direct API access:

- No EAS authentication required
- Uses API keys directly from environment variables
- Supports multiple LLM providers
- Seamless integration with MCP tools

#### Key Features Demonstrated

1. **Model Configuration**: Simple model setup without enterprise requirements
2. **MCP Tool Loading**: Automatic discovery and loading of MCP tools
3. **Agent Creation**: Creating an agent that can use MCP tools
4. **Tool Execution**: Examples of single and multi-tool usage

## The MCP Server

The `simple_mcp_server.py` provides three example tools:

1. **`greet`** - Returns a greeting for a given name
2. **`calculate`** - Performs basic arithmetic operations
3. **`get_info`** - Returns information about the MCP server

### Running the server standalone

You can test the MCP server independently:

```bash
# Run in stdio mode (default)
python examples/mcp/simple_mcp_server.py

# Run in HTTP mode
python examples/mcp/simple_mcp_server.py --http

# Run in SSE mode
python examples/mcp/simple_mcp_server.py --sse
```

## Configuration Options

### Models
```yaml
models:
    '1':
        provider: openai
        type: chat
        model_name: gpt-4
        # Automatically uses OPENAI_API_KEY from environment
```

### MCP Servers
```yaml
mcp:
    servers:
        server_name:
            command: python          # Command to run the server
            args: ["server.py"]      # Arguments to pass
            transport: stdio         # Transport type (stdio, http, sse)
            env:                     # Optional environment variables
                CUSTOM_VAR: value
```

## Troubleshooting

### "No module named 'fastmcp'"
Install ConnectChain with examples dependencies:
```bash
pip install connectchain[examples]
```

### "OPENAI_API_KEY not found"
Ensure your `.env` file contains your OpenAI API key:
```env
OPENAI_API_KEY=sk-...
```

### "No MCP tools loaded"
Check that:
1. The MCP server path in `config.yml` is correct
2. The server file exists and is executable
3. The `fastmcp` package is installed

## Advanced Usage

### Using Multiple MCP Servers

You can configure multiple MCP servers in your `config.yml`:

```yaml
mcp:
    servers:
        math_tools:
            command: python
            args: ["servers/math_server.py"]
            transport: stdio
            
        web_tools:
            command: node
            args: ["servers/web_tools.js"]
            transport: stdio
```

### Custom Transport Options

MCP supports different transport mechanisms:
- **stdio**: Default, communicates via standard input/output
- **http**: HTTP-based communication
- **sse**: Server-Sent Events for streaming

## Next Steps

1. Create your own MCP tools by extending the server example
2. Integrate MCP tools into your ConnectChain applications
3. Explore using multiple providers with direct access
4. Build complex tool chains combining multiple MCP servers

For more information about ConnectChain, see the main [README](../../README.md).