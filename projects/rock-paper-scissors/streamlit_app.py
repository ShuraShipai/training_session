"""Independent browser-camera game using the existing custom best.pt model."""
import hashlib
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from game_logic import Game, MOVES, MIN_CONFIDENCE, valid_detection

MODEL_PATH = Path(__file__).with_name("best.pt")


@st.cache_resource
def load_model():
    from ultralytics import YOLO
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Existing model not found: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))
    if set(model.names.values()) != set(MOVES):
        raise ValueError("best.pt does not contain the expected Rock/Paper/Scissors labels")
    return model


def detect(data):
    import cv2
    import numpy as np
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Could not decode the captured image")
    result = load_model()(frame)[0]
    detections = [(result.names[int(box.cls.item())], float(box.conf.item())) for box in result.boxes]
    return detections, result.plot()


def play_again():
    st.session_state.game.play_again()
    st.session_state.pop("preview", None)


def reset_score():
    st.session_state.game.reset()
    st.session_state.pop("preview", None)


st.set_page_config(page_title="Rock Paper Scissors", page_icon="✊")
st.title("Rock-Paper-Scissors")
st.write("Capture one gesture, inspect the model result, then confirm exactly one round.")
if "game" not in st.session_state:
    st.session_state.game = Game()
game = st.session_state.game
cols = st.columns(3)
for col, label, key in zip(cols, ("Player", "Computer", "Draws"), ("player_score", "computer_score", "draws")):
    col.metric(label, getattr(game, key))

st.button("Reset Score", on_click=reset_score)
if game.completed:
    st.success(game.result)
    st.write(f"Your move: **{game.player}** · Computer move: **{game.computer}**")
    st.button("Play Again", type="primary", on_click=play_again)
else:
    method = st.radio("Gesture input", ("Camera", "Upload image"), horizontal=True)
    if method == "Camera":
        upload = st.camera_input("Capture your gesture", key=f"camera_{game.round_id}")
        st.caption("Allow camera access, then take a picture. Image upload is also available.")
    else:
        upload = st.file_uploader("Choose a gesture photo", type=("jpg", "jpeg", "png", "webp"), key=f"upload_{game.round_id}")
    st.caption(f"One clear gesture with at least {MIN_CONFIDENCE:.0%} confidence is required. The computer chose independently before your detection.")
    if upload:
        data = upload.getvalue()
        image_key = hashlib.sha256(data).hexdigest()
        if st.button("Detect gesture", type="primary"):
            st.session_state.pop("preview", None)
            try:
                detections, annotated = detect(data)
                st.session_state.preview = (game.round_id, image_key, detections, annotated)
            except Exception as exc:
                st.error(f"Detection failed; no points awarded. {exc}")
        preview = st.session_state.get("preview")
        if preview and preview[:2] == (game.round_id, image_key):
            _, _, detections, annotated = preview
            st.image(annotated, channels="BGR", use_container_width=True)
            for label, confidence in detections:
                st.write(f"Detected: **{label}** · confidence {confidence:.0%}")
            if valid_detection(detections) is None:
                st.warning("Need exactly one valid gesture at or above 60% confidence. No points awarded.")
            if st.button("Confirm round", disabled=valid_detection(detections) is None):
                # The completed flag and round id make this a one-result-per-round action.
                if game.confirm(detections, preview[0]):
                    st.rerun()
