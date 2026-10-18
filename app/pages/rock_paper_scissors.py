"""Local two-player RPS using the Mac's OpenCV camera and preserved YOLO model."""
import time

import streamlit as st

from app.components.game import LocalGame, MIN_CONFIDENCE, valid_pair
from app.components.services import detect_live_gestures


st.title("Rock-Paper-Scissors")
st.subheader("Play together in front of this laptop")
st.write("Stand side by side: Player 1 on the left, Player 2 on the right. Show your gestures together.")

if "local_rps_game" not in st.session_state:
    st.session_state.local_rps_game = LocalGame()
if "opencv_camera" not in st.session_state:
    st.session_state.opencv_camera = None
if "opencv_last_inference" not in st.session_state:
    st.session_state.opencv_last_inference = 0.0
if "opencv_annotated_frame" not in st.session_state:
    st.session_state.opencv_annotated_frame = None
if "opencv_camera_error" not in st.session_state:
    st.session_state.opencv_camera_error = None
if "opencv_detections" not in st.session_state:
    st.session_state.opencv_detections = ()

game = st.session_state.local_rps_game

score_columns = st.columns(3)
score_columns[0].metric("Player 1", game.player1_score)
score_columns[1].metric("Player 2", game.player2_score)
score_columns[2].metric("Draws", game.draws)

controls = st.columns([1, 1, 4])
controls[0].button("Reset Score", on_click=game.reset)
if game.completed:
    controls[1].button("Play Again", type="primary", on_click=game.play_again)

st.caption(f"Live detection · one hand on each side · minimum confidence {MIN_CONFIDENCE:.0%}")


def stop_camera():
    camera = st.session_state.get("opencv_camera")
    if camera is not None:
        camera.release()
    st.session_state.opencv_camera = None


def start_camera():
    import cv2

    stop_camera()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        camera.release()
        st.session_state.opencv_camera_error = (
            "OpenCV could not open the laptop camera. Allow camera access for Terminal, "
            "iTerm, or the app running Streamlit in macOS System Settings → "
            "Privacy & Security → Camera, then restart this app."
        )
        return
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    st.session_state.opencv_camera = camera
    st.session_state.opencv_camera_error = None
    st.session_state.opencv_last_inference = 0.0
    st.session_state.opencv_annotated_frame = None
    st.session_state.opencv_detections = ()


if st.session_state.opencv_camera is None:
    st.button("Start live camera", type="primary", on_click=start_camera)
    st.info("This no-relay camera mode works when you run the app on the same laptop as the camera.")
    if st.session_state.opencv_camera_error:
        st.error(st.session_state.opencv_camera_error)
else:
    st.button("Stop camera", on_click=stop_camera)

if game.completed:
    st.success(game.result)
    st.write(f"Player 1: **{game.player1}** · Player 2: **{game.player2}**")

if st.session_state.opencv_camera is not None:
    @st.fragment(run_every=0.15)
    def live_camera_game():
        camera = st.session_state.opencv_camera
        if camera is None:
            st.info("Camera stopped.")
            return

        ok, frame = camera.read()
        if not ok:
            st.session_state.opencv_camera_error = "The camera stopped returning frames. Stop and start the camera again."
            stop_camera()
            st.error(st.session_state.opencv_camera_error)
            return

        now = time.monotonic()
        if now - st.session_state.opencv_last_inference >= 0.33:
            try:
                detections, annotated = detect_live_gestures(frame)
                st.session_state.opencv_detections = tuple(detections)
                st.session_state.opencv_annotated_frame = annotated
                st.session_state.opencv_last_inference = now
            except Exception as error:
                st.session_state.opencv_camera_error = f"Gesture detection failed: {type(error).__name__}: {error}"

        if st.session_state.opencv_annotated_frame is not None:
            st.image(
                st.session_state.opencv_annotated_frame,
                channels="BGR",
                use_container_width=True,
            )
        if st.session_state.opencv_camera_error:
            st.error(st.session_state.opencv_camera_error)

        detections = st.session_state.opencv_detections
        pair = valid_pair(detections)
        if pair:
            left, right = pair
            first, second = st.columns(2)
            first.metric("Player 1 · left", left[0], f"{left[1]:.0%} confidence")
            second.metric("Player 2 · right", right[0], f"{right[1]:.0%} confidence")
        else:
            st.info("Show exactly two clear gestures at the same time, one on each side of the divider.")

        if game.completed:
            st.caption("Round complete. Choose Play Again above when both players are ready.")
        elif st.button("Play Round", type="primary", disabled=pair is None):
            if game.confirm(detections, game.round_id):
                st.rerun()
            else:
                st.warning("The latest camera frame does not contain two fresh, confident gestures. No points awarded.")

    live_camera_game()
