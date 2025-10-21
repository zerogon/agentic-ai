"""
Follow-up Questions Display Component

Provides UI components for rendering and handling follow-up question buttons.
"""
import streamlit as st
from typing import List, Optional


def display_followup_questions(
    questions: List[str],
    container: Optional[st.delta_generator.DeltaGenerator] = None
) -> None:
    """
    Display follow-up questions as clickable buttons.

    Args:
        questions: List of follow-up questions (3 questions expected)
        container: Streamlit container to render in (optional, uses default if None)

    Example:
        >>> questions = [
        ...     "다른 지역도 비교해주세요",
        ...     "상위 지역의 공통점은 무엇인가요?",
        ...     "연도별 변화 추이를 보여주세요"
        ... ]
        >>> display_followup_questions(questions)
    """
    if not questions or len(questions) == 0:
        return

    # Use provided container or create new one
    render_container = container if container else st

    # Display header
    render_container.markdown("---")
    render_container.markdown("### 💬 관련 질문을 더 해보세요")

    # Create columns for buttons (max 3 buttons in one row)
    num_questions = min(len(questions), 3)
    cols = render_container.columns(num_questions)

    # Render each question as a button
    for idx, question in enumerate(questions[:3]):
        with cols[idx]:
            # Create unique key for button
            button_key = f"followup_btn_{hash(question)}_{idx}"

            # Render button with question text
            if st.button(
                f"❓ {question}",
                key=button_key,
                use_container_width=True,
                type="secondary"
            ):
                # Handle click: Store selected question in session state
                st.session_state.pending_prompt = question
                st.rerun()


def display_followup_questions_inline(questions: List[str], message_index: int) -> None:
    """
    Display follow-up questions inline within chat history.

    Used for rendering follow-up questions that are part of message history.

    Args:
        questions: List of follow-up questions (3 questions expected)
        message_index: Index of the message in session_state.messages

    Example:
        >>> # In chat_display.py
        >>> if message.get("followup_questions"):
        ...     display_followup_questions_inline(
        ...         message["followup_questions"],
        ...         idx
        ...     )
    """
    if not questions or len(questions) == 0:
        return

    # Display header
    st.markdown("---")
    st.markdown("#### 💬 관련 질문")

    # Create columns for buttons
    num_questions = min(len(questions), 3)
    cols = st.columns(num_questions)

    # Render each question as a button
    for idx, question in enumerate(questions[:3]):
        with cols[idx]:
            # Create unique key using message index
            button_key = f"history_followup_{message_index}_{idx}"

            # Render button
            if st.button(
                f"❓ {question}",
                key=button_key,
                use_container_width=True,
                type="secondary"
            ):
                # Handle click: Store selected question
                st.session_state.pending_prompt = question
                st.rerun()


def get_followup_button_style() -> str:
    """
    Get custom CSS styling for follow-up question buttons.

    Returns:
        CSS string for button styling

    Example:
        >>> css = get_followup_button_style()
        >>> st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    """
    return """
    <style>
    /* Follow-up question button styling */
    div[data-testid="column"] button[kind="secondary"] {
        border: 1px solid rgba(49, 51, 63, 0.2);
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 14px;
        line-height: 1.4;
        transition: all 0.2s ease;
    }

    div[data-testid="column"] button[kind="secondary"]:hover {
        border-color: rgba(49, 51, 63, 0.4);
        background-color: rgba(49, 51, 63, 0.05);
        transform: translateY(-1px);
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    /* Follow-up section header */
    div[data-testid="stMarkdown"] h3:has(> :first-child:contains("💬")) {
        color: #1f77b4;
        font-size: 18px;
        margin-bottom: 12px;
    }
    </style>
    """
