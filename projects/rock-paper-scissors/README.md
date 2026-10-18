# Rock-Paper-Scissors

Streamlit game using the existing `best.pt` model and a live OpenCV camera. For live play, run the app on the same laptop as the camera. The original desktop OpenCV implementation remains in `rock_paper_scissor.py`.

```bash
cd projects/rock-paper-scissors
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8604
```

Allow browser camera access. Player 1 stands on the left and Player 2 on the right of the center divider. The existing `best.pt` is unchanged; live inference uses a 768-pixel image size and selects the strongest confident detection in each half. Both gestures must reach 25% confidence before **Play Round** is enabled. Play Again starts a fresh round; Reset Score clears all totals.
