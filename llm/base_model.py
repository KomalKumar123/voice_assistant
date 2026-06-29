from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: str = None,
        temperature: float = 0.0,
        max_tokens: int = None,
    ) -> str:
        """
        Generates a text completion statelessly using the model.

        Args:
            system_prompt (str): persona / behavior instructions.
            user_prompt (str): input prompt.
            response_format (str): format type, e.g. "json".
            temperature (float): controls randomness.
            max_tokens (int): cap on generated tokens; None uses provider default.

        Returns:
            str: Generated text response.
        """
        pass
