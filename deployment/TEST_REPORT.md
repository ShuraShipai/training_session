# Deployment and test status

Updated 2026-10-18.

## Streamlit app

- The hosted app is at [trainingsession.streamlit.app](https://trainingsession.streamlit.app/), deployed from branch `codex/ai-training-lab-20261018-101637`.
- The deployed build log reports Python 3.12.15 and successful installation of root requirements. The app runs as a single Streamlit site with four pages.
- The original `best.pt` checkpoint remains unchanged and has detected gestures in the user's camera screenshots.

## Rock-Paper-Scissors recognition fix prepared locally

- The RPS page uses browser camera capture and sends frames through the existing Streamlit connection. It does not use WebRTC, TURN, Cloudflare, or another camera relay.
- A previous screenshot run found that at 640×360 YOLO missed the left player's hand; at full browser frame size and `imgsz=768`, it detected Rock at 82% and Scissors at 41%. The existing 60% game threshold correctly rejects that uncertain pair, so it cannot score until both gestures meet the unchanged requirement.
- Live capture preserves up to 1280×720 and uses the existing checkpoint at `imgsz=768`. The two-player scorer requires one confident, unambiguous gesture in each half. It does not retrain or replace the model.
- The browser must allow camera access. These recognition changes are local and need a Streamlit rebuild before they are available at the hosted URL.

## Checks

- 21 local offline unit and Streamlit page tests pass.
- Python compilation and browser component JavaScript syntax checks pass.
- Real screenshot inference produced one qualifying result per lane with the revised settings. Camera permissions and the rebuilt public page still need verification after publishing.
- TTS/STT use Google's services; background removal downloads model weights on first use.

## Automatic two-player rounds prepared locally

- The RPS page now samples browser frames at no more than one per second while the game is started. It waits for the Streamlit rerun to finish before another capture, and does not run YOLO while stopped.
- Gesture stability is timed at 0.8 seconds. After scoring, both zones must produce no model boxes for at least 1.5 seconds across three samples before the next round can begin. The model has no hands-down class, so this is a conservative gesture-zone-clear proxy rather than direct physical hand tracking.
- The original 60% game confidence threshold, cached `best.pt`, and 768 inference size are unchanged. Community Cloud CPU usage, hosted behavior, and browser camera access have not been measured for this update. The checkout lacks Streamlit/Pillow/YOLO dependencies, so only pure game-state tests and static syntax checks are available here.

## Publish the pending fix

This workspace has no `.git` checkout. From the Mac terminal authenticated to GitHub, run:

```bash
cd ~/Projects/training_sessions
PUBLISH_BRANCH=codex/ai-training-lab-20261018-101637 ./deployment/push_to_github.sh
```

The script fast-forwards the existing feature branch and does not modify the repository default branch. Streamlit Cloud should then rebuild from that watched branch.
