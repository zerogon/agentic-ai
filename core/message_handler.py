import streamlit as st
import pandas as pd
import re
import time
from databricks.sdk import WorkspaceClient
from utils.genie_helper import GenieHelper
from utils.data_helper import DataHelper
from utils.route_helper import RouteHelper
from utils.llm_helper import LLMHelper
from ui.session import update_current_session_messages
from core.config import get_space_id_by_domain
from concurrent.futures import ThreadPoolExecutor, as_completed


def analyze_data_with_llm(w: WorkspaceClient, prompt: str, data_list: list, llm_endpoint: str = None, stream_container=None):
    """
    Analyze data using LLM and generate insights with streaming support.

    Args:
        w: WorkspaceClient instance
        prompt: Original user query
        data_list: List of dicts with {"domain": str, "data": DataFrame, "content": str}
        llm_endpoint: LLM endpoint name (optional)
        stream_container: Streamlit container for streaming display (optional)

    Returns:
        Dict with success, content, and error keys
    """
    try:
        # Prepare data summary for LLM
        data_summary = f"Original Query: {prompt}\n\n"

        for item in data_list:
            domain = item.get("domain", "UNKNOWN")
            df = item.get("data")
            content = item.get("content", "")

            if df is not None and not df.empty:
                data_summary += f"--- {domain} ---\n"
                if content:
                    data_summary += f"Context: {content}\n"
                data_summary += f"\nData Preview ({len(df)} rows):\n"
                data_summary += df.head(10).to_string() + "\n\n"

        # Call LLM for insight analysis
        llm_helper = LLMHelper(workspace_client=w, provider="databricks")

        analysis_messages = [
            {
                "role": "system",
                "content": "You are a data analyst. Analyze the provided data and generate actionable insights, trends, and recommendations in Korean."
            },
            {
                "role": "user",
                "content": data_summary
            }
        ]

        # Get LLM endpoint from secrets or use default
        if not llm_endpoint:
            llm_endpoint = st.secrets.get("databricks", {}).get("llm_endpoint", "databricks-claude-3-7-sonnet")

        # Use streaming if container provided
        if stream_container:
            full_response = ""
            for chunk in llm_helper.chat_completion_stream(
                endpoint_name=llm_endpoint,
                messages=analysis_messages,
                temperature=0.3,
                max_tokens=2000
            ):
                full_response += chunk
                stream_container.markdown(full_response)

            # Return final response after streaming completes
            return {
                "success": True,
                "content": full_response,
                "error": None
            }
        else:
            # Non-streaming fallback
            llm_result = llm_helper.chat_completion(
                endpoint_name=llm_endpoint,
                messages=analysis_messages,
                temperature=0.3,
                max_tokens=2000
            )

            if llm_result["success"]:
                return {
                    "success": True,
                    "content": llm_result["content"],
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "content": None,
                    "error": llm_result.get("error", "Unknown error")
                }

    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": str(e)
        }


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
                            st.markdown("📋 **Action Plan**")

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
                                time.sleep(0.1)  # Delay for typing effect

                        understanding = rationale.get("understanding", "")
                        if understanding:
                            # Stream understanding text
                            st.markdown("💡 **Understanding**")
                            understanding_container = st.empty()
                            displayed_understanding = ""

                            understanding_words = understanding.split()
                            for i, word in enumerate(understanding_words):
                                displayed_understanding += word
                                if i < len(understanding_words) - 1:
                                    displayed_understanding += " "

                                understanding_container.markdown(displayed_understanding)
                                time.sleep(0.1)

                    # Select Genie Space based on routing result
                    genie_domains = routing_result["genie_domain"]

                    # Check if INSIGHT_REPORT intent is present
                    needs_insight_report = "INSIGHT_REPORT" in routing_result.get("intents", [])

                    # Check for previous data in message history
                    has_previous_data = False
                    previous_data_list = []

                    if needs_insight_report:
                        # Look for recent assistant messages with table_data
                        for msg in reversed(st.session_state.messages):
                            if msg.get("role") == "assistant" and msg.get("table_data") is not None:
                                domain = msg.get("domain", "UNKNOWN")
                                previous_data_list.append({
                                    "domain": domain,
                                    "data": msg.get("table_data"),
                                    "content": msg.get("content", "")
                                })

                                # Stop after finding the most recent data-containing message(s)
                                # If it's a multi-domain response, collect all from that exchange
                                if len(previous_data_list) >= 2:
                                    break

                        has_previous_data = len(previous_data_list) > 0

                    # Detect multi-domain scenario (SALES_GENIE + CONTRACT_GENIE)
                    is_multi_domain = (
                        len(genie_domains) >= 2 and
                        "SALES_GENIE" in genie_domains and
                        "CONTRACT_GENIE" in genie_domains
                    )

                    # Branch: Use previous data for INSIGHT_REPORT (no new Genie query)
                    if needs_insight_report and has_previous_data and not genie_domains:
                        st.caption("🔄 Analyzing previous query results...")

                        # Display previous data info
                        with st.expander("📊 Using Previous Data", expanded=False):
                            for item in previous_data_list:
                                st.write(f"**{item['domain']}**: {len(item['data'])} rows")

                        # Analyze with LLM (streaming)
                        st.markdown("### 💡 LLM Insight Analysis")
                        insight_container = st.empty()

                        # Stream LLM analysis and get result
                        llm_result = analyze_data_with_llm(w, prompt, previous_data_list, stream_container=insight_container)

                        if llm_result["success"]:
                            insight_text = llm_result["content"]

                            # Add to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"💡 **LLM Insight Analysis**\n\n{insight_text}"
                            })
                        else:
                            error_msg = f"❌ LLM Analysis Error: {llm_result.get('error', 'Unknown error')}"
                            st.error(error_msg)
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": error_msg
                            })

                        # Update session
                        update_current_session_messages()

                    elif genie_domains:
                        # Stream domain selection message
                        if is_multi_domain:
                            domain_msg = f"🎯 Using multiple Genies: {', '.join(genie_domains)}"
                        else:
                            selected_domain = genie_domains[0]
                            selected_space_id = get_space_id_by_domain(selected_domain)
                            domain_msg = f"🎯 Using {selected_domain} for this query"

                        # Stream domain message
                        domain_container = st.empty()
                        displayed_domain = ""
                        domain_words = domain_msg.split()
                        for i, word in enumerate(domain_words):
                            displayed_domain += word
                            if i < len(domain_words) - 1:
                                displayed_domain += " "
                            domain_container.caption(displayed_domain)
                            time.sleep(0.03)

                        # Detailed routing analysis (for debugging) with streaming
                        with st.expander("🔍 Routing Details", expanded=False):
                            # Stream intents
                            intents_text = f"**Intents:** {', '.join(routing_result['intents'])}"
                            intents_container = st.empty()
                            displayed_intents = ""
                            for char in intents_text:
                                displayed_intents += char
                                intents_container.markdown(displayed_intents)
                                time.sleep(0.01)

                            # Stream genie domains
                            domains_text = f"**Genie Domains:** {', '.join(routing_result['genie_domain'])}"
                            domains_container = st.empty()
                            displayed_domains = ""
                            for char in domains_text:
                                displayed_domains += char
                                domains_container.markdown(displayed_domains)
                                time.sleep(0.01)

                            # Stream keywords
                            keywords_text = f"**Keywords:** {', '.join(routing_result['keywords'])}"
                            keywords_container = st.empty()
                            displayed_keywords = ""
                            for char in keywords_text:
                                displayed_keywords += char
                                keywords_container.markdown(displayed_keywords)
                                time.sleep(0.01)
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
                                    title="Sales Data",
                                    dark_mode=True
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
                                    title="Contract Data",
                                    dark_mode=True
                                )
                                if contract_fig:
                                    st.plotly_chart(contract_fig, use_container_width=True)
                                st.dataframe(contract_data, use_container_width=True)

                        # Clear temporary storage
                        del st.session_state.multi_genie_data

                    # LLM Insight Analysis (if INSIGHT_REPORT intent detected)
                    if needs_insight_report and genie_results:
                        st.markdown("### 💡 LLM Insight Analysis")

                        # Prepare data list for LLM
                        data_list = []
                        for domain, domain_result in genie_results.items():
                            if domain_result["success"] and "result" in domain_result:
                                result_data = domain_result["result"]

                                # Extract data from response
                                if "response" in result_data:
                                    genie = GenieHelper(w, get_space_id_by_domain(domain))
                                    messages = genie.process_response(result_data["response"])

                                    for msg in messages:
                                        if msg.get("type") == "query" and not msg["data"].empty:
                                            data_list.append({
                                                "domain": domain,
                                                "data": msg["data"],
                                                "content": msg.get("content", "")
                                            })

                        # Stream LLM analysis
                        insight_container = st.empty()

                        # Get LLM endpoint
                        llm_endpoint = st.secrets.get("databricks", {}).get("llm_endpoint", "databricks-claude-3-7-sonnet")

                        # Stream and get final result
                        llm_result = analyze_data_with_llm(w, prompt, data_list, llm_endpoint, stream_container=insight_container)

                        if llm_result["success"]:
                            insight_text = llm_result["content"]

                            # Add LLM insight to chat history
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"💡 **LLM Insight Analysis**\n\n{insight_text}"
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
                    # Single-domain execution with progress tracking
                    genie = GenieHelper(w, selected_space_id)

                    # Create status container for progress
                    status_container = st.status("Processing query...", expanded=False)

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

                        if result["success"]:
                            # Store conversation ID (both legacy and new format)
                            st.session_state.conversation_id = result["conversation_id"]
                            if genie_domains and len(genie_domains) > 0:
                                st.session_state.conversation_ids[genie_domains[0]] = result["conversation_id"]

                            # Process response
                            messages = genie.process_response(result["response"])

                            # Update status to complete and expanded after successful processing
                            status_container.update(label="Query complete!", state="complete", expanded=True)

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
                                            title="Query Results",
                                            dark_mode=True
                                        )

                                        if fig:
                                            st.plotly_chart(fig, use_container_width=True)

                                        # Show data table (skip for REGION_GENIE with map visualization)
                                        is_region_genie = genie_domains and "REGION_GENIE" in genie_domains
                                        is_map_chart = selected_chart == "map"

                                        if not (is_region_genie and is_map_chart):
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

                            # LLM Insight Analysis (if INSIGHT_REPORT intent detected)
                            if needs_insight_report:
                                st.markdown("### 💡 LLM Insight Analysis")

                                # Prepare data list for LLM
                                data_list = []
                                for msg in messages:
                                    if msg.get("type") == "query" and not msg["data"].empty:
                                        data_list.append({
                                            "domain": "SINGLE_DOMAIN",
                                            "data": msg["data"],
                                            "content": msg.get("content", "")
                                        })

                                # Stream LLM analysis
                                insight_container = st.empty()

                                # Get LLM endpoint
                                llm_endpoint = st.secrets.get("databricks", {}).get("llm_endpoint", "databricks-claude-3-7-sonnet")

                                # Stream and get final result
                                llm_result = analyze_data_with_llm(w, prompt, data_list, llm_endpoint, stream_container=insight_container)

                                if llm_result["success"]:
                                    insight_text = llm_result["content"]

                                    # Add LLM insight to chat history
                                    st.session_state.messages.append({
                                        "role": "assistant",
                                        "content": f"💡 **LLM Insight Analysis**\n\n{insight_text}"
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
