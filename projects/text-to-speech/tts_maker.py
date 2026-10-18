import streamlit as st
from gtts import gTTS
from io import BytesIO

st.set_page_config(page_title="Text to Speech Converter", page_icon=":microphone:")

st.title("Text to Speech Converter")

text = st.text_area("Enter your text:", height=150)

languages= {
    "English": "en",
    "Hindi": "hi",
    "Kannada": "kn",
    "Tamil": "ta"
}

lang_name=st.selectbox("Language:",list(languages.keys()))
slow=st.checkbox("Speak slowly")

if st.button("Convert to Speech"):
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        with st.spinner("Generating audio..."):
            try:
                tts = gTTS(text=text.strip(), lang=languages[lang_name], slow=slow)
                audio = BytesIO()
                tts.write_to_fp(audio)
                audio_bytes = audio.getvalue()
                if not audio_bytes:
                    raise ValueError("No audio was generated. Please try again.")
                st.session_state["speech_audio"] = audio_bytes
            except Exception as e:
                st.error(f"An error occurred: {e}")

if st.session_state.get("speech_audio"):
    audio_bytes = st.session_state["speech_audio"]
    st.audio(audio_bytes, format="audio/mpeg")
    st.download_button(
        label="Download Audio",
        data=audio_bytes,
        file_name="speech.mp3",
        mime="audio/mpeg",
        on_click="ignore",
    )
