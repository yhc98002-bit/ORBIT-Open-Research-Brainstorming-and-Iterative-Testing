---
name: diagnostic-to-review
description: "ORBIT v1.4 thin pipeline that chains the post-implementation segment: /run-experiment (Stage 16/17 with auto-routing to /experiment-queue if needed) → /analyze-results (Stage 18), then conditional-required /result-to-claim (Stage 21) → /auto-review-loop (Stage 23): not triggered for local diagnostics, but required for paper-bearing diagnostics. Runs the happy path automatically for paper-bearing diagnostics; stops after interpretation + decision log for sanity, provenance, implementation, and local mechanism probes. Aborts are NOT errors — they are awaiting_human_continue states with clear next_action so the user can decide."
argument-hint: [diagnostic-command OR manifest-path OR grid-spec]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /diagnostic-to-review — v1.4 Run → Analyze → Conditional-Required Claim → Review

Chain the post-implementation segment for: **$ARGUMENTS**

## Overview

This skill is a thin orchestrator that walks Stage 17/18 of the ORBIT pipeline, then
continues to Stage 21/23 only when the result affects paper-level claim scope. The user
invokes it once after `/experiment-bridge` returned `MATCHES_PLAN`; this skill takes over
until either the diagnostic-only path has a clean interpretation + decision log, the
paper-bearing happy path completes, or a verdict-line gate aborts the chain and surfaces a
clear "what's blocking + what to decide" report.

Ownership boundary:
- This skill owns formal diagnostic execution via `/run-experiment`.
- This skill owns scientific `RESULT_INTERPRETATION.md`.
- This skill owns `RESEARCH_DECISION_LOG.md` routing after results.
- This skill owns `CLAIM_CONSTRUCTION.md` for paper-level claims through
  `/result-to-claim`.
- This skill owns `RED_TEAM_REVIEW.md` through `/auto-review-loop`.
- `/result-to-claim` and `/auto-review-loop` are conditional-required, not discretionary:
  not triggered for local/sanity/probe diagnostics, but mandatory for paper-bearing
  diagnostics.

**Scope boundary:**
- Starts after `PLAN_CODE_AUDIT.md` exists with verdict = `MATCHES_PLAN` (or scoped
  `PARTIAL_MISMATCH`). Refuses to start otherwise (G11).
- Ends at Stage 23 (red-team review). Does **NOT** invoke `/paper-writing` — paper
  writing is the next stop (STOP D / G16+G18).
- Does **NOT** trigger `SCALEUP_DECISION = PROCEED` automatically — that requires
  `HUMAN_DECISION_NOTE.md` per G15+G19, which by design must be human-written.

```
Input:  diagnostic command / manifest / grid

  Phase 1: /run-experiment "$ARGUMENTS"  (auto-routes solo vs queue per T3a)
           ABORT if DIAGNOSTIC_RUN_AUDIT verdict != PASS (FIX_BEFORE_GPU,
                  REDESIGN_EXPERIMENT, ERROR with regime_check_unanswerable)
           OR     if Stage 17 G12 regime check fails

  Phase 2: /analyze-results "results/"
           ABORT if no parseable results found
           OR     if signs of metric/data fraud per experiment-integrity protocol

  Phase 3: Claim relevance gate
           If sanity/provenance/implementation/local-mechanism: stop after
           RESULT_INTERPRETATION + RESEARCH_DECISION_LOG.
           If paper-level claim scope is affected: /result-to-claim is mandatory.

  Phase 4: /auto-review-loop "<scope>" — difficulty: hard
           Mandatory when Phase 3 ran /result-to-claim; skipped for local diagnostics.
           ABORT if reviewer score < ABORT_REVIEW_SCORE after MAX_ROUNDS
           OR     if G14 (positive framing after tie/failure) detected
           OR     if G17 (post-hoc reframing as pre-planned) detected

  Phase 5: orbit-research/PIPELINE_SUMMARY.md + STATE.status = awaiting_human_continue
           (happy path: STOP D ready; abort: clear next_action describing blocker)
```

## Constants

- **OUTPUT_ROOT_V13 = `orbit-research/`** — v1.3 artifacts.
- **ABORT_REVIEW_SCORE = 4** — `/auto-review-loop` rounds with score below this after
  MAX_ROUNDS round-robin → abort and report. Tunable via `— abort-score: <N>`.
- **CONTINUE_ON_PARTIAL = true** — when `result-to-claim` returns `partial`, continue
  to red-team (the partial scope can still be reviewed; G14/G17 catch overclaims).
  Set `false` to abort on partial too.
- **AUTO_PROCEED = true** — chain phases without prompting unless user passes
  `— human checkpoint: true`.

## Load First

- `shared-references/research-agent-pipeline.md` — Stages 17/18/21/23 + hard gates
  G11/G12/G14/G16/G17
- `shared-references/research-harness-prompts.md` — sections `17`, `18`, `21`, `22`, `23`
- `shared-references/semantic-code-audit.md` — Stage 17 audit + G12 regime check
- `shared-references/experiment-integrity.md` — Phase 2 metric / data fraud signals
- `shared-references/document-hygiene.md` — avoid turning proposal documents into claim
  audits or rebuttal logs

Also read these project artifacts when present because failure routing depends on them:

- `orbit-research/RUN_LEDGER.jsonl` — canonical run provenance and failed/no-result runs
- `refine-logs/EXPERIMENT_PLAN_EXEC.md` — especially `Decision Tree / Branch Table`
- `refine-logs/FINAL_PROPOSAL.md` and `FINAL_PROPOSAL_SHORT.md` — proposal status block
- `orbit-research/ASSUMPTION_LEDGER.md` — critical hypotheses H1-Hk
- `orbit-research/NULL_RESULT_CONTRACT.md` — tie/negative interpretation
- `shared-references/continuation-contract.md` — STATE schema, three-state enum, resume
  rules

## Pre-flight — entry guards

Before Phase 1 starts, verify:

1. **G11 prereq**: `orbit-research/PLAN_CODE_AUDIT.md` exists AND verdict line is
   `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH` whose missing pieces are irrelevant to this
   diagnostic. If `CRITICAL_MISMATCH` or `ERROR` → refuse to start; route user back to
   `/experiment-bridge` to fix code and re-audit.
2. **G8 prereq**: `orbit-research/NULL_RESULT_CONTRACT.md` exists (the diagnostic must
   know what positive/null/tie means). If absent → refuse; route to
   `/experiment-bridge "refine-logs/FINAL_PROPOSAL.md" — mode: plan-only` or a focused
   `/experiment-plan` patch if the plan already exists.
3. **G9 prereq**: `orbit-research/COMPONENT_BUNDLE_LADDER.md` exists (or run is a single-
   component baseline reproduction with explicit declaration). If neither → refuse.
4. **`$ARGUMENTS` parses** as either a single command, a manifest path, or a grid spec
   per `/run-experiment` Step 0 detection rules. If not → ask user.

If any guard fails, write a STATE with `status = "in_progress"` + `next_action = "fix-prereq:<name>"`
and exit. Do not partially run.

## State Persistence (Continuation Contract)

Follows `shared-references/continuation-contract.md`.

**STATE file:** `orbit-research/DIAGNOSTIC_TO_REVIEW_STATE.json`

Schema:

```jsonc
{
  "skill": "diagnostic-to-review",
  "phase": "phase-3-claim",                  // last completed phase
  "status": "in_progress" | "awaiting_human_continue" | "completed",
  "abort_reason": null | "<reason-code>",    // present iff aborted
  "next_action": "<what to do next>",
  "next_skill_hint": "/paper-writing OR /experiment-bridge (re-audit) OR ...",
  "timestamp": "<ISO 8601 UTC>",
  "artifact_inventory": [
    "orbit-research/RUN_LEDGER.jsonl",
    "orbit-research/DIAGNOSTIC_RUN_REPORT.md",
    "orbit-research/DIAGNOSTIC_RUN_AUDIT.md",
    "orbit-research/RESULT_INTERPRETATION.md",
    "orbit-research/CLAIM_CONSTRUCTION.md",
    "orbit-research/HUMAN_DECISION_NOTE.md",
    "orbit-research/RED_TEAM_REVIEW.md",
    "orbit-research/PIPELINE_SUMMARY.md"
  ],
  "diagnostic_run_id": "<from RUN_EXPERIMENT_STATE>",
  "review_thread_id": "<Codex thread id from auto-review-loop>",
  "notes": "Free-form notes"
}
```

### On entry — resume decision tree

Apply the canonical contract decision tree. Specifically:

- `status = "completed"` + no `— resume:` → ask "previous chain completed; rerun?"
- `status = "in_progress"` + `timestamp < 24h` → resume from `phase + 1`; check artifact-presence skip per phase artifact map.
- `status = "awaiting_human_continue"` (abort case) → re-invocation with `— resume: true` AND user has fixed the underlying issue → resume from the aborted phase.
- `status = "awaiting_human_continue"` (happy path completion) → re-invocation = "user wants to rerun the chain; treat as fresh start unless `— resume: true`."

### Override flags

| Flag | Effect |
|---|---|
| `— resume: true` | Force resume even if STATE looks ambiguous |
| `— fresh: true` | Delete STATE; ignore prior artifacts; run from Phase 1 |
| `— from-phase: <N>` | Force start from phase 1–5 |
| `— human checkpoint: true` | Pause at every phase boundary |
| `— no-checkpoint: true` | Run straight through to `completed` (no awaiting_human_continue at end) |
| `— abort-score: <N>` | Override ABORT_REVIEW_SCORE for Phase 4 |
| `— continue-on-no: true` | Continue Phase 4 even if Phase 3 returned `claim_supported=no` (treats as documented negative result) |

### Phase artifact map (idempotent skip)

| Phase | Expected artifacts |
|---|---|
| phase-1-run | `orbit-research/RUN_LEDGER.jsonl` + `DIAGNOSTIC_RUN_REPORT.md` + `DIAGNOSTIC_RUN_AUDIT.md` (verdict line) |
| phase-2-analyze | `orbit-research/RESULT_INTERPRETATION.md` + `RESEARCH_DECISION_LOG.md` when result is failed / mixed / surprising |
| phase-3-claim | `orbit-research/CLAIM_CONSTRUCTION.md` + `HUMAN_DECISION_NOTE.md` + `RESEARCH_DECISION_LOG.md` when claim is unsupported |
| phase-4-review | `orbit-research/RED_TEAM_REVIEW.md` |
| phase-5-summary | `orbit-research/PIPELINE_SUMMARY.md` |

## Workflow

### Phase 1: Run — `/run-experiment`

```bash
/run-experiment "$ARGUMENTS"
```

`/run-experiment` (T3a-state + T3a-route) handles auto-routing (solo vs `/experiment-queue`),
state-based resume on interruption (screen attach + log offset replay), and writes
`RUN_LEDGER.jsonl` + `DIAGNOSTIC_RUN_REPORT.md` + `DIAGNOSTIC_RUN_AUDIT.md` with verdict
line. If the run fails, OOMs, times out, is killed, or produces no result, it is still a
valid ledgered diagnostic event.

**Abort triggers:**

| Verdict / state | Abort reason | next_skill_hint |
|---|---|---|
| `DIAGNOSTIC_RUN_AUDIT.verdict = FIX_BEFORE_GPU` | `fix-code-then-re-audit` | `/experiment-bridge` (re-run plan-code audit after fix) |
| `DIAGNOSTIC_RUN_AUDIT.verdict = REDESIGN_EXPERIMENT` AND G12 regime check passed (regime DID preserve mechanism preconditions) | `redesign-diagnostic` | `/experiment-plan` (redesign Stage 16 plan) |
| `DIAGNOSTIC_RUN_AUDIT.verdict = REDESIGN_EXPERIMENT` AND G12 regime check failed (regime DID NOT preserve mechanism preconditions) | `regime-mismatch-not-mechanism-failure` | `/experiment-plan` (redesign diagnostic to a regime where mechanism could in principle manifest) — do NOT kill the mechanism |
| `DIAGNOSTIC_RUN_AUDIT.verdict = ERROR` AND reason = `regime_check_unanswerable` | `human-must-judge-regime` | manual review — escalate to HUMAN_DECISION_REQUIRED |

Codex unavailability is **not** an abort trigger at this stage — it is
handled earlier by the Phase 0 precondition (see
[`shared-references/codex-precondition.md`](../shared-references/codex-precondition.md)
and the "For Codex MCP unavailability" section below). A run that reaches
this table has already passed the precondition; if Codex then fails
mid-Phase-1, the LOUD STOP in §5 of the precondition contract takes over
and `DIAGNOSTIC_RUN_AUDIT.verdict` is **not** written for the failed
phase. The previous `codex_mcp_unavailable` abort row was the silent-skip
this skill no longer supports.

If verdict = `PASS` → write Phase 1 STATE (`status: in_progress`, `next_action: phase-2-analyze`)
and continue to Phase 2.

### Phase 2: Analyze — `/analyze-results`

```bash
/analyze-results "results/"
```

Or pass an explicit results path / W&B run id derived from Phase 1's `DIAGNOSTIC_RUN_REPORT.md`.

Writes `orbit-research/RESULT_INTERPRETATION.md` per Stage 18 harness.

If the diagnostic is failed, mixed, contradictory, or surprising, write
`orbit-research/RESEARCH_DECISION_LOG.md` before routing or aborting. The log is the
canonical local decision artifact for failed diagnostics; do not default to
`/idea-to-proposal — fresh: true` or broad `/proposal-revise both`.

Use this structure:

```markdown
# Research Decision Log

- Diagnostic / run ID: [from DIAGNOSTIC_RUN_REPORT]
- Result pattern: [positive / negative / mixed / tie / surprising / invalid]
- Affected hypotheses: [H1-Hk, especially paper-breaking entries]
- Failure type: implementation/config issue | invalid diagnostic | mechanism issue | benchmark/headroom issue | central paper-breaking hypothesis false | literature conflict | inconclusive
- Decision: continue | local patch | change diagnostic | re-read literature | failure-to-innovation | proposal-revise | archive
- Local patch target: experiment-bridge | experiment-plan | proposal-revise | research-lit | failure-to-innovation | manual
- Proposal status update: unchanged | SUPPORTED | REFRAMED | ARCHIVED
- Proposal revision needed: no | proposal-only | plan-only | both | assumption-only | mechanism-only | benchmark/control-only | diagnostic-branch-only
- Next skill hint: [/experiment-bridge | /experiment-plan | /proposal-revise | /research-lit | /research-pipeline from Stage 18.5 | human decision]
- Human decision required: yes/no

## Rationale
[Short evidence-based reason, citing RESULT_INTERPRETATION, NULL_RESULT_CONTRACT,
EXPERIMENT_PLAN_EXEC Decision Tree, and affected H-IDs.]
```

**Abort triggers:**

| Condition | Abort reason | next_skill_hint |
|---|---|---|
| No parseable results found at expected paths | `results-not-found` | write RESULT_INTERPRETATION from RUN_LEDGER failure/no-result records, then write/update RESEARCH_DECISION_LOG before routing |
| `experiment-integrity.md` fraud signals detected (fake ground truth, score normalisation fraud, phantom results, scope inflation) | `integrity-failure` | `/experiment-audit` for full integrity audit; do NOT proceed to claim construction with corrupt eval |
| Result interpretation entirely contradicts the proposal's claim direction | `result-contradicts-proposal` | follow `RESEARCH_DECISION_LOG.md`; likely `/proposal-revise — mode: mechanism-only` or human decision to mark proposal `REFRAMED` / `ARCHIVED` |

If interpretation is well-formed (positive / negative / mixed all OK as long as the
result is *interpretable* per `NULL_RESULT_CONTRACT.md`) → write Phase 2 STATE and
continue to Phase 3.

If no metric result exists, still write `RESULT_INTERPRETATION.md` from
`RUN_LEDGER.jsonl`, logs, and `DIAGNOSTIC_RUN_AUDIT.md`. Classify the outcome as
`no_result`, `oom`, `timeout`, `killed`, or `failed`; then write/update
`RESEARCH_DECISION_LOG.md` before routing. Do not skip straight to proposal revision.

### Phase 3: Claim Relevance Gate — conditional-required `/result-to-claim`

Do not invoke `/result-to-claim` after every diagnostic. First classify the run's purpose
from `DIAGNOSTIC_EXPERIMENT_PLAN.md`, `EXPERIMENT_PLAN_EXEC.md`, and
`RESULT_INTERPRETATION.md`.

Stop after `RESULT_INTERPRETATION.md` + `RESEARCH_DECISION_LOG.md` when the diagnostic is:

- sanity / smoke testing
- provenance or logging validation
- implementation/config validation
- mechanism probing that informs the next local patch but does not change paper-level
  claim scope yet
- benchmark plumbing, data availability, or evaluator validity checking

For any diagnostic that affects paper-level claim scope, `/result-to-claim` is mandatory,
such as:

- a main benchmark or ablation intended to support a paper claim
- a critical hypothesis whose truth changes `FINAL_PROPOSAL` status or claim wording
- a scale-up decision where evidence may become primary paper support
- a negative/tie result that would weaken, reframe, or archive a paper-bearing claim

```bash
/result-to-claim "<one-line description: e.g. 'main result on benchmark X with method Y'>"
```

Auto-derive the description from `RESULT_INTERPRETATION.md` if the user did not pass one
and the claim relevance gate says this is paper-bearing.
Writes `orbit-research/CLAIM_CONSTRUCTION.md` and `HUMAN_DECISION_NOTE.md` per Stage 21
harness; writes `NEGATIVE_RESULT_STRATEGY.md` if Stage 22 triggered.

**Abort triggers:**

| Condition | Abort reason | next_skill_hint |
|---|---|---|
| `claim_supported = no` AND `— continue-on-no: true` NOT set | `claim-not-supported` | write/update `RESEARCH_DECISION_LOG.md`; route according to its decision, not broad full-pipeline revision |
| G14 violation detected: NULL_RESULT_CONTRACT triggered tie/failure but draft has positive framing | `g14-positive-framing-on-failure` | rewrite per Stage 22 (Tie / Negative Strategy); G14 is no-exception |
| G17 violation detected: post-hoc claim presented as pre-planned hypothesis | `g17-post-hoc-as-pre-planned` | label explicitly as "exploratory finding, not pre-planned hypothesis" before proceeding; G17 is no-exception |

If `claim_supported = yes` OR (`claim_supported = partial` AND `CONTINUE_ON_PARTIAL = true`)
→ write Phase 3 STATE and continue to Phase 4.

### Failure Routing from `RESEARCH_DECISION_LOG.md`

When the decision log exists, its `Decision`, `Failure type`, and `Proposal revision
needed` fields are binding for recovery routing:

| Failure type | Route | Rule |
|---|---|---|
| implementation/config issue | `/experiment-bridge` fix loop | Patch implementation/config and re-run plan-code audit; do not revise proposal. |
| invalid diagnostic | `/experiment-plan — mode: diagnostic-branch-only` | Patch the diagnostic branch / run card; do not mark mechanism false. |
| mechanism issue | `/proposal-revise — mode: mechanism-only` or failure-to-innovation | Revise only mechanism artifacts unless the log explicitly says proposal-only/both. |
| benchmark/headroom issue | `/experiment-plan — mode: benchmark/control-only` or `/proposal-revise — mode: benchmark/control-only` | Patch controls, benchmark, or claim scope only. |
| central paper-breaking hypothesis false | human decision | Patch only the `## Proposal Status` block in `FINAL_PROPOSAL.md` and `FINAL_PROPOSAL_SHORT.md` to `REFRAMED` or `ARCHIVED`; do not auto-run broad revision. |
| literature conflict | `/research-lit` then targeted revise | Re-read literature before changing mechanism or claims. |
| inconclusive | continue or change diagnostic | Follow the Decision Tree / Branch Table; avoid proposal revision unless required. |

`/idea-to-proposal — fresh: true` is not a default failed-diagnostic recovery. Use it only
when the human explicitly chooses to abandon the current problem/method and restart
discovery.

### Phase 4: Red-team — conditional-required `/auto-review-loop`

```bash
/auto-review-loop "<scope: e.g. 'method Y on benchmark X claim chain'>" — difficulty: hard
```

Do not run this phase for sanity, provenance, implementation, or local mechanism probes
that stopped after `RESULT_INTERPRETATION.md` + `RESEARCH_DECISION_LOG.md`. When Phase 3
ran `/result-to-claim` because the diagnostic affects paper-level claim scope,
`/auto-review-loop` is mandatory. Together Phase 3 and Phase 4 produce
`CLAIM_CONSTRUCTION.md`, `RED_TEAM_REVIEW.md`, and `HUMAN_DECISION_NOTE.md` for STOP C.

**Abort triggers:**

| Condition | Abort reason | next_skill_hint |
|---|---|---|
| Reviewer score below `ABORT_REVIEW_SCORE` (default 4/10) after `MAX_ROUNDS` rounds | `irrecoverable-review-score` | major fixes / new experiments needed before paper writing; cannot defend at top venue |
| G14 / G17 violations re-detected by the red-team reviewer | `gate-violation-flagged-by-reviewer` | rewrite per the violation reason |
| `/auto-review-loop` returned with required fixes that loop into a Stage 11 redesign | `redesign-required` | `/research-pipeline — from-stage: 11` to redo HMBC matrix |

If review converges with score ≥ ABORT_REVIEW_SCORE and no gate violations → write Phase 4
STATE and continue to Phase 5. If the reviewed claim supports the central diagnostic
hypothesis, patch only the `## Proposal Status` block in `FINAL_PROPOSAL.md` and
`FINAL_PROPOSAL_SHORT.md` to `SUPPORTED`, with evidence basis citing
`CLAIM_CONSTRUCTION.md` and `RED_TEAM_REVIEW.md`.

### Phase 5: Pipeline Summary

Write `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /diagnostic-to-review Pipeline Summary

- Input: $ARGUMENTS
- Completed: <ISO timestamp>
- Outcome: DIAGNOSTIC_ONLY | PAPER_BEARING | ABORTED:<reason>

## Artifact map

### Phase 1 — Run (Stage 17)
- orbit-research/DIAGNOSTIC_RUN_REPORT.md
- orbit-research/DIAGNOSTIC_RUN_AUDIT.md  (verdict: PASS)

### Phase 2 — Analyze (Stage 18)
- orbit-research/RUN_LEDGER.jsonl
- orbit-research/RESULT_INTERPRETATION.md
- orbit-research/RESEARCH_DECISION_LOG.md  (if failed / mixed / surprising / unsupported)

### Phase 3 — Claim (Stage 21 / 22, only if paper-level claim scope is affected)
- orbit-research/CLAIM_CONSTRUCTION.md
- orbit-research/HUMAN_DECISION_NOTE.md
- orbit-research/NEGATIVE_RESULT_STRATEGY.md  (if tie/failure)

### Phase 4 — Red-team (Stage 23, only if paper-level claim scope is affected)
- orbit-research/RED_TEAM_REVIEW.md  (final score: <N>/10)

## Next steps (NOT run by this skill)

If diagnostic-only:
1. Review RESULT_INTERPRETATION.md + RESEARCH_DECISION_LOG.md.
2. Decide: continue, local patch, change diagnostic, re-read literature, or archive.

If paper-bearing:
1. Review CLAIM_CONSTRUCTION.md + RED_TEAM_REVIEW.md + HUMAN_DECISION_NOTE.md jointly
   — STOP C in the 4-stop HITL flow.
2. Decide: scale-up to full grid OR write paper now OR pivot.
3. For paper writing: /paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
   (G16 + G18 enforced — CLAIM_CONSTRUCTION.md must exist.)
4. For scale-up: /run-experiment "<full grid manifest>" → re-runs this pipeline with
   bigger N. SCALEUP_DECISION.md must end with PROCEED + HUMAN_DECISION_NOTE per G15+G19.

If aborted:
- See <skill>_STATE.json next_action and next_skill_hint for the specific recovery path.
```

**Write final STATE** at end of Phase 5 with **`awaiting_human_continue`** (designed
human checkpoint — STOP C in the 4-stop HITL flow):

```jsonc
{
  "skill": "diagnostic-to-review",
  "phase": "phase-5-summary",
  "status": "awaiting_human_continue",
  "abort_reason": null,                          // null = happy path
  "next_action": "human-must-confirm-then-call-/paper-writing-or-/run-experiment-for-scale-up",
  "next_skill_hint": "/paper-writing OR /run-experiment (scale-up grid)",
  "timestamp": "<now>",
  "artifact_inventory": [/* full list */]
}
```

If aborted at any prior phase, STATE was already written there with abort context.

## ARIS / Sub-skill Unavailability

For each delegated invocation, follow the standard fallback pattern (per
`shared-references/continuation-contract.md`):

```text
Try slash invocation.
If skill not registered:
  Print "ORBIT skill <name> unavailable. Phase <N> degraded: <fallback or HUMAN_DECISION_REQUIRED>."
  Continue gracefully.
If load-bearing for a hard gate (e.g. /auto-review-loop for Stage 23 + paper-writing G16):
  Escalate — do not silently produce an incomplete review.
```

For Codex MCP unavailability, this skill follows the **Codex Precondition +
Loud-Stop Contract** in
[`shared-references/codex-precondition.md`](../shared-references/codex-precondition.md):

- **Phase 0 precondition.** Codex availability is checked at skill entry
  (§3 of the contract). Phase 1 (diagnostic audit) and Phase 4 (red-team
  review) both depend on independent Codex judgment; a single-model
  "audit" or "red-team" is exactly the silent regression the contract
  removes. A failed precondition stops at `phase-0-precondition` with
  `status: "awaiting_user_action"` *before* Phase 1's audit verdict is
  written.
- **Mid-run failure (§5 of the contract).** A failing Codex call during
  Phase 1 audit or Phase 4 red-team review triggers a LOUD STOP: STATE
  `status: "awaiting_user_action"`, no `DIAGNOSTIC_RUN_AUDIT` verdict or
  `RED_TEAM_REVIEW.md` produced for the failed phase, loud user-facing
  remediation message. Phase 5 pipeline summary is **not** written under
  these conditions — the chain stops where the audit/review was supposed
  to live.
- **Override.** `— codex-required: false` opts into a degraded single-model
  run; `DIAGNOSTIC_RUN_AUDIT` and `RED_TEAM_REVIEW.md` carry the §6 visible
  header at the top of the file, and the next caller (`/paper-writing`
  Phase 5.5/5.8) will see the degraded-mode header and may block at the
  submission gate.

The previous behavior — `DIAGNOSTIC_RUN_AUDIT.verdict = ERROR (codex_mcp_unavailable)`
treated as "advisory at diagnostic" and a `⚠️ degraded` header on `RED_TEAM_REVIEW.md`
that "does not abort the chain" — is **deprecated**. An audit/review that
silently degrades is not an audit/review.

## What This Skill Deliberately Does NOT Do

- Does **not** invoke `/paper-writing`, `/auto-paper-improvement-loop`, `/paper-claim-audit`,
  or `/citation-audit`. Paper writing is the next stop (STOP D in 4-stop flow), gated by
  G16 + G18 on `CLAIM_CONSTRUCTION.md` (which this skill produces).
- Does **not** auto-decide scale-up. `SCALEUP_DECISION.md` must end with `PROCEED` only
  when `HUMAN_DECISION_NOTE.md` explicitly authorises it (G15 + G19).
- Does **not** modify `PLAN_CODE_AUDIT.md` — if Phase 1 abort path is `fix-code`, route
  back to `/experiment-bridge`.
- Does **not** modify `EXPERIMENT_PLAN.md` — if Phase 1 abort path is `redesign-diagnostic`,
  route back to `/experiment-plan` patch mode. Use `/idea-to-proposal — fresh: true` only
  after an explicit human decision to abandon and restart discovery.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Final Rule

```text
Run cheap, interpret honestly, claim only when paper-level scope is affected, review hard.
A bottleneck is information; it is not failure.
Every abort produces a clear next_action — never a silent stop.
Convergence on a defensible claim is the goal; abandoning a bad chain early
is cheaper than burning more GPU and writing a paper that won't survive review.
```
