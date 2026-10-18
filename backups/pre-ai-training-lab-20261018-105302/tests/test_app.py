from io import BytesIO
from pathlib import Path
import hashlib
import json
import unittest
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest
from app.components import services

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
        game = app.session_state["game"]
        game.computer = "Rock"
        game.confirm([("Paper", .9)], game.round_id)
        app.run()
        self.assertEqual(app.success[0].value, "You Win")
        next(b for b in app.button if b.label == "Play Again").click().run()
        self.assertEqual(app.session_state["game"].player_score, 1)
        self.assertFalse(app.session_state["game"].completed)
        next(b for b in app.button if b.label == "Reset Score").click().run()
        self.assertEqual(app.session_state["game"].player_score, 0)
        self.assertFalse(app.exception)

    def test_detect_confirm_rerun_and_replay_flow(self):
        import numpy as np
        frame = np.zeros((8, 8, 3), dtype=np.uint8)
        snapshot = BytesIO(b"camera fixture; inference mocked")
        with patch("streamlit.camera_input", return_value=snapshot), patch(
                "app.components.services.detect_gesture", return_value=([("Paper", .95)], frame)):
            app = AppTest.from_file(str(ROOT / "app/pages/rock_paper_scissors.py")).run()
            app.session_state["game"].computer = "Rock"
            next(b for b in app.button if b.label == "Detect gesture").click().run()
            self.assertEqual(app.session_state["game"].player_score, 0)
            next(b for b in app.button if b.label == "Confirm round").click().run()
            self.assertEqual(app.session_state["game"].player_score, 1)
            app.run()
            self.assertEqual(app.session_state["game"].player_score, 1)
            self.assertFalse(any(b.label == "Confirm round" for b in app.button))
            next(b for b in app.button if b.label == "Play Again").click().run()
            self.assertNotIn("gesture_preview", app.session_state)
            self.assertFalse(any(b.label == "Confirm round" for b in app.button))
            self.assertEqual(app.session_state["game"].player_score, 1)
            self.assertFalse(app.exception)

    def test_uncertain_detection_disables_confirmation(self):
        import numpy as np
        with patch("streamlit.camera_input", return_value=BytesIO(b"fixture")), patch(
                "app.components.services.detect_gesture", return_value=([("Rock", .4)], np.zeros((8, 8, 3), dtype=np.uint8))):
            app = AppTest.from_file(str(ROOT / "app/pages/rock_paper_scissors.py")).run()
            next(b for b in app.button if b.label == "Detect gesture").click().run()
            self.assertTrue(next(b for b in app.button if b.label == "Confirm round").disabled)
            self.assertEqual(app.session_state["game"].player_score, 0)
            self.assertEqual(len(app.warning), 1)

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
