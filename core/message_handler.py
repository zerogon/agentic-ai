import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient
from utils.genie_helper import GenieHelper
from utils.data_helper import DataHelper


def handle_chat_input(w: WorkspaceClient, config: dict):
    """Handle chat input and process responses based on AI mode."""
    ai_mode = config["ai_mode"]
    chart_type = config["chart_type"]
    genie_space_id = config["genie_space_id"]

    data_helper = DataHelper()

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process query based on selected AI mode
        with st.chat_message("assistant"):
            if ai_mode == "Genie API" and genie_space_id:
                # Use Genie API
                genie = GenieHelper(w, genie_space_id)

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
                response_text = f"**Mock Response** (Demo Mode)\\n\\nReceived your query: '{prompt}'\\n\\n"

                if not genie_space_id and ai_mode == "Genie API":
                    response_text += "⚠️ **Please configure Genie Space ID in the sidebar to use Genie API.**\\n\\n"

                response_text += "**Available AI Modes:**\\n"
                response_text += "- **Genie API**: Natural language to SQL with Databricks Genie\\n"
                response_text += "- **LLM Endpoint**: Custom LLM via Databricks Serving Endpoints\\n\\n"
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
