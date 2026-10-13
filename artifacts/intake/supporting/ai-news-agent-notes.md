# AI News Agent - Requirements Notes (for Claude Code intake)

Put this file in `artifacts/intake/transcripts/`. It describes the behaviour of the AI News Agent (Flask + MySQL) so the new tool can be built with it. No secrets are in this file.

Items marked **[FILL]** are decisions only the owner can make.

## 1. Purpose
A web tool that collects technology and industry news from several sources, filters out noise, removes duplicates, classifies each article by domain and deal type, gives it a priority score, stores the result in MySQL, and shows it in a filterable grid. Backend: Python Flask. UI: Flask Jinja template + HTML/JS. Database: MySQL.

## 2. Out of scope (do NOT build)
- UST relevance, UST alignment score, UST offerings catalogue, any RAG over it
- Insight generation (insight paragraphs, "News with Insight", "UST Relevant" filters, Insight tab/dashboard)
- "Important" Yes/No classification, bucket classification, keyword extraction
- Opportunity themes, "where to act first", web-search-based insight calls
- The `important_news_output.txt` export and `classification_logs/` folder

## 3. News sources (all are fetched on every refresh)

### 3.1 RSS feeds (42 entries)
Default: first 7 entries per feed. Only English articles are kept. Summary is cut to 400 characters, except AnalyticsIndiaMag (up to 50 entries, 1500 characters).

| # | Source name | URL |
|---|---|---|
| 1 | TechCrunch | https://techcrunch.com/category/artificial-intelligence/feed/ |
| 2 | Live Mint | https://www.livemint.com/rss/technology/ |
| 3 | MIT Technology Review | https://www.technologyreview.com/feed/ |
| 4 | VentureBeat | https://venturebeat.com/feed/ |
| 5 | AI News | https://artificialintelligence-news.com/feed/ |
| 6 | CNBC Tech | https://www.cnbc.com/id/19854910/device/rss/rss.html |
| 7 | BBC Technology | https://feeds.bbci.co.uk/news/technology/rss.xml |
| 8 | Pragmaticengineer | https://newsletter.pragmaticengineer.com/feed |
| 9 | The Verge | https://www.theverge.com/rss/ai-artificial-intelligence/index.xml |
| 10 | The Guardian | https://www.theguardian.com/technology/artificialintelligenceai/rss |
| 11 | ET Health-IT | https://health.economictimes.indiatimes.com/rss/health-it |
| 12 | ET health top stories | https://health.economictimes.indiatimes.com/rss/topstories |
| 13 | ET medical devices | https://health.economictimes.indiatimes.com/rss/medical-devices |
| 14 | Retail Tech | https://www.retailtechnology.co.uk/rss.xml |
| 15 | ET retail | https://retail.economictimes.indiatimes.com/rss/consumer-durables-and-information-technology |
| 16 | HIT Consultant | https://hitconsultant.net/feed |
| 17 | Retail news | https://retailnews.ai/feed/ |
| 18 | AnalyticsIndiaMag (limit 50) | https://zdpdvwhvukelzzbzbjvh.supabase.co/functions/v1/rss-feed |
| 19 | Pay dive | https://paymentsdive.com/feeds/news/ |
| 20 | Finacial Times | https://www.ft.com/technology?format=rss |
| 21 | Fintech Weekly | https://www.fintechweekly.com/news.rss |
| 22 | modernretail | https://www.modernretail.co/technology/feed/ |
| 23 | Retail Dive | https://retaildive.com/feeds/news// |
| 24 | Techcrunch | https://techcrunch.com/feed/ |
| 25 | BP | https://www.beckerspayer.com/feed |
| 26 | FinTech Times | https://thefintechtimes.com/feed/ |
| 27 | HCD | https://www.healthcaredive.com/feeds/news/ |
| 28 | Fierce Health | https://fiercehealthcare.com/rss/payers/xml |
| 29 | expresshealthcare | https://www.expresshealthcare.in/category/healthcare-it/feed/ |
| 30 | privateequitywire | https://www.privateequitywire.co.uk/feed/ |
| 31 | connectmoney | https://www.connectmoney.com/feed/?story-market=asset-management |
| 32 | connect_money | https://www.connectmoney.com/feed/?story-market=wealth-management |
| 33 | pymnts | https://www.pymnts.com/feed/ |
| 34 | fiercehealthcare | https://www.fiercehealthcare.com/rss/xml |
| 35 | wealthmanagement | https://www.wealthmanagement.com/rss.xml |
| 36 | techrepublic | https://www.techrepublic.com/rssfeeds/topic/fintech/ |
| 37 | assetservicingtimes | https://www.assetservicingtimes.com/rssfeed.php |
| 38 | medcitynews | https://medcitynews.com/feed/ |
| 39 | biopharmadive | https://www.biopharmadive.com/feeds/news/ |
| 40 | fiercebiotech | https://www.fiercebiotech.com/rss/xml |
| 41 | retailtechnology (same URL as #14) | https://www.retailtechnology.co.uk/rss.xml |
| 42 | retailwire | https://retailwire.com/feed/ |

### 3.2 Google News RSS feeds (25 curated searches, priority source)
Each feed is `https://news.google.com/rss/search?q=<query> when:7d` (last 7 days, query must be URL-encoded). Default 7 entries per feed; feeds whose name contains `MnA`, `MnAPartnership`, `Partnership`, `Alliance`, `Alliances` or `Funding` take up to 20 entries. Articles from these feeds get a **+1 priority boost** (max 5). Google News wrapper links must be decoded to the real publisher URL (library: `googlenewsdecoder`).

`<DEAL>` below means this exact group: acquisition OR acquisitions OR merger OR mergers OR "mergers and acquisitions" OR M&A OR divestiture OR divestitures OR partnership OR partnerships OR alliance OR alliances OR "joint venture" OR "joint ventures" OR "strategic investment" OR "strategic investments" OR "spin-off" OR spinoff OR spinoffs

| Domain | Feed name | Query |
|---|---|---|
| Healthcare | GoogleNews-Hospital-HealthTechFunding | ("health tech" OR "healthcare IT" OR "digital health") ("raises" OR funding OR "Series A" OR "Series B" OR "Series C" OR `<DEAL>`) |
| Healthcare | GoogleNews-Hospital-MnAPartnership | (hospital OR "health system" OR payer) (`<DEAL>` OR "EHR implementation") |
| Healthcare | GoogleNews-Hospital-TelehealthRCM | (telehealth OR "revenue cycle" OR interoperability) (funding OR "Series A" OR "Series B" OR "Series C" OR `<DEAL>`) |
| Banking | GoogleNews-Banking-FintechFunding | fintech ("raises" OR funding OR "Series A" OR "Series B" OR "Series C" OR investment OR `<DEAL>`) |
| Banking | GoogleNews-Banking-CoreDigitalPayments | ("core banking" OR "digital banking" OR payments) (`<DEAL>`) |
| Banking | GoogleNews-Banking-BankCreditUnionTech | (bank OR "credit union") ("technology investment" OR "digital transformation" OR "IT modernization" OR `<DEAL>`) |
| Banking | GoogleNews-Banking-InsurtechWealthtechRegtech | (insurtech OR wealthtech OR regtech) (funding OR raises OR investment OR `<DEAL>` OR "Series A" OR "Series B" OR "Series C") |
| Banking | GoogleNews-Banking-FintechInsurtechFundingBroad | (fintech OR insurtech OR regtech OR wealthtech) (funding OR raises OR "Series A" OR "Series B" OR "Series C" OR investment OR `<DEAL>`) |
| Retail | GoogleNews-Retail-DigitalTransformation | (retail OR retailer OR e-commerce OR marketplace OR omnichannel) ("digital transformation" OR AI OR cloud OR modernization OR funding OR investment OR "Series A" OR "Series B" OR "Series C") |
| Retail | GoogleNews-Retail-MnAPartnership | (retail OR retailer OR e-commerce OR marketplace) (`<DEAL>`) |
| Retail | GoogleNews-Retail-SupplyChainAutomation | ("supply chain" OR logistics OR warehouse OR fulfillment OR inventory) (automation OR AI OR robotics OR cloud OR modernization OR investment OR partnership) |
| Retail | GoogleNews-Retail-OmnichannelCRM | (omnichannel OR loyalty OR CRM OR personalization OR ecommerce OR marketplace) (AI OR implementation OR migration OR modernization OR partnership) |
| Retail | GoogleNews-Retail-Payments | (payments OR "digital payments" OR POS OR "point of sale" OR checkout OR "payment gateway" OR "payment processing" OR "digital wallet" OR BNPL OR "buy now pay later") (modernization OR implementation OR migration OR acquisition OR partnership OR investment OR AI) |
| Retail | GoogleNews-Retail-PlatformVendors | (SAP OR Salesforce OR Oracle OR Shopify OR commercetools OR "Adobe Commerce" OR "Microsoft Dynamics") (implementation OR migration OR modernization OR partnership OR acquisition) |
| Technology | GoogleNews-Tech-MnAPartnership | (software OR SaaS OR "enterprise software" OR cloud OR cybersecurity OR AI OR "artificial intelligence" OR GenAI OR telecom OR communications) (`<DEAL>`) |
| Technology | GoogleNews-Tech-CloudDevOpsAlliances | (cloud OR AWS OR Azure OR GCP OR Kubernetes OR DevOps OR "application modernization" OR "cloud migration") (partnership OR partnerships OR alliance OR alliances OR acquisition OR merger OR "strategic investment") |
| Technology | GoogleNews-Tech-AIFundingMnA | (AI OR "artificial intelligence" OR GenAI OR LLM OR "machine learning" OR "data platform" OR analytics) (funding OR raises OR "Series A" OR "Series B" OR "Series C" OR acquisition OR merger OR partnership OR "strategic investment") |
| Technology | GoogleNews-Tech-TelecomNetworking | (telecom OR communications OR 5G OR "Open RAN" OR broadband OR networking OR "edge computing") (acquisition OR merger OR partnership OR alliance OR "joint venture" OR "strategic investment") |
| Technology | GoogleNews-Tech-EnterprisePlatformVendors | (SAP OR Salesforce OR Oracle OR ServiceNow OR Workday OR Adobe OR Snowflake OR Databricks) (implementation OR modernization OR migration OR acquisition OR partnership OR alliance) |
| Technology | GoogleNews-Tech-Cybersecurity | (cybersecurity OR "identity management" OR "zero trust" OR "network security" OR "endpoint security") (acquisition OR merger OR partnership OR alliance OR "strategic investment") |
| Wealth | GoogleNews-Wealth-MnAPartnership | ("wealth management" OR "asset management" OR "investment management" OR "private banking" OR wealthtech OR fintech) (`<DEAL>`) |
| Wealth | GoogleNews-Wealth-DigitalTransformation | ("digital transformation" OR "application modernization" OR "legacy modernization" OR "cloud migration" OR "cloud transformation" OR AI OR "generative AI" OR analytics OR automation) ("wealth management" OR "asset management" OR wealthtech OR fintech) (partnership OR partnerships OR alliance OR alliances OR acquisition OR merger OR "strategic investment") |
| Wealth | GoogleNews-Wealth-PlatformVendors | (Aladdin OR "Charles River" OR SimCorp OR Avaloq OR Temenos OR Broadridge) (implementation OR modernization OR migration OR acquisition OR merger OR partnership OR alliance OR "joint venture") |
| Wealth | GoogleNews-Wealth-RegulatoryCompliance | (AML OR KYC OR DORA OR MiFID OR SEC OR FINRA OR "risk management" OR "regulatory compliance") (technology OR AI OR automation OR modernization OR partnership OR acquisition) |
| Wealth | GoogleNews-Wealth-DataPlatformCyber | ("data platform" OR analytics OR API OR microservices OR cybersecurity OR "identity management" OR "zero trust") ("wealth management" OR "asset management" OR fintech) (partnership OR acquisition OR merger OR "strategic investment") |

### 3.3 SearchAPI.io (Google News engine)
GET `https://www.searchapi.io/api/v1/search` with engine `google_news`, query `technology`, 15 results, location `India`. Use both `top_stories` and `organic_results`. Fields: title, link, source, date, snippet (summary cut to 400 characters). API key from `.env`.

### 3.4 Tavily search
One search per refresh, max 10 results, with answer and raw content on. Query: "Latest Artificial Intelligence and Technology news in English {today's date}, need the link to a specific news, not the portal." Keep only results with a valid published date, a link, and English text. Summary cut to 400 characters. API key from `.env`.

## 4. Article fields
title, link, source, published (IST, `YYYY-MM-DD HH:MM:SS`), summary, domain, priority, deal_categories (list), is_deal_news, is_google_news, published_at. Relative dates ("2 hours ago", "yesterday") are converted to absolute dates and shown in IST (UTC+5:30). Summaries have date/time fragments removed.

## 5. Processing pipeline (order matters)
1. Fetch from all four source types (section 3).
2. **Consumer-noise filter (keywords).** An article is noise if title+summary contains a block word and no allow word.
   - Block words: discount, deal, offer, sale, festive, christmas, diwali, new year, best, top, which model, review, unboxing, price, under, shopping, buy, gaming, game, entertainment, smartphone, laptop, earbuds, headphones, oppo, samsung, xiaomi, iphone, acer, amazon deals, year-end deals
   - Allow words: enterprise, platform, modernization, transformation, AI deployment, cloud migration, POS, supply chain, automation, managed services, IT services, contract, checkout system, inventory system, retail platform, start-up
3. **LLM re-check of the noise-filtered titles** (batches of 6, temperature 0). Restore titles relevant to a technology services company (enterprise tech, cloud, AI, data, deals, regulation, digital transformation); deal-type titles are strongly preferred. Never restore titles containing: christmas, festive, new year, buy, discount, deal, offer, gift, sale.
4. **Dedupe by link, then by title**; keep at most 500 articles.
5. **IT-opportunity relevance gate** (LLM, batches of 8, temperature 0, recall-first). Drop only clear noise: consumer gadgets/shopping, entertainment/sports/lifestyle, pure clinical/drug results with no tech/data/deal angle, personal-finance tips, pure opinion. Keep everything else. When the AI call fails, keep the batch. Force-keep any article whose text contains a deal, enterprise-tech or IT-services-peer keyword (e.g. acqui, merger, joint venture, partnership, funding, cloud, AI, cybersecurity, platform, automation, Accenture, Infosys, TCS, Cognizant, Wipro, Capgemini, UST).
6. **Near-duplicate removal** with embeddings (cosine similarity threshold 0.75), then a title-similarity pass.
7. **Compare with the database**: load the latest 3 snapshots from `new_data` and compare against all their articles; drop new articles whose embedding similarity to any stored article is 0.84 or higher; merge the remaining new articles with the articles of the most recent snapshot only; run near-duplicate removal again (threshold 0.82). If the database comparison fails, continue with the new articles only.
8. **Freshness**: drop articles older than 15 days; missing or invalid dates are set to now; keep the latest 400 articles.
9. **Deal-type tagging** (LLM, batches of 8, temperature 0). Zero, one or several categories per article; precision over recall; the deal must be the article's main subject. Skip articles that already have categories.
10. **Domain + priority + refined summary** (LLM, temperature 0.2, 8 parallel workers). Skip articles loaded from the DB that already have a domain and priority.
11. **Sort** by priority (high to low), then published date (newest first).
12. **Save** the full list as one JSON snapshot row in `new_data`.

## 6. Classification rules

### 6.1 Domains (exactly one per article)
Healthcare; Retail; Banking and Financial Services; Technology & Communication; Wealth & Asset Management.
- Healthcare: hospitals, providers, insurers, medical tech, telehealth, EHRs, clinical systems.
- Retail: retail brands, e-commerce, stores, supply chain, POS, inventory, customer experience.
- Banking and Financial Services: banks, payments, lending, insurance, compliance (KYC/AML), fraud, core banking, fintech infrastructure.
- Technology & Communication: tech vendors, cloud/AI platforms, telecom, networking, chips, cybersecurity, software, hardware.
- Wealth & Asset Management: investment management, asset management, portfolio platforms, trading, brokerage, advisory, robo-advisory.
- If both Banking/Financial Services and Wealth & Asset Management signals appear, choose Wealth & Asset Management.

### 6.2 Priority (1 to 5, higher = more important)
- 5: strategic or market-shifting; reshapes competition, large-scale enterprise AI adoption, cross-industry collaboration, regulatory impact.
- 4: major operational or product advancement; substantial capability or infrastructure improvement.
- 3: emerging opportunity or competitive signal; early adoption, new business model.
- 2: incremental improvement or internal optimisation; pilots, localised changes.
- 1: thought leadership, commentary or cultural context; limited actionable value.
- Default 3 if the AI call fails (domain "Unknown").
- **Boosts (capped at 5):** +1 if the article came from a Google News RSS feed; +1 if it has any deal category.

### 6.3 Deal types (zero or more per article)
| Key | UI label | UI colour | Core test |
|---|---|---|---|
| mergers_acquisitions | Mergers & Acquisitions | green | Two companies combine, or one buys a controlling stake. Includes the buyer's side of a divestiture. |
| partnerships | Partnerships | blue | Specific two-party deal; no new company, no equity change. |
| joint_ventures | Joint Ventures | violet | A new, separate, jointly owned entity is created (new name, ownership split). |
| strategic_investments | Strategic Investments | yellow | Minority, non-controlling stake; investee stays independent. |
| spin_offs_divestitures | Spin-offs | amber | The seller's side: a unit is spun off or sold. |
| alliances | Alliances | red | Formal arrangement among three or more organisations around a shared goal or standard. |

Rules: judge by meaning, not keywords; a passing mention of "partner" does not count; a generic funding round with no strategic angle does not count; when unsure, leave the category out.

## 7. Storage (MySQL, database `news_app`)
- Table `new_data`: `id` (auto), `news` (JSON text of the full article list), `updated_at` (set to NOW() on insert). One new row per refresh.
- Table `refresh_status` (name configurable): one row, `id` = 1; columns `running` (0/1), `started_at`, `finished_at`, `message`, `last_run_type`, `trace`, `updated_at`. Created automatically with a "Ready" message if missing.
- Stale lock: if `running` has been 1 for more than 20 minutes, clear it automatically with a message that the worker likely died.
- If the DB is unavailable, status falls back to a local `refresh_status.json` (dev only).

## 8. Routes
| Route | Method | Purpose |
|---|---|---|
| `/` | GET | News grid page (`index.html`) |
| `/api/news` | GET | Latest snapshot: `{count, results, fetched_at}` (IST). Returns `{count: 0, results: []}` when empty. No-cache headers. |
| `/api/refresh` | POST | If already running, return `status: running`. Otherwise take an atomic DB lock (`UPDATE ... WHERE running=0`), start the refresh job, and return `status: started`. If starting fails, record the failure and return HTTP 500. |
| `/api/refresh/status` | GET | `{running, started_at, finished_at, message, last_run_type}`; no-cache headers |
| `/health` | GET | Health check (does not exist in the current app; must be added) |

The app runs locally on port 5000 (Flask default).

## 9. Refresh job
- Runs outside the request: a separate worker script (`refresh_worker.py`) started as a subprocess; if an Azure WebJob trigger URL is configured in the environment, call that instead.
- Requirement: the refresh route takes the DB lock (section 8). The worker then runs the pipeline in section 5 and, when done, must clear the running flag and write finished_at and a message (or the error trace on failure), so the UI stops polling.
- Running `app.py` only starts the web server; it does not fetch news. The UI shows whatever snapshot is already in MySQL.

## 10. UI (`index.html`)
- Title "Latest Tech News" with a logo; grid of news cards; footer "Copyright 2025 UST".
- Sort by: Priority (High to Low) or Date (Newest to Oldest).
- Filter by domain (All + the 5 domains), with a select-domain popup.
- Filter by deal type, with a count per deal type, colour-coded chips as in section 6.3, and a Clear filter control.
- Refresh News button; while a refresh runs, show "Refreshing news - this may take a while..." and poll `/api/refresh/status` until finished, then reload.
- "No news found" empty state.
- Do not include the "UST Relevant" or "News with Insight" filters, or the Insight popup.

## 11. Configuration and secrets
All secrets come from `.env` through python-dotenv. Never hardcode them. Provide `.env.example` with empty values. The current app has these hardcoded; the new tool must not.
- `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD` (database name `news_app`)
- `REFRESH_STATUS_TABLE` (default `refresh_status`), `REFRESH_STATUS_ROW_ID` (default 1), `REFRESH_STALE_MINUTES` (default 20)
- `TAVILY_API_KEY`, `SEARCHAPI_IO_KEY`
- Azure OpenAI chat: `AZURE_OPENAI_CHAT_ENDPOINT`, `AZURE_OPENAI_CHAT_API_KEY`, `AZURE_OPENAI_CHAT_DEPLOYMENT` (`gpt-5.2-chat`) 
- Azure OpenAI embeddings: `AZURE_OPENAI_EMBED_ENDPOINT`, `AZURE_OPENAI_EMBED_API_KEY`, `AZURE_OPENAI_EMBED_API_VERSION`, `AZURE_OPENAI_EMBED_DEPLOYMENT` (`text-embedding-3-small`)
- `AZURE_WEBJOB_TRIGGER_URL`, `AZURE_WEBJOB_USER`, `AZURE_WEBJOB_PASS` (optional)
- Groq: the current app creates a Groq client.
Libraries used today: Flask, mysql-connector-python, requests, httpx, urllib3, beautifulsoup4, feedparser, openai, tavily-python, python-dateutil, numpy, pandas, googlenewsdecoder.

## 12. Decisions for the owner
- **LLM provider (decided):** Azure OpenAI only. Use `gpt-5.2-chat` for all LLM steps (noise re-check, relevance gate, deal-type tagging, domain/priority/summary) and `text-embedding-3-small` for duplicate removal. No other LLM provider is used. 
- **Expected article count per refresh:** 400
- **Expected refresh time:** 25 minutes

## 13. Acceptance checks (compare with the existing AI News Agent)
- Same sources produce a similar number of articles per source.
- All 5 domains and all 6 deal types appear, with similar counts.
- Priority order, the Google News +1 boost and the deal +1 boost behave the same.
- Duplicate removal removes a similar share of articles.
- Articles older than 15 days never appear.
- Refresh time is comparable. A second refresh immediately after the first returns "running" if the first is still going.
- `GET /health` returns OK.
