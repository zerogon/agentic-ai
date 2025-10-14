"""
Report Validation Helper - Integration Point for Gate Agent
Coordinates Gate Agent and Data Agent for report generation validation
"""

import streamlit as st
from typing import Dict, List
from databricks.sdk import WorkspaceClient
from utils.gate_agent import GateAgent
from utils.data_agent import DataAgent
from utils.llm_helper import LLMHelper
from core.config import get_space_id_by_domain


def validate_report_generation(
    w: WorkspaceClient,
    report_type: str,
    genie_domains: List[str]
) -> Dict:
    """
    Validate if report can be generated based on data availability

    Args:
        w: WorkspaceClient instance
        report_type: Report type to validate (e.g., "monthly_sales")
        genie_domains: List of Genie domains required for report

    Returns:
        Dict with validation result:
        {
            "success": bool,
            "status": "READY" | "PARTIAL" | "BLOCKED",
            "message": str (user-friendly message),
            "missing": [list of missing elements],
            "warnings": [list of warnings],
            "llm_guidance": str (optional, LLM-generated guidance)
        }
    """
    try:
        # Initialize agents
        gate_agent = GateAgent()
        data_agent = DataAgent(w)

        # Get report condition definition
        condition = gate_agent.get_report_condition(report_type)

        if not condition:
            return {
                "success": False,
                "status": "BLOCKED",
                "message": f"리포트 타입 '{report_type}'에 대한 조건이 정의되지 않았습니다.",
                "missing": ["unknown_report_type"],
                "warnings": []
            }

        # Collect metadata from required Genie domains
        required_tables = condition.get("required_tables", [])

        with st.spinner(f"📊 Collecting metadata for {report_type} report..."):
            metadata = data_agent.collect_metadata_from_genie_spaces(
                genie_domains=genie_domains,
                table_names=required_tables,
                space_id_getter=get_space_id_by_domain
            )

        # Validate conditions with Gate Agent
        validation_result = gate_agent.validate(report_type, metadata)

        # Generate LLM guidance if needed
        if validation_result["status"] != "READY":
            try:
                llm_helper = LLMHelper(workspace_client=w, provider="databricks")
                llm_endpoint = st.secrets.get("databricks", {}).get("llm_endpoint", "databricks-claude-3-7-sonnet")

                guidance_result = gate_agent.validate_with_llm_guidance(
                    report_type=report_type,
                    datasets_metadata=metadata,
                    llm_helper=llm_helper
                )

                validation_result["llm_guidance"] = guidance_result.get("llm_guidance", "")
            except Exception as e:
                validation_result["llm_guidance"] = f"LLM 안내 생성 실패: {str(e)}"

        return {
            "success": True,
            **validation_result
        }

    except Exception as e:
        return {
            "success": False,
            "status": "BLOCKED",
            "message": f"리포트 검증 중 오류 발생: {str(e)}",
            "missing": [],
            "warnings": [],
            "error": str(e)
        }


def display_validation_result(validation_result: Dict):
    """
    Display validation result in Streamlit UI

    Args:
        validation_result: Validation result dict from validate_report_generation
    """
    status = validation_result.get("status", "BLOCKED")
    message = validation_result.get("message", "")
    missing = validation_result.get("missing", [])
    warnings = validation_result.get("warnings", [])
    llm_guidance = validation_result.get("llm_guidance")

    # Status-based display
    if status == "READY":
        st.success(f"✅ {message}")
    elif status == "PARTIAL":
        st.warning(f"⚠️ {message}")
    elif status == "BLOCKED":
        st.error(f"❌ {message}")

    # Show details in expander
    with st.expander("📋 Validation Details", expanded=(status != "READY")):
        if missing:
            st.markdown("**누락된 항목:**")
            for item in missing:
                st.markdown(f"- {item}")

        if warnings:
            st.markdown("**경고 사항:**")
            for warning in warnings:
                st.markdown(f"- {warning}")

        # Show LLM guidance if available
        if llm_guidance:
            st.markdown("**💡 AI 안내:**")
            st.markdown(llm_guidance)

    return status == "READY"
