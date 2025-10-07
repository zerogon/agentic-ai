import streamlit as st
from ui.session import create_new_session, switch_session, get_session_preview
from core.config import get_config, init_databricks_client
from utils.report_generator import generate_business_report, generate_report_preview
from datetime import datetime


def render_sidebar():
    """Render the sidebar with chat history, search, and controls."""
    with st.sidebar:
        # Header with title and message count
        st.markdown('<div class="sidebar-header">Databricks Chat</div>', unsafe_allow_html=True)

        total_messages = len(st.session_state.get("messages", []))
        if total_messages > 0:
            st.markdown(f'<div class="message-count">{total_messages} messages</div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-spacing"></div>', unsafe_allow_html=True)

        # New Chat Button
        if st.button("✨ New Chat", use_container_width=True, key="new_chat_btn"):
            config = get_config()
            create_new_session(config["ai_mode"])
            st.rerun()

        st.markdown('<div class="sidebar-section-spacing"></div>', unsafe_allow_html=True)

        # Chat Search
        search_query = st.text_input(
            "Search",
            placeholder="🔍 Search messages...",
            label_visibility="collapsed",
            key="search_input"
        )

        st.markdown('<div class="sidebar-section-spacing"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Recent Chats</div>', unsafe_allow_html=True)

        # Display chat sessions
        chat_sessions = st.session_state.get("chat_sessions", [])

        if search_query:
            # Filter sessions by search query
            filtered_sessions = [
                session for session in chat_sessions
                if any(search_query.lower() in msg.get("content", "").lower() for msg in session["messages"])
            ]

            if filtered_sessions:
                st.markdown(f'<div class="search-results">{len(filtered_sessions)} sessions found</div>', unsafe_allow_html=True)
                for session in filtered_sessions:
                    is_current = session["id"] == st.session_state.get("current_session_id")
                    preview = get_session_preview(session)
                    timestamp = session["created_at"].strftime("%m/%d %H:%M")

                    # Create clickable session button
                    button_key = f"session_{session['id']}"
                    button_label = f"{'📍' if is_current else '💬'} {preview}"

                    if st.button(button_label, key=button_key, use_container_width=True):
                        if not is_current:
                            switch_session(session["id"])
                            st.rerun()

                    # Show timestamp below button
                    st.markdown(
                        f'<div style="font-size: 0.7rem; color: #6b7280; margin-top: -8px; margin-bottom: 8px; padding-left: 8px;">{timestamp}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div class="empty-state">No sessions found</div>', unsafe_allow_html=True)
        else:
            # Show all chat sessions
            if chat_sessions:
                # Show recent sessions (max 10)
                recent_sessions = chat_sessions[:10]
                for session in recent_sessions:
                    is_current = session["id"] == st.session_state.get("current_session_id")
                    preview = get_session_preview(session)
                    timestamp = session["created_at"].strftime("%m/%d %H:%M")

                    # Create clickable session button
                    button_key = f"session_{session['id']}"
                    button_label = f"{'📍' if is_current else '💬'} {preview}"

                    if st.button(button_label, key=button_key, use_container_width=True):
                        if not is_current:
                            switch_session(session["id"])
                            st.rerun()

                    # Show timestamp below button
                    st.markdown(
                        f'<div style="font-size: 0.7rem; color: #6b7280; margin-top: -8px; margin-bottom: 8px; padding-left: 8px;">{timestamp}</div>',
                        unsafe_allow_html=True
                    )

                if len(chat_sessions) > 10:
                    st.markdown(f'<div class="more-messages">+{len(chat_sessions) - 10} more sessions</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state">💬 No chats yet<br><span style="font-size: 0.75rem; color: #6b7280;">Start a conversation!</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-spacing"></div>', unsafe_allow_html=True)

        # Report Generation Section
        if total_messages > 0:
            st.markdown('<div class="section-title">📊 Reports</div>', unsafe_allow_html=True)

            # Generate report preview
            messages = st.session_state.get("messages", [])
            preview = generate_report_preview(messages)

            # Show report stats
            if preview["total_queries"] > 0:
                with st.expander("Report Preview", expanded=False):
                    st.markdown(f"**Queries**: {preview['total_queries']}")
                    st.markdown(f"**Domains**: {', '.join(preview['domains']) if preview['domains'] else 'None'}")
                    st.markdown(f"**Data Points**: {preview['total_data_points']:,}")

                # Initialize report data in session state
                if "generated_report" not in st.session_state:
                    st.session_state.generated_report = None

                # Generate Report Button
                if st.button("📄 Generate Business Report", use_container_width=True, key="gen_report_btn"):
                    with st.spinner("Generating comprehensive report..."):
                        # Get Databricks client
                        w = init_databricks_client()

                        # Generate report
                        result = generate_business_report(
                            w=w,
                            messages=messages,
                            title=f"Business Analysis Report - {datetime.now().strftime('%Y-%m-%d')}",
                            author="Databricks Data Chat"
                        )

                        # Store result in session state
                        st.session_state.generated_report = result

                # Show download buttons if report exists
                if st.session_state.generated_report is not None:
                    result = st.session_state.generated_report

                    if result["success"]:
                        st.success("✅ Report generated successfully!")

                        # Create download buttons
                        col1, col2 = st.columns(2)

                        with col1:
                            st.download_button(
                                label="📥 Download PDF",
                                data=result["pdf"],
                                file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                                key="download_pdf_btn"
                            )

                        with col2:
                            st.download_button(
                                label="📥 Download HTML",
                                data=result["html"],
                                file_name=f"business_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                mime="text/html",
                                use_container_width=True,
                                key="download_html_btn"
                            )

                        # Clear report button
                        if st.button("🔄 Generate New Report", use_container_width=True, key="clear_report_btn"):
                            st.session_state.generated_report = None
                            st.rerun()
                    else:
                        st.error(f"❌ Report generation failed: {result.get('error', 'Unknown error')}")
                        if st.button("🔄 Try Again", use_container_width=True, key="retry_report_btn"):
                            st.session_state.generated_report = None
                            st.rerun()
            else:
                st.info("💡 Chat with data to enable report generation")

            st.markdown('<div class="sidebar-section-spacing"></div>', unsafe_allow_html=True)

        # Clear All Sessions Button
        if st.button("🗑️ Clear All Sessions", use_container_width=True, key="clear_btn"):
            st.session_state.chat_sessions = []
            st.session_state.current_session_id = None
            config = get_config()
            create_new_session(config["ai_mode"])
            st.rerun()
