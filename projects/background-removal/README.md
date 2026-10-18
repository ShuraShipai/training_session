# Background Removal

Independent Streamlit app using the original `rembg.remove` algorithm.

```bash
cd projects/background-removal
python3.11 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8601
```

Upload PNG/JPEG/WEBP, process, preview, and download transparent PNG. The first run may download rembg's default model weights.
