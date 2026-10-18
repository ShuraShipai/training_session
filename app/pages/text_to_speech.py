import streamlit as st
from app.components.services import TTS_LANGUAGES, synthesize

st.title("Text-to-Speech")
st.write("Turn your words into an audio clip, ready to play or download.")
text = st.text_area("Enter your text", height=150, max_chars=5000)
language = st.selectbox("Language", list(TTS_LANGUAGES))
slow = st.checkbox("Speak slowly")
key = (text.strip(), language, slow)
st.caption("Text is sent to Google's speech service when you generate audio.")
if st.button("Generate speech", type="primary"):
    st.session_state.pop("tts_result", None)
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            with st.spinner("Generating audio…"):
                st.session_state.tts_result = (key, synthesize(text, language, slow))
        except Exception:
            st.error("Speech generation failed. Check the connection or try again with a shorter passage.")
result = st.session_state.get("tts_result")
if result and result[0] == key:
    st.audio(result[1], format="audio/mpeg")
    st.download_button("Download MP3", result[1], "speech.mp3", "audio/mpeg", on_click="ignore")
