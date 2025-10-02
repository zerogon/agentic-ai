import streamlit as st
import pandas as pd
from datetime import datetime
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config
import os

# Import helper utilities
from utils.genie_helper import GenieHelper
from utils.data_helper import DataHelper
from utils.report_helper import ReportHelper

# Initialize Databricks WorkspaceClient
# This automatically authenticates when running on Databricks Apps

# 실행 시점에서 강제로 환경변수 제거
os.environ.pop("DATABRICKS_CLIENT_ID", None)
os.environ.pop("DATABRICKS_CLIENT_SECRET", None)

host = st.secrets["databricks"]["HOST"]
token = st.secrets["databricks"]["TOKEN"]

conf = Config(host=host, token=token)
w = WorkspaceClient(config=conf)

data_helper = DataHelper()
report_helper = ReportHelper()



# Configuration - Set your Genie Space ID here
GENIE_SPACE_ID = st.secrets.get("databricks").get("GENIE_SPACE_ID")


# Default settings (previously in sidebar)
ai_mode = "Genie API"  # Default AI mode
chart_type = "Auto"  # Default chart type
llm_endpoint = None
bedrock_model = "anthropic.claude-3-sonnet-20240229-v1:0"
bedrock_region = "us-east-1"
aws_access_key = None
aws_secret_key = None

# Page configuration
st.set_page_config(
    page_title="Databricks Data Chat",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better chat UI and sidebar (Sophisticated Dark Theme)
st.markdown("""
    <style>
    /* Main content area - Sophisticated dark gray theme */
    .stApp {
        background: linear-gradient(135deg, #1a1d23 0%, #0f1115 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        background: linear-gradient(135deg, rgba(26, 29, 35, 0.85) 0%, rgba(15, 17, 21, 0.7) 100%);
        backdrop-filter: blur(20px);
        border-radius: 1.25rem;
        padding: 2.5rem;
        margin-top: 1rem;
        border: 1px solid rgba(64, 68, 78, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 1rem;
        font-size: 1rem;
        background: rgba(32, 35, 42, 0.6) !important;
        border: 1px solid rgba(64, 68, 78, 0.25);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .stChatMessage:hover {
        border-color: rgba(96, 165, 250, 0.3);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(37, 99, 235, 0.04) 100%) !important;
        border-left: 3px solid #5b8fd4;
    }
    .stChatMessage[data-testid="assistant"] {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.08) 0%, rgba(16, 185, 129, 0.04) 100%) !important;
        border-left: 3px solid #4db89d;
    }
    .main-header {
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #e5e7eb;
        letter-spacing: -0.01em;
    }
    /* Sidebar styling - Rich dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0e12 0%, #08090c 100%);
        border-right: 1px solid rgba(64, 68, 78, 0.25);
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        padding: 1.5rem 0 !important;
        box-shadow: 2px 0 16px rgba(0, 0, 0, 0.4);
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 300px !important;
        padding: 0 !important;
    }
    /* Universal sidebar content wrapper - force consistent container width */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    /* Consistent padding for all sidebar elements */
    [data-testid="stSidebar"] .element-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        width: calc(100% - 2rem) !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Button containers - full width within padding */
    [data-testid="stSidebar"] .stButton {
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin: 0 !important;
    }
    /* Input containers - full width within padding */
    [data-testid="stSidebar"] .stTextInput {
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stTextInput > div {
        width: 100% !important;
    }
    /* Remove all emotion cache dynamic classes */
    [data-testid="stSidebar"] [class*="st-emotion-cache"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    /* Reset default Streamlit padding */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
    }
    /* Custom sidebar elements */
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #d1d5db;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        text-align: center;
        padding: 0 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .message-count {
        font-size: 0.8rem;
        color: #6b7280;
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
    }
    .sidebar-spacing {
        height: 1rem;
        padding: 0 !important;
    }
    .sidebar-section-spacing {
        height: 1.25rem;
        padding: 0 !important;
    }
    .section-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.75rem;
        text-align: center;
        padding: 0 1rem;
    }
    [data-testid="stSidebar"] h1 {
        display: none;
    }
    [data-testid="stSidebar"] h3 {
        display: none;
    }
    /* Button styling - Subtle professional theme */
    [data-testid="stSidebar"] button {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.5rem 0.75rem;
        border-radius: 0.5rem;
        white-space: nowrap;
        background: rgba(32, 35, 42, 0.6);
        border: 1px solid rgba(64, 68, 78, 0.3);
        color: #9ca3af;
        transition: all 0.25s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        min-height: auto;
        height: auto;
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] button:hover {
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(91, 143, 212, 0.4);
        color: #d1d5db;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] button:active {
        transform: translateY(0);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }
    /* New Chat button specific styling */
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button:first-of-type {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.08) 100%);
        border: 1px solid rgba(91, 143, 212, 0.35);
        color: #93c5fd;
        font-weight: 700;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] button:first-of-type:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.22) 0%, rgba(37, 99, 235, 0.12) 100%);
        border-color: rgba(91, 143, 212, 0.5);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
    }
    /* Button text container */
    [data-testid="stSidebar"] button > div {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] button p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    /* Message preview styling - Subtle card design */
    .message-preview {
        padding: 0.875rem;
        margin: 0.5rem 1rem;
        border-radius: 0.75rem;
        background: rgba(32, 35, 42, 0.5);
        border: 1px solid rgba(64, 68, 78, 0.25);
        border-left: 3px solid #5b8fd4;
        transition: all 0.3s ease;
        word-wrap: break-word;
        overflow-wrap: break-word;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        cursor: pointer;
        backdrop-filter: blur(12px);
    }
    .message-preview:hover {
        background: rgba(59, 130, 246, 0.08);
        border-left-color: #6b9fe8;
        border-color: rgba(91, 143, 212, 0.3);
        transform: translateX(3px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    }
    .role-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        color: #9ca3af;
        margin-bottom: 0.375rem;
    }
    .preview-text {
        font-size: 0.85rem;
        line-height: 1.4rem;
        color: #d1d5db;
    }
    .search-results {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
    }
    .empty-state {
        text-align: center;
        padding: 2rem 1rem;
        color: #6b7280;
        font-size: 0.875rem;
        line-height: 1.5rem;
        margin: 0 1rem;
    }
    .more-messages {
        text-align: center;
        font-size: 0.75rem;
        color: #6b7280;
        margin: 0.75rem 1rem 0;
        padding: 0.5rem;
        background: rgba(32, 35, 42, 0.4);
        border: 1px solid rgba(64, 68, 78, 0.2);
        border-radius: 0.5rem;
        backdrop-filter: blur(10px);
    }
    /* Input field styling - Subtle modern design */
    [data-testid="stSidebar"] input {
        font-size: 0.875rem;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        background: rgba(32, 35, 42, 0.5);
        color: #d1d5db;
        border: 1.5px solid rgba(64, 68, 78, 0.3);
        width: 100%;
        transition: all 0.3s ease;
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"] input:focus {
        border-color: rgba(91, 143, 212, 0.5);
        background: rgba(32, 35, 42, 0.7);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }
    [data-testid="stSidebar"] input::placeholder {
        color: #4b5563;
        font-size: 0.85rem;
    }
    /* Caption text */
    [data-testid="stSidebar"] .element-container p {
        font-size: 0.8rem;
        color: #d1d5db;
        margin: 0.5rem 0;
    }
    /* Info message styling */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #1f2937;
        border-left: 3px solid #3b82f6;
        border-radius: 0.375rem;
        padding: 0.625rem;
        font-size: 0.8rem;
    }
    /* Divider styling */
    [data-testid="stSidebar"] hr {
        display: none;
    }
    /* Sidebar collapse/expand button styling */
    [data-testid="stSidebarNav"] button,
    button[kind="header"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebarNav"] button:hover,
    button[kind="header"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebarNav"] button svg,
    button[kind="header"] svg {
        color: #9ca3af !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
    }
    [data-testid="stSidebarNav"] button:hover svg,
    button[kind="header"]:hover svg {
        color: #ffffff !important;
    }
    /* Collapsed sidebar expand button */
    [data-testid="collapsedControl"] {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="collapsedControl"]:hover {
        background-color: #3a3a3a !important;
        border-color: #525252 !important;
    }
    [data-testid="collapsedControl"] svg {
        color: #ffffff !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
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

# Main header
st.markdown('<div class="main-header">💬 Databricks Data Chat</div>', unsafe_allow_html=True)
st.markdown("Ask questions about your data in natural language and get instant insights.")
st.divider()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": f"Hello! I'm your Databricks data assistant running in **{ai_mode}** mode. Ask me anything about your data, and I'll help you with queries, visualizations, and reports."
        }
    ]

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Display SQL code if present
        if "code" in message and message["code"]:
            with st.expander("Show generated SQL"):
                st.code(message["code"], language="sql")

        # Display visualization if present
        if "chart_data" in message:
            st.plotly_chart(message["chart_data"], use_container_width=True)

        # Display table if present
        if "table_data" in message and not message["table_data"].empty:
            st.dataframe(message["table_data"], use_container_width=True)

# Chat input
if prompt := st.chat_input("Ask a question about your data..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process query based on selected AI mode
    with st.chat_message("assistant"):
        if ai_mode == "Genie API" and GENIE_SPACE_ID:
            # Use Genie API
            genie = GenieHelper(w, GENIE_SPACE_ID)

            with st.spinner("🤖 Asking Genie..."):
                if st.session_state.conversation_id:
                    # Continue conversation
                    result = genie.continue_conversation(
                        st.session_state.conversation_id,
                        prompt
                    )
                else:
                    # Start new conversation
                    result = genie.start_conversation(prompt)

                if result["success"]:
                    # Store conversation ID
                    st.session_state.conversation_id = result["conversation_id"]

                    # Process response
                    messages = genie.process_response(result["response"])

                    for msg in messages:
                        st.markdown(msg["content"])

                        if msg.get("type") == "query":
                            # Show SQL code
                            if msg.get("code"):
                                with st.expander("Show generated SQL"):
                                    formatted_sql = data_helper.format_sql_code(msg["code"])
                                    st.code(formatted_sql, language="sql")

                            # Show data and visualization
                            if not msg["data"].empty:
                                # Auto-detect or use selected chart type
                                selected_chart = chart_type.lower()
                                if selected_chart == "auto":
                                    selected_chart = data_helper.auto_detect_chart_type(msg["data"])

                                # Create chart
                                fig = data_helper.create_chart(
                                    msg["data"],
                                    selected_chart,
                                    title="Query Results"
                                )

                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)

                                # Show data table
                                st.markdown("**📋 Data:**")
                                st.dataframe(msg["data"], use_container_width=True)

                                # Add to chat history
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": msg["content"],
                                    "code": msg.get("code"),
                                    "chart_data": fig,
                                    "table_data": msg["data"]
                                })
                            else:
                                # Text-only response
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": msg["content"]
                                })
                        else:
                            # Text-only response
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg["content"]
                            })
                else:
                    error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

        

        else:
            # Mock mode (demo)
            response_text = f"**Mock Response** (Demo Mode)\n\nReceived your query: '{prompt}'\n\n"

            if not GENIE_SPACE_ID and ai_mode == "Genie API":
                response_text += "⚠️ **Please configure Genie Space ID in the sidebar to use Genie API.**\n\n"

            response_text += "**Available AI Modes:**\n"
            response_text += "- **Genie API**: Natural language to SQL with Databricks Genie\n"
            response_text += "- **LLM Endpoint**: Custom LLM via Databricks Serving Endpoints\n\n"
            response_text += "Select a mode and configure the settings in the sidebar to get started!"

            st.markdown(response_text)

            # Create sample visualization
            sample_data = pd.DataFrame({
                'Category': ['A', 'B', 'C', 'D', 'E'],
                'Value': [23, 45, 56, 78, 32]
            })

            selected_chart = chart_type.lower() if chart_type != "Auto" else "bar"
            fig = data_helper.create_chart(
                sample_data,
                selected_chart,
                title="Sample Data Visualization"
            )

            if fig:
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("**📋 Sample Data:**")
            st.dataframe(sample_data, use_container_width=True)

            # Add to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text,
                "chart_data": fig,
                "table_data": sample_data
            })

# Footer
st.divider()
st.caption("Powered by Databricks | Built with Streamlit")
