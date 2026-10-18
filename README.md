# AI Training Projects

## Live Applications — Try Them Online

No Streamlit Community Cloud demo has been deployed and verified yet. Live links will appear here after GitHub and Streamlit authorization, deployment, and browser testing are complete.

| Project | Live Demo | Source Code |
|---|---|---|
| Background Removal | Pending verification | [Project folder](projects/background-removal/) |
| Text-to-Speech | Pending verification | [Project folder](projects/text-to-speech/) |
| Speech-to-Text | Pending verification | [Project folder](projects/speech-to-text/) |
| Rock-Paper-Scissors | Pending verification | [Project folder](projects/rock-paper-scissors/) |

The projects are four independent Streamlit applications. Each has its own entry point, dependencies, and README. Original scripts and the custom `best.pt` model are preserved.

## Projects

- **Background Removal** — upload an image, remove the background with the existing rembg implementation, preview the transparent result, and download PNG.
- **Text-to-Speech** — generate, play, and download gTTS audio in English, Hindi, Kannada, or Tamil.
- **Speech-to-Text** — record in the browser or upload WAV, then transcribe using the existing SpeechRecognition Google engine and language options.
- **Rock-Paper-Scissors** — browser camera or image input, existing YOLO `best.pt`, computer move, winner, score, replay, and reset. One valid detection must be explicitly confirmed to score a round.

## Run locally

Install each project's requirements in its own virtual environment. Background Removal requires Python 3.11+ for current rembg; the other three support Python 3.9+.

```bash
cd projects/text-to-speech
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run tts_maker.py
```

Use the entry point and `requirements.txt` in each project's folder for the other apps. Background Removal downloads rembg's default model weights the first time it runs. Rock-Paper-Scissors loads the existing `best.pt`; it does not retrain or substitute another model. Speech generation and transcription require access to Google's services.

## Deployment status

The intended public target is Streamlit Community Cloud, with four separate app entries from this repository. Community Cloud supports multiple apps from one repository and resolves each app's dependencies from its entry point directory. Free apps may sleep after inactivity and have limited CPU and memory; the YOLO app must be verified against those limits before its demo link is published.

GitHub currently has the previously prepared branch `codex/ai-training-lab-20261018-093909`. The local workspace is not a Git checkout, and the saved GitHub CLI token is invalid, so current local changes have not been pushed. No public app URL is claimed. Deployment instructions and current checks are in [deployment/README.md](deployment/README.md) and [deployment/TEST_REPORT.md](deployment/TEST_REPORT.md).

ngrok remains available for local demonstrations. Run `./deployment/start_four_apps.sh` after installing each app's dependencies and authenticating ngrok. Its Free plan allows at most three simultaneous endpoints, so it cannot expose all four apps at once without a higher endpoint allowance.

For browser camera access, allow the browser to use the camera on the HTTPS app page. For local OpenCV camera access, grant the terminal or IDE permission under macOS **System Settings → Privacy & Security → Camera**.
