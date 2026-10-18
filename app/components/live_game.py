"""Thread-safe state and throttled callback for live YOLO camera inference."""
import threading
import time

from app.components.services import detect_live_gestures


class LiveDetectionState:
    """Thread-safe handoff from the WebRTC video worker to the Streamlit page."""

    def __init__(self):
        self._lock = threading.Lock()
        self._detections = ()
        self._updated_at = 0.0
        self._error = None

    def publish(self, detections, error=None):
        with self._lock:
            self._detections = tuple(detections)
            self._updated_at = time.monotonic()
            self._error = error

    def snapshot(self, max_age=1.5):
        with self._lock:
            fresh = time.monotonic() - self._updated_at <= max_age
            return (self._detections if fresh else ()), self._error, fresh


def make_video_callback(state):
    """Return an annotated callback while limiting YOLO to roughly 3 FPS."""
    last_inference = [0.0]
    last_annotated = [None]

    def process(video_frame):
        import av

        frame = video_frame.to_ndarray(format="bgr24")
        now = time.monotonic()
        if now - last_inference[0] >= 0.33:
            last_inference[0] = now
            try:
                detections, annotated = detect_live_gestures(frame)
                state.publish(detections)
                last_annotated[0] = annotated
            except Exception as error:
                state.publish((), error=f"{type(error).__name__}: {error}")
                last_annotated[0] = frame
        output = last_annotated[0] if last_annotated[0] is not None else frame
        return av.VideoFrame.from_ndarray(output, format="bgr24")

    return process
