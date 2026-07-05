import asyncio
from datetime import datetime, timezone
import unittest

from summariezer.telegram_ingest import (
    _coerce_chat_ref,
    _telegram_url,
    fetch_telegram_messages,
)


class TelegramIngestTests(unittest.TestCase):
    def test_coerces_numeric_chat_ref_to_int_for_telethon(self) -> None:
        self.assertEqual(_coerce_chat_ref("-1002023542791"), -1002023542791)
        self.assertEqual(_coerce_chat_ref("2023542791"), 2023542791)

    def test_keeps_username_chat_ref_as_string(self) -> None:
        self.assertEqual(_coerce_chat_ref("@some_chat"), "@some_chat")

    def test_builds_private_channel_message_url_from_marked_id(self) -> None:
        self.assertEqual(
            _telegram_url("-1002023542791", 42),
            "https://t.me/c/2023542791/42",
        )

    def test_fetches_window_from_newest_to_oldest_and_returns_chronological(self) -> None:
        class FakeSender:
            username = "alice"

        class FakeMessage:
            sender = FakeSender()
            sender_id = 123
            reply_to_msg_id = None

            def __init__(self, message_id: int, date: str, text: str) -> None:
                self.id = message_id
                self.date = datetime.fromisoformat(date)
                self.message = text

        class FakeClient:
            seen_kwargs: dict[str, object] = {}

            def __init__(self, session: str, api_id: int, api_hash: str) -> None:
                pass

            async def __aenter__(self) -> "FakeClient":
                return self

            async def __aexit__(self, *args: object) -> None:
                return None

            async def iter_messages(self, chat, **kwargs):
                self.seen_kwargs.update(kwargs)
                yield FakeMessage(3, "2026-07-05T11:30:00+00:00", "third")
                yield FakeMessage(2, "2026-07-05T11:00:00+00:00", "second")
                yield FakeMessage(1, "2026-07-05T09:00:00+00:00", "too old")

        messages = asyncio.run(
            fetch_telegram_messages(
                session_path="session",
                api_id=123,
                api_hash="hash",
                chat="-1002023542791",
                source="chat",
                start=datetime(2026, 7, 5, 10, 0, tzinfo=timezone.utc),
                end=datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc),
                client_factory=FakeClient,
            )
        )

        self.assertEqual([message.message_id for message in messages], ["2", "3"])
        self.assertEqual(FakeClient.seen_kwargs["offset_date"], datetime(2026, 7, 5, 12, 0, tzinfo=timezone.utc))
        self.assertNotIn("reverse", FakeClient.seen_kwargs)
