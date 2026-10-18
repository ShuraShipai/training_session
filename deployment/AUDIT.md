# Audit and preservation record

Rechecked 2026-10-18. The source workspace initially contained ten non-environment files and no Git repository, notebooks, deployment configuration, tests or dependency manifests.

| Original file | Preserved copy / role |
| --- | --- |
| `new.py` | `projects/background-removal/new.py`; raw-byte rembg processing, absolute local input path |
| `tts_maker.py` | `projects/text-to-speech/tts_maker.py`; existing Streamlit gTTS UI |
| `stt_maker.py` | `projects/speech-to-text/stt_maker.py`; existing Streamlit Google recognition UI |
| `rock_paper_scissor.py` | `projects/rock-paper-scissors/rock_paper_scissor.py`; BGR webcam -> YOLO -> plotted output |
| `best.pt` | `projects/rock-paper-scissors/best.pt`; custom Paper/Rock/Scissors detector |
| `Image.jpeg` | `assets/Image.jpeg`; sample input |
| `yolov8n.pt` | `experiments/yolov8n.pt`; unused general detector |
| `model_chat.py` | `experiments/model_chat.py`; unrelated Ollama experiment |
| `memory.py` | `experiments/memory.py`; unrelated Ollama experiment |
| `labeler.html` | `experiments/labeler.html`; unrelated satellite CSV tool |

No exact duplicates existed initially. All originals remain unchanged at root; organized copies were deliberately added rather than deleting/moving originals. The preservation manifest records SHA-256 values. All original Python files parse successfully.

The original `.venv` is Python 3.9.6 with Streamlit 1.50.0, gTTS 2.5.4, SpeechRecognition 3.17.0, Pillow 11.3.0 and NumPy 2.0.2. `pip check` passed. rembg, ONNX Runtime, OpenCV, Ultralytics, PyTorch and Ollama were absent. A separate Python 3.12 `.venv-lab` was created; package download failed, so no ML packages were installed. Existing `.venv` packages were not modified.

Static inspection of `best.pt` found labels Paper, Rock, Scissors, Ultralytics version 8.4.178, and Colab-style `/content/...` training paths. The referenced `rock-paper-scissors-14/data.yaml` and training dataset are absent. Model weights were not executed during the audit, changed, or retrained. The source's YOLO26 docstring conflicts with its YOLOv8 comment; the actual custom checkpoint is authoritative.

Original gaps: background-removal upload/download UI; browser-compatible gesture input; entire game state and scoring layer; unified routes; dependency manifests and deployment documentation. TTS previously displayed old audio after changed input or failed generation; the new wrapper binds output to its input/language/speed and clears failed attempts. Original scripts remain unchanged.

No prior deployment URLs were present in local source. The user subsequently identified Streamlit/ngrok as the prior approach. GitHub could not be inspected because of DNS/authentication failures. Google Drive access is unavailable.

## Notebook files added 2026-10-18

The user subsequently downloaded five notebooks. All five were inspected and organized. Three relevant originals (`paper_scissor_stone.ipynb`, `text_to_speech.ipynb`, `Untitled1.ipynb`) are in `notebooks/original-colab-notebooks/`. Two unrelated originals (`groq.ipynb`, `webscrapping.ipynb`) are in `experiments/notebooks/`. SHA-256 values were appended to the preservation manifest after moves and verified unchanged.

Content review: `Untitled1.ipynb` mixes rembg background removal and gTTS/Streamlit TTS; `text_to_speech.ipynb` covers a Streamlit gTTS app; `paper_scissor_stone.ipynb` contains Roboflow dataset access, YOLOv8n training instructions and inference. The Roboflow training notebook contains a literal API credential in a code cell. Its intact original remains local and is excluded by an exact `.gitignore` rule. A separate sanitized publishing copy reads `ROBOFLOW_API_KEY` from the environment. The credential should be revoked/rotated before use. `groq.ipynb` reads a key from Colab Secrets, with no literal credential in the downloaded file. `webscrapping.ipynb` is a web scraping exercise with a rembg code cell. No speech-to-text notebook was among supplied downloads. No other Drive/Colab files were searched.

No remote repository was read, committed, or changed; current GitHub CLI status remains invalid and `github.com` DNS resolution fails from this environment. No public deployment exists.
