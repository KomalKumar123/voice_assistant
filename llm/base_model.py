from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates a text completion statelessly using the model.
        
        Args:
            system_prompt (str): Instructions defining the model's persona/behavior.
            user_prompt (str): The actual input prompt for the model.
            
        Returns:
            str: Generated text response.
        """
        pass
