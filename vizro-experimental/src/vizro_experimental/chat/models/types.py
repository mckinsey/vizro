"""Wire-format vs parsed chat message types and parsing helpers."""

from __future__ import annotations

import json
from typing import Any, Literal, TypeAlias, TypedDict

Role: TypeAlias = Literal["user", "assistant"]


class Message(TypedDict):
    """Parsed chat item passed to ``generate_response`` (decoded ``content_json``)."""

    role: Role
    content: Any


def _parse_store_messages(messages: list[dict[str, Any]]) -> list[Message]:
    """Decode store / SSE wire messages into ``role`` + ``content`` dicts (internal).

    Each wire item must include ``role`` and ``content_json`` (JSON string). The returned
    list is a shallow copy with new dicts; the input list is not mutated.

    Args:
        messages: Store-shaped history (``role``, ``content_json`` per item).

    Returns:
        Parsed messages suitable for ``generate_response``.

    Raises:
        ValueError: Missing keys, non-string ``content_json``, or invalid JSON.
    """
    parsed: list[Message] = []
    for i, msg in enumerate(messages):
        if "role" not in msg or "content_json" not in msg:
            missing = {"role", "content_json"} - set(msg)
            raise ValueError(f"Message {i}: missing required keys {sorted(missing)}")
        raw = msg["content_json"]
        if not isinstance(raw, str):
            raise ValueError(f"Message {i}: content_json must be str, got {type(raw).__name__}")
        try:
            content = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"Message {i}: invalid content_json: {e}") from e
        role = msg["role"]
        if role not in ("user", "assistant"):
            raise ValueError(f"Message {i}: role must be 'user' or 'assistant', got {role!r}")
        parsed.append({"role": role, "content": content})
    return parsed
