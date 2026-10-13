# Design Brief — News grid (S1, SP-09 and SP-10)

> From `/generate-ui-design`. Mockup only. Production UI code is `/implement-ui`'s job. Copy is from the BRD; article content is `[Label]` placeholders.

| Field | Value |
|-------|-------|
| **Date** | 2026-10-13 |
| **Screen** | News grid (index page) |
| **Sprint items** | SP-09 (grid, index route, footer, no Insight UI); SP-10 (sort, filters, refresh polling) |
| **Plan** | `artifacts/sprints/S1-plan.md`, status **Approved** (Ardra Arun, 2026-10-13) |
| **Reference** | Operator screenshot `artifacts/design/current_ui.png`. No URL was given, so `tools/design/capture-reference.py` was not run. |
| **Mockup** | `artifacts/design/2026-10-13-news-grid-mockup.png` (source: `2026-10-13-news-grid-mockup.html`) |
| **Manifest** | `artifacts/design/2026-10-13-mockup-manifest.json` |

## Plan acceptance criteria this design serves

| AC | Requirement | How the mockup shows it |
|----|-------------|-------------------------|
| AC-013 | Domain filter shows "All" and the five domains | "Filter by domain: All" control (FR-028) |
| AC-014 | Deal-type filter shows a count for each of six deal types; Clear filter resets it | Deal-type chip row with six counts, and "Clear filter" (FR-029) |
| AC-015 | "No news found" when there are no articles | Empty state is described below; not drawn (see Open items) |
| AC-016 | While refreshing, show "Refreshing news - this may take a while..."; reload when done | "Refresh News" button (FR-030); message shown during refresh is described below |

Also covered: FR-026 (card grid), FR-027 (sort: "Priority (High to Low)" and "Date (Newest to Oldest)"), FR-031 (empty state), FR-032 (title "Latest Tech News", footer "Copyright 2025 UST"), FR-033 (no Insight controls).

## Visible elements taken from the reference (screenshot)

| Element | Used in mockup | Why |
|---------|----------------|-----|
| Page title and header bar | Yes ("Latest Tech News") | FR-032 |
| Sort control | Yes | FR-027 |
| Domain filter | Yes | FR-028 |
| Deal-type filter with colour chips | Yes (six colours from BRD §6.3, names only) | FR-029 |
| Refresh button | Yes ("Refresh News") | FR-030 |
| Card grid, three columns | Yes | FR-026 |
| Footer | Yes ("Copyright 2025 UST") | DQ-009 |

## Reference elements not used

| Element | Reason |
|---------|--------|
| "Filter by insight" button | Out of scope: Insight features (FR-033, BRD §2) |
| Insight "i" badge on each card | Out of scope: Insight popup (FR-033) |
| UST logo | Brand asset. Not copied; the mockup shows `[Logo]`. |
| Card colours and border style | Not specified by the BRD. Mockup uses a neutral style with the BRD deal colours only. |

## Owner answers (2026-10-13) and where they land

| Item | Owner answer | In the mockup and brief |
|------|--------------|-------------------------|
| "Updated" timestamp | Yes. Must show the fetched time. | Shown in the toolbar as `Updated: [fetched_at, IST]` (FR-034 `fetched_at`). |
| "See more..." | Yes. | Shown under each summary. Opens the full text (behaviour to be built in `/implement-ui`). |
| Priority or alignment marker | Lavender outline for news more aligned with IT company services. Priority number not stated. | **Not built yet.** See below. |
| Error copy | "No news loaded, check your connection" | Used for the error state (see States). |
| Logo | UST logo | **Placeholder kept.** See below. |

**Open: lavender outline (UD-03).** A marker for news "more aligned with IT company services" looks like the UST alignment or relevance feature. The BRD puts that out of scope (§2 "UST relevance, UST alignment score"; FR-033). Confirm whether the outline is in scope before `/implement-ui` builds it. The priority number isn't mentioned, so it stays out of the mockup.

**Open: logo (UD-05).** The command says not to copy trademarked assets verbatim. The owner has named the UST logo, but the logo file is not in the repo. Send the logo file, and confirm it may be used, and the header will use it. Until then the header shows `[Logo]`.

## States (described, not drawn)

- **Refreshing:** while `POST /api/refresh` is running, the page shows "Refreshing news - this may take a while..." and polls `GET /api/refresh/status` until `running` is false, then reloads (FR-030).
- **Empty:** when the snapshot has no articles, show "No news found" (FR-031).
- **Error (NFR-007):** when the page cannot load news, show "No news loaded, check your connection" (owner copy).
- **Loading (NFR-007):** kit rule 04 requires a loading state; DQ-014 adopted it. The owner has not supplied loading wording, so it stays a `[Label]` placeholder.

## Open items for the owner

| ID | Question | Owner | Blocking `/implement-ui`? |
|----|----------|-------|---------------------------|
| UD-01 | "Updated" timestamp from `fetched_at` | Owner | Answered (yes) |
| UD-02 | "See more..." control | Owner | Answered (yes) |
| UD-03 | Lavender outline for news aligned with IT company services; priority display not stated | Owner | **Open.** Confirm whether the outline is in scope (possible UST alignment feature, out of scope). |
| UD-04 | Loading wording (NFR-007) | Owner (name needed) | No. Error wording answered. |
| UD-05 | UST logo file and permission to use it | Owner (name needed) | **Open.** Logo file needed. |

UD-03 and UD-05 are not blocking `/implement-ui`: it can build the grid, timestamp and see-more control now. The outline and the logo can follow once answered.

## Notes

- The mockup's deal-type counts show "(0)" as placeholders. Real counts come from the snapshot.
- The mockup shows a `Priority [1-5]` tag only as a placeholder for UD-03.
