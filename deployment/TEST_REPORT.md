# Deployment and test status

Updated 2026-10-18.

## Deployment observed

- The user opened `https://trainingsession.streamlit.app/` and navigated the deployed unified dashboard to Rock-Paper-Scissors.
- Streamlit Cloud logs show deployment from `codex/ai-training-lab-20261018-101637` with Python 3.12.15. The full dependency set, including `onnxruntime`, `rembg`, PyTorch, Ultralytics, and OpenCV, installed successfully.
- On the deployed still-image round, the existing model produced Scissors at 77% and Rock at 87% on one captured frame. The old UI correctly rejected the frame because it supported one player versus the computer only.
- The deployment currently uses the still-photo game UI. The live WebRTC implementation described below has not yet been pushed or deployed.

## Local OpenCV game update prepared locally

- Replaced the browser WebRTC capture with direct OpenCV laptop-camera capture. This avoids TURN services and browser streaming, and requires running Streamlit on the same computer as the camera.
- The camera view fills the wide page, and the annotated frame displays a center divider with Player 1/Player 2 labels. Scores appear above the live camera.
- Exactly two valid detections at or above 60% confidence are required. Detections are ordered left-to-right for Player 1 and Player 2. Pressing **Play Round** deliberately scores once; replay and reset are supported. The live frames themselves never award points.
- Removed the WebRTC dependency and all TURN secret handling. Streamlit Community Cloud cannot open a visitor's local camera using OpenCV; the hosted page will explain that OpenCV camera play must run locally.
- All 20 local offline tests pass, including all two-player outcomes, invalid/ambiguous gesture rejection, duplicate-round prevention, replay, reset, and page rendering. Python compilation passes when `PYTHONPYCACHEPREFIX` is directed to `/tmp`.
- Actual laptop camera access and live YOLO inference were not verified in this environment. On macOS, grant camera access to the terminal or IDE process running Streamlit. Browser testing of the hosted page cannot validate the local OpenCV camera.

## Other project checks and limits

- Background removal, gTTS, and Google SpeechRecognition have not been verified with real inputs on the deployed app. The Cloud log confirms installation, not successful image/audio processing. The speech services require outbound access to Google; rembg downloads model weights on first use.
- The Codex workspace has no `.git` checkout and its saved GitHub CLI token is invalid. A local app launch was attempted, but sandbox policy blocked binding to `127.0.0.1:8501`; run the startup script from the Mac Terminal. To publish the local camera update from a GitHub-authenticated Mac terminal, run:

  ```bash
  PUBLISH_BRANCH=codex/ai-training-lab-20261018-101637 ./deployment/push_to_github.sh
  ```

  The script updates the existing branch with a normal fast-forward push. Streamlit Cloud is configured to rebuild from that branch.
