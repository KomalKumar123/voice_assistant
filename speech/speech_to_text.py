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

    def record_until_silence(self, filename: str = None, silence_seconds: float = 3.5) -> str:
        """
        Records microphone audio until silence (a pause of 3-4 seconds) is detected.
        Uses a short calibration window at startup to adapt to ambient room noise.
        """
        import numpy as np
        import sounddevice as sd
        from scipy.io.wavfile import write

        if filename is None:
            filename = os.path.join(TEMP_FOLDER, "current_audio.wav")

        os.makedirs(os.path.dirname(filename), exist_ok=True)

        fs = 16000  # 16 kHz
        chunk_duration = 0.2  # 200 ms chunks
        chunk_size = int(fs * chunk_duration)

        audio_data = []
        silent_chunks = 0
        max_silent_chunks = int(silence_seconds / chunk_duration)

        # Baseline threshold (will be adapted during calibration)
        threshold = 300.0

        # Run stream
        with sd.InputStream(samplerate=fs, channels=1, dtype='int16') as stream:
            # 1. Calibration phase: read the first 3 chunks (600ms) to measure ambient noise
            calibration_chunks = []
            for _ in range(3):
                data, _ = stream.read(chunk_size)
                audio_data.append(data)
                calibration_chunks.append(data)

            # Compute baseline ambient noise RMS
            calib_data = np.concatenate(calibration_chunks, axis=0)
            ambient_rms = np.sqrt(np.mean(np.double(calib_data)**2))

            # Set adaptive threshold (1.5x ambient noise, bounded between 250 and 1000)
            threshold = max(250.0, min(ambient_rms * 1.5, 1000.0))
            print(f"STT: Calibrated silence RMS threshold to {threshold:.2f} (ambient baseline: {ambient_rms:.2f})")

            # Minimum recording duration (1.5 seconds) to prevent premature cutoffs
            min_total_chunks = int(1.5 / chunk_duration)
            chunks_recorded = len(audio_data)

            while True:
                data, _ = stream.read(chunk_size)
                audio_data.append(data)
                chunks_recorded += 1

                # Calculate RMS of this chunk
                rms = np.sqrt(np.mean(np.double(data)**2))

                if chunks_recorded > min_total_chunks:
                    if rms < threshold:
                        silent_chunks += 1
                    else:
                        # Reset silence counter if speaking is detected
                        silent_chunks = 0

                if silent_chunks >= max_silent_chunks:
                    print(f"STT: Silence detected for {silence_seconds}s. Stopping.")
                    break

        # Save recording
        full_recording = np.concatenate(audio_data, axis=0)
        write(filename, fs, full_recording)
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