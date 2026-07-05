from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable


TELEGRAM_MESSAGE_LIMIT = 3900


def split_telegram_message(text: str, limit: int = TELEGRAM_MESSAGE_LIMIT) -> list[str]:
    if limit <= 0:
        raise ValueError("limit must be positive")
    if not text:
        return [""]
    if len(text) <= limit:
        return [text]

    chunks: list[str] = []
    remaining = text
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break

        candidate = remaining[:limit]
        cut_at = max(candidate.rfind("\n\n"), candidate.rfind("\n"), candidate.rfind(" "))
        if cut_at <= 0:
            cut_at = limit
        chunks.append(remaining[:cut_at])
        remaining = remaining[cut_at:]

    return chunks


def build_telegram_send_requests(
    *,
    bot_token: str,
    chat_id: str,
    text: str,
    disable_web_page_preview: bool = True,
) -> list[urllib.request.Request]:
    requests: list[urllib.request.Request] = []
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    for chunk in split_telegram_message(text):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": disable_web_page_preview,
        }
        data = json.dumps(payload).encode("utf-8")
        requests.append(
            urllib.request.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
        )
    return requests


def send_telegram_digest(
    *,
    bot_token: str,
    chat_id: str,
    text: str,
    timeout: float = 30,
    opener: Callable[..., object] = urllib.request.urlopen,
) -> int:
    sent = 0
    for request in build_telegram_send_requests(
        bot_token=bot_token,
        chat_id=chat_id,
        text=text,
    ):
        response = opener(request, timeout=timeout)
        read = getattr(response, "read", None)
        if callable(read):
            read()
        sent += 1
    return sent
