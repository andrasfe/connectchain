"""Tests for MCPToolAgent."""

from unittest.mock import AsyncMock, Mock, patch

import pytest

# Skip tests if langchain-mcp-adapters not installed
pytest.importorskip("langchain_mcp_adapters")

from langchain.schema import AIMessage
from langchain.tools import BaseTool

from connectchain.tools.mcp.agent import MCPToolAgent


class TestMCPToolAgent:
    """Test cases for MCPToolAgent."""

    @pytest.fixture
    def mock_tools(self):
        """Create mock tools."""
        add_tool = Mock(spec=BaseTool)
        add_tool.name = "add"
        add_tool.ainvoke = AsyncMock(return_value=10)

        multiply_tool = Mock(spec=BaseTool)
        multiply_tool.name = "multiply"
        multiply_tool.ainvoke = AsyncMock(return_value=20)

        return [add_tool, multiply_tool]

    @pytest.mark.asyncio
    async def test_no_tool_calls(self, mock_tools):
        """Test agent behavior when LLM doesn't request tools."""
        with patch("connectchain.tools.mcp.agent.model") as mock_model:
            # Mock LLM response without tool calls
            mock_llm = AsyncMock()
            mock_response = AIMessage(content="The answer is 42")
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm.bind_tools = Mock(return_value=mock_llm)
            mock_model.return_value = mock_llm

            agent = MCPToolAgent("1", mock_tools)
            result = await agent.ainvoke({"query": "What is 2+2?"})

            assert result.content == "The answer is 42"
            assert mock_llm.bind_tools.called

    @pytest.mark.asyncio
    async def test_with_tool_calls(self, mock_tools):
        """Test agent executes requested tools."""
        with patch("connectchain.tools.mcp.agent.model") as mock_model:
            # Mock LLM response with tool calls
            mock_llm = AsyncMock()
            mock_response = AIMessage(
                content="I'll calculate that for you.",
                tool_calls=[
                    {"id": "1", "name": "add", "args": {"a": 5, "b": 5}},
                    {"id": "2", "name": "multiply", "args": {"a": 2, "b": 10}},
                ],
            )
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm.bind_tools = Mock(return_value=mock_llm)
            mock_model.return_value = mock_llm

            agent = MCPToolAgent("1", mock_tools)
            result = await agent.ainvoke({"query": "Calculate 5+5 and 2*10"})

            assert result["content"] == "I'll calculate that for you."
            assert len(result["tool_results"]) == 2
            assert result["tool_results"][0] == {"tool": "add", "result": 10}
            assert result["tool_results"][1] == {"tool": "multiply", "result": 20}

    @pytest.mark.asyncio
    async def test_unknown_tool_requested(self, mock_tools):
        """Test agent handles unknown tool gracefully."""
        with patch("connectchain.tools.mcp.agent.model") as mock_model:
            # Mock LLM response requesting unknown tool
            mock_llm = AsyncMock()
            mock_response = AIMessage(
                content="Using unknown tool",
                tool_calls=[{"id": "1", "name": "unknown_tool", "args": {}}],
            )
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm.bind_tools = Mock(return_value=mock_llm)
            mock_model.return_value = mock_llm

            agent = MCPToolAgent("1", mock_tools)
            result = await agent.ainvoke({"query": "Use unknown tool"})

            assert result["content"] == "Using unknown tool"
            assert len(result["tool_results"]) == 0

    @pytest.mark.asyncio
    async def test_tool_execution_error(self, mock_tools):
        """Test agent handles tool execution errors."""
        # Make add tool raise an error
        mock_tools[0].ainvoke = AsyncMock(side_effect=Exception("Tool failed"))

        with patch("connectchain.tools.mcp.agent.model") as mock_model:
            mock_llm = AsyncMock()
            mock_response = AIMessage(
                content="Calculating",
                tool_calls=[{"id": "1", "name": "add", "args": {"a": 1, "b": 2}}],
            )
            mock_llm.ainvoke = AsyncMock(return_value=mock_response)
            mock_llm.bind_tools = Mock(return_value=mock_llm)
            mock_model.return_value = mock_llm

            agent = MCPToolAgent("1", mock_tools)
            result = await agent.ainvoke({"query": "Add 1+2"})

            assert result["tool_results"][0]["tool"] == "add"
            assert result["tool_results"][0]["error"] == "Tool failed"

    def test_invoke_runtime_error(self, mock_tools):
        """Test synchronous invoke raises RuntimeError with helpful message."""
        with patch("connectchain.tools.mcp.agent.asyncio.run") as mock_asyncio_run:
            # Simulate the RuntimeError that occurs when asyncio.run() is called from within an event loop
            mock_asyncio_run.side_effect = RuntimeError("asyncio.run() cannot be called from a running event loop")
            
            agent = MCPToolAgent("1", mock_tools)

            with pytest.raises(RuntimeError, match="MCPToolAgent.invoke\\(\\) failed"):
                agent.invoke({"query": "test"})
