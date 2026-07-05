from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TelegramDialogInfo:
    id: int | str
    title: str
    username: str | None
    kind: str


def list_telegram_dialogs(
    *,
    session_path: Path,
    api_id: int,
    api_hash: str,
    client_factory: type | None = None,
) -> list[TelegramDialogInfo]:
    return asyncio.run(
        _list_telegram_dialogs(
            session_path=session_path,
            api_id=api_id,
            api_hash=api_hash,
            client_factory=client_factory,
        )
    )


async def _list_telegram_dialogs(
    *,
    session_path: Path,
    api_id: int,
    api_hash: str,
    client_factory: type | None = None,
) -> list[TelegramDialogInfo]:
    if client_factory is None:
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise RuntimeError(
                "Telegram dialogs listing requires the optional dependency: "
                "python3 -m pip install 'summariezer[telegram]'"
            ) from exc
        client_factory = TelegramClient

    dialogs: list[TelegramDialogInfo] = []
    async with client_factory(str(session_path), api_id, api_hash) as client:
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            title = getattr(entity, "title", None) or getattr(dialog, "name", "") or ""
            username = getattr(entity, "username", None)
            dialogs.append(
                TelegramDialogInfo(
                    id=getattr(entity, "id", ""),
                    title=title,
                    username=username,
                    kind=_dialog_kind(dialog),
                )
            )
    return dialogs


def _dialog_kind(dialog: object) -> str:
    if getattr(dialog, "is_channel", False):
        return "channel"
    if getattr(dialog, "is_group", False):
        return "group"
    if getattr(dialog, "is_user", False):
        return "user"
    return "unknown"
