# Deployment and publishing

## Preferred target: Hugging Face Docker Spaces

The app's architecture fits a single CPU Docker Space: Python 3.12, CPU PyTorch/YOLO, ONNX Runtime/rembg, OpenCV, FLAC, and a Streamlit server on port 7860. The custom model remains bundled with its original SHA-256. A cached default rembg session avoids loading weights for every request, and an inference lock prevents simultaneous heavy inference in one process. Memory and latency still need measurement on the actual host; architectural suitability is not a successful deployment test.

Current [Spaces documentation](https://huggingface.co/docs/hub/spaces-overview) states CPU Basic provides 2 vCPU, 16 GB RAM and 50 GB ephemeral disk with no hourly hardware charge, **but creating a Docker Space requires a paid account plan**. Check whether the owner already has a suitable plan. Do not subscribe or upgrade hardware without approval. Free hardware sleeps after inactivity; runtime files are ephemeral. Container startup and model initialization introduce cold starts.

[Docker Spaces](https://huggingface.co/docs/hub/spaces-sdks-docker) reads `sdk: docker` and `app_port: 7860` from the root README. The supplied Dockerfile creates UID 1000, installs Linux CPU wheels and FLAC, downloads the default U²-Net weights at build time, then copies only the app and custom model. HTTP/HTTPS speech-service access must be tested from the deployed container. No ports other than the app port need exposing.

```bash
docker build -t ai-training-lab .
docker run --rm -p 7860:7860 ai-training-lab
```

These commands are documentation, not completed operations. Local Docker was not running during implementation.

## Free alternative: Streamlit Community Cloud

[Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud) provides free Streamlit hosting connected to GitHub. Use the existing repository, `app/main.py`, Python 3.12, root `requirements.txt` and `packages.txt`. It supports the same four routes without rewriting the app. Shared resource ceilings, sleep behavior and combined rembg/PyTorch memory use must be checked on the target instance. Do not claim this fallback is suitable for sustained traffic before measuring actual memory and request latency. The Docker target gives greater control over CPU wheel installation and model preloading.

ngrok is no longer the intended deployment. It depends on a running local process and tunnel. Static site hosting cannot execute this application's Python models.

## Safe GitHub integration after access is restored

Destination: `https://github.com/ShuraShipai/training_session.git`. No other GitHub repository should be created.

1. Fetch/clone the existing remote into a clean writable checkout and inspect its default branch, history, notebooks and deployment files.
2. Branch from that remote history (suggested branch `codex/ai-training-lab`). Do not push an unrelated root history over it.
3. Compare this prepared tree against remote files. Preserve unrelated remote content and resolve any collisions explicitly; never use a destructive synchronization command.
4. Review notebooks for project relevance and embedded credentials before publishing. The exact YOLO source notebook is kept locally under an exact `.gitignore` rule because it contains a hard-coded API credential. Publish only its sanitized derivative. Revoke/rotate the exposed credential before using it again.
5. Transfer reviewed application/documentation files and model into the checkout, run tests and real processing checks, then create a normal commit. Check hashes against `original-files.json`.
6. Fetch again, reconcile any remote changes, then push the feature branch without force. The user's authorization covers this push, but remote history must be verified first.

No commit or push was possible in this session: `.git` creation was denied, GitHub DNS failed, and CLI authentication reported invalid credentials. Connector authorization was offered and remains unconfirmed.

When run from the source folder on a machine with working GitHub CLI authentication and network access, `./deployment/push_to_github.sh` clones the existing repository, creates a timestamped feature branch, preserves conflicting remote files under `backups/pre-ai-training-lab/`, merges `.gitignore` rules, commits the prepared files, and pushes without force. It excludes the hard-coded-key original notebook. It does not change the repository's default branch. Review and merge the published branch after inspecting it on GitHub. The script intentionally stops if its own backup destination conflicts.

## Release verification

After authenticated hosting is available and the image builds:

- Confirm the returned canonical app URL and HTTP health endpoint.
- Open `/`, `/background-removal`, `/text-to-speech`, `/speech-to-text`, and `/rock-paper-scissors` directly; also navigate through all home cards and sidebar links.
- Remove a real image background and verify a PNG with transparency downloads.
- Generate nonempty speech, listen, and download the MP3.
- Record or upload a known spoken PCM WAV, verify the transcript, copy and download it.
- Test representative Rock/Paper/Scissors images and camera snapshots, low confidence, no hands, multiple hands, and service/model failures.
- Confirm a round once; reruns and duplicate clicks must not add points. Verify replay, reset and separate-user isolation.
- Inspect desktop and mobile layouts and HTTPS camera/microphone permissions; measure memory with both ML models loaded.
- Record actual deployment URLs and results in README and TEST_REPORT. Never add guessed hosting URLs.
