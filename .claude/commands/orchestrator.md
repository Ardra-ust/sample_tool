# /orchestrator

## Objective

Drive the full command spine **end-to-end in one invocation**, from `/generate-brd` through `/application-summary`, pausing at every human gate instead of guessing past it. This is a **thin sequencing wrapper**, not a new governed command: every step still runs through `orchestrator-agent → <that command's own primary agent> → <its subagents>`, under **that command's own Definition of Done, rules, and clarification protocol** (`.claude/commands/<step>.md`). `/orchestrator` adds no new agents, no new write permissions, and no shortcut past a gate — it only sequences, checks gates, and pauses/resumes.

Not counted in the kit's "12 shipped commands" (`KIT-SCOPE.md`) — it is a convenience sequencer over them. See the pointer added to `KIT-SCOPE.md`, `.claude/commands/README.md`, and `CLAUDE-FLOW.md`.

## Execution engine

`/orchestrator` runs as the saved workflow at `.claude/workflows/orchestrator.js` — invoke it with `Workflow({name: 'orchestrator', args: {requirements, module, sprintId, sprintGoal, sprintDuration, referenceUrl, sprintItem, skipArchitecture, evalMode, from}})`, passing through whichever flags below were supplied. The script mirrors the phase table, model routing, and gates on this page exactly — one agent per phase, `parallel()` for step 4a/4b, a bounded 3-attempt loop for step 8i — and returns a pause descriptor the moment a gate isn't met instead of guessing past it. It shows in `/workflows` as phase → model → what it does per the table below. Do not hand-roll the sequencing described in this file when the workflow is available; call it and relay its result (paused stage + reason, or final completed-through state) to the user.

## Sequence (per the approved spine)

```
/generate-brd
  → /propose-architecture          (satellite; runs, does not block /plan-sprint)
  → /plan-sprint                   (STOP until Approved)
  → /generate-ui-design  ∥  /implement-api      (parallel; both gated only by plan Approved)
  → /implement-ui
  → /expand-test-coverage          (STOP until test-package Approved)
  → /run-tests
  → /run-eval
  → /close-eval-gaps               (inner loop of /run-eval; walks fix-queue until auto_fix clear or needs_human)
  → /review-changes
  → /application-summary
```

This matches `CLAUDE-FLOW.md` exactly; `/close-eval-gaps` is not a separate spine hop here because `/run-eval` already invokes it per its own contract.

## ⚠ Model-routing deviation (read before first run)

Rule 4 (`CLAUDE.md`) assigns: **opus** — orchestrator/intake-judgment/review/security/release/quality-coordination; **sonnet** — implementation *and artifact generation*; **haiku** — narrow mechanical collectors/formatters only.

Per explicit operator instruction, this command overrides the **artifact-generation** half of that split for this run, and additionally pins the UI-design/implement/run-eval/close-eval-gaps phases to sonnet-5 in full (second operator instruction — no more mixed haiku/sonnet within those specific phases):

| Bucket | Model | Rationale |
|---|---|---|
| Pure document / artifact authoring (BRD, architecture proposal, sprint plan, application summary, expand-test-coverage design docs, audit prose) | **`claude-haiku-4-5-20251001`** | Operator request — cheaper/faster for prose-authoring phases |
| UI design brief + all code/implementation generation + eval + eval-fix (`/generate-ui-design`, `/implement-api`, `/implement-ui`, `/run-tests`, `/run-eval`, `/close-eval-gaps`) | **`claude-sonnet-5`** | Operator request — operator judged sonnet-5 gives better results on these specific phases, including their doc/test-case sub-outputs (no haiku split left within these phases) |
| Orchestration judgment, gate enforcement, review, security | **opus (session default)** | Left unchanged — rule 4 scopes this to adjudication, not document creation; downgrading gate judgment was not requested and would weaken the human-gate guarantees this kit exists to enforce |

This **deviates from rule 4** for the artifact-generation bucket (rule 4 default: sonnet) and for `/run-eval`'s quality-coordination bucket (rule 4 default: opus). It is not silently absorbed: the first phase-changing step below must have its `harness-updater` call log a decision row in `docs/harness/decisions.md` (append-only) reading approximately:

> `Model routing override for /orchestrator run <date>: document-authoring phases use haiku-4.5; /generate-ui-design, /implement-api, /implement-ui, /run-tests, /run-eval, /close-eval-gaps use sonnet-5 in full (rule 4 default is sonnet for artifact generation, opus for quality-coordination). Orchestration/review/security unchanged at opus. See .claude/commands/orchestrator.md.`

If you want strict rule-4 compliance instead (sonnet for artifact generation, opus for quality-coordination), tell the orchestrator-agent to ignore the table below and it reverts to rule 4 as written.

## Phase table — agents and model per step

| # | Command | Primary agent | Key subagents | Model | Human gate |
|---|---------|---------------|----------------|-------|------------|
| 0 | Preflight | orchestrator-agent | — | opus | config.yaml present & unplaceholdered, or STOP |
| 1 | `/generate-brd` | requirements-agent | transcript-analyzer → supporting-doc-synthesizer → open-questions-cataloger → brd-writer | **haiku-4.5** | BRD must reach **Accepted** (or waiver) before step 3 |
| 2 | `/propose-architecture` | planner-agent → documentation-agent (mode `architecture`) | open-questions-cataloger → tech-stack-advisor → architecture-proposal-writer | **haiku-4.5** | none (satellite; does not block) |
| 3 | `/plan-sprint` | planner-agent (mode sprint) | gap-identifier, sprint-planner, requirement-traceability-mapper, open-questions-cataloger | **haiku-4.5** | plan must reach **Approved** before steps 4–5 |
| 4a | `/generate-ui-design` | frontend-agent (mode `design-mockup`) | reference-site-capturer → ui-design-brief-writer → ui-mockup-generator | **sonnet-5** (operator override — was haiku) | not a blocking gate, but `/orchestrator` **asks** for reference_url/screenshot before running this step (see Runtime Inputs) — blank/declined → Open DQ, proceed to `/implement-ui` from UX spec/story table |
| 4b | `/implement-api` | backend-agent + api-agent | data-agent/schema-migration-generator (if persistence changes), backend-module-generator, validation-chain-generator, test-case-generator, br-coverage-validator, backend-test-generator, api-test-runner | **sonnet-5** (all of it, incl. test-case doc bodies — operator override, no haiku split in this phase) | none beyond plan Approved (runs parallel to 4a) |
| 5 | `/implement-ui` | frontend-agent | mockup-to-component, flask-template-generator, test-case-generator, e2e-scenario-writer, br-coverage-validator, ui-test-runner | **sonnet-5** (all of it, incl. test-case doc bodies — operator override, no haiku split in this phase) | wiring gate (internal, not a human gate) |
| 6 | `/expand-test-coverage` | quality-agent + test-agent (design mode) | test-intake-normalizer (untrusted only), automation-companion-author, tc-traceability-mapper, tc-completeness-validator, tc-step-quality-validator, bdd-scenario-expander, br-coverage-validator | **haiku-4.5** | `docs/quality/test-package-review.md` must reach **Approved** before step 7 |
| 7 | `/run-tests` | quality-agent + backend-agent + frontend-agent + test-agent | backend-test-generator, e2e-codegen, api-test-runner, ui-test-runner, coverage-analyzer, e2e-defect-analyzer, e2e-self-healer | **sonnet-5** (all of it, incl. defect-analysis prose — operator override, no haiku split in this phase) | none (Approved package already gates entry) |
| 8 | `/run-eval` | quality-agent | eval-agent (`incremental` default) | **sonnet-5** (operator override — rule 4 default is opus for quality-coordination) | completeness ledger required; `auto_fix` must clear or `needs_human` before step 9 |
| 8i | `/close-eval-gaps` (inner loop, auto-invoked by 8) | orchestrator-agent | owning agent per `auto_fix` item (backend/frontend/api/quality/documentation/eval-agent), re-run via eval-agent | **sonnet-5** (all of it — operator override, no haiku split in this phase) | any item still `needs_human` at attempt 3 → **STOP** |
| 9 | `/review-changes` | code-review-agent + security-agent | security-reviewer, coverage-analyzer, br-coverage-validator | opus (unchanged — review/security judgment per rule 4) | Block verdict → **STOP**, do not run step 10 |
| 10 | `/application-summary` | documentation-agent (mode summary) | application-summary-writer, harness-updater | **haiku-4.5** | none (terminal step) |

`harness-updater` and `audit-trail-writer` run at opus/haiku per their own narrow-mechanical role in rule 4 — they are formatters over already-decided content, not authors of new prose; leave them at haiku-4.5 for cost, no material judgment there.

## Runtime Inputs

### Required (asked by each phase's own Clarification Protocol, not upfront)
- Requirements source for `/generate-brd` — default folder: **`requirements/`** at repo root (see `requirements/README.md`, created alongside this command). Convention: `requirements/transcripts/` and `requirements/supporting/` if you separate them; otherwise drop everything in `requirements/` and `requirements-agent` classifies it.
- Sprint metadata for `/plan-sprint` (sprint ID, goal, duration) — orchestrator does not front-load this; `/plan-sprint`'s own Clarification Protocol asks when it reaches that step.
- `reference_url` (or `screenshot_path`) for `/generate-ui-design` — **`/orchestrator` asks once, right before entering step 4a**, matching `/generate-ui-design`'s own Clarification Protocol (it does not silently skip past this the way it used to): "Do you have a reference URL or a screenshot for this screen's UI design? (leave blank to skip mockup generation)." Accepts either a **file path** or a **pasted/dragged image in chat** — a pasted image is saved to `artifacts/design/<date>-reference-capture.png` first and that path is used as `screenshot_path`. A blank/declined answer is **not** a gate failure — it registers Open DQ and step 4a proceeds to `/implement-ui` using the UX spec / story UI table instead of a generated mockup. A supplied answer is passed through as `reference_url`/`screenshot_path` into step 4a.

### Optional flags
- `--requirements=<path>` — override the default `requirements/` root
- `--module=<name>` — bounded context, passed through to `/generate-brd` and `/plan-sprint`
- `--from=<command>` — force resume at a specific spine step (still gate-checked; will not skip an unmet gate)
- `--skip-architecture` — omit step 2 (it is already non-blocking; use this only to save the run)
- `--eval-mode=full-sweep` — pass through to `/run-eval` (default `incremental`)

## Preflight (step 0, every invocation)

1. Confirm `.claude/config.yaml` exists and contains no `<placeholder>` tokens (rule 01). If missing or placeholdered → **STOP**: "Fill `.claude/config.yaml` from `.claude/config.yaml.example` before running `/orchestrator` past `/generate-brd`." `/generate-brd` itself does not need it (no product code), so intake-only runs may proceed; anything from `/plan-sprint` onward refuses per rule 01/09 until it's filled.
2. Read `docs/harness/progress.md` (only `harness-updater` writes it) to find the first non-**Done** pipeline stage. That stage is the resume point unless `--from` overrides it.
3. Confirm the resume point's own gate is actually satisfied (BRD Accepted, plan Approved, test-package Approved, etc. — read the artifact status directly; do not trust progress.md's label alone). If not satisfied, **STOP** and name the exact gate.

## Execution loop (per phase)

1. Route the phase's command through **orchestrator-agent by explicit name** (rule 9) using that command's own `.claude/commands/<name>.md` contract verbatim — do not restate or loosen its DoD here.
   - **Before step 4a specifically:** ask the user once for `reference_url` or `screenshot_path` (per Runtime Inputs above) instead of registering Open DQ unasked. Only if the answer is blank/declined does it fall through to Open DQ + proceed.
2. Apply the model assignment from the phase table above as a routing hint to orchestrator-agent for that phase's primary + subagents.
3. Let that command's own Plan→Act→Validate/Observe→Refine/Reflect loop run to its own ceiling (max 3) — `/orchestrator` does not add a second retry layer on top.
4. On completion, check that command's own Next-command condition:
   - **Human gate not yet met** (Draft BRD, Proposed plan, Pending-Approval test package, `needs_human` fix-queue item, Block verdict on review) → print the pause banner (below), **STOP the whole run**. Do not proceed to the next phase.
   - **Gate met / no gate** → continue to the next phase in sequence (steps 4a/4b run as two parallel Agent-tool calls since both depend only on plan Approved and not on each other).
5. Phase-changing steps (1, 3, 4b, 5, 6, 7, 8, 8i, 9, 10 per rule 10) must each end with their own `harness-updater` call — `/orchestrator` does not write `docs/harness/**` itself and does not skip this because it's mid-sequence.

## Pause banner (used at every stop)

```
⏸ /orchestrator paused after /<last-completed-command>.
Gate: <what is required — e.g. "BRD status is Draft — Pending Domain Review; needs Accepted or a dated waiver in docs/harness/decisions.md">
Resume: once resolved, run /orchestrator again (or /orchestrator --from=<next-command>) — it re-checks the gate and continues.
```

## Human gates enforced (rule 11 / CLAUDE-FLOW.md, unchanged — this command adds no new ones except config.yaml)

| Gate | Blocks |
|------|--------|
| `.claude/config.yaml` missing/placeholder | Everything past `/generate-brd` |
| BRD **Accepted** (or dated waiver) | `/plan-sprint` |
| Plan **Approved** | `/implement-api`, `/implement-ui`, `/generate-ui-design` |
| Test-package **Approved** | `/run-tests` |
| Completeness ledger + `auto_fix` closed or `needs_human` | `/review-changes` |
| Review verdict ≠ Block | `/application-summary` |
| Any `deny`/`ask` permission or secret access | Immediate stop, any phase (rule 4, CLAUDE.md) |

`/orchestrator` never self-approves a BRD, plan, or test package, and never marks a `needs_human` item auto-fixed. Those require a human editing the artifact's status field directly, then re-running `/orchestrator`.

## Enforce Rules

00, 01, 02, 07, 09, 10, 11, 22, 31 (cited by `/generate-brd`/`/expand-test-coverage` only, per that rule's own scope), kit-governance, techstack — plus each individual phase's own rule list from its command file (03/04/05/08/13/14/15/17/21/23 as applicable per phase). `/orchestrator` does not narrow or add to any phase's rule set.

## Definition of Done

- [ ] Ran every phase from the resume point up to either `/application-summary` **Done** or the first unmet human gate
- [ ] Never advanced past a gate without reading the actual artifact status (not just progress.md's cached label)
- [ ] Every phase-changing step's `harness-updater` call fired (rule 10) — `/orchestrator` did not write harness itself
- [ ] Model-routing deviation logged as a `docs/harness/decisions.md` row on first phase-changing call of the run
- [ ] Step 4a: user was asked for reference_url/screenshot before running it (not silently skipped); if declined/blank, absence registered as Open DQ, not silently dropped
- [ ] Parallel branch (4a/4b) both attempted
- [ ] `artifacts/audit/<date>-orchestrator-agent-orchestrator.md` written, listing: phases completed this run, phase paused at (if any), gate/reason, and pointers to each phase's own audit file
- [ ] User told the exact resume command if paused, or the final Next command if the whole spine completed

## Outputs

- `artifacts/audit/<date>-orchestrator-agent-orchestrator.md` — run-level summary (this command's own audit; each phase still writes its own per its command file)
- All per-phase outputs, unchanged from their own command files

## Next command

```
✅ /orchestrator run complete through /<last-completed-command>.
**Next command:** <either "/orchestrator (resume)" with the named gate to clear, or the terminal "/application-summary already Done — nothing further in this spine.">
```
