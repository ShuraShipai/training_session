"""Thin adapters: keep original inference calls, engines and language codes."""
from io import BytesIO
from pathlib import Path
import hashlib
import shutil
import threading
import warnings

import streamlit as st
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "projects/rock-paper-scissors/best.pt"
MODEL_SHA256 = "19e751506467c8179b39d48a0fec4a1cd1b5e017afaf2fad85dd865b009fc691"
MAX_IMAGE_PIXELS = 12_000_000
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
TTS_LANGUAGES = {"English": "en", "Hindi": "hi", "Kannada": "kn", "Tamil": "ta"}
STT_LANGUAGES = {
    "English": "en-IN", "Hindi": "hi-IN", "Kannada": "kn-IN",
    "Urdu": "ur-PK", "Tamil": "ta-IN", "Malayalam": "ml-IN",
    "Telugu": "te-IN", "Arabic": "ar-SA", "French": "fr-FR", "Spanish": "es-ES",
}


def check_upload(data):
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Choose a nonempty file up to 10 MB.")


def read_image(data):
    check_upload(data)
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(BytesIO(data)) as image:
            if image.width * image.height > MAX_IMAGE_PIXELS:
                raise ValueError("Choose an image with at most 12 megapixels.")
            image.load()
            return image.copy()


@st.cache_resource(show_spinner=False)
def inference_lock():
    # Both engines share the CPU budget; user outputs are never globally cached.
    return threading.Lock()


@st.cache_resource(show_spinner=False)
def background_session():
    from rembg import new_session
    # rembg.remove(bytes) creates this same default u2net session internally.
    return new_session()


def remove_background(data):
    read_image(data)
    from rembg import remove
    with inference_lock():
        return remove(data, session=background_session())


def synthesize(text, language, slow=False):
    from gtts import gTTS
    if not text.strip() or len(text) > 5000:
        raise ValueError("Enter between 1 and 5,000 characters.")
    audio = BytesIO()
    gTTS(text=text.strip(), lang=TTS_LANGUAGES[language], slow=slow,
         timeout=(10, 30)).write_to_fp(audio)
    result = audio.getvalue()
    if not result:
        raise ValueError("No audio was generated. Please try again.")
    return result


def transcribe(data, language):
    import speech_recognition as sr
    import speech_recognition.audio as sr_audio
    check_upload(data)
    flac_path = shutil.which("flac")
    if flac_path:
        sr_audio.get_flac_converter = lambda: flac_path
    recognizer = sr.Recognizer()
    recognizer.operation_timeout = 30
    with sr.AudioFile(BytesIO(data)) as source:
        if source.DURATION > 120:
            raise ValueError("Use a recording of two minutes or less.")
        audio_data = recognizer.record(source)
    return recognizer.recognize_google(audio_data, language=STT_LANGUAGES[language])


@st.cache_resource(show_spinner=False)
def gesture_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError("The original best.pt model is missing.")
    if hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest() != MODEL_SHA256:
        raise ValueError("The gesture model differs from the preserved original.")
    from ultralytics import YOLO
    model = YOLO(str(MODEL_PATH))
    if set(model.names.values()) != {"Rock", "Paper", "Scissors"}:
        raise ValueError("The model does not contain the expected gesture labels.")
    return model


def detect_gesture(data):
    read_image(data)
    import cv2
    import numpy as np
    # OpenCV decodes browser snapshots to BGR, matching VideoCapture frames.
    frame = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise ValueError("This image could not be decoded.")
    with inference_lock():
        model = gesture_model()
        result = model(frame)[0]  # Preserve original default preprocessing/inference.
        detections = [(result.names[int(box.cls.item())], float(box.conf.item()))
                      for box in result.boxes]
        annotated = result.plot()
    return detections, annotated


def detect_live_gestures(frame, *, annotate=False):
    """Run the preserved YOLO inference pipeline on one live BGR camera frame."""
    if getattr(frame, "ndim", None) != 3 or frame.shape[2] != 3:
        raise ValueError("Expected a BGR video frame.")
    with inference_lock():
        model = gesture_model()
        # The camera view contains two smaller hands than the original single-hand
        # training examples. A 768px inference canvas recovers the left gesture on
        # the user's supplied camera frame without changing weights or labels.
        result = model(frame, imgsz=768, verbose=False)[0]
        detections = []
        frame_width = frame.shape[1]
        for box in result.boxes:
            x1, _, x2, _ = box.xyxy[0].tolist()
            detections.append((
                result.names[int(box.cls.item())],
                float(box.conf.item()),
                ((x1 + x2) / 2) / frame_width,
            ))
        annotated = None
        if annotate:
            annotated = result.plot()
            # Keep the two-player camera lanes visible when a caller displays it.
            import cv2
            height, width = annotated.shape[:2]
            divider_x = width // 2
            cv2.line(annotated, (divider_x, 0), (divider_x, height), (80, 190, 110), 3)
            cv2.putText(annotated, "PLAYER 1", (18, 34), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (80, 190, 110), 2, cv2.LINE_AA)
            cv2.putText(annotated, "PLAYER 2", (divider_x + 18, 34), cv2.FONT_HERSHEY_SIMPLEX,
                        0.8, (80, 190, 110), 2, cv2.LINE_AA)
    return detections, annotated
