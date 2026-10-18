# Deployment

## One Streamlit Community Cloud app

Deploy the unified AI Training Lab dashboard as one app from the existing GitHub repository:

- Repository: `ShuraShipai/training_session`
- Branch: select the latest branch containing the unified dashboard changes.
- Main file path: `app/main.py`
- Python: 3.12
- Dependencies: root `requirements.txt` and root `packages.txt`

The Home page and sidebar provide all four project pages. New `.py` files added under `app/pages/` are discovered automatically. Add any new Python dependency to the root `requirements.txt` and redeploy.

Community Cloud supports multiple app pages and gives the app approximately up to 2 CPU cores and 2.7 GB RAM. It sleeps after 12 hours without traffic. The existing YOLO checkpoint is 6.2 MB; local CPU inference on the provided image peaked around 375 MiB process RSS. This suggests single-model inference is within the memory ceiling, but the complete app needs an actual Cloud build and real processing checks. rembg downloads its default U²-Net weights on first use, and YOLO/PyTorch adds a substantial install. The two models are loaded lazily, so users incur their memory only when using the relevant project. These estimates do not replace Cloud measurements.

Text-to-Speech and Speech-to-Text send requests to Google's services and require outbound network access. The RPS game captures video in the browser with `getUserMedia` and sends small JPEG frames through the existing Streamlit component connection to the app server for inference. It does not use WebRTC, a TURN server, Cloudflare, or another camera relay. The browser must be allowed to use the camera, and inference runs on the Cloud CPU at a few frames per second. Free Cloud apps may hibernate; a fixed URL is not an uptime guarantee.

To publish later fixes to the already deployed dashboard branch, run this from the project directory on the Mac terminal that has GitHub CLI authorization:

```bash
PUBLISH_BRANCH=codex/ai-training-lab-20261018-101637 ./deployment/push_to_github.sh
```

The script checks out that existing remote branch and makes a normal fast-forward push (no force push). Streamlit Community Cloud should then rebuild the app from its watched branch.

## ngrok local alternative

The existing launcher starts the four independent project apps on ports 8601–8604:

```bash
./deployment/start_four_apps.sh
```

For the unified dashboard, run it separately and tunnel its port:

```bash
streamlit run app/main.py --server.port 8501
ngrok http 8501
```

ngrok Free permits up to three online endpoints. Its public URLs only work while the Mac, app, and tunnel remain running.

## Publication status

The user verified the app at [trainingsession.streamlit.app](https://trainingsession.streamlit.app/) and published branch `codex/ai-training-lab-20261018-101637`. The browser-camera component update is being prepared; it is not live until the updated branch is pushed and Cloud rebuilds it.
