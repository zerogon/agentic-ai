import streamlit as st


def init_session_state(ai_mode: str):
    """Initialize session state for messages and conversation."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Hello! I'm your Databricks data assistant running in **{ai_mode}** mode. Ask me anything about your data, and I'll help you with queries, visualizations, and reports."
            }
        ]

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None
