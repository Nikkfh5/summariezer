from __future__ import annotations

import argparse
import asyncio
import os
from datetime import datetime
from pathlib import Path

from .chunking import chunk_messages
from .codex_runner import CodexRunner
from .config import load_config
from .jsonl_ingest import load_jsonl_messages
from .prompting import build_digest_prompt
from .storage import MessageStore
from .telegram_ingest import fetch_telegram_messages


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="summariezer")
    parser.add_argument("--config", default="configs/example.toml")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("init-db")

    ingest_jsonl = subparsers.add_parser("ingest-jsonl")
    ingest_jsonl.add_argument("--source", required=True)
    ingest_jsonl.add_argument("--file", required=True)

    ingest_tg = subparsers.add_parser("ingest-telegram")
    ingest_tg.add_argument("--source", required=True)
    ingest_tg.add_argument("--chat", required=True)
    ingest_tg.add_argument("--session", required=True)
    ingest_tg.add_argument("--api-id", type=int, required=True)
    ingest_tg.add_argument("--api-hash-env", default="TELEGRAM_API_HASH")
    ingest_tg.add_argument("--start", required=True)
    ingest_tg.add_argument("--end", required=True)

    digest = subparsers.add_parser("digest")
    digest.add_argument("--source", required=True)
    digest.add_argument("--profile", required=True)
    digest.add_argument("--start", required=True)
    digest.add_argument("--end", required=True)
    digest.add_argument("--dry-run", action="store_true")
    digest.add_argument("--discard-prompts", action="store_true")

    args = parser.parse_args(argv)
    config = load_config(args.config)
    store = MessageStore(config.database_path)
    store.initialize()

    if args.command == "init-db":
        print(f"initialized {config.database_path}")
        return 0

    if args.command == "ingest-jsonl":
        messages = load_jsonl_messages(Path(args.file), args.source)
        count = store.upsert_messages(messages)
        print(f"upserted {count} messages into {config.database_path}")
        return 0

    if args.command == "ingest-telegram":
        api_hash = os.environ.get(args.api_hash_env)
        if not api_hash:
            print(f"missing Telegram API hash env var: {args.api_hash_env}")
            return 2
        messages = asyncio.run(
            fetch_telegram_messages(
                session_path=Path(args.session),
                api_id=args.api_id,
                api_hash=api_hash,
                chat=args.chat,
                source=args.source,
                start=datetime.fromisoformat(args.start),
                end=datetime.fromisoformat(args.end),
            )
        )
        count = store.upsert_messages(messages)
        print(f"upserted {count} telegram messages into {config.database_path}")
        return 0

    if args.command == "digest":
        profile = config.profiles[args.profile]
        messages = store.fetch_messages(args.source, args.start, args.end)
        chunks = chunk_messages(messages, config.max_chunk_tokens)
        run_dir = config.runs_dir / _run_slug(args.source, args.profile, args.start, args.end)
        run_dir.mkdir(parents=True, exist_ok=True)
        runner = CodexRunner(config.codex)
        summary_paths: list[Path] = []
        for chunk in chunks:
            prompt_path = run_dir / f"chunk_{chunk.index:03d}.prompt.md"
            output_path = run_dir / f"chunk_{chunk.index:03d}.summary.md"
            prompt_path.write_text(
                build_digest_prompt(
                    profile=profile,
                    chunk=chunk,
                    window_label=f"{args.start}..{args.end}",
                ),
                encoding="utf-8",
            )
            if args.dry_run:
                print(f"wrote {prompt_path}")
                continue
            result = runner.run(prompt_path, output_path)
            if result.returncode != 0:
                print(result.stderr)
                return result.returncode
            if args.discard_prompts:
                prompt_path.unlink(missing_ok=True)
            summary_paths.append(output_path)
            print(f"wrote {output_path}")
        if not chunks:
            print("no messages found for window")
            return 0
        if args.dry_run:
            return 0
        if len(summary_paths) == 1:
            final_path = run_dir / "digest.md"
            final_path.write_text(summary_paths[0].read_text(encoding="utf-8"), encoding="utf-8")
            print(f"wrote {final_path}")
            return 0

        from .prompting import build_merge_prompt

        merge_prompt_path = run_dir / "merge.prompt.md"
        merge_output_path = run_dir / "digest.md"
        merge_prompt_path.write_text(
            build_merge_prompt(
                profile=profile,
                summaries=[path.read_text(encoding="utf-8") for path in summary_paths],
                window_label=f"{args.start}..{args.end}",
            ),
            encoding="utf-8",
        )
        result = runner.run(merge_prompt_path, merge_output_path)
        if result.returncode != 0:
            print(result.stderr)
            return result.returncode
        if args.discard_prompts:
            merge_prompt_path.unlink(missing_ok=True)
        print(f"wrote {merge_output_path}")
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


def _run_slug(source: str, profile: str, start: str, end: str) -> str:
    raw = f"{source}_{profile}_{start}_{end}"
    return "".join(char if char.isalnum() or char in "._-" else "-" for char in raw)


if __name__ == "__main__":
    raise SystemExit(main())
