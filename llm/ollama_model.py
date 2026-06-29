import re
from ollama import Client
from llm.base_model import BaseLLM
from config.settings import MODEL_NAME, HOST, ENABLE_THINKING, NUM_PREDICT


class OllamaModel(BaseLLM):

    def __init__(self, model_name: str = None, host: str = None):
        """
        Wrapper around the local Ollama Python SDK client.
        Uses object-attribute access (response.message.content) as required
        by the Ollama SDK — NOT dictionary indexing.

        Thinking mode (Qwen3 chain-of-thought):
            Controlled by ENABLE_THINKING in settings/env.
            Defaults to False (fast mode) — passes think=False to Ollama SDK
            which suppresses chain-of-thought at the model level.
        """
        self.model_name      = model_name or MODEL_NAME or "qwen3:14b"
        self.host            = host or HOST or "http://localhost:11434"
        self.enable_thinking = ENABLE_THINKING
        self.num_predict     = NUM_PREDICT
        self.client          = Client(host=self.host)

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = None,
        temperature: float = 0.0,
        max_tokens: int = None,
    ) -> str:
        """
        Generates a stateless response from Ollama.

        Args:
            system_prompt   (str):  System/persona instructions.
            user_prompt     (str):  The user's input.
            response_format (str):  If "json", forces JSON-mode output.
            temperature     (float): Temperature parameter (0 = deterministic).
            max_tokens      (int):  Override default token cap for this call.

        Returns:
            str: Model response with any <think> blocks stripped.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ]

        kwargs: dict = {}
        if response_format == "json":
            kwargs["format"] = "json"

        # Pass think=False to suppress Qwen3 chain-of-thought at the model level.
        # This is the official Ollama SDK mechanism (supported since ollama-python 0.4+).
        # When False, the model skips generating <think>...</think> blocks entirely,
        # cutting response time from minutes to seconds.
        kwargs["think"] = self.enable_thinking

        # Ollama SDK returns a ChatResponse object — access via attributes
        response = self.client.chat(
            model=self.model_name,
            messages=messages,
            options={
                "temperature": temperature,
                "num_predict": max_tokens if max_tokens is not None else self.num_predict,
            },
            **kwargs,
        )

        raw_text = response.message.content.strip()

        # Strip any residual <think>…</think> blocks defensively
        cleaned = self._strip_think_tags(raw_text)

        return cleaned

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_think_tags(text: str) -> str:
        """
        Removes <think>…</think> reasoning blocks emitted by Qwen3 models.
        These blocks appear before the actual answer and must be removed to
        prevent polluting JSON parsers, code extractors, and TTS engines.
        """
        cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
        return cleaned.strip()
