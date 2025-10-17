"""Theme configuration for light and dark modes."""


DARK_THEME = {
    "name": "dark",
    "app_background": "linear-gradient(135deg, #1a1d23 0%, #0f1115 100%)",
    "container_background": "linear-gradient(135deg, rgba(26, 29, 35, 0.85) 0%, rgba(15, 17, 21, 0.7) 100%)",
    "container_border": "rgba(64, 68, 78, 0.15)",
    "container_shadow": "0 8px 32px rgba(0, 0, 0, 0.3)",

    # Chat messages
    "message_background": "rgba(32, 35, 42, 0.6)",
    "message_border": "rgba(64, 68, 78, 0.25)",
    "message_hover_border": "rgba(96, 165, 250, 0.3)",
    "message_shadow": "0 4px 16px rgba(0, 0, 0, 0.2)",

    "user_message_background": "linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(37, 99, 235, 0.04) 100%)",
    "user_message_border": "#5b8fd4",
    "assistant_message_background": "linear-gradient(135deg, rgba(52, 211, 153, 0.08) 0%, rgba(16, 185, 129, 0.04) 100%)",
    "assistant_message_border": "#4db89d",

    # Avatars
    "user_avatar_bg": "#6366f1",
    "user_avatar_color": "#ffffff",
    "assistant_avatar_bg": "#475569",
    "assistant_avatar_color": "#e2e8f0",

    # Text colors
    "header_color": "#e5e7eb",
    "text_color": "#d1d5db",
    "secondary_text": "#9ca3af",
    "muted_text": "#6b7280",
    "placeholder_text": "#4b5563",

    # Sidebar
    "sidebar_background": "linear-gradient(180deg, #0d0e12 0%, #08090c 100%)",
    "sidebar_border": "rgba(64, 68, 78, 0.25)",
    "sidebar_shadow": "2px 0 16px rgba(0, 0, 0, 0.4)",

    # Buttons
    "button_background": "rgba(32, 35, 42, 0.6)",
    "button_border": "rgba(64, 68, 78, 0.3)",
    "button_color": "#9ca3af",
    "button_shadow": "0 2px 6px rgba(0, 0, 0, 0.2)",
    "button_hover_background": "rgba(59, 130, 246, 0.12)",
    "button_hover_border": "rgba(91, 143, 212, 0.4)",
    "button_hover_color": "#d1d5db",
    "button_hover_shadow": "0 4px 12px rgba(0, 0, 0, 0.25)",

    "primary_button_background": "linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.08) 100%)",
    "primary_button_border": "rgba(91, 143, 212, 0.35)",
    "primary_button_color": "#93c5fd",
    "primary_button_hover_background": "linear-gradient(135deg, rgba(59, 130, 246, 0.22) 0%, rgba(37, 99, 235, 0.12) 100%)",
    "primary_button_hover_border": "rgba(91, 143, 212, 0.5)",
    "primary_button_hover_shadow": "0 4px 16px rgba(59, 130, 246, 0.2)",

    # Inputs
    "input_background": "rgba(32, 35, 42, 0.5)",
    "input_border": "rgba(64, 68, 78, 0.3)",
    "input_focus_border": "rgba(91, 143, 212, 0.5)",
    "input_focus_background": "rgba(32, 35, 42, 0.7)",
    "input_focus_shadow": "0 0 0 3px rgba(59, 130, 246, 0.15)",

    # Message previews
    "preview_background": "rgba(32, 35, 42, 0.5)",
    "preview_border": "rgba(64, 68, 78, 0.25)",
    "preview_border_left": "#5b8fd4",
    "preview_shadow": "0 2px 10px rgba(0, 0, 0, 0.3)",
    "preview_hover_background": "rgba(59, 130, 246, 0.08)",
    "preview_hover_border_left": "#6b9fe8",
    "preview_hover_border": "rgba(91, 143, 212, 0.3)",
    "preview_hover_shadow": "0 4px 16px rgba(0, 0, 0, 0.35)",

    # Alerts
    "alert_background": "#1f2937",
    "alert_border": "#3b82f6",
    "success_background": "rgba(16, 185, 129, 0.1)",
    "success_border": "rgba(16, 185, 129, 0.3)",
    "success_border_left": "#10b981",
}


LIGHT_THEME = {
    "name": "light",
    "app_background": "#ffffff",
    "container_background": "#ffffff",
    "container_border": "rgba(255, 255, 255, 0)",
    "container_shadow": "none",

    # Chat messages
    "message_background": "#fbfbfbd3",
    "message_border": "rgba(220, 220, 220, 0.5)",
    "message_hover_border": "rgba(59, 130, 246, 0.4)",
    "message_shadow": "0 2px 8px rgba(0, 0, 0, 0.05)",

    "user_message_background": "linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(37, 99, 235, 0.04) 100%)",
    "user_message_border": "#5b8fd4",
    "assistant_message_background": "linear-gradient(135deg, rgba(52, 211, 153, 0.08) 0%, rgba(16, 185, 129, 0.04) 100%)",
    "assistant_message_border": "#4db89d",

    # Avatars
    "user_avatar_bg": "#6366f1",
    "user_avatar_color": "#ffffff",
    "assistant_avatar_bg": "#94a3b8",
    "assistant_avatar_color": "#ffffff",

    # Text colors
    "header_color": "#1f2937",
    "text_color": "#374151",
    "secondary_text": "#6b7280",
    "muted_text": "#9ca3af",
    "placeholder_text": "#d1d5db",

    # Sidebar (light theme)
    "sidebar_background": "linear-gradient(180deg, #f9fafb 0%, #f3f4f6 100%)",
    "sidebar_border": "rgba(220, 220, 220, 0.4)",
    "sidebar_shadow": "2px 0 16px rgba(0, 0, 0, 0.08)",

    # Buttons (light theme)
    "button_background": "#ffffff",
    "button_border": "rgba(220, 220, 220, 0.6)",
    "button_color": "#374151",
    "button_shadow": "0 2px 6px rgba(0, 0, 0, 0.05)",
    "button_hover_background": "rgba(59, 130, 246, 0.08)",
    "button_hover_border": "rgba(59, 130, 246, 0.3)",
    "button_hover_color": "#1f2937",
    "button_hover_shadow": "0 4px 12px rgba(0, 0, 0, 0.1)",

    "primary_button_background": "linear-gradient(135deg, rgba(59, 130, 246, 0.12) 0%, rgba(37, 99, 235, 0.06) 100%)",
    "primary_button_border": "rgba(59, 130, 246, 0.4)",
    "primary_button_color": "#2563eb",
    "primary_button_hover_background": "linear-gradient(135deg, rgba(59, 130, 246, 0.18) 0%, rgba(37, 99, 235, 0.1) 100%)",
    "primary_button_hover_border": "rgba(59, 130, 246, 0.6)",
    "primary_button_hover_shadow": "0 4px 16px rgba(59, 130, 246, 0.15)",

    # Inputs (light theme)
    "input_background": "#ffffff",
    "input_border": "rgba(220, 220, 220, 0.6)",
    "input_focus_border": "rgba(59, 130, 246, 0.5)",
    "input_focus_background": "#ffffff",
    "input_focus_shadow": "0 0 0 3px rgba(59, 130, 246, 0.1)",

    # Message previews (light theme)
    "preview_background": "#ffffff",
    "preview_border": "rgba(220, 220, 220, 0.5)",
    "preview_border_left": "#5b8fd4",
    "preview_shadow": "0 2px 10px rgba(0, 0, 0, 0.06)",
    "preview_hover_background": "rgba(59, 130, 246, 0.05)",
    "preview_hover_border_left": "#3b82f6",
    "preview_hover_border": "rgba(59, 130, 246, 0.3)",
    "preview_hover_shadow": "0 4px 16px rgba(0, 0, 0, 0.1)",

    # Alerts (light theme)
    "alert_background": "#f0f9ff",
    "alert_border": "#3b82f6",
    "success_background": "rgba(16, 185, 129, 0.08)",
    "success_border": "rgba(16, 185, 129, 0.3)",
    "success_border_left": "#10b981",
}


def get_theme(theme_name: str = "light") -> dict:
    """Get theme configuration by name.

    Args:
        theme_name: Theme name ('light' or 'dark')

    Returns:
        Theme configuration dictionary
    """
    if theme_name == "dark":
        return DARK_THEME
    return LIGHT_THEME
