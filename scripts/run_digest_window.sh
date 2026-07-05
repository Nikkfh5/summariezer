#!/usr/bin/env bash
set -euo pipefail

CONFIG="${SUMMARIEZER_CONFIG:-/opt/summariezer/app/configs/example.toml}"
SOURCE="${SUMMARIEZER_SOURCE:?SUMMARIEZER_SOURCE is required}"
CHAT="${SUMMARIEZER_CHAT:?SUMMARIEZER_CHAT is required}"
SESSION="${SUMMARIEZER_SESSION:-/opt/summariezer/secrets/tg-reader}"
PROFILE="${SUMMARIEZER_PROFILE:-hft}"
WINDOW_DAYS="${SUMMARIEZER_WINDOW_DAYS:-3}"
API_ID="${TELEGRAM_API_ID:?TELEGRAM_API_ID is required}"

read -r START END < <(python3 - "$WINDOW_DAYS" <<'PY'
from datetime import datetime, timedelta, timezone
import sys

days = int(sys.argv[1])
end = datetime.now(timezone.utc).replace(microsecond=0)
start = end - timedelta(days=days)
print(start.isoformat(), end.isoformat())
PY
)

python3 -m summariezer.cli --config "$CONFIG" ingest-telegram \
  --source "$SOURCE" \
  --chat "$CHAT" \
  --session "$SESSION" \
  --api-id "$API_ID" \
  --api-hash-env TELEGRAM_API_HASH \
  --start "$START" \
  --end "$END"

DELIVERY_ARGS=(--deliver-telegram)
if [[ -z "${TELEGRAM_BOT_TOKEN:-}" || -z "${TELEGRAM_DELIVERY_CHAT_ID:-}" ]]; then
  if [[ -n "${TELEGRAM_DELIVERY_PEER:-}" ]]; then
    DELIVERY_ARGS=(--deliver-telegram-user --telegram-session "$SESSION")
  else
    DELIVERY_ARGS=()
  fi
fi

python3 -m summariezer.cli --config "$CONFIG" digest \
  --source "$SOURCE" \
  --profile "$PROFILE" \
  --start "$START" \
  --end "$END" \
  --discard-prompts \
  "${DELIVERY_ARGS[@]}"
