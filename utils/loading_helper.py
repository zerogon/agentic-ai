import streamlit as st
import base64
import time
import uuid
import threading
from pathlib import Path

# Default loading messages (can be customized)
DEFAULT_LOADING_MESSAGES = [
    "Understanding query",
    "Connecting to Genie",
    "Generating SQL",
    "Fetching data",
    "Preparing results"
]


def display_loading_video(video_path: str = "static/test.mp4", width: int = 600, loop: bool = True, message: str = ""):
    """
    Display a loading video while processing with optional overlay message.

    Args:
        video_path: Path to the video file (default: static/test.mp4)
        width: Width of the video in pixels (default: 600)
        loop: Whether to loop the video (default: True)
        message: Optional overlay message to display on video (default: "")

    Returns:
        Tuple of (container, video_id, message_id) for fadeout control and message updates
    """
    # Check if video file exists
    video_file = Path(video_path)
    if not video_file.exists():
        st.warning(f"⚠️ Loading video not found: {video_path}")
        return None, None, None

    # Read video file and encode to base64
    with open(video_file, "rb") as f:
        video_bytes = f.read()

    video_base64 = base64.b64encode(video_bytes).decode()

    # Generate unique IDs for this video instance
    video_id = f"loading-video-{uuid.uuid4().hex[:8]}"
    message_id = f"loading-message-{uuid.uuid4().hex[:8]}"

    # Create HTML with video element and overlay message
    loop_attr = "loop" if loop else ""

    # Full HTML with subtle animations for st.markdown compatibility
    video_html = f"""
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 0.85; transform: translate(-50%, -50%) scale(1); }}
            50% {{ opacity: 0.7; transform: translate(-50%, -50%) scale(1.01); }}
        }}
        @keyframes shimmer {{
            0% {{ background-position: -1000px 0; }}
            100% {{ background-position: 1000px 0; }}
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        @keyframes dots {{
            0%, 20% {{ content: '.'; }}
            40% {{ content: '..'; }}
            60%, 100% {{ content: '...'; }}
        }}
        .loading-dots::after {{
            content: '...';
            animation: dots 1.5s infinite;
            display: inline-block;
            width: 20px;
            text-align: left;
        }}
        .progress-border {{
            position: relative;
            overflow: hidden;
        }}
        .progress-border::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(90deg,
                transparent,
                rgba(91, 143, 212, 0.5),
                transparent
            );
            background-size: 200% 100%;
            animation: shimmer 2.5s infinite;
            border-radius: 14px;
            z-index: -1;
        }}
    </style>
    <div id="{video_id}" style="position: relative; display: flex; justify-content: center; align-items: center; padding: 20px 0; margin: 10px 0;">
        <video width="{width}" autoplay muted {loop_attr} playsinline style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4); border: 2px solid rgba(91, 143, 212, 0.3);">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div id="{message_id}" class="progress-border" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0, 0, 0, 0.6); color: white; padding: 10px 20px; border-radius: 12px; font-size: 18px; font-weight: 600; z-index: 10; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); max-width: 80%; word-wrap: break-word; animation: pulse 2s ease-in-out infinite; line-height: 1.2;">
            <svg width="16" height="16" viewBox="0 0 24 24" style="animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px; transform-origin: center;">
                <circle cx="12" cy="12" r="10" fill="none" stroke="white" stroke-width="3" stroke-dasharray="31.4 31.4" stroke-linecap="round" />
            </svg><span class="loading-dots" style="display: inline-block; vertical-align: middle;">{message if message else ""}</span>
        </div>
    </div>
    """

    # Display video
    container = st.empty()
    container.markdown(video_html, unsafe_allow_html=True)

    return container, video_id, message_id


def update_loading_message(container, video_id: str, message_id: str, new_message: str, video_path: str = "static/test.mp4", width: int = 600):
    """
    Update the overlay message on a loading video.

    Args:
        container: Streamlit container with video element
        video_id: Unique ID of the video element
        message_id: Unique ID of the message element
        new_message: New message to display
        video_path: Path to the video file (default: static/test.mp4)
        width: Width of the video in pixels (default: 600)
    """
    if not container or not video_id or not message_id:
        return

    # Re-encode video to base64
    video_file = Path(video_path)
    if not video_file.exists():
        return

    with open(video_file, "rb") as f:
        video_bytes = f.read()

    video_base64 = base64.b64encode(video_bytes).decode()

    # Recreate video HTML with updated message and subtle animations
    video_html = f"""
    <style>
        @keyframes pulse {{
            0%, 100% {{ opacity: 0.85; transform: translate(-50%, -50%) scale(1); }}
            50% {{ opacity: 0.7; transform: translate(-50%, -50%) scale(1.01); }}
        }}
        @keyframes shimmer {{
            0% {{ background-position: -1000px 0; }}
            100% {{ background-position: 1000px 0; }}
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        @keyframes dots {{
            0%, 20% {{ content: '.'; }}
            40% {{ content: '..'; }}
            60%, 100% {{ content: '...'; }}
        }}
        .loading-dots::after {{
            content: '...';
            animation: dots 1.5s infinite;
            display: inline-block;
            width: 20px;
            text-align: left;
        }}
        .progress-border {{
            position: relative;
            overflow: hidden;
        }}
        .progress-border::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(90deg,
                transparent,
                rgba(91, 143, 212, 0.5),
                transparent
            );
            background-size: 200% 100%;
            animation: shimmer 2.5s infinite;
            border-radius: 14px;
            z-index: -1;
        }}
    </style>
    <div id="{video_id}" style="position: relative; display: flex; justify-content: center; align-items: center; padding: 20px 0; margin: 10px 0;">
        <video width="{width}" autoplay muted loop playsinline style="border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4); border: 2px solid rgba(91, 143, 212, 0.3);">
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <div id="{message_id}" class="progress-border" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: rgba(0, 0, 0, 0.6); color: white; padding: 10px 20px; border-radius: 12px; font-size: 18px; font-weight: 600; z-index: 10; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4); max-width: 80%; word-wrap: break-word; animation: pulse 2s ease-in-out infinite; line-height: 1.2;">
            <svg width="16" height="16" viewBox="0 0 24 24" style="animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px; transform-origin: center;">
                <circle cx="12" cy="12" r="10" fill="none" stroke="white" stroke-width="3" stroke-dasharray="31.4 31.4" stroke-linecap="round" />
            </svg><span class="loading-dots" style="display: inline-block; vertical-align: middle;">{new_message if new_message else ""}</span>
        </div>
    </div>
    """

    # Update container
    container.markdown(video_html, unsafe_allow_html=True)


def remove_loading_video(container, video_id=None, fade_duration: float = 0.5):
    """
    Remove loading video from the container.

    Args:
        container: Streamlit container with video element
        video_id: Unique ID of the video element (kept for API compatibility)
        fade_duration: Duration of fadeout animation in seconds (default: 0.5)
    """
    if not container:
        return

    # Simply remove the container (st.html iframe doesn't support external JS manipulation)
    # Brief pause for visual continuity
    time.sleep(fade_duration)
    container.empty()


def display_loading_with_sequential_messages(
    messages: list = None,
    interval: float = 1.5,
    video_path: str = "static/test.mp4",
    width: int = 600
):
    """
    Display loading video with sequential messages that update automatically.

    Args:
        messages: List of messages to display sequentially (default: DEFAULT_LOADING_MESSAGES)
        interval: Time between message updates in seconds (default: 1.5)
        video_path: Path to the video file (default: static/test.mp4)
        width: Width of the video in pixels (default: 600)

    Returns:
        Dict with:
            - container: Streamlit container
            - video_id: Unique ID of video element
            - message_id: Unique ID of message element
            - messages: List of messages
            - current_index: Current message index (stored in session state)

    Example:
        >>> # Start loading with sequential messages
        >>> loading_state = display_loading_with_sequential_messages()
        >>>
        >>> # Update to next message
        >>> update_to_next_message(loading_state)
        >>>
        >>> # Remove loading video
        >>> remove_loading_video(loading_state["container"])
    """
    if messages is None:
        messages = DEFAULT_LOADING_MESSAGES.copy()

    # Start with first message
    container, video_id, message_id = display_loading_video(
        video_path=video_path,
        width=width,
        loop=True,
        message=messages[0] if messages else ""
    )

    return {
        "container": container,
        "video_id": video_id,
        "message_id": message_id,
        "messages": messages,
        "current_index": 0,
        "video_path": video_path,
        "width": width
    }


def update_to_next_message(loading_state: dict):
    """
    Update to the next message in the sequence.

    Args:
        loading_state: Dict returned from display_loading_with_sequential_messages()
    """
    if not loading_state or not loading_state.get("messages"):
        return

    # Move to next message
    loading_state["current_index"] = (loading_state["current_index"] + 1) % len(loading_state["messages"])
    next_message = loading_state["messages"][loading_state["current_index"]]

    # Update display
    update_loading_message(
        loading_state["container"],
        loading_state["video_id"],
        loading_state["message_id"],
        next_message,
        video_path=loading_state.get("video_path", "static/test.mp4"),
        width=loading_state.get("width", 600)
    )
