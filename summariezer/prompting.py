from __future__ import annotations

from .models import DigestProfile, MessageChunk
from .rendering import render_messages


def build_digest_prompt(
    profile: DigestProfile,
    chunk: MessageChunk,
    window_label: str,
) -> str:
    priorities = "\n".join(f"{idx}. {item}" for idx, item in enumerate(profile.priorities, 1))
    low_priority = "\n".join(f"- {item}" for item in profile.low_priority)
    sections = "\n".join(f"- {section}" for section in profile.output_sections)

    return f"""You are producing a digest of a noisy chat transcript.

Audience:
{profile.audience}

Language:
{profile.language}

Window:
{window_label}

Chunk:
{chunk.index}

Estimated input tokens:
{chunk.estimated_tokens}

Priority order:
{priorities}

Low-priority or noise candidates:
{low_priority}

Required output sections:
{sections}

Rules:
- Do not treat noisy consensus as signal.
- Prefer claims that can be checked, measured, backtested, or linked to concrete infrastructure changes.
- Separate facts, interpretations, rumors, and pure opinion.
- Every non-trivial item must include source message links or message ids.
- If the chunk is mostly noise, say that directly and keep the digest short.
- Preserve uncertainty. Do not invent missing context.

Messages:
{render_messages(chunk.messages)}
"""


def build_merge_prompt(
    profile: DigestProfile,
    summaries: list[str],
    window_label: str,
) -> str:
    priorities = "\n".join(f"{idx}. {item}" for idx, item in enumerate(profile.priorities, 1))
    sections = "\n".join(f"- {section}" for section in profile.output_sections)
    summary_blocks = "\n\n".join(
        f"## Chunk summary {idx}\n{summary}" for idx, summary in enumerate(summaries, 1)
    )

    return f"""You are merging chunk-level summaries into one final digest.

Audience:
{profile.audience}

Language:
{profile.language}

Window:
{window_label}

Priority order:
{priorities}

Required final digest sections:
{sections}

Merge rules:
- Produce one final digest, not a list of chunk summaries.
- Keep source message ids and links for every important claim.
- Deduplicate repeated topics across chunks.
- Prefer HFT/microstructure/execution/infra signals over generic market chatter when the profile says so.
- Keep uncertainty labels. Do not upgrade rumors into facts.
- Include a short "what to verify or calculate next" section when useful.

Chunk summaries:
{summary_blocks}
"""
