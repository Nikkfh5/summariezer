import unittest

from summariezer.models import Message
from summariezer.chunking import chunk_messages


def make_message(message_id: int, text: str) -> Message:
    return Message(
        source="chat",
        message_id=str(message_id),
        date="2026-07-05T10:00:00+03:00",
        author="alice",
        text=text,
        url=f"https://t.me/c/123/{message_id}",
    )


class ChunkingTests(unittest.TestCase):
    def test_preserves_order_and_budget(self) -> None:
        messages = [
            make_message(1, "4"),
            make_message(2, "4"),
            make_message(3, "6"),
            make_message(4, "1"),
        ]

        chunks = chunk_messages(
            messages,
            max_tokens=10,
            estimate_message_tokens=lambda message: int(message.text),
        )

        self.assertEqual(
            [[m.message_id for m in chunk.messages] for chunk in chunks],
            [["1", "2"], ["3", "4"]],
        )
        self.assertEqual([chunk.estimated_tokens for chunk in chunks], [8, 7])
        self.assertTrue(all(not chunk.over_budget for chunk in chunks))

    def test_keeps_oversized_message_as_own_chunk(self) -> None:
        messages = [make_message(1, "14"), make_message(2, "2")]

        chunks = chunk_messages(
            messages,
            max_tokens=10,
            estimate_message_tokens=lambda message: int(message.text),
        )

        self.assertEqual(
            [[m.message_id for m in chunk.messages] for chunk in chunks],
            [["1"], ["2"]],
        )
        self.assertEqual(chunks[0].estimated_tokens, 14)
        self.assertTrue(chunks[0].over_budget)
        self.assertFalse(chunks[1].over_budget)
