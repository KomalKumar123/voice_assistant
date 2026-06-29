import streamlit as st
from session.session_manager import SessionManager
from ui.styles import inject_styles
from ui.upload_component import upload_file_ui, render_sidebar_registry
from ui.microphone_component import microphone_ui
from ui.chat_component import chat_ui
from metadata.road_registry import RoadRegistry
from config.settings import LLM_PROVIDER, MODEL_NAME

# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Road Asset Analytics Assistant",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global styles ─────────────────────────────────────────────────────────────
inject_styles()

# ── Session bootstrap ─────────────────────────────────────────────────────────
SessionManager.init_session()

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        """
        <div style='text-align:center; padding: 0.5rem 0 1rem 0;'>
            <div style='font-size:2.2rem;'>🛣️</div>
            <div style='font-size:1rem; font-weight:700; color:#e6edf3;'>
                Road Asset Analytics
            </div>
            <div style='font-size:0.72rem; color:#8b949e; margin-top:2px;'>
                Powered by Qwen3 · Fully Offline
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="section-header">Dataset Upload</div>', unsafe_allow_html=True)
    upload_file_ui()

    # ── Dataset registry ──────────────────────────────────────────────────────
    registry = RoadRegistry.get_registry()
    if registry:
        st.markdown(
            '<div class="section-header" style="margin-top:1.2rem;">Active Datasets</div>',
            unsafe_allow_html=True,
        )
        render_sidebar_registry(registry)

    # ── Controls ──────────────────────────────────────────────────────────────
    if st.session_state.get("file_uploaded", False):
        st.markdown('<div class="section-header" style="margin-top:1.2rem;">Session</div>', unsafe_allow_html=True)
        if st.button("🔄 Reset Session", use_container_width=True, key="reset_btn"):
            st.session_state.clear()
            st.rerun()

    # ── Model status ──────────────────────────────────────────────────────────
    st.markdown("---")
    is_local = LLM_PROVIDER.strip().lower() == "ollama"
    status_text = "🔒 Fully Local · No Cloud APIs" if is_local else "🌐 Cloud Integration Active"
    st.markdown(
        f"""
        <div style='text-align:center;'>
            <div class='status-online'>{LLM_PROVIDER.capitalize()} · {MODEL_NAME}</div>
        </div>
        <div style='text-align:center; margin-top:0.5rem;'>
            <span style='font-size:0.7rem; color:#484f58;'>
                {status_text}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN PANEL
# ═══════════════════════════════════════════════════════════════════════════════

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="raa-hero">
        <div class="badge">🛣️ Road Asset Analytics Engine</div>
        <h1>AI Road Asset Analytics Assistant</h1>
        <p>
            Upload your road survey Excel workbooks, then ask any analytical question
            by voice or text. The assistant understands engineering terminology,
            generates precise analytics code, and responds conversationally.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI row (when datasets are loaded) ───────────────────────────────────────
registry = RoadRegistry.get_registry()
if registry:
    total_datasets = len(registry)
    total_sheets   = sum(len(v.get("available_sheets", [])) for v in registry.values())
    total_queries  = len(st.session_state.get("conversation_history", []))

    st.markdown(
        f"""
        <div class="kpi-row">
            <div class="kpi-card">
                <div class="kpi-value">{total_datasets}</div>
                <div class="kpi-label">Datasets Loaded</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{total_sheets}</div>
                <div class="kpi-label">Survey Sheets</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{total_queries}</div>
                <div class="kpi-label">Queries Run</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Gate: show query interface only when data is loaded ──────────────────────
if not st.session_state.get("file_uploaded", False):
    st.markdown(
        """
        <div class="glass-card" style="text-align:center; padding:2.5rem;">
            <div style="font-size:3rem; margin-bottom:0.8rem;">📂</div>
            <div style="font-size:1.1rem; font-weight:600; color:#e6edf3; margin-bottom:0.4rem;">
                No Dataset Loaded
            </div>
            <div style="font-size:0.88rem; color:#8b949e;">
                Upload one or more Excel workbooks in the sidebar to begin analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    # ── Voice / Text query interface ──────────────────────────────────────────
    st.markdown('<div class="section-header">Query Interface</div>', unsafe_allow_html=True)
    microphone_ui()

    # ── Conversation history ──────────────────────────────────────────────────
    if st.session_state.get("conversation_history"):
        st.markdown('<div class="section-header" style="margin-top:1.5rem;">Conversation History</div>', unsafe_allow_html=True)
        chat_ui()