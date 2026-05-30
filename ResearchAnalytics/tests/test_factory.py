from evaluate.config import Config, ModelClass, ModelSpec
from evaluate.llm.factory import build_client
from evaluate.llm.openai import OpenAIClient
from evaluate.llm.anthropic import AnthropicClient


def test_config_maps_classes():
    cfg = Config(
        routing={
            ModelClass.LIGHT:  ModelSpec(provider="deepseek", model="deepseek-chat"),
            ModelClass.MEDIUM: ModelSpec(provider="openai",   model="gpt-4o-mini"),
            ModelClass.HEAVY:  ModelSpec(provider="anthropic", model="claude-x"),
        },
        depth_budget=4, max_searches=50,
    )
    assert cfg.routing[ModelClass.HEAVY].provider == "anthropic"


def test_build_client_returns_right_type():
    spec = ModelSpec(provider="anthropic", model="claude-x")
    client, model = build_client(spec, keys={"anthropic": "k"})
    assert isinstance(client, AnthropicClient) and model == "claude-x"
    spec2 = ModelSpec(provider="openai", model="gpt-x")
    client2, _ = build_client(spec2, keys={"openai": "k"})
    assert isinstance(client2, OpenAIClient)
