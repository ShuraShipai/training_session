"""Explicit real-service checks, separate from offline tests. Run from repo root.

Use --ml only when ready for the default rembg model download.
"""
import argparse
import json
from io import BytesIO
from pathlib import Path
import subprocess
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.components import services

parser = argparse.ArgumentParser()
parser.add_argument("--ml", action="store_true", help="Run real rembg and YOLO inference; rembg may download U2Net")
args = parser.parse_args()
results = {}


def check(name, action):
    try:
        detail = action()
        results[name] = {"status": "passed", "detail": detail}
    except Exception as error:
        results[name] = {"status": "failed", "error_type": type(error).__name__, "detail": str(error)}


def speech():
    audio = services.synthesize("Hello from AI Training Lab.", "English")
    assert len(audio) > 100
    return f"Generated {len(audio)} MP3 bytes"


def transcription():
    # macOS's installed voice creates a non-silent fixture, not fake recognition.
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "speech.wav"
        subprocess.run(["say", "-o", str(path), "--file-format=WAVE", "--data-format=LEI16@16000", "Hello from the training lab"], check=True, capture_output=True)
        text = services.transcribe(path.read_bytes(), "English")
        assert text.strip()
        return text


check("gtts_real_request", speech)
check("google_real_transcription", transcription)
if args.ml:
    from PIL import Image
    data = (services.ROOT / "assets/Image.jpeg").read_bytes()
    def background():
        result = services.remove_background(data)
        image = Image.open(BytesIO(result))
        assert image.format == "PNG" and image.mode == "RGBA"
        return f"Transparent PNG {image.size}"
    check("rembg_real_inference", background)
    check("yolo_real_inference", lambda: str(services.detect_gesture(data)[0]))
else:
    for name in ("rembg_real_inference", "yolo_real_inference"):
        results[name] = {"status": "not_run", "detail": "ML dependencies unavailable; --ml explicitly enables model use"}
print(json.dumps(results, indent=2))
sys.exit(any(v["status"] == "failed" for v in results.values()))
