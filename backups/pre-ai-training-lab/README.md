---
title: AI Training Lab
sdk: docker
app_port: 7860
---

# AI Training Lab

Four AI training projects in one Streamlit application: remove an image background, generate speech, transcribe audio, and play rock-paper-scissors against the computer.

**Status:** implemented locally with offline tests passing. Five downloaded notebooks have been inspected and organized; one original contains a credential and is excluded from Git, with a sanitized copy prepared. GitHub synchronization, deployment, real ML inference, and successful external speech processing are not yet verified. See [the test report](deployment/TEST_REPORT.md). No public application URL has been issued.

The intended existing repository is [ShuraShipai/training_session](https://github.com/ShuraShipai/training_session). Remote contents and history could not be read from the development sandbox; this link is the user-provided destination, not confirmation of a successful push.

## Projects

| Project | Features | Existing engine preserved |
| --- | --- | --- |
| Background Removal | Image upload, original/result previews, transparent PNG download | `rembg.remove`, default U²-Net |
| Text-to-Speech | Four languages, slow speech, playback, MP3 download | gTTS |
| Speech-to-Text | Browser recording, WAV upload, ten languages, copy/download transcript | SpeechRecognition `recognize_google` |
| Rock-Paper-Scissors | Camera snapshot or upload, confidence, explicit confirmation, winner, scores, replay/reset | Ultralytics YOLO and original `best.pt` |

TTS languages: English, Hindi, Kannada, Tamil. STT languages: English, Hindi, Kannada, Urdu, Tamil, Malayalam, Telugu, Arabic, French, Spanish. Original language codes are unchanged.

The computer commits a random move before the player's detection. Only one recognized gesture at 60% confidence or above can be confirmed. Multiple detections, unknown labels, invalid confidence values and stale confirmations cannot score. Completed rounds stay locked until Play Again. Reset Score clears the counters and starts a fresh round. Scores belong to the browser session and do not persist across server restarts or disconnected sessions.

## Repository layout

```text
app/main.py                         Unified entry point and four home cards
app/pages/                          Four navigable project pages
app/components/                     Engine adapters and tested round state
projects/                           Byte-identical copies of original scripts
projects/rock-paper-scissors/best.pt  Original custom model, used by the app
assets/Image.jpeg                   Preserved sample image
experiments/                        Preserved unrelated experiments and general YOLO model
notebooks/original-colab-notebooks/  Original relevant Colab notebooks
notebooks/publishable/               Sanitized public copy of credential-bearing notebook
experiments/notebooks/               Preserved unrelated downloaded notebooks
deployment/                         Audit, hash manifest, deployment guide, test report
tests/                              Game, UI, input validation and preservation tests
Dockerfile                          Python 3.12 CPU deployment
```

Original Python files and model assets remain untouched at the root; organized copies are also retained. Downloaded original notebooks are byte-for-byte preserved in the notebook/experiment archive, with hashes in `deployment/original-files.json`. The Roboflow training notebook's original file is explicitly gitignored because it contains a hard-coded credential. Its sanitized publishing copy uses an environment variable instead. Revoke and replace that credential before using it again. The custom model is approximately 6.5 MB and is included directly; `yolov8n.pt` is never substituted if `best.pt` fails. No training takes place. Notebook and model metadata retain their upstream provenance; no new blanket license is asserted for the original material.

## Local setup

Use Python 3.12 for the full application. The existing Python 3.9 environment is retained for offline UI tests, but is not the target for the complete ML dependency set.

```bash
python3.12 -m venv .venv-lab
source .venv-lab/bin/activate
python -m pip install -r requirements.txt
streamlit run app/main.py
```

On Apple Silicon, pip should select native macOS wheels. Install the native `flac` executable if it is not already on PATH; the audited Mac already has it. Docker provides FLAC and OpenCV's system dependencies. PyTorch and rembg's default U²-Net weights are substantial downloads. The existing custom YOLO model is reused without downloading or training a replacement.

Dependency pins are proposed deployment inputs, not a verified lockfile: package resolution was blocked in the sandbox. Validate them on the target host before release. `requirements-dev.txt` adds no development packages because tests use standard-library unittest and Streamlit's included AppTest.

## Navigation

Run one process, `streamlit run app/main.py`. Home cards and the sidebar use the same registered pages. Once running locally on the default port, the routes are:

| Page | Local address (requires running server) | Deployment path |
| --- | --- | --- |
| Home | `http://localhost:8501/` | `/` |
| Background Removal | `http://localhost:8501/background-removal` | `/background-removal` |
| Text-to-Speech | `http://localhost:8501/text-to-speech` | `/text-to-speech` |
| Speech-to-Text | `http://localhost:8501/speech-to-text` | `/speech-to-text` |
| Rock-Paper-Scissors | `http://localhost:8501/rock-paper-scissors` | `/rock-paper-scissors` |

These are configured routes, not claims that a local or public server is running. Public links will be added only after deployment and verification. No screenshots are included because a browser preview could not run in this sandbox.

## Tests

```bash
python -m unittest discover -s tests -v
python deployment/smoke_processing.py
# With all ML dependencies installed; may download the default rembg weights:
python deployment/smoke_processing.py --ml
```

The smoke script makes real gTTS and Google recognition calls. Its transcription fixture uses macOS's installed `say` command; on Linux, use a known spoken PCM WAV with `app.components.services.transcribe` instead. YOLO smoke inference on the sample image validates execution only; gesture accuracy needs representative labeled hand photos. Mocked UI tests are reported separately from actual service tests.

## Deployment and limitations

See [deployment instructions and platform comparison](deployment/README.md). The Docker image serves Streamlit on port 7860 as a non-root user and preloads the unchanged default rembg weights during build. Models are lazy-loaded in the application and cached per process; CPU inference is serialized to control concurrency. Results remain per-session, without a global user-output cache.

- Images are limited to 10 MB and 12 megapixels; WAV input to 10 MB and two minutes; speech input to 5,000 characters. These are new web resource limits, not changes to the original algorithms.
- TTS text and STT audio go to Google's services. Service availability/rate limits can interrupt processing. No API key is required by the existing implementations.
- Browser microphone/camera capture requires permissions and a secure context (HTTPS or localhost). When embedding a hosted app, open its direct app origin if browser permissions are blocked by the iframe.
- No live video loop is used: each camera snapshot is deliberately detected and confirmed.
- Free/shared hosting can sleep or exhaust resources. A stable address is not an uptime guarantee.
- No speech-to-text Colab notebook was among the five downloads. Other Colab/Drive notebooks have not been searched because account access is unavailable.
- The background-removal source's exact historical rembg version is unknown. Its default algorithm is retained; bit-for-bit equivalence to an unavailable historical environment cannot be asserted.
