import os
import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from config.settings import TEMP_FOLDER, WHISPER_MODEL_SIZE, WHISPER_COMPUTE_TYPE


class SpeechToText:

    def __init__(self):
        """
        Loads the Faster Whisper model once at initialisation.
        Model size and compute type are configurable via settings.py or .env.
        """
        self.model = WhisperModel(
            WHISPER_MODEL_SIZE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )

    def record_audio(self, duration: int = 5, filename: str = None) -> str:
        """
        Records microphone audio for the specified duration and saves it as WAV.

        Args:
            duration (int): Recording length in seconds.
            filename (str): Output path. Defaults to temp/current_audio.wav.

        Returns:
            str: Absolute path to the saved WAV file.
        """
        if filename is None:
            filename = os.path.join(TEMP_FOLDER, "current_audio.wav")

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        fs = 16000  # 16 kHz — optimal for Whisper
        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype="int16",
        )
        sd.wait()

        write(filename, fs, recording)
        return filename

    def transcribe(self, filename: str) -> str:
        """
        Transcribes a WAV file to text using Faster Whisper.

        Args:
            filename (str): Path to the WAV file.

        Returns:
            str: Transcribed text, or empty string on failure.
        """
        if not os.path.exists(filename):
            return ""

        segments, _ = self.model.transcribe(
            filename,
            language="en",   # Hint: English — speeds up detection
            beam_size=5,     # Better accuracy vs beam_size=1
        )

        return "".join(seg.text for seg in segments).strip()