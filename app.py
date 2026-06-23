import streamlit as st
from session.session_manager import SessionManager
from ui.upload_component import upload_file_ui
from ui.microphone_component import microphone_ui
from ui.chat_component import chat_ui

# Page settings
st.set_page_config(
    page_title="Road Asset Voice Assistant",
    page_icon="🛣️",
    layout="centered"
)

# Initialize session and clean previous session files
SessionManager.init_session()

# Upload component (hides itself once file is uploaded)
upload_file_ui()

# Renders Microphone control & history when dataset is loaded
if st.session_state.get("file_uploaded", False):
    if st.sidebar.button("🔄 Reset / Upload New File", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    microphone_ui()
    st.divider()
    chat_ui()