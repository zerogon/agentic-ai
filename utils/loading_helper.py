import streamlit as st
import base64
import time
import uuid
from pathlib import Path


def display_loading_video(video_path: str = "static/test.mp4", width: int = 600, loop: bool = True):
    """
    Display a loading video while processing.

    Args:
        video_path: Path to the video file (default: static/test.mp4)
        width: Width of the video in pixels (default: 600)
        loop: Whether to loop the video (default: True)

    Returns:
        Tuple of (container, video_id) for fadeout control
    """
    # Check if video file exists
    video_file = Path(video_path)
    if not video_file.exists():
        st.warning(f"⚠️ Loading video not found: {video_path}")
        return None, None

    # Read video file and encode to base64
    with open(video_file, "rb") as f:
        video_bytes = f.read()

    video_base64 = base64.b64encode(video_bytes).decode()

    # Generate unique ID for this video instance
    video_id = f"loading-video-{uuid.uuid4().hex[:8]}"

    # Create HTML with video element and CSS animation
    loop_attr = "loop" if loop else ""
    video_html = f"""
    <style>
        #{video_id} {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px 0;
            margin: 10px 0;
            opacity: 1;
            transition: opacity 0.5s ease-out;
        }}
        #{video_id}.fadeout {{
            opacity: 0;
        }}
        #{video_id} video {{
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border: 2px solid rgba(0, 0, 0, 0.05);
            outline: none;
        }}
    </style>
    <div id="{video_id}">
        <video width="{width}" autoplay muted {loop_attr} playsinline>
            <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    </div>
    """

    # Display video
    container = st.empty()
    container.markdown(video_html, unsafe_allow_html=True)

    return container, video_id


def remove_loading_video(container, video_id=None, fade_duration: float = 0.5):
    """
    Remove loading video from the container with fadeout effect.

    Args:
        container: Streamlit container with video element
        video_id: Unique ID of the video element (for fadeout animation)
        fade_duration: Duration of fadeout animation in seconds (default: 0.5)
    """
    if not container:
        return

    # If video_id provided, trigger fadeout animation
    if video_id:
        # Add fadeout class to trigger CSS transition
        fadeout_html = f"""
        <script>
            (function() {{
                var elem = document.getElementById('{video_id}');
                if (elem) {{
                    elem.classList.add('fadeout');
                }}
            }})();
        </script>
        """
        container.markdown(fadeout_html, unsafe_allow_html=True)

        # Wait for animation to complete
        time.sleep(fade_duration)

    # Remove the container
    container.empty()
