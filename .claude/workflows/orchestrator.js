export const meta = {
  name: 'orchestrator',
  description: 'Runs the full /generate-brd -> /application-summary spine end-to-end, pausing at every human gate',
  whenToUse: 'Invoked by the /orchestrator command. One agent per spine phase; stops and returns a pause reason at the first unmet human gate instead of guessing past it.',
  phases: [
    { title: 'Preflight', detail: 'check config.yaml + docs/harness/progress.md to find the resume point', model: 'opus' },
    { title: 'Generate BRD', detail: 'requirements-agent authors BRD from requirements/ intake', model: 'haiku' },
    { title: 'Propose Architecture', detail: 'planner-agent + documentation-agent — satellite, never blocks', model: 'haiku' },
    { title: 'Plan Sprint', detail: 'planner-agent turns Accepted BRD into sprint backlog', model: 'haiku' },
    { title: 'Generate UI Design', detail: 'frontend-agent design-mockup — satellite, never blocks', model: 'sonnet' },
    { title: 'Implement API', detail: 'backend-agent + api-agent — schema, contract, backend slice, tests run', model: 'sonnet' },
    { title: 'Implement UI', detail: 'frontend-agent — components, FE<->BE wiring gate, UI/e2e tests', model: 'sonnet' },
    { title: 'Expand Test Coverage', detail: 'quality-agent — case bodies, matrix, BR-coverage gate, approval package', model: 'haiku' },
    { title: 'Run Tests', detail: 'quality/backend/frontend-agent — generate + execute the Approved package', model: 'sonnet' },
    { title: 'Run Eval', detail: 'eval-agent — completeness ledger + fix-queue', model: 'sonnet' },
    { title: 'Close Eval Gaps', detail: 'owning agents fix auto_fix:true items, re-eval, up to 3 attempts', model: 'sonnet' },
    { title: 'Review Changes', detail: 'code-review-agent + security-agent — read-only review, Block gates summary', model: 'opus' },
    { title: 'Application Summary', detail: 'documentation-agent — delivery summary, harness update', model: 'haiku' },
  ],
}

// Mirrors .claude/commands/orchestrator.md exactly: same sequence, same gates, same
// model routing. This script only decides WHICH agent runs WHEN; every agent still
// follows its own command file's Definition of Done, rules, and clarification protocol.

const cfg = args || {}

const STAGE_ORDER = [
  'generate_brd', 'propose_architecture', 'plan_sprint', 'parallel_branch',
  'implement_ui', 'expand_test_coverage', 'run_tests', 'run_eval',
  'review_changes', 'application_summary', 'done',
]
const idx = (stage) => { const i = STAGE_ORDER.indexOf(stage); return i === -1 ? 0 : i }

const STATUS_SCHEMA = {
  type: 'object',
  properties: {
    status: { type: 'string', description: 'short status label read from the artifact itself, e.g. Draft, Accepted, Proposed, Approved, PASS, FAIL' },
    gate_met: { type: 'boolean', description: 'true only if the human gate for this phase (if any) is actually satisfied' },
    blocking_reason: { type: 'string' },
    artifact_paths: { type: 'array', items: { type: 'string' } },
    audit_path: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['status', 'gate_met'],
}

const PREFLIGHT_SCHEMA = {
  type: 'object',
  properties: {
    config_ready: { type: 'boolean' },
    config_blocking_reason: { type: 'string' },
    start_stage: { type: 'string', description: 'one of: generate_brd, propose_architecture, plan_sprint, parallel_branch, implement_ui, expand_test_coverage, run_tests, run_eval, review_changes, application_summary, done' },
    notes: { type: 'string' },
  },
  required: ['config_ready', 'start_stage'],
}

const EVAL_SCHEMA = {
  type: 'object',
  properties: {
    ledger_complete: { type: 'boolean' },
    open_autofix_count: { type: 'integer' },
    needs_human_present: { type: 'boolean' },
    audit_path: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['open_autofix_count'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    verdict: { type: 'string', description: 'Approve, Conditionally Approve, or Block' },
    blocking: { type: 'boolean', description: 'true only for a Block verdict' },
    audit_path: { type: 'string' },
    notes: { type: 'string' },
  },
  required: ['verdict', 'blocking'],
}

function base(commandFile, extra) {
  return `Act as orchestrator-agent per .claude/agents/orchestrator-agent.md, routing through the primary agent named in .claude/commands/${commandFile}. Follow that command file's Definition of Done, Enforce Rules, Use Skills, and Clarification Protocol exactly as written there — do not restate, loosen, or skip any of it. Never self-approve a human gate (BRD Accepted, plan Approved, test-package Approved). Write real artifacts to the paths that command file specifies; do not simulate or fabricate results. ${extra} Read the actual artifact/file content before reporting the schema fields — do not infer status from memory.`
}

function pauseResult(stage, result) {
  return {
    paused: true,
    stoppedAt: stage,
    status: result && result.status,
    blocking_reason: result && (result.blocking_reason || result.notes),
    message: `Paused after "${stage}". Resolve the named gate, then re-run /orchestrator — it re-reads docs/harness/progress.md and the artifact itself, and continues from here.`,
  }
}

phase('Preflight')
const preflight = await agent(
  base('orchestrator.md', 'Confirm .claude/config.yaml exists and has no <placeholder> tokens (rule 01; .claude/config.yaml.example is the template). Read docs/harness/progress.md (only harness-updater writes it) to find the first non-Done pipeline stage, then confirm that stage\'s own gate directly against the real artifact (BRD status, sprint-plan status, test-package-review status, fix-queue, review verdict) rather than trusting the cached label. Map the result to exactly one of the enumerated start_stage values.'),
  { phase: 'Preflight', model: 'opus', schema: PREFLIGHT_SCHEMA },
)

const startIdx = cfg.from ? idx(cfg.from) : idx(preflight.start_stage)
const shouldRun = (stage) => idx(stage) >= startIdx

if (!preflight.config_ready && startIdx > idx('generate_brd')) {
  log(`Preflight: config.yaml not ready — ${preflight.config_blocking_reason || 'missing or still placeholdered'}`)
  return pauseResult('preflight', { status: 'config_not_ready', blocking_reason: preflight.config_blocking_reason })
}

let brd = null
if (shouldRun('generate_brd')) {
  phase('Generate BRD')
  brd = await agent(
    base('generate-brd.md', `Requirements intake root: ${cfg.requirements || 'requirements/'} (rule 31 untrusted intake — run python3 scripts/intake-safety-scan.py on that path first; exit 2 stops here, exit 1 stops until human redaction or a dated waiver in docs/harness/decisions.md). Module/bounded context: ${cfg.module || 'infer from the intake content; register Open DQ if unclear, do not invent'}. gate_met = true only if BRD status is Accepted, or a dated waiver exists in docs/harness/decisions.md.`),
    { phase: 'Generate BRD', model: 'haiku', schema: STATUS_SCHEMA },
  )
  if (!brd.gate_met) return pauseResult('generate_brd', brd)
}

if (shouldRun('propose_architecture') && !cfg.skipArchitecture) {
  phase('Propose Architecture')
  await agent(
    base('propose-architecture.md', 'Satellite step — this never blocks /plan-sprint regardless of ADR/proposal status. Report status as Proposed or Accepted; set gate_met=true always.'),
    { phase: 'Propose Architecture', model: 'haiku', schema: STATUS_SCHEMA },
  )
}

let plan = null
if (shouldRun('plan_sprint')) {
  phase('Plan Sprint')
  plan = await agent(
    base('plan-sprint.md', `Plan against the Accepted BRD. Sprint metadata — id: ${cfg.sprintId || 'not supplied, ask per this command\'s own Clarification Protocol'}; goal: ${cfg.sprintGoal || 'ask'}; duration: ${cfg.sprintDuration || 'ask'}. gate_met = true only if plan status is Approved.`),
    { phase: 'Plan Sprint', model: 'haiku', schema: STATUS_SCHEMA },
  )
  if (!plan.gate_met) return pauseResult('plan_sprint', plan)
}

let uiDesign = null
let apiImpl = null
if (shouldRun('parallel_branch')) {
  const results = await parallel([
    () => agent(
      base('generate-ui-design.md', `Satellite step — never blocks /implement-ui. reference_url: ${cfg.referenceUrl || 'none supplied — if genuinely unavailable, register Open DQ per this command\'s own Clarification Protocol; still set gate_met=true (satellite).'} screen_or_feature: from the Approved sprint plan.`),
      { phase: 'Generate UI Design', model: 'sonnet', schema: STATUS_SCHEMA },
    ),
    () => agent(
      base('implement-api.md', `Implement the backend slice for ${cfg.sprintItem || 'the first SP item in the Approved sprint plan'}. gate_met = true only when this command's own Definition of Done is fully met (tests actually run, not just written).`),
      { phase: 'Implement API', model: 'sonnet', schema: STATUS_SCHEMA },
    ),
  ])
  uiDesign = results[0]
  apiImpl = results[1]
  if (!apiImpl) return pauseResult('parallel_branch', { status: 'agent_failed', blocking_reason: 'implement-api agent errored or was skipped' })
  if (!apiImpl.gate_met) return pauseResult('parallel_branch', apiImpl)
}

let implUi = null
if (shouldRun('implement_ui')) {
  phase('Implement UI')
  implUi = await agent(
    base('implement-ui.md', `Implement the UI slice for the same SP item as Implement API. Use the mockup from the Generate UI Design phase if one was produced (${uiDesign && uiDesign.artifact_paths ? uiDesign.artifact_paths.join(', ') : 'none — fall back to UX spec / story UI table per this command\'s own contract'}). gate_met = true only when the FE<->BE wiring gate and this command's Definition of Done are fully met.`),
    { phase: 'Implement UI', model: 'sonnet', schema: STATUS_SCHEMA },
  )
  if (!implUi.gate_met) return pauseResult('implement_ui', implUi)
}

let expand = null
if (shouldRun('expand_test_coverage')) {
  phase('Expand Test Coverage')
  expand = await agent(
    base('expand-test-coverage.md', 'Close remaining FR/BR test-design gaps for the current slice. gate_met = true only if docs/quality/test-package-review.md status is Approved — Pending Approval (the normal agent-produced state) means gate_met=false; agents must not self-approve.'),
    { phase: 'Expand Test Coverage', model: 'haiku', schema: STATUS_SCHEMA },
  )
  if (!expand.gate_met) return pauseResult('expand_test_coverage', expand)
}

let runTests = null
if (shouldRun('run_tests')) {
  phase('Run Tests')
  runTests = await agent(
    base('run-tests.md', 'Generate and run executable tests from the Approved expand package. Refuse (gate_met=false) if the package is not Approved or coverage is not PASS, per this command\'s own hardening — do not run anyway.'),
    { phase: 'Run Tests', model: 'sonnet', schema: STATUS_SCHEMA },
  )
  if (!runTests.gate_met) return pauseResult('run_tests', runTests)
}

let runEval = null
let closeResult = null
let closeAttempts = 0
if (shouldRun('run_eval')) {
  phase('Run Eval')
  runEval = await agent(
    base('run-eval.md', `Mode: ${cfg.evalMode || 'incremental'}. Emit the completeness ledger and fix-queue. Report open_autofix_count = count of open auto_fix:true items in the fix-queue, and whether any item is already needs_human.`),
    { phase: 'Run Eval', model: 'sonnet', schema: EVAL_SCHEMA },
  )
  let openCount = runEval.open_autofix_count || 0
  let needsHuman = !!runEval.needs_human_present
  while (openCount > 0 && !needsHuman && closeAttempts < 3) {
    closeAttempts++
    phase('Close Eval Gaps')
    closeResult = await agent(
      base('close-eval-gaps.md', `Attempt ${closeAttempts} of 3. Walk the current fix-queue: delegate every open auto_fix:true item to its owning agent, re-run only those case_paths via eval-agent, and log every hop. Report the remaining open_autofix_count and whether any item is now needs_human.`),
      { phase: 'Close Eval Gaps', model: 'sonnet', schema: EVAL_SCHEMA, label: `close-eval-gaps attempt ${closeAttempts}` },
    )
    openCount = closeResult.open_autofix_count || 0
    needsHuman = !!closeResult.needs_human_present
    log(`close-eval-gaps attempt ${closeAttempts}: ${openCount} auto_fix item(s) still open${needsHuman ? ' (needs_human present)' : ''}`)
  }
  if (needsHuman) return pauseResult('run_eval', { status: 'needs_human', blocking_reason: `fix-queue item(s) needs_human after ${closeAttempts} close-eval-gaps attempt(s)` })
  if (openCount > 0) return pauseResult('run_eval', { status: 'auto_fix_open', blocking_reason: `${openCount} auto_fix item(s) still open after ${closeAttempts} attempt(s)` })
  if (runEval.ledger_complete === false) return pauseResult('run_eval', { status: 'ledger_incomplete', blocking_reason: 'completeness ledger not complete' })
}

let review = null
if (shouldRun('review_changes')) {
  phase('Review Changes')
  review = await agent(
    base('review-changes.md', 'Code, test, and security review of the slice. Refuse if the completeness ledger from /run-eval is missing. Block if any P0/P1 safety item remains, or any family has zero cases on the ledger.'),
    { phase: 'Review Changes', model: 'opus', schema: REVIEW_SCHEMA },
  )
  if (review.blocking) return pauseResult('review_changes', { status: review.verdict, blocking_reason: 'Block verdict — owning agents must fix findings, then re-run /review-changes' })
}

let appSummary = null
if (shouldRun('application_summary')) {
  phase('Application Summary')
  appSummary = await agent(
    base('application-summary.md', 'Delivery summary using the latest test-results and review artifact; update the harness via harness-updater.'),
    { phase: 'Application Summary', model: 'haiku', schema: STATUS_SCHEMA },
  )
}

return {
  paused: false,
  completedThrough: 'application_summary',
  preflight, brd, plan, uiDesign, apiImpl, implUi, expand, runTests, runEval,
  closeEvalGapsAttempts: closeAttempts,
  review, appSummary,
}
