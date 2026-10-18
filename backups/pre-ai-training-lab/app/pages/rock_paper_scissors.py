import hashlib
import streamlit as st
from app.components.game import Game, MIN_CONFIDENCE, valid_detection
from app.components.services import detect_gesture

st.title("Rock-Paper-Scissors")
st.write("Capture one hand, check the detection, then confirm your round.")
if "game" not in st.session_state:
    st.session_state.game = Game()
game = st.session_state.game
for column, label, value in zip(st.columns(3), ["Player", "Computer", "Draws"],
                                [game.player_score, game.computer_score, game.draws]):
    column.metric(label, value)


def advance(reset=False):
    if reset:
        game.reset()
    else:
        game.play_again()
    st.session_state.pop("gesture_preview", None)
    for name in list(st.session_state):
        if name.startswith(("camera_round_", "upload_round_")):
            del st.session_state[name]


st.button("Reset Score", on_click=advance, args=(True,))
if game.completed:
    st.success(game.result)
    st.write(f"Your move: **{game.player}** · Computer move: **{game.computer}**")
    preview = st.session_state.get("gesture_preview")
    if preview:
        st.caption(f"Detection confidence: {preview[1][0][1]:.0%}")
        st.image(preview[2], channels="BGR", width="stretch")
    st.button("Play Again", type="primary", on_click=advance)
else:
    method = st.radio("Gesture input", ["Camera", "Upload image"], horizontal=True)
    if method == "Camera":
        upload = st.camera_input("Capture your gesture", key=f"camera_round_{game.round_id}")
        st.caption("Allow camera access, then take a picture. You can also upload a photo.")
    else:
        upload = st.file_uploader("Choose a gesture photo", type=["jpg", "jpeg", "png", "webp"], key=f"upload_round_{game.round_id}")
    st.caption(f"Show one gesture clearly. A single detection with at least {MIN_CONFIDENCE:.0%} confidence is required. The computer has already chosen its move.")
    if upload is not None:
        data = upload.getvalue()
        key = (game.round_id, method, hashlib.sha256(data).hexdigest())
        if st.button("Detect gesture", type="primary"):
            st.session_state.pop("gesture_preview", None)
            try:
                with st.spinner("Detecting your gesture…"):
                    detections, image = detect_gesture(data)
                    st.session_state.gesture_preview = (key, detections, image)
            except Exception:
                st.error("Detection failed. Check the image and the server's original best.pt model and dependencies. No points were awarded.")
        preview = st.session_state.get("gesture_preview")
        if preview and preview[0] == key:
            st.image(preview[2], channels="BGR", width="stretch")
            detection = valid_detection(preview[1])
            for label, confidence in preview[1]:
                st.write(f"Detected: **{label}** · Confidence: **{confidence:.0%}**")
            if detection is None:
                st.warning("No single confident gesture found. Capture one clearly visible hand and try again. No points awarded.")
            if st.button("Confirm round", disabled=detection is None):
                if game.confirm(preview[1], key[0]):
                    st.rerun()
