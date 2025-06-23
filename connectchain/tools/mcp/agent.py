"""LCEL-compatible MCP tool agent."""

from typing import Any, Dict, List, Optional

from langchain.schema import AIMessage
from langchain.schema.runnable import Runnable
from langchain.tools import BaseTool

from ...lcel import model
from ...utils.logger import Logger


class MCPToolAgent(Runnable):
    """LCEL-compatible agent that can execute MCP tools based on LLM decisions."""

    def __init__(self, model_id: str, tools: List[BaseTool]):
        self.model_id = model_id
        self.tools = {tool.name: tool for tool in tools}
        self.logger = Logger()

    async def ainvoke(self, input: Dict[str, Any], config: Optional[Dict] = None) -> Any:
        """Process input through LLM and execute any requested tools."""
        # Get LLM with bound tools
        llm = model(self.model_id).bind_tools(list(self.tools.values()))

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
                self.logger.info(f"Executing tool: {tool_name}")
                try:
                    result = await self.tools[tool_name].ainvoke(tool_args)
                    results.append({"tool": tool_name, "result": result})
                except Exception as e:
                    self.logger.error(f"Tool execution failed: {tool_name} - {str(e)}")
                    results.append({"tool": tool_name, "error": str(e)})
            else:
                self.logger.warning(f"Unknown tool requested: {tool_name}")

        return {
            "content": response.content if isinstance(response, AIMessage) else str(response),
            "tool_results": results,
        }

    def invoke(self, input: Dict[str, Any], config: Optional[Dict] = None) -> Any:
        """Synchronous version - not implemented, use ainvoke."""
        raise NotImplementedError("Use ainvoke for async execution")
