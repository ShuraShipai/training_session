# AI Training Lab

## Live Application — Try It Online

The unified dashboard has not yet been deployed and verified. Its public link will be added here after the Streamlit build and feature tests pass.

| Application | Live Demo | Source Code |
|---|---|---|
| AI Training Lab — Background Removal, Text-to-Speech, Speech-to-Text, and Rock-Paper-Scissors | Pending verification | [Dashboard and pages](app/) |

AI Training Lab brings the four training projects together in one Streamlit website. Each feature keeps its existing processing engine and has its own page. The original source scripts and custom YOLO `best.pt` model are preserved.

## Features

- **Background Removal:** upload an image, remove its background with the existing rembg implementation, preview the transparent result, and download a PNG.
- **Text-to-Speech:** generate, play, and download gTTS audio in English, Hindi, Kannada, or Tamil.
- **Speech-to-Text:** record in the browser or upload WAV, then transcribe using the existing SpeechRecognition Google engine and language options.
- **Rock-Paper-Scissors:** browser camera or image input, existing YOLO `best.pt`, computer move, winner, score, replay, and reset. A single valid detection must be explicitly confirmed to score a round.

## Add another page

Create a Streamlit page as a `.py` file under `app/pages/`. The dashboard discovers page files automatically and adds them to Home and the navigation. Add any new package to the root `requirements.txt`. For a custom title or Home description, add its metadata to `PAGE_DETAILS` in `app/main.py`.

## Run locally

Use Python 3.12 and install the root requirements:

```bash
python3.12 -m venv .venv-lab
source .venv-lab/bin/activate
python -m pip install -r requirements.txt
streamlit run app/main.py
```

Background removal downloads rembg's default model weights on first use. YOLO/PyTorch dependencies are large; the app loads the original `best.pt` and does not retrain or substitute another model. Speech generation and transcription need outbound access to Google's services.

## Deployment status

The intended public target is one Streamlit Community Cloud app from `app/main.py`, using the root `requirements.txt`. Its Home page links to all four projects; adding a page under `app/pages/` extends the same app. Community Cloud can sleep after inactivity and has limited CPU and memory, so verify model startup and inference before publishing the URL.

The existing repository is [ShuraShipai/training_session](https://github.com/ShuraShipai/training_session). Deployment should use the latest branch containing `app/main.py` and all project files. The Codex workspace cannot reach GitHub or Streamlit Cloud, so it has not verified a commit or deployment. See [deployment notes](deployment/README.md) and the [test report](deployment/TEST_REPORT.md).

ngrok remains available for local demonstrations: `./deployment/start_four_apps.sh` exposes the independent project apps, not the unified dashboard. For the dashboard, start `streamlit run app/main.py` and expose its port with ngrok separately. The Free ngrok plan allows up to three simultaneous endpoints.

Browser camera and microphone use require visitor permission. For local OpenCV access, allow the terminal or IDE under macOS **System Settings → Privacy & Security → Camera**.
