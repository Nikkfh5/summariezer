from __future__ import annotations

from math import ceil


def estimate_tokens(text: str) -> int:
    """Fast conservative-ish estimate without adding tokenizer dependencies."""
    if not text:
        return 0
    return max(1, ceil(len(text) / 4))
