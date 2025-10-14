import streamlit as st

# Import configuration and setup
from core.config import init_databricks_client, get_config

# Import UI components
from ui.styles import apply_custom_styles
from ui.sidebar import render_sidebar
from ui.session import init_session_state
from ui.chat_display import display_messages

# Import core logic
from core.message_handler import handle_chat_input

# Page configuration
st.set_page_config(
    page_title="SK Shieldus Chat Bot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Databricks client and configuration
w = init_databricks_client()
config = get_config()

# Apply custom styling
apply_custom_styles()

# Render sidebar
render_sidebar()

# Main header
st.markdown('<div class="main-header">💬 SK Shieldus Chat Bot</div>', unsafe_allow_html=True)
st.markdown("Ask questions about your data in natural language and get instant insights.")
st.divider()

# Initialize session state
init_session_state(config["ai_mode"])

# Display chat messages
display_messages()

# Handle chat input
handle_chat_input(w, config)

# Footer
st.divider()
st.caption("Powered by Databricks | Built with Streamlit")
