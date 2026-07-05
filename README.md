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

For Telegram ingestion:

```bash
python3 -m pip install -e '.[telegram]'
export TELEGRAM_API_HASH='...'
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

The runner uses:

```bash
codex --ask-for-approval never exec --cd <work_dir> --sandbox read-only \
  --ephemeral --output-last-message <summary-file> -
```

On this machine, `codex exec --help` does not show a documented temperature
flag. Keep any verified provider-specific overrides in `codex.extra_args`.
