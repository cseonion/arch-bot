from __future__ import annotations


def split_message(text: str, limit: int = 1900) -> list[str]:
    """Split text into Discord-safe chunks, preferring line boundaries."""
    if limit < 1:
        raise ValueError("limit must be positive")
    if not text:
        return [""]

    chunks: list[str] = []
    remaining = text
    while len(remaining) > limit:
        split_at = remaining.rfind("\n", 0, limit + 1)
        if split_at <= 0:
            split_at = remaining.rfind(" ", 0, limit + 1)
        if split_at <= 0:
            split_at = limit
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    if remaining or not chunks:
        chunks.append(remaining)
    return chunks
