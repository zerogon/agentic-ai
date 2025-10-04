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
