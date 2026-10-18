"""Browser camera component that sends small JPEG frames over Streamlit's connection."""
from pathlib import Path

import streamlit.components.v1 as components


_camera_component = components.declare_component(
    "ai_training_lab_browser_camera",
    path=str(Path(__file__).with_name("browser_camera_frontend")),
)


def browser_camera(*, key, capture_disabled=False):
    """Show a live browser preview and return a frame only after explicit capture."""
    return _camera_component(
        key=key,
        capture_disabled=capture_disabled,
        default=None,
    )
