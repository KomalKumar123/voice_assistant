import datetime
import streamlit as st
from speech.speech_to_text import SpeechToText
from speech.text_to_speech import TextToSpeech
from agent.road_agent import RoadAgent
from data.dataframe_store import DataFrameStore
from dataclasses import asdict


def microphone_ui():
    """
    Renders the voice + text query interface.

    Features:
    - Voice recording with configurable duration slider
    - Text input fallback
    - Staged progress spinners (intent → code → narration)
    - RoadQuery structured display
    - TTS audio playback
    - Double-fire prevention via session state flag
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
        st.session_state.road_agent = RoadAgent()

    # ── Query input panel ─────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="glass-card">
            <div style="font-size:0.8rem; font-weight:600; color:#8b949e;
                        text-transform:uppercase; letter-spacing:0.08em; margin-bottom:0.8rem;">
                🎙️ Ask Your Question
            </div>
        """,
        unsafe_allow_html=True,
    )

    col_voice, col_text = st.columns([1, 2])

    question = ""

    with col_voice:
        duration = st.slider(
            "Recording duration (s)",
            min_value=3,
            max_value=20,
            value=7,
            key="duration_slider",
            help="How many seconds to record your voice",
        )

        if st.button("🎤 Start Listening", use_container_width=True, key="mic_btn"):
            # Guard against double-fire on rerender
            st.session_state["_mic_active"] = True

        if st.session_state.pop("_mic_active", False):
            stt = st.session_state.stt_engine
            with st.spinner(f"🎙️ Recording for {duration} seconds… speak now!"):
                audio_file = stt.record_audio(duration=duration)
            with st.spinner("📝 Transcribing…"):
                question = stt.transcribe(audio_file)
            if question.strip():
                st.session_state["_pending_question"] = question
                st.info(f"🗣️ Heard: *{question}*")
            else:
                st.warning("⚠️ No speech detected. Please try again.")

    with col_text:
        manual_input = st.text_input(
            "Or type your question:",
            placeholder="e.g. What is the maximum rut depth on Road A in July?",
            key="manual_input",
            label_visibility="collapsed",
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

    # ── Stage 1: Intent parsing ───────────────────────────────────────────────
    response = None
    pipeline_status = st.empty()

    with pipeline_status.container():
        st.markdown(
            """
            <div class="glass-card" style="padding:1rem 1.2rem;">
                <div style="color:#8b949e; font-size:0.82rem;">
                    ⏳ <strong>Step 1/3</strong> — Parsing intent…
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    try:
        # We run the whole agent.answer() call — it handles all 3 steps internally.
        # Show staged feedback via placeholder updates.
        pipeline_status.empty()

        col_prog1, col_prog2, col_prog3 = st.columns(3)
        prog1 = col_prog1.empty()
        prog2 = col_prog2.empty()
        prog3 = col_prog3.empty()

        prog1.info("🧠 Parsing intent…")
        prog2.empty()
        prog3.empty()

        # Actually run the full pipeline
        with st.spinner("🔍 Analyzing dataset — this may take 15–30 seconds…"):
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
                <div style="font-size:1rem; color:#e6edf3; line-height:1.6;">
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
        with st.expander("🔍 RoadQuery (Parsed Intent)", expanded=False):
            rq = asdict(response["road_query"])
            # Pretty-print key fields
            st.markdown(
                f"""
                <div class="intent-card">
                    <div class="intent-label">Structured RoadQuery</div>
                    <b>Intent:</b> {rq.get("intent")} &nbsp;|&nbsp;
                    <b>Type:</b> {rq.get("analysis_type")} &nbsp;|&nbsp;
                    <b>Metric:</b> {rq.get("primary_metric") or "—"} &nbsp;|&nbsp;
                    <b>Op:</b> {rq.get("operation") or "—"} &nbsp;|&nbsp;
                    <b>Top-K:</b> {rq.get("top_k")}
                    <br><br>
                    <b>Roads:</b> {", ".join(rq.get("road_identifiers") or []) or "all"} &nbsp;|&nbsp;
                    <b>Periods:</b> {", ".join(rq.get("time_periods") or []) or "all"} &nbsp;|&nbsp;
                    <b>Grouping:</b> {rq.get("grouping") or "—"}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with st.expander("⚙️ Generated Python Code", expanded=False):
            st.code(response.get("generated_code", ""), language="python")
            st.caption("Raw execution result:")
            st.write(response.get("raw_result"))

        # ── TTS playback ──────────────────────────────────────────────────────
        with st.spinner("🔊 Synthesizing voice response…"):
            try:
                tts = st.session_state.tts_engine
                audio_path = tts.speak(response["final_answer"])
                st.audio(audio_path, autoplay=True)
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