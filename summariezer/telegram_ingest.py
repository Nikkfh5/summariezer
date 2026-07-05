from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .models import Message


async def fetch_telegram_messages(
    *,
    session_path: Path | str,
    api_id: int,
    api_hash: str,
    chat: str,
    source: str,
    start: datetime,
    end: datetime,
    client_factory: type | None = None,
) -> list[Message]:
    if client_factory is None:
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise RuntimeError(
                "Telegram ingestion requires the optional dependency: "
                "python3 -m pip install 'summariezer[telegram]'"
            ) from exc
        client_factory = TelegramClient

    session_path = Path(session_path)
    session_path.parent.mkdir(parents=True, exist_ok=True)
    messages: list[Message] = []
    async with client_factory(str(session_path), api_id, api_hash) as client:
        async for item in client.iter_messages(
            _coerce_chat_ref(chat),
            offset_date=end,
        ):
            if item.date is None:
                continue
            if item.date < start:
                break
            if item.date >= end:
                continue
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
    messages.reverse()
    return messages


def _telegram_url(chat: str, message_id: int) -> str | None:
    if chat.startswith("https://t.me/"):
        return f"{chat.rstrip('/')}/{message_id}"
    if chat.startswith("@"):
        return f"https://t.me/{chat[1:]}/{message_id}"
    if chat.startswith("-100") and chat[4:].isdigit():
        return f"https://t.me/c/{chat[4:]}/{message_id}"
    return None


def _coerce_chat_ref(chat: str) -> str | int:
    stripped = chat.strip()
    if stripped.startswith("-") and stripped[1:].isdigit():
        return int(stripped)
    if stripped.isdigit():
        return int(stripped)
    return chat
