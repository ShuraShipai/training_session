"""Live two-player camera game using browser capture and the existing YOLO model."""
import base64
import hashlib
import time

import streamlit as st

from app.components.browser_camera import browser_camera
from app.components.game import LocalGame, MIN_CONFIDENCE, valid_pair
from app.components.services import detect_live_gestures


st.title("Rock-Paper-Scissors")
st.caption("Play together in front of one camera. Player 1 stands left; Player 2 stands right.")

if "local_rps_game" not in st.session_state:
    st.session_state.local_rps_game = LocalGame()
if "browser_frame_digest" not in st.session_state:
    st.session_state.browser_frame_digest = None
if "browser_detections" not in st.session_state:
    st.session_state.browser_detections = ()
if "browser_frame_time" not in st.session_state:
    st.session_state.browser_frame_time = 0.0
if "browser_camera_error" not in st.session_state:
    st.session_state.browser_camera_error = None

game = st.session_state.local_rps_game
score_columns = st.columns(3)
score_columns[0].metric("Player 1", game.player1_score)
score_columns[1].metric("Player 2", game.player2_score)
score_columns[2].metric("Draws", game.draws)

controls = st.columns([1, 1, 4])
controls[0].button("Reset Score", on_click=game.reset)
if game.completed:
    controls[1].button("Play Again", type="primary", on_click=game.play_again)

st.caption(f"Live YOLO detection · one gesture per side · minimum confidence {MIN_CONFIDENCE:.0%}")
frame_data_url = browser_camera(key="rps_browser_camera", target_fps=2.5)

# The component sends compact frames over the existing Streamlit connection. This
# avoids WebRTC ICE/TURN services while keeping camera capture in the browser.
if isinstance(frame_data_url, str) and frame_data_url.startswith("data:image/jpeg;base64,"):
    digest = hashlib.sha256(frame_data_url.encode("ascii")).hexdigest()
    if digest != st.session_state.browser_frame_digest:
        st.session_state.browser_frame_digest = digest
        try:
            import cv2
            import numpy as np

            encoded = base64.b64decode(frame_data_url.partition(",")[2], validate=True)
            frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("The browser camera frame could not be decoded.")
            detections, _annotated = detect_live_gestures(frame)
            st.session_state.browser_detections = tuple(detections)
            st.session_state.browser_frame_time = time.monotonic()
            st.session_state.browser_camera_error = None
        except Exception as error:
            st.session_state.browser_detections = ()
            st.session_state.browser_camera_error = f"Live detection failed: {type(error).__name__}: {error}"

if st.session_state.browser_camera_error:
    st.error(st.session_state.browser_camera_error)

fresh = time.monotonic() - st.session_state.browser_frame_time < 2.5
detections = st.session_state.browser_detections if fresh else ()
pair = valid_pair(detections)
if pair:
    left, right = pair
    left_col, right_col = st.columns(2)
    left_col.metric("Player 1 · left", left[0], f"{left[1]:.0%} confidence")
    right_col.metric("Player 2 · right", right[0], f"{right[1]:.0%} confidence")
elif st.session_state.browser_frame_time and fresh:
    if detections:
        seen = []
        for detection in detections:
            if len(detection) == 3:
                label, confidence, center_x = detection
                side = "left" if center_x < 0.5 else "right"
                seen.append(f"{label} · {confidence:.0%} · {side} side")
            else:
                seen.append(f"{detection[0]} · {detection[1]:.0%}")
        st.warning("YOLO sees: " + " | ".join(seen))
        st.caption(
            "A confident gesture is needed in each half. If YOLO returns extra boxes, "
            f"the strongest box per side is used; confidence threshold is {MIN_CONFIDENCE:.0%}."
        )
    else:
        st.warning("YOLO did not recognize a hand gesture in the latest frame.")
        st.caption("Move both hands closer to the camera, keep them inside the frame, and improve the lighting.")
else:
    st.info("Press **Start live camera** in the camera view and allow this site to use your camera.")

if game.completed:
    st.success(game.result)
    st.write(f"Player 1: **{game.player1}** · Player 2: **{game.player2}**")

if st.button("Play Round", type="primary", disabled=pair is None or game.completed):
    if game.confirm(detections, game.round_id):
        st.rerun()
    st.warning("The latest camera frame is no longer valid. No points awarded.")
