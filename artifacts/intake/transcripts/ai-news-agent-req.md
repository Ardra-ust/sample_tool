# AI News Agent — Requirements Specification

**Source of truth:** `artifacts/intake/supporting/ai-news-agent-notes.md` (section references below are to that file).
**Status:** Draft — Pending Domain Review (`/generate-brd` output; not Accepted).
**Scope note:** UST relevance, insights, GDELT and Groq are out of scope and are not specified here.

---

## 1. Scope

### 1.1 What the system provides
- Collects technology and industry news from four source types: RSS feeds, Google News RSS searches, SearchAPI.io, and Tavily.
- Filters out consumer noise, uses an LLM relevance gate, and removes duplicate articles.
- Classifies each article by domain, deal type and priority.
- Stores each refresh as one snapshot in MySQL.
- Shows the latest snapshot in a filterable news grid.
- Runs manual refreshes through a separate worker, with status polling in the UI.
- Exposes a health endpoint.

### 1.2 Out of Scope
- UST relevance, UST alignment score, UST offerings catalogue, any RAG over it (§2)
- Insight generation: insight paragraphs, "News with Insight", "UST Relevant" filters, Insight tab/dashboard (§2)
- "Important" Yes/No classification, bucket classification, keyword extraction (§2)
- Trend summaries, including all GDELT calls; GDELT is not a news source here (§2)
- Opportunity themes, "where to act first", web-search-based insight calls (§2)
- The `important_news_output.txt` export and `classification_logs/` folder (§2)

---

## 2. Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| FR-001 | The system shall fetch every RSS feed in the 42-entry RSS list on each refresh, taking the first 7 entries per feed, except AnalyticsIndiaMag, which shall take up to 50 entries. | §3.1 |
| FR-002 | The system shall keep only English-language articles from RSS feeds. | §3.1 |
| FR-003 | The system shall cut RSS summaries to 400 characters, except AnalyticsIndiaMag, whose summaries shall be cut to 1500 characters. | §3.1 |
| FR-004 | The system shall fetch each of the 25 curated Google News RSS searches on each refresh, using the URL form `https://news.google.com/rss/search?q=<query> when:7d` with the query URL-encoded. | §3.2 |
| FR-005 | The system shall take up to 20 entries from each Google News feed whose name contains `MnA`, `MnAPartnership`, `Partnership`, `Alliance`, `Alliances` or `Funding`, and 7 entries from every other Google News feed. | §3.2 |
| FR-006 | The system shall decode Google News wrapper links to the real publisher URL before storing them. | §3.2 |
| FR-007 | The system shall call the SearchAPI.io Google News engine with query `technology`, 15 results and location `India`, and shall use both `top_stories` and `organic_results`. | §3.3 |
| FR-008 | The system shall run one Tavily search per refresh, with a maximum of 10 results, with answer and raw content enabled, using the query defined in §3.4 with the current date. | §3.4 |
| FR-009 | The system shall keep only Tavily results that have a valid published date, a link and English text. | §3.4 |
| FR-010 | The system shall fetch from all four source types on every refresh. | §5 step 1 |
| FR-011 | The system shall mark an article as consumer noise when its title plus summary contains a block word and no allow word, using the lists in §5 step 2. | §5 step 2 |
| FR-012 | The system shall re-check noise-filtered titles with the LLM in batches of 6 at temperature 0, restoring titles relevant to a technology services company, and shall never restore a title containing a forbidden word (see BR-014). | §5 step 3 |
| FR-013 | The system shall remove duplicate articles by link, then by title, and shall keep at most 500 articles. | §5 step 4 |
| FR-014 | The system shall run an LLM relevance gate in batches of 8 at temperature 0, dropping only clear noise and force-keeping any article containing a deal, enterprise-tech or IT-services-peer keyword listed in §5 step 5. | §5 step 5 |
| FR-015 | The system shall keep the LLM relevance gate's batch when the LLM call fails. | §5 step 5 |
| FR-016 | The system shall remove near-duplicate articles using embedding similarity at the threshold in BR-011, then run a title-similarity pass. | §5 step 6 |
| FR-017 | The system shall load the latest 3 snapshots from `new_data`, drop each new article whose embedding similarity to any stored article is at or above the threshold in BR-011, merge the remaining new articles with the articles of the most recent snapshot only, and run near-duplicate removal again at the threshold in BR-011. | §5 step 7 |
| FR-018 | The system shall continue with the new articles only when the database comparison in FR-017 fails. | §5 step 7 |
| FR-019 | The system shall drop articles older than 15 days, set missing or invalid dates to the current time, and keep the latest 400 articles. | §5 step 8 |
| FR-020 | The system shall tag each article with zero, one or several deal types using the LLM in batches of 8 at temperature 0, skipping articles that already have deal categories. | §5 step 9 |
| FR-021 | The system shall assign each article one domain, a priority and a refined summary using the LLM at temperature 0.2 with 8 parallel workers, skipping articles loaded from the database that already have a domain and priority. | §5 step 10 |
| FR-022 | The system shall sort articles by priority (high to low), then by published date (newest first). | §5 step 11 |
| FR-023 | The system shall save the full sorted list as one JSON snapshot row in `new_data` on each refresh. | §5 step 12, §7 |
| FR-024 | The system shall store each article with the fields: title, link, source, published (IST, `YYYY-MM-DD HH:MM:SS`), summary, domain, priority, deal_categories, is_deal_news, is_google_news, published_at. | §4 |
| FR-025 | The system shall convert relative dates (for example "2 hours ago", "yesterday") to absolute dates shown in IST (UTC+5:30), and shall remove date/time fragments from summaries. | §4 |
| FR-026 | The system shall display the latest snapshot on the index page as a grid of news cards. | §10 |
| FR-027 | The system shall provide a sort control with two options: Priority (High to Low) and Date (Newest to Oldest). | §10 |
| FR-028 | The system shall provide a domain filter with "All" and the five domains, with a select-domain popup. | §10 |
| FR-029 | The system shall provide a deal-type filter showing colour-coded chips with a count per deal type, and a Clear filter control. | §10 |
| FR-030 | The system shall provide a Refresh News button that, while a refresh runs, shows "Refreshing news - this may take a while..." and polls `/api/refresh/status` until the refresh finishes, then reloads the page. | §10 |
| FR-031 | The system shall show a "No news found" empty state when the snapshot has no articles. | §10 |
| FR-032 | The system shall show the page title "Latest Tech News" with a logo, and a footer reading "Copyright 2025 UST" (see OQ-7). | §10 |
| FR-033 | The system shall not show the "UST Relevant" or "News with Insight" filters, or the Insight popup. | §10 |
| FR-034 | The system shall serve `GET /api/news` with the latest snapshot as `{count, results, fetched_at}` (IST), returning `{count: 0, results: []}` when no snapshot exists, with no-cache headers. | §8 |
| FR-035 | The system shall handle `POST /api/refresh` by returning `status: running` when a refresh is in progress; otherwise it shall take the atomic lock in BR-013, start the refresh job, and return `status: started`. | §8 |
| FR-036 | The system shall return HTTP 500 from `POST /api/refresh` when starting the refresh fails, and shall record the failure. | §8 |
| FR-037 | The system shall serve `GET /api/refresh/status` with `{running, started_at, finished_at, message, last_run_type}` and no-cache headers. | §8 |
| FR-038 | The system shall serve `GET /health` and respond with OK. This route does not exist in the current app and must be added. | §8, §13 |
| FR-039 | The system shall run the refresh pipeline in a separate worker script (`refresh_worker.py`) started as a subprocess, unless an Azure WebJob trigger URL is configured, in which case it shall call that URL instead. | §9 |
| FR-040 | The worker shall clear the running flag when the pipeline ends, and shall write `finished_at` and either a success message or the error trace. | §9 |
| FR-041 | The system shall start only the web server when `app.py` runs, and shall not fetch news at startup. The UI shall show the snapshot already in MySQL. | §9 |
| FR-042 | The system shall read all secrets and connection settings from `.env` through python-dotenv, never hardcode them, and provide `.env.example` with empty values. | §11 |
| FR-043 | The system shall store refresh status in MySQL and, when the database is unavailable, fall back to a local `refresh_status.json` (development only). | §7 |
| FR-044 | The system shall create the `refresh_status` row automatically with a "Ready" message when it is missing. | §7 |

---

## 3. Business Rules

| ID | Rule | Source |
|---|---|---|
| BR-001 | The system shall use exactly five domains: Healthcare; Retail; Banking and Financial Services; Technology & Communication; Wealth & Asset Management. | §6.1 |
| BR-002 | Each article shall have exactly one domain. Healthcare covers hospitals, providers, insurers, medical tech, telehealth, EHRs and clinical systems. Retail covers retail brands, e-commerce, stores, supply chain, POS, inventory and customer experience. Banking and Financial Services covers banks, payments, lending, insurance, KYC/AML compliance, fraud, core banking and fintech infrastructure. Technology & Communication covers tech vendors, cloud/AI platforms, telecom, networking, chips, cybersecurity, software and hardware. Wealth & Asset Management covers investment management, asset management, portfolio platforms, trading, brokerage, advisory and robo-advisory. | §6.1 |
| BR-003 | When both Banking and Financial Services and Wealth & Asset Management signals appear, the article shall be classified as Wealth & Asset Management. | §6.1 |
| BR-004 | The system shall use six deal types: Mergers & Acquisitions (`mergers_acquisitions`, green); Partnerships (`partnerships`, blue); Joint Ventures (`joint_ventures`, violet); Strategic Investments (`strategic_investments`, yellow); Spin-offs (`spin_offs_divestitures`, amber); Alliances (`alliances`, red). | §6.3 |
| BR-005 | Deal-type core tests: Mergers & Acquisitions — two companies combine, or one buys a controlling stake, including the buyer's side of a divestiture. Partnerships — a specific two-party deal with no new company and no equity change. Joint Ventures — a new, separate, jointly owned entity is created (new name, ownership split). Strategic Investments — a minority, non-controlling stake where the investee stays independent. Spin-offs — the seller's side: a unit is spun off or sold. Alliances — a formal arrangement among three or more organisations around a shared goal or standard. | §6.3 |
| BR-006 | Deal types shall be judged by meaning, not keywords. A passing mention of "partner" does not count. A generic funding round with no strategic angle does not count. When unsure, the category shall be left out. Deal tagging is precision-first. | §5 step 9, §6.3 |
| BR-007 | Priority shall be an integer from 1 to 5, where higher is more important. 5: strategic or market-shifting. 4: major operational or product advancement. 3: emerging opportunity or competitive signal. 2: incremental improvement or internal optimisation. 1: thought leadership, commentary or cultural context. | §6.2 |
| BR-008 | When the classification AI call fails, the priority shall default to 3 and the domain shall be set to "Unknown" (see OQ-5). | §6.2 |
| BR-009 | An article from a Google News RSS feed shall receive a +1 priority boost. | §6.2 |
| BR-010 | An article with any deal category shall receive a +1 priority boost. The total priority shall be capped at 5 after boosts. | §6.2 |
| BR-011 | Embedding similarity thresholds: near-duplicate removal (new articles, step 6) cosine ≥ 0.75 is a duplicate; database comparison (step 7) similarity ≥ 0.84 to any stored article drops the new article; second near-duplicate removal after the database merge uses 0.82. The title-similarity threshold is not specified (see OQ-4). | §5 steps 6–7 |
| BR-012 | Articles older than 15 days shall be dropped. | §5 step 8 |
| BR-013 | At most 500 articles shall be kept after deduplication (step 4), and at most 400 after the freshness filter (step 8). | §5 steps 4, 8 |
| BR-014 | Titles containing any of these words shall never be restored by the LLM re-check: christmas, festive, new year, buy, discount, deal, offer, gift, sale. | §5 step 3 |
| BR-015 | Refresh lock: a refresh shall take an atomic database lock (`UPDATE ... WHERE running=0`). Only one refresh shall run at a time. | §8 |
| BR-016 | Stale lock: when `running` has been 1 for more than 20 minutes (`REFRESH_STALE_MINUTES`), the system shall clear it automatically with a message that the worker likely died. | §7, §11 |
| BR-017 | The LLM relevance gate shall drop only clear noise: consumer gadgets and shopping, entertainment, sports and lifestyle, pure clinical or drug results with no tech, data or deal angle, personal-finance tips, and pure opinion. Everything else shall be kept. | §5 step 5 |
| BR-018 | Articles shall be sorted by priority (high to low), then by published date (newest first). | §5 step 11 |

---

## 4. Technical Requirements

### 4.1 Technology Stack

| Layer | Requirement |
|---|---|
| Frontend | Flask Jinja templates + HTML/JS |
| Backend | Python 3.11+ |
| API framework | Flask |
| Database | MySQL (database `news_app`) |
| API communication | REST/JSON |
| Architecture | Single Flask web service plus a separate refresh worker |
| LLM and embeddings | Open (see OQ-1) |

### 4.2 Backend
- Serve the routes in §5 from one Flask service on port 5000 (Flask default).
- Run the fetch, filter, classify and save pipeline (§4.5) in a separate worker script, `refresh_worker.py`, and not inside a request.
- Read all configuration from environment variables loaded from `.env`: `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`; `REFRESH_STATUS_TABLE` (default `refresh_status`); `REFRESH_STATUS_ROW_ID` (default 1); `REFRESH_STALE_MINUTES` (default 20); `TAVILY_API_KEY`; `SEARCHAPI_IO_KEY`; the Azure OpenAI chat and embedding settings (see OQ-1); and the optional `AZURE_WEBJOB_TRIGGER_URL`, `AZURE_WEBJOB_USER`, `AZURE_WEBJOB_PASS`.
- Validate and sanitise all external responses before storing them.
- Mask secrets in logs and error traces.

### 4.3 Frontend
- One index page, `index.html`, with the title, logo, sort control, domain filter, deal-type filter, Refresh News button, news grid, empty state and footer (see FR-026 to FR-033).
- Poll `/api/refresh/status` while a refresh runs, then reload.
- Show loading, empty and error states for every journey.

### 4.4 Database
Database `news_app`, MySQL.

**Table `new_data`** (one row per refresh)

| Column | Notes |
|---|---|
| `id` | Auto-increment primary key |
| `news` | JSON text of the full article list |
| `updated_at` | Set to NOW() on insert |

**Table `refresh_status`** (name configurable via `REFRESH_STATUS_TABLE`; one row with `id` = 1)

| Column | Notes |
|---|---|
| `id` | Always 1 (`REFRESH_STATUS_ROW_ID`) |
| `running` | 0 or 1 |
| `started_at` | Set when a refresh starts |
| `finished_at` | Set when a refresh ends |
| `message` | Status or failure message |
| `last_run_type` | Type of the last run |
| `trace` | Error trace on failure |
| `updated_at` | Last update time |

The table is created automatically with a "Ready" message if missing.

### 4.5 Core Processing Flow

```
[1] Fetch: RSS (42 feeds) + Google News RSS (25 searches) + SearchAPI.io + Tavily
     │
[2] Consumer-noise keyword filter (block words vs allow words)
     │
[3] LLM re-check of noise-filtered titles (batches of 6, temperature 0)
     │
[4] Dedupe by link, then by title; keep at most 500
     │
[5] LLM relevance gate (batches of 8, temperature 0, recall-first)
     │
[6] Near-duplicate removal (embeddings, cosine ≥ 0.75), then title-similarity pass
     │
[7] Compare with DB: latest 3 snapshots; drop similarity ≥ 0.84;
     merge with most recent snapshot; near-duplicate removal again (≥ 0.82)
     │
[8] Freshness: drop > 15 days old; invalid dates → now; keep latest 400
     │
[9] Deal-type tagging (LLM, batches of 8, temperature 0)
     │
[10] Domain + priority + refined summary (LLM, temperature 0.2, 8 workers)
     │
[11] Sort: priority high→low, then published newest first
     │
[12] Save full list as one JSON row in new_data
```

---

## 5. Key APIs

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | News grid page (`index.html`) |
| `/api/news` | GET | Latest snapshot: `{count, results, fetched_at}` (IST); no-cache headers |
| `/api/refresh` | POST | Start a refresh, or return `running` if one is in progress; HTTP 500 on start failure |
| `/api/refresh/status` | GET | `{running, started_at, finished_at, message, last_run_type}`; no-cache headers |
| `/health` | GET | Health check; returns OK (new route) |

---

## 6. Acceptance Criteria

| ID | Criterion | Verifies |
|---|---|---|
| AC-001 | An article published more than 15 days before the refresh time never appears in `/api/news` results. | BR-012, FR-019 |
| AC-002 | When a refresh is running, a second `POST /api/refresh` returns `status: running` and starts no new job. | BR-015, FR-035 |
| AC-003 | `GET /health` returns OK with a success status. | FR-038 |
| AC-004 | After a refresh completes, `refresh_status.running` is 0 and `finished_at` and `message` are set. | FR-040 |
| AC-005 | A refresh lock left at `running = 1` for more than 20 minutes is cleared automatically and the message states that the worker likely died. | BR-016 |
| AC-006 | Every article in the snapshot has exactly one of the five domains. | BR-001, BR-002 |
| AC-007 | Every article with a deal category receives a priority boost of +1 (total capped at 5). | BR-010 |
| AC-008 | An article from a Google News feed receives a priority boost of +1 (total capped at 5). | BR-009 |
| AC-009 | Articles in the snapshot are ordered by priority descending, then by published date descending. | BR-018, FR-022 |
| AC-010 | Each snapshot holds no more than 400 articles after the freshness filter. | BR-013, FR-019 |
| AC-011 | Articles with missing or invalid dates are stored with a date equal to the refresh time. | FR-019 |
| AC-012 | `/api/news` returns `{count: 0, results: []}` when no snapshot exists. | FR-034 |
| AC-013 | The domain filter shows "All" and exactly the five domains; selecting one shows only that domain's articles. | FR-028 |
| AC-014 | The deal-type filter shows a count for each of the six deal types and the Clear filter control resets it. | FR-029 |
| AC-015 | The UI shows "No news found" when the snapshot has no articles. | FR-031 |
| AC-016 | While a refresh runs, the UI shows "Refreshing news - this may take a while..." and reloads when the refresh finishes. | FR-030 |
| AC-017 | Starting the app with `app.py` does not fetch news. | FR-041 |
| AC-018 | No secret value appears in source code, logs or `.env.example`. | FR-042 |
| AC-019 | When the database is unavailable, status is read from `refresh_status.json`. | FR-043 |
| AC-020 | The UI shows no "UST Relevant" or "News with Insight" filter and no Insight popup. | FR-033 |

---

## 7. Open Questions

| ID | Question | Why it matters |
|---|---|---|
| OQ-1 | **LLM provider.** Keep Azure OpenAI (chat model `gpt-5.2-chat` for all LLM steps; `text-embedding-3-small` for embeddings), or switch to Claude via Foundry? Claude has no embeddings, so near-duplicate removal (FR-016, FR-017) would need title similarity instead. | Determines the LLM steps (FR-012, FR-014, FR-020, FR-021), BR-011 thresholds, and §4.2 settings. |
| OQ-2 | **Expected article count per refresh:** ______ | Acceptance check §13 "similar number of articles per source" needs a baseline. |
| OQ-3 | **Expected refresh time:** ______ | Acceptance check §13 "refresh time is comparable" needs a baseline. |
| OQ-4 | **Title-similarity threshold** for the title-similarity pass (FR-016) is not given in the notes. | The pass cannot be tested without a value. |
| OQ-5 | **"Unknown" domain fallback.** BR-008 sets the domain to "Unknown" when the classification call fails, but BR-001/BR-002 require exactly one of five domains. Which takes precedence? | Conflicts with AC-006. |
| OQ-6 | **Database.** The kit's `.claude/rules/techstack.md` names SQLite for persistence. This tool requires MySQL (`news_app`). Confirm MySQL and record the override in `docs/harness/decisions.md`. | Affects the stack rule and conventions the agents follow. |
| OQ-7 | **Footer text.** Keep "Copyright 2025 UST" (FR-032) for the new tool, or use different text? | UI copy must come from the owner, not be invented. |
| OQ-8 | **Feed list issues.** The RSS list has duplicate entries (TechCrunch at #1 and #24 with different URLs; retailtechnology at #14 and #41 with the same URL), a Retail Dive URL with a trailing `//`, and a source name spelled "Finacial Times". Keep, fix or remove? | Duplicate feeds fetch the same articles twice before deduplication. |
