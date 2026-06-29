from openai import OpenAI
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, API_KEY


class OpenAIModel(BaseLLM):
    """
    OpenAI LLM provider — uses the official OpenAI Python SDK.

    Recommended models:
        gpt-4o-mini   — fast and cheap, excellent for structured JSON
        gpt-4o        — best quality
        gpt-3.5-turbo — legacy, cheapest

    Configuration (.env):
        LLM_PROVIDER=openai
        MODEL_NAME=gpt-4o-mini
        API_KEY=sk-...
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, model_name: str = None, host: str = None, api_key: str = None, **kwargs):
        self.model_name = model_name or MODEL_NAME or self.DEFAULT_MODEL
        self.client = OpenAI(
            api_key=api_key or API_KEY,
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
        kwargs: dict = {
            "model":       self.model_name,
            "messages":    [
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            "temperature": temperature,
        }

        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens

        if response_format == "json":
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content.strip()
