# Sanitized notebook copies

`rock_paper_scissor_stone.ipynb` is derived from the intact local original. Its hard-coded Roboflow credential is replaced by `os.environ["ROBOFLOW_API_KEY"]` so that no API key is published. Before running it, create a replacement key after revoking the credential exposed in the original. The exact source notebook stays local and is gitignored; see `notebooks/original-colab-notebooks/`.
