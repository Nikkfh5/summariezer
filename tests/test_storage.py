from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from summariezer.models import Message
from summariezer.storage import MessageStore


class StorageTests(unittest.TestCase):
    def test_upserts_and_fetches_messages_in_time_order(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            store = MessageStore(Path(tmp_dir) / "messages.sqlite3")
            store.initialize()

            first = Message(
                source="chat",
                message_id="2",
                date="2026-07-05T12:00:00+03:00",
                author="alice",
                text="second",
                url="https://t.me/c/123/2",
            )
            duplicate = Message(
                source="chat",
                message_id="2",
                date="2026-07-05T12:00:00+03:00",
                author="alice",
                text="second updated",
                url="https://t.me/c/123/2",
            )
            earlier = Message(
                source="chat",
                message_id="1",
                date="2026-07-05T11:00:00+03:00",
                author="bob",
                text="first",
                url="https://t.me/c/123/1",
            )

            store.upsert_messages([first, duplicate, earlier])

            messages = store.fetch_messages(
                source="chat",
                start="2026-07-05T00:00:00+03:00",
                end="2026-07-06T00:00:00+03:00",
            )

            self.assertEqual([message.message_id for message in messages], ["1", "2"])
            self.assertEqual(messages[1].text, "second updated")
