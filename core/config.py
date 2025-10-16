import streamlit as st
import os
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import Config


def init_databricks_client():
    """Initialize Databricks WorkspaceClient with configuration."""
    # Remove Databricks Apps credentials to use token-based auth
    os.environ.pop("DATABRICKS_CLIENT_ID", None)
    os.environ.pop("DATABRICKS_CLIENT_SECRET", None)

    # Try secrets first, fallback to environment variables
    host = st.secrets.get("databricks", {}).get("HOST") or os.environ.get("DATABRICKS_HOST")
    token = st.secrets.get("databricks", {}).get("TOKEN") or os.environ.get("DATABRICKS_TOKEN")

    if not host or not token:
        raise ValueError("Databricks HOST and TOKEN must be set in secrets.toml or environment variables")

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


def get_space_id_by_domain(domain: str = "REGION_GENIE"):
    """
    Get Genie Space ID for REGION_GENIE (simplified - only one domain now)

    Args:
        domain: Genie domain name (default: "REGION_GENIE")

    Returns:
        Genie Space ID for REGION_GENIE
    """
    # Simplified: Always return REGION_GENIE Space ID
    genie_spaces = st.secrets.get("genie_spaces", {})
    region_space_id = genie_spaces.get("REGION_GENIE", st.secrets.get("databricks", {}).get("GENIE_SPACE_ID"))
    return region_space_id
