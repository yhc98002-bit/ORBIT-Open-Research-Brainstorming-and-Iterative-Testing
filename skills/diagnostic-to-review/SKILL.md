---
name: diagnostic-to-review
description: "ORBIT v1.3 thin pipeline that chains the post-implementation segment: /run-experiment (Stage 16/17 with auto-routing to /experiment-queue if needed) → /analyze-results (Stage 18) → /result-to-claim (Stage 21) → /auto-review-loop (Stage 23). Runs the happy path automatically; aborts and reports cleanly the moment any verdict-line gate signals a bottleneck (DIAGNOSTIC_RUN_AUDIT != PASS, claim_supported = no, irrecoverable review score, G14/G17 violations). Aborts are NOT errors — they are awaiting_human_continue states with clear next_action so the user can decide. Use when user has PLAN_CODE_AUDIT verdict = MATCHES_PLAN and wants to chain diagnostic → claim → review without re-typing four skill calls."
argument-hint: [diagnostic-command OR manifest-path OR grid-spec]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /diagnostic-to-review — v1.3 Run → Analyze → Claim → Review

Chain the post-implementation segment for: **$ARGUMENTS**

## Overview

This skill is a thin orchestrator that walks Stages 17/18/21/23 of the ORBIT v1.3
pipeline as one continuous run. The user invokes it once after `/experiment-bridge`
returned `MATCHES_PLAN`; this skill takes over until either the happy path completes
(red-team review done, claim construction stable) or a verdict-line gate aborts the chain
and surfaces a clear "what's blocking + what to decide" report.

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

  Phase 3: /result-to-claim "<auto-derived experiment description>"
           ABORT if claim_supported = "no"
           Continue (with downgrade) if claim_supported = "partial"

  Phase 4: /auto-review-loop "<scope>" — difficulty: hard
           ABORT if reviewer score < ABORT_REVIEW_SCORE after MAX_ROUNDS
           OR     if G14 (positive framing after tie/failure) detected
           OR     if G17 (post-hoc reframing as pre-planned) detected

  Phase 5: PIPELINE_SUMMARY.md + STATE.status = awaiting_human_continue
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
- `shared-references/continuation-contract.md` — STATE schema, three-state enum, resume
  rules

## Pre-flight — entry guards

Before Phase 1 starts, verify:

1. **G11 prereq**: `orbit-research/PLAN_CODE_AUDIT.md` exists AND verdict line is
   `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH` whose missing pieces are irrelevant to this
   diagnostic. If `CRITICAL_MISMATCH` or `ERROR` → refuse to start; route user back to
   `/experiment-bridge` to fix code and re-audit.
2. **G8 prereq**: `orbit-research/NULL_RESULT_CONTRACT.md` exists (the diagnostic must
   know what positive/null/tie means). If absent → refuse; route to `/experiment-plan`.
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
  "notes": "Optional"
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
| phase-1-run | `orbit-research/DIAGNOSTIC_RUN_REPORT.md` + `DIAGNOSTIC_RUN_AUDIT.md` (verdict line) |
| phase-2-analyze | `orbit-research/RESULT_INTERPRETATION.md` |
| phase-3-claim | `orbit-research/CLAIM_CONSTRUCTION.md` + `HUMAN_DECISION_NOTE.md` |
| phase-4-review | `orbit-research/RED_TEAM_REVIEW.md` |
| phase-5-summary | `orbit-research/PIPELINE_SUMMARY.md` |

## Workflow

### Phase 1: Run — `/run-experiment`

```bash
/run-experiment "$ARGUMENTS"
```

`/run-experiment` (T3a-state + T3a-route) handles auto-routing (solo vs `/experiment-queue`),
state-based resume on interruption (screen attach + log offset replay), and writes
`DIAGNOSTIC_RUN_REPORT.md` + `DIAGNOSTIC_RUN_AUDIT.md` with verdict line.

**Abort triggers:**

| Verdict / state | Abort reason | next_skill_hint |
|---|---|---|
| `DIAGNOSTIC_RUN_AUDIT.verdict = FIX_BEFORE_GPU` | `fix-code-then-re-audit` | `/experiment-bridge` (re-run plan-code audit after fix) |
| `DIAGNOSTIC_RUN_AUDIT.verdict = REDESIGN_EXPERIMENT` AND G12 regime check passed (regime DID preserve mechanism preconditions) | `redesign-diagnostic` | `/experiment-plan` (redesign Stage 16 plan) |
| `DIAGNOSTIC_RUN_AUDIT.verdict = REDESIGN_EXPERIMENT` AND G12 regime check failed (regime DID NOT preserve mechanism preconditions) | `regime-mismatch-not-mechanism-failure` | `/experiment-plan` (redesign diagnostic to a regime where mechanism could in principle manifest) — do NOT kill the mechanism |
| `DIAGNOSTIC_RUN_AUDIT.verdict = ERROR` AND reason = `regime_check_unanswerable` | `human-must-judge-regime` | manual review — escalate to HUMAN_DECISION_REQUIRED |
| `DIAGNOSTIC_RUN_AUDIT.verdict = ERROR` AND reason = `codex_mcp_unavailable` AND this is a scale-up | `codex-down-block-scale-up` | wait for Codex; user explicit acknowledgement to override |

If verdict = `PASS` → write Phase 1 STATE (`status: in_progress`, `next_action: phase-2-analyze`)
and continue to Phase 2.

### Phase 2: Analyze — `/analyze-results`

```bash
/analyze-results "results/"
```

Or pass an explicit results path / W&B run id derived from Phase 1's `DIAGNOSTIC_RUN_REPORT.md`.

Writes `orbit-research/RESULT_INTERPRETATION.md` per Stage 18 harness.

**Abort triggers:**

| Condition | Abort reason | next_skill_hint |
|---|---|---|
| No parseable results found at expected paths | `results-not-found` | manual investigation; check `/run-experiment` output paths |
| `experiment-integrity.md` fraud signals detected (fake ground truth, score normalisation fraud, phantom results, scope inflation) | `integrity-failure` | `/experiment-audit` for full integrity audit; do NOT proceed to claim construction with corrupt eval |
| Result interpretation entirely contradicts the proposal's claim direction | `result-contradicts-proposal` | `/idea-to-proposal — fresh: true` to reframe, or `/experiment-plan` to revise design |

If interpretation is well-formed (positive / negative / mixed all OK as long as the
result is *interpretable* per `NULL_RESULT_CONTRACT.md`) → write Phase 2 STATE and
continue to Phase 3.

### Phase 3: Claim — `/result-to-claim`

```bash
/result-to-claim "<one-line description: e.g. 'main result on benchmark X with method Y'>"
```

Auto-derive the description from `RESULT_INTERPRETATION.md` if the user did not pass one.
Writes `orbit-research/CLAIM_CONSTRUCTION.md` and `HUMAN_DECISION_NOTE.md` per Stage 21
harness; writes `NEGATIVE_RESULT_STRATEGY.md` if Stage 22 triggered.

**Abort triggers:**

| Condition | Abort reason | next_skill_hint |
|---|---|---|
| `claim_supported = no` AND `— continue-on-no: true` NOT set | `claim-not-supported` | review options: revise claim, run more experiments, pivot, or treat as documented negative result via `/idea-to-proposal — fresh: true` |
| G14 violation detected: NULL_RESULT_CONTRACT triggered tie/failure but draft has positive framing | `g14-positive-framing-on-failure` | rewrite per Stage 22 (Tie / Negative Strategy); G14 is no-exception |
| G17 violation detected: post-hoc claim presented as pre-planned hypothesis | `g17-post-hoc-as-pre-planned` | label explicitly as "exploratory finding, not pre-planned hypothesis" before proceeding; G17 is no-exception |

If `claim_supported = yes` OR (`claim_supported = partial` AND `CONTINUE_ON_PARTIAL = true`)
→ write Phase 3 STATE and continue to Phase 4.

### Phase 4: Red-team — `/auto-review-loop`

```bash
/auto-review-loop "<scope: e.g. 'method Y on benchmark X claim chain'>" — difficulty: hard
```

Runs review → fix → re-review iterations per Stage 23. Writes `orbit-research/RED_TEAM_REVIEW.md`.

**Abort triggers:**

| Condition | Abort reason | next_skill_hint |
|---|---|---|
| Reviewer score below `ABORT_REVIEW_SCORE` (default 4/10) after `MAX_ROUNDS` rounds | `irrecoverable-review-score` | major fixes / new experiments needed before paper writing; cannot defend at top venue |
| G14 / G17 violations re-detected by the red-team reviewer | `gate-violation-flagged-by-reviewer` | rewrite per the violation reason |
| `/auto-review-loop` returned with required fixes that loop into a Stage 11 redesign | `redesign-required` | `/research-pipeline — from-stage: 11` to redo HMBC matrix |

If review converges with score ≥ ABORT_REVIEW_SCORE and no gate violations → write Phase 4
STATE and continue to Phase 5.

### Phase 5: Pipeline Summary

Write `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /diagnostic-to-review Pipeline Summary

- Input: $ARGUMENTS
- Completed: <ISO timestamp>
- Outcome: HAPPY_PATH | ABORTED:<reason>

## Artifact map

### Phase 1 — Run (Stage 17)
- orbit-research/DIAGNOSTIC_RUN_REPORT.md
- orbit-research/DIAGNOSTIC_RUN_AUDIT.md  (verdict: PASS)

### Phase 2 — Analyze (Stage 18)
- orbit-research/RESULT_INTERPRETATION.md

### Phase 3 — Claim (Stage 21 / 22)
- orbit-research/CLAIM_CONSTRUCTION.md
- orbit-research/HUMAN_DECISION_NOTE.md
- orbit-research/NEGATIVE_RESULT_STRATEGY.md  (if tie/failure)

### Phase 4 — Red-team (Stage 23)
- orbit-research/RED_TEAM_REVIEW.md  (final score: <N>/10)

## Next steps (NOT run by this skill)

If happy path:
1. Review CLAIM_CONSTRUCTION.md + RED_TEAM_REVIEW.md + HUMAN_DECISION_NOTE.md jointly
   — STOP C in the 4-stop HITL flow.
2. Decide: scale-up to full grid OR write paper now OR pivot.
3. For paper writing: /paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
   (G16 + G18 enforced — CLAIM_CONSTRUCTION.md must exist; this skill produced it.)
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

For Codex MCP unavailability:
- Phase 1 audit → `DIAGNOSTIC_RUN_AUDIT.verdict = ERROR (codex_mcp_unavailable)` →
  advisory at diagnostic, blocks at scale-up per G11.
- Phase 4 review → `RED_TEAM_REVIEW.md` header marked `⚠️ degraded: codex_mcp_unreachable, single-model review only`.
  Does not abort the chain (Phase 5 still writes pipeline summary), but the next caller
  (`/paper-writing` Phase 5.5/5.8) will see the degradation note and may block at the
  submission gate.

## What This Skill Deliberately Does NOT Do

- Does **not** invoke `/paper-writing`, `/auto-paper-improvement-loop`, `/paper-claim-audit`,
  or `/citation-audit`. Paper writing is the next stop (STOP D in 4-stop flow), gated by
  G16 + G18 on `CLAIM_CONSTRUCTION.md` (which this skill produces).
- Does **not** auto-decide scale-up. `SCALEUP_DECISION.md` must end with `PROCEED` only
  when `HUMAN_DECISION_NOTE.md` explicitly authorises it (G15 + G19).
- Does **not** modify `PLAN_CODE_AUDIT.md` — if Phase 1 abort path is `fix-code`, route
  back to `/experiment-bridge`.
- Does **not** modify `EXPERIMENT_PLAN.md` — if Phase 1 abort path is `redesign-diagnostic`,
  route back to `/experiment-plan` or `/idea-to-proposal — fresh: true`.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Final Rule

```text
Run cheap, interpret honestly, claim narrowly, review hard.
A bottleneck is information; it is not failure.
Every abort produces a clear next_action — never a silent stop.
Convergence on a defensible claim is the goal; abandoning a bad chain early
is cheaper than burning more GPU and writing a paper that won't survive review.
```
