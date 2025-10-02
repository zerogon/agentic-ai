import streamlit as st
import pandas as pd
from datetime import datetime
from databricks.sdk import WorkspaceClient
import os

# Import helper utilities
from utils.genie_helper import GenieHelper
from utils.llm_helper import LLMHelper
from utils.data_helper import DataHelper
from utils.report_helper import ReportHelper

# Initialize Databricks WorkspaceClient
# This automatically authenticates when running on Databricks Apps
w = WorkspaceClient()

# Initialize helpers
data_helper = DataHelper()
report_helper = ReportHelper()

# Configuration - Set your Genie Space ID here
GENIE_SPACE_ID = st.secrets.get("GENIE_SPACE_ID", "01f09e5ad40117acb8b6b820e30a0f8e")  # Or set via Databricks secrets

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
    layout="wide"
)

# Custom CSS for better chat UI and sidebar (Dark theme optimized)
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1.25rem;
        border-radius: 0.75rem;
        font-size: 1rem;
    }
    .main-header {
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    /* Sidebar styling - Dark theme with fixed width */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a1a 0%, #0f0f0f 100%);
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        padding: 1.5rem 1rem !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 300px !important;
        padding: 0 !important;
    }
    /* Remove emotion cache area */
    [data-testid="stSidebar"] .st-emotion-cache-1q82h82 {
        display: none !important;
    }
    [data-testid="stSidebar"] .e1wr3kle3 {
        display: none !important;
    }
    /* Hide default padding areas */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
    }
    /* Custom sidebar elements */
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }
    .message-count {
        font-size: 0.8rem;
        color: #9ca3af;
        font-weight: 500;
    }
    .sidebar-spacing {
        height: 1rem;
    }
    .sidebar-section-spacing {
        height: 1.25rem;
    }
    .section-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #d1d5db;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.75rem;
    }
    [data-testid="stSidebar"] h1 {
        display: none;
    }
    [data-testid="stSidebar"] h3 {
        display: none;
    }
    /* Button styling - Dark theme optimized */
    [data-testid="stSidebar"] button {
        font-size: 0.75rem;
        font-weight: 500;
        padding: 0.4rem 0.6rem;
        border-radius: 0.3rem;
        white-space: nowrap;
        background-color: #2d2d2d;
        border: 1px solid #404040;
        color: #ffffff;
        transition: all 0.15s ease;
        box-shadow: none;
        min-height: auto;
        height: auto;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: #3a3a3a;
        border-color: #525252;
        color: #ffffff;
    }
    [data-testid="stSidebar"] button:active {
        background-color: #252525;
        transform: scale(0.98);
    }
    /* New Chat button specific styling */
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button:first-of-type {
        background-color: #1f2937;
        border: 1px solid #3b82f6;
        color: #93c5fd;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] button:first-of-type:hover {
        background-color: #374151;
        border-color: #60a5fa;
        color: #bfdbfe;
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
    /* Message preview styling - Modern card design */
    .message-preview {
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #2d2d2d 0%, #252525 100%);
        border-left: 3px solid #3b82f6;
        transition: all 0.2s ease;
        word-wrap: break-word;
        overflow-wrap: break-word;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        cursor: pointer;
    }
    .message-preview:hover {
        background: linear-gradient(135deg, #3a3a3a 0%, #2d2d2d 100%);
        border-left-color: #60a5fa;
        transform: translateX(2px);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
    }
    .role-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        color: #d1d5db;
        margin-bottom: 0.375rem;
    }
    .preview-text {
        font-size: 0.85rem;
        line-height: 1.4rem;
        color: #f3f4f6;
    }
    .search-results {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    .empty-state {
        text-align: center;
        padding: 2rem 1rem;
        color: #9ca3af;
        font-size: 0.875rem;
        line-height: 1.5rem;
    }
    .more-messages {
        text-align: center;
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.75rem;
        padding: 0.5rem;
        background-color: #1f2937;
        border-radius: 0.375rem;
    }
    /* Input field styling - Modern design */
    [data-testid="stSidebar"] input {
        font-size: 0.875rem;
        padding: 0.625rem 0.875rem;
        border-radius: 0.5rem;
        background-color: #2d2d2d;
        color: #ffffff;
        border: 1.5px solid #404040;
        width: 100%;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] input:focus {
        border-color: #3b82f6;
        background-color: #333333;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }
    [data-testid="stSidebar"] input::placeholder {
        color: #6b7280;
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
    st.markdown('<div class="sidebar-header">💬 Databricks Chat</div>', unsafe_allow_html=True)

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

    # Clear History Button
    col_clear1, col_clear2, col_clear3 = st.columns([1, 2, 1])
    with col_clear2:
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

        elif ai_mode == "LLM Endpoint (Databricks)" and 'llm_endpoint' in locals() and llm_endpoint:
            # Use Databricks LLM Endpoint
            llm = LLMHelper(w, provider="databricks")

            with st.spinner("🤖 Calling Databricks LLM..."):
                # Build message history for context
                messages = [
                    {"role": "system", "content": "You are a helpful data analyst assistant. Help users analyze their data and answer questions."}
                ]

                # Add recent conversation history (last 5 messages)
                for msg in st.session_state.messages[-5:]:
                    if msg["role"] in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"] if msg["role"] == "user" else "assistant",
                            "content": msg["content"]
                        })

                # Add current prompt
                messages.append({"role": "user", "content": prompt})

                # Call LLM
                result = llm.chat_completion(llm_endpoint, messages)

                if result["success"]:
                    response_text = result["content"] or "No response from LLM"
                    st.markdown(response_text)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text
                    })
                else:
                    error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

        elif ai_mode == "LLM Endpoint (Bedrock)":
            # Use AWS Bedrock
            try:
                # Initialize Bedrock LLM Helper
                llm = LLMHelper(
                    provider="bedrock",
                    bedrock_region=bedrock_region,
                    aws_access_key_id=aws_access_key if aws_access_key else None,
                    aws_secret_access_key=aws_secret_key if aws_secret_key else None
                )

                with st.spinner(f"🤖 Calling AWS Bedrock ({bedrock_model.split('.')[-1]})..."):
                    # Build message history for context
                    messages = [
                        {"role": "system", "content": "You are a helpful data analyst assistant. Help users analyze their data and answer questions."}
                    ]

                    # Add recent conversation history (last 5 messages)
                    for msg in st.session_state.messages[-5:]:
                        if msg["role"] in ["user", "assistant"]:
                            messages.append({
                                "role": msg["role"] if msg["role"] == "user" else "assistant",
                                "content": msg["content"]
                            })

                    # Add current prompt
                    messages.append({"role": "user", "content": prompt})

                    # Call Bedrock
                    result = llm.chat_completion(bedrock_model, messages)

                    if result["success"]:
                        response_text = result["content"] or "No response from Bedrock"
                        st.markdown(response_text)

                        # Show token usage if available
                        if "usage" in result and result["usage"]:
                            with st.expander("📊 Token Usage"):
                                usage = result["usage"]
                                st.json(usage)

                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": response_text
                        })
                    else:
                        error_msg = f"❌ Bedrock Error: {result.get('error', 'Unknown error')}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
            except Exception as e:
                error_msg = f"❌ Bedrock Configuration Error: {str(e)}"
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
