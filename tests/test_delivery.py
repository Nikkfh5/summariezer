import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from summariezer.delivery import (
    build_telegram_get_updates_request,
    build_telegram_send_requests,
    send_telegram_user_digest,
    split_telegram_message,
)


class DeliveryTests(unittest.TestCase):
    def test_splits_long_telegram_messages_under_limit(self) -> None:
        text = "alpha\n\n" + ("x" * 80) + "\n\nomega"

        chunks = split_telegram_message(text, limit=50)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(len(chunk) <= 50 for chunk in chunks))
        self.assertEqual("".join(chunks).replace("\n\n", ""), text.replace("\n\n", ""))

    def test_builds_plain_text_telegram_send_requests(self) -> None:
        requests = build_telegram_send_requests(
            bot_token="123:secret",
            chat_id="456",
            text="digest",
        )

        self.assertEqual(len(requests), 1)
        request = requests[0]
        self.assertEqual(request.full_url, "https://api.telegram.org/bot123:secret/sendMessage")
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["chat_id"], "456")
        self.assertEqual(payload["text"], "digest")
        self.assertTrue(payload["disable_web_page_preview"])

    def test_builds_get_updates_request(self) -> None:
        request = build_telegram_get_updates_request(bot_token="123:secret")

        self.assertEqual(request.full_url, "https://api.telegram.org/bot123:secret/getUpdates")
        self.assertEqual(request.get_method(), "GET")

    def test_sends_digest_through_telegram_user_session(self) -> None:
        class FakeClient:
            sent: list[tuple[str, str, bool]] = []

            def __init__(self, session: str, api_id: int, api_hash: str) -> None:
                self.session = session
                self.api_id = api_id
                self.api_hash = api_hash

            async def __aenter__(self) -> "FakeClient":
                return self

            async def __aexit__(self, *args: object) -> None:
                return None

            async def send_message(
                self,
                peer: str,
                message: str,
                link_preview: bool,
            ) -> None:
                self.sent.append((peer, message, link_preview))

        with TemporaryDirectory() as tmp_dir:
            sent = send_telegram_user_digest(
                session_path=Path(tmp_dir) / "reader",
                api_id=123,
                api_hash="hash",
                peer="@main_account",
                text="digest",
                client_factory=FakeClient,
            )

        self.assertEqual(sent, 1)
        self.assertEqual(FakeClient.sent, [("@main_account", "digest", False)])
