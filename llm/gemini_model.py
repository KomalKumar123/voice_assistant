from google import genai
from google.genai import types
from llm.base_model import BaseLLM
from config.settings import GEMINI_API_KEY, GEMINI_MODEL


class GeminiLLM(BaseLLM):

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set it in your .env file."
            )
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = GEMINI_MODEL

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.0,  # 0.0 temperature for deterministic code generation
        )
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=config
        )
        
        return response.text.strip()
