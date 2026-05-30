from ..config import ModelSpec
from .openai import OpenAIClient
from .deepseek import DeepSeekClient
from .anthropic import AnthropicClient


def build_client(spec: ModelSpec, keys: dict[str, str]):
    p = spec.provider
    if p == "openai":
        return OpenAIClient(api_key=keys.get("openai", "")), spec.model
    if p == "deepseek":
        return DeepSeekClient(api_key=keys.get("deepseek", "")), spec.model
    if p == "anthropic":
        return AnthropicClient(api_key=keys.get("anthropic", "")), spec.model
    raise ValueError(f"unknown provider: {p}")
