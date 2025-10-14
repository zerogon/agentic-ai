"""
Gate Agent - Report Generation Condition Validation
Validates data availability and quality against YAML-defined conditions
"""

import yaml
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path


class GateAgent:
    """
    Gate Agent for validating report generation conditions

    Validates:
    - Required tables existence
    - Required columns presence
    - Minimum row count
    - Data freshness (last_updated)
    - Period requirements
    """

    def __init__(self, conditions_file: str = None):
        """
        Initialize Gate Agent with condition file

        Args:
            conditions_file: Path to YAML conditions file (defaults to config/report_conditions.yaml)
        """
        if conditions_file is None:
            # Default to config/report_conditions.yaml
            project_root = Path(__file__).parent.parent
            conditions_file = project_root / "config" / "report_conditions.yaml"

        self.conditions_file = conditions_file
        self.conditions = self._load_conditions()

    def _load_conditions(self) -> Dict:
        """
        Load report conditions from YAML file

        Returns:
            Dict of report conditions
        """
        try:
            with open(self.conditions_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data.get('report_conditions', {})
        except FileNotFoundError:
            raise FileNotFoundError(f"Conditions file not found: {self.conditions_file}")
        except yaml.YAMLError as e:
            raise ValueError(f"Failed to parse YAML: {str(e)}")

    def get_available_report_types(self) -> List[str]:
        """
        Get list of available report types

        Returns:
            List of report type names
        """
        return list(self.conditions.keys())

    def get_report_condition(self, report_type: str) -> Optional[Dict]:
        """
        Get condition definition for specific report type

        Args:
            report_type: Report type name

        Returns:
            Condition dict or None if not found
        """
        return self.conditions.get(report_type)

    def validate(self, report_type: str, datasets_metadata: Dict) -> Dict:
        """
        Validate if report can be generated based on available data

        Args:
            report_type: Report type to validate (e.g., "monthly_sales")
            datasets_metadata: Dict of available datasets with metadata
                Format: {
                    "table_name": {
                        "columns": ["col1", "col2"],
                        "rows": 100,
                        "last_updated": "2025-10-12T14:00:00Z"
                    }
                }

        Returns:
            Dict with validation result:
            {
                "report_type": str,
                "status": "READY" | "PARTIAL" | "BLOCKED",
                "missing": [list of missing elements],
                "warnings": [list of warnings],
                "message": str (user-friendly message),
                "details": {
                    "tables_validated": bool,
                    "columns_validated": bool,
                    "rows_validated": bool,
                    "freshness_validated": bool
                }
            }
        """
        condition = self.get_report_condition(report_type)

        if not condition:
            return {
                "report_type": report_type,
                "status": "BLOCKED",
                "missing": ["unknown_report_type"],
                "warnings": [],
                "message": f"리포트 타입 '{report_type}'에 대한 조건이 정의되지 않았습니다.",
                "details": {}
            }

        missing = []
        warnings = []
        details = {
            "tables_validated": False,
            "columns_validated": False,
            "rows_validated": False,
            "freshness_validated": False
        }

        # 1. Validate required tables
        required_tables = condition.get("required_tables", [])
        available_tables = set(datasets_metadata.keys())
        missing_tables = [table for table in required_tables if table not in available_tables]

        if missing_tables:
            missing.extend(missing_tables)
        else:
            details["tables_validated"] = True

        # 2. Validate required columns
        required_columns = condition.get("required_columns", {})
        for table, cols in required_columns.items():
            if table not in datasets_metadata:
                continue  # Already flagged in table validation

            table_meta = datasets_metadata[table]
            available_cols = set(table_meta.get("columns", []))
            missing_cols = [col for col in cols if col not in available_cols]

            if missing_cols:
                missing.append(f"{table}: {', '.join(missing_cols)}")

        if not missing or len([m for m in missing if ":" in m]) == 0:
            details["columns_validated"] = True

        # 3. Validate minimum rows
        min_rows = condition.get("min_rows", 0)
        for table in required_tables:
            if table not in datasets_metadata:
                continue

            table_meta = datasets_metadata[table]
            actual_rows = table_meta.get("rows", 0)

            if actual_rows < min_rows:
                warnings.append(f"{table}: {actual_rows} rows (minimum: {min_rows})")

        if not warnings:
            details["rows_validated"] = True

        # 4. Validate data freshness
        freshness_days = condition.get("freshness_days")
        if freshness_days:
            from datetime import timezone
            now = datetime.now(timezone.utc)
            threshold = now - timedelta(days=freshness_days)

            for table in required_tables:
                if table not in datasets_metadata:
                    continue

                table_meta = datasets_metadata[table]
                last_updated_str = table_meta.get("last_updated")

                if last_updated_str:
                    try:
                        # Parse ISO format timestamp
                        last_updated = datetime.fromisoformat(last_updated_str.replace('Z', '+00:00'))

                        if last_updated < threshold:
                            warnings.append(f"{table}: Last updated {last_updated.date()} (older than {freshness_days} days)")
                    except ValueError:
                        warnings.append(f"{table}: Invalid timestamp format")

        if not warnings or not freshness_days:
            details["freshness_validated"] = True

        # Determine status
        if missing:
            status = "BLOCKED"
            message = f"{condition.get('description', report_type)} 리포트를 생성할 수 없습니다. 필수 데이터가 누락되었습니다."
        elif warnings:
            status = "PARTIAL"
            message = f"{condition.get('description', report_type)} 리포트를 생성할 수 있지만, 일부 데이터 품질 문제가 있습니다."
        else:
            status = "READY"
            message = f"{condition.get('description', report_type)} 리포트 생성 조건이 충족되었습니다."

        return {
            "report_type": report_type,
            "status": status,
            "missing": missing,
            "warnings": warnings,
            "message": message,
            "details": details,
            "condition": condition
        }

    def validate_with_llm_guidance(self, report_type: str, datasets_metadata: Dict, llm_helper=None) -> Dict:
        """
        Validate report conditions and generate LLM-based user guidance

        Args:
            report_type: Report type to validate
            datasets_metadata: Available datasets metadata
            llm_helper: Optional LLMHelper instance for generating guidance

        Returns:
            Validation result with LLM-generated guidance message
        """
        validation_result = self.validate(report_type, datasets_metadata)

        # If LLM helper provided, generate natural language guidance
        if llm_helper and validation_result["status"] != "READY":
            guidance_prompt = self._generate_guidance_prompt(validation_result)

            try:
                llm_response = llm_helper.chat_completion(
                    messages=[
                        {"role": "system", "content": "너는 데이터 분석 시스템의 안내 에이전트입니다. 사용자에게 리포트 생성 조건 미충족 상황을 명확하고 친절하게 설명해주세요."},
                        {"role": "user", "content": guidance_prompt}
                    ],
                    temperature=0.3,
                    max_tokens=500
                )

                if llm_response.get("success"):
                    validation_result["llm_guidance"] = llm_response["content"]
            except Exception as e:
                validation_result["llm_guidance"] = f"LLM 안내 생성 실패: {str(e)}"

        return validation_result

    def _generate_guidance_prompt(self, validation_result: Dict) -> str:
        """
        Generate prompt for LLM to create user guidance

        Args:
            validation_result: Validation result dict

        Returns:
            Formatted prompt string
        """
        prompt = f"""리포트 생성 조건 검증 결과:

리포트 타입: {validation_result['report_type']}
상태: {validation_result['status']}

누락된 항목:
{chr(10).join(['- ' + item for item in validation_result['missing']]) if validation_result['missing'] else '(없음)'}

경고 사항:
{chr(10).join(['- ' + item for item in validation_result['warnings']]) if validation_result['warnings'] else '(없음)'}

위 검증 결과를 바탕으로, 사용자에게 어떤 데이터가 부족한지, 어떻게 해결할 수 있는지 명확하고 친절하게 안내해주세요.
"""
        return prompt
