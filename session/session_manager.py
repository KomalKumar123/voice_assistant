import streamlit as st
from data.file_manager import FileManager


class SessionManager:

    @staticmethod
    def init_session():
        """
        Initializes Streamlit session variables and performs startup directory cleanup.
        """
        if "startup_initialized" not in st.session_state:
            # Clean previous uploads and audio recordings
            FileManager.clear_folders()

            # Initialize states
            st.session_state.file_uploaded = False
            st.session_state.file_path = None
            st.session_state.dfs = {}
            st.session_state.metadata = {}
            
            # Conversation history structure:
            # list of {"question": str, "generated_code": str, "raw_result": Any, "final_answer": str}
            st.session_state.conversation_history = []

            # Set initialization flag
            st.session_state.startup_initialized = True
