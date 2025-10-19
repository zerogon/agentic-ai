import streamlit as st
import pandas as pd
import time
from databricks.sdk import WorkspaceClient
from utils.genie_helper import GenieHelper
from utils.data_helper import DataHelper
from utils.llm_helper import LLMHelper
from utils.loading_helper import display_loading_video, remove_loading_video, update_loading_message, display_loading_with_sequential_messages, update_to_next_message
from ui.session import update_current_session_messages
from core.config import get_space_id_by_domain
from prompts.manager import load_prompt


def analyze_data_with_llm(w: WorkspaceClient, prompt: str, data_list: list, llm_endpoint: str = None, stream_container=None, spinner_container=None):
    """
    Analyze data using LLM and generate insights with streaming support.
    Supports inq-based dynamic prompt selection.

    Args:
        w: WorkspaceClient instance
        prompt: Original user query
        data_list: List of dicts with {"domain": str, "data": DataFrame, "content": str}
        llm_endpoint: LLM endpoint name (optional)
        stream_container: Streamlit container for streaming display (optional)
        spinner_container: Streamlit spinner to hide when first token arrives (optional)

    Returns:
        Dict with success, content, and error keys
    """
    try:
        from utils.prompt_selector import group_data_by_inq, get_prompt_by_inq, merge_analysis_results


        # Group data by inq values
        grouped_data = group_data_by_inq(data_list)


        # Get LLM endpoint from secrets or use default
        if not llm_endpoint:
            llm_endpoint = st.secrets.get("databricks", {}).get("llm_endpoint", "databricks-meta-llama-3-3-70b-instruct")

        # Initialize LLM helper
        llm_helper = LLMHelper(workspace_client=w, provider="databricks")

        # Process each inq group separately
        inq_results = {}

        for inq_value, group_items in grouped_data.items():
            # Select appropriate prompt for this inq value
            prompt_name = get_prompt_by_inq(inq_value)
            system_prompt = load_prompt(prompt_name)


            # Prepare data summary for this group
            data_summary = f"Original Query: {prompt}\n\n"

            for item in group_items:
                domain = item.get("domain", "UNKNOWN")
                df = item.get("data")
                content = item.get("content", "")

                if df is not None and not df.empty:
                    data_summary += f"--- {domain} ---\n"
                    if content:
                        data_summary += f"Context: {content}\n"
                    data_summary += f"\nData Preview ({len(df)} rows):\n"
                    data_summary += df.head(10).to_string() + "\n\n"

            # Prepare messages for this inq group
            analysis_messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": data_summary
                }
            ]

            # Call LLM for this group
            if stream_container and len(grouped_data) == 1:
                # Only use streaming if single group (to avoid multiple streams)
                full_response = ""
                first_token = True
                for chunk in llm_helper.chat_completion_stream(
                    endpoint_name=llm_endpoint,
                    messages=analysis_messages,
                    temperature=0.3,
                    max_tokens=2000
                ):
                    # Hide spinner when first token arrives
                    if first_token and spinner_container:
                        spinner_container.empty()
                        first_token = False

                    full_response += chunk
                    stream_container.markdown(full_response)

                inq_results[inq_value] = {
                    "success": True,
                    "content": full_response,
                    "error": None
                }
            else:
                # Non-streaming for multiple groups or no stream container
                llm_result = llm_helper.chat_completion(
                    endpoint_name=llm_endpoint,
                    messages=analysis_messages,
                    temperature=0.3,
                    max_tokens=2000
                )

                inq_results[inq_value] = llm_result

        # Merge results from all inq groups
        merged_result = merge_analysis_results(inq_results)

        # Display merged result if streaming and multiple groups
        if stream_container and len(grouped_data) > 1 and merged_result["success"]:
            stream_container.markdown(merged_result["content"])

        return merged_result

    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": str(e)
        }




def handle_chat_input(w: WorkspaceClient, config: dict):
    """Handle chat input and process responses - simplified flow with REGION_GENIE only."""
    ai_mode = config["ai_mode"]
    chart_type = config["chart_type"]
    genie_space_id = config["genie_space_id"]

    data_helper = DataHelper()

    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message immediately to trigger UI transition
        st.session_state.messages.append({"role": "user", "content": prompt})
        update_current_session_messages()

        # Store prompt for processing in next cycle
        st.session_state.pending_prompt = prompt
        st.rerun()

    # Process pending prompt if exists (after rerun with messages already added)
    if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
        prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = None  # Clear the pending prompt

        # Process query based on selected AI mode (user message already in messages list)
        with st.chat_message("assistant"):
            if ai_mode == "Genie API" and genie_space_id:
                # Simplified flow: Direct REGION_GENIE query → Map detection → LLM analysis

                # Show loading video with sequential messages
                loading_state = display_loading_with_sequential_messages(
                    messages=None,  # Use default messages from loading_helper.DEFAULT_LOADING_MESSAGES
                    interval=1.5,
                    width=600
                )
                loading_container = loading_state["container"]
                video_id = loading_state["video_id"]
                message_id = loading_state["message_id"]

                # Message 1: "Understanding query" (already shown)
                time.sleep(0.8)

                # Message 2: "Connecting to Genie"
                update_to_next_message(loading_state)
                time.sleep(0.8)

                # Get REGION_GENIE Space ID
                region_space_id = get_space_id_by_domain("REGION_GENIE")

                # Execute REGION_GENIE query
                genie = GenieHelper(w, region_space_id)

                # Message 3: "Generating SQL"
                update_to_next_message(loading_state)

                # Get conversation ID for REGION_GENIE
                conv_id = st.session_state.conversation_ids.get("REGION_GENIE")

                if conv_id:
                    # Continue conversation
                    result = genie.continue_conversation(conv_id, prompt)
                else:
                    # Start new conversation
                    result = genie.start_conversation(prompt)

                # Message 4: "Fetching data"
                update_to_next_message(loading_state)
                time.sleep(0.5)

                # Message 5: "Preparing results"
                update_to_next_message(loading_state)
                time.sleep(0.5)

                if result["success"]:
                    # Show completion message briefly
                    update_loading_message(
                        loading_container,
                        video_id,
                        message_id,
                        "Complete"
                    )
                    time.sleep(0.3)

                    # Remove loading video
                    remove_loading_video(loading_container, video_id)

                    # Store conversation ID
                    st.session_state.conversation_id = result["conversation_id"]
                    st.session_state.conversation_ids["REGION_GENIE"] = result["conversation_id"]

                    # Process response
                    messages = genie.process_response(result["response"])

                    # Process each message from Genie
                    data_for_llm = []

                    for msg in messages:
                        # Skip displaying content from Genie - only show SQL/charts/tables
                        # st.markdown(msg["content"])

                        if msg.get("type") == "query":
                            # Show SQL code in collapsible expander
                            if msg.get("code"):
                                with st.expander("📝 Generated SQL", expanded=False):
                                    formatted_sql = data_helper.format_sql_code(msg["code"])
                                    st.code(formatted_sql, language="sql")

                            # Show data and visualization
                            if not msg["data"].empty:
                                # Collect data for LLM analysis
                                data_for_llm.append({
                                    "domain": "REGION_GENIE",
                                    "data": msg["data"],
                                    "content": msg.get("content", "")
                                })

                                # Auto-detect chart type or use map
                                selected_chart = chart_type.lower()
                                if selected_chart == "auto":
                                    selected_chart = "map"  # Default to map for REGION_GENIE

                                # Create map or Plotly chart
                                folium_map = None
                                plotly_fig = None

                                if selected_chart == "map":
                                    # Try to create map (returns Plotly Figure)
                                    map_result = data_helper.create_folium_map(msg["data"])

                                    if map_result:
                                        # It's a Plotly Figure
                                        plotly_fig = map_result
                                        st.plotly_chart(
                                            plotly_fig,
                                            use_container_width=True,
                                            config={'responsive': True, 'displayModeBar': False}
                                        )
                                    else:
                                        # Fallback to bar chart if map fails
                                        plotly_fig = data_helper.create_chart(
                                            msg["data"],
                                            "bar",
                                            title="Query Results",
                                            dark_mode=True
                                        )
                                        if plotly_fig:
                                            st.plotly_chart(plotly_fig, use_container_width=True)
                                else:
                                    # Create Plotly chart for non-map visualizations
                                    plotly_fig = data_helper.create_chart(
                                        msg["data"],
                                        selected_chart,
                                        title="Query Results",
                                        dark_mode=True
                                    )

                                    if plotly_fig:
                                        st.plotly_chart(plotly_fig, use_container_width=True)

                                # Show data table (skip for maps)
                                is_map_chart = selected_chart == "map" and plotly_fig is not None

                                if not is_map_chart:
                                    st.markdown("**📋 Data:**")
                                    st.dataframe(msg["data"], use_container_width=True)

                                # Add to chat history (without content text)
                                message_data = {
                                    "role": "assistant",
                                    "content": "",  # Hide content, only show SQL/charts/tables
                                    "code": msg.get("code"),
                                    "table_data": msg["data"],
                                    "domain": "REGION_GENIE"
                                }

                                # Store chart as HTML
                                if plotly_fig:
                                    message_data["chart_data"] = plotly_fig.to_html(
                                        include_plotlyjs='cdn',
                                        div_id=f'plotly-chart-{len(st.session_state.messages)}'
                                    )

                                st.session_state.messages.append(message_data)
                            else:
                                # Text-only response
                                st.session_state.messages.append({
                                    "role": "assistant",
                                    "content": msg["content"],
                                    "domain": "REGION_GENIE"
                                })
                        else:
                            # Text-only response
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": msg["content"],
                                "domain": "REGION_GENIE"
                            })

                    # LLM Analysis (mandatory for all responses with data)
                    if data_for_llm:
                        # Create containers
                        spinner_placeholder = st.empty()
                        insight_container = st.empty()

                        # Get LLM endpoint
                        llm_endpoint = st.secrets.get("databricks", {}).get("llm_endpoint", "databricks-meta-llama-3-3-70b-instruct")

                        # Show spinner (will be hidden when first token arrives)
                        with spinner_placeholder:
                            with st.spinner("Analyzing data..."):
                                # Stream and get final result
                                llm_result = analyze_data_with_llm(
                                    w,
                                    prompt,
                                    data_for_llm,
                                    llm_endpoint,
                                    stream_container=insight_container,
                                    spinner_container=spinner_placeholder
                                )

                        if llm_result["success"]:
                            insight_text = llm_result["content"]
                            # Add LLM insight to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"💡 **LLM Analysis**\n\n{insight_text}"
                            })
                        else:
                            error_msg = f"❌ LLM Analysis Error: {llm_result.get('error', 'Unknown error')}"
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })

                    # Update session after all messages processed
                    update_current_session_messages()
                else:
                    # Remove loading video on error
                    remove_loading_video(loading_container, video_id)

                    error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    update_current_session_messages()

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
                    title="Sample Data Visualization",
                    dark_mode=True
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

                # Update session after mock response
                update_current_session_messages()
