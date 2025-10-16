import streamlit as st
import uuid
from datetime import datetime


def init_session_state(ai_mode: str):
    """Initialize session state for messages and conversation."""
    # Initialize chat sessions list (stores all chat histories)
    if "chat_sessions" not in st.session_state:
        st.session_state.chat_sessions = []

    # Initialize current session ID
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = None

    # Create first session if none exists
    if not st.session_state.chat_sessions:
        create_new_session(ai_mode)

    # Load current session messages
    if "messages" not in st.session_state:
        st.session_state.messages = get_current_session_messages()

    # Initialize conversation IDs for multi-Genie support
    if "conversation_ids" not in st.session_state:
        st.session_state.conversation_ids = {}

    # Legacy single conversation_id support (backward compatibility)
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = None


def create_new_session(ai_mode: str):
    """Create a new chat session."""
    session_id = str(uuid.uuid4())

    new_session = {
        "id": session_id,
        "created_at": datetime.now(),
        "messages": [],  # Start with empty messages to show landing page
        "first_user_message": None  # Will be set when user sends first message
    }

    st.session_state.chat_sessions.insert(0, new_session)  # Add to beginning
    st.session_state.current_session_id = session_id
    st.session_state.messages = []  # Empty messages to trigger landing page

    # Clear Genie conversation IDs for new session
    if "conversation_ids" in st.session_state:
        st.session_state.conversation_ids = {}
    if "conversation_id" in st.session_state:
        st.session_state.conversation_id = None

    return session_id


def switch_session(session_id: str):
    """Switch to a different chat session."""
    session = next((s for s in st.session_state.chat_sessions if s["id"] == session_id), None)

    if session:
        st.session_state.current_session_id = session_id
        st.session_state.messages = session["messages"].copy()

        # Clear Genie conversation IDs when switching sessions
        if "conversation_ids" in st.session_state:
            st.session_state.conversation_ids = {}
        if "conversation_id" in st.session_state:
            st.session_state.conversation_id = None


def get_current_session_messages():
    """Get messages for the current session."""
    if not st.session_state.current_session_id:
        return []

    session = next((s for s in st.session_state.chat_sessions if s["id"] == st.session_state.current_session_id), None)
    return session["messages"] if session else []


def update_current_session_messages():
    """Update the current session's messages from st.session_state.messages."""
    if not st.session_state.current_session_id:
        return

    for session in st.session_state.chat_sessions:
        if session["id"] == st.session_state.current_session_id:
            session["messages"] = st.session_state.messages.copy()

            # Update first_user_message if not set
            if session["first_user_message"] is None:
                user_messages = [msg for msg in st.session_state.messages if msg["role"] == "user"]
                if user_messages:
                    session["first_user_message"] = user_messages[0]["content"]
            break


def get_session_preview(session):
    """Get a preview text for a chat session."""
    if session["first_user_message"]:
        preview = session["first_user_message"]
        return preview[:50] + "..." if len(preview) > 50 else preview
    else:
        return "New conversation"
