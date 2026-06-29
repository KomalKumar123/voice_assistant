from google import genai
from google.genai import types
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, API_KEY


class GeminiModel(BaseLLM):
    """
    Google Gemini LLM provider — uses the official google-genai Python SDK.

    Recommended models:
        gemini-2.5-flash — extremely fast, excellent JSON and code generation.
        gemini-2.5-pro   — best for complex reasoning and tasks.

    Configuration (.env):
        LLM_PROVIDER=gemini
        MODEL_NAME=gemini-2.5-flash
        API_KEY=AIzaSy...
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(self, model_name: str = None, host: str = None, api_key: str = None, **kwargs):
        self.model_name = model_name or MODEL_NAME or self.DEFAULT_MODEL
        key = api_key or API_KEY
        client_kwargs = {}
        if key:
            client_kwargs["api_key"] = key
        # If host is passed (e.g. for proxy/endpoint overrides), we can set http_options
        if host:
            client_kwargs["http_options"] = {"api_version": "v1beta"}
        self.client = genai.Client(**client_kwargs)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = None,
        temperature: float = 0.0,
        max_tokens: int = None,
    ) -> str:
        config_kwargs = {}
        if system_prompt:
            config_kwargs["system_instruction"] = system_prompt
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if max_tokens is not None:
            config_kwargs["max_output_tokens"] = max_tokens
        if response_format == "json":
            config_kwargs["response_mime_type"] = "application/json"

        config = types.GenerateContentConfig(**config_kwargs)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=user_prompt,
            config=config,
        )
        return response.text.strip()
