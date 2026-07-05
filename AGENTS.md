# Summariezer Guidance

This project builds chat digests from sensitive message streams.

- Do not commit raw chat exports, Telegram sessions, API hashes, `.env`, `data/`,
  `runs/`, or `secrets/`.
- Prefer stdlib-first Python. Keep Telegram as an optional dependency.
- Use `python3 -m unittest discover -s tests` for the fast test suite.
- Codex CLI prompts should be passed through stdin or local prompt files, never
  shell arguments.
- Keep digest profiles generic. HFT is a profile, not a hard-coded product
  assumption.
- Preserve source `message_id` and URLs in every non-trivial digest claim.
