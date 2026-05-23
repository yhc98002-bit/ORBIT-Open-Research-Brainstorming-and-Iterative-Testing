---
name: research-refine
description: 'Turn a vague research direction into a problem-anchored, elegant, frontier-aware, implementation-oriented method plan via iterative GPT-5.5 xhigh review. Use when the user says "refine my approach", "帮我细化方案", "decompose this problem", "打磨idea", "refine research plan", "细化研究方案", or wants a concrete research method with a publishable normal-paper route instead of a vague or overbuilt idea.'
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, mcp__codex__codex, mcp__codex__codex-reply
---

> **ORBIT compatibility note:** This skill may still accept legacy v1.0 artifact aliases
> (e.g. `TASK_ONTOLOGY.md`, `COMPONENT_LADDER.md`, `TINY_RUN_AUDIT.md`), but new ORBIT
> refinement gates use the v1.3 artifact/gate contract defined in
> [`skills/shared-references/research-agent-pipeline.md`](../shared-references/research-agent-pipeline.md);
> v1.4 wrapper skills build on that contract without replacing it. Legacy names are read
> only as aliases.

# Research Refine: Problem-Anchored, Elegant, Frontier-Aware Plan Refinement

Refine and concretize: **$ARGUMENTS**

## Overview

Use this skill when the research problem is already visible but the technical route is still fuzzy. The goal is not to produce a bloated proposal or a benchmark shopping list. The goal is to turn a vague direction into a **problem -> focused method -> minimal validation** document that is concrete enough to implement, elegant enough to feel paper-worthy, and current enough to resonate in the foundation-model era.

Four principles dominate this skill:

1. **Do not lose the original problem.** Freeze an immutable **Problem Anchor** and reuse it in every round.
2. **The smallest adequate mechanism wins.** Prefer the minimal intervention that directly fixes the bottleneck.
3. **One paper, one dominant contribution.** Prefer one sharp thesis plus at most one supporting contribution.
4. **Modern leverage is a prior, not a decoration.** When LLM / VLM / Diffusion / RL / distillation / inference-time scaling naturally fit the bottleneck, use them concretely. Do not bolt them on as buzzwords.

```
User input (PROBLEM + vague APPROACH)
  -> Phase 0 (Claude): Freeze Problem Anchor
  -> Phase 1 (Claude): Scan grounding papers -> identify technical gap -> choose the sharpest route -> write focused proposal
  -> Phase 2 (Codex/GPT-5.5): Review for fidelity, specificity, contribution quality, and frontier leverage
  -> Phase 3 (Claude): Anchor check + simplicity check -> revise method -> rewrite full proposal
  -> Phase 4 (Codex, same thread): Re-evaluate revised proposal
  -> Repeat Phase 3-4 until OVERALL SCORE >= SCORE_THRESHOLD or MAX_ROUNDS reached
     (SCORE_THRESHOLD and MAX_ROUNDS are derived from REVIEWER_DIFFICULTY:
      medium → 9 / 5, hard / nightmare → 9.5 / 7)
  -> Phase 5: Save full history to refine-logs/
  -> STOP A handoff: /experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
```

## Constants

- **REVIEWER_MODEL = `gpt-5.5`** — Reviewer model used via Codex MCP.
- **REVIEWER_EFFORT = `xhigh`** — Codex `model_reasoning_effort` for the reviewer call.
  Override with `— effort: <level>` (one of `low`, `medium`, `high`, `xhigh`, `max`
  where `max` = `xhigh`). Subject to Codex MCP environment availability — if the
  requested level is unavailable, Codex falls back to the next lower available level
  and the fallback is logged in `STATE.notes`.
- **VENUE = `""`** — Target venue name (e.g. `ICLR`, `NeurIPS`, `ICML`, `CVPR`, `ACL`,
  `AAAI`, `ACM`, `IEEE_CONF`, `IEEE_JOURNAL`). When set, Phase 2 / Phase 4 reviewer
  prompts replace the default normal-paper venue target with the named venue
  so the reviewer framing is concrete to the user's actual target. Override with
  `— venue: <name>`. Default empty (uses the hardcoded list). Mirrors
  `/research-pipeline`'s `VENUE` constant.
- **PAPER_MODE = `normal`** — Override with
  `— paper-mode: <normal|breakthrough|benchmark|reproduction-plus|system|audit>`.
  Normal mode does not require a completely new algorithmic breakthrough by default.
- **REVIEW_POSTURE = `collaborator` before STOP A** — Override with
  `— review-posture: <collaborator|adversarial>`. Use adversarial posture after STOP C
  or when the user explicitly requests it.
- **NOVELTY_POLICY = `positioning-first`** — Load
  `../shared-references/research-posture.md` before review/refinement.
- **REVIEWER_DIFFICULTY = `medium`** — How strict the Phase 2 / Phase 4 reviewer
  is. Three levels (mirrors `/auto-review-loop`'s `REVIEWER_DIFFICULTY` so the user can
  pass the same `— difficulty:` flag through any wrapper skill — e.g. `/idea-to-proposal`,
  `/research-pipeline`):
  - `medium` (default): standard reviewer prompt; **SCORE_THRESHOLD = 9**,
    **MAX_ROUNDS = 5** (the historical defaults — backward-compatible).
  - `hard`: stricter collaborator before STOP A; **SCORE_THRESHOLD = 9.5**,
    **MAX_ROUNDS = 7**. The reviewer pushes harder on contribution sprawl, weak
    mechanism specificity, and unfocused validation while still providing survival
    routes.
  - `nightmare`: before STOP A, interpret as "strong collaborator review" unless the
    user explicitly sets `— review-posture: adversarial` or the workflow is after STOP C.
    In adversarial mode it adds per-dimension vetoes.
  Override with `— difficulty: <level>`.
- **MAX_ROUNDS** — derived from `REVIEWER_DIFFICULTY`: `medium → 5`, `hard → 7`,
  `nightmare → 7`. Default 5 (medium).
- **SCORE_THRESHOLD** — derived from `REVIEWER_DIFFICULTY`: `medium → 9`, `hard → 9.5`,
  `nightmare → 9.5`. Default 9 (medium). Note `nightmare` adds a per-dimension `≥ 8`
  side-condition on top of the overall threshold.
- **OUTPUT_DIR = `refine-logs/`** — Directory for round files and final report.
- **MAX_LOCAL_PAPERS = 15** — Maximum local papers/notes to scan for grounding.
- **MAX_CORE_EXPERIMENTS = 3** — Default cap for core validation blocks inside this skill.
- **MAX_PRIMARY_CLAIMS = 2** — Soft cap for paper-level claims. Prefer one dominant claim plus one supporting claim.
- **MAX_NEW_TRAINABLE_COMPONENTS = 2** — Soft cap for genuinely new trainable pieces. Exceed only if the paper breaks otherwise.

## ORBIT Refinement Gates

These gates are always-on. Load `../shared-references/research-agent-pipeline.md`,
`../shared-references/document-hygiene.md`, and `../shared-references/research-posture.md`
before refining. Run `mkdir -p orbit-research/`.

Before STOP A, refine from the proposal-stage artifacts only:

- `orbit-research/PROBLEM_SELECTION.md`
- `orbit-research/ASSUMPTION_LEDGER.md`
- `orbit-research/ABSTRACT_TASK_MECHANISM.md`  *(legacy alias accepted: `TASK_ONTOLOGY.md`)*
- `orbit-research/BASELINE_CEILING.md`

Do not force full experiment-planning contracts before STOP A. `CONTROL_DESIGN.md`,
`NULL_RESULT_CONTRACT.md`, and `COMPONENT_BUNDLE_LADDER.md` belong to
`/experiment-bridge` after STOP A. Before STOP A, include only a candidate validation
sketch, expected diagnostic, likely baseline/control needs, and null-result intuition.

The method proposal must identify the simplest strong baseline, the highest-headroom
regime, the intended mechanism, and the minimum evidence that would make the proposal
worth formal experiment planning.

> Override via argument if needed, e.g.
> `/research-refine "problem | approach" — max rounds: 3 — threshold: 9 — venue: ICLR — difficulty: hard — effort: xhigh`.
>
> The `— venue:` and `— difficulty:` flags mirror the upstream `/research-pipeline`
> and `/auto-review-loop` argument syntax respectively, so the same flag string passed
> to a wrapper skill (e.g. `/idea-to-proposal`) propagates here verbatim.

## State Persistence (Checkpoint Recovery)

Long-running refinement sessions may fail mid-way (e.g., API timeout, context compaction, or session interruption). To avoid losing completed work, persist state to `refine-logs/REFINE_STATE.json` after each phase boundary:

```json
{
  "phase": "review",
  "round": 1,
  "threadId": "019cd392-...",
  "last_score": 6.5,
  "last_verdict": "REVISE",
  "status": "in_progress",
  "venue": "",
  "difficulty": "medium",
  "effort": "xhigh",
  "max_rounds_effective": 5,
  "score_threshold_effective": 9.0,
  "timestamp": "2026-03-22T20:00:00"
}
```

**Field definitions:**

| Field | Values | Meaning |
|-------|--------|---------|
| `phase` | `"anchor"` / `"proposal"` / `"review"` / `"refine"` / `"done"` | Last **completed** phase |
| `round` | 0–MAX_ROUNDS | Current round number |
| `threadId` | string or null | Reviewer thread ID for `codex-reply` continuity |
| `last_score` | number or null | Most recent overall score from reviewer |
| `last_verdict` | string or null | Most recent verdict (READY / REVISE / RETHINK) |
| `status` | `"in_progress"` / `"awaiting_human_continue"` / `"awaiting_user_action"` / `"completed"` | Loop status — four-state enum per `../shared-references/continuation-contract.md` |
| `venue` | string (e.g. `"ICLR"`) or `""` | Target venue parsed from `— venue:` flag. Empty string = normal ML venue target without breakthrough-only assumptions. |
| `difficulty` | `"medium"` / `"hard"` / `"nightmare"` | Reviewer difficulty parsed from `— difficulty:` flag. Drives `max_rounds_effective` + `score_threshold_effective` + reviewer prompt routing. Default `"medium"`. |
| `effort` | `"low"` / `"medium"` / `"high"` / `"xhigh"` / `"max"` | Codex `model_reasoning_effort` parsed from `— effort:` flag (`max` = `xhigh`). Default `"xhigh"`. The actual effort honored is recorded in `STATE.notes` if Codex MCP fell back. |
| `max_rounds_effective` | integer | The MAX_ROUNDS in effect for this run after `difficulty` derivation: `medium → 5`, `hard / nightmare → 7`. |
| `score_threshold_effective` | number | The SCORE_THRESHOLD in effect for this run after `difficulty` derivation: `medium → 9.0`, `hard / nightmare → 9.5`. |
| `timestamp` | ISO 8601 | When state was last written |
| `next_action` | string (optional) | Free-text hint for resume |
| `next_skill_hint` | string (optional) | Downstream skill the user should call next (e.g. `/experiment-plan`) |
| `artifact_inventory` | array (optional) | Output artifacts produced so far |

**Write rules:**
- **Write after each phase completes** (not before). Overwrite each time — only the latest state matters.
- **Default state during execution:** `"in_progress"`.
- **On user-paused checkpoint** (when `— human checkpoint: true` is set, or after the
  proposal stabilises if the user wants to inspect before downstream consumption): set
  `"status": "awaiting_human_continue"` and include `next_skill_hint`. The next caller
  (same skill or downstream) reads this and treats invocation as approval per the
  cross-skill resume rules in `continuation-contract.md`.
- **On completion** (Phase 5 finished AND user did not request the human checkpoint):
  set `"status": "completed"`.

This is the v1.3 canonical contract; old STATE files with only `in_progress` / `completed`
still parse. `awaiting_human_continue` and `awaiting_user_action` are additive states.

## Output Structure

```
refine-logs/
├── REFINE_STATE.json
├── round-0-initial-proposal.md
├── round-1-review.md
├── round-1-refinement.md
├── round-2-review.md
├── round-2-refinement.md
├── ...
├── REVIEW_SUMMARY.md
├── FINAL_PROPOSAL.md
├── REFINEMENT_REPORT.md
└── score-history.md
```

Every `round-N-refinement.md` must contain a **full anchored proposal**, not just incremental fixes.

## Workflow

### Initialization (Checkpoint Recovery)

Before starting any phase, check whether a previous run left a checkpoint:

1. **Check for `refine-logs/REFINE_STATE.json`**:
   - If it **does not exist** → **fresh start** (proceed to Phase 0 normally)
   - If it exists AND `status` is `"completed"` → **fresh start** (delete state file, previous run finished)
   - If it exists AND `status` is `"in_progress"` AND `timestamp` is **older than 24 hours** → **fresh start** (stale state from a killed/abandoned run — delete the file)
   - If it exists AND `status` is `"in_progress"` AND `timestamp` is **within 24 hours** → **resume**

2. **On resume**, read the state file and recover context:
   - Read all existing `refine-logs/round-*.md` files to restore prior work
   - Read `refine-logs/score-history.md` if it exists
   - Recover `threadId` for reviewer thread continuity
   - Log to the user: `"Checkpoint found. Resuming after phase: {phase}, round: {round}."`
   - **Jump to the next phase** based on the saved `phase` value:

   | Saved `phase` | What was completed | Resume from |
   |---------------|-------------------|-------------|
   | `"anchor"` | Phase 0 done | Phase 1 (read anchor from round-0 context) |
   | `"proposal"` | Phase 1 done | Phase 2 (read `round-0-initial-proposal.md`) |
   | `"review"` | Phase 2 or 4 done | Phase 3 (read latest `round-N-review.md`) |
   | `"refine"` | Phase 3 done | Phase 4 (read latest `round-N-refinement.md`) |

3. **On fresh start**, ensure `refine-logs/` directory exists and proceed to Phase 0.

### Phase 0: Freeze the Problem Anchor

Load and follow [problem_anchor.md](prompts/problem_anchor.md). Keep the extracted anchor
verbatim through every proposal and refinement round; mark reviewer suggestions that change
the problem as drift.

**Checkpoint:** Write `refine-logs/REFINE_STATE.json` with phase `anchor`, round `0`,
`status = in_progress`, and the current timestamp.

### Phase 1: Build the Initial Proposal

Load and follow [initial_proposal.md](prompts/initial_proposal.md). The prompt preserves
the full grounding scan, technical-gap, route-selection, concrete-method, and minimal
claim-driven validation template.

Save the result to `refine-logs/round-0-initial-proposal.md` and update
`refine-logs/REFINE_STATE.json` with phase `proposal`, round `0`, and current status.

### Phase 2: External Method Review (Round 1)

Load [reviewer_critique.md](prompts/reviewer_critique.md) and send the full proposal to
Codex/GPT-5.5 with the parsed `VENUE`, `PAPER_MODE`, `REVIEWER_DIFFICULTY`,
`REVIEW_POSTURE`, and `REVIEWER_EFFORT` substitutions. Preserve the difficulty
escalation blocks and Codex standalone handoff behavior from that asset exactly.

Save the raw response to `refine-logs/round-1-review.md`, save the `threadId`, parse score
and verdict, and update `refine-logs/REFINE_STATE.json` with phase `review`.

### Phase 3: Parse Feedback and Revise the Method

#### Step 3.1: Parse the Review

Extract:

- **Problem Fidelity**
- **Method Specificity**
- **Contribution Quality**
- **Frontier Leverage**
- **Feasibility**
- **Validation Focus**
- **Paper-Mode Fit**
- **Overall score**
- **Verdict**
- **Drift Warning**
- **Simplification Opportunities**
- **Modernization Opportunities**
- **Action items** ranked by priority

Update `refine-logs/score-history.md`:

```markdown
# Score Evolution

| Round | Problem Fidelity | Method Specificity | Contribution Quality | Frontier Leverage | Feasibility | Validation Focus | Paper-Mode Fit | Overall | Verdict |
|-------|------------------|--------------------|----------------------|-------------------|-------------|------------------|-----------------|---------|---------|
| 1     | X                | X                  | X                    | X                 | X           | X                | X               | X       | REVISE  |
```

**STOP CONDITION**: If overall score >= SCORE_THRESHOLD, verdict is READY, and there is no unresolved drift warning, skip to Phase 5.

#### Step 3.2: Revise With an Anchor Check and a Simplicity Check

Load and follow [anchor_simplicity_revision.md](prompts/anchor_simplicity_revision.md).
The asset preserves the exact revision discipline: copy the problem anchor, run anchor
and simplicity checks, accept valid feedback, push back on drift, and save the round-N
refinement artifact.

**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with phase `refine`, round `N`,
and the parsed review state.

### Phase 4: Re-evaluation (Round 2+)

Send the revised proposal back to GPT-5.5 in the **same thread**. The
REVIEWER_DIFFICULTY routing established in Phase 2 persists across all rounds —
do NOT downgrade difficulty mid-loop, and do NOT re-issue the difficulty
escalation paragraphs (the reviewer thread retains them from Phase 2). The
verdict rule below uses the same SCORE_THRESHOLD derived from
REVIEWER_DIFFICULTY.

```
mcp__codex__codex-reply:
  threadId: [saved from Phase 2]
  model: REVIEWER_MODEL
  config: {"model_reasoning_effort": REVIEWER_EFFORT}
  prompt: |
    [Round N re-evaluation]

    I revised the proposal based on your feedback.
    First, check whether the original Problem Anchor is still preserved.
    Second, judge whether the method is now more concrete, more focused, and more current.

    Key changes:
    1. [Method change 1]
    2. [Method change 2]
    3. [Simplification / modernization / pushback if any]

    === REVISED PROPOSAL ===
    [Paste the FULL revised proposal]
    === END REVISED PROPOSAL ===

    Please:
    - Re-score the same 7 dimensions and overall
    - State whether the Problem Anchor is preserved or drifted
    - State whether the dominant contribution is now sharper or still too broad
    - State whether the method is simpler or still overbuilt
    - State whether the frontier leverage is now appropriate or still old-school / forced
    - Focus new critiques on missing mechanism, weak training signal, weak integration point, pseudo-novelty, or unnecessary complexity
    - Use the same verdict rule: READY only if overall score >= SCORE_THRESHOLD and no blocking issue remains (and, when REVIEWER_DIFFICULTY = nightmare, every individual dimension >= 8)

    Same output format: 7 scores, overall score, verdict, drift warning, simplification opportunities, modernization opportunities, remaining action items.
```

Save review to `refine-logs/round-N-review.md`.

**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "review", "round": N, "threadId": "<saved>", "last_score": <parsed>, "last_verdict": "<parsed>", ...}`.

Then return to Phase 3 until:

- **Overall score >= SCORE_THRESHOLD** and verdict is READY and no unresolved drift
- or **MAX_ROUNDS reached**

### Phase 5: Final Report and Logs

#### Step 5.1: Write `refine-logs/REVIEW_SUMMARY.md`

This file is the high-level round-by-round review record. It should answer: each round was trying to solve what, what changed, what got resolved, and what remained.

```markdown
# Review Summary

**Problem**: [user's problem]
**Initial Approach**: [user's vague approach]
**Date**: [today]
**Rounds**: N / MAX_ROUNDS
**Final Score**: X / 10
**Final Verdict**: [READY / REVISE / RETHINK]

## Problem Anchor
[Verbatim anchor used across all rounds]

## Round-by-Round Resolution Log

| Round | Main Reviewer Concerns | What This Round Simplified / Modernized | Solved? | Remaining Risk |
|-------|-------------------------|------------------------------------------|---------|----------------|
| 1     | [top issues from review] | [main method changes]                    | [yes / partial / no] | [if any] |
| 2     | ...                     | ...                                      | ...     | ...            |

## Overall Evolution
- [How the method became more concrete]
- [How the dominant contribution became more focused]
- [How unnecessary complexity was removed]
- [How modern technical leverage improved or stayed intentionally minimal]
- [How drift was avoided or corrected]

## Final Status
- Anchor status: [preserved / corrected / unresolved]
- Focus status: [tight / slightly broad / still diffuse]
- Modernity status: [appropriately frontier-aware / intentionally conservative / still old-school]
- Strongest parts of final method:
- Remaining weaknesses:
```

#### Step 5.2: Write the progressive-disclosure proposal bundle

Write `refine-logs/FINAL_PROPOSAL.md` as a short **index**, not as the full proposal.
It should route readers to the right level of detail and avoid review chatter, round
history, raw reviewer output, repeated caveats, or long method exposition.

Do not paste reviewer objections or rebuttal-style defenses into `FINAL_PROPOSAL.md`.
Resolve them by changing method/scope or moving decision history to
`orbit-research/RESEARCH_DECISION_LOG.md`, claim support to
`orbit-research/CLAIM_CONSTRUCTION.md`, and reviewer concerns to
`orbit-research/RED_TEAM_REVIEW.md`.

```markdown
# Final Proposal — Index

**Purpose**: this file is an **index**. The proposal is split into progressive-disclosure files so agents read only the layer they need.

**Project**: [one-line project / method / target venue / current status]

## Proposal Status

**Status**: PROPOSAL_READY
**Allowed values**: PROPOSAL_READY / EXPERIMENT_PLAN_READY / SCALE_READY / SUPPORTED / REFRAMED / ARCHIVED
**Evidence basis**: proposal/refinement only; central hypotheses are tracked in the risk register and not validated until diagnostics support them
**Next gate**: `/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"` for experiment planning, implementation, and plan-code audit
**Last status change**: <ISO date> — created by `/research-refine`

## Critical Hypotheses

Brief summary only. The canonical risk register lives in
`orbit-research/ASSUMPTION_LEDGER.md` when present.

| ID | Role | Confidence | Cheapest diagnostic | If false |
|----|------|------------|----------------------|----------|
| H1 | paper-breaking/supporting/optional | low/medium/high | [diagnostic] | continue/weaken/reframe/archive |

## Read first

| File | Purpose | Audience | Length |
|---|---|---|---|
| `FINAL_PROPOSAL_SHORT.md` | Pitch document: problem, core reframing, method, claims, next gate | mentor / coauthor / quick self-review | 2-4 pages |

## Method spec

| File | Purpose |
|---|---|
| `METHOD_SPEC.md` | Implementation contract: equations, modules, data flow, training/inference protocol, hyperparameters |
| `FAILURE_CONTRACT.md` | Failure modes, null-result routing, and forbidden post-hoc reframings, if not already covered by `orbit-research/NULL_RESULT_CONTRACT.md` |

## Execution

| File | Purpose |
|---|---|
| `EXPERIMENT_PLAN.md` | Index for the experiment plan |
| `EXPERIMENT_PLAN_EXEC.md` | Claim map, experiment blocks, run order, gates, budget |

## Archive

| File | Purpose |
|---|---|
| `FINAL_PROPOSAL_FULL.md` | Optional archive of the previous monolithic proposal or revision-history wording. Create only when preserving history is useful. |

## Reading paths

- First time on this project -> `FINAL_PROPOSAL_SHORT.md`
- Implementing the method -> `METHOD_SPEC.md`
- Running experiments -> `EXPERIMENT_PLAN.md` then `EXPERIMENT_PLAN_EXEC.md`
- Something broke -> `FAILURE_CONTRACT.md` or `orbit-research/NULL_RESULT_CONTRACT.md`
- Reviewer asks about past wording -> `FINAL_PROPOSAL_FULL.md`, if present

## Status

**STATE**: [READY / REVISE / RETHINK / awaiting_human_continue]
**Next gate**: [next decision or experiment gate]
```

Also write:

- `refine-logs/FINAL_PROPOSAL_SHORT.md` — the clean 2-4 page proposal. It must include the same `## Proposal Status` block and a compact `## Critical Hypotheses` table, then only the problem, thesis, method overview, core claims, strongest baselines, main risks, and next gate.
- `refine-logs/METHOD_SPEC.md` — the implementation-level method contract. This is where formulas, module boundaries, hyperparameters, and data flow belong.
- `refine-logs/FAILURE_CONTRACT.md` — only when failure routing is not already cleanly represented in `orbit-research/NULL_RESULT_CONTRACT.md`.
- `refine-logs/FINAL_PROPOSAL_FULL.md` — optional archive only when the current run started from a useful monolithic proposal or when preserving round-history language matters.

If the final verdict is not READY, still write the best current index, short proposal, and method spec, and mark the unresolved status in the index.

#### Step 5.3: Write `refine-logs/REFINEMENT_REPORT.md`

```markdown
# Refinement Report

**Problem**: [user's problem]
**Initial Approach**: [user's vague approach]
**Date**: [today]
**Rounds**: N / MAX_ROUNDS
**Final Score**: X / 10
**Final Verdict**: [READY / REVISE / RETHINK]

## Problem Anchor
[Verbatim anchor used across all rounds]

## Output Files
- Review summary: `refine-logs/REVIEW_SUMMARY.md`
- Proposal index: `refine-logs/FINAL_PROPOSAL.md`
- Short proposal: `refine-logs/FINAL_PROPOSAL_SHORT.md`
- Method spec: `refine-logs/METHOD_SPEC.md`
- Optional archive: `refine-logs/FINAL_PROPOSAL_FULL.md`

## Score Evolution

| Round | Problem Fidelity | Method Specificity | Contribution Quality | Frontier Leverage | Feasibility | Validation Focus | Paper-Mode Fit | Overall | Verdict |
|-------|------------------|--------------------|----------------------|-------------------|-------------|------------------|-----------------|---------|---------|
| 1     | ...              | ...                | ...                  | ...               | ...         | ...              | ...             | ...     | ...     |

## Round-by-Round Review Record

| Round | Main Reviewer Concerns | What Was Changed | Result |
|-------|-------------------------|------------------|--------|
| 1     | [top issues]            | [main fixes]     | [resolved / partial / unresolved] |
| 2     | ...                     | ...              | ...    |

## Final Proposal Snapshot
- Canonical navigation entry lives in `refine-logs/FINAL_PROPOSAL.md`
- Clean short version lives in `refine-logs/FINAL_PROPOSAL_SHORT.md`
- Implementation details live in `refine-logs/METHOD_SPEC.md`
- Summarize the final thesis in 3-5 bullets here

## Method Evolution Highlights
1. [Most important simplification or focusing move]
2. [Most important mechanism upgrade]
3. [Most important modernization or justification for staying simple]

## Pushback / Drift Log
| Round | Reviewer Said | Author Response | Outcome |
|-------|---------------|-----------------|---------|
| 1     | [criticism]   | [pushback + anchor / evidence] | [accepted / rejected] |

## Remaining Weaknesses
[Honest unresolved issues]

## Raw Reviewer Responses

<details>
<summary>Round 1 Review</summary>

[Full verbatim response from GPT-5.5]

</details>

...

## Next Steps
- If READY: proceed to `/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"` for experiment planning, implementation, and plan-code audit
- If REVISE: manually address the remaining mechanism weaknesses, then re-run `/research-refine`
- If RETHINK: revisit the core mechanism, possibly with `/idea-creator`
```

#### Step 5.4: Finalize `score-history.md`

Ensure it contains the complete score evolution table using the new dimensions.

#### Step 5.5: Present a Brief Summary to the User

```
Refinement complete after N rounds.

Final score: X/10 (Verdict: READY / REVISE / RETHINK)

Anchor status:
- [preserved / drift corrected / unresolved concern]

Focus status:
- [tight / slightly broad / still diffuse]

Modernity status:
- [appropriately frontier-aware / intentionally conservative / still old-school]

Key method upgrades:
- [method change 1]
- [method change 2]

Remaining concerns:
- [if any]

Review summary: refine-logs/REVIEW_SUMMARY.md
Full report: refine-logs/REFINEMENT_REPORT.md
Proposal index: refine-logs/FINAL_PROPOSAL.md
Short proposal: refine-logs/FINAL_PROPOSAL_SHORT.md
Method spec: refine-logs/METHOD_SPEC.md
Suggested next step: /experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
```

**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "done", "status": "completed", ...}`.

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — apply selective milestone timestamping rules
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Progressive disclosure.** Keep `FINAL_PROPOSAL.md` as an index. Put the clean pitch in `FINAL_PROPOSAL_SHORT.md`, implementation detail in `METHOD_SPEC.md`, and long history in `FINAL_PROPOSAL_FULL.md` only when it is useful.
- **Document hygiene.** Do not paste reviewer objections or rebuttal-style defenses into `FINAL_PROPOSAL`. Resolve them by changing method/scope or moving decision history to `RESEARCH_DECISION_LOG`, claim support to `CLAIM_CONSTRUCTION`, and reviewer concerns to `RED_TEAM_REVIEW`.

- **Anchor first, every round.** Always carry forward the same Problem Anchor.
- **One paper, one dominant contribution.** Avoid multiple parallel contributions unless the paper truly needs them.
- **The smallest adequate mechanism wins.** Bigger is not automatically better.
- **Prefer reuse over invention.** Start from strong existing backbones and add only what the bottleneck requires.
- **Modern techniques are a prior, not a decoration.** Use LLM / VLM / Diffusion / RL-era components when they sharpen the method, not when they only make the proposal sound trendy.
- **Minimal experiments.** Inside this skill, experiments only need to prove the core claims.
- **Review the mechanism, not the parts count.** A long module list is not novelty.
- **Pushback is encouraged.** If reviewer feedback causes drift or unnecessary complexity, argue back with evidence.
- **ALWAYS use `config: {"model_reasoning_effort": "xhigh"}`** for all Codex review calls.
- **Save `threadId` from Phase 2** and use `mcp__codex__codex-reply` for later rounds.
- **Codex remains required.** If MCP/auth/sandbox fails, export/import a standalone Codex
  review via `/import-codex-review`; do not mark the review satisfied until an MCP or
  imported standalone Codex response exists.
- **Do not fabricate results.** Only describe expected evidence and planned experiments.
- **Be specific about compute and data assumptions.** Vague "we'll train a model" is not enough.
- **Document in the right layer.** Save raw reviews, anchor checks, simplicity checks, and major method changes in round files or `REFINEMENT_REPORT.md`; do not carry them into `FINAL_PROPOSAL`.

## Composing with Other Skills

This skill sits between idea discovery and execution:

```
/research-refine-pipeline       -> legacy one-shot refine + experiment planning when explicitly requested
/idea-creator "direction"       -> candidate ideas
/research-refine "PROBLEM: ... | APPROACH: ..."  <- you are here
/experiment-bridge              -> experiment planning + implementation + plan-code audit + STOP B
/diagnostic-to-review           -> formal diagnostic + interpretation + conditional-required claim/review
```

Typical flow:

1. `/idea-creator` or local reading gives you a problem and a vague method direction
2. `/research-refine` turns that into an anchored, elegant, frontier-aware method plan
3. `/experiment-bridge` turns the approved proposal into an experiment plan, implements code, and writes `PLAN_CODE_AUDIT.md`
4. `/diagnostic-to-review` executes formal diagnostics and routes results
5. Later loops operate on results, not just ideas

This skill also works standalone if you already know the problem and just need the method to become concrete.
