"""Normalize raw DB rubric strings into a stable, numbered block for the grader prompt."""

from __future__ import annotations

import re
from typing import List

_MAX_CRITERIA = 12


def _split_into_criteria(raw: str) -> List[str]:
    text = raw.strip()
    if not text:
        return []

    lower = text.lower()
    if "should mention" in lower:
        idx = lower.index("should mention")
        tail = text[idx + len("should mention") :].lstrip(":,- ").strip()
        text = tail or text

    parts = re.split(r"[\n;,]+", text)
    out: List[str] = []
    for p in parts:
        s = p.strip()
        if s:
            out.append(s)
    return out[:_MAX_CRITERIA]


def format_rubric_for_prompt(raw: str) -> str:
    """Turn a vague rubric line into numbered criteria the model must use."""
    criteria = _split_into_criteria(raw or "")
    if not criteria:
        return (
            "Criteria (grade only against these):\n"
            "1. (No rubric items supplied — judge alignment to the exam question only; "
            "do not invent extra requirements.)"
        )
    lines = ["Criteria (grade only against these; every bullet is mandatory to address for full credit):"]
    for i, c in enumerate(criteria, start=1):
        lines.append(f"{i}. {c}")
    return "\n".join(lines)
