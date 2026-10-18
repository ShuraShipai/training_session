
import streamlit as st
import speech_recognition as sr
import hashlib
import os
import shutil
import speech_recognition.audio as sr_audio

st.set_page_config(
    page_title="Speech to Text",
    page_icon="🎤"
)

# Prefer Homebrew's native FLAC executable on Mac
flac_path = shutil.which("flac")
if flac_path:
    sr_audio.get_flac_converter = lambda: flac_path

st.title("🎤 Speech to Text")
st.write("Record your voice or upload an audio file.")

languages = {
    "English": "en-IN",
    "Hindi": "hi-IN",
    "Kannada": "kn-IN",
    "Urdu": "ur-PK",
    "Tamil": "ta-IN",
    "Malayalam": "ml-IN",
    "Telugu": "te-IN",
    "Arabic": "ar-SA",
    "French": "fr-FR",
    "Spanish": "es-ES"
}

language = st.selectbox(
    "Select Language",
    list(languages.keys())
)

method = st.radio(
    "Audio Input",
    ["Record Audio", "Upload Audio"]
)

if method == "Record Audio":
    audio_file = st.audio_input(
        "Record your voice",
        sample_rate=16000
    )
else:
    audio_file = st.file_uploader(
        "Upload a WAV file",
        type=["wav"]
    )

if audio_file is not None:
    audio_bytes = audio_file.getvalue()
    audio_key = (
        hashlib.sha256(audio_bytes).hexdigest(),
        language
    )

    st.audio(audio_bytes)

    if st.button("Convert to Text", type="primary"):
        st.session_state.pop("result", None)
        st.session_state.pop("result_key", None)

        try:
            recognizer = sr.Recognizer()

            with sr.AudioFile(audio_file) as source:
                audio_data = recognizer.record(source)

            with st.spinner("Recognizing speech..."):
                text = recognizer.recognize_google(
                    audio_data,
                    language=languages[language]
                )

            st.session_state["result"] = text
            st.session_state["result_key"] = audio_key

        except sr.UnknownValueError:
            st.error(
                "Speech not understood. "
                "Try speaking clearly for 5–10 seconds."
            )

        except sr.RequestError as e:
            st.error(f"Recognition service error: {e}")

        except Exception as e:
            st.error(f"Error: {e}")

    if (
        st.session_state.get("result_key") == audio_key
        and st.session_state.get("result")
    ):
        st.success("Speech recognized!")

        text = st.text_area(
            "Recognized Text",
            st.session_state["result"],
            height=150
        )

        st.download_button(
            "Download Text",
            text,
            file_name="transcription.txt"
        )
