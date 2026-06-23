import os
from faster_whisper import WhisperModel
import sounddevice as sd
from scipy.io.wavfile import write
from config.settings import TEMP_FOLDER


class SpeechToText:

    def __init__(self):
        # We load whisper on demand or init it.
        # base model is small and fast.
        self.model = WhisperModel(
            "base",
            compute_type="int8"
        )

    def record_audio(
            self,
            duration=5,
            filename=None
    ):
        if filename is None:
            filename = os.path.join(TEMP_FOLDER, "current_audio.wav")
            
        # Ensure temp directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        fs = 16000

        recording = sd.rec(
            int(duration * fs),
            samplerate=fs,
            channels=1,
            dtype='int16'
        )

        sd.wait()

        write(
            filename,
            fs,
            recording
        )

        return filename

    def transcribe(
            self,
            filename
    ):
        if not os.path.exists(filename):
            return ""

        segments, info = self.model.transcribe(
            filename
        )

        text = ""

        for segment in segments:
            text += segment.text

        return text.strip()