# Deployment and test status

Updated 2026-10-18.

## Deployment observed

- The user opened `https://trainingsession.streamlit.app/` and navigated the deployed unified dashboard to Rock-Paper-Scissors.
- Streamlit Cloud logs show deployment from `codex/ai-training-lab-20261018-101637` with Python 3.12.15. The full dependency set, including `onnxruntime`, `rembg`, PyTorch, Ultralytics, and OpenCV, installed successfully.
- On the deployed still-image round, the existing model produced Scissors at 77% and Rock at 87% on one captured frame. The old UI correctly rejected the frame because it supported one player versus the computer only.
- The deployment currently uses the still-photo game UI. The live WebRTC implementation described below has not yet been pushed or deployed.

## Live two-player update prepared locally

- Added continuous browser camera video with `streamlit-webrtc`; YOLO inference is throttled to roughly three frames per second and uses the unchanged `best.pt` and inference defaults.
- Exactly two valid detections at or above 60% confidence are required. Detections are ordered left-to-right for Player 1 and Player 2. Pressing **Play Round** deliberately scores once; replay and reset are supported. The live frames themselves never award points.
- Added `streamlit-webrtc==0.70.1` to root dependencies. HTTPS and browser camera permission are required. The configured public Google STUN service may not work on every restricted network; some networks require TURN.
- All 20 local offline tests pass, including all two-player outcomes, invalid/ambiguous gesture rejection, duplicate-round prevention, replay, reset, and UI rendering. Python compilation passes when `PYTHONPYCACHEPREFIX` is directed to `/tmp`.
- Live WebRTC/browser camera and two simultaneous hand inference have not yet been verified against the deployed update. After the code is pushed, test the camera permission, both live labels, each round result, replay, and reset at the public URL.

## Other project checks and limits

- Background removal, gTTS, and Google SpeechRecognition have not been verified with real inputs on the deployed app. The Cloud log confirms installation, not successful image/audio processing. The speech services require outbound access to Google; rembg downloads model weights on first use.
- The Codex workspace has no `.git` checkout and cannot push. To publish the local live-game update from the authenticated Mac terminal, run:

  ```bash
  PUBLISH_BRANCH=codex/ai-training-lab-20261018-101637 ./deployment/push_to_github.sh
  ```

  The script updates the existing branch with a normal fast-forward push. Streamlit Cloud is configured to rebuild from that branch.
