from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import Message


async def fetch_telegram_messages(
    *,
    session_path: Path,
    api_id: int,
    api_hash: str,
    chat: str,
    source: str,
    start: datetime,
    end: datetime,
) -> list[Message]:
    try:
        from telethon import TelegramClient
    except ImportError as exc:
        raise RuntimeError(
            "Telegram ingestion requires the optional dependency: "
            "python3 -m pip install 'summariezer[telegram]'"
        ) from exc

    session_path.parent.mkdir(parents=True, exist_ok=True)
    messages: list[Message] = []
    async with TelegramClient(str(session_path), api_id, api_hash) as client:
        async for item in client.iter_messages(chat, offset_date=end, reverse=True):
            if item.date is None:
                continue
            if item.date < start:
                continue
            if item.date >= end:
                break
            text = item.message or ""
            if not text.strip():
                continue
            messages.append(
                Message(
                    source=source,
                    message_id=str(item.id),
                    date=item.date.isoformat(),
                    author=str(getattr(item.sender, "username", "") or item.sender_id or ""),
                    text=text,
                    url=_telegram_url(chat, item.id),
                    reply_to=str(item.reply_to_msg_id) if item.reply_to_msg_id else None,
                )
            )
    return messages


def _telegram_url(chat: str, message_id: int) -> str | None:
    if chat.startswith("https://t.me/"):
        return f"{chat.rstrip('/')}/{message_id}"
    if chat.startswith("@"):
        return f"https://t.me/{chat[1:]}/{message_id}"
    return None
