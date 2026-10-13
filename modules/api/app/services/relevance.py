"""IT-services relevance: stage 3 title re-check and stage 5 relevance gate (FR-012, FR-014, FR-015, FR-048).

The model call is a parameter, so the code can run with a real client or a stub. Failures follow the owner file:
- Stage 3: any error, or output with no JSON object, restores nothing from that batch. Never-restore words in the
  TITLE block restoration (BR-014).
- Stage 5: any error keeps the whole batch. Output without keep_indices keeps only force-keep matches.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterator
from typing import Any

from app.llm.prompts import load, render
from app.llm.stages import (
    STAGE_3,
    STAGE_5,
    extract_json_object,
    has_force_keep_keyword,
    has_never_restore_word,
    keep_indices_from,
)

# call(system_message, user_message, temperature, max_tokens) -> model text
LlmCall = Callable[[str, str, float, int | None], str]


def chunks(items: list[Any], size: int) -> Iterator[list[Any]]:
    """Yield consecutive batches of at most size items."""
    for start in range(0, len(items), size):
        yield items[start : start + size]


def title_recheck(noise_articles: list[dict[str, Any]], call: LlmCall) -> list[dict[str, Any]]:
    """Stage 3. Returns the noise-filtered articles that the model restores (FR-012)."""
    system = load("a_title_recheck_system.txt")
    template = load("a_title_recheck_user.txt")
    restored: list[dict[str, Any]] = []
    for batch in chunks(noise_articles, STAGE_3.batch_size):
        titles = [article["title"] for article in batch]
        user = render(template, titles_json=json.dumps(titles, ensure_ascii=False))
        try:
            text = call(system, user, STAGE_3.temperature, STAGE_3.max_tokens)
            # Stage 3 failure is output with no JSON object (owner file), so keep_indices must be present.
            keep = extract_json_object(text).get("keep_indices")
            if not isinstance(keep, list):
                raise ValueError("keep_indices missing")
        except Exception:
            continue  # nothing in this batch is restored
        for index in keep:
            if not (isinstance(index, int) and 0 <= index < len(batch)):
                continue  # ignore indices outside the batch
            article = batch[index]
            if has_never_restore_word(article["title"]):
                continue  # safety net: title contains a never-restore word (BR-014)
            restored.append(article)
    return restored


def relevance_gate(articles: list[dict[str, Any]], call: LlmCall) -> list[dict[str, Any]]:
    """Stage 5. Keeps an article when the model keeps it or it has a force-keep keyword (FR-014, FR-015)."""
    system = load("b_relevance_gate_system.txt")
    template = load("b_relevance_gate_user.txt")
    kept: list[dict[str, Any]] = []
    for batch in chunks(articles, STAGE_5.batch_size):
        items = [{"title": a["title"], "summary": (a.get("summary") or "")[:300]} for a in batch]
        user = render(template, items_json=json.dumps(items, ensure_ascii=False))
        try:
            keep = set(keep_indices_from(call(system, user, STAGE_5.temperature, STAGE_5.max_tokens)))
        except Exception:
            kept.extend(batch)  # FR-015: a failed call keeps the whole batch
            continue
        for index, article in enumerate(batch):
            if index in keep or has_force_keep_keyword(article["title"], article.get("summary") or ""):
                kept.append(article)
    return kept


def count_batches(total: int, size: int) -> int:
    """Number of model calls a stage makes for total items (used by checks)."""
    return (total + size - 1) // size if total else 0

