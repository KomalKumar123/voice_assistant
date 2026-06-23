import os
from dotenv import load_dotenv

# Load env variables from root folder
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Absolute paths to stay safe
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploaded_files")
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")
