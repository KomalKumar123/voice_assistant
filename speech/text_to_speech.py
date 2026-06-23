import os
import pyttsx3
from config.settings import TEMP_FOLDER


class TextToSpeech:

    def speak(self, text: str, filename: str = None) -> str:
        """
        Synthesizes text to an audio file offline using pyttsx3.
        
        Args:
            text (str): The message to synthesize.
            filename (str, optional): The path to save the audio file.
            
        Returns:
            str: Absolute path to the generated audio file.
        """
        if filename is None:
            filename = os.path.join(TEMP_FOLDER, "response.wav")

        # Make sure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Clear previous audio response file if present
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass

        # Initialize pyttsx3 (must be local to method for thread safety in Streamlit)
        engine = pyttsx3.init()
        
        # Customizations: rate (speed) and volume
        engine.setProperty("rate", 160)  # Slightly slower than default for clarity
        engine.setProperty("volume", 0.9)

        # Save to file
        engine.save_to_file(text, filename)
        engine.runAndWait()

        return filename
