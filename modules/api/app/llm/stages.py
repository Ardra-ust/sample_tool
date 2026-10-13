"""Stage parameters and output parsing for the LLM stages (BRD §17; owner file).

Parsing follows the owner file: take the text from the first "{" to the last "}" and parse it as JSON.
The stage 3 and stage 5 rules here are the IT-services relevance decisions (FR-012, FR-014, FR-048).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StageParams:
    batch_size: int
    temperature: float
    max_tokens: int | None  # None means no limit (stage 10)


STAGE_3: StageParams = StageParams(batch_size=6, temperature=0.0, max_tokens=150)
STAGE_5: StageParams = StageParams(batch_size=8, temperature=0.0, max_tokens=300)
STAGE_9: StageParams = StageParams(batch_size=8, temperature=0.0, max_tokens=800)
STAGE_10: StageParams = StageParams(batch_size=1, temperature=0.2, max_tokens=None)

# Stage 3 safety net: a kept title containing any of these is not restored (BR-014, title only).
NEVER_RESTORE_TITLE_WORDS: tuple[str, ...] = (
    "christmas", "festive", "new year", "buy", "discount", "deal", "offer", "gift", "sale",
)

# Stage 5 force-keep keywords (BRD FR-014, copied from the owner's list). Substring match on lowercased text.
FORCE_KEEP_KEYWORDS: tuple[str, ...] = (
    "acqui", "merger", "merge", "m&a", "buyout", "takeover", "divest", "spin-off", "spinoff", "spin off",
    "joint venture", " jv ", "partnership", "partner with", "alliance", "strategic investment", "invests",
    "investment", "funding", "raises", "raised", "series a", "series b", "series c", "seed round", "venture",
    "ipo", "stake", "valuation", "unicorn", "cloud", "azure", "aws", "gcp", "data platform", "data center",
    "datacenter", "modernization", "modernisation", "migration", "digital transformation", "genai",
    "generative ai", "llm", "ai agent", "agentic", "machine learning", "cybersecurity", "cyber security",
    "ransomware", "breach", "zero trust", "core banking", "ehr", "emr", "erp", "saas", "platform",
    "automation", "contract", "deal", "gcc", "outsourc", "managed services", "integration", "infrastructure",
    "chip", "semiconductor", "analytics", "api", "accenture", "infosys", "tcs", "cognizant", "wipro",
    "capgemini", "mphasis", "ltimindtree", "hcltech", "tech mahindra", "fractal", "ust",
)


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse the text from the first "{" to the last "}". Raises ValueError when there is none."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("no JSON object in model output")
    parsed = json.loads(text[start : end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("model output is not a JSON object")
    return parsed


def keep_indices_from(text: str) -> list[int]:
    """Return keep_indices from stage 3 or 5 output. Unparseable output gives an empty list."""
    try:
        raw = extract_json_object(text).get("keep_indices", [])
    except (ValueError, json.JSONDecodeError):
        return []
    if not isinstance(raw, list):
        return []
    return [i for i in raw if isinstance(i, int) and not isinstance(i, bool)]


def has_never_restore_word(title: str) -> bool:
    """True when a title contains a word that blocks restoration at stage 3."""
    lowered = title.lower()
    return any(word in lowered for word in NEVER_RESTORE_TITLE_WORDS)


def has_force_keep_keyword(title: str, summary: str) -> bool:
    """True when title plus summary contains a force-keep keyword (stage 5, FR-014)."""
    text = f"{title} {summary}".lower()
    return any(keyword in text for keyword in FORCE_KEEP_KEYWORDS)
