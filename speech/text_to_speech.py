import os
import re
import pyttsx3
from config.settings import TEMP_FOLDER


class TextToSpeech:

    def speak(self, text: str, filename: str = None) -> str:
        """
        Synthesizes text to an audio WAV file offline using pyttsx3.

        Strips markdown formatting characters before synthesis so the TTS
        engine reads clean prose rather than asterisks or hash symbols.

        Args:
            text     (str): The message to synthesize.
            filename (str): Output path. Defaults to temp/response.wav.

        Returns:
            str: Absolute path to the generated audio file.
        """
        if filename is None:
            filename = os.path.join(TEMP_FOLDER, "response.wav")

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Remove existing file to avoid pyttsx3 append issues
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception:
                pass

        # Strip markdown artefacts that would be read aloud literally
        clean_text = self._strip_markdown(text)

        # Initialise engine fresh each call for Streamlit thread safety
        engine = pyttsx3.init()
        engine.setProperty("rate", 155)    # Slightly slower for clarity
        engine.setProperty("volume", 0.92)

        # Prefer a female voice if available (tends to be clearer for TTS)
        voices = engine.getProperty("voices")
        for voice in voices:
            if "female" in voice.name.lower() or "zira" in voice.name.lower():
                engine.setProperty("voice", voice.id)
                break

        engine.save_to_file(clean_text, filename)
        engine.runAndWait()

        return filename

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _strip_markdown(text: str) -> str:
        """
        Removes common markdown formatting characters that would be read
        aloud literally by a TTS engine.
        """
        # Remove headers (##, ###, etc.)
        text = re.sub(r"#{1,6}\s*", "", text)
        # Remove bold/italic markers
        text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
        text = re.sub(r"_{1,2}(.*?)_{1,2}", r"\1", text)
        # Remove bullet list markers
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        # Remove numbered list markers (1. 2. etc.)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
        # Remove backtick code spans
        text = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", text)
        # Collapse multiple blank lines
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
