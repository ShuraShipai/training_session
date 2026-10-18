from io import BytesIO
from pathlib import Path
import hashlib
import json
import base64
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest
from app.components import services
from app.components.game import LocalGame

ROOT = Path(__file__).resolve().parents[1]


class AppTests(unittest.TestCase):
    def test_home_and_all_navigation_targets(self):
        app = AppTest.from_file(str(ROOT / "app/main.py")).run()
        self.assertFalse(app.exception)
        self.assertEqual(app.title[0].value, "AI Training Lab")
        self.assertEqual(len(app.get("page_link")), 4)
        for route, title in [("background_removal", "Background Removal"),
                             ("text_to_speech", "Text-to-Speech"),
                             ("speech_to_text", "Speech-to-Text"),
                             ("rock_paper_scissors", "Rock-Paper-Scissors")]:
            # Streamlit 1.50's switch_page hashes the filename, ignoring custom
            # url_path. Use the route hash to simulate the actual navigation.
            app._page_hash = hashlib.md5(route.replace("_", "-").encode()).hexdigest()
            app.run()
            self.assertFalse(app.exception, route)
            self.assertEqual(app.title[0].value, title)

    def test_tts_blank_and_service_failure(self):
        app = AppTest.from_file(str(ROOT / "app/pages/text_to_speech.py")).run()
        app.button[0].click().run()
        self.assertEqual(len(app.warning), 1)
        with patch("app.components.services.synthesize", side_effect=RuntimeError("offline")):
            app.text_area[0].input("Hello").run()
            app.button[0].click().run()
        self.assertEqual(len(app.error), 1)
        self.assertNotIn("tts_result", app.session_state)

    def test_tts_output_and_stale_output(self):
        app = AppTest.from_file(str(ROOT / "app/pages/text_to_speech.py")).run()
        with patch("app.components.services.synthesize", return_value=b"mock audio"):
            app.text_area[0].input("Hello").run()
            app.button[0].click().run()
        self.assertEqual(len(app.get("audio")), 1)
        self.assertEqual(len(app.get("download_button")), 1)
        app.selectbox[0].select("Hindi").run()
        self.assertEqual(len(app.get("audio")), 0)

    def test_game_completed_round_and_reset_controls(self):
        app = AppTest.from_file(str(ROOT / "app/pages/rock_paper_scissors.py")).run()
        app.session_state["local_rps_game"] = LocalGame()
        app.run()
        self.assertTrue(any(b.label == "Reset Score" for b in app.button))
        self.assertTrue(any(m.label == "Player 1" for m in app.metric))
        self.assertFalse(app.exception)

    def test_live_rps_page_and_unready_round(self):
        app = AppTest.from_file(str(ROOT / "app/pages/rock_paper_scissors.py")).run()
        self.assertTrue(any(b.label == "Reset Score" for b in app.button))
        self.assertEqual(app.session_state["local_rps_game"].player1_score, 0)
        self.assertFalse(app.exception)

    def test_one_prediction_per_unique_round_capture(self):
        import numpy as np

        payload = {
            "capture_id": "capture-1",
            "image": "data:image/jpeg;base64," + base64.b64encode(b"frame").decode("ascii"),
        }
        cv2_stub = ModuleType("cv2")
        cv2_stub.IMREAD_COLOR = 1
        cv2_stub.imdecode = lambda *_args: np.zeros((16, 16, 3), dtype=np.uint8)
        annotated = np.zeros((16, 16, 3), dtype=np.uint8)
        detections = [("Paper", .91, .2), ("Rock", .86, .8)]

        with patch("app.components.browser_camera._camera_component", return_value=None) as component, \
             patch("app.components.services.detect_live_gestures", return_value=(detections, annotated)) as predict, \
             patch.dict("sys.modules", {"cv2": cv2_stub}):
            app = AppTest.from_file(str(ROOT / "app/pages/rock_paper_scissors.py")).run()
            component.return_value = payload
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(predict.call_count, 1)
            self.assertEqual(app.session_state["local_rps_game"].player1_score, 1)
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(predict.call_count, 1)

    def test_gesture_model_resource_is_loaded_once(self):
        from app.components import services

        model_path = ROOT / "projects/rock-paper-scissors/best.pt"
        model = SimpleNamespace(names={0: "Paper", 1: "Rock", 2: "Scissors"})
        ultralytics_stub = ModuleType("ultralytics")
        with patch("app.components.services.MODEL_PATH", model_path), \
             patch("app.components.services.MODEL_SHA256", hashlib.sha256(model_path.read_bytes()).hexdigest()), \
             patch.dict("sys.modules", {"ultralytics": ultralytics_stub}):
            from unittest.mock import Mock
            ultralytics_stub.YOLO = Mock(return_value=model)
            services.gesture_model.clear()
            try:
                loaded_once = services.gesture_model()
                loaded_twice = services.gesture_model()
                self.assertIs(loaded_once, model)
                self.assertIs(loaded_twice, model)
                ultralytics_stub.YOLO.assert_called_once_with(str(model_path))
            finally:
                services.gesture_model.clear()

    def test_originals_preserved(self):
        manifest = json.loads((ROOT / "deployment/original-files.json").read_text())
        for record in manifest:
            preserved = ROOT / record["preserved_copy"]
            self.assertTrue(preserved.is_file(), record["preserved_copy"])
            self.assertEqual(hashlib.sha256(preserved.read_bytes()).hexdigest(), record["sha256"])

    def test_real_image_decode_and_invalid_input(self):
        image = services.read_image((ROOT / "Image.jpeg").read_bytes())
        self.assertGreater(image.width, 0)
        with self.assertRaises(Exception):
            services.read_image(b"invalid image")
        with self.assertRaises(ValueError):
            services.check_upload(b"x" * (services.MAX_UPLOAD_BYTES + 1))

    def test_original_language_options(self):
        self.assertEqual(list(services.TTS_LANGUAGES.values()), ["en", "hi", "kn", "ta"])
        self.assertEqual(list(services.STT_LANGUAGES.values()),
                         ["en-IN", "hi-IN", "kn-IN", "ur-PK", "ta-IN", "ml-IN", "te-IN", "ar-SA", "fr-FR", "es-ES"])

    def test_invalid_audio_handled_before_service_call(self):
        with self.assertRaises(ValueError):
            services.transcribe(b"not a WAV", "English")
