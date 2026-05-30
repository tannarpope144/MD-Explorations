import os
from enum import Enum
from pydantic import BaseModel


class ModelClass(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"


class ModelSpec(BaseModel):
    provider: str
    model: str


class Config(BaseModel):
    model_config = {"frozen": False}

    routing: dict[ModelClass, ModelSpec]
    depth_budget: int = 4
    max_searches: int = 50


def load_keys() -> dict[str, str]:
    return {
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "deepseek": os.environ.get("DEEPSEEK_API_KEY", ""),
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "firecrawl": os.environ.get("FIRECRAWL_API_KEY", ""),
        "tavily": os.environ.get("TAVILY_API_KEY", ""),
    }


def default_config() -> "Config":
    return Config(routing={
        ModelClass.LIGHT:  ModelSpec(provider="openai", model="gpt-4o-mini"),
        ModelClass.MEDIUM: ModelSpec(provider="openai", model="gpt-4o"),
        ModelClass.HEAVY:  ModelSpec(provider="openai", model="gpt-5.4"),
    })
