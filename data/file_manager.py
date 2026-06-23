import os
import shutil
from config.settings import UPLOAD_FOLDER, TEMP_FOLDER


class FileManager:

    @staticmethod
    def save_uploaded_file(uploaded_file):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, "current.xlsx")
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return file_path

    @staticmethod
    def clear_folders():
        # Clear upload folder
        if os.path.exists(UPLOAD_FOLDER):
            try:
                shutil.rmtree(UPLOAD_FOLDER)
            except Exception:
                pass
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Clear temp folder
        if os.path.exists(TEMP_FOLDER):
            try:
                shutil.rmtree(TEMP_FOLDER)
            except Exception:
                pass
        os.makedirs(TEMP_FOLDER, exist_ok=True)