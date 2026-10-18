# Deployment and test status

Updated 2026-10-18.

## Streamlit app

- The hosted app is at [trainingsession.streamlit.app](https://trainingsession.streamlit.app/), deployed from branch `codex/ai-training-lab-20261018-101637`.
- The deployed build log reports Python 3.12.15 and successful installation of the root requirements. The app runs as a single Streamlit site with four pages.
- The existing `best.pt` model remains in place. Cloud installation and the prior browser screenshots confirm it ran YOLO inference on camera snapshots; the model reported gestures in those images.

## Live two-player camera change prepared locally

- The RPS page now uses browser `getUserMedia` and a bundled Streamlit Component. It displays a wide live camera view with a center divider and player labels; it sends reduced JPEG frames through the app's existing Streamlit connection for existing YOLO inference. It does not use WebRTC, TURN, Cloudflare, or an additional relay/API.
- Scores remain above the camera. Each side needs a confident gesture, and **Play Round** scores once; replay and reset remain available.
- The browser must grant camera permission to the site. The new component has not yet been verified on the hosted app; publish the code and wait for the Streamlit rebuild before testing it there.

## Checks

- 20 local offline unit and Streamlit page tests pass. Python module compilation and shell syntax checks were completed previously.
- The latest checks validate page rendering and game logic. They do not test browser camera permissions, live hosted frame transport, or a Cloud rebuild.
- Earlier deployment checks showed gTTS/SpeechRecognition depend on outbound Google access; background removal downloads model weights on first use. These services require real network-enabled checks on the hosted app.

## Publish the pending update

This workspace has no `.git` checkout. From the Mac terminal authenticated to GitHub, run:

```bash
cd ~/Projects/training_sessions
PUBLISH_BRANCH=codex/ai-training-lab-20261018-101637 ./deployment/push_to_github.sh
```

The script fast-forwards the existing feature branch and does not modify the repository default branch. Streamlit Cloud should rebuild from that watched branch.
