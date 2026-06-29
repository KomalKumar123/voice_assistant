from openai import OpenAI
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, API_KEY


class DeepSeekModel(BaseLLM):
    """
    DeepSeek API LLM provider — uses the OpenAI compatibility client.

    Recommended models:
        deepseek-chat   — general purpose chat/coder
        deepseek-coder  — code generation specific

    Configuration (.env):
        LLM_PROVIDER=deepseek
        MODEL_NAME=deepseek-chat
        API_KEY=sk-...
    """

    DEFAULT_HOST  = "https://api.deepseek.com/v1"
    DEFAULT_MODEL = "deepseek-chat"

    def __init__(self, model_name: str = None, host: str = None, api_key: str = None, **kwargs):
        self.model_name = model_name or MODEL_NAME or self.DEFAULT_MODEL
        self.client = OpenAI(
            base_url=host or self.DEFAULT_HOST,
            api_key=api_key or API_KEY,
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
