from __future__ import annotations

from .models import Message


def render_message(message: Message) -> str:
    lines = [
        f"- source: {message.source}",
        f"  message_id: {message.message_id}",
        f"  date: {message.date}",
        f"  author: {message.author or 'unknown'}",
    ]
    if message.url:
        lines.append(f"  url: {message.url}")
    if message.reply_to:
        lines.append(f"  reply_to: {message.reply_to}")
    lines.append("  text: |-")
    for line in message.text.splitlines() or [""]:
        lines.append(f"    {line}")
    return "\n".join(lines)


def render_messages(messages: list[Message]) -> str:
    return "\n\n".join(render_message(message) for message in messages)
