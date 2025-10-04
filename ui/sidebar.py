import streamlit as st


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
            st.session_state.messages = []
            if "conversation_id" in st.session_state:
                del st.session_state.conversation_id
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

        # Chat history container
        if search_query:
            # Filter messages by search query
            filtered_messages = [
                msg for msg in st.session_state.get("messages", [])
                if search_query.lower() in msg.get("content", "").lower()
            ]

            if filtered_messages:
                st.markdown(f'<div class="search-results">{len(filtered_messages)} results</div>', unsafe_allow_html=True)
                for idx, msg in enumerate(filtered_messages):
                    role_icon = "👤" if msg["role"] == "user" else "🤖"
                    role_label = "You" if msg["role"] == "user" else "AI"
                    preview = msg["content"][:55] + "..." if len(msg["content"]) > 55 else msg["content"]
                    st.markdown(
                        f'<div class="message-preview"><span class="role-badge">{role_icon} {role_label}</span><div class="preview-text">{preview}</div></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div class="empty-state">No messages found</div>', unsafe_allow_html=True)
        else:
            # Show all messages
            if total_messages > 0:
                # Show recent messages (last 8)
                recent_messages = st.session_state.get("messages", [])[-8:]
                for idx, msg in enumerate(recent_messages):
                    role_icon = "👤" if msg["role"] == "user" else "🤖"
                    role_label = "You" if msg["role"] == "user" else "AI"
                    preview = msg["content"][:55] + "..." if len(msg["content"]) > 55 else msg["content"]
                    st.markdown(
                        f'<div class="message-preview"><span class="role-badge">{role_icon} {role_label}</span><div class="preview-text">{preview}</div></div>',
                        unsafe_allow_html=True
                    )
                if total_messages > 8:
                    st.markdown(f'<div class="more-messages">+{total_messages - 8} more messages</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="empty-state">💬 No messages yet<br><span style="font-size: 0.75rem; color: #6b7280;">Start a conversation!</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="sidebar-section-spacing"></div>', unsafe_allow_html=True)

        # Clear History Button - centered
        if st.button("🗑️ Clear All", use_container_width=True, key="clear_btn"):
            st.session_state.messages = []
            if "conversation_id" in st.session_state:
                del st.session_state.conversation_id
            st.rerun()
