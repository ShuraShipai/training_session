# Deployment and test status

Updated 2026-10-18.

## Streamlit app

- The hosted app is at [trainingsession.streamlit.app](https://trainingsession.streamlit.app/), deployed from branch `codex/ai-training-lab-20261018-101637`.
- The deployed build log reports Python 3.12.15 and successful installation of root requirements. The app runs as a single Streamlit site with four pages.
- The original `best.pt` checkpoint remains unchanged and has detected gestures in the user's camera screenshots.

## Rock-Paper-Scissors recognition fix prepared locally

- The RPS page uses browser camera capture and sends frames through the existing Streamlit connection. It does not use WebRTC, TURN, Cloudflare, or another camera relay.
- I ran the original checkpoint against the user's actual camera screenshot. At 640×360, YOLO missed the left player's hand. At full browser frame size with `imgsz=768`, it detected Rock at 82% and Scissors at 41%. The previous 60% game threshold rejected the Scissors result.
- Live capture now preserves up to 1280×720, uses the existing checkpoint at `imgsz=768`, and accepts detections from 25% confidence. If YOLO returns extra overlapping boxes, it selects the strongest qualifying box in each player's half. It does not retrain or replace the model.
- The browser must allow camera access. These recognition changes are local and need a Streamlit rebuild before they are available at the hosted URL.

## Checks

- 21 local offline unit and Streamlit page tests pass.
- Python compilation and browser component JavaScript syntax checks pass.
- Real screenshot inference produced one qualifying result per lane with the revised settings. Camera permissions and the rebuilt public page still need verification after publishing.
- TTS/STT use Google's services; background removal downloads model weights on first use.

## Publish the pending fix

This workspace has no `.git` checkout. From the Mac terminal authenticated to GitHub, run:

```bash
cd ~/Projects/training_sessions
PUBLISH_BRANCH=codex/ai-training-lab-20261018-101637 ./deployment/push_to_github.sh
```

The script fast-forwards the existing feature branch and does not modify the repository default branch. Streamlit Cloud should then rebuild from that watched branch.
