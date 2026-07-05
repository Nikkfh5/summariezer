from __future__ import annotations

from collections.abc import Callable, Sequence

from .models import Message, MessageChunk
from .rendering import render_message
from .tokenization import estimate_tokens


def default_message_token_estimate(message: Message) -> int:
    return estimate_tokens(render_message(message))


def chunk_messages(
    messages: Sequence[Message],
    max_tokens: int,
    estimate_message_tokens: Callable[[Message], int] = default_message_token_estimate,
) -> list[MessageChunk]:
    if max_tokens <= 0:
        raise ValueError("max_tokens must be positive")

    chunks: list[MessageChunk] = []
    current_messages: list[Message] = []
    current_tokens = 0

    def flush(over_budget: bool = False) -> None:
        nonlocal current_messages, current_tokens
        if not current_messages:
            return
        chunks.append(
            MessageChunk(
                index=len(chunks) + 1,
                messages=list(current_messages),
                estimated_tokens=current_tokens,
                over_budget=over_budget or current_tokens > max_tokens,
            )
        )
        current_messages = []
        current_tokens = 0

    for message in messages:
        message_tokens = estimate_message_tokens(message)
        if message_tokens > max_tokens:
            flush()
            current_messages = [message]
            current_tokens = message_tokens
            flush(over_budget=True)
            continue

        if current_messages and current_tokens + message_tokens > max_tokens:
            flush()

        current_messages.append(message)
        current_tokens += message_tokens

    flush()
    return chunks
