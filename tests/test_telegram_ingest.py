import unittest

from summariezer.telegram_ingest import _coerce_chat_ref, _telegram_url


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
