import datetime
import streamlit as st
import base64
from speech.speech_to_text import SpeechToText
from speech.text_to_speech import TextToSpeech
from agent.road_agent import RoadAgent
from data.dataframe_store import DataFrameStore
from dataclasses import asdict


def microphone_ui():
    """
    Renders the voice + text query interface.

    Features:
    - Big centered circular voice button
    - Hands-free recording with adaptive silence detection (stops after 3.5s of pause)
    - Manual text input fallback
    - Immediate transcription display
    - Staged progress indicators (intent → code → narration)
    - Audio output using a custom HTML element that pauses on any screen click/tap
    """
    if not st.session_state.get("file_uploaded", False):
        return

    # ── Lazy-load heavy components into session state ─────────────────────────
    if "stt_engine" not in st.session_state:
        with st.spinner("Loading Whisper speech-to-text engine…"):
            st.session_state.stt_engine = SpeechToText()

    if "tts_engine" not in st.session_state:
        st.session_state.tts_engine = TextToSpeech()

    if "road_agent" not in st.session_state:
        try:
            st.session_state.road_agent = RoadAgent()
        except ValueError as e:
            st.error(f"⚠️ **LLM Initialization Failed**: {str(e)}")
            st.info("Please check that your API key is configured correctly in the `.env` file.")
            return
        except Exception as e:
            st.error(f"⚠️ **Error initializing RoadAgent**: {str(e)}")
            return

    # ── Query input panel ─────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size:0.8rem; font-weight:600; color:#8b949e;
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.8rem; text-align:center;">
                🎙️ Ask Your Question (Voice or Text)
            </div>
        """,
        unsafe_allow_html=True,
    )

    # Centered circular mic button
    col_l, col_c, col_r = st.columns([1, 1, 1])
    question = ""

    with col_c:
        st.markdown('<div class="big-mic-container">', unsafe_allow_html=True)
        if st.button("🎤", key="big_mic_btn", use_container_width=True, help="Click and start speaking — stops recording automatically after 3-4s of silence"):
            st.session_state["_mic_active"] = True
        st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.pop("_mic_active", False):
        stt = st.session_state.stt_engine
        with st.spinner("🎙️ Listening... speak now! (Recording stops automatically after 3s of silence)"):
            audio_file = stt.record_until_silence(silence_seconds=3.5)
        with st.spinner("📝 Transcribing your speech…"):
            question = stt.transcribe(audio_file)
        if question.strip():
            st.session_state["_pending_question"] = question
            st.success(f"🗣️ Heard: *\"{question}\"*")
        else:
            st.warning("⚠️ No speech detected. Please try again.")

    # Manual text input below
    manual_input = st.text_input(
        "Or type your question here:",
        placeholder="e.g., Which road has the highest roughness in Jul-24?",
        key="manual_input",
        label_visibility="visible",
    )
    if manual_input.strip():
        st.session_state["_pending_question"] = manual_input.strip()

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Execute pipeline if a question is pending ─────────────────────────────
    pending_question = st.session_state.pop("_pending_question", "")
    if pending_question:
        _run_pipeline(pending_question)


def _run_pipeline(question: str):
    """
    Runs the full analytics pipeline for a given question and renders the result.
    """
    agent         = st.session_state.road_agent
    dataset_store = DataFrameStore.get_dataset_store()
    metadata      = DataFrameStore.get_metadata()

    # ── Stage 1: Processing indicators ─────────────────────────────────────────
    pipeline_status = st.empty()

    with pipeline_status.container():
        st.markdown(
            """
            <div class="glass-card" style="padding:1rem 1.2rem;">
                <div style="color:#8b949e; font-size:0.82rem;">
                    ⏳ Running analysis pipeline...
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    try:
        pipeline_status.empty()

        col_prog1, col_prog2, col_prog3 = st.columns(3)
        prog1 = col_prog1.empty()
        prog2 = col_prog2.empty()
        prog3 = col_prog3.empty()

        prog1.info("🧠 Parsing intent…")
        prog2.empty()
        prog3.empty()

        # Actually run the full pipeline
        with st.spinner("🔍 Analyzing dataset — this may take 10–20 seconds…"):
            response = agent.answer(question, dataset_store, metadata)

        prog1.success("✅ Intent parsed")
        prog2.success("✅ Code generated & executed")
        prog3.success("✅ Response narrated")

    except Exception as e:
        st.error(f"❌ Pipeline error: {str(e)}")
        return

    # ── Render result ─────────────────────────────────────────────────────────
    if response:
        st.markdown(
            f"""
            <div class="glass-card" style="border-color:rgba(46,160,67,0.4);">
                <div style="font-size:0.72rem; color:#2ea043; font-weight:600;
                            text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.5rem;">
                    🤖 Assistant Response
                </div>
                <div id="response-text" style="font-size:1rem; color:#e6edf3; line-height:1.6;">
                    {response["final_answer"]}
                </div>
                <div style="font-size:0.68rem; color:#484f58; margin-top:0.6rem;">
                    {response.get("timestamp", "")}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Collapsible details ───────────────────────────────────────────────
        with st.expander("🔍 RoadQuery (Parsed Parameters)", expanded=False):
            rq = asdict(response["road_query"])
            st.markdown(
                f"""
                <div class="intent-card">
                    <div class="intent-label">Structured Search Parameters</div>
                    <b>Metric:</b> {rq.get("metric") or "any"} &nbsp;|&nbsp;
                    <b>Operation:</b> {rq.get("operation") or "list"} &nbsp;|&nbsp;
                    <b>Lane:</b> {rq.get("lane") or "any"} &nbsp;|&nbsp;
                    <b>Road:</b> {rq.get("road_name") or "any"} &nbsp;|&nbsp;
                    <b>Survey Month:</b> {rq.get("survey_period") or "any"}
                    <br><br>
                    <b>Chainage Range:</b> {rq.get("chainage_start") or "0"} to {rq.get("chainage_end") or "Max"} &nbsp;|&nbsp;
                    <b>Top-K:</b> {rq.get("top_k", 1)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("⚙️ Generated Python Code", expanded=False):
            st.code(response.get("generated_code", ""), language="python")
            st.caption("Raw execution result:")
            st.write(response.get("raw_result"))

        # ── TTS playback with Tap-To-Stop screen listener ─────────────────────
        with st.spinner("🔊 Synthesizing voice response…"):
            try:
                tts = st.session_state.tts_engine
                audio_path = tts.speak(response["final_answer"])
                
                # Base64 embed the audio file so we can run a custom JavaScript listener
                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()
                audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                
                # Embed the audio player + a listener on both the local iframe and parent window
                audio_html = f"""
                <audio id="tts-audio" src="data:audio/wav;base64,{audio_b64}" autoplay></audio>
                <script>
                    const stopTTSAudio = () => {{
                        const audio = document.getElementById("tts-audio");
                        if (audio) {{
                            audio.pause();
                            audio.currentTime = 0;
                            console.log("TTS playback stopped on tap.");
                        }}
                    }};
                    // Listen to clicks inside the component iframe
                    window.addEventListener('click', stopTTSAudio);
                    
                    // Listen to clicks on the parent Streamlit container document
                    if (window.parent) {{
                        window.parent.document.addEventListener('click', stopTTSAudio);
                    }}
                </script>
                """
                st.components.v1.html(audio_html, height=0)
            except Exception as e:
                st.warning(f"⚠️ TTS unavailable: {str(e)}")

        # ── Append to conversation history ────────────────────────────────────
        st.session_state.conversation_history.append({
            "question":       response["question"],
            "road_query":     response["road_query"],
            "generated_code": response["generated_code"],
            "raw_result":     response["raw_result"],
            "final_answer":   response["final_answer"],
            "timestamp":      response.get("timestamp", datetime.datetime.now().isoformat()),
        })