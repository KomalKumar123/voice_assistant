import os
import streamlit as st
from data.file_manager import FileManager


class SessionManager:

    @staticmethod
    def init_session():
        """
        Initializes Streamlit session state and performs startup directory cleanup.
        Runs only once per browser session thanks to the startup_initialized guard.
        """
        if "startup_initialized" not in st.session_state:
            # --- Startup cleanup: remove previous uploads, temp files, and generated code ---
            FileManager.clear_folders()

            # --- Initialize core data stores ---
            st.session_state.dataset_store = {}      # hierarchical DataFrames
            st.session_state.road_registry = {}      # dataset registry (name, sheets)
            st.session_state.file_uploaded = False
            st.session_state.file_path = None

            # Conversation history list:
            # Each entry: {question, road_query, generated_code, raw_result, final_answer, timestamp}
            st.session_state.conversation_history = []

            # Set initialization flag so this block runs only once
            st.session_state.startup_initialized = True
