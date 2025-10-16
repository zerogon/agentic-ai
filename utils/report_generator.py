"""
Business Report Generator
Generates comprehensive business reports from chat session data using LLM analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from databricks.sdk import WorkspaceClient
from utils.llm_helper import LLMHelper
from utils.report_helper import ReportHelper
from prompts.manager import load_prompt


def generate_business_report(
    w: WorkspaceClient,
    messages: List[Dict],
    llm_endpoint: str = None,
    title: str = "Business Data Analysis Report",
    author: str = "Databricks Data Chat"
) -> Dict:
    """
    Generate a comprehensive business report from chat session messages.

    Args:
        w: WorkspaceClient instance
        messages: List of chat messages from session
        llm_endpoint: LLM endpoint name (optional)
        title: Report title
        author: Report author name

    Returns:
        Dict with success status, PDF bytes, HTML string, and error message
    """
    try:
        # Step 1: Extract conversation data
        conversation_summary = _extract_conversation_data(messages)

        if not conversation_summary["queries"]:
            return {
                "success": False,
                "error": "No data queries found in conversation",
                "pdf": None,
                "html": None
            }

        # Step 2: Generate LLM analysis
        llm_analysis = _generate_llm_analysis(
            w,
            conversation_summary,
            llm_endpoint
        )

        if not llm_analysis["success"]:
            return {
                "success": False,
                "error": llm_analysis.get("error", "LLM analysis failed"),
                "pdf": None,
                "html": None
            }

        # Step 3: Build report structure
        report = _build_report_structure(
            conversation_summary,
            llm_analysis["content"],
            title,
            author
        )

        # Step 4: Generate PDF and HTML
        pdf_bytes = report.generate_pdf(title=title, author=author)
        html_string = report.generate_html(title=title, author=author)

        return {
            "success": True,
            "pdf": pdf_bytes,
            "html": html_string,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "pdf": None,
            "html": None
        }


def _extract_conversation_data(messages: List[Dict]) -> Dict:
    """
    Extract structured data from conversation messages.

    Args:
        messages: List of chat messages

    Returns:
        Dict with queries, user questions, data samples, and domains
    """
    data = {
        "queries": [],
        "user_questions": [],
        "data_samples": [],
        "domains": set(),
        "total_messages": len(messages)
    }

    current_query = None

    for msg in messages:
        role = msg.get("role")
        content = msg.get("content", "")

        # Extract user questions
        if role == "user":
            data["user_questions"].append(content)
            current_query = {"question": content, "responses": []}

        # Extract assistant responses with data
        elif role == "assistant":
            if current_query:
                current_query["responses"].append(content)

            # Extract table data
            table_data = msg.get("table_data")
            if table_data is not None and not table_data.empty:
                domain = msg.get("domain", "UNKNOWN")
                data["domains"].add(domain)

                data_sample = {
                    "domain": domain,
                    "data": table_data,
                    "content": content,
                    "code": msg.get("code", ""),
                    "row_count": len(table_data)
                }
                data["data_samples"].append(data_sample)

                if current_query:
                    current_query["data"] = data_sample

            # Extract chart data
            chart_data = msg.get("chart_data")
            if chart_data is not None:
                if current_query and "chart" not in current_query:
                    current_query["chart"] = chart_data

            # Finalize query if we have all components
            if current_query and ("data" in current_query or "chart" in current_query):
                data["queries"].append(current_query)
                current_query = None

    return data


def _generate_llm_analysis(
    w: WorkspaceClient,
    conversation_data: Dict,
    llm_endpoint: str = None
) -> Dict:
    """
    Generate comprehensive business insights using LLM.

    Args:
        w: WorkspaceClient instance
        conversation_data: Extracted conversation data
        llm_endpoint: LLM endpoint name

    Returns:
        Dict with success status and generated content
    """
    try:
        # Prepare summary for LLM
        summary = _prepare_llm_prompt(conversation_data)

        # Initialize LLM helper
        llm_helper = LLMHelper(workspace_client=w, provider="databricks")

        # Load system prompt from prompts management system
        system_prompt = load_prompt("business_report_analyst")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": summary}
        ]

        # Get LLM endpoint
        if not llm_endpoint:
            llm_endpoint = st.secrets.get("databricks", {}).get(
                "llm_endpoint",
                "databricks-meta-llama-3-3-70b-instruct"
            )

        # Generate analysis
        result = llm_helper.chat_completion(
            endpoint_name=llm_endpoint,
            messages=messages,
            temperature=0.3,
            max_tokens=4000
        )

        if result["success"]:
            return {
                "success": True,
                "content": result["content"],
                "error": None
            }
        else:
            return {
                "success": False,
                "content": None,
                "error": result.get("error", "Unknown error")
            }

    except Exception as e:
        return {
            "success": False,
            "content": None,
            "error": str(e)
        }


def _prepare_llm_prompt(conversation_data: Dict) -> str:
    """
    Prepare detailed prompt for LLM analysis.

    Args:
        conversation_data: Extracted conversation data

    Returns:
        Formatted prompt string
    """
    prompt = "# 데이터 분석 대화 내역\n\n"
    prompt += f"**총 메시지 수**: {conversation_data['total_messages']}\n"
    prompt += f"**분석 도메인**: {', '.join(conversation_data['domains'])}\n"
    prompt += f"**데이터 쿼리 수**: {len(conversation_data['queries'])}\n\n"

    prompt += "---\n\n"

    # Add each query with context
    for idx, query in enumerate(conversation_data["queries"], 1):
        prompt += f"## 쿼리 #{idx}\n\n"
        prompt += f"**사용자 질문**: {query['question']}\n\n"

        # Add response summary
        if query.get("responses"):
            prompt += "**AI 응답**:\n"
            for resp in query["responses"]:
                # Truncate long responses
                resp_text = resp[:500] + "..." if len(resp) > 500 else resp
                prompt += f"{resp_text}\n\n"

        # Add data summary
        if query.get("data"):
            data_info = query["data"]
            df = data_info["data"]

            prompt += f"**데이터 정보**:\n"
            prompt += f"- 도메인: {data_info['domain']}\n"
            prompt += f"- 행 수: {data_info['row_count']}\n"
            prompt += f"- 컬럼: {', '.join(df.columns.tolist())}\n\n"

            # Add data preview
            prompt += "**데이터 미리보기** (처음 5행):\n"
            prompt += df.head(5).to_string() + "\n\n"

            # Add SQL code if available
            if data_info.get("code"):
                prompt += "**생성된 SQL**:\n```sql\n"
                prompt += data_info["code"] + "\n```\n\n"

        prompt += "---\n\n"

    prompt += "\n\n**분석 요청**: 위 대화 내역과 데이터를 바탕으로 종합적인 비즈니스 보고서를 작성해주세요."

    return prompt


def _build_report_structure(
    conversation_data: Dict,
    llm_analysis: str,
    title: str,
    author: str
) -> ReportHelper:
    """
    Build structured report with LLM analysis and data.

    Args:
        conversation_data: Extracted conversation data
        llm_analysis: LLM-generated analysis text
        title: Report title
        author: Report author

    Returns:
        ReportHelper instance with populated sections
    """
    report = ReportHelper()

    # Add LLM analysis as main content
    report.add_section(
        title="📊 Executive Analysis",
        content=llm_analysis,
        section_type="text"
    )

    # Add data sections for each query
    for idx, query in enumerate(conversation_data["queries"], 1):
        # Add query context
        query_title = f"Query #{idx}: {query['question'][:100]}"

        if query.get("data"):
            data_info = query["data"]

            # Add SQL code if available
            if data_info.get("code"):
                code_section = f"```sql\n{data_info['code']}\n```"
                report.add_section(
                    title=f"{query_title} - SQL",
                    content=code_section,
                    section_type="text"
                )

            # Add data table
            report.add_dataframe(
                title=f"{query_title} - Data",
                df=data_info["data"]
            )

            # Add chart if available
            if query.get("chart"):
                report.add_chart(
                    title=f"{query_title} - Visualization",
                    fig=query["chart"]
                )

    # Add metadata section
    metadata = f"""
**Report Metadata**

- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Author: {author}
- Total Queries: {len(conversation_data['queries'])}
- Domains Analyzed: {', '.join(conversation_data['domains'])}
- Data Points: {sum(q['data']['row_count'] for q in conversation_data['queries'] if q.get('data'))}
"""

    report.add_section(
        title="📋 Report Information",
        content=metadata,
        section_type="text"
    )

    return report


def generate_report_preview(messages: List[Dict]) -> Dict:
    """
    Generate quick preview of report without LLM analysis.

    Args:
        messages: List of chat messages

    Returns:
        Dict with preview statistics
    """
    data = _extract_conversation_data(messages)

    return {
        "total_messages": data["total_messages"],
        "total_queries": len(data["queries"]),
        "domains": list(data["domains"]),
        "total_data_points": sum(
            sample["row_count"]
            for sample in data["data_samples"]
        ),
        "user_questions": data["user_questions"]
    }
