# Test-case BR Coverage — ai-news-agent (S1, BRD v0.2)

> Validates `docs/test-cases.md` against `evals.rule_source` (Accepted BRD). **PASS required before scripts or execution.** Written **only** by **br-coverage-validator** (quality-agent). Implementers must not stamp PASS.

| Field | Value |
|-------|-------|
| **Scope** | S1 full in-scope rule set of BRD v0.2: all FR-, BR-, NFR- rows (§5, §6, §10) and all AC- rows (§15) |
| **Rule source** | `artifacts/brd/ai-news-agent-BRD-draft.md` (v0.2, Accepted by Ardra Arun, 2026-10-13) |
| **Cases file** | `docs/test-cases.md` (51 cases) |
| **Matrix file** | `docs/test-matrix.md` (51 rows) |
| **Scorer** | br-coverage-validator |
| **Date** | 2026-10-13 |
| **Status** | **PASS** |
| **Coverage ratio** | 100% (100 mapped / 100 in-scope) |

## Coverage rules

- Every in-scope FR/BR has ≥1 `case_id` or an explicit **gap** row.
- A missing case is **gap**, not covered. **Silence is FAIL.**
- P0/P1 gaps cannot be waived by test-agent.
- A rule counts as covered only when at least one case in `docs/test-cases.md` cites it in `rule_ids`, or cites the AC in its AC line.
- Priority: all FR and BR are P0 (DQ-013 confirmed). All NFR are P1. Each AC takes the priority of the rule it maps to (AC-021 and AC-023 map to NFR, so P1; all others P0).
- Taxonomy: the BRD has no Type column, so all rules are scored as Guideline. Negatives are required only where the case file records an explicit reject path. No rule is failed for lacking a negative. Owner Type tagging is tracked as **DQ-E3** (open, non-blocking).

## Coverage matrix

Scoring rule for `status`: **covered** = at least one case cites the rule. Every row below is covered.

| rule_id | cited statement (short) | priority | case_ids | status | notes |
|---------|-------------------------|----------|----------|--------|-------|
| FR-001 | 42 RSS feeds, per-feed entry limits | P0 | TC-001 | covered | |
| FR-002 | RSS English only | P0 | TC-002 | covered | negative in TC-002 |
| FR-003 | RSS summary cut 400 / 1500 chars | P0 | TC-002 | covered | |
| FR-004 | Google News query URL form | P0 | TC-003 | covered | |
| FR-005 | Google News entry limits 20 / 7 | P0 | TC-003 | covered | |
| FR-006 | Decode Google News wrapper links | P0 | TC-003 | covered | |
| FR-007 | SearchAPI.io parameters | P0 | TC-004 | covered | |
| FR-008 | One Tavily search, max 10, answer and raw content | P0 | TC-005 | covered | |
| FR-009 | Tavily valid date, link, English filter | P0 | TC-005 | covered | negative in TC-005 |
| FR-010 | Failing source skipped, run continues | P0 | TC-001, TC-006 | covered | AC-017 also in TC-006 |
| FR-011 | Consumer-noise block and allow words | P0 | TC-007 | covered | negative in TC-007 |
| FR-012 | Stage 3 LLM title re-check | P0 | TC-008 | covered | negative in TC-008 |
| FR-013 | Dedupe by link then title, max 500 | P0 | TC-009 | covered | negative in TC-009 |
| FR-014 | Stage 5 relevance gate, force-keep list | P0 | TC-010 | covered | negative in TC-010 |
| FR-015 | Relevance gate failure keeps batch | P0 | TC-011 | covered | negative case |
| FR-016 | Embedding near-duplicate removal and title pass | P0 | TC-012 | covered | AC-020 also in TC-012 |
| FR-017 | DB comparison, merge, second dedupe | P0 | TC-013 | covered | |
| FR-018 | DB comparison failure fallback | P0 | TC-013 | covered | negative in TC-013 |
| FR-019 | 15-day cut, invalid date, cap 400 | P0 | TC-014 | covered | AC-001, AC-010, AC-011 in TC-014 |
| FR-020 | Deal-type tagging, failure fallback | P0 | TC-015 | covered | |
| FR-021 | Domain, priority, summary LLM call | P0 | TC-016 | covered | |
| FR-022 | Sort priority then date | P0 | TC-018 | covered | AC-009 in TC-018 |
| FR-023 | Save one snapshot; nothing fetched saves none | P0 | TC-019, TC-034 | covered | AC-018 in TC-019 |
| FR-024 | Article fields, is_deal_news, published_at | P0 | TC-021 | covered | AC-019 in TC-021 |
| FR-025 | Relative dates to IST; summary fragments removed | P0 | TC-021, TC-022 | covered | |
| FR-026 | Latest snapshot as news card grid | P0 | TC-035 | covered | |
| FR-027 | Sort control, two options | P0 | TC-036 | covered | |
| FR-028 | Domain filter, All plus five | P0 | TC-037 | covered | AC-013 in TC-037 |
| FR-029 | Deal-type chips with counts; Clear filter | P0 | TC-038 | covered | AC-014 in TC-038 |
| FR-030 | Refresh button message and polling | P0 | TC-039 | covered | AC-016 in TC-039 |
| FR-031 | "No news found" empty state | P0 | TC-040 | covered | AC-015 in TC-040 |
| FR-032 | Title "Latest Tech News", footer | P0 | TC-035 | covered | |
| FR-033 | No Insight or "UST Relevant" UI | P0 | TC-035 | covered | negative in TC-035 |
| FR-034 | GET /api/news shape, empty, no-cache | P0 | TC-023 | covered | AC-012 in TC-023 |
| FR-035 | POST /api/refresh running or started | P0 | TC-025, TC-047 | covered | AC-002 in TC-025 |
| FR-036 | POST /api/refresh HTTP 500 on start failure | P0 | TC-026 | covered | negative case |
| FR-037 | GET /api/refresh/status shape, no-cache | P0 | TC-027 | covered | |
| FR-038 | GET /health returns OK | P0 | TC-024 | covered | AC-003 in TC-024 |
| FR-039 | Worker subprocess; WebJob only when URL set | P0 | TC-028 | covered | |
| FR-040 | Worker clears running flag; writes finish fields | P0 | TC-029 | covered | AC-004 in TC-029 |
| FR-041 | App start does not fetch news | P0 | TC-030 | covered | |
| FR-042 | Settings from .env; examples empty | P0 | TC-031 | covered | |
| FR-043 | Status file fallback (development only) | P0 | TC-032 | covered | see follow-up F-1 on AC column |
| FR-044 | Status row auto-created; news_app database | P0 | TC-033, TC-034 | covered | |
| FR-045 | Pipeline stage order | P0 | TC-020 | covered | AC-022 in TC-020 |
| FR-046 | Prompts stored verbatim | P0 | TC-048 | covered | AC-024 in TC-048 |
| FR-047 | LLM calls use per-stage parameters | P0 | TC-050 | covered | negative in TC-050 |
| FR-048 | Relevance judged for IT services company | P0 | TC-049 | covered | |
| BR-001 | Exactly five domains | P0 | TC-016 | covered | |
| BR-002 | Domain classification signals | P0 | TC-016 | covered | |
| BR-003 | Wealth precedence over Banking | P0 | TC-016 | covered | |
| BR-004 | Six deal types and colours | P0 | TC-015 | covered | |
| BR-005 | Deal-type core tests | P0 | TC-015 | covered | |
| BR-006 | Deal types by meaning, main subject | P0 | TC-015 | covered | negative in TC-015 |
| BR-007 | Priority integer 1 to 5 scale | P0 | TC-016 | covered | |
| BR-008 | "Unknown" only on AI failure | P0 | TC-016 | covered | negative in TC-016 |
| BR-009 | Google News +1 boost | P0 | TC-003, TC-017 | covered | AC-008 in TC-017 |
| BR-010 | Deal +1 boost, cap 5 | P0 | TC-016, TC-017 | covered | AC-007 in TC-017 |
| BR-011 | Similarity thresholds 0.75 / 0.84 / 0.82 / title 0.92 | P0 | TC-012, TC-013 | covered | AC-020 in TC-012 |
| BR-012 | Drop articles older than 15 days | P0 | TC-014 | covered | AC-001 in TC-014 |
| BR-013 | At most 500 after dedupe, 400 after freshness | P0 | TC-014 | covered | AC-010 in TC-014 |
| BR-014 | Never-restore words (title only) | P0 | TC-008 | covered | negative in TC-008 |
| BR-015 | Atomic refresh lock, one at a time | P0 | TC-025 | covered | AC-002 in TC-025 |
| BR-016 | Stale lock cleared after 70 minutes | P0 | TC-026a | covered | AC-005 in TC-026a |
| BR-017 | Relevance gate drops only clear noise | P0 | TC-010 | covered | negative in TC-010 |
| BR-018 | Sort priority then newest date | P0 | TC-018 | covered | AC-009 in TC-018 |
| NFR-001 | Secrets from .env, none hardcoded | P1 | TC-031 | covered | |
| NFR-002 | No-cache headers on status and snapshot endpoints | P1 | TC-023, TC-027 | covered | |
| NFR-003 | Dates shown in IST | P1 | TC-022 | covered | |
| NFR-004 | Atomic lock; stale clear at 70 minutes | P1 | TC-026a | covered | |
| NFR-005 | Parity check against baseline only | P1 | TC-045, TC-045b | covered | executable TC-045 covers alone; TC-045b blocked (owner input) |
| NFR-006 | Mask secrets and PII in logs, traces | P1 | TC-043 | covered | negative case |
| NFR-007 | Loading, empty and error states | P1 | TC-041 | covered | error state only; empty state in TC-040 |
| NFR-008 | Backend line coverage at least 70% | P1 | TC-044 | covered | AC-021 in TC-044 |
| NFR-009 | Strip HTML from feed summaries | P1 | TC-046 | covered | negative in TC-046 |
| NFR-010 | No authentication (recorded risk) | P1 | TC-047 | covered | recorded-risk test |
| AC-001 | Article older than 15 days never in /api/news | P0 (BR-012) | TC-014 | covered | |
| AC-002 | Second POST while running returns running | P0 (BR-015) | TC-025 | covered | |
| AC-003 | GET /health returns 200 OK | P0 (FR-038) | TC-024 | covered | |
| AC-004 | Status row cleared with finished_at and message | P0 (FR-040) | TC-029 | covered | |
| AC-005 | Lock older than 70 minutes cleared | P0 (BR-016) | TC-026a | covered | |
| AC-006 | Exactly one of five domains; Unknown only on failure | P0 (FR-021, BR-001, BR-002, BR-008) | TC-016 | covered | |
| AC-007 | Deal-type article priority +1, cap 5 | P0 (BR-010) | TC-017 | covered | |
| AC-008 | Google News article priority +1, cap 5 | P0 (BR-009) | TC-017 | covered | |
| AC-009 | Ordered by priority, then date | P0 (BR-018, FR-022) | TC-018 | covered | |
| AC-010 | At most 400 articles after freshness | P0 (BR-013) | TC-014 | covered | |
| AC-011 | Missing or invalid date set to refresh time | P0 (FR-019) | TC-014 | covered | |
| AC-012 | /api/news returns count 0 when no snapshot | P0 (FR-034) | TC-023 | covered | |
| AC-013 | Domain filter shows All and five domains | P0 (FR-028) | TC-037 | covered | |
| AC-014 | Deal-type chips with counts; Clear filter | P0 (FR-029) | TC-038 | covered | |
| AC-015 | "No news found" when snapshot empty | P0 (FR-031) | TC-040 | covered | |
| AC-016 | Refreshing message shown; reload on finish | P0 (FR-030) | TC-039 | covered | |
| AC-017 | One failing source; refresh still completes | P0 (FR-010) | TC-006 | covered | |
| AC-018 | Nothing fetched: error, flag cleared, no snapshot | P0 (FR-023) | TC-019 | covered | |
| AC-019 | is_deal_news and published_at rules | P0 (FR-024) | TC-021 | covered | TC-032 also cites AC-019; see follow-up F-1 |
| AC-020 | No saved pair meets dedup thresholds | P0 (BR-011, FR-016, FR-017) | TC-012 | covered | TC-035 also cites AC-020; see follow-up F-2 |
| AC-021 | Backend line coverage at least 70% | P1 (NFR-008) | TC-044 | covered | |
| AC-022 | Stage order and deal tagging before priority | P0 (FR-045, FR-020, FR-021) | TC-020 | covered | |
| AC-023 | Parity within tolerance; not evaluated if baseline incomplete | P1 (NFR-005) | TC-045, TC-045b | covered | |
| AC-024 | Prompt text matches owner file byte for byte | P0 (FR-046) | TC-048 | covered | |

## Roll-up

Rules counted: 48 FR + 18 BR + 10 NFR + 24 AC = 100 in-scope rows.

| Priority | Total rules | Covered | Gaps | Coverage % |
|----------|-------------|---------|------|------------|
| P0 | 88 (FR 48, BR 18, AC 22) | 88 | 0 | 100% (must be 100% for PASS: met) |
| P1 | 12 (NFR 10, AC 2) | 12 | 0 | 100% |
| P2 | 0 | 0 | 0 | n/a |
| **All in-scope** | **100** | **100** | **0** | **100%** |

Per source type: FR 48/48, BR 18/18, NFR 10/10, AC 24/24.

Checks run:
- Every `rule_ids` value in `docs/test-cases.md` (51 cases) was read and compared against the 100 in-scope rows. No in-scope row is uncited.
- Every case_id in `docs/test-matrix.md` (51 rows) has a matching body section in `docs/test-cases.md`. Layer counts in the matrix roll-up (api 7, IT 17, integration 19, uat 7, blocked 1) match the case file.
- Cases with no `rule_ids`: none. Orphan count: 0.

## Gaps requiring action

None. No P0 or P1 rule lacks a citing case, so no gap rows apply and no test-agent action blocks PASS.

Non-blocking follow-ups (not gaps; they do not change Status):

| ref | item | Owner | Blocking scripts |
|-----|------|-------|------------------|
| F-1 | TC-032 (status-file fallback, FR-043) cites AC-019, which is the is_deal_news / published_at criterion. The AC column should be corrected or left blank. FR-043 is still covered by its own rule_ids. | test-agent | no |
| F-2 | TC-035 (index page title, footer, no Insight controls) cites AC-020, which is the dedup-threshold criterion. The AC column should be corrected or left blank. FR-026, FR-032 and FR-033 are still covered by TC-035 rule_ids. AC-020 is still covered by TC-012. | test-agent | no |
| F-3 | TC-045b lists `DQ-019` in `rule_ids`. This is a decision ID, not a BRD rule. Move it to a notes field. NFR-005 and AC-023 are also covered by TC-045. | test-agent | no |
| F-4 | Case IDs skip TC-042 (numbering only; no missing rule depends on it). | test-agent | no |
| DQ-E3 | Owner to tag BR/FR Types (Constraint, Condition, Guideline). Negatives for Constraint and gate Condition rules can then be checked against `.claude/templates/br-tc-taxonomy.md`. Open, non-blocking. | Owner (to be named) | no |

Automated column: no scripts exist yet (matrix status `designed`), so the "cite automated test ID per Tested BR" check is not applicable at this stage.

## Validator attestation

| Check | Result |
|-------|--------|
| All P0 covered or waived with decision | PASS: 88 of 88 P0 rules covered; no waivers used |
| All P1 covered or documented gap | PASS: 12 of 12 P1 rules covered; no gaps |
| case_ids exist in test-cases.md | PASS: 51 of 51 matrix case_ids have body sections |
| No orphan cases without rule_ids | PASS: 0 orphans |

**Overall status: PASS** (coverage ratio 100%, 100 of 100 in-scope rows mapped).

Scope of this stamp: this file records rule-to-case mapping only. It does not approve the test package. `docs/quality/test-package-review.md` remains a human decision, and `/run-tests` remains gated on human **Approved**.

**Output path:** `docs/test-cases-br-coverage.md`
