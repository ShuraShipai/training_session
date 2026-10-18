import hashlib
import streamlit as st
import speech_recognition as sr
from app.components.services import STT_LANGUAGES, transcribe

st.title("Speech-to-Text")
st.write("Record a short message or upload a WAV file.")
language = st.selectbox("Language", list(STT_LANGUAGES))
method = st.radio("Audio input", ["Record audio", "Upload WAV"], horizontal=True)
if method == "Record audio":
    upload = st.audio_input("Record your voice", sample_rate=16000)
    st.caption("Allow microphone access in your browser. If recording is unavailable, use Upload WAV.")
else:
    upload = st.file_uploader("Choose a WAV file", type=["wav"])
st.caption("Up to two minutes and 10 MB. Audio is sent to Google's recognition service when you transcribe.")
if upload is not None:
    data = upload.getvalue()
    key = (hashlib.sha256(data).hexdigest(), language)
    st.audio(data)
    if st.button("Transcribe audio", type="primary"):
        st.session_state.pop("stt_result", None)
        try:
            with st.spinner("Recognizing speech…"):
                st.session_state.stt_result = (key, transcribe(data, language))
        except sr.UnknownValueError:
            st.warning("No clear speech was recognized. Try a clearer recording and check the selected language.")
        except sr.RequestError:
            st.error("The recognition service is unavailable. Please try again later.")
        except Exception:
            st.error("Audio could not be processed. Use an uncompressed PCM WAV under two minutes and 10 MB; the server also needs FLAC.")
    result = st.session_state.get("stt_result")
    if result and result[0] == key:
        st.subheader("Transcript")
        st.code(result[1], language=None, wrap_lines=True)
        st.caption("Use the copy control above or download the text.")
        st.download_button("Download transcript", result[1], "transcription.txt", "text/plain", on_click="ignore")
