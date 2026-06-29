import os
import shutil
from config.settings import UPLOAD_FOLDER, TEMP_FOLDER, LOGS_FOLDER


class FileManager:

    @staticmethod
    def save_uploaded_file(uploaded_file, dataset_id: str) -> str:
        """
        Saves an uploaded Streamlit file object to disk with a unique filename
        derived from the dataset_id, so multiple uploads never overwrite each other.

        Args:
            uploaded_file: Streamlit UploadedFile object.
            dataset_id (str): Unique dataset identifier (e.g. 'dataset_1').

        Returns:
            str: Absolute path to the saved file.
        """
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        # Use dataset_id as the filename to guarantee uniqueness across uploads
        safe_name = f"{dataset_id}.xlsx"
        file_path = os.path.join(UPLOAD_FOLDER, safe_name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path

    @staticmethod
    def clear_folders():
        """
        Removes and recreates the upload and temp working directories.
        The logs directory is preserved (it accumulates conversation history).
        """
        for folder in (UPLOAD_FOLDER, TEMP_FOLDER):
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                except Exception:
                    pass
            os.makedirs(folder, exist_ok=True)

        # Ensure logs folder exists but never delete it
        os.makedirs(LOGS_FOLDER, exist_ok=True)