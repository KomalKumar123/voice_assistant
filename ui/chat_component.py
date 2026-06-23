import streamlit as st


def chat_ui():
    """
    Renders the conversation history using Streamlit chat formatting.
    """
    if not st.session_state.get("file_uploaded", False):
        return

    history = st.session_state.get("conversation_history", [])
    if not history:
        return

    st.subheader("Conversation History")

    # Display conversation messages in chronological order
    for interaction in history:
        with st.chat_message("user"):
            st.markdown(interaction["question"])

        with st.chat_message("assistant"):
            st.markdown(interaction["final_answer"])
            
            # Collapsible execution details for past messages
            with st.expander("Show code & output details"):
                st.markdown("**Executed Pandas Query:**")
                st.code(interaction["generated_code"], language="python")
                st.markdown("**Raw Calculations Output:**")
                st.write(interaction["raw_result"])
