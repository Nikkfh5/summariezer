from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Message:
    source: str
    message_id: str
    date: str
    author: str
    text: str
    url: str | None = None
    reply_to: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class MessageChunk:
    index: int
    messages: list[Message]
    estimated_tokens: int
    over_budget: bool


@dataclass(frozen=True)
class DigestProfile:
    name: str
    audience: str
    priorities: list[str]
    low_priority: list[str]
    output_sections: list[str]
    language: str = "en"


@dataclass(frozen=True)
class CodexSettings:
    executable: str = "codex"
    model: str | None = None
    work_dir: Path = Path(".")
    extra_args: list[str] = field(default_factory=list)
    ephemeral: bool = True
    sandbox: str = "read-only"
    ask_for_approval: str = "never"


@dataclass(frozen=True)
class AppConfig:
    database_path: Path
    runs_dir: Path
    max_chunk_tokens: int
    codex: CodexSettings
    profiles: dict[str, DigestProfile]
