# ADR-002 — Refresh worker as subprocess with an atomic status-record lock

> Architecture Decision Record. Status **Accepted** by Ardra Arun on 2026-10-13 (human architecture review).

| Field | Value |
|-------|-------|
| **ADR ID** | ADR-002 |
| **Status** | Accepted — Ardra Arun, 2026-10-13 |
| **Date** | 2026-10-13 |
| **Deciders** | (to be named) |
| **Consulted** | Operator (stack statement); BRD owner answers (DQ-012, DQ-018) |
| **Command / trigger** | `/propose-architecture` |
| **Supersedes** | N/A |
| **Superseded by** | N/A |

## Context

- **Problem statement:** How does a manual refresh run the twelve-stage pipeline without holding the HTTP request open, and how is a second refresh prevented?
- **Business / technical drivers:** BRD FR-035 to FR-040 (start, running response, failure 500, status route, worker behaviour); FR-045 (stage order); BR-015 (atomic lock, one refresh at a time); BR-016 (stale lock clears after 70 minutes); FR-039 (worker subprocess, optional WebJob).
- **Current state:** The notes describe a worker script started as a subprocess, with the lock on a status record (notes §8, §9). The app does not yet have this worker.
- **Constraints:** Refresh duration baseline is the average of 3 reference runs, recorded by the owner; tolerance at most 1.5× that average (DQ-004). Refresh must not block the request. The optional WebJob is used only when `AZURE_WEBJOB_TRIGGER_URL` is set (DQ-012).
- **Assumptions:** ASSUMPTION-ARCH-001, ASSUMPTION-ARCH-002 (see proposal).

## Decision

- **Chosen option:** The refresh route takes an atomic lock on the single status record, starts `refresh_worker.py` as a subprocess, and returns. The worker runs stages in FR-045 order, then clears the running flag and writes `finished_at` and the message or error trace. If `AZURE_WEBJOB_TRIGGER_URL` is set, the route calls the WebJob instead of starting the subprocess.
- **Alternatives considered:**

| Option | Pros | Cons | Rejected because |
|--------|------|------|------------------|
| A. Run the pipeline in the request | No process management | Long request; conflicts with FR-039 | Rejected |
| B. Subprocess plus status-record lock (chosen) | Short request; matches BRD; works locally | No supervisor by design (DQ-A4 answer) | — |
| C. In-process background thread | No subprocess | Shares the web process's memory and lifetime; a web restart kills the run; harder to test in isolation | Less isolation than B; no driver for it |
| D. External queue | Durable scheduling | Not named in any source; would be invented | Rejected (no source) |

- **Rationale:** Option B meets FR-039 and BR-015 with the smallest moving parts.

## Consequences

### Positive

- The HTTP request returns quickly with `status: started` or `status: running` (FR-035).
- The lock is a single conditional update on the status record, so concurrent requests cannot both start a run (BR-015).

### Negative / trade-offs

- If the web process restarts during a run, the worker finishes and clears its own running flag (DQ-A4 answer). If the worker dies, BR-016's 70-minute stale-lock rule clears the flag.
- A 70-minute stale limit leaves a long window before a crashed run is cleared. The refresh-duration baseline is not yet recorded (BRD DQ-018 answer; notes say 20 minutes).

### Neutral

- Both start paths (subprocess and WebJob) call the same worker logic.

## Implementation notes

| Area | Impact | Owner | Target |
|------|--------|-------|--------|
| API / contracts | `POST /api/refresh` and `GET /api/refresh/status` per BRD §8 | backend-agent | `/implement-api` |
| UI | Polling script until `running` is false, then reload | frontend-agent | `/implement-ui` |
| Data / migrations | Status record with fields listed in BRD §7; no DDL in this ADR | backend-agent / data-agent | `/implement-api` |
| Infra / CI | Worker process entry point; WebJob settings optional | — | Local only (DQ-A2 answer) |
| Tests | Lock test (second request returns running); stale-lock test at 70 minutes; ordering test (AC-022) | test-agent | `/expand-test-coverage` |
| Documentation | Stale-lock limit recorded as 70 minutes (BRD BR-016) | documentation-agent | — |

## Compliance and security

- **AuthN/Z impact:** `POST /api/refresh` is open to anyone who can reach the server (DQ-A1 answer; known risk RISK-A1). It starts a pipeline run that calls paid LLM and search APIs, so authentication is required before wider exposure.
- **Data classification impact:** Status fields only; no secrets in status.
- **Audit logging impact:** Worker failures written to the status record's error trace, with masking (NFR-006).

## Validation

| Check | Result | Evidence |
|-------|--------|----------|
| Aligns with BRD/NFR | Yes | FR-035–FR-040, FR-045, BR-015, BR-016 |
| Reviewed by architect/SME | Pending | — |
| Rollback path documented | Yes | Disable the refresh route and keep serving the stored snapshot (FR-041) |

## References

| Ref | Locator |
|-----|---------|
| BRD | `artifacts/brd/ai-news-agent-BRD-draft.md` §5 FR-035–FR-040, §6 BR-015–BR-016 |
| Related ADR | ADR-001, ADR-003 |
| Proposal | `docs/architecture/2026-10-13-architecture-proposal.md` |
