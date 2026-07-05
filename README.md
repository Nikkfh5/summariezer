# Summariezer

Universal chat digest tooling. The first target is a noisy Telegram chat where
HFT and market microstructure matter more than generic crypto chatter, but the
core is profile-based and can be reused for other chats.

## Current shape

- SQLite message store.
- Message chunking by approximate token budget.
- Profile-driven prompt generation.
- Codex CLI runner using `codex exec -` with prompt content on stdin.
- Optional Telegram ingestion through a reader account.
- JSONL ingestion for local testing and non-Telegram sources.

## Privacy model

Use a separate Telegram reader account. Treat its session file as sensitive:

- keep sessions under `secrets/`;
- do not sync or commit `secrets/`, `data/`, or `runs/`;
- pass `TELEGRAM_API_HASH` through an environment variable, not a CLI argument;
- use `--discard-prompts` after prompt-quality tuning if you do not want raw
  transcript prompts left in `runs/`.

Codex still receives the chat text. Passing prompts through files/stdin avoids
shell history and process-argument leakage; it does not make the LLM call local.

## Setup

```bash
cd /Users/nixito/hse/summariezer
python3 -m unittest discover -s tests
python3 -m summariezer.cli --config configs/example.toml init-db
```

## What to fill in

Minimal fields for the first real Telegram run:

- `--source`: local source name, for example `hft_chat`.
- `--chat`: Telegram chat username/link/id, for example `@some_chat`.
- `--session`: local reader-account session path, usually `secrets/tg-reader`.
- `--api-id`: numeric API id from `https://my.telegram.org/apps`.
- `TELEGRAM_API_HASH`: API hash from the same page, exported as an environment variable.
- `--profile`: `hft` for the HFT-first digest, or `generic` for general chats.
- `--start` / `--end`: digest window.

Output channel:

- default: local Markdown files under `runs/.../digest.md`;
- optional: Telegram DM/channel via a separate BotFather bot using
  `TELEGRAM_BOT_TOKEN` and `TELEGRAM_DELIVERY_CHAT_ID`.

For Telegram ingestion and optional delivery:

```bash
python3 -m pip install -e '.[telegram]'
export TELEGRAM_API_HASH='...'
export TELEGRAM_BOT_TOKEN='...'                 # optional delivery
export TELEGRAM_DELIVERY_CHAT_ID='...'          # optional delivery
```

## Ingest JSONL

Each JSONL line should contain at least `message_id`, `date`, and `text`.

```json
{"message_id":"1","date":"2026-07-05T10:00:00+03:00","author":"alice","text":"Venue latency changed.","url":"https://t.me/c/123/1"}
```

```bash
python3 -m summariezer.cli --config configs/example.toml ingest-jsonl \
  --source hft_chat \
  --file sample/messages.jsonl
```

## Ingest Telegram

```bash
python3 -m summariezer.cli --config configs/example.toml ingest-telegram \
  --source hft_chat \
  --chat @some_chat \
  --session secrets/tg-reader \
  --api-id 123456 \
  --api-hash-env TELEGRAM_API_HASH \
  --start 2026-07-02T00:00:00+03:00 \
  --end 2026-07-05T00:00:00+03:00
```

For private chats, message links may require Telegram's private `t.me/c/...`
format. Verify links on the first real run.

## Build a digest

Dry-run first to inspect the prompt files:

```bash
python3 -m summariezer.cli --config configs/example.toml digest \
  --source hft_chat \
  --profile hft \
  --start 2026-07-02T00:00:00+03:00 \
  --end 2026-07-05T00:00:00+03:00 \
  --dry-run
```

Run Codex:

```bash
python3 -m summariezer.cli --config configs/example.toml digest \
  --source hft_chat \
  --profile hft \
  --start 2026-07-02T00:00:00+03:00 \
  --end 2026-07-05T00:00:00+03:00
```

Run Codex and deliver the final digest to Telegram:

```bash
python3 -m summariezer.cli --config configs/example.toml digest \
  --source hft_chat \
  --profile hft \
  --start 2026-07-02T00:00:00+03:00 \
  --end 2026-07-05T00:00:00+03:00 \
  --deliver-telegram \
  --discard-prompts
```

Deliver an already generated digest:

```bash
python3 -m summariezer.cli --config configs/example.toml deliver-telegram \
  --file runs/<run-id>/digest.md
```

The runner uses:

```bash
codex --ask-for-approval never exec --cd <work_dir> --sandbox read-only \
  --ephemeral --output-last-message <summary-file> -
```

On this machine, `codex exec --help` does not show a documented temperature
flag. Keep any verified provider-specific overrides in `codex.extra_args`.
