"""Browser camera component that sends small JPEG frames over Streamlit's connection."""
from pathlib import Path

import streamlit.components.v1 as components


_camera_component = components.declare_component(
    "ai_training_lab_browser_camera",
    path=str(Path(__file__).with_name("browser_camera_frontend")),
)


def browser_camera(*, key, live_enabled=False, processed_capture_id=None,
                   interval_ms=1100):
    """Show live preview and request the next frame after server inference ends."""
    return _camera_component(
        key=key,
        live_enabled=live_enabled,
        processed_capture_id=processed_capture_id,
        interval_ms=interval_ms,
        default=None,
    )
