"""Run from the repository root: streamlit run app/main.py."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st

st.set_page_config(page_title="AI Training Lab", layout="wide")


def home():
    st.title("AI Training Lab")
    st.write("Four hands-on projects. Bring an image, a few words, or your next move.")
    st.divider()
    cards = [
        ("Background Removal", "Turn a photo into a transparent PNG.", "pages/background_removal.py", "Open image studio"),
        ("Text-to-Speech", "Give your words a voice in four languages.", "pages/text_to_speech.py", "Create speech"),
        ("Speech-to-Text", "Record or upload audio and take away a transcript.", "pages/speech_to_text.py", "Transcribe audio"),
        ("Rock-Paper-Scissors", "Show your hand. Confirm your move. Play a round.", "pages/rock_paper_scissors.py", "Play the game"),
    ]
    for offset in (0, 2):
        for column, (title, description, page, label) in zip(st.columns(2), cards[offset:offset+2]):
            with column, st.container(border=True):
                st.subheader(title)
                st.write(description)
                st.page_link(page, label=label, use_container_width=True)
    st.caption("Images are processed on the app server. Speech features use Google's services. Download results before closing your session.")


navigation = st.navigation([
    st.Page(home, title="Home", default=True),
    st.Page("pages/background_removal.py", title="Background Removal", url_path="background-removal"),
    st.Page("pages/text_to_speech.py", title="Text-to-Speech", url_path="text-to-speech"),
    st.Page("pages/speech_to_text.py", title="Speech-to-Text", url_path="speech-to-text"),
    st.Page("pages/rock_paper_scissors.py", title="Rock-Paper-Scissors", url_path="rock-paper-scissors"),
])
with st.sidebar:
    st.divider()
    st.caption("AI Training Lab · Images, voice & play")
navigation.run()
