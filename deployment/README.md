# Deployment

## Streamlit Community Cloud

The four projects deploy as four independent Community Cloud apps from the existing GitHub repository. For each deployment, select the repository `ShuraShipai/training_session`, the verified branch, and one entry point:

| Project | Entrypoint | Dependencies |
|---|---|---|
| Background Removal | `projects/background-removal/streamlit_app.py` | `projects/background-removal/requirements.txt` |
| Text-to-Speech | `projects/text-to-speech/tts_maker.py` | `projects/text-to-speech/requirements.txt` |
| Speech-to-Text | `projects/speech-to-text/stt_maker.py` | `projects/speech-to-text/requirements.txt` |
| Rock-Paper-Scissors | `projects/rock-paper-scissors/streamlit_app.py` | `projects/rock-paper-scissors/requirements.txt` |

Community Cloud supports multiple entry points in one repository with a separate dependency file beside each app. It uses a shared root `.streamlit/config.toml` and root `packages.txt`. Select Python 3.12 in the app's Advanced settings for Background Removal; current rembg releases require Python 3.11+. Python 3.12 is also suitable for the other three. Avoid adding multiple dependency formats beside an entry point.

Cloud's published approximate limits are up to 2 CPU cores and 2.7 GB RAM, with apps sleeping after 12 hours without traffic. The original YOLO model is 6.2 MB. Local CPU inference loaded that model and peaked around 375 MiB process RSS on the supplied sample image, so the model appears likely to fit, but this is not a substitute for a Cloud build and runtime measurement. YOLO/PyTorch installation is substantially larger than the checkpoint and must be allowed to finish. rembg also downloads its default U²-Net weights on first inference. Keep the apps separate so each process has its own resource budget. Streamlit may still throttle or stop an app that exceeds its limits.

Background removal and YOLO inference must be tested on Cloud after deployment. gTTS and SpeechRecognition need outbound access to Google's services. Browser camera access requires HTTPS and the visitor's browser permission. Community Cloud apps may hibernate; their URLs remain fixed but visitors may need to wake them.

## ngrok alternative for local demos

ngrok remains configured locally and can expose the independent local apps. Install each app's dependencies, authenticate ngrok, then run:

```bash
./deployment/start_four_apps.sh
```

The script uses ports 8601–8604 and reports only URLs returned by ngrok. Its Free plan allows up to three online endpoints; expose any three concurrently or start one app at a time, unless the account supports four endpoints. ngrok URLs require the local app, tunnel, and Mac to stay running.

## Authorization and publication status

The public repository is [ShuraShipai/training_session](https://github.com/ShuraShipai/training_session). GitHub web access confirms the prepared branch `codex/ai-training-lab-20261018-093909` exists. In this workspace `gh auth status` reports that the saved `ShuraShipai` token is invalid, and `git ls-remote` fails with `Could not resolve host: github.com`. There is no local `.git` checkout. Community Cloud also requires an authorized GitHub connection. No new commit, push, app deployment, or live URL is claimed from this workspace.

After account access is restored, clone/fetch the existing repository, reconcile the current four-app files without force-pushing, run tests, push a normal commit, deploy each entry point, and test actual inputs and browser camera on each resulting public URL. Add only verified URLs to the README table.
