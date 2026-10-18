# Rock-Paper-Scissors

Streamlit game using the existing `best.pt` model and a live OpenCV camera. For live play, run the app on the same laptop as the camera. The original desktop OpenCV implementation remains in `rock_paper_scissor.py`.

```bash
cd projects/rock-paper-scissors
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8604
```

Click **Start live camera** and allow camera access to Terminal (or the app running Streamlit) in macOS **System Settings → Privacy & Security → Camera**. Player 1 stands on the left and Player 2 on the right of the center divider. When both gestures are detected at 60% confidence or higher, click **Play Round** once. Play Again starts a fresh round; Reset Score clears all totals. The app loads the original `best.pt`, without training or fallback model substitution. Streamlit Cloud cannot access the visitor's laptop camera through OpenCV; run this page locally for camera play.
