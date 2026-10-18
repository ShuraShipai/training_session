#!/usr/bin/env bash
# Clone the existing remote, publish this prepared tree on a new branch, and
# retain any replaced remote files as branch-local backups. Never force-push.
set -euo pipefail

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOSITORY="ShuraShipai/training_session"
STAMP="$(date +%Y%m%d-%H%M%S)"
BRANCH="${PUBLISH_BRANCH:-codex/ai-training-lab-${STAMP}}"
WORK_DIR="$(mktemp -d "${TMPDIR:-/tmp}/ai-training-lab-push.XXXXXX")"

cleanup() {
  if [[ "${KEEP_CHECKOUT:-0}" != "1" ]]; then rm -rf "$WORK_DIR"; fi
}
trap cleanup EXIT

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required. Install it, authenticate, then rerun." >&2
  exit 1
fi
gh auth status -h github.com >/dev/null
gh auth setup-git

echo "Cloning the existing repository and preserving its history..."
gh repo clone "$REPOSITORY" "$WORK_DIR/repo"
cd "$WORK_DIR/repo"
if [[ -n "${PUBLISH_BRANCH:-}" ]]; then
  git switch --track -c "$BRANCH" "origin/$BRANCH"
else
  git switch -c "$BRANCH"
fi

# Copy the original project sources as well as their organized copies. Never
# copy the original Roboflow notebook containing a hard-coded API credential.
export SOURCE_DIR WORK_DIR STAMP
python3 - <<'PY'
from pathlib import Path
import os, shutil

source = Path(os.environ["SOURCE_DIR"])
repo = Path(os.environ["WORK_DIR"]) / "repo"
allowed = [
    "app", "projects", "assets", "experiments", "deployment", "tests",
    "notebooks/original-colab-notebooks/README.md",
    "notebooks/original-colab-notebooks/Untitled1.ipynb",
    "notebooks/original-colab-notebooks/text_to_speech.ipynb",
    "notebooks/publishable", ".streamlit", "README.md", "PRODUCT.md",
    "DESIGN.md", ".dockerignore", "Dockerfile",
    "requirements.txt", "requirements-dev.txt", "packages.txt",
    # Original root exercises/assets remain preserved; local venvs are excluded.
    "new.py", "tts_maker.py", "stt_maker.py", "rock_paper_scissor.py",
    "Image.jpeg", "best.pt", "yolov8n.pt", "model_chat.py", "memory.py",
    "labeler.html",
]
excluded = {
    "notebooks/original-colab-notebooks/paper_scissor_stone.ipynb",
}
backup_root = repo / "backups" / f"pre-ai-training-lab-{os.environ.get('STAMP', 'snapshot')}"
conflicts = []
copied = 0

for relative in allowed:
    src = source / relative
    if not src.exists():
        continue
    paths = [src] if src.is_file() else sorted(p for p in src.rglob("*") if p.is_file())
    for file in paths:
        rel = file.relative_to(source).as_posix()
        if rel in excluded:
            continue
        if any(part in {".venv", ".venv-lab", "__pycache__", ".git"} for part in Path(rel).parts):
            continue
        target = repo / rel
        if target.is_file() and target.read_bytes() != file.read_bytes():
            backup = backup_root / rel
            if backup.exists() and backup.read_bytes() != target.read_bytes():
                conflicts.append(f"Both {rel} and its backup path already differ")
                continue
            backup.parent.mkdir(parents=True, exist_ok=True)
            if not backup.exists():
                shutil.copy2(target, backup)
                print(f"Preserved previous remote file: {backup.relative_to(repo).as_posix()}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        copied += 1

# Merge ignore rules rather than replacing the remote repository's rules.
src_ignore = source / ".gitignore"
dst_ignore = repo / ".gitignore"
if src_ignore.is_file():
    existing = dst_ignore.read_text().splitlines() if dst_ignore.exists() else []
    additions = [line for line in src_ignore.read_text().splitlines()
                 if line not in existing]
    if additions:
        with dst_ignore.open("a") as stream:
            if existing and existing[-1] != "":
                stream.write("\n")
            stream.write("\n".join(additions) + "\n")

if conflicts:
    print("Cannot safely preserve these pre-existing remote files:", *conflicts, sep="\n- ")
    raise SystemExit(2)
print(f"Prepared {copied} files; original credential-bearing YOLO notebook excluded.")
PY

git add -A
git diff --cached --check
if git diff --cached --quiet; then
  echo "No new changes to publish."
  exit 0
fi
echo "Reviewing the exact branch changes:"
git diff --cached --stat
git commit -m "Publish extensible AI Training Lab dashboard"
git push -u origin "$BRANCH"
echo "Published branch: https://github.com/${REPOSITORY}/tree/${BRANCH}"
echo "The existing default branch was not changed."
