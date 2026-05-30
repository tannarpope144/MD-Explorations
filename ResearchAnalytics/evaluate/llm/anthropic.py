import json
from pydantic import BaseModel
from .base import LLMClient


class AnthropicClient(LLMClient):
    def __init__(self, client=None, api_key=None):
        if client is None:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
        self._c = client

    def _raw_structured(self, schema: type[BaseModel], messages, model,
                        max_tokens=4096, **kw) -> str:
        tool = {
            "name": "emit",
            "description": f"Emit a {schema.__name__} object.",
            "input_schema": schema.model_json_schema(),
        }
        resp = self._c.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=[tool],
            tool_choice={"type": "tool", "name": "emit"},
        )
        for block in resp.content:
            if getattr(block, "type", None) == "tool_use":
                return json.dumps(block.input)
        raise RuntimeError("no tool_use block in Anthropic response")
