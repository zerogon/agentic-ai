import streamlit as st
import pandas as pd
import re
import time
from databricks.sdk import WorkspaceClient
from utils.genie_helper import GenieHelper
from utils.data_helper import DataHelper
from utils.route_helper import RouteHelper
from ui.session import update_current_session_messages
from core.config import get_space_id_by_domain
from concurrent.futures import ThreadPoolExecutor, as_completed


def execute_genie_query(w: WorkspaceClient, space_id: str, domain: str, prompt: str, conversation_id: str = None):
    """
    Execute a single Genie query with error handling.

    Args:
        w: WorkspaceClient instance
        space_id: Genie Space ID
        domain: Domain name (e.g., SALES_GENIE, CONTRACT_GENIE)
        prompt: User query
        conversation_id: Optional conversation ID for multi-turn conversation

    Returns:
        dict: {"success": bool, "domain": str, "result": dict, "error": str}
    """
    try:
        genie = GenieHelper(w, space_id)

        if conversation_id:
            # Continue existing conversation
            result = genie.continue_conversation(conversation_id, prompt)
        else:
            # Start new conversation
            result = genie.start_conversation(prompt)

        if result["success"]:
            return {
                "success": True,
                "domain": domain,
                "result": result,
                "error": None
            }
        else:
            return {
                "success": False,
                "domain": domain,
                "result": None,
                "error": result.get("error", "Unknown error")
            }

    except Exception as e:
        return {
            "success": False,
            "domain": domain,
            "result": None,
            "error": str(e)
        }


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

        # Update session history immediately after user message
        update_current_session_messages()

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Process query based on selected AI mode
        with st.chat_message("assistant"):
            if ai_mode == "Genie API" and genie_space_id:
                # Use Routing Model to analyze query with streaming
                router = RouteHelper()

                # Show loading spinner
                with st.spinner("🔍 Analyzing query..."):
                    # Collect streamed content (hidden from user)
                    streamed_text = ""
                    for chunk in router.analyze_query(prompt, stream=True):
                        streamed_text += chunk

                    # Parse the complete response
                    routing_result = router.parse_last_stream_result()

                # Now stream the execution plan with typing effect
                if routing_result["success"]:
                    rationale = routing_result.get("rationale", {})
                    if isinstance(rationale, dict):
                        execution_plan = rationale.get("execution_plan", "")

                        if execution_plan:
                            st.markdown("📋 **실행 계획**")

                            # Create placeholder for streaming text
                            plan_container = st.empty()
                            displayed_text = ""

                            # Stream word by word for better performance
                            words = execution_plan.split()
                            for i, word in enumerate(words):
                                displayed_text += word
                                if i < len(words) - 1:
                                    displayed_text += " "

                                # Update display
                                plan_container.markdown(displayed_text)
                                time.sleep(0.05)  # Delay for typing effect

                        understanding = rationale.get("understanding", "")
                        if understanding:
                            st.write(f"💡 {understanding}")

                    # Select Genie Space based on routing result
                    genie_domains = routing_result["genie_domain"]

                    # Detect multi-domain scenario (SALES_GENIE + CONTRACT_GENIE)
                    is_multi_domain = (
                        len(genie_domains) >= 2 and
                        "SALES_GENIE" in genie_domains and
                        "CONTRACT_GENIE" in genie_domains
                    )

                    if genie_domains:
                        if is_multi_domain:
                            st.caption(f"🎯 Using multiple Genies: {', '.join(genie_domains)}")
                        else:
                            selected_domain = genie_domains[0]
                            selected_space_id = get_space_id_by_domain(selected_domain)
                            st.caption(f"🎯 Using {selected_domain} for this query")

                        # Detailed routing analysis (for debugging)
                        with st.expander("🔍 Routing Details", expanded=False):
                            st.write(f"**Intents:** {', '.join(routing_result['intents'])}")
                            st.write(f"**Genie Domains:** {', '.join(routing_result['genie_domain'])}")
                            st.write(f"**Keywords:** {', '.join(routing_result['keywords'])}")
                    else:
                        selected_space_id = genie_space_id
                        st.warning("⚠️ No specific domain detected, using default Genie")
                        is_multi_domain = False
                else:
                    # Routing failed, use default
                    selected_space_id = genie_space_id
                    st.warning(f"⚠️ Routing analysis failed: {routing_result.get('error', 'Unknown error')}")
                    is_multi_domain = False

                # Execute Genie query - single or multi-domain
                if is_multi_domain:
                    # Multi-domain parallel execution with spinner
                    with st.spinner("🔄 Processing queries..."):
                        # Prepare parallel tasks
                        tasks = []
                        with ThreadPoolExecutor(max_workers=2) as executor:
                            for domain in ["SALES_GENIE", "CONTRACT_GENIE"]:
                                if domain in genie_domains:
                                    space_id = get_space_id_by_domain(domain)
                                    conv_id = st.session_state.conversation_ids.get(domain)

                                    future = executor.submit(
                                        execute_genie_query,
                                        w, space_id, domain, prompt, conv_id
                                    )
                                    tasks.append((future, domain))

                            # Collect results
                            genie_results = {}
                            for future, domain in tasks:
                                result = future.result()
                                genie_results[domain] = result

                    # Process results
                    for domain in ["SALES_GENIE", "CONTRACT_GENIE"]:
                        if domain not in genie_results:
                            continue

                        result = genie_results[domain]

                        if result["success"]:
                            # Update conversation ID for this domain
                            st.session_state.conversation_ids[domain] = result["result"]["conversation_id"]

                            # Display domain header
                            st.markdown(f"### 📊 {domain} Results")

                            # Process and display response
                            genie = GenieHelper(w, get_space_id_by_domain(domain))
                            messages = genie.process_response(result["result"]["response"])

                            for msg in messages:
                                st.markdown(msg["content"])

                                if msg.get("type") == "query":
                                    # Show SQL code
                                    if msg.get("code"):
                                        with st.expander(f"Show generated SQL ({domain})"):
                                            formatted_sql = data_helper.format_sql_code(msg["code"])
                                            st.code(formatted_sql, language="sql")

                                    # Store data for visualization
                                    if not msg["data"].empty:
                                        # Store for later side-by-side visualization
                                        if "multi_genie_data" not in st.session_state:
                                            st.session_state.multi_genie_data = {}
                                        st.session_state.multi_genie_data[domain] = {
                                            "data": msg["data"],
                                            "content": msg["content"],
                                            "code": msg.get("code")
                                        }

                                        # Add to chat history
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": f"[{domain}] {msg['content']}",
                                            "code": msg.get("code"),
                                            "table_data": msg["data"],
                                            "domain": domain
                                        })
                                    else:
                                        # Text-only response
                                        st.session_state.messages.append({
                                            "role": "assistant",
                                            "content": f"[{domain}] {msg['content']}"
                                        })
                                else:
                                    # Text-only response
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": f"[{domain}] {msg['content']}"
                                    })

                        else:
                            # Display error for this domain
                            error_msg = f"❌ {domain} Error: {result['error']}"
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })

                    # Display side-by-side visualizations
                    if "multi_genie_data" in st.session_state and len(st.session_state.multi_genie_data) == 2:
                        st.markdown("### 📈 Comparative Visualization")

                        col1, col2 = st.columns(2)

                        # SALES_GENIE - Line chart (left)
                        if "SALES_GENIE" in st.session_state.multi_genie_data:
                            sales_data = st.session_state.multi_genie_data["SALES_GENIE"]["data"]
                            with col1:
                                st.markdown("**SALES_GENIE (Line Chart)**")
                                sales_fig = data_helper.create_chart(
                                    sales_data,
                                    "line",
                                    title="Sales Data"
                                )
                                if sales_fig:
                                    st.plotly_chart(sales_fig, use_container_width=True)
                                st.dataframe(sales_data, use_container_width=True)

                        # CONTRACT_GENIE - Bar chart (right)
                        if "CONTRACT_GENIE" in st.session_state.multi_genie_data:
                            contract_data = st.session_state.multi_genie_data["CONTRACT_GENIE"]["data"]
                            with col2:
                                st.markdown("**CONTRACT_GENIE (Bar Chart)**")
                                contract_fig = data_helper.create_chart(
                                    contract_data,
                                    "bar",
                                    title="Contract Data"
                                )
                                if contract_fig:
                                    st.plotly_chart(contract_fig, use_container_width=True)
                                st.dataframe(contract_data, use_container_width=True)

                        # Clear temporary storage
                        del st.session_state.multi_genie_data

                    # Update session after all messages processed
                    update_current_session_messages()

                else:
                    # Single-domain execution with progress tracking
                    genie = GenieHelper(w, selected_space_id)

                    # Create status container for progress
                    status_container = st.status("Processing query...", expanded=True)

                    # Progress callback
                    progress_placeholder = st.empty()
                    def update_progress(icon: str, message: str):
                        progress_placeholder.markdown(f"{icon} {message}")

                    genie.set_progress_callback(update_progress)

                    with status_container:
                        # Get conversation ID from dict or legacy single ID
                        conv_id = None
                        if genie_domains and len(genie_domains) > 0:
                            conv_id = st.session_state.conversation_ids.get(genie_domains[0])
                        if not conv_id:
                            conv_id = st.session_state.conversation_id

                        if conv_id:
                            # Continue conversation
                            result = genie.continue_conversation(conv_id, prompt)
                        else:
                            # Start new conversation
                            result = genie.start_conversation(prompt)

                        status_container.update(label="Query complete!", state="complete")

                        if result["success"]:
                            # Store conversation ID (both legacy and new format)
                            st.session_state.conversation_id = result["conversation_id"]
                            if genie_domains and len(genie_domains) > 0:
                                st.session_state.conversation_ids[genie_domains[0]] = result["conversation_id"]

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

                            # Update session after all messages processed
                            update_current_session_messages()
                        else:
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

                # Update session after mock response
                update_current_session_messages()
