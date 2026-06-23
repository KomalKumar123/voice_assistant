import streamlit as st
from speech.speech_to_text import SpeechToText
from speech.text_to_speech import TextToSpeech
from agent.road_agent import RoadAgent
from data.dataframe_store import DataFrameStore


def microphone_ui():
    """
    Renders the microphone voice interface and handles execution & playback.
    Includes text input fallback for accessibility and quiet environments.
    """
    if not st.session_state.get("file_uploaded", False):
        return

    st.subheader("Voice Interface")

    # Initialize components lazily in session state
    if "stt_engine" not in st.session_state:
        with st.spinner("Loading Whisper speech-to-text engine..."):
            st.session_state.stt_engine = SpeechToText()
            
    if "tts_engine" not in st.session_state:
        st.session_state.tts_engine = TextToSpeech()
        
    if "road_agent" not in st.session_state:
        st.session_state.road_agent = RoadAgent()

    # User controls duration of audio capture
    duration = st.slider(
        "Voice recording duration (seconds)",
        min_value=3,
        max_value=15,
        value=5,
        key="duration_slider"
    )

    col1, col2 = st.columns([1, 1])

    question = ""

    with col1:
        if st.button("🎤 Start Listening", use_container_width=True):
            stt = st.session_state.stt_engine
            with st.spinner("Listening... Speak now!"):
                audio_file = stt.record_audio(duration=duration)
                
            with st.spinner("Transcribing speech..."):
                question = stt.transcribe(audio_file)
                
            if not question.strip():
                st.warning("No speech detected. Please speak louder or try again.")

    with col2:
        manual_input = st.text_input(
            "Or type your question and press Enter:",
            key="manual_input"
        )
        if manual_input:
            question = manual_input

    # Execute analysis if a question is provided
    if question:
        st.markdown(f"**You:** *{question}*")
        
        agent = st.session_state.road_agent
        dfs = DataFrameStore.get_dfs()
        metadata = DataFrameStore.get_metadata()

        with st.spinner("Analyzing dataset..."):
            try:
                # Answer question via stateless agent
                response = agent.answer(question, dfs, metadata)

                # Show Final Answer
                st.markdown(f"**Assistant:** {response['final_answer']}")

                # Collapsible Generated Code & Result details
                with st.expander("Details (Generated Python & Raw Results)"):
                    st.markdown("**Generated Pandas Query:**")
                    st.code(response["generated_code"], language="python")
                    st.markdown("**Raw Calculations Output:**")
                    st.write(response["raw_result"])

                # Speak Answer
                with st.spinner("Synthesizing voice response..."):
                    tts = st.session_state.tts_engine
                    audio_output_path = tts.speak(response["final_answer"])
                    
                st.audio(audio_output_path, autoplay=True)

                # Append to conversation history (with the new structured contract)
                st.session_state.conversation_history.append({
                    "question": response["question"],
                    "generated_code": response["generated_code"],
                    "raw_result": response["raw_result"],
                    "final_answer": response["final_answer"]
                })
            except Exception as e:
                st.error(f"Error during query execution: {str(e)}")