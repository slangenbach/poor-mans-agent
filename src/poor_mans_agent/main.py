"""Agent."""

import json
import os
from collections.abc import Callable

from claudette import Client, mk_msgs

from .config import get_config
from .logger import get_logger

config = get_config()
logger = get_logger(__name__)


class Agent:
    """A poor man's agent implementation."""

    def __init__(self, model: str | None, tools: list[Callable] | None) -> None:  # noqa: D107
        self.model = model if model else config.ai_model_name
        self.tools = tools if tools else None
        self.client = Client(model=self.model)

        os.environ["ANTHROPIC_API_KEY"] = config.anthropic_key.get_secret_value()

    @staticmethod
    def _get_tool(name: str):
        try:
            return globals()[name]
        except KeyError:
            logger.error("Could not find tool %s", name)
            raise

    @staticmethod
    def _call_tool(tool, input):
        return tool(**input)

    @staticmethod
    def _format_tool_call_result(id: str, result):
        return {"type": "tool_result", "tool_use_id": id, "content": json.dumps(result.text)}

    def run_loop(self, prompt: str):
        """Run agent loop."""
        response = self.client(prompt, tools=self.tools)

        while response.stop_reason == "tool_use":
            tool_use_block = response.content[1]
            _tool = self._get_tool(tool_use_block.name)

            logger.debug("Calling tool: %s", tool_use_block.name)
            _result = self._call_tool(tool=_tool, input=tool_use_block.input)

            tool_call_result = self._format_tool_call_result(id=tool_use_block.id, result=_result)
            logger.debug("Result: %s", tool_call_result)

            messages = mk_msgs([prompt, response.content, [tool_call_result]])
            response = self.client(messages)

        return response
