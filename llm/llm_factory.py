from config.settings import LLM_PROVIDER, MODEL_NAME, HOST, API_KEY
from llm.base_model import BaseLLM
import os


class FallbackLLM(BaseLLM):
    def __init__(self, models: list[BaseLLM]):
        self.models = models

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = None,
        temperature: float = 0.0,
        max_tokens: int = None,
    ) -> str:
        errors = []
        for i, model in enumerate(self.models):
            provider_name = model.__class__.__name__
            model_name = getattr(model, "model_name", "unknown")
            try:
                print(f"FallbackLLM: Attempting generation with model {i+1}/{len(self.models)}: {provider_name} ({model_name})...")
                result = model.generate(system_prompt, user_prompt, response_format, temperature, max_tokens)
                print(f"FallbackLLM: {provider_name} call succeeded!")
                return result
            except Exception as e:
                err_msg = f"{provider_name} ({model_name}) failed: {str(e)}"
                print(f"FallbackLLM Error: {err_msg}")
                errors.append(err_msg)
        
        raise RuntimeError("All LLM providers in fallback chain failed:\n" + "\n".join(errors))


class LLMFactory:

    @staticmethod
    def create() -> BaseLLM:
        primary = LLM_PROVIDER.strip().lower()
        
        # Build order of preferences. Primary goes first.
        providers_order = ["gemini", "openai", "ollama"]
        if primary in providers_order:
            providers_order.remove(primary)
            providers_order.insert(0, primary)
        else:
            providers_order.insert(0, primary)

        models_list = []
        
        for provider in providers_order:
            try:
                if provider == "ollama":
                    try:
                        is_local_host = "localhost" in (HOST or "") or "127.0.0.1" in (HOST or "") or not HOST
                        if not is_local_host and API_KEY:
                            from llm.future.openai_model import OpenAIModel
                            models_list.append(OpenAIModel(
                                model_name=os.getenv("OLLAMA_MODEL", "qwen3:14b"),
                                host=HOST,
                                api_key=API_KEY
                            ))
                            print("LLMFactory: Cloud Ollama model detected. Routed via OpenAI Completion client.")
                        else:
                            from llm.ollama_model import OllamaModel
                            models_list.append(OllamaModel(
                                model_name=os.getenv("OLLAMA_MODEL", "qwen3:14b"),
                                host=HOST or "http://localhost:11434"
                            ))
                    except ImportError:
                        pass
                elif provider == "gemini":
                    # Retrieve Gemini key (check fallback env names too)
                    gemini_key = os.getenv("API_KEY", "") if LLM_PROVIDER == "gemini" else os.getenv("GEMINI_API_KEY", os.getenv("API_KEY", ""))
                    if gemini_key:
                        try:
                            from llm.future.gemini_model import GeminiModel
                            models_list.append(GeminiModel(
                                model_name="gemini-2.5-flash",
                                api_key=gemini_key
                            ))
                        except ImportError:
                            pass
                elif provider == "openai":
                    # Retrieve OpenAI key
                    openai_key = os.getenv("API_KEY", "") if LLM_PROVIDER == "openai" else os.getenv("OPENAI_API_KEY", "")
                    if openai_key:
                        try:
                            from llm.future.openai_model import OpenAIModel
                            models_list.append(OpenAIModel(
                                model_name="gpt-4o-mini",
                                api_key=openai_key
                            ))
                        except ImportError:
                            pass
            except Exception as e:
                print(f"LLMFactory: Failed to initialize optional fallback '{provider}': {str(e)}")

        # Fallback safeguard: if list is empty, initialize the primary as a last-resort (which will fail with import error if not setup)
        if not models_list:
            if primary == "ollama":
                is_local_host = "localhost" in (HOST or "") or "127.0.0.1" in (HOST or "") or not HOST
                if not is_local_host and API_KEY:
                    from llm.future.openai_model import OpenAIModel
                    return OpenAIModel(model_name=MODEL_NAME, host=HOST, api_key=API_KEY)
                else:
                    from llm.ollama_model import OllamaModel
                    return OllamaModel(model_name=MODEL_NAME, host=HOST)
            elif primary == "openai":
                from llm.future.openai_model import OpenAIModel
                return OpenAIModel(model_name=MODEL_NAME, api_key=API_KEY)
            elif primary == "gemini":
                from llm.future.gemini_model import GeminiModel
                return GeminiModel(model_name=MODEL_NAME, api_key=API_KEY)
            else:
                raise ValueError(f"Unknown LLM provider configuration: {LLM_PROVIDER}")

        return FallbackLLM(models_list)

