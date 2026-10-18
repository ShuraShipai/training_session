# AI Training Lab

## Live Applications — Try Them Online

Open the hosted app and choose a project from its navigation.

| Project | Live Demo | Source Code |
|---|---|---|
| Background Removal | [Try it](https://trainingsession.streamlit.app/) | [App page](app/pages/background_removal.py) |
| Text-to-Speech | [Try it](https://trainingsession.streamlit.app/) | [App page](app/pages/text_to_speech.py) |
| Speech-to-Text | [Try it](https://trainingsession.streamlit.app/) | [App page](app/pages/speech_to_text.py) |
| Rock-Paper-Scissors | [Try it](https://trainingsession.streamlit.app/rock-paper-scissors) | [App page](app/pages/rock_paper_scissors.py) |

The four projects have separate pages and keep their existing processing engines. The Rock-Paper-Scissors page uses the original `best.pt` YOLO model for two players in front of one browser camera. Allow camera access, stand on opposite sides of the center line, and press **Play Round** to score once.

## Run locally

```bash
python3.12 -m venv .venv-lab
source .venv-lab/bin/activate
python -m pip install -r requirements.txt
streamlit run app/main.py
```

Camera frames are sent to the Streamlit app for YOLO inference through the app's existing connection. The camera implementation does not use a separate TURN relay or paid camera service. TTS and STT use Google's services; background removal may download rembg model weights on first use. YOLO/PyTorch dependencies are large, and Community Cloud has limited CPU and memory.

To add a project page, add a Python file under `app/pages/` and its required packages to `requirements.txt`. The home page and navigation discover pages automatically. See [deployment notes](deployment/README.md) and [test status](deployment/TEST_REPORT.md).
