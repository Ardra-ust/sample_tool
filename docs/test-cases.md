# Test cases — ai-news-agent (S1, BRD v0.2)

Designed cases only. Not scripts. Every case cites FR/BR/AC IDs from the accepted BRD (`artifacts/brd/ai-news-agent-BRD-draft.md`, v0.2, accepted by Ardra Arun on 2026-10-13). Source for every case: that BRD, section noted. Owner answers recorded in BRD §14.1 are cited where they set a value.

Notes on classification:
- The BRD has no Type column (Constraint, Condition, Guideline). Per `br-tc-taxonomy.md`, rules are treated as Guideline. A negative case is written only where the BRD states an explicit reject path, limit, or error. Open DQ-E3 asks the owner to tag Types so Constraint and gate negatives can be checked against the taxonomy.
- Behavioural statements ("is not invoked", "does not run") get no negative case.
- Cases that depend on code not yet built (SP-04 to SP-08) are designed here; they are not blocked by design.

| case_id | title | rule_ids | AC | execution_layer | type | source_path |
|---------|-------|----------|----|-----------------|------|-------------|
| TC-001 | RSS feeds: per-feed entry limits | FR-001, FR-010 | — | integration | positive | BRD §5 FR-001 |
| TC-002 | RSS: English only; summary cut lengths | FR-002, FR-003 | — | integration | positive, negative | BRD §5 FR-002, FR-003 |
| TC-003 | Google News: query form, entry limits, boost, decoded links | FR-004, FR-005, FR-006, BR-009 | — | integration | positive | BRD §5 FR-004 to FR-006 |
| TC-004 | SearchAPI.io request parameters | FR-007 | — | integration | positive | BRD §5 FR-007 |
| TC-005 | Tavily: one search, valid date, link and English filter | FR-008, FR-009 | — | integration | positive, negative | BRD §5 FR-008, FR-009 |
| TC-006 | One failing source is skipped; run continues | FR-010 | AC-017 | integration | negative | BRD §5 FR-010; §14.1 DQ-018 |
| TC-007 | Consumer-noise filter: block and allow words | FR-011 | — | IT | positive, negative | BRD §5 FR-011; notes §5 step 2 |
| TC-008 | Stage 3 title re-check and never-restore words | FR-012, BR-014 | — | integration | positive, negative | BRD §5 FR-012; BR-014; §17 |
| TC-009 | De-duplication by link then title; cap of 500 | FR-013 | — | integration | positive, negative | BRD §5 FR-013 |
| TC-010 | Stage 5 relevance gate: keep, drop, force-keep | FR-014, BR-017 | — | integration | positive, negative | BRD §5 FR-014; BR-017; §17 |
| TC-011 | Relevance gate failure keeps the batch | FR-015 | — | integration | negative | BRD §5 FR-015; §14.1 DQ-018 |
| TC-012 | Embedding near-duplicate removal and title pass | FR-016, BR-011 | AC-020 | IT | positive, negative | BRD §5 FR-016; BR-011; §14.1 DQ-002 |
| TC-013 | Database comparison: 0.84 drop, merge, 0.82 pass; DB failure | FR-017, FR-018, BR-011 | — | integration | positive, negative | BRD §5 FR-017, FR-018; BR-011 |
| TC-014 | Freshness: 15-day cut, invalid date, cap of 400 | FR-019, BR-012, BR-013 | AC-001, AC-010, AC-011 | IT | positive, negative | BRD §5 FR-019; BR-012; BR-013 |
| TC-015 | Deal-type tagging: six types, main-subject rule, failure | FR-020, BR-004, BR-005, BR-006 | — | integration | positive, negative | BRD §5 FR-020; §6.3; §17 stage 9 |
| TC-016 | Domain, priority and summary: classification, Unknown fallback, priority cap | FR-021, BR-001, BR-002, BR-003, BR-007, BR-008, BR-010 | AC-006 | integration | positive, negative | BRD §5 FR-021; §6.1; §6.2; §14.1 DQ-005 |
| TC-017 | Priority boosts: Google News +1, deal +1, cap 5 | BR-009, BR-010 | AC-007, AC-008 | IT | positive, negative | BRD §6.2; §14.1 DQ-005 |
| TC-018 | Sort: priority high to low, then newest published | FR-022, BR-018 | AC-009 | IT | positive | BRD §5 FR-022; BR-018 |
| TC-019 | Save one snapshot per refresh; nothing fetched saves nothing | FR-023 | AC-018 | integration | positive, negative | BRD §5 FR-023; §14.1 DQ-018 |
| TC-020 | Pipeline stage order and no overlap | FR-045 | AC-022 | integration | positive | BRD §5 FR-045 |
| TC-021 | Article fields; is_deal_news and published_at | FR-024, FR-025 | AC-019 | IT | positive | BRD §5 FR-024; §14.1 DQ-017 |
| TC-022 | Relative dates to absolute IST; summary fragments removed | FR-025, NFR-003 | — | IT | positive | BRD §5 FR-025; NFR-003 |
| TC-023 | GET /api/news: shape, empty snapshot, no-cache | FR-034, NFR-002, AC-012 | AC-012 | api | positive | BRD §5 FR-034; NFR-002 |
| TC-024 | GET /health returns OK | FR-038 | AC-003 | api | positive | BRD §5 FR-038 |
| TC-025 | POST /api/refresh: started, then running (one refresh at a time) | FR-035, BR-015 | AC-002 | api | positive, negative | BRD §5 FR-035; BR-015 |
| TC-026 | Refresh start failure: HTTP 500 and failure recorded | FR-036 | — | api | negative | BRD §5 FR-036 |
| TC-026a | Stale lock: cleared after 70 minutes, not before | BR-016, NFR-004 | AC-005 | IT | positive, negative | BRD §6 BR-016; §10 NFR-004; §14.1 DQ-018 |
| TC-027 | GET /api/refresh/status: shape and no-cache | FR-037, NFR-002 | — | api | positive | BRD §5 FR-037 |
| TC-028 | Worker start: subprocess by default; WebJob only when URL is set | FR-039 | — | integration | positive | BRD §5 FR-039; §14.1 DQ-012 |
| TC-029 | Worker finish: running flag cleared; message or trace written | FR-040 | AC-004 | integration | positive, negative | BRD §5 FR-040 |
| TC-030 | Starting the app does not fetch news | FR-041 | — | api | positive | BRD §5 FR-041 |
| TC-031 | Settings read from .env; no hardcoded secret | FR-042, NFR-001 | — | IT | positive | BRD §5 FR-042; §10 NFR-001 |
| TC-032 | Status file fallback when the database is unavailable (development only) | FR-043 | — | IT | positive | BRD §5 FR-043 |
| TC-033 | Status row created with "Ready" when missing | FR-044 | — | integration | positive | BRD §5 FR-044; §7 |
| TC-034 | Snapshots and status stored in database news_app | FR-044, FR-023 | — | integration | positive | BRD §5 FR-044; §7 |
| TC-035 | Index page: title, footer, no Insight controls | FR-026, FR-032, FR-033 | — | uat | positive, negative | BRD §5 FR-026, FR-032, FR-033; §14.1 DQ-009 |
| TC-036 | Sort control: two options | FR-027 | — | uat | positive | BRD §5 FR-027 |
| TC-037 | Domain filter: All and five domains | FR-028 | AC-013 | uat | positive, negative | BRD §5 FR-028; §6.1 |
| TC-038 | Deal-type filter: six chips with counts; Clear filter | FR-029 | AC-014 | uat | positive | BRD §5 FR-029; §6.3 |
| TC-039 | Refresh button: message, polling, reload | FR-030 | AC-016 | uat | positive | BRD §5 FR-030 |
| TC-040 | Empty state "No news found" | FR-031 | AC-015 | uat | positive | BRD §5 FR-031 |
| TC-041 | Load failure shows the connection message | NFR-007 | — | uat | negative | BRD §10 NFR-007; §14.1 DQ-014 |
| TC-043 | Secrets masked in traces and logs | NFR-006 | — | IT | negative | BRD §10 NFR-006; §14.1 DQ-014 |
| TC-044 | Backend line coverage gate at 70% | NFR-008 | AC-021 | IT | positive, negative | BRD §10 NFR-008; §14.1 DQ-010 |
| TC-045 | Parity check: reported only against a complete baseline | NFR-005 | AC-023 | IT | positive, negative | BRD §10 NFR-005; §15 AC-023; §14.1 DQ-019 |
| TC-045b | Parity baseline values recorded by the owner | NFR-005 | AC-023 | blocked | positive | BRD §14.1 DQ-019 |
| TC-046 | HTML stripped from feed summaries | NFR-009 | — | IT | positive, negative | BRD §10 NFR-009; §14.1 DQ-014 |
| TC-047 | No authentication in this build (recorded risk) | NFR-010, FR-035 | — | api | positive | BRD §10 NFR-010; §14.1 DQ-020 |
| TC-048 | Prompts stored verbatim as templates | FR-046 | AC-024 | IT | positive, negative | BRD §5 FR-046; §17 |
| TC-049 | Relevance judged for an IT services company (stages 3 and 5) | FR-048 | — | IT | positive | BRD §5 FR-048; §17 |
| TC-050 | LLM calls use supported parameters per stage | FR-047 | — | IT | positive, negative | BRD §5 FR-047; §17 |

---

## TC-001 — RSS feeds: per-feed entry limits

- **rule_ids:** FR-001, FR-010
- **AC:** —
- **execution_layer:** integration
- **type:** positive
- **preconditions:** Source adapters are replaced by stubs; the RSS list has 42 entries (BRD §3.1). No network is used.
- **steps:**
  1. Run the refresh pipeline entry point with the RSS stub serving 10 entries for every feed except AnalyticsIndiaMag, which serves 60 entries.
  2. Read the list of fetched RSS items from the run's stage 1 output.
  3. Count items per feed source name.
- **expected:** Every feed except AnalyticsIndiaMag contributes exactly 7 items. AnalyticsIndiaMag contributes exactly 50 items. All four source types are requested in the run (FR-010).
- **source_path / locator:** artifacts/brd/ai-news-agent-BRD-draft.md, §5 FR-001, FR-010

## TC-002 — RSS: English only; summary cut lengths

- **rule_ids:** FR-002, FR-003
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** RSS stub serves one English item and one non-English item in the same feed. One item has a 600-character summary; an AnalyticsIndiaMag item has a 1,600-character summary.
- **steps:**
  1. Run stage 1 with the stubbed RSS feed.
  2. Read the stored article list.
  3. Check the language of each item and the length of each summary.
- **expected:** The non-English item is absent from the output (negative, FR-002). The 600-character summary is cut to 400 characters (FR-003). The AnalyticsIndiaMag summary is cut to 1500 characters (FR-003).
- **source_path / locator:** BRD §5 FR-002, FR-003

## TC-003 — Google News: query form, entry limits, boost, decoded links

- **rule_ids:** FR-004, FR-005, FR-006, BR-009
- **AC:** —
- **execution_layer:** integration
- **type:** positive
- **preconditions:** Google News stub returns entries for each of the 25 searches. One feed name contains "MnAPartnership"; another does not.
- **steps:**
  1. Run stage 1 with the Google News stub.
  2. Inspect the request URLs made to the stub.
  3. Count items for a feed whose name contains "MnAPartnership", and for a feed whose name does not.
  4. Inspect the stored link of a Google News item.
- **expected:** Each request URL has the form `https://news.google.com/rss/search?q=<url-encoded query> when:7d`. The MnAPartnership feed contributes up to 20 items; the other feed up to 7. Each Google News item has `is_google_news` true (BR-009 input). Each stored link is the publisher URL, not the Google wrapper URL (FR-006).
- **source_path / locator:** BRD §5 FR-004 to FR-006; §6.2 BR-009

## TC-004 — SearchAPI.io request parameters

- **rule_ids:** FR-007
- **AC:** —
- **execution_layer:** integration
- **type:** positive
- **preconditions:** SearchAPI.io client replaced by a stub that records the request.
- **steps:**
  1. Run stage 1 with the SearchAPI stub.
  2. Read the recorded request.
- **expected:** Engine is `google_news`; query is `technology`; results count is 15; location is `India`; both `top_stories` and `organic_results` are read.
- **source_path / locator:** BRD §5 FR-007

## TC-005 — Tavily: one search, valid date, link and English filter

- **rule_ids:** FR-008, FR-009
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Tavily stub returns 10 results: 8 with a valid date, a link and English text; 1 with no date; 1 with no link.
- **steps:**
  1. Run stage 1 with the Tavily stub.
  2. Count the Tavily search calls made in the run.
  3. Read the Tavily items in the stage 1 output.
- **expected:** Exactly one Tavily search per run, with max results 10, answer on, raw content on (FR-008). The item with no date and the item with no link are absent (negative, FR-009). The 8 valid items are kept.
- **source_path / locator:** BRD §5 FR-008, FR-009

## TC-006 — One failing source is skipped; the run continues

- **rule_ids:** FR-010
- **AC:** AC-017
- **execution_layer:** integration
- **type:** negative
- **preconditions:** The SearchAPI stub raises a connection error. The other three sources return items.
- **steps:**
  1. Run stage 1 with the failing SearchAPI stub.
  2. Read the run log and the stage 1 output.
- **expected:** The run does not stop. The failure is logged. Items from RSS, Google News and Tavily are present in the output. No SearchAPI items are present (owner answer, BRD §14.1 DQ-018).
- **source_path / locator:** BRD §5 FR-010; §14.1 DQ-018

## TC-007 — Consumer-noise filter: block and allow words

- **rule_ids:** FR-011
- **AC:** —
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** The block and allow lists from notes §5 step 2 are loaded. Matching is a substring match on lowercased title plus summary.
- **steps:**
  1. Pass the article "Best laptop deals this week" (title) with summary "shopping guide" to the noise filter.
  2. Pass the article "Enterprise platform modernization in banks" with summary "deal news" to the noise filter.
  3. Pass the article "POS vendor position announced" with summary "" to the noise filter.
- **expected:** Article 1 is noise: it has block words ("best", "laptop", "deal", "shopping") and no allow word. Article 2 is not noise (negative): it has the block word "deal" but also the allow words "enterprise" and "platform". Article 3 is not noise: "POS" is an allow word, so the result is not noise even though the summary is empty. Known side effect recorded in DQ-007: "POS" also matches "position" and "possible" as a substring.
- **source_path / locator:** BRD §5 FR-011; §14.1 DQ-007

## TC-008 — Stage 3 title re-check and never-restore words

- **rule_ids:** FR-012, BR-014
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Model client is a stub that returns fixed JSON. Noise articles: "Mergers announced in cloud sector", "Christmas gadget sale", "Chip firm raises funding".
- **steps:**
  1. Run stage 3 with the stub returning `{"keep_indices": [0, 1, 2]}`.
  2. Read the restored list.
  3. Run stage 3 with the stub returning `{"keep_indices": [0]}` for a batch whose title is "Deal of the year in retail".
- **expected:** Restored: "Mergers announced in cloud sector" and "Chip firm raises funding". Not restored (negative, BR-014): "Christmas gadget sale", because the title contains "christmas" and "sale". In step 3, "Deal of the year in retail" is not restored, because the title contains "deal" (title only, DQ-006).
- **source_path / locator:** BRD §5 FR-012; §6 BR-014; §17 stage 3; §14.1 DQ-006

## TC-009 — De-duplication by link then title; cap of 500

- **rule_ids:** FR-013
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** A list of 510 articles: 10 share a link with another item; 3 pairs have different links and identical titles.
- **steps:**
  1. Run the de-duplication step on the list.
  2. Count the output items.
  3. Inspect the output for duplicate links.
- **expected:** Items with a repeated link are removed. Items with a repeated title are removed. The output has at most 500 items (negative: the 501st and later items are dropped).
- **source_path / locator:** BRD §5 FR-013

## TC-010 — Stage 5 relevance gate: keep, drop, force-keep

- **rule_ids:** FR-014, BR-017
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Model stub returns `{"keep_indices": [0]}` for a batch of three: "Quarterly headline" (summary "general news"), "Acquisition of a bank" (summary "deal news"), "Garden show" (summary "flowers").
- **steps:**
  1. Run stage 5 on the batch.
  2. Read the kept list.
  3. Run stage 5 with the model returning `{"keep_indices": []}` for the single article "Garden show" (summary "flowers").
- **expected:** Kept: "Quarterly headline" (model keep), "Acquisition of a bank" (force-keep "acqui"). Step 3: "Garden show" is dropped (negative, BR-017 clear noise, no force-keep match).
- **source_path / locator:** BRD §5 FR-014; §6 BR-017; §17 stage 5

## TC-011 — Relevance gate failure keeps the batch

- **rule_ids:** FR-015
- **AC:** —
- **execution_layer:** integration
- **type:** negative
- **preconditions:** Model stub raises a timeout for the batch.
- **steps:**
  1. Run stage 5 on a batch of 8 articles, none with a force-keep keyword.
  2. Read the kept list.
- **expected:** All 8 articles are kept. No article is dropped because the call failed.
- **source_path / locator:** BRD §5 FR-015; §14.1 DQ-018

## TC-012 — Embedding near-duplicate removal and title pass

- **rule_ids:** FR-016, BR-011
- **AC:** AC-020
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Embedding client is a stub returning fixed vectors. Titles compared with the title rule: lowercase, keep letters and digits only; duplicate when length difference is below 10 and SequenceMatcher ratio is 0.92 or higher (DQ-002).
- **steps:**
  1. Pass two articles with embedding similarity 0.80 to the dedupe function.
  2. Pass two articles with embedding similarity 0.70 to the dedupe function.
  3. Pass two titles "Infosys wins deal" and "Infosys wins deal!" (length difference 1, ratio 1.0) to the title pass.
  4. Pass two titles "Infosys wins deal" and "Wipro announces results" to the title pass.
  5. Make the embedding client raise an error and call the dedupe function on a list of three articles.
- **expected:** Step 1: the second article is removed (similarity 0.80 is at least 0.75). Step 2: both articles are kept (negative, 0.70 is below 0.75). Step 3: the second title is removed. Step 4: both are kept (negative). Step 5: the list is returned unchanged; no embedding or title dedupe runs (DQ-018).
- **source_path / locator:** BRD §5 FR-016; §6 BR-011; §14.1 DQ-002, DQ-018

## TC-013 — Database comparison: 0.84 drop, merge, 0.82 pass; DB failure

- **rule_ids:** FR-017, FR-018, BR-011
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Database holds the latest 3 snapshots. Embedding stub returns fixed similarities.
- **steps:**
  1. Compare one new article with similarity 0.86 to a stored article.
  2. Compare one new article with similarity 0.80 to a stored article.
  3. Merge the remaining new articles with the most recent snapshot, then run the second dedupe with 0.82.
  4. Make the database read fail and run the comparison.
- **expected:** Step 1: the new article is dropped (0.86 is at least 0.84). Step 2: it is kept (negative, 0.80 is below 0.84). Step 3: the merge uses only the most recent snapshot; the second dedupe removes pairs at 0.82 or higher. Step 4: database-duplicate removal is skipped and only the new articles are kept (FR-018).
- **source_path / locator:** BRD §5 FR-017, FR-018; §6 BR-011

## TC-014 — Freshness: 15-day cut, invalid date, cap of 400

- **rule_ids:** FR-019, BR-012, BR-013
- **AC:** AC-001, AC-010, AC-011
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Current time is 2026-10-13 12:00 IST. Articles: one published 2026-09-27 (16 days before), one published 2026-09-29 (14 days before), one with an unparseable date, and 401 valid articles.
- **steps:**
  1. Run the freshness filter on the articles.
  2. Read the output.
  3. Read the date of the item with the unparseable date.
  4. Count the output items.
- **expected:** The 16-day-old article is dropped (negative, AC-001). The 14-day-old article is kept. The unparseable date is set to 2026-10-13 12:00 (AC-011). The output has exactly 400 items; the oldest item of the 401 is dropped (negative, AC-010).
- **source_path / locator:** BRD §5 FR-019; §6 BR-012, BR-013

## TC-015 — Deal-type tagging: six types, main-subject rule, failure

- **rule_ids:** FR-020, BR-004, BR-005, BR-006
- **AC:** —
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Model stub returns fixed categories. Category definitions are the owner's file (`c_deal_category_definitions.txt`).
- **steps:**
  1. Tag an article titled "Two banks form a new jointly owned company" with the stub returning `["joint_ventures"]`.
  2. Tag an article titled "Partner logos on our website" with the stub returning `["partnerships"]`.
  3. Make the model call raise an error and tag a batch of 2 articles.
  4. Read the category keys for each article.
- **expected:** Step 1: `deal_categories` is `["joint_ventures"]` and `is_deal_news` is true. Step 2: the stub's category is dropped by the code, because it is not the article's main subject (negative, BR-006); `deal_categories` is `[]`. Step 3: both articles get `deal_categories` `[]` and `is_deal_news` false (DQ-018). Keys are one of the six types only (BR-004).
- **source_path / locator:** BRD §5 FR-020; §6 BR-004 to BR-006; §17 stage 9; §14.1 DQ-018

## TC-016 — Domain, priority and summary: classification, Unknown fallback, cap

- **rule_ids:** FR-021, BR-001, BR-002, BR-003, BR-007, BR-008, BR-010
- **AC:** AC-006
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Model stub returns JSON with `refined_summary`, `domain` and `priority`.
- **steps:**
  1. Classify an article about a bank and a wealth manager; the stub returns domain "Wealth & Asset Management".
  2. Classify an article with the stub returning domain "Technology & Communication" and priority 4.
  3. Make the model call raise an error for an article.
  4. Classify an article where the stub returns priority 5 and the article has a deal category and a Google News origin.
- **expected:** Step 1: domain is "Wealth & Asset Management" (BR-003 precedence). Step 2: domain is "Technology & Communication"; priority is 4. Step 3: domain is "Unknown"; priority is 3 plus boosts, capped at 5; summary is unchanged (BR-008; DQ-005). Step 4: priority is 5 (capped, BR-010). Every article's domain is one of the five domains or "Unknown" (AC-006). Priority is between 1 and 5.
- **source_path / locator:** BRD §5 FR-021; §6 BR-001 to BR-003, BR-007, BR-008, BR-010; §14.1 DQ-005

## TC-017 — Priority boosts: Google News +1, deal +1, cap 5

- **rule_ids:** BR-009, BR-010
- **AC:** AC-007, AC-008
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Articles with classified priority 3 before boosts.
- **steps:**
  1. Apply boosts to an article from a Google News feed with no deal category.
  2. Apply boosts to an article with a deal category and no Google News origin.
  3. Apply boosts to an article with priority 4 from Google News with a deal category.
- **expected:** Step 1: priority 4 (BR-009). Step 2: priority 4 (BR-010). Step 3: priority 5 (6 would exceed the cap, so 5, BR-010). An article with no boosts keeps its priority (negative).
- **source_path / locator:** BRD §6 BR-009, BR-010; §14.1 DQ-005

## TC-018 — Sort: priority high to low, then newest published

- **rule_ids:** FR-022, BR-018
- **AC:** AC-009
- **execution_layer:** IT
- **type:** positive
- **preconditions:** Articles: priority 5 published 2026-10-01; priority 5 published 2026-10-09; priority 3 published 2026-10-12.
- **steps:**
  1. Sort the list by the pipeline sort.
  2. Read the order of the three articles.
- **expected:** Order: priority 5 published 2026-10-09, then priority 5 published 2026-10-01, then priority 3 published 2026-10-12.
- **source_path / locator:** BRD §5 FR-022; §6 BR-018

## TC-019 — Save one snapshot per refresh; nothing fetched saves nothing

- **rule_ids:** FR-023
- **AC:** AC-018
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Database test copy with the snapshot table and the status row.
- **steps:**
  1. Run a refresh that fetches and saves articles.
  2. Count snapshot rows.
  3. Run a refresh where every source returns nothing.
  4. Count snapshot rows and read the status row.
- **expected:** Step 1: one new snapshot row with the full sorted list. Step 3: no new snapshot row is saved (negative, AC-018); the run ends with an error; the running flag is cleared.
- **source_path / locator:** BRD §5 FR-023; §14.1 DQ-018

## TC-020 — Pipeline stage order and no overlap

- **rule_ids:** FR-045
- **AC:** AC-022
- **execution_layer:** integration
- **type:** positive
- **preconditions:** Each stage is replaced by a stub that records its start and end time, with an error if the previous stage has not ended.
- **steps:**
  1. Run the refresh pipeline with the recording stubs.
  2. Read the recorded start and end times for stages 1 to 12.
- **expected:** The stages run in the FR-045 order: fetch, noise filter, title re-check, dedupe, relevance gate, embedding dedupe, database comparison, freshness, deal tagging, domain/priority/summary, sort, save. No stage starts before the previous one ends.
- **source_path / locator:** BRD §5 FR-045

## TC-021 — Article fields; is_deal_news and published_at

- **rule_ids:** FR-024, FR-025
- **AC:** AC-019
- **execution_layer:** IT
- **type:** positive
- **preconditions:** An article with deal categories; an article with no deal categories; an article with a missing date.
- **steps:**
  1. Build the stored record for the article with deal categories.
  2. Build the stored record for the article with no deal categories.
  3. Build the stored record for the article with a missing date.
- **expected:** Step 1: the record has the eleven fields (title, link, source, published, summary, domain, priority, deal_categories, is_deal_news, is_google_news, published_at); `is_deal_news` is true; `published_at` equals `published`. Step 2: `is_deal_news` is false. Step 3: both `published` and `published_at` are the current time (DQ-017).
- **source_path / locator:** BRD §5 FR-024; §14.1 DQ-017

## TC-022 — Relative dates to absolute IST; summary fragments removed

- **rule_ids:** FR-025, NFR-003
- **AC:** —
- **execution_layer:** IT
- **type:** positive
- **preconditions:** Current time is 2026-10-13 12:00 IST.
- **steps:**
  1. Parse the date "2 hours ago".
  2. Parse the date "yesterday".
  3. Clean the summary "Posted 13 Oct 2026, 09:00. The bank expands its platform."
- **expected:** Step 1: "2026-10-13 10:00:00" (IST). Step 2: "2026-10-12" with the time shown in IST (UTC+5:30). Step 3: the date and time fragment is removed; the summary reads "The bank expands its platform."
- **source_path / locator:** BRD §5 FR-025; §10 NFR-003

## TC-023 — GET /api/news: shape, empty snapshot, no-cache

- **rule_ids:** FR-034, NFR-002
- **AC:** AC-012
- **execution_layer:** api
- **type:** positive
- **preconditions:** Test database with a snapshot table and no rows (case A) and with one stored snapshot of 2 articles (case B).
- **steps:**
  1. Send `GET /api/news` in case A.
  2. Send `GET /api/news` in case B.
  3. Read the response headers in case B.
- **expected:** Case A: status 200; body `{"count": 0, "results": [], "fetched_at": null}`. Case B: status 200; `count` is 2; `results` has 2 items; `fetched_at` is the stored time as `YYYY-MM-DD HH:MM:SS`. Both responses have `Cache-Control: no-cache`.
- **source_path / locator:** BRD §5 FR-034; §10 NFR-002; §8 route table

## TC-024 — GET /health returns OK

- **rule_ids:** FR-038
- **AC:** AC-003
- **execution_layer:** api
- **type:** positive
- **preconditions:** Application started with `flask --app app.main:app run` (no database needed).
- **steps:**
  1. Send `GET /health`.
  2. Read the response status, content type and body.
- **expected:** Status 200, content type `text/plain`, body `OK`.
- **source_path / locator:** BRD §5 FR-038; §8

## TC-025 — POST /api/refresh: started, then running

- **rule_ids:** FR-035, BR-015
- **AC:** AC-002
- **execution_layer:** api
- **type:** positive, negative
- **preconditions:** Status row is idle (running 0). The worker start is replaced by a stub that does not block.
- **steps:**
  1. Send `POST /api/refresh`.
  2. Send `POST /api/refresh` again while the first refresh is still running (the stub has not finished).
  3. Read the status row.
- **expected:** Step 1: status 200, body `{"status": "started"}`. Step 2: status 200, body `{"status": "running"}` (negative, BR-015: no second worker is started). Step 3: `running` is 1. The worker stub has been called once.
- **source_path / locator:** BRD §5 FR-035; §6 BR-015

## TC-026 — Refresh start failure: HTTP 500 and failure recorded

- **rule_ids:** FR-036
- **AC:** —
- **execution_layer:** api
- **type:** negative
- **preconditions:** Worker start is replaced by a stub that raises an error.
- **steps:**
  1. Send `POST /api/refresh`.
  2. Read the status row.
- **expected:** Status 500 with an empty body (contract OQ-API-1). The status row has `running` 0, the failure message, and a trace with no secret values.
- **source_path / locator:** BRD §5 FR-036; §8

## TC-026a — Stale lock: cleared after 70 minutes, not before

- **rule_ids:** BR-016, NFR-004
- **AC:** AC-005
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Status row with `running` 1 and `started_at` set. Stale limit is 70 minutes (`REFRESH_STALE_MINUTES` default, owner decision DQ-018).
- **steps:**
  1. Set `started_at` to 69 minutes before now and run the stale-clear step.
  2. Set `started_at` to 72 minutes before now and run the stale-clear step.
  3. Read the status row after step 2.
- **expected:** Step 1: lock is not cleared (negative, 69 minutes is under the limit). Step 2: lock is cleared. Step 3: `running` is 0 and the message states that the worker likely died (BR-016).
- **source_path / locator:** BRD §6 BR-016; §10 NFR-004; §14.1 DQ-018

## TC-027 — GET /api/refresh/status: shape and no-cache

- **rule_ids:** FR-037, NFR-002
- **AC:** —
- **execution_layer:** api
- **type:** positive
- **preconditions:** Status row with a completed run.
- **steps:**
  1. Send `GET /api/refresh/status`.
  2. Read the response body and headers.
- **expected:** Status 200; body has `running`, `started_at`, `finished_at`, `message`, `last_run_type`; no `trace` field; header `Cache-Control: no-cache`.
- **source_path / locator:** BRD §5 FR-037; §10 NFR-002

## TC-028 — Worker start: subprocess by default; WebJob only when URL is set

- **rule_ids:** FR-039
- **AC:** —
- **execution_layer:** integration
- **type:** positive
- **preconditions:** Settings with `AZURE_WEBJOB_TRIGGER_URL` empty (case A) and set to a test URL (case B). Subprocess launch and WebJob call are stubs.
- **steps:**
  1. Start a refresh with the URL empty.
  2. Start a refresh with the URL set.
- **expected:** Case A: `refresh_worker.py` is started as a subprocess; no WebJob call is made. Case B: the WebJob trigger is called with the configured URL, user and password; no subprocess is started.
- **source_path / locator:** BRD §5 FR-039; §14.1 DQ-012

## TC-029 — Worker finish: running flag cleared; message or trace written

- **rule_ids:** FR-040
- **AC:** AC-004
- **execution_layer:** integration
- **type:** positive, negative
- **preconditions:** Status row with `running` 1. Pipeline stub completes (case A) or raises (case B).
- **steps:**
  1. Run the worker with the completing stub.
  2. Read the status row.
  3. Run the worker with the raising stub; read the status row.
- **expected:** Case A: `running` 0; `finished_at` set; `message` set. Case B: `running` 0 (the flag is cleared even on failure); `finished_at` set; `message` is the failure text; `trace` is written and contains no configured secret value.
- **source_path / locator:** BRD §5 FR-040; §10 NFR-006

## TC-030 — Starting the app does not fetch news

- **rule_ids:** FR-041
- **AC:** —
- **execution_layer:** api
- **type:** positive
- **preconditions:** Source adapters are replaced by spies.
- **steps:**
  1. Start the web application with `flask --app app.main:app run`.
  2. Wait 5 seconds and send `GET /`.
  3. Read the spy call counts.
- **expected:** No source adapter is called at start. The page responds with the stored snapshot only.
- **source_path / locator:** BRD §5 FR-041

## TC-031 — Settings read from .env; no hardcoded secret

- **rule_ids:** FR-042, NFR-001
- **AC:** —
- **execution_layer:** IT
- **type:** positive
- **preconditions:** A test `.env` file with a test database user and a test API key value.
- **steps:**
  1. Load settings from the test `.env` file with no environment overrides.
  2. Read the settings values.
  3. Search the source code for the test values.
- **expected:** Settings hold the values from `.env`. The test values appear in no source file (NFR-001). `.env.example` contains variable names with empty values.
- **source_path / locator:** BRD §5 FR-042; §10 NFR-001; §11

## TC-032 — Status file fallback when the database is unavailable

- **rule_ids:** FR-043
- **AC:** —
- **execution_layer:** IT
- **type:** positive
- **preconditions:** Database connection is set to fail. A local `refresh_status.json` exists (development only).
- **steps:**
  1. Read the refresh status with the database failing.
  2. Read which source the status came from, and check the file was read.
- **expected:** Status is read from `refresh_status.json`.
- **source_path / locator:** BRD §5 FR-043; §7

## TC-033 — Status row created with "Ready" when missing

- **rule_ids:** FR-044
- **AC:** —
- **execution_layer:** integration
- **type:** positive
- **preconditions:** Test database with the migration applied and no status row.
- **steps:**
  1. Run the migration to head.
  2. Read the status row with id 1.
- **expected:** The row exists with `running` 0 and message "Ready".
- **source_path / locator:** BRD §5 FR-044; §7

## TC-034 — Snapshots and status stored in database news_app

- **rule_ids:** FR-044, FR-023
- **AC:** —
- **execution_layer:** integration
- **type:** positive
- **preconditions:** Test database named news_app.
- **steps:**
  1. Run a refresh that saves a snapshot.
  2. Read the snapshot table and the status table in news_app.
- **expected:** Both tables are in news_app; one new snapshot row; status row updated.
- **source_path / locator:** BRD §5 FR-044; §7; §11

## TC-035 — Index page: title, footer, no Insight controls

- **rule_ids:** FR-026, FR-032, FR-033
- **AC:** —
- **execution_layer:** uat
- **type:** positive, negative
- **preconditions:** App running with a stored snapshot. Browser at `http://localhost:5000/`.
- **steps:**
  1. Open `GET /`.
  2. Read the page title and the footer text.
  3. Read the page for any "Insight" control, "UST Relevant" filter, or Insight popup.
  4. Count the news cards.
- **expected:** Title "Latest Tech News". Footer "Copyright 2025 UST" (owner answer, DQ-009). No Insight control, no "UST Relevant" or "News with Insight" filter (negative, FR-033). The grid shows one card per stored article (FR-026).
- **source_path / locator:** BRD §5 FR-026, FR-032, FR-033; §14.1 DQ-009

## TC-036 — Sort control: two options

- **rule_ids:** FR-027
- **AC:** —
- **execution_layer:** uat
- **type:** positive
- **preconditions:** App running with a stored snapshot of at least two articles with different priorities and dates.
- **steps:**
  1. Open `GET /`.
  2. Read the options of the sort control.
  3. Select "Date (Newest to Oldest)".
  4. Read the first card title.
- **expected:** Options are exactly "Priority (High to Low)" and "Date (Newest to Oldest)". After selecting Date, the newest article is first.
- **source_path / locator:** BRD §5 FR-027

## TC-037 — Domain filter: All and five domains

- **rule_ids:** FR-028
- **AC:** AC-013
- **execution_layer:** uat
- **type:** positive, negative
- **preconditions:** Stored snapshot with articles in at least two domains.
- **steps:**
  1. Open `GET /`.
  2. Read the options of the domain filter.
  3. Select "Retail".
  4. Read the visible cards.
- **expected:** Options are "All" and the five domains, nothing else (negative: no sixth option). Selecting Retail shows only Retail articles.
- **source_path / locator:** BRD §5 FR-028; §6.1

## TC-038 — Deal-type filter: six chips with counts; Clear filter

- **rule_ids:** FR-029
- **AC:** AC-014
- **execution_layer:** uat
- **type:** positive
- **preconditions:** Stored snapshot where two articles have "partnerships" and one has "alliances".
- **steps:**
  1. Open `GET /`.
  2. Read the deal chips.
  3. Click the "Partnerships" chip.
  4. Click "Clear filter".
- **expected:** Six chips, each with a count: Partnerships shows 2, Alliances shows 1, the others show their own counts. After clicking Partnerships, only the two partnership articles are shown. Clear filter restores all cards.
- **source_path / locator:** BRD §5 FR-029; §6.3

## TC-039 — Refresh button: message, polling, reload

- **rule_ids:** FR-030
- **AC:** AC-016
- **execution_layer:** uat
- **type:** positive
- **preconditions:** Worker stub that finishes after 2 seconds. App running.
- **steps:**
  1. Open `GET /` and click "Refresh News".
  2. Read the notice text.
  3. Wait for the status to show finished.
- **expected:** Notice reads "Refreshing news - this may take a while..." while running. The page polls `GET /api/refresh/status` and reloads when `running` is false.
- **source_path / locator:** BRD §5 FR-030; §10

## TC-040 — Empty state: "No news found"

- **rule_ids:** FR-031
- **AC:** AC-015
- **execution_layer:** uat
- **type:** positive
- **preconditions:** Snapshot table with no rows.
- **steps:**
  1. Open `GET /`.
  2. Read the page.
- **expected:** The text "No news found" is shown and no cards are shown.
- **source_path / locator:** BRD §5 FR-031; §10

## TC-041 — Load failure shows the connection message

- **rule_ids:** NFR-007
- **AC:** —
- **execution_layer:** uat
- **type:** negative
- **preconditions:** `GET /api/news` is made to fail (returns an error).
- **steps:**
  1. Open `GET /`.
  2. Read the notice.
- **expected:** The notice reads "No news loaded, check your connection" (owner copy, BRD §14.1 DQ-014). The grid shows no cards.
- **source_path / locator:** BRD §10 NFR-007; §14.1 DQ-014

## TC-043 — Secrets masked in traces and logs

- **rule_ids:** NFR-006
- **AC:** —
- **execution_layer:** IT
- **type:** negative
- **preconditions:** A failure is raised with a message that contains a configured secret value.
- **steps:**
  1. Trigger the failure in the worker.
  2. Read the stored trace and the log output.
- **expected:** The secret value does not appear; it is replaced by `***` (negative: no secret in the trace or log).
- **source_path / locator:** BRD §10 NFR-006; §14.1 DQ-014

## TC-044 — Backend line coverage gate at 70%

- **rule_ids:** NFR-008
- **AC:** AC-021
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Coverage report from the API test run.
- **steps:**
  1. Read the total line coverage from the report.
  2. Compare with the configured minimum `quality_gates.api_unit_line_coverage_min` (0.70).
- **expected:** Coverage at or above 70% passes the gate (AC-021). Coverage below 70% fails the gate (negative).
- **source_path / locator:** BRD §10 NFR-008; §14.1 DQ-010; `.claude/config.yaml`

## TC-045 — Parity check: reported only against a complete baseline

- **rule_ids:** NFR-005
- **AC:** AC-023
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Test copies of `evals/product/baseline.md`: one complete, one missing, one with blank values.
- **steps:**
  1. Run the parity check with the complete file and a current run.
  2. Run the parity check with the missing file.
  3. Run the parity check with the blank-values file.
- **expected:** Step 1: counts and shares within ±25% and refresh time at most 1.5× the baseline are reported as passed or failed. Steps 2 and 3: the check is reported as "not evaluated", never as passed (negative, AC-023).
- **source_path / locator:** BRD §10 NFR-005; §15 AC-023; §14.1 DQ-019

## TC-045b — Parity baseline values recorded by the owner

- **rule_ids:** NFR-005
- **AC:** AC-023
- **execution_layer:** blocked
- **type:** positive
- **preconditions:** Owner has not yet run the existing app three times on one day and recorded the averages in `evals/product/baseline.md`.
- **steps:**
  1. Owner runs the existing app three times on one day.
  2. Owner records the averages in `evals/product/baseline.md`.
- **expected:** The file holds averages for total articles, articles per domain (5), articles per deal type (6), duplicate-removal share, and refresh duration. Blocked until the owner records them; no value is invented here.
- **source_path / locator:** BRD §14.1 DQ-019

## TC-046 — HTML stripped from feed summaries

- **rule_ids:** NFR-009
- **AC:** —
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Feed item summary "<p>Bank <b>expands</b></p><script>x()</script>".
- **steps:**
  1. Run the summary cleaning step on the summary.
  2. Read the stored summary.
- **expected:** Stored summary is "Bank expands" with the script removed (positive). No HTML tag and no script text remain (negative).
- **source_path / locator:** BRD §10 NFR-009; §14.1 DQ-014

## TC-047 — No authentication in this build (recorded risk)

- **rule_ids:** NFR-010, FR-035
- **AC:** —
- **execution_layer:** api
- **type:** positive
- **preconditions:** Application running with no credentials supplied.
- **steps:**
  1. Send `GET /api/news` with no authorisation header.
  2. Send `POST /api/refresh` with no authorisation header.
- **expected:** Both requests are answered without any credential check (recorded risk, owner decision DQ-020). This test records the risk; it does not approve an authentication design.
- **source_path / locator:** BRD §10 NFR-010; §14.1 DQ-020

## TC-048 — Prompts stored verbatim as templates

- **rule_ids:** FR-046
- **AC:** AC-024
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Owner file `artifacts/intake/supporting/llm-prompts-workflow.md` and the templates in `modules/api/app/prompts/`.
- **steps:**
  1. For each template, check that its text appears byte for byte in the owner file.
  2. Change one character in a template copy in a temporary folder and repeat the check.
- **expected:** Step 1: all nine templates match (AC-024). Step 2: the check fails for the changed copy (negative, FR-046: code shall not edit prompt text).
- **source_path / locator:** BRD §5 FR-046; §17; AC-024

## TC-049 — Relevance judged for an IT services company (stages 3 and 5)

- **rule_ids:** FR-048
- **AC:** —
- **execution_layer:** IT
- **type:** positive
- **preconditions:** Model client is a stub that records the system message.
- **steps:**
  1. Run stage 3 and record the system message.
  2. Run stage 5 and record the system message.
- **expected:** Both system messages are the owner text for stages 3 and 5, which state the company type (IT services company) and the relevance criteria.
- **source_path / locator:** BRD §5 FR-048; §17

## TC-050 — LLM calls use supported parameters per stage

- **rule_ids:** FR-047
- **AC:** —
- **execution_layer:** IT
- **type:** positive, negative
- **preconditions:** Model client is a stub that records the request.
- **steps:**
  1. Run stage 3, stage 5, stage 9 and stage 10 with the stub.
  2. Read the recorded temperature and token limit for each call.
  3. Make the stub reject a parameter and run stage 5.
- **expected:** Stage 3: temperature 0, max tokens 150. Stage 5: 0 and 300. Stage 9: 0 and 800. Stage 10: 0.2 and no limit. The model name is taken from `AZURE_OPENAI_CHAT_DEPLOYMENT`; no model name is written in code (FR-047). Step 3: the request is not sent with the rejected parameter (negative).
- **source_path / locator:** BRD §5 FR-047; §17
