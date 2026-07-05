from __future__ import annotations

import asyncio
from pathlib import Path


def login_telegram_user_session(
    *,
    session_path: Path,
    api_id: int,
    api_hash: str,
    client_factory: type | None = None,
) -> None:
    asyncio.run(
        _login_telegram_user_session(
            session_path=session_path,
            api_id=api_id,
            api_hash=api_hash,
            client_factory=client_factory,
        )
    )


async def _login_telegram_user_session(
    *,
    session_path: Path,
    api_id: int,
    api_hash: str,
    client_factory: type | None = None,
) -> None:
    if client_factory is None:
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise RuntimeError(
                "Telegram login requires the optional dependency: "
                "python3 -m pip install 'summariezer[telegram]'"
            ) from exc
        client_factory = TelegramClient

    session_path.parent.mkdir(parents=True, exist_ok=True)
    async with client_factory(str(session_path), api_id, api_hash) as client:
        await client.start()
