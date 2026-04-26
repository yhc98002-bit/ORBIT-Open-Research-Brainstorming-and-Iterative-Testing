---
name: proposal-revise
description: "ORBIT v1.3 feedback-driven targeted revision loop. Accepts a target artifact (refine-logs/FINAL_PROPOSAL.md, refine-logs/EXPERIMENT_PLAN.md, or both) plus user-authored critique points (inline string or critique file), classifies each critique by which v1.3 stage owns the underlying decision, re-runs only the affected stages, then re-integrates via /research-refine Phase 3-4 (anchor + simplicity check) for proposal targets or /experiment-plan for experiment-plan targets. Stops at awaiting_human_continue with a diff report. Use when user says \"改proposal\", \"修改方案\", \"不满意\", \"revise proposal\", \"critique-driven update\", \"针对性修改\", or wants STOP A revision without a full pipeline rerun."
argument-hint: [target-artifact-path-or-both]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /proposal-revise — STOP A revision loop

Run a feedback-driven targeted revision for: **$ARGUMENTS**

## Overview

After STOP A in the standard 4-stop HITL flow (`/idea-to-proposal` produces FINAL_PROPOSAL
+ EXPERIMENT_PLAN), if the user is dissatisfied with specific points, this skill takes
the user's critique and revises only the affected v1.3 artifacts — not the whole pipeline.
It reuses existing machinery rather than building new:

- **Phase 3-4 of `/research-refine`** for anchor-check + simplicity-check + revise-and-rewrite
- **HUMAN_CHECKPOINT flow** of `/auto-review-loop` for accepting custom modification instructions
- **Reviewer Independence Protocol** of `/auto-paper-improvement-loop` for confirmation-bias-free re-evaluation
- **Override flags + idempotent skip** from `/idea-to-proposal` for partial re-runs and resume
- **Per-stage harness prompts** from `shared-references/research-harness-prompts.md` for targeted re-execution

```
Input: target artifact + critique points
  Phase 0: Intake & Triage     — parse critique → classify by owning stage
  Phase 1: Targeted Re-runs    — invoke per-stage prompts to update affected v1.3 artifacts
  Phase 2: Anchor + Simplicity — does revision still solve the original problem? not over-complex?
  Phase 3: Re-integrate        — /research-refine for proposal target, /experiment-plan for plan target
  Phase 4: Diff Report + STOP awaiting_human_continue
```

**Scope boundary:** does NOT touch GPU, does NOT modify v1.3 contract files, does NOT
regenerate every v1.3 artifact (only those flagged by critique items), does NOT auto-accept
revisions (Phase 4 always ends `awaiting_human_continue` unless `— no-checkpoint: true`).

## Constants

- **MAX_ROUNDS = 2** — cap on revise → re-eval iterations within a single invocation. Override with `— max-rounds: <N>`.
- **CODEX_REVIEW_MODEL = `gpt-5.5`**, **CODEX_REVIEW_EFFORT = `xhigh`**.
- **CODEX_INNOVATION_MODE** — `COLLABORATIVE` for Stage 8/9/10/18.5 re-runs; `ADVERSARIAL` everywhere else (per `innovation-loops.md` §7).
- **REVIEWER_INDEPENDENCE = on** — Phase 3 Codex re-evaluation uses **fresh** `mcp__codex__codex` thread (NOT `codex-reply`) per `auto-paper-improvement-loop` reviewer-independence protocol — avoids confirmation bias on whether the fix actually works.
- **AUTO_PROCEED = true** — chain phases without prompting unless user passes `— human checkpoint: true`.

## Load First

- `shared-references/research-agent-pipeline.md` — v1.3 stage definitions for the targeted re-runs
- `shared-references/research-harness-prompts.md` — per-stage canonical prompts (sections 4/5/7/8/9/10/11/12/13/14/16) invoked in Phase 1
- `shared-references/innovation-loops.md` — Codex collaborative-mode prompt template (§7.1) for Stage 8/9/10/18.5 re-runs
- `shared-references/continuation-contract.md` — STATE.json schema, three-state enum, cross-skill resume rules
- `shared-references/reviewer-independence.md`

## Inputs

```text
# Required positional
$ARGUMENTS = path to target artifact OR "both"
  Accepted values:
    refine-logs/FINAL_PROPOSAL.md       # revise the proposal only
    refine-logs/EXPERIMENT_PLAN.md      # revise the experiment plan only
    both                                 # revise both (common when user critiqued each)

# Critique input (one of these is required)
— critiques: "<inline string with one or more bullet-style critiques>"
— critique-file: <path/to/critique.md>   # multi-line free-form critique file

# Optional scope hint (auto-classifies if absent)
— scope: method | mechanism | baseline | claim | experiments | assumptions
       | controls | null-result | bundle | formalization | diagnostic
  (multiple comma-separated allowed; pre-classifies and skips Phase 0 triage)

# Override flags (per continuation contract)
— resume: true              # force resume even if STATE looks ambiguous
— fresh: true               # delete STATE; rerun from Phase 0
— from-phase: <0-4>         # force start from a specific phase
— human checkpoint: true    # pause at every phase boundary, not just Phase 4
— no-checkpoint: true       # skip Phase 4 awaiting_human_continue exit
— max-rounds: <N>           # cap revise→re-review iterations (default 2)
```

## State Persistence (Continuation Contract)

This skill follows `shared-references/continuation-contract.md`.

**STATE file:** `orbit-research/PROPOSAL_REVISE_STATE.json`

Schema:

```jsonc
{
  "skill": "proposal-revise",
  "phase": "phase-3-reintegrate",          // last completed phase, one of:
                                            // phase-0-intake, phase-1-targeted-reruns,
                                            // phase-2-anchor-simplicity,
                                            // phase-3-reintegrate, phase-4-summary
  "round": 1,                              // current revise→re-eval round (≤ MAX_ROUNDS)
  "status": "in_progress" | "awaiting_human_continue" | "completed",
  "target": "FINAL_PROPOSAL" | "EXPERIMENT_PLAN" | "both",
  "critique_inventory": [
    {
      "id": "C1",
      "raw_text": "ALGORITHM_TOURNAMENT picks S2 but S5 has stronger falsifiability",
      "owning_stage": 10,
      "addressed": "yes" | "no" | "rejected: <reason>" | "pending"
    }
  ],
  "next_action": "phase-4-summary" | "human-must-confirm-revision-then-call-/experiment-bridge" | ...,
  "next_skill_hint": "/experiment-bridge OR /diagnostic-to-review OR /proposal-revise (more rounds)",
  "timestamp": "<ISO 8601 UTC>",
  "artifact_inventory": [
    "refine-logs/REVISION_INTAKE.md",
    "refine-logs/REVISION_REPORT.md",
    "refine-logs/FINAL_PROPOSAL.md",       // if target includes proposal
    "refine-logs/EXPERIMENT_PLAN.md",      // if target includes plan
    "orbit-research/<updated subset>.md"   // only the artifacts whose owning stage was re-run
  ],
  "codex_thread_id": "<for Phase 3 re-eval continuity within a single round>",
  "notes": "Optional"
}
```

### On entry — resume decision tree

Apply the canonical contract decision tree:

1. Read STATE if it exists.
2. `status = "completed"` AND user did not pass `— resume:` / `— fresh:` → ask "previous
   revision completed; new round with new critique?" Default fresh under AUTO_PROCEED.
3. `status = "in_progress"`:
   - `timestamp ≥ 24h` → stale; warn; default fresh start (delete STATE first).
   - `timestamp < 24h` → resume from `STATE.phase + 1`. For each phase ≤ STATE.phase,
     apply artifact-presence skip per the table below.
4. `status = "awaiting_human_continue"`:
   - Same skill re-invoked with new critique → start Round N+1 (in_progress); preserve
     prior critique inventory; append new critiques.
   - Same skill re-invoked with `— resume: true` and no new critique → no-op (STOP A
     review still pending).
   - Downstream skill invoked elsewhere → that skill reads this STATE and treats as approval.

### Idempotent phase skip

| Phase | Expected output | Skip condition |
|---|---|---|
| phase-0-intake | `refine-logs/REVISION_INTAKE.md` | exists AND STATE entry says completed |
| phase-1-targeted-reruns | `orbit-research/<updated>.md` files per critique inventory | each artifact mtime > intake mtime |
| phase-2-anchor-simplicity | `REVISION_INTAKE.md` updated with `anchor_check` + `simplicity_check` fields | both fields populated |
| phase-3-reintegrate | `refine-logs/FINAL_PROPOSAL.md` and/or `EXPERIMENT_PLAN.md` mtime > Phase 2 | regenerated this round |
| phase-4-summary | `refine-logs/REVISION_REPORT.md` | exists AND STATE.status = `awaiting_human_continue` |

## Workflow

### Phase 0: Intake & Triage

Read inputs:
- target artifact(s) — load FINAL_PROPOSAL.md and/or EXPERIMENT_PLAN.md depending on `$ARGUMENTS`
- critique source — `— critiques:` inline string OR `— critique-file:` file path

Read all current v1.3 artifacts under `orbit-research/` to build a section index for
critique mapping (PROBLEM_SELECTION, ASSUMPTION_LEDGER, ABSTRACT_TASK_MECHANISM,
BASELINE_CEILING, MECHANISM_IDEATION, ANALOGY_TRANSFER, ALGORITHM_TOURNAMENT,
CONTROL_DESIGN, NULL_RESULT_CONTRACT, COMPONENT_BUNDLE_LADDER, ALGORITHMIC_FORMALIZATION,
DIAGNOSTIC_EXPERIMENT_PLAN).

Parse the critique into structured items. Each item:

```text
{
  "id": "C<n>",
  "raw_text": "<exact user text>",
  "target_artifact": "FINAL_PROPOSAL.md" | "EXPERIMENT_PLAN.md" | "<orbit-research artifact>",
  "target_section": "<heading or paragraph anchor>",
  "owning_stage": <v1.3 stage number>,
  "suggested_direction": "<short paraphrase of what the user wants changed>"
}
```

**Owning-stage classification rules** (auto-applied; user can override with `— scope:`):

| Critique pattern | Owning stage | Affected artifact |
|---|---|---|
| "baseline ceiling weak" / "should beat <stronger baseline>" / "headroom not enough" | 7 | BASELINE_CEILING.md |
| "assumption A<n> doesn't hold" / "assume X but Y is true" | 4 | ASSUMPTION_LEDGER.md |
| "mechanism not elegant" / "wrong mechanism family" / "abstract task off" | 5 + 8 | ABSTRACT_TASK_MECHANISM.md, MECHANISM_IDEATION.md |
| "should consider analogy from <field>" / "transfer Y to X" | 9 | ANALOGY_TRANSFER.md |
| "tournament picked wrong sketch" / "S<n> would be better" / "switch to alternate" | 10 | ALGORITHM_TOURNAMENT.md |
| "experiment block N missing baseline" / "control X needed" | 11 + 13 | CONTROL_DESIGN.md, COMPONENT_BUNDLE_LADDER.md |
| "null result not interpretable" / "can't tell why it fails" | 12 | NULL_RESULT_CONTRACT.md |
| "bundle ladder skips a rung" / "components shouldn't bundle" | 13 | COMPONENT_BUNDLE_LADDER.md |
| "formalization wrong update rule" / "loss should be X" | 14 | ALGORITHMIC_FORMALIZATION.md |
| "diagnostic too expensive" / "smaller pilot" / "regime wrong" | 16 | DIAGNOSTIC_EXPERIMENT_PLAN.md |
| "claim too strong" / "scope too wide" / "evidence chain weak" | 21 | (target FINAL_PROPOSAL claim section directly; no orbit-research artifact yet) |
| free-form / unclear | 23 (red-team default) | flag for user clarification |

If a critique is unclear or matches multiple stages, ask the user inline (one question
per ambiguous item) before proceeding to Phase 1. Under AUTO_PROCEED, default to the
broadest applicable stage and log the ambiguity in `REVISION_INTAKE.md`.

Write `refine-logs/REVISION_INTAKE.md`:

```markdown
# Revision Intake — Round <N>
- Target: FINAL_PROPOSAL | EXPERIMENT_PLAN | both
- Critique source: inline | <file>
- Timestamp: <ISO>

## Critique Items

| ID | Owning Stage | Affected Artifact(s) | Raw Text | Suggested Direction |
|----|--------------|----------------------|----------|---------------------|
| C1 | 10 | ALGORITHM_TOURNAMENT.md | "..." | "switch winner to S5" |
| C2 | 4  | ASSUMPTION_LEDGER.md   | "..." | "mark A2 as falsified, add A12 for temporal correlation" |

## Stages To Re-run (Phase 1 plan)
- Stage 4: revise ASSUMPTION_LEDGER.md (driven by C2)
- Stage 10: revise ALGORITHM_TOURNAMENT.md (driven by C1)
```

**Write STATE** at end of Phase 0:

```jsonc
{
  "phase": "phase-0-intake",
  "round": <N>,
  "status": "in_progress",
  "target": "...",
  "critique_inventory": [/* parsed items, addressed: "pending" */],
  "next_action": "phase-1-targeted-reruns",
  "timestamp": "<now>",
  "artifact_inventory": ["refine-logs/REVISION_INTAKE.md"]
}
```

If `— human checkpoint: true`, write `awaiting_human_continue` here and stop. User
re-invocation continues to Phase 1.

### Phase 1: Targeted Stage Re-runs

For each critique item in the inventory whose `addressed = "pending"`:

1. Look up the owning stage's prompt in `shared-references/research-harness-prompts.md`
   (sections 4/5/7/8/9/10/11/12/13/14/16/21/23).
2. Set Codex mode per `innovation-loops.md` §7:
   - Stages 8/9/10/18.5 → COLLABORATIVE (use template §7.1)
   - Everything else → ADVERSARIAL (default semantic-code-audit-style)
3. Build the re-run prompt:
   ```text
   <stage harness prompt body>

   ## Revision context
   - Existing artifact: <orbit-research/<file>.md content>
   - User critique: <C<n>.raw_text>
   - Suggested direction: <C<n>.suggested_direction>

   Re-run this stage with the user's critique as binding feedback. Update the artifact
   in place (preserve fields the critique does not touch). Append a "## Revision history"
   footer recording: the critique ID that triggered the change, the prior content of any
   touched section, and the new content.
   ```
4. Invoke Codex (or for some stages, the corresponding sub-skill — see "Optional skill
   delegation" below).
5. Write the updated artifact to `orbit-research/<file>.md`.
6. Mark `critique_inventory[i].addressed = "yes"` (preliminary; final addressed status
   set after Phase 2 anchor/simplicity check).

**Optional skill delegation** when the critique implies a heavier re-run than a single
stage:
- "needs more literature in <area>" → invoke `/research-lit "<focused query>"`; rewrite
  affected sections of `LITERATURE_MAP.md` and re-derive PROBLEM_SELECTION if needed.
- "more candidate mechanisms" → invoke `/idea-creator "<direction>"` then re-run Stage 8.
- "experiment design needs full rebuild" → defer to a separate `/experiment-plan` invocation
  in Phase 3 rather than patching here.

**Codex unavailability:**
- Innovation re-runs (Stage 8/9/10): mark the artifact's "Codex collaborative additions"
  section `NOT_AVAILABLE (codex_mcp_unreachable)` and continue (advisory).
- Adversarial re-runs (Stage 11/14 etc.): single-model fallback; flag in REVISION_REPORT.md.
- Critique items that REQUIRE Codex (e.g. semantic audit verdict change) and Codex is down:
  mark `addressed = "rejected: codex_mcp_unreachable"` and surface to user.

**Write STATE** at end of Phase 1 with updated `artifact_inventory` listing every
`orbit-research/<file>.md` that changed.

### Phase 2: Anchor + Simplicity Check

Reuse `/research-refine` Phase 3 logic verbatim. The two checks operate on the
**collected revision set** (all updated artifacts from Phase 1 + the existing
PROBLEM_SELECTION.md as the original-problem anchor):

**Anchor Check.** Construct the prompt:

```text
You are checking whether a proposed revision still solves the originally selected problem.

Problem Anchor (immutable, from orbit-research/PROBLEM_SELECTION.md):
<problem statement + selection rationale>

Revised artifacts (Phase 1 outputs):
- <list of updated artifact paths + the user critique that drove each>

Question: does the revised set of artifacts, taken together, still solve the problem
anchor? Specifically check:
1. Is the dominant contribution still aimed at the anchored problem, or did revisions
   drift to a different problem?
2. Did any "factual" assumption become "working" without a corresponding plan to test it?
3. Did the mechanism family change in a way that no longer addresses the named bottleneck?

Return on its own line: ANCHOR_PASS | ANCHOR_DRIFT | ANCHOR_AMBIGUOUS
Then a one-paragraph rationale per critique item. If DRIFT, list which critique caused it.
```

**Simplicity Check.** Construct the prompt:

```text
You are checking whether a proposed revision adds unnecessary complexity.

Constants from /research-refine:
- MAX_NEW_TRAINABLE_COMPONENTS = 2
- MAX_PRIMARY_CLAIMS = 2
- "smallest adequate mechanism wins"

Revised artifacts:
- <list>

Question: does the revised method violate any simplicity constraint?
1. Did total trainable components exceed MAX_NEW_TRAINABLE_COMPONENTS?
2. Did the claim count exceed MAX_PRIMARY_CLAIMS?
3. Did revisions add a mechanism that could be removed without losing the anchored claim?

Return on its own line: SIMPLICITY_PASS | SIMPLICITY_VIOLATION
Then list specific violations with which critique caused them.
```

For each critique item:
- If both checks pass → `addressed = "yes"`.
- If anchor drift caused by this critique → `addressed = "rejected: anchor-check-failed"` and revert that critique's Phase 1 artifact updates (restore from `orbit-research/<file>.md.prerevise.<round>` snapshot — write snapshots before each Phase 1 update).
- If simplicity violation caused by this critique → `addressed = "rejected: simplicity-check-failed"` and revert similarly.

Update `REVISION_INTAKE.md` with the check results and final `addressed` status per item.

**Write STATE** at end of Phase 2.

### Phase 3: Re-integrate (target-dependent)

For each critique item with `addressed = "yes"`, the relevant `orbit-research/<file>.md`
has been updated (and survived anchor + simplicity check). Now re-integrate into the
target artifact(s):

**If target includes FINAL_PROPOSAL.md:**

Invoke `/research-refine` on the existing FINAL_PROPOSAL.md, with the revised
`orbit-research/*` artifacts as new context and the critique items as a synthetic reviewer
round (framed as "User dissatisfaction audit, round <N>" rather than GPT-5.5 reviewer):

```bash
/research-refine "refine-logs/FINAL_PROPOSAL.md" — resume: true
```

`/research-refine` reads its own REFINE_STATE.json; this skill writes a marker in there
hinting "revision round <N> from /proposal-revise; treat critique items in
REVISION_INTAKE.md as the new reviewer round." `/research-refine` Phase 3 absorbs the
critique into the next refinement round and Phase 4 re-evaluates.

After `/research-refine` returns, copy its `refine-logs/FINAL_PROPOSAL.md` (regenerated)
into our artifact_inventory.

**If target includes EXPERIMENT_PLAN.md:**

Invoke `/experiment-plan` on the (possibly-revised) FINAL_PROPOSAL.md:

```bash
/experiment-plan "refine-logs/FINAL_PROPOSAL.md" — fresh: true
```

`/experiment-plan` (T4-upgraded) reads the v1.3 grounding/innovation artifacts produced
in Phase 1 and writes a v1.3-aware EXPERIMENT_PLAN.md that cites the revised
ASSUMPTION_LEDGER row IDs and ALGORITHM_TOURNAMENT sketch IDs.

**Codex Phase 3 re-evaluation** (per `auto-paper-improvement-loop` reviewer-independence):

For each addressed critique, evaluate whether the revision actually fixed the issue. Use
a **fresh** `mcp__codex__codex` thread (NOT `codex-reply`) — fresh context defeats the
"of course my fix works" confirmation bias:

```text
Reviewer Independence Protocol — fresh thread, no prior conversation history.

Original critique: <C<n>.raw_text>
Pre-revision artifact excerpt: <relevant section from snapshot>
Post-revision artifact excerpt: <relevant section from current artifact>

Evaluate on three dimensions (1-5 each):
1. Does the post-revision artifact address the critique's substance?
2. Does the post-revision artifact preserve the original problem anchor?
3. Did the revision introduce new issues (over-complexity, scope drift, broken citations)?

Return: SCORE_DELTA + brief rationale.
```

If `SCORE_DELTA` indicates the revision did NOT address the critique adequately AND
`round < MAX_ROUNDS` → loop back to Phase 1 with the unaddressed items + Codex's specific
gap analysis as additional context. Increment `STATE.round`.

If `SCORE_DELTA` is positive across all addressed items OR `round = MAX_ROUNDS` → proceed
to Phase 4.

**Codex unavailability in Phase 3:**
- `/research-refine` and `/experiment-plan` invocations still run (they have their own
  Codex unavailability handling).
- The Codex re-evaluation step is skipped; mark each critique
  `addressed = "yes (codex_re_eval skipped)"` and write
  `Phase 3 Codex re-eval: SKIPPED (codex_mcp_unreachable)` in REVISION_REPORT.md.

**Write STATE** at end of Phase 3.

### Phase 4: Diff Report + STOP

Write `refine-logs/REVISION_REPORT.md`:

```markdown
# Revision Report — Round <final round>

- Target: FINAL_PROPOSAL | EXPERIMENT_PLAN | both
- Critique source: inline | <file>
- Round: <N> of MAX_ROUNDS=<M>
- Started: <Phase 0 timestamp>
- Completed: <now>

## Critique Resolution

| ID | Owning Stage | Addressed | Codex Re-eval Score Delta | Notes |
|----|--------------|-----------|---------------------------|-------|
| C1 | 10 | yes | +2.3 / 5 | tournament winner switched S2 → S5 |
| C2 | 4  | yes | +1.8 / 5 | A2 reclassified factual → working; new A12 added |
| C3 | 11 | rejected: anchor-check-failed | — | proposed extra baseline drifts to different problem |

## Stages Re-run

- Stage 4: ASSUMPTION_LEDGER.md updated (driven by C2)
- Stage 10: ALGORITHM_TOURNAMENT.md updated (driven by C1)

## Artifact Diffs (lines added / removed)

- orbit-research/ASSUMPTION_LEDGER.md:    +12 / -3
- orbit-research/ALGORITHM_TOURNAMENT.md: +8  / -5
- refine-logs/FINAL_PROPOSAL.md:          +24 / -19  (regenerated by /research-refine)
- refine-logs/EXPERIMENT_PLAN.md:         +6  / -2   (regenerated by /experiment-plan; cites new A12, S5)

## Anchor + Simplicity Check Results

- ANCHOR_PASS — revised set still solves the originally selected problem
- SIMPLICITY_VIOLATION (one item, C3) — caused C3 to be rejected; revert applied

## Next steps

- Review the regenerated FINAL_PROPOSAL.md and EXPERIMENT_PLAN.md.
- If satisfied, invoke /experiment-bridge "refine-logs/EXPERIMENT_PLAN.md" to begin
  implementation (STOP B in the 4-stop HITL flow).
- If still dissatisfied, invoke /proposal-revise again with new critique points
  (Round <N+1> will be triggered).
```

**Write final STATE** at end of Phase 4 with **`awaiting_human_continue`** (the designed
human checkpoint of this skill — re-entry to STOP A):

```jsonc
{
  "skill": "proposal-revise",
  "phase": "phase-4-summary",
  "round": <final>,
  "status": "awaiting_human_continue",
  "target": "...",
  "critique_inventory": [/* with final addressed status */],
  "next_action": "human-must-confirm-revision-then-call-/experiment-bridge-or-/diagnostic-to-review",
  "next_skill_hint": "/experiment-bridge OR /diagnostic-to-review OR /proposal-revise (more rounds)",
  "timestamp": "<now>",
  "artifact_inventory": [/* full list */]
}
```

`awaiting_human_continue` is the **deliberate** terminal state. The user inspects
`REVISION_REPORT.md` + the regenerated FINAL_PROPOSAL.md / EXPERIMENT_PLAN.md and decides:

- **Accept revision and continue forward** — invoke `/experiment-bridge`. The downstream
  skill reads `PROPOSAL_REVISE_STATE.json`, sees `awaiting_human_continue`, treats
  invocation as approval, proceeds to Stage 15 plan-code audit.
- **More revisions needed** — invoke `/proposal-revise` again with new critique points;
  triggers Round N+1. Already-addressed items remain (idempotent skip); only new critiques
  go through Phase 1.
- **Reverted critiques unsatisfactory** — for items rejected by anchor/simplicity check,
  reframe the critique to avoid the rejection cause and re-invoke. The revert snapshots
  in `orbit-research/<file>.md.prerevise.<round>` are preserved for diff inspection.
- **Abandon revision direction** — stop invoking; STATE stays `awaiting_human_continue`.
  To clear and start a different revision, pass `— fresh: true`.

To skip this checkpoint and run straight through to `completed`, pass `— no-checkpoint: true`.

## ARIS / Sub-skill Unavailability

For each delegated invocation (`/research-refine`, `/experiment-plan`, `/research-lit`,
`/idea-creator`), follow the standard fallback pattern:

```text
Try slash invocation.
If skill not registered:
  Print "ORBIT skill <name> unavailable. Phase <N> degraded: <fallback or HUMAN_DECISION_REQUIRED>."
  Continue gracefully.
If load-bearing for the revision (e.g. /research-refine for proposal target):
  Escalate — do not silently produce a half-revised artifact.
```

Codex MCP unavailability per the three-tier degradation in
`shared-references/continuation-contract.md`:

| Tier | Where in this skill |
|---|---|
| Advisory | Phase 1 Stage 8/9/10 collaborative additions; Phase 3 Codex re-eval |
| Block pending human ack | None at this skill's gates (no scale-up, no commitment irreversible) |
| Load-bearing degradation | Phase 1 critique items requiring semantic Codex audit (mark `rejected: codex_mcp_unreachable`) |

## What This Skill Deliberately Does NOT Do

- Does **not** touch GPU. (Same scope boundary as `/idea-to-proposal`.)
- Does **not** modify v1.3 contract files (`research-agent-pipeline.md`,
  `research-harness-prompts.md`, etc.) — only reads them.
- Does **not** regenerate every v1.3 artifact — only those whose owning stage was flagged
  by a critique item (idempotent on unaffected artifacts).
- Does **not** auto-accept revisions — Phase 4 always ends `awaiting_human_continue`
  unless `— no-checkpoint: true`.
- Does **not** write `CLAIM_CONSTRUCTION.md`, `RED_TEAM_REVIEW.md`, etc. (those are STOP C
  territory, owned by `/diagnostic-to-review`).
- Does **not** auto-rerun `/idea-to-proposal` Phase 1 (Discovery — `/idea-discovery` or
  `/research-refine`); revision is in-place on existing artifacts.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Final Rule

```text
A user critique is binding feedback — but the revision must still preserve the
problem anchor and the simplicity discipline. Anchor drift and complexity creep
are not improvements; they are failure modes that this skill is designed to catch.
A rejected critique is not a refusal to listen; it is a flag that the user's
desired change would break what they originally chose to build.
```
