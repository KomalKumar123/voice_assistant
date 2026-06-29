import streamlit as st
from dataclasses import asdict


def chat_ui():
    """
    Renders the full conversation history using premium chat bubble styling.

    Each interaction shows:
    - User question (right-aligned bubble)
    - Assistant answer (left-aligned bubble)
    - Timestamp
    - Collapsible RoadQuery + generated code + raw result
    """
    history = st.session_state.get("conversation_history", [])
    if not history:
        return

    for idx, interaction in enumerate(reversed(history)):
        ts = interaction.get("timestamp", "")
        # Format timestamp for display (ISO → human-readable if possible)
        try:
            from datetime import datetime
            dt_obj = datetime.fromisoformat(ts)
            ts_display = dt_obj.strftime("%d %b %Y  %H:%M:%S")
        except Exception:
            ts_display = ts

        entry_num = len(history) - idx  # descending display

        # ── User bubble ───────────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-end; margin-bottom:0.2rem;">
                <div class="chat-user-bubble">
                    <span style="font-size:0.72rem; color:#388bfd; font-weight:600;
                                 display:block; margin-bottom:3px;">
                        🧑 You · #{entry_num}
                    </span>
                    {interaction["question"]}
                    <div class="chat-timestamp">{ts_display}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Assistant bubble ──────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="display:flex; justify-content:flex-start; margin-bottom:0.8rem;">
                <div class="chat-assistant-bubble">
                    <span style="font-size:0.72rem; color:#2ea043; font-weight:600;
                                 display:block; margin-bottom:3px;">
                        🤖 Assistant
                    </span>
                    {interaction["final_answer"]}
                    <div class="chat-timestamp">{ts_display}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Collapsible details ───────────────────────────────────────────────
        with st.expander(f"📋 Query #{entry_num} — Details", expanded=False):
            # RoadQuery summary
            rq_obj  = interaction.get("road_query")
            if rq_obj is not None:
                try:
                    rq = asdict(rq_obj)
                except Exception:
                    rq = rq_obj if isinstance(rq_obj, dict) else {}

                st.markdown(
                    f"""
                    <div class="intent-card">
                        <div class="intent-label">RoadQuery</div>
                        <b>Intent:</b> {rq.get("intent")} &nbsp;|&nbsp;
                        <b>Type:</b> {rq.get("analysis_type")} &nbsp;|&nbsp;
                        <b>Metric:</b> {rq.get("primary_metric") or "—"} &nbsp;|&nbsp;
                        <b>Operation:</b> {rq.get("operation") or "—"} &nbsp;|&nbsp;
                        <b>Top-K:</b> {rq.get("top_k", 1)}
                        <br><br>
                        <b>Road IDs:</b>  {", ".join(rq.get("road_identifiers") or []) or "all"} &nbsp;|&nbsp;
                        <b>Periods:</b>   {", ".join(rq.get("time_periods") or []) or "all"} &nbsp;|&nbsp;
                        <b>Grouping:</b>  {rq.get("grouping") or "—"} &nbsp;|&nbsp;
                        <b>Filters:</b>   {rq.get("filters") or "none"}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Generated code
            code = interaction.get("generated_code", "")
            if code:
                st.markdown("**Generated Pandas Code:**")
                st.code(code, language="python")

            # Raw result
            raw = interaction.get("raw_result")
            if raw is not None:
                st.markdown("**Raw Execution Result:**")
                st.write(raw)

        st.markdown(
            "<hr style='margin:0.3rem 0 0.8rem 0; border-color:rgba(48,54,61,0.5);'>",
            unsafe_allow_html=True,
        )
