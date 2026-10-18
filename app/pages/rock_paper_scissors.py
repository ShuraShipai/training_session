"""Two-player camera game; run one YOLO prediction for each captured round."""
import base64

import streamlit as st

from app.components.browser_camera import browser_camera
from app.components.game import LocalGame, MIN_CONFIDENCE, valid_pair
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

        Keep the live preview open. Both players show a gesture, then capture once
        to play the round. Lower your hands before starting the next round.
        """
    )

if "local_rps_game" not in st.session_state:
    st.session_state.local_rps_game = LocalGame()
if "last_processed_capture_id" not in st.session_state:
    st.session_state.last_processed_capture_id = None
if "latest_round_capture" not in st.session_state:
    st.session_state.latest_round_capture = None

game = st.session_state.local_rps_game
scores = st.empty()
controls = st.columns([1, 1, 4])

if controls[0].button("Reset Score"):
    game.reset()
    st.session_state.latest_round_capture = None
    st.rerun()
if game.completed and controls[1].button("Next Round", type="primary"):
    game.play_again()
    st.session_state.latest_round_capture = None
    st.rerun()

st.caption(
    f"One YOLO prediction per captured round · existing model · "
    f"minimum confidence {MIN_CONFIDENCE:.0%}"
)
capture = browser_camera(
    key="rps_browser_camera",
    capture_disabled=game.completed,
)

# A new capture ID is generated only when the player presses Capture & Play Round.
# Re-renders of the same component value therefore never repeat model inference.
if isinstance(capture, dict):
    capture_id = capture.get("capture_id")
    image_data_url = capture.get("image")
    is_new_capture = (
        isinstance(capture_id, str)
        and bool(capture_id)
        and capture_id != st.session_state.last_processed_capture_id
    )
    if is_new_capture and isinstance(image_data_url, str) and image_data_url.startswith(
        "data:image/jpeg;base64,"
    ) and not game.completed:
        # Mark before inference so a Streamlit rerun cannot score this frame twice.
        st.session_state.last_processed_capture_id = capture_id
        try:
            import cv2
            import numpy as np

            encoded = base64.b64decode(image_data_url.partition(",")[2], validate=True)
            frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
            if frame is None:
                raise ValueError("The camera frame could not be decoded.")
            detections, annotated = detect_live_gestures(frame)
            scored = game.confirm(detections, game.round_id)
            st.session_state.latest_round_capture = {
                "detections": tuple(detections),
                "annotated": annotated,
                "error": None,
                "scored": scored,
            }
        except Exception as error:
            st.session_state.latest_round_capture = {
                "detections": (),
                "annotated": None,
                "error": f"Prediction failed: {type(error).__name__}: {error}",
                "scored": False,
            }

with scores.container():
    score_columns = st.columns(3)
    score_columns[0].metric("Player 1", game.player1_score)
    score_columns[1].metric("Player 2", game.player2_score)
    score_columns[2].metric("Draws", game.draws)

latest = st.session_state.latest_round_capture
if latest:
    if latest["error"]:
        st.error(latest["error"])
    else:
        st.image(latest["annotated"], channels="BGR", width="stretch")
        pair = valid_pair(latest["detections"])
        if pair and latest["scored"]:
            left, right = pair
            st.success(
                f"{game.result} · Player 1: {left[0]} ({left[1]:.0%}) · "
                f"Player 2: {right[0]} ({right[1]:.0%})"
            )
        elif pair:
            st.info("This round was already scored. Start the next round to play again.")
        else:
            st.warning(
                "No point awarded. Show one clear Rock, Paper, or Scissors gesture "
                "on each side of the center line, then capture the round again."
            )
            if latest["detections"]:
                seen = " · ".join(
                    f"{label} {confidence:.0%} at {center_x:.0%} across the frame"
                    for label, confidence, center_x in latest["detections"]
                )
                st.caption(f"Model detections: {seen}")

if game.completed:
    st.caption("Both players lower their hands, then press Next Round when ready.")
else:
    st.caption("The camera preview stays live; YOLO runs only when you capture a round.")
