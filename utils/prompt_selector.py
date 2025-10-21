"""
Prompt selector for inq-based dynamic prompt selection.

This module provides functions to select appropriate analysis prompts
based on the 'inq' column value in query results.
"""
from typing import Optional
import pandas as pd


def get_prompt_by_inq(inq_value: str) -> str:
    """
    Get the appropriate prompt name based on inq value.

    Args:
        inq_value: The inq column value (p1, p2, p3, p4, p5)

    Returns:
        Prompt name to use for analysis

    Example:
        >>> get_prompt_by_inq("p1")
        "p1_analyst"
        >>> get_prompt_by_inq("p5")
        "p5_analyst"
        >>> get_prompt_by_inq("unknown")
        "data_analyst"
    """
    # Normalize input (handle case variations)
    inq_normalized = str(inq_value).lower().strip()

    # Prompt mapping
    prompt_mapping = {
        "p1": "p1_analyst",
        "p2": "p2_analyst",
        "p3": "p3_analyst",
        "p4": "p4_analyst",
        "p5": "p5_analyst"
    }

    # Return mapped prompt or default
    return prompt_mapping.get(inq_normalized, "data_analyst")


def detect_inq_column(df: pd.DataFrame) -> Optional[str]:
    """
    Detect the inq column name in a DataFrame.

    Args:
        df: DataFrame to check for inq column

    Returns:
        Column name if found, None otherwise

    Example:
        >>> df = pd.DataFrame({"inq": ["p1", "p2"], "value": [1, 2]})
        >>> detect_inq_column(df)
        "inq"
    """
    # Check for exact match first
    if "inq" in df.columns:
        return "inq"

    # Check for case-insensitive match
    for col in df.columns:
        if col.lower() == "inq":
            return col

    return None


def group_data_by_inq(data_list: list) -> dict:
    """
    Group data items by their inq values.

    Args:
        data_list: List of dicts with {"domain": str, "data": DataFrame, "content": str}

    Returns:
        Dictionary mapping inq values to grouped data items
        {
            "p1": [{"domain": ..., "data": ..., "content": ...}, ...],
            "p2": [...],
            ...
        }

    Example:
        >>> data_list = [
        ...     {"domain": "REGION", "data": df_with_p1, "content": "..."},
        ...     {"domain": "REGION", "data": df_with_p2, "content": "..."}
        ... ]
        >>> grouped = group_data_by_inq(data_list)
        >>> "p1" in grouped
        True
    """
    grouped = {}

    for item in data_list:
        df = item.get("data")

        if df is None or df.empty:
            # No data, use default group
            grouped.setdefault("default", []).append(item)
            continue

        # Detect inq column
        inq_col = detect_inq_column(df)

        if inq_col is None:
            # No inq column, use default group
            grouped.setdefault("default", []).append(item)
            continue

        # Get unique inq values from this DataFrame
        unique_inq_values = df[inq_col].unique()

        # If only one unique value, assign entire item to that group
        if len(unique_inq_values) == 1:
            inq_value = str(unique_inq_values[0]).lower().strip()
            grouped.setdefault(inq_value, []).append(item)
        else:
            # Multiple inq values in same DataFrame - split by inq
            for inq_value in unique_inq_values:
                inq_value_str = str(inq_value).lower().strip()

                # Filter DataFrame for this inq value
                filtered_df = df[df[inq_col] == inq_value].copy()

                # Create new item with filtered data
                filtered_item = {
                    "domain": item.get("domain", "UNKNOWN"),
                    "data": filtered_df,
                    "content": item.get("content", "")
                }

                grouped.setdefault(inq_value_str, []).append(filtered_item)

    return grouped


def merge_analysis_results(results: dict) -> dict:
    """
    Merge multiple inq-based analysis results into single response.

    Args:
        results: Dictionary mapping inq values to LLM analysis results
                {"p1": {"success": True, "content": "..."}, ...}

    Returns:
        Combined result dictionary with merged content

    Example:
        >>> results = {
        ...     "p1": {"success": True, "content": "P1 analysis..."},
        ...     "p2": {"success": True, "content": "P2 analysis..."}
        ... }
        >>> merged = merge_analysis_results(results)
        >>> merged["success"]
        True
    """
    # Check if all results succeeded
    all_success = all(
        result.get("success", False)
        for result in results.values()
    )

    if not all_success:
        # Collect errors
        errors = [
            f"{inq}: {result.get('error', 'Unknown error')}"
            for inq, result in results.items()
            if not result.get("success", False)
        ]

        return {
            "success": False,
            "content": None,
            "error": "; ".join(errors)
        }

    # Merge successful results
    merged_content_parts = []

    # Sort by inq value for consistent ordering (p1, p2, p3, p4, p5)
    inq_order = ["p1", "p2", "p3", "p4", "p5", "default"]
    sorted_inq_values = sorted(
        results.keys(),
        key=lambda x: inq_order.index(x) if x in inq_order else 999
    )

    for inq_value in sorted_inq_values:
        result = results[inq_value]
        content = result.get("content", "")

        if content:
            # Add header for each inq section
            merged_content_parts.append(content)

    # Join with separator
    merged_content = "\n\n---\n\n".join(merged_content_parts)

    return {
        "success": True,
        "content": merged_content,
        "error": None
    }
