# ADR-003 — Azure OpenAI and MySQL as the only external dependencies for LLM and data work

> Architecture Decision Record. Status **Accepted** by Ardra Arun on 2026-10-13 (human architecture review).

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-003 |
| **Status** | Accepted — Ardra Arun, 2026-10-13 |
| **Date** | 2026-10-13 |
| **Deciders** | (to be named) |
| **Consulted** | Owner answers to BRD DQ-001 and DQ-016 |
| **Command / trigger** | `/propose-architecture` |
| **Supersedes** | N/A |
| **Superseded by** | N/A |

## Context

- **Problem statement:** Which LLM and embedding provider, and which data store, does the pipeline use?
- **Business / technical drivers:** BRD DQ-001 answer (Azure OpenAI only, one resource for chat and embeddings; no Claude; no Groq); BRD §7 (MySQL `news_app`, snapshot and status records); FR-016–FR-021 (embedding dedup, LLM steps); FR-023 (one snapshot row per refresh); DQ-016 answer (snapshots never deleted; comparison uses latest 3).
- **Current state:** Notes §11 list the Azure OpenAI settings and a Groq client. The owner excluded Groq.
- **Constraints:** Embeddings are required for duplicate removal (BRD BR-011). The chat model is whatever `AZURE_OPENAI_CHAT_DEPLOYMENT` names (DQ-A3, resolved).
- **Assumptions:** None beyond the proposal's open gaps.

## Decision

- **Chosen option:** Azure OpenAI is the only LLM and embedding provider, using one resource. Chat uses the deployment named by `AZURE_OPENAI_CHAT_DEPLOYMENT`; embeddings use `text-embedding-3-small` from `AZURE_OPENAI_EMBED_DEPLOYMENT`. The client sends only request parameters that the configured deployment supports; it must not send `temperature` or `max_tokens` settings that the deployment rejects. MySQL (`news_app`) is the only data store. ORM and migrations are SQLAlchemy 2.x and Alembic, per techstack.md (DQ-A6 answer). Alembic creates the `new_data` and `refresh_status` tables if they are missing.
- **Alternatives considered:**

| Option | Pros | Cons | Rejected because |
|--------|------|------|------------------|
| A. Azure OpenAI only, MySQL only (chosen) | Single provider; embeddings available; matches the owner's answers | Tied to Azure for LLM work | — |
| B. Claude via Foundry for LLM steps | Alternative model family | No embeddings, so dedup would need a different method | Rejected by the owner (DQ-001) |
| C. Groq for LLM steps | Lower-latency option named in the notes | Excluded by the owner (DQ-001); a second provider adds scope | Rejected by the owner |
| D. SQLite as the data store | No server | Stack names MySQL; notes use MySQL | Rejected (stack) |

- **Rationale:** The owner decided the provider and resource. MySQL is the stack's data store.

## Consequences

### Positive

- One provider and one resource to configure, with embeddings available for duplicate removal.
- One data store for snapshots and status, which keeps the comparison in FR-017 in one place.

### Negative / trade-offs

- Changing the chat deployment changes LLM output (DQ-A3).
- Snapshot rows are never deleted (DQ-016 answer), so storage grows with every refresh. Growth rate is not stated. DQ-016 is to be confirmed by the owner.

### Neutral

- Secrets for the provider and database come from `.env` only (NFR-001).

## Implementation notes

| Area | Impact | Owner | Target |
|------|--------|-------|--------|
| API / contracts | No change to routes | backend-agent | `/implement-api` |
| UI | None | — | — |
| Data / migrations | Snapshot and status records; SQLAlchemy 2.x and Alembic, which create the tables if missing (DQ-A6 answer). No DDL in this ADR. | data-agent / backend-agent | `/implement-api` |
| Infra / CI | Environment variables for the provider and database; local only for this build (DQ-A2 answer) | — | — |
| Tests | Stubbed provider in unit tests; no live calls in CI (AC-022 uses stubs). A unit test confirms that the LLM client builds a valid request for the configured deployment (no unsupported `temperature` or `max_tokens`). | test-agent | `/expand-test-coverage` |
| Documentation | Chat model value is set in environment config only, not in this ADR (DQ-A3) | documentation-agent | — |

## Compliance and security

- **AuthN/Z impact:** Provider keys and database credentials are read from `.env` only (NFR-001). Not stored in any artefact.
- **Data classification impact:** Public news content (no personal data) is sent to the provider for classification and embeddings. Approved for this use by Ardra Arun on 2026-10-13 (DQ-A5).
- **Audit logging impact:** Provider errors logged and skipped per DQ-018; no secret values logged (NFR-006).

## Validation

| Check | Result | Evidence |
|-------|--------|----------|
| Aligns with BRD/NFR | Yes | BRD DQ-001 and DQ-016 answers; §7; FR-016–FR-023; NFR-001 |
| Reviewed by architect/SME | Pending | — |
| Rollback path documented | Partial | Provider can be switched only by a new ADR; snapshot rows are kept, so earlier data survives |

## Open items

- **DQ-A3 (resolved):** the chat model is whatever `AZURE_OPENAI_CHAT_DEPLOYMENT` names. No model name is recorded in this ADR.
- **DQ-A6 (answered):** SQLAlchemy 2.x and Alembic, per techstack.md. Alembic creates the `new_data` and `refresh_status` tables if they are missing.
- **DQ-A5 (cleared):** approved by Ardra Arun on 2026-10-13. The gate no longer blocks the first real refresh.

## References

| Ref | Locator |
|-----|---------|
| BRD | `artifacts/brd/ai-news-agent-BRD-draft.md` §7, §8, DQ-001, DQ-016 (§14.1) |
| Related ADR | ADR-001, ADR-002 |
| Proposal | `docs/architecture/2026-10-13-architecture-proposal.md` |
