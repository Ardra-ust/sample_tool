"""Prompt loader. Templates are the owner's text, stored verbatim in app/prompts/ (FR-046).

Placeholders are replaced by exact string match. The text is never passed through str.format,
because the prompts contain literal braces (JSON examples).
"""

from __future__ import annotations

from pathlib import Path

PROMPTS_DIR: Path = Path(__file__).resolve().parents[1] / "prompts"


def load(name: str) -> str:
    """Return one template exactly as stored (UTF-8, no trailing newline added or removed)."""
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")


def render(template: str, **values: str) -> str:
    """Replace {name} placeholders with the given values, by exact match."""
    text = template
    for key, value in values.items():
        text = text.replace("{" + key + "}", value)
    return text
