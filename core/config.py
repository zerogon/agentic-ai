import streamlit as st
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config


def init_databricks_client():
    """Initialize Databricks WorkspaceClient with configuration."""
    # Remove Databricks Apps credentials to use token-based auth
    os.environ.pop("DATABRICKS_CLIENT_ID", None)
    os.environ.pop("DATABRICKS_CLIENT_SECRET", None)

    host = st.secrets["databricks"]["HOST"]
    token = st.secrets["databricks"]["TOKEN"]

    conf = Config(host=host, token=token)
    w = WorkspaceClient(config=conf)

    return w


def get_config():
    """Get application configuration."""
    return {
        "genie_space_id": st.secrets.get("databricks", {}).get("GENIE_SPACE_ID"),
        "ai_mode": "Genie API",  # Default AI mode
        "chart_type": "Auto"      # Default chart type
    }


def get_genie_spaces():
    """
    Get Genie Space ID mapping for routing

    Returns:
        Dict mapping Genie domain names to Space IDs
    """
    genie_spaces = st.secrets.get("genie_spaces", {})

    # Convert to regular dict and provide fallback
    spaces_dict = {
        "SALES_GENIE": genie_spaces.get("SALES_GENIE", st.secrets.get("databricks", {}).get("GENIE_SPACE_ID")),
        "CONTRACT_GENIE": genie_spaces.get("CONTRACT_GENIE", st.secrets.get("databricks", {}).get("GENIE_SPACE_ID")),
        "REGION_GENIE": genie_spaces.get("REGION_GENIE", st.secrets.get("databricks", {}).get("GENIE_SPACE_ID"))
    }
    return spaces_dict

def get_space_id_by_domain(domain: str):
    """
    Get Genie Space ID by domain name

    Args:
        domain: Genie domain name (e.g., "SALES_GENIE")

    Returns:
        Genie Space ID for the specified domain
    """
    spaces = get_genie_spaces()
    return spaces.get(domain, st.secrets.get("databricks", {}).get("GENIE_SPACE_ID"))
