from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from summariezer.telegram_dialogs import list_telegram_dialogs


class TelegramDialogsTests(unittest.TestCase):
    def test_lists_dialogs_from_client(self) -> None:
        class Entity:
            def __init__(self) -> None:
                self.id = 123
                self.title = "Attached HFT chat"
                self.username = "attached_hft"

        class Dialog:
            def __init__(self) -> None:
                self.entity = Entity()
                self.name = "Attached HFT chat"
                self.is_channel = False
                self.is_group = True
                self.is_user = False

        class FakeClient:
            def __init__(self, session: str, api_id: int, api_hash: str) -> None:
                self.session = session
                self.api_id = api_id
                self.api_hash = api_hash

            async def __aenter__(self) -> "FakeClient":
                return self

            async def __aexit__(self, *args: object) -> None:
                return None

            async def iter_dialogs(self):
                yield Dialog()

        with TemporaryDirectory() as tmp_dir:
            dialogs = list_telegram_dialogs(
                session_path=Path(tmp_dir) / "reader",
                api_id=123,
                api_hash="hash",
                client_factory=FakeClient,
            )

        self.assertEqual(len(dialogs), 1)
        self.assertEqual(dialogs[0].id, 123)
        self.assertEqual(dialogs[0].title, "Attached HFT chat")
        self.assertEqual(dialogs[0].username, "attached_hft")
        self.assertEqual(dialogs[0].kind, "group")
