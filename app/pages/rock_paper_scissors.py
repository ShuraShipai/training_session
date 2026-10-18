"""Two-player automatic RPS, sampled at a controlled rate from the browser camera."""
import base64
import time

import streamlit as st

from app.components.browser_camera import browser_camera
from app.components.game import MIN_CONFIDENCE, LiveRoundTracker, LocalGame, valid_pair
from app.components.services import detect_live_gestures


st.title("Rock-Paper-Scissors")
st.caption("Player 1 stands on the left; Player 2 stands on the right.")
with st.expander("How to play"):
    st.markdown(
        """
        1. Start the game and camera, then both players show Rock, Paper, or Scissors.
        2. Hold both gestures steady while the game confirms the round.
        3. After the result, move both hands out of their camera zones. The next round
           starts automatically after two consecutive empty-zone predictions.

        Rock beats Scissors, Scissors beats Paper, and Paper beats Rock. Matching
        gestures are a draw. This model only recognizes those three gestures; it has
        no separate hands-down class, so clearing means no gesture boxes in either
        half of the camera view.
        """
    )

if "local_rps_game" not in st.session_state:
    st.session_state.local_rps_game = LocalGame()
if "rps_tracker" not in st.session_state:
    st.session_state.rps_tracker = LiveRoundTracker()
if "rps_last_capture_id" not in st.session_state:
    st.session_state.rps_last_capture_id = None
if "rps_latest_detections" not in st.session_state:
    st.session_state.rps_latest_detections = []
if "rps_last_event" not in st.session_state:
    st.session_state.rps_last_event = ""
if "rps_game_enabled" not in st.session_state:
    st.session_state.rps_game_enabled = False

game = st.session_state.local_rps_game
tracker = st.session_state.rps_tracker

def reset_score():
    tracker.reset(game)
    st.session_state.rps_latest_detections = []
    st.session_state.rps_last_event = "reset"

scores = st.columns(4)
scores[0].metric("Player 1 wins", game.player1_score)
scores[1].metric("Player 2 wins", game.player2_score)
scores[2].metric("Draws", game.draws)
scores[3].metric("Round", game.player1_score + game.player2_score + game.draws + 1)

controls = st.columns([1, 1, 4])
if controls[0].button("Stop Game" if st.session_state.rps_game_enabled else "Start Game",
                       type="primary" if not st.session_state.rps_game_enabled else "secondary"):
    st.session_state.rps_game_enabled = not st.session_state.rps_game_enabled
    tracker.reset_candidate()
    st.rerun()
controls[1].button("Reset Score", on_click=reset_score)

st.caption(
    f"One cached-model prediction at a time · {MIN_CONFIDENCE:.0%} confidence minimum · "
    "gestures must stay stable for 0.8 seconds"
)
capture = browser_camera(
    key="rps_browser_camera",
    live_enabled=st.session_state.rps_game_enabled,
    processed_capture_id=st.session_state.rps_last_capture_id,
)

# The component produces at most one JPEG per second while the game is running.
# Unique capture IDs plus this session lock make ordinary Streamlit reruns inert.
if isinstance(capture, dict):
    capture_id = capture.get("capture_id")
    image_data_url = capture.get("image")
    new_capture = (isinstance(capture_id, str) and bool(capture_id)
                   and capture_id != st.session_state.rps_last_capture_id)
    if new_capture:
        # Acknowledge every unique frame, including one received as the user
        # stops the game. The browser waits for this ID before sampling again.
        st.session_state.rps_last_capture_id = capture_id
        if (st.session_state.rps_game_enabled and isinstance(image_data_url, str)
                and image_data_url.startswith("data:image/jpeg;base64,")):
            try:
                import cv2
                import numpy as np

                encoded = base64.b64decode(image_data_url.partition(",")[2], validate=True)
                frame = cv2.imdecode(np.frombuffer(encoded, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    raise ValueError("The camera frame could not be decoded.")
                detections, _ = detect_live_gestures(frame)
                event = tracker.update(game, detections, time.monotonic())
                st.session_state.rps_latest_detections = detections
                st.session_state.rps_last_event = event
            except Exception as error:
                st.session_state.rps_last_event = "error"
                st.session_state.rps_detection_error = (
                    f"Prediction failed: {type(error).__name__}: {error}"
                )
        # Refresh component arguments with the processed ID so its iframe can
        # release the one-frame-in-flight lock and schedule the next sample.
        # The unique ID is already stored, so this state-only rerun never
        # repeats YOLO for the same JPEG.
        st.rerun()

latest = st.session_state.rps_latest_detections
pair = valid_pair(latest)
left, right = st.columns(2)
for column, player, zone in ((left, "Player 1 — Left", "left"), (right, "Player 2 — Right", "right")):
    candidates = [d for d in latest if len(d) == 3 and
                  ((d[2] < .5) if zone == "left" else (d[2] >= .5))]
    confident = [d for d in candidates if d[0] in ("Rock", "Paper", "Scissors")
                 and d[1] >= MIN_CONFIDENCE]
    labels = {d[0] for d in confident}
    if pair:
        gesture = pair[0] if zone == "left" else pair[1]
        display = f"{gesture[0]} · {gesture[1]:.0%}"
    elif len(labels) > 1:
        display = "Ambiguous detection"
    elif confident:
        best = max(confident, key=lambda d: d[1])
        display = f"{best[0]} · {best[1]:.0%} (pair not confirmed)"
    else:
        display = "No valid gesture"
    column.subheader(player)
    column.metric("Detected gesture", display)

if game.completed:
    result = {"Player 1 Wins": "PLAYER 1 WINS!", "Player 2 Wins": "PLAYER 2 WINS!",
              "Draw": "IT'S A DRAW!"}.get(game.result, game.result)
    st.success(result)
    st.write(
        f"Player 1: **{game.player1}** ({game.player1_confidence:.0%}) · "
        f"Player 2: **{game.player2}** ({game.player2_confidence:.0%})"
    )
    st.info("Round complete! Both players, lower your hands out of the camera zones.")
elif not st.session_state.rps_game_enabled:
    st.info("Game stopped. Start the game when both players are ready.")
elif tracker.state == "WAITING_FOR_HANDS_DOWN":
    st.info("Both players, lower your hands out of the camera zones. Confirming both zones are clear…")
elif tracker.state == "BOTH_HANDS_CLEARED" or (
        tracker.state == "WAITING_FOR_HANDS" and game.round_id > 0):
    st.info("Ready for the next round! Raise both hands.")
elif tracker.state == "VALIDATE_GESTURES":
    st.info("Hold both gestures steady…")
elif tracker.state == "BOTH_HANDS_DETECTED":
    st.info("Both gestures detected. Hold steady…")
else:
    st.info("Both players, get ready!")

if st.session_state.rps_last_event == "error":
    st.error(st.session_state.get("rps_detection_error", "Gesture detection failed."))
if st.session_state.rps_game_enabled:
    st.caption(
        "Automatic mode waits for each YOLO prediction, then pauses 1.1 seconds before the next frame. "
        "Rearm requires two empty-zone predictions at least 0.8 seconds apart."
    )
else:
    st.caption("The live camera preview stays available; YOLO inference runs only while the game is started.")
