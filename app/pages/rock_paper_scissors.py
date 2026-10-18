"""Live two-player camera game using browser capture and the existing YOLO model."""
import base64
import hashlib
import time

import streamlit as st

from app.components.browser_camera import browser_camera
from app.components.game import LiveRoundTracker, LocalGame, MIN_CONFIDENCE, valid_pair
from app.components.services import detect_live_gestures


st.title("Rock-Paper-Scissors")
st.caption("Play together in front of one camera. Player 1 stands left; Player 2 stands right.")
with st.expander("How to play"):
    st.markdown(
        """
        - **Rock beats Scissors.**
        - **Scissors beats Paper.**
        - **Paper beats Rock.**
        - Matching gestures are a **draw**.

        Show one gesture each. After the score appears, both players lower their hands;
        the next round starts automatically when you show your gestures again.
        """
    )

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
if "live_round_tracker" not in st.session_state:
    st.session_state.live_round_tracker = LiveRoundTracker()

game = st.session_state.local_rps_game


def reset_game():
    game.reset()
    tracker = st.session_state.live_round_tracker
    tracker.completed_at = None
    tracker.neutral_frames = 0
    tracker.last_round = None
    tracker.reset_candidate()


score_columns = st.columns(3)
score_columns[0].metric("Player 1", game.player1_score)
score_columns[1].metric("Player 2", game.player2_score)
score_columns[2].metric("Draws", game.draws)

controls = st.columns([1, 1, 4])
controls[0].button("Reset Score", on_click=reset_game)
if game.completed and controls[1].button("Next Round", type="primary"):
    game.play_again()
    st.session_state.live_round_tracker.completed_at = None
    st.session_state.live_round_tracker.neutral_frames = 0
    st.session_state.live_round_tracker.reset_candidate()

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
            tracker_status = st.session_state.live_round_tracker.update(
                game, detections, st.session_state.browser_frame_time
            )
            st.session_state.live_round_status = tracker_status
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
    if not game.completed:
        stable = st.session_state.live_round_tracker.stable_frames
        st.info(f"Hold steady — scoring automatically after {max(0, 3 - stable)} more clear frames.")
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
    st.caption("Hands down to arm the next round. The camera stays live; show both gestures again when ready.")
elif st.session_state.get("live_round_status") == "ready":
    st.success("Next round ready — show both gestures.")
elif st.session_state.live_round_tracker.last_round:
    result, player1, player2 = st.session_state.live_round_tracker.last_round
    st.caption(f"Last round: {result} · Player 1: {player1} · Player 2: {player2}")
