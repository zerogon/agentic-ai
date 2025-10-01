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

# Page configuration
st.set_page_config(
    page_title="Databricks Data Chat",
    page_icon="💬",
    layout="wide"
)

# Custom CSS for better chat UI
st.markdown("""
    <style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    # AI Mode Selection
    st.subheader("AI Mode")
    ai_mode = st.selectbox(
        "Select AI Backend",
        ["Genie API", "LLM Endpoint (Databricks)", "LLM Endpoint (Bedrock)", "Mock (Demo)"],
        help="Choose how to process queries"
    )

    # Genie Space ID input (if using Genie)
    if ai_mode == "Genie API":
        genie_space_input = st.text_input(
            "Genie Space ID",
            value=GENIE_SPACE_ID,
            help="Enter your Genie Space ID"
        )
        if genie_space_input:
            GENIE_SPACE_ID = genie_space_input

    # LLM Endpoint input (if using Databricks LLM)
    if ai_mode == "LLM Endpoint (Databricks)":
        llm_endpoint = st.text_input(
            "LLM Endpoint Name",
            placeholder="chat-assistant-model",
            help="Enter your Databricks serving endpoint name"
        )

    # Bedrock Configuration (if using Bedrock)
    if ai_mode == "LLM Endpoint (Bedrock)":
        st.markdown("**AWS Bedrock Configuration**")

        bedrock_model = st.selectbox(
            "Claude Model",
            [
                "anthropic.claude-3-sonnet-20240229-v1:0",
                "anthropic.claude-3-opus-20240229-v1:0",
                "anthropic.claude-3-haiku-20240307-v1:0",
                "anthropic.claude-v2:1",
                "anthropic.claude-v2"
            ],
            help="Select Claude model from AWS Bedrock"
        )

        bedrock_region = st.text_input(
            "AWS Region",
            value="us-east-1",
            help="AWS region for Bedrock"
        )

        # Optional: AWS credentials (if not using environment variables)
        with st.expander("AWS Credentials (Optional)"):
            st.info("Leave empty to use environment variables or IAM role")
            aws_access_key = st.text_input("AWS Access Key ID", type="password")
            aws_secret_key = st.text_input("AWS Secret Access Key", type="password")

    st.subheader("Visualization Options")
    chart_type = st.selectbox(
        "Default Chart Type",
        ["Auto", "Bar", "Line", "Pie", "Scatter", "Heatmap"]
    )

    st.subheader("Export Options")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Export PDF", use_container_width=True):
            if len(st.session_state.messages) > 1:
                try:
                    # Build report from chat history
                    report_helper.clear()
                    report_helper.add_section("Chat Summary", f"Conversation with {len(st.session_state.messages)} messages", "text")

                    for msg in st.session_state.messages:
                        if msg["role"] == "assistant":
                            report_helper.add_section(
                                "Response",
                                msg.get("content", ""),
                                "text"
                            )
                            if "table_data" in msg and not msg["table_data"].empty:
                                report_helper.add_dataframe("Data", msg["table_data"])
                            if "chart_data" in msg:
                                report_helper.add_chart("Visualization", msg["chart_data"])

                    # Generate PDF
                    pdf_bytes = report_helper.generate_pdf(
                        title="Databricks Chat Report",
                        author=email
                    )

                    st.download_button(
                        label="⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"chat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
            else:
                st.info("Start a conversation to export reports")
    with col2:
        if st.button("🌐 Export HTML", use_container_width=True):
            if len(st.session_state.messages) > 1:
                try:
                    # Build report from chat history
                    report_helper.clear()
                    report_helper.add_section("Chat Summary", f"Conversation with {len(st.session_state.messages)} messages", "text")

                    for msg in st.session_state.messages:
                        if msg["role"] == "assistant":
                            report_helper.add_section(
                                "Response",
                                msg.get("content", ""),
                                "text"
                            )
                            if "table_data" in msg and not msg["table_data"].empty:
                                report_helper.add_dataframe("Data", msg["table_data"])
                            if "chart_data" in msg:
                                report_helper.add_chart("Visualization", msg["chart_data"])

                    # Generate HTML
                    html_content = report_helper.generate_html(
                        title="Databricks Chat Report",
                        author=email
                    )

                    st.download_button(
                        label="⬇️ Download HTML",
                        data=html_content,
                        file_name=f"chat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                except Exception as e:
                    st.error(f"HTML generation failed: {str(e)}")
            else:
                st.info("Start a conversation to export reports")

    st.divider()

    st.subheader("Session Info")
    st.text(f"Session: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Display current user info
    headers = st.context.headers
    email = headers.get("X-Forwarded-Email", "Unknown")
    st.text(f"User: {email}")
    st.text(f"Mode: {ai_mode}")

    if st.button("🗑️ Clear Chat History", use_container_width=True):
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
mode_info = f"Mode: {ai_mode}"
if ai_mode == "Genie API" and GENIE_SPACE_ID:
    mode_info += f" | Space: {GENIE_SPACE_ID[:8]}..."
st.caption(f"Powered by Databricks | Built with Streamlit | {mode_info}")
