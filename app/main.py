"""Run from the repository root: streamlit run app/main.py."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import streamlit as st

st.set_page_config(page_title="AI Training Lab", layout="wide")

PAGE_DETAILS = {
    "background_removal": (
        "Background Removal", "Turn a photo into a transparent PNG.", "Open image studio", "background-removal"
    ),
    "text_to_speech": (
        "Text-to-Speech", "Give your words a voice in four languages.", "Create speech", "text-to-speech"
    ),
    "speech_to_text": (
        "Speech-to-Text", "Record or upload audio and take away a transcript.", "Transcribe audio", "speech-to-text"
    ),
    "rock_paper_scissors": (
        "Rock-Paper-Scissors", "Show your hand. Confirm your move. Play a round.", "Play the game", "rock-paper-scissors"
    ),
}


def discover_pages():
    """Discover Streamlit page files; new pages appear in navigation and on Home."""
    pages = []
    for file in sorted((Path(__file__).parent / "pages").glob("*.py")):
        if file.name == "__init__.py":
            continue
        stem = file.stem
        title, description, action, route = PAGE_DETAILS.get(
            stem,
            (stem.replace("_", " ").title(), "Explore this project.", "Open project", stem.replace("_", "-")),
        )
        pages.append({
            "path": f"pages/{file.name}",
            "title": title,
            "description": description,
            "action": action,
            "route": route,
        })
    return pages


PAGES = discover_pages()


def home():
    st.title("AI Training Lab")
    st.write("Four hands-on projects. Bring an image, a few words, or your next move.")
    st.divider()
    for offset in range(0, len(PAGES), 2):
        for column, page in zip(st.columns(2), PAGES[offset:offset + 2]):
            with column, st.container(border=True):
                st.subheader(page["title"])
                st.write(page["description"])
                st.page_link(page["path"], label=page["action"], use_container_width=True)
    st.caption("Add another Python page file under app/pages/ to extend the lab. Add its dependencies to requirements.txt.")
    st.caption("Images are processed on the app server. Speech features use Google's services. Download results before closing your session.")


navigation = st.navigation(
    [st.Page(home, title="Home", default=True)]
    + [
        st.Page(page["path"], title=page["title"], url_path=page["route"])
        for page in PAGES
    ]
)
with st.sidebar:
    st.divider()
    st.caption("AI Training Lab · Images, voice & play")
navigation.run()
