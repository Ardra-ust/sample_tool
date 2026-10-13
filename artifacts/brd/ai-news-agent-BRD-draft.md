# Business Requirements Document — AI News Agent

> Status: **Draft — Pending Domain Review** (v0.2). v0.1 was accepted by Ardra Arun on 2026-10-13. v0.2 adds the LLM stage specification (§17) and FR-046 to FR-048, and needs re-acceptance before it is treated as current.
> Source of truth: `artifacts/intake/supporting/ai-news-agent-notes.md`. `§` references below point to that file unless marked otherwise.
> Open items are in §14 as DQ-xxx. Nothing here is invented: where the notes are silent, the item is a DQ, not a requirement.

| Field | Value |
|-------|-------|
| **BRD ID** | BRD-ai-news-agent |
| **Version** | 0.2 |
| **Date** | 2026-10-13 |
| **Author** | requirements-agent |
| **Status** | Draft — Pending Domain Review (v0.2; re-acceptance needed; v0.1 accepted 2026-10-13) |
| **Module / context** | `ai-news-agent` / `news-intelligence` |
| **Sources** | `artifacts/intake/supporting/ai-news-agent-notes.md` (primary); intake notes `artifacts/intake/2026-10-13-intake-notes.md` |

---

## 1. Purpose

- **Problem statement:** Teams must follow technology and industry news across Healthcare, Retail, Banking and Financial Services, Technology & Communication, and Wealth & Asset Management. News is spread over 42 RSS feeds, 25 Google News searches, SearchAPI.io and Tavily, mixed with consumer noise and duplicates. Deal activity (M&A, partnerships, JVs, strategic investments, spin-offs, alliances) is hard to spot and rank manually. (RESOLVED DQ-010.)
- **Business outcomes:** (1) One page of fresh, deduplicated, relevant news. (2) Each article has one of five domains and zero or more of six deal types. (3) 1–5 priority ranking with deal and Google News boosts. (4) Filter by domain and deal type, sort by priority or date, manual refresh. (5) Rolling history up to 400 articles, none older than 15 days. (RESOLVED DQ-010.)
- **Success metrics:** (a) All four source types run each refresh, and one failing source does not stop it. (b) Every article has a domain ("Unknown" only on AI failure) and a priority 1–5. (c) No article is older than 15 days, and there are at most 400 articles. (d) No saved pair meets the dedup thresholds: embedding similarity 0.75 for new articles, 0.84 against stored articles, 0.82 after the merge; title 0.92. (e) A second refresh while one is running returns "running", and the flag clears at job end or after 70 minutes. (f) `GET /health` returns OK. (g) Backend line coverage ≥ 70%. (h) Parity with the baseline measurements: article count, domain and deal-type mix, duplicate-removal share and refresh time, within +/-25% on counts and shares and at most 1.5x on refresh time (DQ-019). Baseline values are recorded in `evals/product/baseline.md`. (RESOLVED DQ-010, DQ-019.)

## 2. Scope / out of scope

| In scope | Out of scope |
|----------|--------------|
| Fetching news from RSS feeds, Google News RSS, SearchAPI.io and Tavily (§3) | UST relevance, UST alignment score, UST offerings catalogue, any RAG over it (§2) |
| Noise filtering, LLM relevance gate, duplicate removal, 15-day freshness, deal-type tagging, domain and priority classification, sorting (§5) | Insight generation: insight paragraphs, "News with Insight", "UST Relevant" filters, Insight tab/dashboard (§2) |
| Saving each refresh as a MySQL snapshot (§7) | "Important" Yes/No classification, bucket classification, keyword extraction (§2) |
| Filterable news grid, manual refresh with status polling, health endpoint (§8–§10) | Trend summaries, including all GDELT calls; GDELT is not a news source here (§2, §3) |
| | Opportunity themes, "where to act first", web-search-based insight calls (§2) |
| | `important_news_output.txt` export and `classification_logs/` folder (§2) |

## 3. Actors and systems

| Actor | Role | Systems used |
|-------|------|--------------|
| Viewer | Browses, sorts and filters the news grid (§10) | Web UI (Flask Jinja templates) |
| Refresh user | Presses Refresh News and watches progress (§10) | Web UI, `POST /api/refresh`, `GET /api/refresh/status` (§8) |
| Refresh worker | Runs the processing pipeline outside the request (§9) | `refresh_worker.py` (subprocess) |
| News sources | Supply articles (§3) | RSS feeds, Google News RSS, SearchAPI.io, Tavily |
| Azure OpenAI | Filtering, tagging, classification, embeddings (§5) | Azure OpenAI only, one resource for chat and embeddings (RESOLVED DQ-001) |
| Database | Stores snapshots and refresh status (§7) | MySQL, database `news_app` |
| Azure WebJob (optional) | Alternative trigger for the worker (§9) | Azure (DQ-012) |

## 4. Glossary

| Term | Definition | Source |
|------|------------|--------|
| Snapshot | One JSON row in `new_data` holding the full sorted article list for one refresh | §7 |
| Domain | One of five fixed categories an article belongs to | §6.1 |
| Deal type | One of six categories an article can carry, zero or more | §6.3 |
| Priority | Integer 1–5, higher is more important, with boosts | §6.2 |
| Consumer-noise filter | Keyword filter using block and allow words | §5 step 2 |
| Relevance gate | LLM filter that drops only clear noise | §5 step 5 |
| Freshness window | 15 days; older articles are dropped | §5 step 8 |
| Refresh lock | Atomic database flag that allows one refresh at a time | §8 |
| Stale lock | A lock held for more than 70 minutes, cleared automatically (RESOLVED DQ-018; notes say 20) | §7 |

## 5. Functional requirements (FR-xxx)

Priority is **P0 for all rows**, as confirmed by the owner (RESOLVED DQ-013).

| FR ID | Statement | Priority | source_path | source_locator |
|-------|-----------|----------|-------------|----------------|
| FR-001 | The system shall fetch the 42 RSS feeds listed in the notes on each refresh, taking the first 7 entries per feed, except AnalyticsIndiaMag, which takes up to 50 entries. | P0 (confirmed, DQ-013) | artifacts/intake/supporting/ai-news-agent-notes.md | §3.1 |
| FR-002 | The system shall keep only English-language articles from RSS feeds. | P0 (confirmed, DQ-013) | (same) | §3.1 |
| FR-003 | The system shall cut RSS summaries to 400 characters, except AnalyticsIndiaMag, whose summaries are cut to 1500 characters. | P0 (confirmed, DQ-013) | (same) | §3.1 |
| FR-004 | The system shall fetch each of the 25 curated Google News RSS searches on each refresh, using the form `https://news.google.com/rss/search?q=<query> when:7d` with the query URL-encoded. | P0 (confirmed, DQ-013) | (same) | §3.2 |
| FR-005 | The system shall take up to 20 entries from each Google News feed whose name contains `MnA`, `MnAPartnership`, `Partnership`, `Alliance`, `Alliances` or `Funding`, and 7 entries from every other Google News feed. | P0 (confirmed, DQ-013) | (same) | §3.2 |
| FR-006 | The system shall decode Google News wrapper links to the publisher URL before storing an article. | P0 (confirmed, DQ-013) | (same) | §3.2 |
| FR-007 | The system shall call SearchAPI.io with engine `google_news`, query `technology`, 15 results and location `India`, and shall use both `top_stories` and `organic_results`. | P0 (confirmed, DQ-013) | (same) | §3.3 |
| FR-008 | The system shall run one Tavily search per refresh, with a maximum of 10 results, answer and raw content enabled, and the query defined in the notes with the current date. | P0 (confirmed, DQ-013) | (same) | §3.4 |
| FR-009 | The system shall keep only Tavily results that have a valid published date, a link and English text. | P0 (confirmed, DQ-013) | (same) | §3.4 |
| FR-010 | The system shall fetch from all four source types on every refresh. If one source fails, the failure is logged and skipped, and the run continues (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §3, §5 step 1 |
| FR-011 | The system shall mark an article as consumer noise when its lowercased title plus summary contains at least one block word as a substring and no allow word as a substring, using the lists in §5 step 2. Known side effect: "POS" matches "position" and "possible" (RESOLVED DQ-007). | P0 (confirmed, DQ-013) | (same) | §5 step 2 (resolved DQ-006, DQ-007) |
| FR-012 | The system shall re-check noise-filtered titles with the LLM in batches of 6 at temperature 0, restoring titles relevant to enterprise technology, cloud, AI, data, deals, regulation and digital transformation, and shall not restore any title containing a forbidden word (BR-014). If the LLM call fails, the batch is not restored (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 3 (resolved DQ-006) |
| FR-013 | The system shall remove duplicate articles by link, then by title, and shall keep at most 500 articles. | P0 (confirmed, DQ-013) | (same) | §5 step 4 |
| FR-014 | The system shall run an LLM relevance gate in batches of 8 at temperature 0, dropping only the clear noise described in BR-017 and force-keeping any article whose lowercased title plus summary contains a keyword (substring match) from this list: acqui, merger, merge, m&a, buyout, takeover, divest, spin-off, spinoff, spin off, joint venture, " jv ", partnership, partner with, alliance, strategic investment, invests, investment, funding, raises, raised, series a, series b, series c, seed round, venture, ipo, stake, valuation, unicorn, cloud, azure, aws, gcp, data platform, data center, datacenter, modernization, modernisation, migration, digital transformation, genai, generative ai, llm, ai agent, agentic, machine learning, cybersecurity, cyber security, ransomware, breach, zero trust, core banking, ehr, emr, erp, saas, platform, automation, contract, deal, gcc, outsourc, managed services, integration, infrastructure, chip, semiconductor, analytics, api, accenture, infosys, tcs, cognizant, wipro, capgemini, mphasis, ltimindtree, hcltech, tech mahindra, fractal, ust. The entry "ust" matches substrings such as "just", "must" and "industry"; this is recorded as known behaviour for parity and is not a UST feature (RESOLVED DQ-008). If the relevance-gate LLM call fails, the batch is kept (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 5 (resolved DQ-008) |
| FR-015 | The system shall keep an entire batch when the relevance-gate LLM call fails. | P0 (confirmed, DQ-013) | (same) | §5 step 5 |
| FR-016 | The system shall remove near-duplicate articles using embedding similarity at the threshold in BR-011, then run a title-similarity pass as defined in BR-011. If the embedding dedup function fails, the list is returned unchanged and neither embedding nor title dedup runs (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 6 (resolved DQ-001, DQ-002) |
| FR-017 | The system shall load the latest 3 snapshots from `new_data`, drop each new article whose embedding similarity to any stored article is at or above the threshold in BR-011, merge the remaining new articles with the articles of the most recent snapshot only, and run near-duplicate removal again at the threshold in BR-011. | P0 (confirmed, DQ-013) | (same) | §5 step 7 |
| FR-018 | If the database comparison in FR-017 fails (embedding or read), the system shall skip database-duplicate removal. The latest snapshot is still merged if it loads. If the history cannot load, only the new articles are kept (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 7 |
| FR-019 | The system shall drop articles older than 15 days, set missing or invalid dates to the current time, and keep the latest 400 articles. | P0 (confirmed, DQ-013) | (same) | §5 step 8; §6.2 |
| FR-020 | The system shall assign zero, one or several deal types to each article using the LLM in batches of 8 at temperature 0, skipping articles that already have deal types. If the tagging call fails, deal_categories is [] and is_deal_news is false (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 9; §6.3 |
| FR-021 | The system shall assign each article one domain, a priority and a refined summary using the LLM at temperature 0.2 with 8 parallel workers, skipping articles loaded from the database that already have a domain and priority. If the domain and priority call fails, domain is "Unknown", priority is 3 plus boosts (capped at 5), and the summary is unchanged (RESOLVED DQ-005, DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 10 |
| FR-022 | The system shall sort articles by priority from high to low, then by published date, newest first. | P0 (confirmed, DQ-013) | (same) | §5 step 11; BR-018 |
| FR-023 | The system shall save the full sorted list as one JSON snapshot row in `new_data` on each refresh. If nothing is fetched, the run ends with an error, the running flag is cleared, and no empty snapshot is saved. This is a deliberate change from the existing app (RESOLVED DQ-018). | P0 (confirmed, DQ-013) | (same) | §5 step 12; §7 |
| FR-024 | The system shall store each article with the fields: title, link, source, published (IST, `YYYY-MM-DD HH:MM:SS`), summary, domain, priority, deal_categories, is_deal_news, is_google_news, published_at. `is_deal_news` is true when deal_categories is a non-empty list, and false otherwise (including when the tagging call fails). `published_at` is a copy of `published` (IST `YYYY-MM-DD HH:MM:SS`, or `YYYY-MM-DD` if only a date is known) and is used for the 15-day cut-off and for sorting. If the date is missing or cannot be parsed, both `published` and `published_at` are set to the current time (RESOLVED DQ-017). | P0 (confirmed, DQ-013) | (same) | §4 (resolved DQ-017) |
| FR-025 | The system shall convert relative dates (for example "2 hours ago", "yesterday") to absolute dates in IST (UTC+5:30), and shall remove date and time fragments from summaries. | P0 (confirmed, DQ-013) | (same) | §4 |
| FR-026 | The system shall show the latest snapshot on the index page as a grid of news cards. | P0 (confirmed, DQ-013) | (same) | §8 `/`; §10 |
| FR-027 | The system shall provide a sort control with two options: Priority (High to Low) and Date (Newest to Oldest). | P0 (confirmed, DQ-013) | (same) | §10 |
| FR-028 | The system shall provide a domain filter with "All" and the five domains, with a select-domain popup. | P0 (confirmed, DQ-013) | (same) | §10 |
| FR-029 | The system shall provide a deal-type filter that shows a count per deal type as colour-coded chips, and a Clear filter control. | P0 (confirmed, DQ-013) | (same) | §10; §6.3 (colours) |
| FR-030 | The system shall show a Refresh News button which, while a refresh runs, displays "Refreshing news - this may take a while..." and polls `/api/refresh/status` until the refresh finishes, then reloads the page. | P0 (confirmed, DQ-013) | (same) | §10; §8 |
| FR-031 | The system shall show a "No news found" empty state when the snapshot has no articles. | P0 (confirmed, DQ-013) | (same) | §10 |
| FR-032 | The system shall show the page title "Latest Tech News" with a logo, and a footer reading "Copyright 2025 UST" (RESOLVED DQ-009). | P0 (confirmed, DQ-013) | (same) | §10 |
| FR-033 | The system shall not show the "UST Relevant" or "News with Insight" filters, or the Insight popup. | P0 (confirmed, DQ-013) | (same) | §10; §2 |
| FR-034 | The system shall serve `GET /api/news` with the latest snapshot as `{count, results, fetched_at}` in IST, returning `{count: 0, results: []}` when no snapshot exists, with no-cache headers. | P0 (confirmed, DQ-013) | (same) | §8 |
| FR-035 | The system shall handle `POST /api/refresh` by returning `status: running` when a refresh is in progress; otherwise it shall take the atomic lock in BR-015, start the refresh job, and return `status: started`. | P0 (confirmed, DQ-013) | (same) | §8 |
| FR-036 | The system shall return HTTP 500 from `POST /api/refresh` when starting the refresh fails, and shall record the failure. | P0 (confirmed, DQ-013) | (same) | §8 |
| FR-037 | The system shall serve `GET /api/refresh/status` with `{running, started_at, finished_at, message, last_run_type}` and no-cache headers. | P0 (confirmed, DQ-013) | (same) | §8 |
| FR-038 | The system shall serve `GET /health`, which returns OK. The notes state this route does not exist in the current app and must be added. | P0 (confirmed, DQ-013) | (same) | §8 |
| FR-039 | The system shall run the pipeline in a separate worker script, `refresh_worker.py`, started as a subprocess, unless an Azure WebJob trigger URL is configured, in which case it shall call that URL instead (RESOLVED DQ-012: the WebJob is optional, and is called only when `AZURE_WEBJOB_TRIGGER_URL` is set). | P0 (confirmed, DQ-013) | (same) | §9; §11 |
| FR-040 | The worker shall clear the running flag when the pipeline ends and shall write `finished_at` and either a completion message or the error trace. | P0 (confirmed, DQ-013) | (same) | §9 |
| FR-041 | The system shall start only the web server when `app.py` runs, and shall not fetch news at startup. The UI shall show the snapshot already stored in MySQL. | P0 (confirmed, DQ-013) | (same) | §9 |
| FR-042 | The system shall read all secrets and connection settings from `.env` through python-dotenv, shall not hardcode them, and shall provide `.env.example` with empty values. | P0 (confirmed, DQ-013) | (same) | §11 |
| FR-043 | The system shall store refresh status in MySQL, create the status row automatically with a "Ready" message when it is missing, and fall back to a local `refresh_status.json` only when the database is unavailable (development only). | P0 (confirmed, DQ-013) | (same) | §7 |
| FR-044 | The system shall store snapshots and refresh status in the MySQL database `news_app`. | P0 (confirmed, DQ-013) | (same) | §7; §11 |
| FR-045 | The refresh worker shall run the pipeline stages in exactly this order: (1) fetch from all four source types; (2) consumer-noise keyword filter; (3) LLM re-check of noise-filtered titles; (4) dedupe by link then title, max 500; (5) LLM relevance gate; (6) embedding near-duplicate removal plus title pass; (7) database comparison, merge with latest snapshot, second near-duplicate removal; (8) freshness filter (15 days, max 400); (9) deal-type tagging; (10) domain, priority and refined summary (priority boosts need deal types from step 9); (11) sort; (12) save snapshot. A stage shall not start before the previous one ends. | P0 (confirmed, DQ-013) | (same) | §5 "order matters" |
| FR-046 | The system shall store each LLM prompt from the owner file `artifacts/intake/supporting/llm-prompts-workflow.md` verbatim as a template under `modules/api/app/prompts/`. Code shall not rewrite, shorten or edit prompt text. | P0 (confirmed, DQ-013) | (same) | §17; llm-prompts-workflow.md "How to use this file" |
| FR-047 | The system shall call the chat deployment named by `AZURE_OPENAI_CHAT_DEPLOYMENT` for the LLM stages, with the batch size, temperature and token limit listed in §17 for each stage. It shall not send a parameter that the deployment rejects. | P0 (confirmed, DQ-013) | (same) | §17; llm-prompts-workflow.md "How to use this file" |
| FR-048 | The relevance decisions of stages 3 and 5 shall be judged for an IT services company, as the owner's prompts state. | P0 (confirmed, DQ-013) | (same) | §17; llm-prompts-workflow.md Stage 3 and Stage 5 |

## 6. Business rules (BR-xxx)

| BR ID | Statement | Priority | source_path | source_locator |
|-------|-----------|----------|-------------|----------------|
| BR-001 | The system shall use exactly five domains: Healthcare; Retail; Banking and Financial Services; Technology & Communication; Wealth & Asset Management. | P0 (confirmed, DQ-013) | artifacts/intake/supporting/ai-news-agent-notes.md | §6.1 |
| BR-002 | Each article shall have exactly one domain, classified by these signals: Healthcare (hospitals, providers, insurers, medical tech, telehealth, EHRs, clinical systems); Retail (retail brands, e-commerce, stores, supply chain, POS, inventory, customer experience); Banking and Financial Services (banks, payments, lending, insurance, KYC/AML, fraud, core banking, fintech infrastructure); Technology & Communication (tech vendors, cloud/AI platforms, telecom, networking, chips, cybersecurity, software, hardware); Wealth & Asset Management (investment management, asset management, portfolio platforms, trading, brokerage, advisory, robo-advisory). | P0 (confirmed, DQ-013) | (same) | §6.1 |
| BR-003 | When both Banking and Financial Services and Wealth & Asset Management signals appear, the article shall be classified as Wealth & Asset Management. | P0 (confirmed, DQ-013) | (same) | §6.1 |
| BR-004 | The system shall use six deal types: Mergers & Acquisitions (`mergers_acquisitions`, green); Partnerships (`partnerships`, blue); Joint Ventures (`joint_ventures`, violet); Strategic Investments (`strategic_investments`, yellow); Spin-offs (`spin_offs_divestitures`, amber); Alliances (`alliances`, red). | P0 (confirmed, DQ-013) | (same) | §6.3 |
| BR-005 | Deal-type core tests: Mergers & Acquisitions: two companies combine, or one buys a controlling stake, including the buyer's side of a divestiture. Partnerships: a specific two-party deal with no new company and no equity change. Joint Ventures: a new, separate, jointly owned entity is created. Strategic Investments: a minority, non-controlling stake where the investee stays independent. Spin-offs: the seller's side, a unit is spun off or sold. Alliances: a formal arrangement among three or more organisations around a shared goal or standard. | P0 (confirmed, DQ-013) | (same) | §6.3 |
| BR-006 | Deal types shall be judged by meaning, not keywords. A passing mention of "partner" does not count. A generic funding round with no strategic angle does not count. When unsure, the category shall be left out. The deal must be the article's main subject. | P0 (confirmed, DQ-013) | (same) | §5 step 9; §6.3 |
| BR-007 | Priority shall be an integer from 1 to 5, where higher is more important. 5: strategic or market-shifting. 4: major operational or product advancement. 3: emerging opportunity or competitive signal. 2: incremental improvement or internal optimisation. 1: thought leadership, commentary or cultural context. | P0 (confirmed, DQ-013) | (same) | §6.2 |
| BR-008 | The domain shall be set to "Unknown" only when the AI classification call fails or returns no domain. In that case priority is 3 plus boosts, capped at 5. Articles that already have a domain and priority are not re-classified (RESOLVED DQ-005). | P0 (confirmed, DQ-013) | (same) | §6.2 |
| BR-009 | An article from a Google News RSS feed shall receive a +1 priority boost. | P0 (confirmed, DQ-013) | (same) | §6.2; §3.2 |
| BR-010 | An article with any deal type shall receive a +1 priority boost. The priority after boosts shall not exceed 5. | P0 (confirmed, DQ-013) | (same) | §6.2 |
| BR-011 | Similarity thresholds: near-duplicate removal on new articles, cosine similarity 0.75 or higher counts as a duplicate; database comparison, similarity 0.84 or higher to any stored article drops the new article; the second near-duplicate removal after the database merge uses 0.82. Title pass (RESOLVED DQ-002): lowercase both titles and keep only letters and digits. Two titles are duplicates when their length difference is less than 10 AND `difflib.SequenceMatcher` ratio is 0.92 or higher. The title pass runs inside the embedding dedup function. | P0 (confirmed, DQ-013) | (same) | §5 steps 6–7 |
| BR-012 | Articles older than 15 days shall be dropped. | P0 (confirmed, DQ-013) | (same) | §5 step 8 |
| BR-013 | At most 500 articles shall be kept after de-duplication (step 4), and at most 400 after the freshness filter (step 8). | P0 (confirmed, DQ-013) | (same) | §5 steps 4, 8 |
| BR-014 | Titles containing any of these words shall never be restored by the LLM re-check: christmas, festive, new year, buy, discount, deal, offer, gift, sale. The check applies to the title only. A word appearing only in the summary does not block restoration (RESOLVED DQ-006). | P0 (confirmed, DQ-013) | (same) | §5 step 3 (resolved DQ-006) |
| BR-015 | A refresh shall take an atomic database lock (`UPDATE ... WHERE running=0`). Only one refresh shall run at a time. | P0 (confirmed, DQ-013) | (same) | §8 |
| BR-016 | When `running` has been 1 for more than 70 minutes, the system shall clear it automatically with a message that the worker likely died. The limit is configurable as `REFRESH_STALE_MINUTES`. The owner answer (DQ-018) sets 70 minutes; the notes §7 and §11 say 20 minutes. This departure is recorded in §14.1. | P0 (confirmed, DQ-013) | (same) | §7; §11; resolved DQ-018 |
| BR-017 | The relevance gate shall drop only clear noise: consumer gadgets and shopping, entertainment, sports and lifestyle, pure clinical or drug results with no tech, data or deal angle, personal-finance tips, and pure opinion. Everything else shall be kept. | P0 (confirmed, DQ-013) | (same) | §5 step 5 |
| BR-018 | Articles shall be sorted by priority from high to low, then by published date, newest first. | P0 (confirmed, DQ-013) | (same) | §5 step 11 |

## 7. Data

| Entity | Description | Source |
|--------|-------------|--------|
| `new_data` | One row per refresh. Columns: `id` (auto), `news` (JSON text of the full article list), `updated_at` (set to NOW() on insert). | §7 |
| `refresh_status` (name configurable via `REFRESH_STATUS_TABLE`) | One row, `id` = 1. Columns: `running` (0/1), `started_at`, `finished_at`, `message`, `last_run_type`, `trace`, `updated_at`. Created automatically with "Ready" if missing. | §7, §11 |
| Article | Fields listed in FR-024. | §4 |
| Local status file | `refresh_status.json`, used only when the database is unavailable (development only). | §7 |

## 8. Integrations

| System | Direction | Protocol | Notes |
|--------|-----------|----------|-------|
| RSS feeds (42) | inbound | HTTP RSS | §3.1 |
| Google News RSS (25 searches) | inbound | HTTP RSS; wrapper links decoded with `googlenewsdecoder` | §3.2 |
| SearchAPI.io | inbound | HTTP GET, REST/JSON, API key from `.env` | §3.3 |
| Tavily search | inbound | Tavily search API, API key from `.env` | §3.4 |
| Azure OpenAI chat | outbound | Chat model is whatever the deployment named by `AZURE_OPENAI_CHAT_DEPLOYMENT` is set to (DQ-A3, resolved). No Claude, no Groq. | DQ-001, DQ-A3 |
| Azure OpenAI embeddings | outbound | `text-embedding-3-small`, deployment named by `AZURE_OPENAI_EMBED_DEPLOYMENT`. | DQ-001 |
| MySQL (`news_app`) | inbound and outbound | MySQL connection, settings from `.env` | §7, §11 |
| Azure WebJob trigger (optional) | outbound | HTTP call, credentials from `.env` | §9, §11; DQ-012 |

## 9. UX / journeys

| Journey | Actor | Steps summary | UX source |
|---------|-------|---------------|-----------|
| J-01 Browse news | Viewer | Opens the index page; sees the grid of cards from the latest snapshot; sees the title, logo and footer | §10 |
| J-02 Sort | Viewer | Chooses Priority (High to Low) or Date (Newest to Oldest) | §10 |
| J-03 Filter | Viewer | Filters by domain (All or one of five) and by deal type (count per type; Clear filter) | §10 |
| J-04 Refresh | Refresh user | Presses Refresh News; sees the running message; the page polls status and reloads when finished | §10; §8 |
| J-05 Empty | Viewer | Sees "No news found" when the snapshot has no articles | §10 |

## 10. NFRs (security, audit, performance)

| NFR ID | Category | Requirement | Target | Source |
|--------|----------|-------------|--------|--------|
| NFR-001 | security | Secrets and connection settings are read from `.env`; none is hardcoded in source; `.env.example` has empty values | none hardcoded | §11 |
| NFR-002 | caching | Status and snapshot endpoints send no-cache headers | per FR-034, FR-037 | §8 |
| NFR-003 | time | Published dates are shown in IST (UTC+5:30) | IST | §4 |
| NFR-004 | concurrency | A refresh lock is atomic; stale locks clear after 70 minutes | 70 min (RESOLVED DQ-018; notes say 20) | §7, §8 |
| NFR-005 | performance / availability | No availability or latency targets are required. The only performance check is refresh-time parity. | None required (RESOLVED DQ-015); refresh-time parity is DQ-004 | §12 |
| NFR-006 | data protection (kit policy) | Mask PII and secrets in logs, traces and test artefacts | Per kit rule 02; not in notes | `.claude/rules/02-security-and-compliance.md` (adopted by owner; RESOLVED DQ-014) |
| NFR-007 | UX states (kit policy) | Loading, empty and error states for every user journey | Per kit rule 04; only the empty state is in notes | `.claude/rules/04-frontend.md` (adopted by owner; RESOLVED DQ-014) |
| NFR-008 | quality (owner answer) | Backend line coverage | ≥ 70% | Owner answer to DQ-010; `.claude/config.yaml` `quality_gates.api_unit_line_coverage_min` (RESOLVED DQ-010) |
| NFR-009 | security (owner answer) | Sanitise external text before storing it: strip HTML from feed summaries | Applies to all fetched text | Owner answer to DQ-014 (RESOLVED DQ-014) |
| NFR-010 | security | No authentication is implemented in this build; the risk is recorded in DQ-020 | None (no authentication) | DQ-020 answer |

## 11. Assumptions

| ID | Assumption | Owner |
|----|------------|-------|
| ASSUMPTION-STACK-001 | Backend is Python 3.11+ with Flask; the UI is Flask Jinja templates with HTML/JS; the database is MySQL. Recorded from the user's command argument and `.claude/config.yaml` / `.claude/rules/techstack.md`. Not a business requirement. | Owner (pending) |
| ASSUMPTION-STACK-002 | Flask serves the Jinja UI from the same process as the API, so there is no separate UI server. | Owner (pending) |
| ASSUMPTION-SCOPE-001 | The "transcript" input is the notes file, because no meeting transcript was supplied. | Owner (pending) |

Assumptions are pending approval. They do not make this BRD Ready (rule 22).

## 12. Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|------------|--------|------------|
| RISK-001 | The LLM provider choice changes the duplicate-removal design, because the notes' Claude option has no embeddings. | Medium | High | Resolved by DQ-001: Azure OpenAI only, with embeddings in the same resource |
| RISK-002 | Block word `deal` may drop real deal news before the deal-type step. | High | High | DQ-006 keeps `deal` as a block word; the restore check applies to titles only. Residual risk accepted by the owner answer. |
| RISK-003 | Feed, API or LLM failures have no defined behaviour beyond two fallbacks (`[INFERRED]`, see DQ-018). | Medium | Medium | Resolved by DQ-018: failure behaviour defined per component |
| RISK-004 | The relevance gate's force-keep list names `UST`, which may conflict with the out-of-scope UST relevance (see DQ-008). | Medium | Medium | Resolved by DQ-008: recorded as known substring behaviour, not a UST feature |

## 13. Discussion coverage matrix

Every section of the notes is mapped below. Status: **captured** means it is in §5–§11 with a source. **open** means it is a DQ in §14.

| Notes section | Topic | BRD section | ID(s) | Status |
|---------------|-------|-------------|-------|--------|
| §1 | Purpose | §1 | — | captured |
| §2 | Out of scope | §2 | — | captured |
| §3.1 | RSS sources | §5 | FR-001–003 | captured (feed list issues DQ-011) |
| §3.2 | Google News RSS | §5 | FR-004–006, BR-009 | captured |
| §3.3 | SearchAPI.io | §5 | FR-007 | captured |
| §3.4 | Tavily | §5 | FR-008–009 | captured |
| §4 | Article fields | §5 | FR-024–025 | captured (DQ-017) |
| §5 steps 1–4 | Fetch, noise filter, LLM re-check, de-dupe | §5 | FR-010–013 | captured (DQ-006, DQ-007) |
| §5 step 5 | Relevance gate | §5 | FR-014–015, BR-017 | captured (DQ-008) |
| §5 steps 6–7 | Duplicate removal, database comparison | §5 | FR-016–018, BR-011 | captured (DQ-001, DQ-002) |
| §5 steps 8–12 | Freshness, tagging, classification, sort, save | §5 | FR-019–023, BR-012–014, BR-018 | captured |
| §6.1 | Domains | §6 | BR-001–003 | captured (DQ-005) |
| §6.2 | Priority and boosts | §6 | BR-007–010 | captured (DQ-005) |
| §6.3 | Deal types | §6 | BR-004–006 | captured |
| §7 | Storage | §7 | FR-043–044, BR-015–016 | captured (DQ-016) |
| §8 | Routes | §5 | FR-034–038 | captured |
| §9 | Refresh job | §5 | FR-039–041 | captured (DQ-012) |
| §10 | UI | §5, §9 | FR-026–033, J-01–J-05 | captured (DQ-009) |
| §11 | Configuration and secrets | §5 | FR-042, NFR-001 | captured (out-of-scope items in §11 excluded) |
| §12 | Decisions (`[FILL]`) | §14 | DQ-001, DQ-003, DQ-004 (resolved; method decisions) | resolved |
| §13 | Acceptance checks | §15 | AC-001–022 | captured (DQ-003, DQ-019) |

**Uncovered topics:** none beyond the DQ items.

## 14. Open questions (DQ-xxx)

Blocking = **yes** means it blocks `/plan-sprint`. Owners are not named in the sources, so each owner is "Owner (to be named)". Items marked **RESOLVED** are answered by the owner; their decisions are in §14.1.

| DQ ID | Question | Owner | Blocking |
|-------|----------|-------|----------|
| DQ-001 | **RESOLVED (§14.1).** LLM provider: keep Azure OpenAI (chat model per `AZURE_OPENAI_CHAT_DEPLOYMENT`; `text-embedding-3-small` for embeddings). Claude has no embeddings, so duplicate removal would need title similarity instead. | Owner (to be named) | no |
| DQ-002 | **RESOLVED (§14.1).** What is the title-similarity threshold for the title pass in §5 step 6? | Owner (to be named) | no |
| DQ-003 | **RESOLVED (§14.1; method decision; Blocking = no).** Baseline and tolerance for article counts are set by the method in §14.1. The 400 freshness cap (BR-013) is not an expected count. | Owner | no |
| DQ-004 | **RESOLVED (§14.1; method decision; Blocking = no).** Baseline and tolerance for refresh time are set by the method in §14.1. The earlier 30-minute figure is removed as unverified. | Owner | no |
| DQ-005 | **RESOLVED (§14.1).** The "Unknown" domain fallback (§6.2, BR-008) conflicts with exactly-one-of-five domains (§6.1, BR-001–002). Which takes precedence? | Owner (to be named) | no |
| DQ-006 | **RESOLVED (§14.1).** `deal` is a block word (§5 step 2) and a forbidden restore word (§5 step 3), yet deal-type titles are "strongly preferred" (§5 step 3) and deal news is a core topic. Should `deal` block articles at all? | Owner (to be named) | no |
| DQ-007 | **RESOLVED (§14.1).** Do block and allow words match whole words or substrings? For example, `top` and `under` as substrings would match many unrelated titles. | Owner (to be named) | no |
| DQ-008 | **RESOLVED (§14.1).** The relevance gate's force-keep list names `UST` as an IT-services peer (§5 step 5). Is this the out-of-scope "UST relevance", or a peer-name keyword that may stay? | Owner (to be named) | no |
| DQ-009 | **RESOLVED (§14.1).** Footer text "Copyright 2025 UST" (§10): keep it, or use different text for this tool? | Owner (to be named) | no |
| DQ-010 | **RESOLVED (§14.1; baseline method in DQ-019).** The sources give no problem statement, business outcome or success metric beyond parity with the existing app (§13). Please provide them. | Owner (to be named) | no |
| DQ-011 | **RESOLVED (§14.1).** Feed list (§3.1): TechCrunch appears as #1 and #24 with different URLs; retailtechnology appears as #14 and #41 with the same URL; Retail Dive has a trailing `//`; "Finacial Times" is misspelled. Keep, fix or remove? | Owner (to be named) | no |
| DQ-012 | **RESOLVED (§14.1).** Is the Azure WebJob trigger (§9, §11) a required deployment path, or an optional one? | Owner (to be named) | no |
| DQ-013 | **RESOLVED (§14.1).** Confirm priorities for each FR and BR. All are P0 (proposed) because the sources give none. | Owner (to be named) | no |
| DQ-014 | **RESOLVED (§14.1).** Kit rules require loading and error states (rule 04), masking PII and secrets in logs (rule 02) and sanitising external responses. The notes say none of these. Adopt them as NFRs, or waive them? | Owner (to be named) | no |
| DQ-015 | **RESOLVED (§14.1).** No availability, latency or refresh-time targets are stated (NFR-005). Provide targets, or confirm none are needed. | Owner (to be named) | no |
| DQ-016 | **RESOLVED (§14.1; owner decision; Blocking = no).** How many snapshots must be retained in `new_data`? The notes use the latest 3 for comparison but do not state a retention rule. | Owner (to be named) | no |
| DQ-017 | **RESOLVED (§14.1).** Define `is_deal_news` and `published_at` (§4). `is_deal_news` may mean "has deal types"; this is not stated. | Owner (to be named) | no |
| DQ-018 | **RESOLVED (§14.1).** What happens when a feed, SearchAPI.io, Tavily or the LLM call fails? The notes define fallbacks only for the database comparison (§5 step 7) and the relevance gate (§5 step 5). | Owner (to be named) | no |
| DQ-019 | **RESOLVED (§14.1; method decision; Blocking = no).** Parity baseline and tolerance (owner answer to DQ-010, item h), set by the method in §14.1. The baseline values are recorded by the owner in `evals/product/baseline.md` before `/run-eval`. | Owner | no |
| DQ-020 | **RESOLVED (§14.1).** Authentication: is authentication required for the UI and the routes? | Owner (to be named) | no |
| DQ-021 | **RESOLVED (§14.1).** Hosting and cloud target for this build | Owner (to be named) | no |
| DQ-022 | **OPEN (non-blocking).** Alignment marker: the owner file gives no per-article output that marks news as IT-services aligned. Decide the rule for the blue marker (UD-03) and confirm it is in scope, given BRD §2 and FR-033. | Owner (to be named) | no |

### 14.1 Resolved DQs (owner answers, 2026-10-13)

The owner answers below are recorded as given. Each one is a decision by the owner, not a requirement derived from the notes. The BRD status is now **Accepted** (Ardra Arun, 2026-10-13); see the header.

| DQ | Owner answer (recorded) | Where it changes the BRD | Conflict or note |
|----|-------------------------|--------------------------|------------------|
| DQ-001 | Azure OpenAI only, one resource for chat and embeddings. No Claude, no Groq. Chat deployment from `AZURE_OPENAI_CHAT_DEPLOYMENT`; the chat model is the one named in `AZURE_OPENAI_CHAT_DEPLOYMENT` (no model name is written in the BRD). Embeddings: `text-embedding-3-small` from `AZURE_OPENAI_EMBED_DEPLOYMENT`. | §3, §8, RISK-001 | The BRD does not name a model (DQ-A3, resolved). |
| DQ-002 | Title threshold 0.92. Lowercase both titles and keep only letters and digits. Duplicate when the length difference is below 10 AND `difflib.SequenceMatcher` ratio is 0.92 or higher. Runs inside the embedding dedup function. | FR-016, BR-011, AC-020 | None. |
| DQ-005 | Keep "Unknown", only when the AI classification call fails or returns no domain. Priority is then 3 plus boosts, capped at 5. Articles that already have a domain and priority are not re-classified. | FR-021, BR-008, AC-006 | Replaces the earlier "exactly one domain" conflict. |
| DQ-006 | Keep `deal` as a block word and in the never-restore list. The never-restore check applies to the title only. A `deal` appearing only in the summary can still be restored. | FR-011, FR-012, BR-014, RISK-002 | None. |
| DQ-007 | Substring match on lowercased title plus summary. Noise = at least one block word and no allow word. Known side effect: "POS" matches "position" and "possible". | FR-011 | None. |
| DQ-008 | Keep "ust" in the force-keep list for parity. Substring match, so it also matches "just", "must" and "industry". Recorded as known behaviour, not a UST feature. Full list given in FR-014. | FR-014, RISK-004 | The out-of-scope UST relevance is not added. |
| DQ-010 | Problem, five outcomes, and metrics as recorded in §1. Parity baseline method and tolerance are set in DQ-019. | §1, NFR-008, AC-017 to AC-021 | None. |
| DQ-017 | `is_deal_news` is true when `deal_categories` is a non-empty list, and false otherwise, including when the tagging call fails. `published_at` is a copy of `published` in IST (`YYYY-MM-DD HH:MM:SS`, or `YYYY-MM-DD` if only a date is known). Used for the 15-day cut-off and sorting. If missing or unparseable, both fields are set to the current time. | FR-024, AC-019 | None. |
| DQ-018 | RSS, Google News, SearchAPI or Tavily failure: log, skip, continue. Title re-check LLM fails: batch not restored. Relevance-gate LLM fails: batch kept. Deal tagging fails: `deal_categories` = [], `is_deal_news` = false. Domain/priority call fails: domain "Unknown", priority 3 plus boosts (cap 5), summary unchanged. Embedding dedup fails: list returned unchanged, no embedding or title dedup. DB comparison fails: no DB-duplicate removal; latest snapshot still merged if loaded; if history cannot load, keep only new articles. Worker crash: running flag auto-clears after 70 minutes. Refresh cannot start: record failure in `refresh_status` and return HTTP 500. Nothing fetched: end run with error, clear running flag, do NOT save an empty snapshot. | FR-010, FR-012, FR-016, FR-018, FR-020, FR-021, FR-023, BR-016, AC-005, AC-017, AC-018 | **Two departures from the notes:** (1) the stale-lock limit is 70 minutes, but notes §7 and §11 say 20 (`REFRESH_STALE_MINUTES` default 20); BR-016 and AC-005 now use 70. (2) No empty snapshot is saved, but notes §5 step 12 says to save every run. Owner to confirm both. |

**Second round of owner answers (2026-10-13):**

- **Baseline method (DQ-003, DQ-004, DQ-019; RESOLVED as method decisions; Blocking = no):** the baseline is the average of 3 reference runs made on the same day with the same sources. It covers: total articles; articles per domain (5 values); articles per deal type (6 values); share removed by duplicate removal; and refresh duration.
- **Tolerance:** counts and shares must be within ±25% of the baseline average. Refresh time must be at most 1.5× the baseline average.
- **Not an expected count:** 400 is the freshness cap (BR-013), not a target. The earlier 30-minute figure is removed because it is unverified.
- **Where the baseline lives:** the owner records the averages in `evals/product/baseline.md` before `/run-eval`. If that file is missing or has blank values, `/run-eval` reports the parity check as **not evaluated**, never as passed.
- **DQ-009 (RESOLVED):** keep the footer text "Copyright 2025 UST" (FR-032).
- **DQ-011 (RESOLVED):** keep all 42 feeds and URLs exactly as listed, for parity with the existing app. Both TechCrunch entries (#1, #24) and both retailtechnology entries (#14, #41) stay, because link-based dedup handles repeats. Keep the Retail Dive URL as written. Only the label is corrected: "Finacial Times" becomes "Financial Times". The source notes file still spells it "Finacial Times"; this BRD uses the corrected label.
- **DQ-012 (RESOLVED):** the Azure WebJob trigger is optional. By default, `refresh_worker.py` starts as a subprocess. The WebJob is called only when `AZURE_WEBJOB_TRIGGER_URL` is set in `.env` (FR-039).
- **DQ-013 (RESOLVED):** all FR and BR are confirmed as P0. This is a parity rebuild of an existing tool.
- **DQ-014 (RESOLVED):** adopt NFR-006 (mask secrets and PII in logs, traces and test artefacts) and NFR-007 (loading, empty and error states in the UI). Also adopt sanitising external text, meaning stripping HTML from feed summaries, recorded as NFR-009. Nothing is waived.
- **DQ-015 (RESOLVED):** no availability or latency targets are required. The only performance check is refresh-time parity (DQ-004).
- **DQ-016 (RESOLVED; owner decision; Blocking = no):** snapshot rows are never deleted. Each refresh adds one row, and the comparison step reads the latest 3.
- **DQ-019 (RESOLVED; method decision; Blocking = no):** the parity baseline and tolerance are the method above. The owner records the values in `evals/product/baseline.md`. No numbers are invented here.

**Third round of owner answers (2026-10-13):**

- **DQ-020 (RESOLVED, blocking in the table, answered):** no authentication for this build, for parity with the existing app. The UI and all routes, including `POST /api/refresh`, are open to anyone who can reach the server. The plan has no login, JWT or session slice. **Known risk:** anyone who can reach the server can start a refresh and use Azure OpenAI quota. Authentication must be added before the tool is exposed beyond a trusted network. Recorded as NFR-010.
- **DQ-021 (RESOLVED, blocking in the table, answered):** hosting for this build is local only: Flask on port 5000, local MySQL, started with `scripts/run-local-stack.sh`. No cloud target, infra, Terraform, deployment or CI/CD slice is in the plan. The optional Azure WebJob trigger stays as in FR-039. **Cloud target: not decided, out of scope for this sprint.**

**Open after these answers:** none in the BRD. The baseline values are recorded by the owner in `evals/product/baseline.md` before `/run-eval`. The DQ-A5 approval gate is tracked in the architecture proposal.

## 15. Testable acceptance criteria

| AC ID | Criterion | Maps to FR/BR |
|-------|-----------|---------------|
| AC-001 | An article published more than 15 days before the refresh never appears in `GET /api/news`. | BR-012, FR-019 |
| AC-002 | While a refresh is running, a second `POST /api/refresh` returns `status: running` and starts no new job. | BR-015, FR-035 |
| AC-003 | `GET /health` returns HTTP 200 with the body `OK`. | FR-038 |
| AC-004 | After a refresh completes, the status row has `running` = 0 and `finished_at` and `message` set. | FR-040 |
| AC-005 | A lock with `running` = 1 for more than 70 minutes is cleared automatically, and the message states that the worker likely died (RESOLVED DQ-018; notes say 20 minutes). | BR-016 |
| AC-006 | Every article in a snapshot has exactly one of the five domains. "Unknown" appears only when the AI classification call fails or returns no domain (RESOLVED DQ-005). | BR-001, BR-002, BR-008 |
| AC-007 | An article with at least one deal type has its priority raised by 1, with the result capped at 5. | BR-010 |
| AC-008 | An article from a Google News RSS feed has its priority raised by 1, with the result capped at 5. | BR-009 |
| AC-009 | Articles in a snapshot are ordered by priority descending, then published date descending. | BR-018, FR-022 |
| AC-010 | A snapshot holds at most 400 articles after the freshness filter. | BR-013, FR-019 |
| AC-011 | An article with a missing or invalid date is stored with the refresh time as its date. | FR-019 |
| AC-012 | `GET /api/news` returns `{count: 0, results: []}` when no snapshot exists. | FR-034 |
| AC-013 | The domain filter shows "All" and exactly the five domains; choosing one shows only that domain's articles. | FR-028 |
| AC-014 | The deal-type filter shows a count for each of the six deal types, and Clear filter resets it. | FR-029 |
| AC-015 | The UI shows "No news found" when the snapshot has no articles. | FR-031 |
| AC-016 | While a refresh runs, the UI shows "Refreshing news - this may take a while..." and reloads when it finishes. | FR-030 |
| AC-017 | When one source fails, the refresh still completes with the other sources, and the failure is logged. | FR-010 |
| AC-018 | When nothing is fetched, the run ends with an error, the running flag is cleared, and no snapshot row is written. | FR-023 |
| AC-019 | `is_deal_news` is true only when `deal_categories` is non-empty. `published_at` equals `published`, or the current time when the date is missing or unparseable. | FR-024 |
| AC-020 | No saved pair of articles meets the dedup thresholds: embedding similarity 0.75 for new articles, 0.84 against stored articles, 0.82 after the merge; and title ratio 0.92 with length difference below 10. | BR-011, FR-016, FR-017 |
| AC-021 | Backend line coverage is at least 70%. | NFR-008 |
| AC-022 | A test with stubbed sources and LLM calls confirms that the stages run in the order of FR-045, and that deal-type tagging completes before priority is calculated. | FR-045, FR-020, FR-021 |
| AC-023 | When `evals/product/baseline.md` has all values, the run's article count, per-domain counts, per-deal-type counts and duplicate-removal share are within +/-25% of the baseline, and refresh time is at most 1.5x the baseline. If the file is missing or has blank values, the parity check is reported as not evaluated. | NFR-005, DQ-019 |
| AC-024 | Each LLM prompt used by the pipeline matches the owner's text in `llm-prompts-workflow.md` byte for byte, as stored under `modules/api/app/prompts/`. | FR-046 |

AC-017 to AC-021 come from the owner answers (DQ-010, DQ-018, DQ-017, DQ-002 and DQ-006 in §14.1). Four criteria from the earlier spec (app start does not fetch; no secret in code; `refresh_status.json` fallback; no Insight UI) are covered by FR-041, FR-042, FR-043 and FR-033. They are not yet written as AC and can be added once the owner confirms.

## 16. Traceability to sources

| Artifact | Path | Version/date |
|----------|------|--------------|
| Primary source (raw owner notes) | `artifacts/intake/supporting/ai-news-agent-notes.md` | as found on 2026-10-13 |
| Intake notes | `artifacts/intake/2026-10-13-intake-notes.md` | 2026-10-13 |
| Derived requirements spec (cross-reference only) | `artifacts/intake/transcripts/ai-news-agent-req.md` | earlier pass; not an independent source |
| Stack configuration | `.claude/config.yaml`, `.claude/rules/techstack.md` | current |
| Owner answers to blocking DQs | Supplied in the session on 2026-10-13; recorded in §14.1 | 2026-10-13 |

### 16.1 Test strategy mapping (stack-neutral; tools per `.claude/rules/techstack.md`)

| Level | What it covers | BRD IDs |
|-------|----------------|---------|
| Unit | Boost rules, priority cap, thresholds, freshness cut-off, domain precedence, date conversion | BR-003, BR-007–013, FR-019, FR-025 |
| Integration | Source fetchers (with stubs), pipeline stages, snapshot save, status lock, stale lock, routes | FR-001–023, FR-034–037, BR-015–016 |
| End-to-end | Grid, sort, filters, refresh and polling, empty state | FR-026–031, AC-013–016 |

---

## 17. LLM stage specification (owner file)

Source: `artifacts/intake/supporting/llm-prompts-workflow.md` (owner file). Prompt texts are stored verbatim under `modules/api/app/prompts/` (FR-046). The model is the chat deployment named by `AZURE_OPENAI_CHAT_DEPLOYMENT` (FR-047). No model name is written in this BRD.

| Stage | Requirement | Prompt templates | Batch | Temperature | Max tokens | Output | On failure (DQ-018) |
|-------|-------------|------------------|-------|-------------|------------|--------|---------------------|
| 3 Title re-check | FR-012, BR-014 | `a_title_recheck_system.txt`, `a_title_recheck_user.txt` | 6 | 0 | 150 | `keep_indices`; only noise-filtered titles | Batch not restored |
| 5 Relevance gate | FR-014, FR-015, BR-017 | `b_relevance_gate_system.txt`, `b_relevance_gate_user.txt` | 8 | 0 | 300 | `keep_indices`; force-keep list applied in code | Batch kept |
| 9 Deal-type tagging | FR-020, BR-004 to BR-006 | `c_deal_tagging_system.txt`, `c_deal_tagging_user.txt`, `c_deal_category_definitions.txt` | 8 | 0 | 800 | `results[]` with `index` and `categories` (valid keys only) | `deal_categories` = []; `is_deal_news` = false |
| 10 Domain, priority, summary | FR-021, BR-001 to BR-003, BR-007 to BR-010 | `d_domain_priority_summary_system.txt`, `d_domain_priority_summary_user.txt` | 1 per article, 8 workers | 0.2 | No limit | `refined_summary`, `domain`, `priority` | Domain "Unknown"; priority 3 plus boosts (cap 5); summary unchanged |

Points recorded from the owner file:
- **Stage 3 deal preference:** the prompt asks the model to prefer keeping deal titles. The title safety net (BR-014, title only) blocks restoring any title containing "deal", so deal titles are not restored at stage 3. This is the owner's decision (RISK-002).
- **Stage 5 peer names:** the prompt names IT-services peers, including UST. Kept as known substring behaviour (DQ-008).
- **Stage 10 example:** the trailing comma after `"priority": 4` is removed so the example is valid JSON (G-01 closure, 2026-10-13).
- **Relevance framing:** stages 3 and 5 judge relevance for an IT services company (FR-048). Stage 5 keeps by default and drops only clear noise (BR-017).
- **Deal categories:** the owner's category definitions (`c_deal_category_definitions.txt`) refine BR-005. A category applies only when the deal is the article's main subject.

## Governance

- Every FR and BR cites `source_path` and `source_locator` in the notes. Inferences are marked `[INFERRED]` and tied to a DQ (RISK-003 → DQ-018).
- The BRD is Accepted by Ardra Arun on 2026-10-13. Acceptance was given by a human reviewer; no agent approved it.
- Conflicts are resolved only by owner answers, recorded in §14.1. Departures from the notes are listed there: the stale-lock limit (70 minutes, DQ-018), no empty snapshot (DQ-018), and the chat model, set by `AZURE_OPENAI_CHAT_DEPLOYMENT` (DQ-A3).

**Output path:** `artifacts/brd/ai-news-agent-BRD-draft.md`

**Next command after Accepted:** `/plan-sprint`
