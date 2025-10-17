import streamlit as st
from ui.theme_config import get_theme


def apply_custom_styles():
    """Apply custom CSS styling for the Streamlit app with dynamic theme support."""
    # Get current theme from session state (default to light)
    current_theme = st.session_state.get("theme", "light")
    theme = get_theme(current_theme)

    st.markdown(f"""
    <style>
    /* Main content area - Dynamic theme */
    .stApp {{
        background: {theme["app_background"]};
        background-attachment: fixed;
    }}
    .main .block-container {{
        background: {theme["container_background"]};
        backdrop-filter: blur(20px);
        border-radius: 1.25rem;
        padding: 1.5rem;
        margin-top: 1rem;
        border: 1px solid {theme["container_border"]};
        box-shadow: {theme["container_shadow"]};
    }}
    .stChatMessage {{
        padding: 1.5rem;
        border-radius: 1rem;
        font-size: 1rem;
        background: {theme["message_background"]} !important;
        border: 1px solid {theme["message_border"]};
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }}
    .stChatMessage:hover {{
        border-color: {theme["message_hover_border"]};
        box-shadow: {theme["message_shadow"]};
    }}
    .stChatMessage[data-testid="user"] {{
        background: {theme["user_message_background"]} !important;
        border-left: 3px solid {theme["user_message_border"]};
    }}
    .stChatMessage[data-testid="assistant"] {{
        background: {theme["assistant_message_background"]} !important;
        border-left: 3px solid {theme["assistant_message_border"]};
    }}
    /* Avatar styling with dynamic theme */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="chatAvatarIcon-user"],
    .stChatMessage[data-testid="user"] svg,
    .stChatMessage[data-testid="user"] [class*="Avatar"] {{
        background-color: {theme["user_avatar_bg"]} !important;
        background: {theme["user_avatar_bg"]} !important;
        color: {theme["user_avatar_color"]} !important;
        fill: {theme["user_avatar_color"]} !important;
    }}
    [data-testid="stChatMessageAvatarAssistant"],
    [data-testid="chatAvatarIcon-assistant"],
    .stChatMessage[data-testid="assistant"] svg,
    .stChatMessage[data-testid="assistant"] [class*="Avatar"] {{
        background-color: {theme["assistant_avatar_bg"]} !important;
        background: {theme["assistant_avatar_bg"]} !important;
        color: {theme["assistant_avatar_color"]} !important;
        fill: {theme["assistant_avatar_color"]} !important;
    }}
    .main-header {{
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: {theme["header_color"]};
        letter-spacing: -0.01em;
    }}
    /* Sidebar styling with dynamic theme */
    [data-testid="stSidebar"] {{
        background: {theme["sidebar_background"]};
        border-right: 1px solid {theme["sidebar_border"]};
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        padding: 1.5rem 0 !important;
        box-shadow: {theme["sidebar_shadow"]};
    }}
    [data-testid="stSidebar"] > div:first-child {{
        width: 300px !important;
        padding: 0 !important;
    }}
    /* Universal sidebar content wrapper - force consistent container width */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {{
        width: 100% !important;
        max-width: 100% !important;
    }}
    /* Consistent padding for all sidebar elements */
    [data-testid="stSidebar"] .element-container {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        width: calc(100% - 2rem) !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }}
    /* Button containers - full width within padding */
    [data-testid="stSidebar"] .stButton {{
        width: 100% !important;
    }}
    [data-testid="stSidebar"] .stButton > button {{
        width: 100% !important;
        margin: 0 !important;
    }}
    /* Input containers - full width within padding */
    [data-testid="stSidebar"] .stTextInput {{
        width: 100% !important;
    }}
    [data-testid="stSidebar"] .stTextInput > div {{
        width: 100% !important;
    }}
    /* Remove all emotion cache dynamic classes */
    [data-testid="stSidebar"] [class*="st-emotion-cache"] {{
        padding-left: 0 !important;
        padding-right: 0 !important;
    }}
    /* Reset default Streamlit padding */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {{
        padding-top: 0 !important;
    }}
    /* Custom sidebar elements */
    .sidebar-header {{
        font-size: 1.5rem;
        font-weight: 700;
        color: {theme["text_color"]};
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        text-align: center;
        padding: 0 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    .message-count {{
        font-size: 0.8rem;
        color: {theme["muted_text"]};
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
    }}
    .sidebar-spacing {{
        height: 1rem;
        padding: 0 !important;
    }}
    .sidebar-section-spacing {{
        height: 1.25rem;
        padding: 0 !important;
    }}
    .section-title {{
        font-size: 0.875rem;
        font-weight: 600;
        color: {theme["secondary_text"]};
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.75rem;
        text-align: center;
        padding: 0 1rem;
    }}
    [data-testid="stSidebar"] h1 {{
        display: none;
    }}
    [data-testid="stSidebar"] h3 {{
        display: none;
    }}
    /* Button styling with dynamic theme */
    [data-testid="stSidebar"] button {{
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.5rem 0.75rem;
        border-radius: 0.5rem;
        white-space: nowrap;
        background: {theme["button_background"]};
        border: 1px solid {theme["button_border"]};
        color: {theme["button_color"]};
        transition: all 0.25s ease;
        box-shadow: {theme["button_shadow"]};
        min-height: auto;
        height: auto;
        backdrop-filter: blur(10px);
    }}
    [data-testid="stSidebar"] button:hover {{
        background: {theme["button_hover_background"]};
        border-color: {theme["button_hover_border"]};
        color: {theme["button_hover_color"]};
        box-shadow: {theme["button_hover_shadow"]};
        transform: translateY(-1px);
    }}
    [data-testid="stSidebar"] button:active {{
        transform: translateY(0);
        box-shadow: {theme["button_shadow"]};
    }}
    /* New Chat button specific styling */
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button:first-of-type {{
        background: {theme["primary_button_background"]};
        border: 1px solid {theme["primary_button_border"]};
        color: {theme["primary_button_color"]};
        font-weight: 700;
    }}
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] button:first-of-type:hover {{
        background: {theme["primary_button_hover_background"]};
        border-color: {theme["primary_button_hover_border"]};
        box-shadow: {theme["primary_button_hover_shadow"]};
    }}
    /* Button text container */
    [data-testid="stSidebar"] button > div {{
        padding: 0 !important;
    }}
    [data-testid="stSidebar"] button p {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }}
    /* Message preview styling with dynamic theme */
    .message-preview {{
        padding: 0.875rem;
        margin: 0.5rem 1rem;
        border-radius: 0.75rem;
        background: {theme["preview_background"]};
        border: 1px solid {theme["preview_border"]};
        border-left: 3px solid {theme["preview_border_left"]};
        transition: all 0.3s ease;
        word-wrap: break-word;
        overflow-wrap: break-word;
        box-shadow: {theme["preview_shadow"]};
        cursor: pointer;
        backdrop-filter: blur(12px);
    }}
    .message-preview:hover {{
        background: {theme["preview_hover_background"]};
        border-left-color: {theme["preview_hover_border_left"]};
        border-color: {theme["preview_hover_border"]};
        transform: translateX(3px);
        box-shadow: {theme["preview_hover_shadow"]};
    }}
    .role-badge {{
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        color: {theme["secondary_text"]};
        margin-bottom: 0.375rem;
    }}
    .preview-text {{
        font-size: 0.85rem;
        line-height: 1.4rem;
        color: {theme["text_color"]};
    }}
    .search-results {{
        font-size: 0.75rem;
        color: {theme["muted_text"]};
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
    }}
    .empty-state {{
        text-align: center;
        padding: 2rem 1rem;
        color: {theme["muted_text"]};
        font-size: 0.875rem;
        line-height: 1.5rem;
        margin: 0 1rem;
    }}
    .more-messages {{
        text-align: center;
        font-size: 0.75rem;
        color: {theme["muted_text"]};
        margin: 0.75rem 1rem 0;
        padding: 0.5rem;
        background: {theme["button_background"]};
        border: 1px solid {theme["button_border"]};
        border-radius: 0.5rem;
        backdrop-filter: blur(10px);
    }}
    /* Input field styling with dynamic theme */
    [data-testid="stSidebar"] input {{
        font-size: 0.875rem;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        background: {theme["input_background"]};
        color: {theme["text_color"]};
        border: 1.5px solid {theme["input_border"]};
        width: 100%;
        transition: all 0.3s ease;
        backdrop-filter: blur(12px);
    }}
    [data-testid="stSidebar"] input:focus {{
        border-color: {theme["input_focus_border"]};
        background: {theme["input_focus_background"]};
        box-shadow: {theme["input_focus_shadow"]};
    }}
    [data-testid="stSidebar"] input::placeholder {{
        color: {theme["placeholder_text"]};
        font-size: 0.85rem;
    }}
    /* Caption text */
    [data-testid="stSidebar"] .element-container p {{
        font-size: 0.8rem;
        color: {theme["text_color"]};
        margin: 0.5rem 0;
    }}
    /* Info message styling */
    [data-testid="stSidebar"] .element-container:has([data-testid="stAlert"]) {{
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        border: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"] {{
        background-color: {theme["alert_background"]} !important;
        border: none !important;
        border-top: none !important;
        border-right: none !important;
        border-bottom: none !important;
        border-left: 3px solid {theme["alert_border"]} !important;
        border-radius: 0.375rem !important;
        padding: 0.75rem !important;
        font-size: 0.8rem !important;
        min-height: 3rem !important;
        margin: 0 !important;
        overflow: visible !important;
        box-shadow: none !important;
    }}
    /* Remove thin line from emotion cache */
    [data-testid="stSidebar"] .st-emotion-cache-1xmp9w2,
    [data-testid="stSidebar"] .e9q2xfh0 {{
        border: none !important;
        border-top: none !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    /* Success message styling - remove green line */
    [data-testid="stSidebar"] [data-testid="stSuccess"],
    [data-testid="stSidebar"] .element-container:has([data-testid="stSuccess"]) {{
        border: none !important;
        border-top: none !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSuccess"] {{
        background-color: {theme["success_background"]} !important;
        border: 1px solid {theme["success_border"]} !important;
        border-left: 3px solid {theme["success_border_left"]} !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        font-size: 0.8rem !important;
        margin: 0.5rem 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stSuccess"] p {{
        margin: 0 !important;
        padding: 0 !important;
        color: {theme["text_color"]} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"]::before,
    [data-testid="stSidebar"] [data-testid="stAlert"]::after {{
        display: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"] * {{
        box-sizing: border-box !important;
        border-top: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"] [class*="stAlertContainer"] {{
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 0.5rem !important;
        padding: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin: 0 !important;
        margin-top: 0 !important;
        margin-bottom: 0 !important;
        border: none !important;
        border-top: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stSidebar"] [class*="stAlertContainer"] {{
        padding-top: 0 !important;
        margin-top: 0 !important;
        border-top: none !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"] > div {{
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"] svg {{
        flex-shrink: 0 !important;
        width: 1rem !important;
        height: 1rem !important;
        margin: 0 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stAlert"] p {{
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
        white-space: nowrap !important;
        text-align: center !important;
    }}
    /* Divider styling */
    [data-testid="stSidebar"] hr {{
        display: none;
    }}
    /* Sidebar collapse/expand button styling */
    [data-testid="stSidebarNav"] button,
    button[kind="header"] {{
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem !important;
        transition: all 0.15s ease !important;
    }}
    [data-testid="stSidebarNav"] button:hover,
    button[kind="header"]:hover {{
        background-color: rgba(255, 255, 255, 0.05) !important;
    }}
    [data-testid="stSidebarNav"] button svg,
    button[kind="header"] svg {{
        color: {theme["secondary_text"]} !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
    }}
    [data-testid="stSidebarNav"] button:hover svg,
    button[kind="header"]:hover svg {{
        color: {theme["text_color"]} !important;
    }}
    /* Collapsed sidebar expand button */
    [data-testid="collapsedControl"] {{
        background-color: {theme["button_background"]} !important;
        border: 1px solid {theme["button_border"]} !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        transition: all 0.15s ease !important;
    }}
    [data-testid="collapsedControl"]:hover {{
        background-color: {theme["button_hover_background"]} !important;
        border-color: {theme["button_hover_border"]} !important;
    }}
    [data-testid="collapsedControl"] svg {{
        color: {theme["text_color"]} !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
    }}

    /* Chat input container styling */
    [data-testid="stChatInputContainer"] {{
        background: {theme["input_background"]} !important;
        border: 1px solid {theme["input_border"]} !important;
        border-radius: 0.75rem !important;
    }}

    /* Chat input textarea */
    [data-testid="stChatInput"] textarea {{
        background: {theme["input_background"]} !important;
        color: {theme["text_color"]} !important;
        border: none !important;
    }}

    [data-testid="stChatInput"] textarea:focus {{
        background: {theme["input_focus_background"]} !important;
        border: none !important;
        outline: none !important;
    }}

    [data-testid="stChatInput"] textarea::placeholder {{
        color: {theme["placeholder_text"]} !important;
    }}

    /* Chat input submit button */
    [data-testid="stChatInput"] button {{
        background: {theme["primary_button_background"]} !important;
        color: {theme["primary_button_color"]} !important;
        border: 1px solid {theme["primary_button_border"]} !important;
    }}

    [data-testid="stChatInput"] button:hover {{
        background: {theme["primary_button_hover_background"]} !important;
        border-color: {theme["primary_button_hover_border"]} !important;
    }}

    /* Bottom container for chat input */
    .stBottom {{
        background: {theme["app_background"]} !important;
    }}

    /* Divider color */
    hr {{
        border-color: {theme["message_border"]} !important;
    }}

    /* Caption and helper text */
    .stCaption {{
        color: {theme["muted_text"]} !important;
    }}
    </style>
""", unsafe_allow_html=True)
