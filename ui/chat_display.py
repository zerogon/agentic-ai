import streamlit as st
from ui.followup_display import display_followup_questions_inline


def display_messages():
    """Display chat messages from session state with exact state preservation."""
    for idx, message in enumerate(st.session_state.messages):
        # Generate unique key for this message based on index and content hash
        msg_hash = hash(str(message.get("content", ""))[:50])  # Hash first 50 chars for stability

        with st.chat_message(message["role"]):
            # Display content for all messages (user and assistant)
            if message["role"] == "user":
                st.markdown(message["content"])
            elif message["role"] == "assistant":
                # Show assistant content (Genie responses and LLM Analysis)
                if message.get("content"):
                    st.markdown(message["content"])

            # Display SQL code with saved expander state
            if "code" in message and message["code"]:
                # Restore expander state from message (default collapsed)
                expanded_state = message.get("sql_expanded", False)
                with st.expander("📝 Generated SQL", expanded=expanded_state):
                    st.code(message["code"], language="sql")

            # Display Plotly visualization if present
            if "chart_data" in message:
                chart_data = message["chart_data"]

                # Check if chart_data is HTML string (new format) or Figure object (legacy)
                if isinstance(chart_data, str):
                    # HTML string - render with st.components
                    st.components.v1.html(
                        chart_data,
                        height=600,
                        scrolling=True
                    )
                else:
                    # Plotly Figure object - use plotly_chart (legacy compatibility)
                    # Check if figure has custom config (e.g., for interactive maps)
                    config = getattr(chart_data, '_config', None) or {
                        'displayModeBar': True,
                        'displaylogo': False
                    }
                    st.plotly_chart(
                        chart_data,
                        use_container_width=True,
                        key=f"chart_{idx}_{msg_hash}",
                        config=config
                    )

            # Display table only if show_table flag is True (conditional display)
            if message.get("show_table", True) and "table_data" in message and not message["table_data"].empty:
                st.markdown("**📋 Data:**")
                st.dataframe(
                    message["table_data"],
                    use_container_width=True,
                    key=f"table_{idx}_{msg_hash}"
                )

            # Display follow-up questions if present (for LLM analysis messages)
            if "followup_questions" in message and message.get("followup_questions"):
                followup_questions = message["followup_questions"]
                if followup_questions and len(followup_questions) >= 3:
                    display_followup_questions_inline(followup_questions, idx)
