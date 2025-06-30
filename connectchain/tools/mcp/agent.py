"""LCEL-compatible MCP tool agent."""

from typing import Any, List, Optional

from langchain.schema import AIMessage
from langchain.schema.runnable import Runnable, RunnableConfig
from langchain.tools import BaseTool

from ...lcel import model


class MCPToolAgent(Runnable):
    """LCEL-compatible agent that can execute MCP tools based on LLM decisions."""

    def __init__(self, model_id: str, tools: List[BaseTool]):
        self.model_id = model_id
        self.tools = {tool.name: tool for tool in tools}

    async def ainvoke(
        self,
        input: Any,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,  # pylint: disable=redefined-builtin
    ) -> Any:
        """Process input through LLM and execute any requested tools."""
        # Get LLM with bound tools
        llm = model(self.model_id)
        if hasattr(llm, "bind_tools"):
            llm = llm.bind_tools(list(self.tools.values()))

        # Get LLM response
        response = await llm.ainvoke(input, config)

        # If no tool calls, return the content
        if not hasattr(response, "tool_calls") or not response.tool_calls:
            return response.content if isinstance(response, AIMessage) else response

        # Execute tool calls
        results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
            tool_args = tool_call.get("args", {}) if isinstance(tool_call, dict) else tool_call.args

            if tool_name in self.tools:
                # Executing tool
                try:
                    result = await self.tools[tool_name].ainvoke(tool_args)
                    results.append({"tool": tool_name, "result": result})
                except Exception as e:  # pylint: disable=broad-except
                    # Tool execution failed
                    results.append({"tool": tool_name, "error": str(e)})
            else:
                # Unknown tool requested
                pass

        return {
            "content": response.content if isinstance(response, AIMessage) else str(response),
            "tool_results": results,
        }

    def invoke(
        self,
        input: Any,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,  # pylint: disable=redefined-builtin
    ) -> Any:
        """Synchronous version - not implemented, use ainvoke."""
        raise NotImplementedError("Use ainvoke for async execution")
