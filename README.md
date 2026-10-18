# AI Training Lab

## Live Application — Try It Online

The dashboard is live. The continuous two-player camera update is prepared in the repository but is not on the deployed branch until published and rebuilt.

| Application | Live Demo | Source Code |
|---|---|---|
| AI Training Lab — Background Removal, Text-to-Speech, Speech-to-Text, and Rock-Paper-Scissors | [Open the dashboard](https://trainingsession.streamlit.app/) | [Dashboard and pages](app/) |

AI Training Lab brings the four training projects together in one Streamlit website. Each feature keeps its existing processing engine and has its own page. The original source scripts and custom YOLO `best.pt` model are preserved.

## Features

- **Background Removal:** upload an image, remove its background with the existing rembg implementation, preview the transparent result, and download a PNG.
- **Text-to-Speech:** generate, play, and download gTTS audio in English, Hindi, Kannada, or Tamil.
- **Speech-to-Text:** record in the browser or upload WAV, then transcribe using the existing SpeechRecognition Google engine and language options.
- **Rock-Paper-Scissors:** live browser camera, existing YOLO `best.pt`, two players in front of one laptop, detected moves, winner, scores, replay, and reset. Both confident gestures must be present; press **Play Round** to score once. Video frames never score by themselves.

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

The existing repository is [ShuraShipai/training_session](https://github.com/ShuraShipai/training_session). The current live app was deployed from branch `codex/ai-training-lab-20261018-101637`. The updated live-camera game needs to be pushed to that branch and rebuilt before it appears online. See [deployment notes](deployment/README.md) and the [test report](deployment/TEST_REPORT.md).

ngrok remains available for local demonstrations: `./deployment/start_four_apps.sh` exposes the independent project apps, not the unified dashboard. For the dashboard, start `streamlit run app/main.py` and expose its port with ngrok separately. The Free ngrok plan allows up to three simultaneous endpoints.

The live game uses WebRTC, so allow camera access in your browser when prompted. Its public camera stream requires HTTPS and a network that permits WebRTC; some restricted networks may also require a TURN server.
