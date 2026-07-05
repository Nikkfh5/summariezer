import json
import unittest

from summariezer.delivery import (
    build_telegram_send_requests,
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
