# Speech-to-Text

Independent Streamlit app preserving SpeechRecognition with Google's recognition service and the existing language options.

```bash
cd projects/speech-to-text
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run stt_maker.py --server.port 8603
```

Record in the browser or upload WAV. Requires microphone permission for recording and internet connectivity for transcription.
