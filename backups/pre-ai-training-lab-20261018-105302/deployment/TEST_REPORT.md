# Independent application validation report

Run date: 2026-10-18. No public URL is verified in this session.

## Passed

- `bash -n deployment/start_four_apps.sh` passes.
- Python compilation passes for the independent project scripts.
- 18 offline tests pass, including the existing UI/game tests and the independent game logic: all winner combinations, invalid/low-confidence detections, one score per round, stale round rejection, replay and reset.
- Streamlit AppTest rendered the independent TTS, STT and Rock-Paper-Scissors interfaces without app exceptions. The independent background app cannot import because `rembg` is absent.
- The existing `best.pt` loaded with the installed system Ultralytics/PyTorch environment, labels were Paper/Rock/Scissors, and prediction plus annotated-image generation completed on the provided `Image.jpeg`. It detected zero gestures; this sample contains no known hand gesture, so it does not validate gesture accuracy.
- Existing ngrok v3.39.11 is installed and `ngrok config check` reports a valid local configuration. The credential was not read or printed.
- ngrok plan was checked against its current pricing page: Free permits up to three online endpoints, fewer than the four simultaneous URLs requested.

## Real processing attempts and blockers

- **Background removal:** cannot run; `.venv` lacks `rembg` and `onnxruntime`. Current rembg requires Python 3.11+, whereas the reusable `.venv` is Python 3.9.6. Package downloads are blocked by the current network/DNS restrictions. No model weights were downloaded.
- **Text-to-speech:** a real gTTS request failed to connect (`gTTSError: Failed to connect`). No generated audio is claimed.
- **Speech-to-text:** a real non-silent WAV generated with macOS `say` was sent to the existing Google recognition engine; it failed DNS resolution (`RequestError: recognition connection failed ... nodename nor servname provided`). No transcription is claimed.
- **Rock-Paper-Scissors:** actual model loading/inference worked on the available sample, but no gesture was detected. No representative gesture image was present, and browser camera capture could not be tested from this sandbox. OpenCV access to the Mac camera was previously denied by macOS; allow the terminal/IDE host in System Settings → Privacy & Security → Camera.
- **Local servers/ngrok URLs:** the current environment blocks loopback HTTP inspection, so the existing ngrok inspector at `127.0.0.1:4040` could not be queried. Existing Streamlit listeners occupy ports 8501 and 8502; the new launcher uses 8601–8604 and refuses occupied ports. Starting listener/tunnels here is not a valid end-to-end check because the required background dependency is missing and this environment cannot test local HTTP/public requests. No ngrok URL is known or invented.
- **GitHub:** this workspace has no `.git` checkout. `gh auth status` reports the stored token for `ShuraShipai` is invalid. `git ls-remote https://github.com/ShuraShipai/training_session.git HEAD` fails exactly with `Could not resolve host: github.com`. No Git commit or push is claimed.

## Status

The independent entry points, requirements files, documentation, launcher and game logic are prepared. The game winner/score behavior passes offline tests and the original model was executed, but the end-to-end real-service checks and four live ngrok URLs remain blocked by missing dependencies, external DNS, ngrok's three-endpoint Free limit, and browser/camera access. Do not treat this report as deployment confirmation.

## Streamlit Community Cloud continuation check

- GitHub's public repository page is reachable read-only in the browser and shows the existing branch `codex/ai-training-lab-20261018-093909`; its current remote README still describes the earlier unified dashboard. No remote changes were made.
- The requested GitHub device-login flow was attempted after user authorization, but `gh auth login --hostname github.com --git-protocol https --web` failed immediately: `error connecting to github.com; check your internet connection or https://githubstatus.com`.
- Direct terminal access also still fails with `Could not resolve host: github.com`; this checkout has no `.git` directory. Therefore the current local independent-app changes cannot be safely fetched, reconciled, committed, or pushed here.
- Streamlit's official documentation supports multiple apps from one repository, with a separate dependency file beside each entry point. The four project directories use that layout. Community Cloud still needs an authenticated GitHub connection before app creation.
- Streamlit's documentation gives approximate limits up to 2 CPU cores and 2.7 GB RAM; it also says apps sleep after 12 hours without traffic. The existing YOLO model executed locally at approximately 375 MiB maximum process RSS on `Image.jpeg` (zero gesture detections). This suggests the isolated RPS process can fit, but does not verify Cloud build size, memory, or gesture accuracy.
- README now has the requested Live Applications table, but each demo cell says `Pending verification`; no unverified or guessed URLs were added. No Cloud app was deployed or browser-tested, and the README was not pushed.
