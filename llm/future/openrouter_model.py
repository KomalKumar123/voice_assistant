from openai import OpenAI
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, HOST, API_KEY


class OpenRouterModel(BaseLLM):
    """
    OpenRouter LLM provider — uses the OpenAI-compatible OpenRouter API.

    OpenRouter gives access to 200+ models (DeepSeek, Claude, Gemini, Llama,
    Mistral, etc.) through a single unified API key.

    Recommended models:
        deepseek/deepseek-chat          — best value, very fast, cheap
        anthropic/claude-3.5-sonnet     — best overall quality
        meta-llama/llama-3.3-70b-instruct — strong open-source
        google/gemini-flash-1.5         — fastest

    Configuration (.env):
        LLM_PROVIDER=openrouter
        MODEL_NAME=deepseek/deepseek-chat
        API_KEY=sk-or-...
        HOST=https://openrouter.ai/api/v1   (optional, this is the default)
    """

    DEFAULT_HOST  = "https://openrouter.ai/api/v1"
    DEFAULT_MODEL = "deepseek/deepseek-chat"

    def __init__(self, model_name: str = None, host: str = None, api_key: str = None, **kwargs):
        self.model_name = model_name or MODEL_NAME or self.DEFAULT_MODEL
        self.client = OpenAI(
            base_url=host or HOST or self.DEFAULT_HOST,
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
        """
        Generates a stateless response via OpenRouter's API.

        Args:
            system_prompt   (str):  System/persona instructions.
            user_prompt     (str):  The user's input.
            response_format (str):  If "json", forces JSON-mode output.
            temperature     (float): Temperature (0 = deterministic).
            max_tokens      (int):  Cap on generated tokens.

        Returns:
            str: Generated text response.
        """
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
