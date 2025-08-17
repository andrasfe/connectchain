"""MCPToolAgent: LCEL-compatible agent for executing MCP tools based on LLM decisions.
This module provides the MCPToolAgent class, which integrates with LCEL and executes
MCP tools as requested by language model outputs. It supports both synchronous and
asynchronous invocation, error handling, and tool result aggregation."""

import asyncio
import logging
from typing import Any, List, Optional

from langchain.schema import AIMessage
from langchain.schema.runnable import Runnable, RunnableConfig
from langchain.tools import BaseTool

from ...lcel import model


class MCPToolAgent(Runnable):  # pylint: disable=redefined-builtin
    """LCEL-compatible agent that can execute MCP tools based on LLM decisions.
    Attributes:
        model_id (str): The model identifier.
        tools (Dict[str, BaseTool]): Mapping of tool names to tool instances.
    """

    def __init__(self, model_id: str, tools: List[BaseTool]):
        self.model_id = model_id
        self.tools = {tool.name: tool for tool in tools}

    async def ainvoke(
        self,
        input_data: Any,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> dict:
        """Process input through LLM and execute any requested tools."""
        llm = model(self.model_id)
        if hasattr(llm, "bind_tools"):
            llm = llm.bind_tools(list(self.tools.values()))

        response = await llm.ainvoke(input_data, config)

        if not hasattr(response, "tool_calls") or not response.tool_calls:
            return response

        results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name") if isinstance(tool_call, dict) else tool_call.name
            tool_args = tool_call.get("args", {}) if isinstance(tool_call, dict) else tool_call.args

            if tool_name in self.tools:
                try:
                    result = await self.tools[tool_name].ainvoke(tool_args)
                    results.append({"tool": tool_name, "result": result})
                except Exception as e:  # pylint: disable=broad-except
                    logging.getLogger(__name__).warning(
                        "Tool '%s' execution failed: %s", tool_name, e
                    )
                    results.append({"tool": tool_name, "error": str(e)})
            else:
                logging.getLogger(__name__).warning("Unknown tool requested: %s", tool_name)

        return {
            "content": response.content if isinstance(response, AIMessage) else str(response),
            "tool_results": results,
        }

    def invoke(
        self,
        input_data: Any,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> dict:
        """Synchronous wrapper for the asynchronous ainvoke function."""
        try:
            return asyncio.run(self.ainvoke(input_data, config, **kwargs))
        except RuntimeError as e:
            raise RuntimeError(
                "MCPToolAgent.invoke() failed. If you are running from within an event loop "
                "(e.g., in a web server or async application), please use the async ainvoke() "
                "method with await instead."
            ) from e

    def _call(
        self,
        input_data: Any,
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> dict:
        raise NotImplementedError(
            "MCPToolAgent does not support hidden `_call`. Please use a supported method (`invoke`, etc.)."
        )

    def batch(
        self,
        inputs: List[Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,  # pylint: disable=redefined-builtin
    ) -> List[dict]:
        raise NotImplementedError(
            "MCPToolAgent does not support `batch`. Please use a supported method (`invoke`, etc.)."
        )

    async def abatch(
        self,
        inputs: List[Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,  # pylint: disable=redefined-builtin
    ) -> List[dict]:
        raise NotImplementedError(
            "MCPToolAgent does not support `abatch`. Please use a supported method (`invoke`, etc.)."
        )
