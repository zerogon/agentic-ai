import streamlit as st


def apply_custom_styles():
    """Apply custom CSS styling for the Streamlit app."""
    st.markdown("""
    <style>
    /* Main content area - Sophisticated dark gray theme */
    .stApp {
        background: linear-gradient(135deg, #1a1d23 0%, #0f1115 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        background: linear-gradient(135deg, rgba(26, 29, 35, 0.85) 0%, rgba(15, 17, 21, 0.7) 100%);
        backdrop-filter: blur(20px);
        border-radius: 1.25rem;
        padding: 2.5rem;
        margin-top: 1rem;
        border: 1px solid rgba(64, 68, 78, 0.15);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .stChatMessage {
        padding: 1.5rem;
        border-radius: 1rem;
        font-size: 1rem;
        background: rgba(32, 35, 42, 0.6) !important;
        border: 1px solid rgba(64, 68, 78, 0.25);
        backdrop-filter: blur(10px);
        margin-bottom: 1rem;
        transition: all 0.3s ease;
    }
    .stChatMessage:hover {
        border-color: rgba(96, 165, 250, 0.3);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    .stChatMessage[data-testid="user"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(37, 99, 235, 0.04) 100%) !important;
        border-left: 3px solid #5b8fd4;
    }
    .stChatMessage[data-testid="assistant"] {
        background: linear-gradient(135deg, rgba(52, 211, 153, 0.08) 0%, rgba(16, 185, 129, 0.04) 100%) !important;
        border-left: 3px solid #4db89d;
    }
    .main-header {
        font-size: 2.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: #e5e7eb;
        letter-spacing: -0.01em;
    }
    /* Sidebar styling - Rich dark theme */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0e12 0%, #08090c 100%);
        border-right: 1px solid rgba(64, 68, 78, 0.25);
        width: 300px !important;
        min-width: 300px !important;
        max-width: 300px !important;
        padding: 1.5rem 0 !important;
        box-shadow: 2px 0 16px rgba(0, 0, 0, 0.4);
    }
    [data-testid="stSidebar"] > div:first-child {
        width: 300px !important;
        padding: 0 !important;
    }
    /* Universal sidebar content wrapper - force consistent container width */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        width: 100% !important;
        max-width: 100% !important;
    }
    /* Consistent padding for all sidebar elements */
    [data-testid="stSidebar"] .element-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        width: calc(100% - 2rem) !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    /* Button containers - full width within padding */
    [data-testid="stSidebar"] .stButton {
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin: 0 !important;
    }
    /* Input containers - full width within padding */
    [data-testid="stSidebar"] .stTextInput {
        width: 100% !important;
    }
    [data-testid="stSidebar"] .stTextInput > div {
        width: 100% !important;
    }
    /* Remove all emotion cache dynamic classes */
    [data-testid="stSidebar"] [class*="st-emotion-cache"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
    }
    /* Reset default Streamlit padding */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
    }
    /* Custom sidebar elements */
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #d1d5db;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        text-align: center;
        padding: 0 1rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .message-count {
        font-size: 0.8rem;
        color: #6b7280;
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
    }
    .sidebar-spacing {
        height: 1rem;
        padding: 0 !important;
    }
    .sidebar-section-spacing {
        height: 1.25rem;
        padding: 0 !important;
    }
    .section-title {
        font-size: 0.875rem;
        font-weight: 600;
        color: #9ca3af;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.75rem;
        text-align: center;
        padding: 0 1rem;
    }
    [data-testid="stSidebar"] h1 {
        display: none;
    }
    [data-testid="stSidebar"] h3 {
        display: none;
    }
    /* Button styling - Subtle professional theme */
    [data-testid="stSidebar"] button {
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.5rem 0.75rem;
        border-radius: 0.5rem;
        white-space: nowrap;
        background: rgba(32, 35, 42, 0.6);
        border: 1px solid rgba(64, 68, 78, 0.3);
        color: #9ca3af;
        transition: all 0.25s ease;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
        min-height: auto;
        height: auto;
        backdrop-filter: blur(10px);
    }
    [data-testid="stSidebar"] button:hover {
        background: rgba(59, 130, 246, 0.12);
        border-color: rgba(91, 143, 212, 0.4);
        color: #d1d5db;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transform: translateY(-1px);
    }
    [data-testid="stSidebar"] button:active {
        transform: translateY(0);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
    }
    /* New Chat button specific styling */
    [data-testid="stSidebar"] button[kind="primary"],
    [data-testid="stSidebar"] button:first-of-type {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.08) 100%);
        border: 1px solid rgba(91, 143, 212, 0.35);
        color: #93c5fd;
        font-weight: 700;
    }
    [data-testid="stSidebar"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] button:first-of-type:hover {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.22) 0%, rgba(37, 99, 235, 0.12) 100%);
        border-color: rgba(91, 143, 212, 0.5);
        box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
    }
    /* Button text container */
    [data-testid="stSidebar"] button > div {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] button p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.2 !important;
    }
    /* Message preview styling - Subtle card design */
    .message-preview {
        padding: 0.875rem;
        margin: 0.5rem 1rem;
        border-radius: 0.75rem;
        background: rgba(32, 35, 42, 0.5);
        border: 1px solid rgba(64, 68, 78, 0.25);
        border-left: 3px solid #5b8fd4;
        transition: all 0.3s ease;
        word-wrap: break-word;
        overflow-wrap: break-word;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
        cursor: pointer;
        backdrop-filter: blur(12px);
    }
    .message-preview:hover {
        background: rgba(59, 130, 246, 0.08);
        border-left-color: #6b9fe8;
        border-color: rgba(91, 143, 212, 0.3);
        transform: translateX(3px);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    }
    .role-badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        color: #9ca3af;
        margin-bottom: 0.375rem;
    }
    .preview-text {
        font-size: 0.85rem;
        line-height: 1.4rem;
        color: #d1d5db;
    }
    .search-results {
        font-size: 0.75rem;
        color: #6b7280;
        margin-bottom: 0.5rem;
        font-weight: 500;
        text-align: center;
        padding: 0 1rem;
    }
    .empty-state {
        text-align: center;
        padding: 2rem 1rem;
        color: #6b7280;
        font-size: 0.875rem;
        line-height: 1.5rem;
        margin: 0 1rem;
    }
    .more-messages {
        text-align: center;
        font-size: 0.75rem;
        color: #6b7280;
        margin: 0.75rem 1rem 0;
        padding: 0.5rem;
        background: rgba(32, 35, 42, 0.4);
        border: 1px solid rgba(64, 68, 78, 0.2);
        border-radius: 0.5rem;
        backdrop-filter: blur(10px);
    }
    /* Input field styling - Subtle modern design */
    [data-testid="stSidebar"] input {
        font-size: 0.875rem;
        padding: 0.75rem 1rem;
        border-radius: 0.75rem;
        background: rgba(32, 35, 42, 0.5);
        color: #d1d5db;
        border: 1.5px solid rgba(64, 68, 78, 0.3);
        width: 100%;
        transition: all 0.3s ease;
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"] input:focus {
        border-color: rgba(91, 143, 212, 0.5);
        background: rgba(32, 35, 42, 0.7);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15);
    }
    [data-testid="stSidebar"] input::placeholder {
        color: #4b5563;
        font-size: 0.85rem;
    }
    /* Caption text */
    [data-testid="stSidebar"] .element-container p {
        font-size: 0.8rem;
        color: #d1d5db;
        margin: 0.5rem 0;
    }
    /* Info message styling */
    [data-testid="stSidebar"] .element-container:has([data-testid="stAlert"]) {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        margin-top: 0 !important;
        padding-top: 0 !important;
        border: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #1f2937 !important;
        border: none !important;
        border-top: none !important;
        border-right: none !important;
        border-bottom: none !important;
        border-left: 3px solid #3b82f6 !important;
        border-radius: 0.375rem !important;
        padding: 0.75rem !important;
        font-size: 0.8rem !important;
        min-height: 3rem !important;
        margin: 0 !important;
        overflow: visible !important;
        box-shadow: none !important;
    }
    /* Remove thin line from emotion cache */
    [data-testid="stSidebar"] .st-emotion-cache-1xmp9w2,
    [data-testid="stSidebar"] .e9q2xfh0 {
        border: none !important;
        border-top: none !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    /* Success message styling - remove green line */
    [data-testid="stSidebar"] [data-testid="stSuccess"],
    [data-testid="stSidebar"] .element-container:has([data-testid="stSuccess"]) {
        border: none !important;
        border-top: none !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSuccess"] {
        background-color: rgba(16, 185, 129, 0.1) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-left: 3px solid #10b981 !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        font-size: 0.8rem !important;
        margin: 0.5rem 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSuccess"] p {
        margin: 0 !important;
        padding: 0 !important;
        color: #d1d5db !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"]::before,
    [data-testid="stSidebar"] [data-testid="stAlert"]::after {
        display: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] * {
        box-sizing: border-box !important;
        border-top: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] [class*="stAlertContainer"] {
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
    }
    [data-testid="stSidebar"] [class*="stAlertContainer"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
        border-top: none !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] > div {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] svg {
        flex-shrink: 0 !important;
        width: 1rem !important;
        height: 1rem !important;
        margin: 0 !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        margin: 0 !important;
        padding: 0 !important;
        line-height: 1.4 !important;
        white-space: nowrap !important;
        text-align: center !important;
    }
    /* Divider styling */
    [data-testid="stSidebar"] hr {
        display: none;
    }
    /* Sidebar collapse/expand button styling */
    [data-testid="stSidebarNav"] button,
    button[kind="header"] {
        background-color: transparent !important;
        border: none !important;
        padding: 0.5rem !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="stSidebarNav"] button:hover,
    button[kind="header"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    [data-testid="stSidebarNav"] button svg,
    button[kind="header"] svg {
        color: #9ca3af !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
    }
    [data-testid="stSidebarNav"] button:hover svg,
    button[kind="header"]:hover svg {
        color: #ffffff !important;
    }
    /* Collapsed sidebar expand button */
    [data-testid="collapsedControl"] {
        background-color: #2d2d2d !important;
        border: 1px solid #404040 !important;
        border-radius: 0.5rem !important;
        padding: 0.75rem !important;
        transition: all 0.15s ease !important;
    }
    [data-testid="collapsedControl"]:hover {
        background-color: #3a3a3a !important;
        border-color: #525252 !important;
    }
    [data-testid="collapsedControl"] svg {
        color: #ffffff !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
    }
    </style>
""", unsafe_allow_html=True)
