from pydantic import BaseModel
from .base import LLMClient


def _strict_schema(schema: dict) -> dict:
    """Recursively add additionalProperties: false to all object nodes."""
    if isinstance(schema, dict):
        if schema.get("type") == "object" or "properties" in schema:
            schema.setdefault("additionalProperties", False)
        for v in schema.values():
            if isinstance(v, dict):
                _strict_schema(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        _strict_schema(item)
    return schema


class OpenAIClient(LLMClient):
    def __init__(self, client=None, api_key=None, base_url=None):
        if client is None:
            from openai import OpenAI
            client = OpenAI(api_key=api_key, base_url=base_url)
        self._c = client

    def _raw_structured(self, schema: type[BaseModel], messages, model, **kw) -> str:
        js = _strict_schema(schema.model_json_schema())
        resp = self._c.chat.completions.create(
            model=model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": {"name": schema.__name__, "strict": True,
                                "schema": js},
            },
        )
        return resp.choices[0].message.content
