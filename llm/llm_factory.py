from config.settings import LLM_PROVIDER, MODEL_NAME, HOST, API_KEY
from llm.base_model import BaseLLM


class LLMFactory:

    @staticmethod
    def create() -> BaseLLM:
        provider = LLM_PROVIDER.strip().lower()

        if provider == "ollama":
            from llm.ollama_model import OllamaModel
            return OllamaModel(model_name=MODEL_NAME, host=HOST)
        elif provider == "openrouter":
            from llm.future.openrouter_model import OpenRouterModel
            return OpenRouterModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        elif provider == "openai":
            from llm.future.openai_model import OpenAIModel
            return OpenAIModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        elif provider == "gemini":
            from llm.future.gemini_model import GeminiModel
            return GeminiModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        elif provider == "groq":
            from llm.future.groq_model import GroqModel
            return GroqModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        elif provider == "deepseek":
            from llm.future.deepseek_model import DeepSeekModel
            return DeepSeekModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        elif provider == "together":
            from llm.future.together_model import TogetherModel
            return TogetherModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        elif provider == "anthropic":
            from llm.future.anthropic_model import AnthropicModel
            return AnthropicModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
        else:
            raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}")
