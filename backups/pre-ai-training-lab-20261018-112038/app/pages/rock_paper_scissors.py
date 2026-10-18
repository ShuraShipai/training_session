"""Live two-player Rock-Paper-Scissors using the preserved YOLO checkpoint."""
import streamlit as st

from app.components.game import LocalGame, MIN_CONFIDENCE, valid_pair
from app.components.live_game import LiveDetectionState, make_video_callback


st.title("Rock-Paper-Scissors")
st.subheader("Live two-player game")
st.write("Play together in front of one camera. Player 1 stands on the left; Player 2 on the right.")

if "local_rps_game" not in st.session_state:
    st.session_state.local_rps_game = LocalGame()
if "live_detection_state" not in st.session_state:
    st.session_state.live_detection_state = LiveDetectionState()

game = st.session_state.local_rps_game
state = st.session_state.live_detection_state

for column, label, value in zip(
    st.columns(3),
    ["Player 1", "Player 2", "Draws"],
    [game.player1_score, game.player2_score, game.draws],
):
    column.metric(label, value)

top_controls = st.columns([1, 1, 4])
top_controls[0].button("Reset Score", on_click=game.reset)
if game.completed:
    top_controls[1].button("Play Again", type="primary", on_click=game.play_again)

try:
    from streamlit_webrtc import webrtc_streamer
except ImportError:
    st.error("Live camera support is not installed yet. Redeploy after adding streamlit-webrtc.")
else:
    st.caption(
        f"Live detection runs continuously. Show one clear hand each, one on either side. "
        f"Both gestures need at least {MIN_CONFIDENCE:.0%} confidence."
    )
    webrtc_streamer(
        key="local-two-player-rps-camera",
        video_frame_callback=make_video_callback(state),
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    @st.fragment(run_every=0.5)
    def live_round_controls():
        detections, error, fresh = state.snapshot()
        pair = valid_pair(detections)
        if error:
            st.error(f"Live detection error: {error}")
        if not fresh:
            st.info("Waiting for live camera detections…")
        elif pair:
            left, right = pair
            player1, player2 = st.columns(2)
            player1.metric("Player 1 · left", left[0], f"{left[1]:.0%} confidence")
            player2.metric("Player 2 · right", right[0], f"{right[1]:.0%} confidence")
        else:
            st.info("Show exactly two clear gestures at the same time, one on each side of the camera.")

        if game.completed:
            st.success(game.result)
            st.write(f"Player 1: **{game.player1}** · Player 2: **{game.player2}**")
            st.caption("This round is locked. Choose Play Again when you are ready.")
        elif st.button("Play Round", type="primary", disabled=pair is None):
            if game.confirm(detections, game.round_id):
                st.rerun()
            else:
                st.warning("The camera no longer has two fresh, confident gestures. No points awarded.")

    live_round_controls()
