import re
from groq import Groq
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, API_KEY


class GroqModel(BaseLLM):
    """
    Groq Cloud LLM provider — uses the official Groq Python SDK.

    Groq runs on custom LPU (Language Processing Unit) hardware and delivers
    some of the fastest inference speeds available (often 200-500 tok/s).
    Free tier is available at console.groq.com.

    Recommended models:
        llama-3.3-70b-versatile  — best quality, still very fast
        llama3-8b-8192           — fastest, good for intent parsing
        mixtral-8x7b-32768       — good general-purpose model

    Configuration (.env):
        LLM_PROVIDER=groq
        MODEL_NAME=llama-3.3-70b-versatile
        API_KEY=gsk_...
    """

    DEFAULT_MODEL = "llama-3.3-70b-versatile"

    def __init__(self, model_name: str = None, api_key: str = None, **kwargs):
        self.model_name = model_name or MODEL_NAME or self.DEFAULT_MODEL
        self.client = Groq(api_key=api_key or API_KEY)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = None,
        temperature: float = 0.0,
        max_tokens: int = None,
    ) -> str:
        """
        Generates a stateless response via Groq's API.

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
