#!/usr/bin/env bash
# Launch each independent Streamlit app and its own ngrok HTTP endpoint.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP="${1:-all}"
PORTS=(8601 8602 8603 8604)
NAMES=(background-removal text-to-speech speech-to-text rock-paper-scissors)
ENTRIES=(projects/background-removal/streamlit_app.py projects/text-to-speech/tts_maker.py projects/speech-to-text/stt_maker.py projects/rock-paper-scissors/streamlit_app.py)
PROJECT_DIRS=(projects/background-removal projects/text-to-speech projects/speech-to-text projects/rock-paper-scissors)
LOG_DIR="${TMPDIR:-/tmp}/training-sessions-ngrok"
mkdir -p "$LOG_DIR"
OWNED_PIDS=()

cleanup() {
  for pid in "${OWNED_PIDS[@]}"; do kill "$pid" 2>/dev/null || true; done
}
trap cleanup INT TERM EXIT

if ! command -v ngrok >/dev/null 2>&1; then
  echo "ngrok is not installed or is not on PATH." >&2; exit 1
fi
if ! ngrok config check >/dev/null 2>&1; then
  echo "ngrok is not authenticated/configured. Run 'ngrok config add-authtoken' locally; do not share the token." >&2; exit 1
fi

selected=()
if [[ "$APP" == all ]]; then
  selected=(0 1 2 3)
else
  found=0
  for i in 0 1 2 3; do
    if [[ "$APP" == "${NAMES[$i]}" ]]; then selected=("$i"); found=1; fi
  done
  if [[ $found == 0 ]]; then echo "Usage: $0 [all|${NAMES[*]}]" >&2; exit 2; fi
fi

for i in "${selected[@]}"; do
  port="${PORTS[$i]}"
  entry="$ROOT/${ENTRIES[$i]}"
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Port $port is already occupied. Stop the existing listener, then retry; refusing to tunnel the wrong app." >&2
    exit 1
  else
    project_venv="$ROOT/${PROJECT_DIRS[$i]}/.venv/bin/streamlit"
    if [[ -x "$project_venv" ]]; then streamlit_cmd=("$project_venv")
    elif [[ -x "$ROOT/.venv/bin/streamlit" ]]; then streamlit_cmd=("$ROOT/.venv/bin/streamlit")
    else streamlit_cmd=(streamlit); fi
    if ! command -v "${streamlit_cmd[0]}" >/dev/null 2>&1; then
      echo "Streamlit is unavailable. Install the requirements for ${NAMES[$i]} first." >&2; exit 1
    fi
    "${streamlit_cmd[@]}" run "$entry" --server.address 127.0.0.1 --server.port "$port" --server.headless true >"$LOG_DIR/${NAMES[$i]}.streamlit.log" 2>&1 &
    OWNED_PIDS+=("$!")
    echo "Started ${NAMES[$i]} at http://127.0.0.1:$port/"
  fi
done

# Do not expose an app unless its server actually bound the expected port.
for attempt in {1..20}; do
  all_ready=1
  for i in "${selected[@]}"; do
    if ! lsof -nP -iTCP:"${PORTS[$i]}" -sTCP:LISTEN >/dev/null 2>&1; then all_ready=0; fi
  done
  [[ $all_ready == 1 ]] && break
  sleep 1
done
for i in "${selected[@]}"; do
  if ! lsof -nP -iTCP:"${PORTS[$i]}" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "${NAMES[$i]} failed to start; see $LOG_DIR/${NAMES[$i]}.streamlit.log" >&2
    tail -n 8 "$LOG_DIR/${NAMES[$i]}.streamlit.log" >&2
    exit 1
  fi
done

for i in "${selected[@]}"; do
  port="${PORTS[$i]}"
  log="$LOG_DIR/${NAMES[$i]}.ngrok.log"
  ngrok http "$port" --log=stdout --log-format=logfmt >"$log" 2>&1 &
  OWNED_PIDS+=("$!")
  echo "Requested ngrok endpoint for ${NAMES[$i]} (port $port)."
done

sleep 5
for i in "${selected[@]}"; do
  log="$LOG_DIR/${NAMES[$i]}.ngrok.log"
  url="$(sed -nE 's/.*url=(https:\/\/[^[:space:]]+).*/\1/p' "$log" | head -n 1)"
  if [[ -n "$url" ]]; then
    echo "${NAMES[$i]}: $url"
  else
    echo "${NAMES[$i]}: tunnel did not report a URL; see $log"
    tail -n 4 "$log"
  fi
done
if [[ "$APP" == all ]]; then
  echo "The ngrok Free plan allows at most three simultaneous online endpoints. If the fourth is rejected, use '$0 <app-name>' to expose one independent app at a time, or use a plan allowing four endpoints."
fi
echo "Press Ctrl-C to stop processes started by this script. Services that were already running are left alone."
wait
