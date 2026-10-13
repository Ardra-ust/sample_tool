# LLM Prompts and Pipeline Workflow - AI News Agent

Put this file in `artifacts/intake/supporting/`. It closes plan gap G-01 (LLM prompts and output formats). No secrets are in this file.

## How to use this file
- The pipeline has 12 stages in a fixed order (BRD FR-045). Four stages call the LLM. Their prompts are below, in run order.
- Store each prompt as a separate template file under `modules/api/app/prompts/`. Keep the prompt text **verbatim**, including its wording. Do not rewrite, shorten or "fix" a prompt. If you believe a change is needed, record it as an assumption for the owner.
- `{placeholder}` marks a value filled in at run time. Everything else is literal text.
- Model: the chat deployment named by `AZURE_OPENAI_CHAT_DEPLOYMENT`. Do not write a model name in code or docs. Use the temperature and token limit listed for each prompt. If the deployment rejects a parameter, use the nearest supported equivalent (for example `max_completion_tokens`) and record it as an assumption.
- All four prompts are LLM calls with a system message and a user message, except where stated.
- Non-LLM stages are listed only to keep the order. Their rules are in the BRD (FR/BR IDs given).

## Traceability

| Prompt | Stage | BRD |
|---|---|---|
| A. Title re-check | 3 | FR-012, BR-014 |
| B. Relevance gate | 5 | FR-014, FR-015, BR-017 |
| C. Deal-type tagging | 9 | FR-020, BR-004 to BR-006 |
| D. Domain, priority and summary | 10 | FR-021, BR-001 to BR-003, BR-007 to BR-010 |

---

## Stage 1 - Fetch (no prompt)
Fetch from the four source types (BRD FR-001 to FR-010). Articles from Google News RSS feeds carry `is_google_news = true` and `source_priority_boost = 1`. Stage 10 uses these.

## Stage 2 - Consumer-noise keyword filter (no prompt)
BRD FR-011. Substring match on lowercased title + summary. An article is noise when it has at least one block word and no allow word. Noise articles are not dropped yet. They go to stage 3.

Block words: discount, deal, offer, sale, festive, christmas, diwali, new year, best, top, which model, review, unboxing, price, under, shopping, buy, gaming, game, entertainment, smartphone, laptop, earbuds, headphones, oppo, samsung, xiaomi, iphone, acer, amazon deals, year-end deals

Allow words (lowercase before matching): enterprise, platform, modernization, transformation, AI deployment, cloud migration, POS, supply chain, automation, managed services, IT services, contract, checkout system, inventory system, retail platform, start-up

---

## Stage 3 - Prompt A: LLM re-check of noise-filtered titles

- Input: only the articles that stage 2 marked as noise.
- Batch size: 6. Temperature: 0. Max tokens: 150.
- Item list: the titles of the batch, in order, as a JSON array of strings. `{titles_json}` is that array serialised with `ensure_ascii=False`.
- Output: JSON object with `keep_indices`, a list of integer positions in the batch.
- Parsing: take the text from the first `{` to the last `}` and parse it as JSON. If there is no JSON object, treat the call as failed.
- Post-processing: ignore any index outside the batch. **Safety net:** skip a kept article if its lowercased TITLE contains any of: christmas, festive, new year, buy, discount, deal, offer, gift, sale. Kept articles are restored into the main list.
- On failure (any error): nothing in that batch is restored.

### System message
```
You are filtering news for a TECHNOLOGY SERVICES COMPANY.

Your task:
Given a list of article titles, identify which ones are RELEVANT.

A title is RELEVANT if it involves ANY of the following:
- Enterprise technology, cloud, AI, data platforms
-
- Major service providers, hyperscalers, IT vendors
- Regarding any use case or news related to any AI platforms Openai, gemini ,Lovable,...
- M&A, funding, spin-offs, strategic investment, alliances, joint ventures involving tech/data/AI companies
- Regulations, policy changes impacting technology, healthcare, BFSI, energy, infrastructure
- Large-scale digital transformation, modernization, or infrastructure investments
- Industry-wide technology shifts with commercial or enterprise impact
- Strategic technology analysis or market intelligence
- High-value strategic acquisitions or technology news involving major companies

GIVE EXTRA WEIGHT / STRONGLY PREFER KEEPING any title that describes a
merger, acquisition, joint venture, partnership, strategic
investment, spin-off, or alliance between organizations — these deal-type
signals are HIGH PRIORITY business-development opportunities and should be
kept even if the enterprise-technology angle is only implied (e.g. the deal
involves a retailer, bank, hospital system, or other company that will need
IT integration/consulting support as a result of the transaction).

A title is NOT relevant if it is:
- Consumer shopping, buying advice, product reviews
- Entertainment, gaming, celebrity news
- Generic opinion pieces without enterprise implications
- Personal finance tips or retail investing advice

Respond ONLY in JSON.
```

### User message
```
Return ONLY valid JSON.
Schema:
{
  "keep_indices": [0, 2]
}

Titles:
{titles_json}
```

---

## Stage 4 - Merge and dedupe by link, then title (no prompt)
BRD FR-013. Restored articles from stage 3 are merged back first. Key = link, or title when there is no link. Keep at most 500.

---

## Stage 5 - Prompt B: relevance gate

- Input: all articles after stage 4.
- Batch size: 8. Temperature: 0. Max tokens: 300.
- Item list: for each article in the batch, an object `{"title": ..., "summary": ...}` with the summary cut to the first 300 characters. `{items_json}` is the list serialised with `ensure_ascii=False`. Items have no index field. The index is the position in the batch.
- Output: JSON object with `keep_indices`.
- Parsing: take the text from the first `{` to the last `}` and parse it as JSON. If none is found, treat `keep_indices` as empty.
- Decision per article: keep it if its index is in `keep_indices` **or** its lowercased title + summary contains any force-keep keyword (substring match, list below). Otherwise drop it.
- On failure (any error): keep the whole batch.

Force-keep keywords (BRD FR-014): acqui, merger, merge, m&a, buyout, takeover, divest, spin-off, spinoff, spin off, joint venture, " jv ", partnership, partner with, alliance, strategic investment, invests, investment, funding, raises, raised, series a, series b, series c, seed round, venture, ipo, stake, valuation, unicorn, cloud, azure, aws, gcp, data platform, data center, datacenter, modernization, modernisation, migration, digital transformation, genai, generative ai, llm, ai agent, agentic, machine learning, cybersecurity, cyber security, ransomware, breach, zero trust, core banking, ehr, emr, erp, saas, platform, automation, contract, deal, gcc, outsourc, managed services, integration, infrastructure, chip, semiconductor, analytics, api, accenture, infosys, tcs, cognizant, wipro, capgemini, mphasis, ltimindtree, hcltech, tech mahindra, fractal, ust

### System message
```
You are a relevance gate for a market-intelligence news feed used by a large
IT / technology SERVICES company (like Accenture, Infosys, TCS, Cognizant, UST).

Your job is NOT to decide whether we can sell into the story. Your ONLY job is
to REMOVE clear noise and KEEP everything that could matter to such a company's
business development, competitive intelligence, or market awareness.

KEEP (this is the default) any article about:
- Enterprise tech, cloud, AI / GenAI / LLMs, data platforms, analytics,
  software, telecom, networking, chips/semiconductors, IT infrastructure
- Cybersecurity incidents, breaches, threats, or security tooling
- ANY deal-type news in ANY sector — mergers, acquisitions, funding rounds,
  partnerships, joint ventures, strategic investments, spin-offs, alliances,
  IPOs, stakes, valuations
- Digital transformation, modernization, IT contracts, outsourcing, GCCs
- IT-services peers/competitors — their earnings, deals, hires, strategy, layoffs
- Vendor/platform product or feature launches with enterprise relevance
- Regulation/policy changes affecting technology, BFSI, healthcare, retail, telecom
- Healthcare / retail / BFSI / wealth news that has ANY technology, data,
  digital, funding, or deal angle
- Market/industry trend or funding reports in tech or the verticals above

DROP only clear noise:
- Consumer shopping, buying advice, product reviews, consumer gadget launches
- Entertainment, celebrity, sports, lifestyle, human-interest, animal stories
- Pure clinical/drug/biotech trial or medical results with NO technology, data,
  digital, funding, or deal angle
- Generic personal-finance or retail-investing tips
- Pure opinion/philosophy/culture pieces with no organizational or tech action

WHEN IN DOUBT, KEEP THE ARTICLE. A later stage does the precise filtering, so
recall matters more than precision here.

Respond ONLY in JSON.
```

### User message
```
Return ONLY valid JSON.
Schema:
{
  "keep_indices": [0, 2]
}

Articles:
{items_json}
```

---

## Stage 6 - Embedding near-duplicate removal plus title pass (no prompt)
BRD FR-016, BR-011. Embedding input text per article: `{title} — {summary} ({source})`, sent in batches of 10 to the embeddings deployment (`AZURE_OPENAI_EMBED_DEPLOYMENT`). Similarity threshold 0.75. Then the title pass as defined in BR-011. If this stage fails, return the list unchanged.

## Stage 7 - Database comparison, merge, second duplicate removal (no prompt)
BRD FR-017, FR-018, BR-011. Same embedding input text. Compare against the latest 3 snapshots at 0.84. Merge the remaining new articles with the most recent snapshot only. Run stage 6 again at 0.82. Before this stage, copy `published` to `published_at` where it is missing.

## Stage 8 - Freshness (no prompt)
BRD FR-019, BR-012, BR-013. Drop articles older than 15 days. Missing or invalid dates are set to the current time. Keep the last 400 articles.

---

## Stage 9 - Prompt C: deal-type tagging

- Input: articles after stage 8 that do not already have a `deal_categories` list.
- Batch size: 8. Temperature: 0. Max tokens: 800.
- Valid category keys (exact spelling): `mergers_acquisitions`, `partnerships`, `joint_ventures`, `strategic_investments`, `spin_offs_divestitures`, `alliances`.
- Item list: for each article, `{"index": <position in batch>, "title": ..., "summary": ...}` with the summary cut to the first 400 characters. `{items_json}` is the list serialised with `ensure_ascii=False`.
- Output: JSON object `{"results": [{"index": n, "categories": [...]}]}`.
- Parsing: take the text from the first `{` to the last `}` and parse it as JSON. Keep only categories that are valid keys. If `categories` is not a list, use `[]`. An article with no result gets `[]`.
- Result per article: `deal_categories` = the list; `is_deal_news` = true when the list is not empty.
- On failure (any error): the whole batch gets `deal_categories = []` and `is_deal_news = false`.
- Colours for the UI chips: mergers_acquisitions green, partnerships blue, joint_ventures violet, strategic_investments yellow, spin_offs_divestitures amber, alliances red.

### System message
`{definitions_block}` is the "Category definitions" text below.
```
You are a precise business-news classifier for a technology services company.

For each article (title + summary), decide which of the following DEAL-TYPE
categories it GENUINELY belongs to, based on what the article's core news
actually is — NOT based on the presence of any particular word or phrase.
An article can belong to ZERO, ONE, or MULTIPLE categories. Most articles
will belong to none of them — only tag categories that truly apply.

CATEGORIES:
{definitions_block}

STRICT RULES:
- Judge by meaning and context, not by keyword matching. A word like
  "partner", "alliance", "merger", or "invests" appearing in passing, in an
  unrelated context, or about something that already happened long ago and
  isn't the actual subject of THIS article does NOT count.
- The deal must be the ARTICLE'S MAIN SUBJECT, not a minor mention.
- If genuinely unsure whether a category applies, leave it out — precision
  matters more than recall.
- Use ONLY these category keys (exact spelling): mergers_acquisitions, partnerships, joint_ventures, strategic_investments, spin_offs_divestitures, alliances.

Respond ONLY in JSON.
```

### User message
```
Return ONLY valid JSON in this exact schema:
{
  "results": [
    {"index": 0, "categories": ["mergers_acquisitions"]},
    {"index": 1, "categories": []}
  ]
}

Articles:
{items_json}
```

### Category definitions (`{definitions_block}`)
```
- "mergers_acquisitions" (Mergers & Acquisitions): A MERGER is when two companies combine to form a single new entity, typically pooling assets, operations, and ownership — shareholders of both original companies end up holding shares in the new combined company, and no single party is described as 'buying' the other. An ACQUISITION is when one company purchases a controlling stake (majority or full ownership) in another company, which then becomes a subsidiary or is absorbed into the acquirer and stops operating as an independent company. This applies regardless of deal size, and applies to the BUYER'S side of a sale of a business unit/subsidiary as well as a full-company acquisition. Do NOT tag for a minority (non-controlling) stake or investment where the target remains independently operated (see 'strategic_investments'). Do NOT tag the SELLER'S side of a divestiture where the seller is simply shedding a unit — tag that side under 'spin_offs' only if it results in a new independent/publicly traded company; otherwise it is out of scope for these categories.

- "partnerships" (Partnerships): Two (or a small number of) organizations agree to WORK TOGETHER on a specific, named initiative — e.g. a go-to-market deal, technology integration, distribution agreement, reseller/channel deal, licensing deal, or co-branded offering. KEY TEST — no new company is formed and no equity/ownership changes hands; each party keeps operating fully independently and this is purely a contractual/commercial collaboration. Do NOT tag just because the word 'partner' appears casually or generically (e.g. 'valued partner', 'our partners in the region') with no specific deal described. Do NOT tag if the companies are forming a new jointly owned entity (that's 'joint_ventures') or if it's a broad, three-or-more-party consortium/standard-setting effort (that's 'alliances'), or if equity or cash changes hands as an investment (that's 'strategic_investments').

- "joint_ventures" (Joint Ventures): A JOINT VENTURE is when two or more organizations pool resources — capital, technology, personnel, or assets — to create a NEW, SEPARATE, JOINTLY-OWNED business entity, while each parent company continues to exist and operate independently outside of that new entity. The new entity has its own name, its own ownership structure (split between the parents, e.g. 50-50 or 60-40), and is typically set up to pursue a specific shared business goal — such as entering a new market, developing a product, or combining complementary strengths — that would be harder for either parent to pursue alone. KEY TEST — look for a NEW LEGAL ENTITY: a new company name, a stated ownership split, a newly registered/incorporated business, or explicit phrases like 'joint venture', 'JV', 'form a new company', 'newly formed entity'. If there is no new entity being created, it is NOT a joint venture — it is at most a 'partnerships' (simple two-party collaboration) or 'alliances' (broad multi-party effort). Do NOT tag a supply deal, licensing deal, or technology integration as a JV just because it's described as 'strategic' or 'deep' — those stay in 'partnerships' unless a new jointly-owned company is explicitly created. Do NOT tag if one party is simply buying a stake in an existing company (that's 'strategic_investments' or 'mergers_acquisitions', depending on the size of the stake).

- "strategic_investments" (Strategic Investments): A STRATEGIC INVESTMENT is when one organization (or an investor with a clear corporate/strategic angle) puts capital into another company by taking a MINORITY, NON-CONTROLLING stake — without acquiring the company, merging with it, or forming a new jointly-owned entity. The investee company keeps operating fully independently, retains its own management and board control, and is NOT absorbed, majority-owned, or consolidated into the investor. The purpose is typically to gain financial upside, secure a commercial or technology relationship, or support a company strategically aligned with the investor's business — rather than to take over its operations. KEY TEST — after the deal, does the investee remain independently run? If yes, and the investor holds a minority position, it's a strategic investment. Do NOT tag pure consumer/retail investing content, or a generic VC/financial 'funding round' with no strategic/corporate investor angle — that falls outside these categories. Do NOT tag if the stake is a controlling/majority stake (that's 'mergers_acquisitions') or if it results in a new co-owned company (that's 'joint_ventures').

- "spin_offs_divestitures" (Spin-offs & Divestitures): This category covers the SELLER'S SIDE of a company shedding a business unit, division, or subsidiary — whether it becomes a new independent company (spin-off) or is sold to another company. A SPIN-OFF is when a company separates or carves out a unit into its OWN INDEPENDENT company, typically by distributing shares of the new entity to existing shareholders or listing/IPO'ing it separately — with NO OTHER COMPANY buying the unit. Signal words: 'spin off', 'spin-off', 'separates into two independent companies', 'to be listed as a standalone company', 'carve-out IPO'. A DIVESTITURE is when a company sells or disposes of a unit, division, or subsidiary TO ANOTHER EXISTING COMPANY, for cash, stock, or other consideration, as the SELLER in that transaction. KEY TEST — is a brand-new standalone company being created (spin-off), or is the unit being absorbed into an already-existing buyer (divestiture)? Either way, tag this category if the article's focus is the SELLER separating from the unit. Do NOT tag the BUYER'S side of a divestiture here — from the buyer's perspective that story belongs in 'mergers_acquisitions', since the buyer is acquiring a business. Do NOT tag a simple restructuring, rebranding, or internal reorganization where no unit is being separated, sold, or made independent.

- "alliances" (Alliances): An ALLIANCE is a FORMAL arrangement among THREE OR MORE organizations that come together around a shared goal, industry standard, ecosystem, or common cause — broader in scope and less transactional than a two-party commercial deal. Unlike a partnership, an alliance is not usually about one specific bilateral deal (like a distribution agreement between two companies); it's about multiple, often competing or unrelated, organizations coordinating together on something bigger than any single relationship — such as setting a technical standard, forming an industry coalition, or building a shared ecosystem that others can join. If only TWO organizations are named and there's a specific commercial deal between them, that's 'partnerships', not 'alliances', even if the article uses the word 'alliance' loosely or informally. An alliance requires a genuinely multi-party structure (three or more distinct organizations) forming around a shared purpose. Do NOT tag a simple two-company integration, reseller deal, or licensing agreement here just because it sounds broad or industry-wide — that belongs in 'partnerships'. Do NOT tag if the group is forming a single new jointly-owned entity together (that's 'joint_ventures').
```

---

## Stage 10 - Prompt D: domain, priority and refined summary

- Input: every article after stage 9 that does not already have both a `domain` and a `priority`. Articles loaded from the database that have both are returned unchanged.
- One call per article. Run with 8 parallel workers. Temperature: 0.2. No max-token limit.
- Placeholders: `{title}` is the article title. `{summary}` is the stored summary (full, not cut).
- Output: one JSON object with `refined_summary`, `domain`, `priority`.
- Parsing: remove ```` ```json ```` and ```` ``` ```` fence markers, trim, and parse the whole text as JSON.
- Result per article:
  - `summary` = `refined_summary`, or the original summary if missing.
  - `domain` = the returned `domain`, or "Unknown" if missing.
  - `priority` = `int(priority)`, or 3 if missing.
- Boosts, applied in this order, each capped at 5:
  1. If `is_google_news` is true: add `source_priority_boost` (1).
  2. If `deal_categories` is not empty: add 1.
- On failure (any error, including invalid JSON): `domain` = "Unknown", `summary` unchanged, `priority` = 3 plus the same two boosts, capped at 5.
- The deal-type boost needs stage 9 to have finished. Do not run this stage before it.

### System message
```
You are a precise AI news classifier and summarizer.
```

### User message
```
You are an AI system that performs two precise tasks for each news article:

### Task 1: Summary Refinement
- Review the provided summary.
- If the summary appears incomplete, abruptly cut off, or missing key context, rewrite it into a **complete and concise summary (2–3 sentences)** that clearly explains the core message of the article.
- If the summary is already coherent and complete, leave it mostly unchanged — only polish grammar or phrasing slightly.

### Task 2: Classification
Then, classify the article into the following three fields:

1. **domain** — which business domain or sector the article primarily relates to.
2. **priority** — a score from 1 to 5 indicating its importance and impact.

Domains: Healthcare, Retail, Banking and Financial Services, Technology & Communication, Wealth & Asset Management.

### Domain Selection Rules (Simple Version)
Choose the MOST SPECIFIC domain based on what the article is mainly about:

Healthcare  - Hospitals, providers, insurers, medical tech, telehealth, EHRs, clinical systems.
Retail  - Retail brands, e-commerce, stores, supply chain, POS, inventory, customer experience.
Banking and Financial Services  - Banks, payments, lending, insurance, compliance (KYC/AML), fraud, core banking, fintech infrastructure.
Technology & Communication  - Tech vendors, cloud/AI platforms, telecom, networking, chips, cybersecurity, software, hardware.
Wealth & Asset Management  - Investment management, asset management, portfolio platforms, trading, brokerage, advisory, robo-advisory.

**If both BFSI and WAM signals appear → choose Wealth & Asset Management** (more specific).

### Scoring Guide (Business Perspective)

5 — Strategic / Market-Shifting Breakthrough
- Reshapes competitive landscape or industry direction
- Signals large-scale transformation in enterprise AI adoption
- Contacts between companies or AI adoption
- Reflects cross-industry collaboration or regulatory impact
- Drives long-term strategic change

4 — Major Operational or Product Advancement
- Introduces substantial improvement in AI capabilities or infrastructure
- Enhances enterprise productivity, efficiency, or scalability
- Represents major product or platform-level innovation
- Has measurable impact on core business operations

3 — Emerging Opportunity or Competitive Signal
- Highlights sector-specific innovation or early adoption
- Indicates potential for competitive advantage or market entry
- Demonstrates meaningful directional trend or new business model
- Shows expanding enterprise relevance

2 — Incremental Improvement or Internal Optimization
- Describes small-scale or localized improvements
- Covers internal automation or pilot-level deployment
- Represents limited strategic or market impact
- Operationally beneficial but not transformation-driven

1 — Thought Leadership, Commentary, or Cultural Context
- Focuses on opinions, predictions, or ethical discussions
- Contains conceptual or narrative viewpoints without business application
- Provides contextual understanding but limited actionable value
- Relates to societal perception or cultural framing of AI

### Output Format
Return ONLY a valid JSON object — no code fences, no extra text.

Example:
{
"refined_summary": "OpenAI has announced a new strategic partnership with Microsoft to scale AI infrastructure, marking a major milestone in enterprise AI adoption.",
"domain": "Technology & Communication",
"priority": 4
}

Title: {title}
Summary: {summary}
```

---

## Stage 11 - Sort (no prompt)
BRD FR-022, BR-018. Priority high to low, then published date newest first.

## Stage 12 - Save (no prompt)
BRD FR-023. Save the full sorted list as one JSON snapshot row in `new_data`. If nothing was fetched, do not save an empty snapshot.

---

## Not included on purpose (out of scope, BRD section 2)
Do not build any of these, and do not add prompts for them:
- Importance (Yes/No) classification and its domain rule blocks.
- Bucket classification and keyword extraction.
- Trend summaries (this includes all GDELT calls).
- Insight generation, including the UST platform knowledge text and the web-search call.
