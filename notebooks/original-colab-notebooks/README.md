# Original Colab notebooks

Downloaded Colab notebooks have now been organized here. Original contents are preserved and their SHA-256 hashes are recorded in `deployment/original-files.json`.

User-reported filenames awaiting inspection:

- `paper_scissor_stone.ipynb` — Rock/Paper/Scissors Roboflow dataset and YOLO training. This original contains a hard-coded Roboflow API credential and is excluded from Git by `.gitignore`. Do not publish it. A sanitized publishing copy is under `notebooks/publishable/`; rotate the exposed key in Roboflow before any further use.
- `text_to_speech.ipynb` — TTS Streamlit exercise.
- `Untitled1.ipynb` — Background removal and TTS exercises in one original notebook.

The downloaded `groq.ipynb` and `webscrapping.ipynb` are preserved under `experiments/notebooks/`; they are outside the four requested projects. No speech-to-text notebook was found among the supplied downloads. No additional notebook search was possible inside private Colab/Drive. Do not import unrelated deepfake, oil-spill, satellite/fire, or other notebooks just because they appear in the same account. Colab's GitHub authorization does not grant this agent Google Drive access.
