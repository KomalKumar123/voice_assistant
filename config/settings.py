import os
from dotenv import load_dotenv

# Load env variables from root folder
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

# --- LLM Provider Settings ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL_NAME   = os.getenv("MODEL_NAME", os.getenv("OLLAMA_MODEL", "qwen3:14b"))
HOST         = os.getenv("HOST", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
API_KEY      = os.getenv("API_KEY", "")

# Max code-generation + execution retry attempts
MAX_RETRIES = 3

# --- Qwen3 / LLM generation control ---
# Set ENABLE_THINKING=true in .env to enable chain-of-thought reasoning.
# WARNING: Leaving this enabled makes every call extremely slow (Qwen3 can
# generate thousands of <think> tokens before producing the actual answer).
# Default: False — disables thinking for fast responses.
ENABLE_THINKING = os.getenv("ENABLE_THINKING", "false").lower() == "true"

# Maximum tokens the model may generate per call (intent parsing overrides this with 256).
NUM_PREDICT = int(os.getenv("NUM_PREDICT", "2048"))

# --- Whisper STT ---
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")   # base | small | medium
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")  # int8 | float16 | float32

# --- Absolute paths ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploaded_files")
TEMP_FOLDER   = os.path.join(BASE_DIR, "temp")
LOGS_FOLDER   = os.path.join(BASE_DIR, "logs")
