from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from summariezer.telegram_auth import login_telegram_user_session


class TelegramAuthTests(unittest.TestCase):
    def test_login_starts_client_with_session_credentials(self) -> None:
        class FakeClient:
            started: list[tuple[str, int, str]] = []

            def __init__(self, session: str, api_id: int, api_hash: str) -> None:
                self.session = session
                self.api_id = api_id
                self.api_hash = api_hash

            async def __aenter__(self) -> "FakeClient":
                return self

            async def __aexit__(self, *args: object) -> None:
                return None

            async def start(self) -> None:
                self.started.append((self.session, self.api_id, self.api_hash))

        with TemporaryDirectory() as tmp_dir:
            session_path = Path(tmp_dir) / "reader"
            login_telegram_user_session(
                session_path=session_path,
                api_id=123,
                api_hash="hash",
                client_factory=FakeClient,
            )

        self.assertEqual(FakeClient.started, [(str(session_path), 123, "hash")])
