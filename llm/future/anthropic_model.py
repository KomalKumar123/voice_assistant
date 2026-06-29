import anthropic
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, API_KEY


class AnthropicModel(BaseLLM):
    """
    Anthropic LLM provider — uses the official Anthropic Python SDK.

    Recommended models:
        claude-3-5-sonnet-latest — best overall quality and coding capabilities
        claude-3-5-haiku-latest  — fastest and most cost-effective

    Configuration (.env):
        LLM_PROVIDER=anthropic
        MODEL_NAME=claude-3-5-sonnet-latest
        API_KEY=sk-ant-...
    """

    DEFAULT_MODEL = "claude-3-5-sonnet-latest"

    def __init__(self, model_name: str = None, host: str = None, api_key: str = None, **kwargs):
        self.model_name = model_name or MODEL_NAME or self.DEFAULT_MODEL
        # Anthropic Client will automatically load ANTHROPIC_API_KEY from environment if api_key is None
        self.client = anthropic.Anthropic(
            api_key=api_key or API_KEY or None,
            **({"base_url": host} if host else {}),
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = None,
        temperature: float = 0.0,
        max_tokens: int = None,
    ) -> str:
        # Default max_tokens to 1024 or higher if code generation is requested
        # Anthropic requires max_tokens to be provided
        tokens_limit = max_tokens if max_tokens is not None else 2048

        kwargs: dict = {
            "model": self.model_name,
            "max_tokens": tokens_limit,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        
        # Extract the text content from Anthropic response block
        text = ""
        for content_block in response.content:
            if hasattr(content_block, "text"):
                text += content_block.text
            elif isinstance(content_block, dict) and "text" in content_block:
                text += content_block["text"]
                
        return text.strip()
