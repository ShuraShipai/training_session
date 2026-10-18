# Text-to-Speech

Independent Streamlit app preserving the existing gTTS languages and speech generation.

```bash
cd projects/text-to-speech
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run tts_maker.py --server.port 8602
```

Enter text, choose English/Hindi/Kannada/Tamil, generate, play, or download MP3. Requires Google service connectivity.
