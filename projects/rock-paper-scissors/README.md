# Rock-Paper-Scissors

Independent Streamlit game using the existing `best.pt` model. The original desktop OpenCV implementation remains in `rock_paper_scissor.py`.

```bash
cd projects/rock-paper-scissors
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8604
```

Use browser camera capture or upload a gesture image. A single Rock/Paper/Scissors detection at 60% confidence or higher must be explicitly confirmed. The computer chooses first; one confirmed round updates the score once. Play Again starts a new round; Reset Score clears all totals. The app loads this directory's original `best.pt`, without training or fallback model substitution.
