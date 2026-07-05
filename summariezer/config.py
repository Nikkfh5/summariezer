from __future__ import annotations

import tomllib
from pathlib import Path

from .models import AppConfig, CodexSettings, DigestProfile


def load_config(path: Path | str) -> AppConfig:
    config_path = Path(path)
    raw = tomllib.loads(config_path.read_text(encoding="utf-8"))
    base_dir = config_path.parent

    storage = raw.get("storage", {})
    digest = raw.get("digest", {})
    codex_raw = raw.get("codex", {})
    profiles_raw = raw.get("profiles", {})

    profiles = {
        name: DigestProfile(
            name=name,
            audience=str(profile.get("audience", "")),
            priorities=list(profile.get("priorities", [])),
            low_priority=list(profile.get("low_priority", [])),
            output_sections=list(profile.get("output_sections", [])),
            language=str(profile.get("language", "en")),
        )
        for name, profile in profiles_raw.items()
    }

    if not profiles:
        raise ValueError("config must define at least one [profiles.<name>] section")

    return AppConfig(
        database_path=_resolve_path(base_dir, storage.get("database_path", "data/messages.sqlite3")),
        runs_dir=_resolve_path(base_dir, storage.get("runs_dir", "runs")),
        max_chunk_tokens=int(digest.get("max_chunk_tokens", 50_000)),
        codex=CodexSettings(
            executable=str(codex_raw.get("executable", "codex")),
            model=codex_raw.get("model"),
            work_dir=_resolve_path(base_dir, codex_raw.get("work_dir", ".")),
            extra_args=list(codex_raw.get("extra_args", [])),
            ephemeral=bool(codex_raw.get("ephemeral", True)),
            sandbox=str(codex_raw.get("sandbox", "read-only")),
            ask_for_approval=str(codex_raw.get("ask_for_approval", "never")),
        ),
        profiles=profiles,
    )


def _resolve_path(base_dir: Path, value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return (base_dir / path).resolve()
