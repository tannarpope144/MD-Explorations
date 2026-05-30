from .openai import OpenAIClient


class DeepSeekClient(OpenAIClient):
    """DeepSeek is OpenAI-API-compatible; just point at its base_url."""
    def __init__(self, api_key=None, base_url="https://api.deepseek.com", client=None):
        super().__init__(client=client, api_key=api_key, base_url=base_url)
