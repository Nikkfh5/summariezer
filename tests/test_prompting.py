import unittest

from summariezer.models import DigestProfile, Message, MessageChunk
from summariezer.prompting import build_digest_prompt, build_merge_prompt


class PromptingTests(unittest.TestCase):
    def test_includes_profile_priorities_and_source_links(self) -> None:
        profile = DigestProfile(
            name="hft",
            audience="User tracks HFT first, crypto second.",
            priorities=[
                "HFT, market microstructure, latency, execution",
                "Crypto only when it changes trading edge",
            ],
            low_priority=["Price chatter", "Memes", "Unverifiable hype"],
            output_sections=[
                "Main HFT signals",
                "Claims to verify",
                "Noise and weak claims",
            ],
            language="ru",
        )
        chunk = MessageChunk(
            index=1,
            messages=[
                Message(
                    source="chat",
                    message_id="42",
                    date="2026-07-05T10:00:00+03:00",
                    author="bob",
                    text="Matching engine latency changed after venue update.",
                    url="https://t.me/c/123/42",
                )
            ],
            estimated_tokens=32,
            over_budget=False,
        )

        prompt = build_digest_prompt(
            profile=profile,
            chunk=chunk,
            window_label="2026-07-02..2026-07-05",
        )

        self.assertIn("HFT, market microstructure", prompt)
        self.assertIn("Crypto only when it changes trading edge", prompt)
        self.assertIn("Do not treat noisy consensus as signal", prompt)
        self.assertIn("https://t.me/c/123/42", prompt)
        self.assertIn("message_id: 42", prompt)
        self.assertIn("Claims to verify", prompt)

    def test_merge_prompt_keeps_final_digest_source_requirement(self) -> None:
        profile = DigestProfile(
            name="hft",
            audience="User tracks HFT first, crypto second.",
            priorities=["HFT", "Crypto only with execution relevance"],
            low_priority=["Price chatter"],
            output_sections=["Main HFT signals", "Claims to verify"],
            language="ru",
        )

        prompt = build_merge_prompt(
            profile=profile,
            summaries=["Chunk 1: venue latency claim [message_id: 42]"],
            window_label="2026-07-02..2026-07-05",
        )

        self.assertIn("final digest", prompt)
        self.assertIn("Keep source message ids and links", prompt)
        self.assertIn("Chunk 1: venue latency claim", prompt)
