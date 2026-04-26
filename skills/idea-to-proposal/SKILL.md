---
name: idea-to-proposal
description: "ORBIT v1.3 thin pipeline from a research-area keyword OR a draft idea .md file to a full v1.3 proposal artifact set. Chains existing /idea-discovery (for keywords) or /research-refine (for .md), then runs Stage 4/5/7 (Grounding) + Stage 8/9/10 (Innovation, Codex collaborative) + a final /research-refine pass that integrates the tentative sketch winner. Outputs FINAL_PROPOSAL.md plus the seven Discovery/Grounding/Innovation artifacts. Does NOT trigger Validation (no experiments, no scale-up, no paper). Use when user says \"领域到proposal\", \"出proposal\", \"想法到方案\", \"idea-to-proposal\", \"proposal pipeline\", \"从领域跑到方案\", or wants a v1.3-complete proposal package without committing to runs yet."
argument-hint: [research-area-keyword OR path/to/draft-idea.md]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /idea-to-proposal — v1.3 Discovery → Grounding → Innovation → Proposal

Run a v1.3-complete proposal pipeline for: **$ARGUMENTS**

## Overview

This skill chains existing skills + the v1.3 Grounding and Innovation Spines into one
non-Validation pipeline. It produces a problem-anchored proposal **plus** the v1.3
artifact set that distinguishes ORBIT from earlier versions: assumption ledger, abstract
task / mechanism framing, baseline ceiling, mechanism ideation, analogy transfer, and
algorithm sketch tournament.

**Scope boundary** — this skill stops *before* the Validation Spine. It does not write
`CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`, `COMPONENT_BUNDLE_LADDER.md`,
`ALGORITHMIC_FORMALIZATION.md`, `PLAN_CODE_AUDIT.md`, or run any experiment. To take the
proposal further, hand off to `/research-pipeline` Stage 11+ or `/experiment-plan`.

```
Input:                     Phase 1                Phase 2 (Grounding)        Phase 3 (Innovation, Codex collab)        Phase 4              Phase 5
keyword ────► /idea-discovery ──┐
.md file ───► /research-refine ─┴►  Stage 4 → 5 → 7  ──────────────►  Stage 8 → 9 → 10  ──────────────►  /research-refine final pass ────► PIPELINE_SUMMARY.md
                                    (assumption    abstract  baseline)    (mechanism   analogy   sketch)    (integrates winner sketch)
```

## Constants

- **OUTPUT_ROOT_V13 = `orbit-research/`** — v1.3 grounding + innovation artifacts.
- **OUTPUT_ROOT_PROPOSAL = `refine-logs/`** — the existing FINAL_PROPOSAL.md location.
- **CODEX_REVIEW_MODEL = `gpt-5.5`**, **CODEX_REVIEW_EFFORT = `xhigh`**.
- **CODEX_INNOVATION_MODE** — `COLLABORATIVE` for Phase 3 (Stages 8/9/10); `ADVERSARIAL`
  for the Phase 4 final refinement review.
- **AUTO_PROCEED = true** — chain phases without prompting unless user passes
  `— human checkpoint: true`.
- **STOP_AT_GROUNDING = false** — if `true`, skip Phase 3 and Phase 4 (produce only the
  Grounding artifacts on top of Phase 1 output).

## Load First

- `shared-references/research-agent-pipeline.md` — v1.3 stage definitions for the
  Grounding (Stages 4/5/7) and Innovation (Stages 8/9/10) blocks
- `shared-references/research-harness-prompts.md` — sections `4`, `5`, `7`, `8`, `9`, `10`
  (the canonical prompt body for each stage this skill triggers)
- `shared-references/innovation-loops.md` — Loop A/B/C procedures (sections §2/§3/§4) +
  Codex collaborative-mode prompt template (§7.1)
- `shared-references/reviewer-independence.md`

## Workflow

### Phase 0: Detect Input Type and Initialise

Inspect `$ARGUMENTS`:

- If it is a **path to an existing file** ending in `.md` → **idea-mode**.
- Otherwise → **keyword-mode** (research area, topic phrase).

```bash
mkdir -p orbit-research/ refine-logs/
```

Write a one-line classifier note to `orbit-research/PIPELINE_INTAKE.md`:

```markdown
# Pipeline Intake
- Input: $ARGUMENTS
- Mode: keyword | idea
- Started: <ISO timestamp>
- Stops at: proposal (Validation Spine NOT triggered)
```

### Phase 1: Discovery — produce a baseline proposal + problem selection

#### Phase 1a — keyword-mode

Invoke the existing Workflow 1:

```bash
/idea-discovery "$ARGUMENTS"
```

This produces:
- `idea-stage/IDEA_REPORT.md` (ranked candidates)
- `refine-logs/FINAL_PROPOSAL.md` (top idea, refined via `/research-refine-pipeline`)
- `refine-logs/EXPERIMENT_PLAN.md` (preliminary — will be **regenerated** when the user
  later commits to the Validation Spine; do NOT treat as canonical)
- `refine-logs/EXPERIMENT_TRACKER.md`
- `orbit-research/PROBLEM_SELECTION.md`

When `/idea-discovery` reaches its post-Phase-2 user checkpoint, pass through with the
top-ranked candidate unless the user passed `— human checkpoint: true`.

#### Phase 1b — idea-mode

Read the user's draft `.md` file, then invoke:

```bash
/research-refine "$ARGUMENTS"
```

This produces `refine-logs/FINAL_PROPOSAL.md`. Then derive `orbit-research/PROBLEM_SELECTION.md`
manually by extracting the Problem Anchor from `FINAL_PROPOSAL.md` and writing a brief
selection rationale (importance / audience / feasibility / headroom / paper survivability)
ending with `PROCEED | NARROW | RETHINK`. If `RETHINK`, stop here and surface the issue.

### Phase 2: Grounding — Stages 4 → 5 → 7

For each stage below, use the exact harness prompt from
`shared-references/research-harness-prompts.md`. Read the proposal from Phase 1 as input
context. Codex stays in adversarial mode here (Grounding is calibration, not invention).

#### Phase 2a — Stage 4: Assumption Ledger

Use harness §4. List every assumption the Phase 1 proposal depends on. Tag each as
`factual` (citable) or `working` (must be tested). Cover at minimum: data availability,
mechanism plausibility, baseline behaviour, evaluator validity, scale regime,
infrastructure cost, time horizon.

Write `orbit-research/ASSUMPTION_LEDGER.md`.

**Inline G2 reminder:** any "is/will/always" claim in downstream artifacts must trace
to a row in this ledger or get demoted.

#### Phase 2b — Stage 5: Abstract Task / Mechanism Framing

Use harness §5. Strip the problem to: input space, output space, decision structure,
information bottleneck, primary failure modes, candidate mechanism families (3–5).

Write `orbit-research/ABSTRACT_TASK_MECHANISM.md`.

#### Phase 2c — Stage 7: Baseline Ceiling / Headroom Audit

Use harness §7. If Phase 1 output already mentions baselines, deepen them; otherwise
estimate from scratch. List relevant simple-strong baselines, their estimated ceiling,
benchmark saturation risk, highest-headroom regime.

Write `orbit-research/BASELINE_CEILING.md`.

**Note:** headroom is a *reference*, not a veto. A low ceiling does not block the
pipeline; it calibrates how loud Phase 4's claim wording can be.

**Stop here if `STOP_AT_GROUNDING = true`.** Skip to Phase 5.

### Phase 3: Innovation — Stages 8 → 9 → 10 (Codex COLLABORATIVE)

Switch Codex to **collaborative mode** for all three stages (template in
`shared-references/innovation-loops.md` §7.1). Codex appends candidates / blind spots /
alternative framings; it does NOT veto, prune, or converge.

#### Phase 3a — Stage 8: Mechanism Invention Loop

Use harness §8 + procedure in `innovation-loops.md` §2. Generate 5–10 candidate
mechanisms aimed at the abstract task from Phase 2b. Score each on novelty / feasibility /
falsifiability (1–5 each). Aim for breadth — at least one obvious, one borrowed-from-
another-field, one minimal, one complex/composite, one wild card. Append a "Codex
collaborative additions" section after Codex returns.

Write `orbit-research/MECHANISM_IDEATION.md`. Mark a tentative top-3 for Phase 3b.

#### Phase 3b — Stage 9: Analogy / Cross-pollination Loop

Use harness §9 + procedure in `innovation-loops.md` §3. For each top-3 candidate, name ≥1
analogous solved problem from another field. Map *what transfers / what doesn't / what
new constraint*. Codex collaborative additions append more analogies.

Write `orbit-research/ANALOGY_TRANSFER.md`.

#### Phase 3c — Stage 10: Algorithm Sketch Tournament

Use harness §10 + procedure in `innovation-loops.md` §4. Write 1-page sketches per top
candidate (3–5 sketches). Round-robin pairwise on diagnosability / fidelity /
falsifiability / integration cost. Mark a TENTATIVE_PREFERRED_SKETCH_ID for Phase 4.
Keep alternates with their scores.

Codex on sketch quality is collaborative; on tournament adjudication Codex switches to
adversarial (this is the one place inside innovation loops where Codex challenges Claude's
pairwise picks — see `innovation-loops.md` §4 for the contract).

Write `orbit-research/ALGORITHM_TOURNAMENT.md` ending with the canonical line:

```
TENTATIVE_PREFERRED_SKETCH_ID: S<id>
ALTERNATES: S<id>, S<id>
ABSTAIN_REASONS: <if Codex objected>
NOT_FINAL_NOTE: Stage 10 selects candidates for Stage 11 HMBC review (not run by this
skill). The tentative pick is not a method commitment.
```

### Phase 4: Integrated Final Refinement (Codex ADVERSARIAL)

Codex switches **back to adversarial mode**.

Feed the Phase 3c winner sketch back into `/research-refine`:

```bash
/research-refine "refine-logs/FINAL_PROPOSAL.md + orbit-research/ALGORITHM_TOURNAMENT.md TENTATIVE_PREFERRED_SKETCH_ID + orbit-research/ABSTRACT_TASK_MECHANISM.md + orbit-research/ASSUMPTION_LEDGER.md"
```

Goal: regenerate `refine-logs/FINAL_PROPOSAL.md` so it (a) anchors on the Phase 1 problem,
(b) declares the Phase 3c tentative sketch as the proposed method, (c) cites
ASSUMPTION_LEDGER row IDs for every "is/will" claim, (d) cites the abstract task framing,
(e) acknowledges the alternate sketches kept on the table for later revival.

If Codex flags a serious problem with the winner sketch, the integrated proposal MAY pick
an alternate from `ALGORITHM_TOURNAMENT.md` instead — record this in the proposal's
`## Method Selection Rationale` section.

The output is a **v1.3-aware FINAL_PROPOSAL.md**, not a brand-new file.

### Phase 5: Pipeline Summary

Write `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /idea-to-proposal Pipeline Summary

- Input: $ARGUMENTS
- Mode: keyword | idea
- Completed: <ISO timestamp>
- Validation Spine triggered: NO

## Artifact map (Discovery + Grounding + Innovation)

### Discovery (from /idea-discovery or /research-refine)
- refine-logs/FINAL_PROPOSAL.md           — final proposal (v1.3-integrated)
- idea-stage/IDEA_REPORT.md                — (keyword mode only)
- orbit-research/PROBLEM_SELECTION.md      — problem selection verdict

### Grounding (Phase 2)
- orbit-research/ASSUMPTION_LEDGER.md      — every assumption tagged factual / working
- orbit-research/ABSTRACT_TASK_MECHANISM.md — abstract task + mechanism families
- orbit-research/BASELINE_CEILING.md       — simple-strong baseline reference

### Innovation (Phase 3, Codex collaborative)
- orbit-research/MECHANISM_IDEATION.md     — 5–10 candidate mechanisms
- orbit-research/ANALOGY_TRANSFER.md       — cross-domain analogies
- orbit-research/ALGORITHM_TOURNAMENT.md   — tentative preferred sketch + alternates

## Next steps (NOT run by this skill)

To take the proposal toward implementation:

1. /experiment-plan "refine-logs/FINAL_PROPOSAL.md"
   → produces CONTROL_DESIGN.md, NULL_RESULT_CONTRACT.md,
     COMPONENT_BUNDLE_LADDER.md, ALGORITHMIC_FORMALIZATION.md,
     DIAGNOSTIC_EXPERIMENT_PLAN.md (Stages 11–16, Validation Spine prerequisites)

2. /experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
   → implements code + writes PLAN_CODE_AUDIT.md (Stage 15 loop)

3. /run-experiment "[diagnostic command]"
   → Stage 17 — first time GPU is touched in the v1.3 pipeline

4. /research-pipeline can also continue from here; pass the existing artifact paths
   so it skips re-doing Discovery/Grounding/Innovation.
```

## ARIS / Sub-skill Unavailability

For each delegated invocation (`/idea-discovery`, `/research-refine`, `/research-refine-pipeline`),
follow the standard fallback pattern:

```text
Try slash invocation.
If skill not registered:
  Print "ORBIT skill <name> unavailable. Phase <N> degraded: <fallback or HUMAN_DECISION_REQUIRED>."
  Continue gracefully.
If the missing skill was load-bearing for a v1.3 artifact (e.g. /research-refine for
FINAL_PROPOSAL.md):
  Escalate — do not silently produce an incomplete proposal.
```

For Codex MCP unavailability during Phase 3 (Innovation):
- The collaborative-mode addition is **enrichment**, not load-bearing. Mark each affected
  artifact with `## Codex collaborative additions: NOT_AVAILABLE (codex_mcp_unreachable)`
  and continue. Do not block the pipeline.
- For Phase 3c tournament adjudication (where Codex is adversarial), if Codex is down,
  proceed with Claude's pairwise picks but mark `ABSTAIN_REASONS: codex_mcp_unreachable —
  tournament adjudication is single-model only this round`.

For Codex MCP unavailability during Phase 4 (final refinement adversarial review):
- Skip Codex review, mark proposal `## Phase 4 review: SKIPPED (codex_mcp_unreachable)`,
  and continue. The integrated FINAL_PROPOSAL.md still gets written.

## What This Skill Deliberately Does NOT Do

- Does **not** invoke `/experiment-plan`, `/experiment-bridge`, `/run-experiment`,
  `/experiment-queue`, `/result-to-claim`, `/auto-review-loop`, `/paper-writing`, or any
  Validation Spine skill.
- Does **not** write `CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`,
  `COMPONENT_BUNDLE_LADDER.md`, `ALGORITHMIC_FORMALIZATION.md`, `PLAN_CODE_AUDIT.md`, or
  any DIAGNOSTIC_RUN_*.md.
- Does **not** touch GPUs.
- Does **not** finalise method commitment — Stage 10's pick is explicitly tentative
  (`TENTATIVE_PREFERRED_SKETCH_ID`); convergence happens at Stage 11 HMBC, run by
  `/research-pipeline` or `/experiment-plan`.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Final Rule

```text
Discover then ground then invent then write a proposal — no implementation, no GPU.
Innovation produces candidates; this skill stops before commitment picks one for real.
The proposal carries the tentative sketch ID forward; downstream skills can switch.
```
