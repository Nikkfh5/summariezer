from __future__ import annotations

import json
from pathlib import Path

from .models import Message


def load_jsonl_messages(path: Path | str, source: str) -> list[Message]:
    messages: list[Message] = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            line = line.strip()
            if not line:
                continue
            raw = json.loads(line)
            messages.append(
                Message(
                    source=str(raw.get("source", source)),
                    message_id=str(raw["message_id"]),
                    date=str(raw["date"]),
                    author=str(raw.get("author", "")),
                    text=str(raw.get("text", "")),
                    url=raw.get("url"),
                    reply_to=raw.get("reply_to"),
                    metadata={k: str(v) for k, v in raw.get("metadata", {}).items()},
                )
            )
    return messages
