"""Browser camera component that sends small JPEG frames over Streamlit's connection."""
from pathlib import Path

import streamlit.components.v1 as components


_camera_component = components.declare_component(
    "ai_training_lab_browser_camera",
    path=str(Path(__file__).with_name("browser_camera_frontend")),
)


def browser_camera(*, key, target_fps=2.5):
    """Return the most recent browser JPEG data URL, or None before camera starts."""
    return _camera_component(key=key, target_fps=target_fps, default=None)
