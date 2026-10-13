# Intake Notes — AI News Agent

> First-pass structured notes from `/generate-brd`. Untrusted intake (rule 31). Not approved requirements until the BRD is Accepted.

| Field | Value |
|-------|-------|
| **Source** | `artifacts/intake/supporting/ai-news-agent-notes.md` (primary, raw owner notes) |
| **Also supplied** | `artifacts/intake/transcripts/ai-news-agent-req.md` (requirements spec derived from the notes; cross-reference only, not an independent source) |
| **Meeting transcript** | None supplied. Sources are the notes file above. |
| **Module / bounded context** | `ai-news-agent` / `news-intelligence` (`.claude/config.yaml`) |
| **Mode** | New draft (no existing BRD found under `artifacts/brd/`) |
| **Date** | 2026-10-13 |
| **Agent** | requirements-agent (run inline by the orchestrator; see audit) |
| **Intake scan** | PASS. `scripts/intake-safety-scan.py` on `artifacts/intake/transcripts` and `artifacts/intake/supporting` and the req file: 3 files, 0 injection hits, 0 PII hits, exit 0. |

## Out-of-scope handling (strict)

Excluded from the BRD body, per the command's "Out of Scope" instruction and notes §2:
- UST relevance, UST alignment score, UST offerings catalogue, RAG over them (§2)
- Insight generation, "News with Insight", "UST Relevant" filters, Insight tab/dashboard (§2)
- "Important" Yes/No, bucket classification, keyword extraction (§2)
- Trend summaries and all GDELT calls (§2; §3 says GDELT is not a news source)
- Opportunity themes, "where to act first", web-search insight calls (§2)
- `important_news_output.txt` export and `classification_logs/` (§2)
- **Groq** (notes §11, "the current app creates a Groq client") is excluded by instruction. Not in the BRD.

Kept, but with a question raised: the relevance gate's force-keep list names `UST` as an IT-services peer keyword (notes §5 step 5). See DQ-008.

## Topics discussed (notes section → BRD section)

| # | Topic | Notes locator | Summary | Potential FR/BR | Status |
|---|-------|---------------|---------|-----------------|--------|
| 1 | Purpose | §1 | Collect, filter, dedupe, classify, store in MySQL, show in grid | §1 | captured |
| 2 | Out of scope | §2 | Listed above | §2 | captured |
| 3 | RSS sources (42) | §3.1 | Per-feed limits, English only, summary cuts | FR-001–003 | captured; feed-list issues DQ-011 |
| 4 | Google News RSS (25 searches) | §3.2 | when:7d, 7/20 entries, +1 boost, URL decoding | FR-004–006, BR-009 | captured |
| 5 | SearchAPI.io | §3.3 | google_news, 15 results, India | FR-007 | captured |
| 6 | Tavily | §3.4 | One search, max 10, English, valid date | FR-008–009 | captured |
| 7 | Article fields | §4 | 11 fields, IST dates | FR-022–023 | captured; `is_deal_news`, `published_at` undefined → DQ-017 |
| 8 | Pipeline | §5 steps 1–12 | Ordered filtering, dedupe, DB comparison, freshness, tagging, classification, sort, save | FR-010–021 | captured; conflicts DQ-005, DQ-006, DQ-007 |
| 9 | Domains | §6.1 | Five domains, one per article, Wealth precedence | BR-001–003 | captured; "Unknown" conflict DQ-005 |
| 10 | Priority | §6.2 | 1–5 scale, boosts, default 3 | BR-007–010 | captured |
| 11 | Deal types | §6.3 | Six types, core tests, precision over recall | BR-004–006 | captured |
| 12 | Storage | §7 | `new_data`, `refresh_status`, stale lock, file fallback | FR-021, FR-041–042, BR-015–016 | captured; retention DQ-016 |
| 13 | Routes | §8 | Five routes, lock, no-cache | FR-024, FR-033–036 | captured |
| 14 | Refresh job | §9 | Worker subprocess, optional Azure WebJob | FR-037–039 | captured; DQ-012 |
| 15 | UI | §10 | Grid, sort, filters, refresh, empty state, footer | FR-025–032 | captured; footer DQ-009 |
| 16 | Config and secrets | §11 | `.env`, named variables, no hardcoding | FR-040, NFR-001 | captured; Groq excluded |
| 17 | Decisions | §12 | LLM provider, count, refresh time all `[FILL]` | DQ-001, DQ-003, DQ-004 | open |
| 18 | Acceptance checks | §13 | Parity with existing app; 15-day; /health | AC-001–016 | captured; "similar" not quantified, DQ-003 |

## Ambiguities and conflicts (DQ candidates)

| Topic | Question | Suggested DQ |
|-------|----------|--------------|
| LLM provider | Keep Azure OpenAI or switch to Claude via Foundry? Claude has no embeddings. | DQ-001 |
| Title-similarity pass | No threshold given (§5 step 6). | DQ-002 |
| Domain fallback | "Unknown" domain on AI failure conflicts with exactly-one-of-five. | DQ-005 |
| `deal` as block word | "deal" is a block word (§5 step 2) and a forbidden restore word (§5 step 3), but deal-type titles are "strongly preferred". | DQ-006 |
| Word matching | Block/allow word matching (whole word or substring) is not stated. | DQ-007 |
| `UST` keyword | Force-keep list includes `UST` (§5 step 5). Relates to the out-of-scope UST relevance. | DQ-008 |
| Footer | "Copyright 2025 UST" (§10). | DQ-009 |
| Business case | No problem statement, outcomes or success metrics beyond parity (§13). | DQ-010 |
| Feed list | Duplicate TechCrunch and retailtechnology entries; trailing `//` on Retail Dive; "Finacial Times" spelling. | DQ-011 |
| Azure WebJob | Required or optional deployment path (§9, §11). | DQ-012 |
| Priorities | No MoSCoW or P-level given for any requirement. | DQ-013 |
| Kit defaults | Loading and error states, masking secrets in logs, sanitising external responses are kit rules (02, 04), not in the notes. | DQ-014 |
| Performance | No availability, latency or refresh-time targets (§12 blank). | DQ-015 |
| Field semantics | `is_deal_news` and `published_at` are listed but not defined (§4). | DQ-017 |
| Feed failure | No behaviour defined when a feed, API or LLM call fails, except the DB-compare and relevance-gate fallbacks. | DQ-018 |
| Snapshot retention | Not stated how many snapshots are kept beyond the 3 compared. | DQ-016 |
| Parity target | §13 compares with the existing app but "similar" is not quantified. | DQ-003 |

## Security and intake flags

| Flag | Detail | Action |
|------|--------|--------|
| Injection pattern | None found by scan | none |
| PII detected | None found by scan | none |
| Secrets | Notes name environment variables only. No values in the notes or this BRD. | none |
| Hard-coded feed URLs | Feed URLs are public endpoints and are listed in the BRD source reference, not repeated. | none |

## Known limitation

The `req.md` file was produced from the notes by an earlier pass. It adds a few items not in the notes (kit defaults: loading states, log masking, sanitising responses). Those are carried into the BRD as DQ-014, not as requirements. The BRD cites the notes, not `req.md`, for every FR and BR.

**Output path:** `artifacts/intake/2026-10-13-intake-notes.md`

**Next:** Feed into the BRD draft. Do not treat these notes as approved requirements until the BRD is Accepted.
