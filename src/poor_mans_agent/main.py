"""Agent."""

import json
from collections.abc import Callable
from datetime import datetime
from typing import Any

from dateutil import tz
from openai import OpenAI
from openai.types.chat import ChatCompletion

from .config import get_config
from .errors import PoorMansAgentError
from .logger import get_logger
from .prompts import SYSTEM_PROMPT

config = get_config()
logger = get_logger(__name__, level=config.log_level)


class Agent:
    """A poor man's agent implementation."""

    def __init__(  # noqa: D107
        self,
        model: str | None = None,
        tools: list[Callable] | None = None,
        system_prompt: str | None = None,
        max_iterations: int = 3,
    ) -> None:
        self.model = model if model else config.ai_model_name
        self.tools = {tool.__name__: tool for tool in tools} if tools else {}  # type: ignore[unresolved-attribute]
        self._tool_schemas = [self._get_tool_schema(tool) for tool in tools] if tools else None
        self.system_prompt = (
            system_prompt
            if system_prompt
            else SYSTEM_PROMPT.format(current_timestamp=datetime.now(tz=tz.UTC).isoformat())
        )
        self.max_iterations = max_iterations
        self._client = OpenAI(
            base_url=config.ai_model_base_url, api_key=config.ai_model_key.get_secret_value()
        )
        self.messages = [{"role": "system", "content": self.system_prompt}]

    @staticmethod
    def _get_json_type(param_type: type) -> str:
        mapping = {str: "string", int: "integer", float: "number", bool: "boolean"}
        _type = mapping.get(param_type, "string")

        return _type

    def _get_tool_schema(self, tool: Callable) -> dict:
        params = {}

        for k, v in tool.__annotations__.items():
            if k == "return":
                continue
            params[k] = {"type": self._get_json_type(v)}

        return {
            "type": "function",
            "function": {
                "name": tool.__name__,  # type: ignore[unresolved-attribute]
                "description": tool.__doc__,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": [k for k in params.keys()],
                },
            },
        }

    def _get_tool(self, name: str) -> Callable:
        try:
            return self.tools[name]
        except KeyError as err:
            logger.error("Could not find tool %s", name)
            raise PoorMansAgentError(
                f"Tool '{name}' not found. Make sure the tool is actually defined."
            ) from err

    @staticmethod
    def _call_tool(tool: Callable, input: dict[str, Any] | str) -> Any:
        if not isinstance(tool, dict):
            input = json.loads(input)  # type: ignore[invalid-argument-type]

        return tool(**input)  # type: ignore[invalid-argument-type]

    @staticmethod
    def _format_tool_call_result(id: str, result: Any) -> dict[str, str]:
        return {
            "role": "tool",
            "tool_call_id": id,
            "content": str(result),
        }

    def _call_model(self) -> ChatCompletion:
        """Call AI model."""
        logger.debug("Getting response from AI")
        response = self._client.chat.completions.create(
            model=self.model, tools=self._tool_schemas, messages=self.messages
        )

        self.messages.append(response.choices[0].message.model_dump())

        return response

    def run(self, prompt: str) -> str | None:
        """Run agent loop."""
        self.messages.append({"role": "user", "content": prompt})

        response = self._call_model()
        iterations = 0

        while response.choices[0].finish_reason == "tool_calls":
            iterations += 1

            if iterations >= self.max_iterations:
                logger.warning("Reached max iteration (%d) limit", self.max_iterations)
                raise PoorMansAgentError(
                    f"Agent exceeded max iterations ({self.max_iterations}) without completing the task."  # noqa: E501
                )

            tool_use_block = response.choices[0].message.tool_calls[0]  # type: ignore[not-subscriptable]
            tool_name = tool_use_block.function.name  # type: ignore[possibly-missing-attribute]
            tool_params = tool_use_block.function.arguments  # type: ignore[possibly-missing-attribute]

            try:
                _tool = self._get_tool(tool_name)
                logger.debug("Calling tool %s with params: %s", tool_name, tool_params)
                _result = self._call_tool(tool=_tool, input=tool_params)

                tool_call_result = self._format_tool_call_result(
                    id=tool_use_block.id, result=_result
                )
                logger.debug("Result: %s", tool_call_result)

            except Exception as err:  # noqa: BLE001
                logger.error("Tool execution failed: %s", err)
                _result = f"Tool execution failed: {type(err).__name__}: {str(err)}"
                tool_call_result = self._format_tool_call_result(
                    id=tool_use_block.id, result=_result
                )

            self.messages.append(tool_call_result)
            response = self._call_model()

        return response.choices[0].message.content
