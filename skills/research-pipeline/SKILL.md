---
name: research-pipeline
description: "Claude × Codex co-evolution research pipeline with mandatory cross-agent checks at each critical stage. Small-refactor chain: Stage 0 problem framing → Stage 1 proposal/experiment consistency → Stage 2 implementation review → Stage 3 execution tracking → Stage 4 result audit → Stage 5 hypothesis refinement → Stage 6 paper writing (optional) → Stage 7 debate convergence. Use when user says 全流程/full pipeline/end-to-end research/从问题到论文 with correctness gates."
argument-hint: [research-direction]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Research Pipeline (Claude × Codex Co-Evolution)

End-to-end research workflow for: **$ARGUMENTS**

> Design target: keep ARIS's existing strengths, but re-order the chain around **convergence gates** to prevent silent failure (plan ≠ code ≠ paper).

## Constants

- **CLAUDE_EFFORT = max** — Default planning/writing depth for this convergence pipeline.
- **CODEX_REVIEW_EFFORT = xhigh** — Mandatory reasoning depth for cross-agent verification stages.
- **AUTO_PROCEED = true** — When `true`, Gate 0 auto-selects the top-ranked problem after presenting options. When `false`, wait for explicit user confirmation.
- **ARXIV_DOWNLOAD = false** — Passed through to literature discovery stage (`/research-lit`).
- **HUMAN_CHECKPOINT = false** — When `true`, pause at every major gate (Stage 1/2/4/6) for user review.
- **REVIEWER_DIFFICULTY = medium** — Passed to review skills (`medium | hard | nightmare`).
- **AUTO_WRITE = false** — If `true`, run paper stage automatically after Stage 5.
- **VENUE = ICLR** — Used only when `AUTO_WRITE=true`.

## Stage Map (small-refactor chain)

```text
Stage 0  Problem Discovery & Framing      (W1)
Stage 1  Proposal & Experiment Design      (W1 + consistency gate)
Stage 2  Implementation                    (W1.5 + code review gate)
Stage 3  Execution & Tracking              (W1.5/W2 runtime)
Stage 4  Result Analysis & Integrity Audit (W2 + audit gate)
Stage 5  Hypothesis Refinement / Pivot     (W2 loopback)
Stage 6  Paper Framing & Writing (optional)(W3 + claim gate)
Stage 7  Multi-Agent Debate & Convergence  (final consensus)
```

This keeps the original ARIS skill ecosystem (`idea-discovery`, `experiment-bridge`, `run-experiment`, `auto-review-loop`, `paper-writing`) while adding explicit cross-agent verification outputs.

## Pipeline

### Stage 0 — Problem Discovery & Framing (ARIS-style)

Invoke:

```bash
/idea-discovery "$ARGUMENTS"
```

Use existing W1 discovery chain (`/research-lit → /idea-creator → /novelty-check → /research-review`) and distill:

- `PROBLEM.md` (problem anchor, failure signals, domain motivation)
- `HYPOTHESIS.md` (hypothesis space + assumptions)

**Gate 0 (AUTO_PROCEED):**
- If `AUTO_PROCEED=false`: wait for user choice.
- If `AUTO_PROCEED=true`: present top choices, then auto-pick top candidate if no user response.

---

### Stage 1 — Proposal & Experiment Design (mandatory Codex double-check)

Create:

- `FINAL_PROPOSAL.md`
- `EXPERIMENT_PLAN.md`

Then run consistency check (mandatory):

```text
Compare FINAL_PROPOSAL.md with EXPERIMENT_PLAN.md.
Check:
1. Are all proposed methods implemented?
2. Are variables clearly defined?
3. Any mismatch between description and execution?
4. Any logic bugs in experiment flow?
Return structured inconsistencies.
```

Write:

- `REVIEW/CONSISTENCY_REPORT.md`

Do not enter Stage 2 before high-severity inconsistencies are resolved.

---

### Stage 2 — Implementation (mandatory review gate)

Primary implementation can use the existing bridge path:

```bash
/experiment-bridge
```

or direct implementation from `EXPERIMENT_PLAN.md` when appropriate.

Mandatory implementation review:

```text
Given:
- EXPERIMENT_PLAN.md
- CODE
Check:
1. Does code implement the plan exactly?
2. Any deviation from described method?
3. Any silent logic bugs?
Return:
- mismatch list
- critical bug list
```

Write:

- `REVIEW/CODE_REVIEW.md`

Only proceed after critical bugs are addressed.

---

### Stage 3 — Execution & Tracking

Run experiments via:

- `/run-experiment` for small batches
- `/experiment-queue` for large sweeps / dependency chains
- `/monitor-experiment` for tracking

Maintain:

- `LOGS/`
- `EXPERIMENT_TRACKER.md`

Tracker must include config hash, dataset split signature, seed set, and run status.

---

### Stage 4 — Result Analysis (mandatory integrity audit)

Aggregate results and write:

- `EXPERIMENT_RESULTS.md`
- `FAILURE_ANALYSIS.md`

Then run integrity audit (mandatory):

```text
Given results + evaluation code:
Check:
1. Any metric computation errors?
2. Any data leakage?
3. Any unfair comparison?
4. Any inconsistent experiment setting?
Return critical issues.
```

Append findings to:

- `REVIEW/CODE_REVIEW.md` (evaluation section) and/or
- `REVIEW/CONSISTENCY_REPORT.md` (stage mismatch section)

If critical audit issues exist, loop back to Stage 1 or Stage 2.

---

### Stage 5 — Hypothesis Refinement / Pivot

Based on Stage 4 failures:

- update hypotheses
- propose next-wave plan

Write:

- `NEXT_PROPOSAL.md`

Use `/research-refine` when the pivot needs problem re-anchoring.

---

### Stage 6 — Paper Framing & Writing (optional, but claim gate is mandatory when enabled)

If `AUTO_WRITE=false`, stop with handoff:

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR
```

If enabled:

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: $VENUE
```

Before finalizing draft, run claim check:

```text
Given:
- PAPER_DRAFT
- EXPERIMENT_RESULTS
Check:
1. Are all claims supported?
2. Any missing experiment?
3. Any inconsistency between text and results?
Return issues.
```

Write:

- `PAPER_DRAFT.md`
- `REVIEW/CLAIM_CHECK.md`

---

### Stage 7 — Multi-Agent Debate & Convergence

Run final adversarial reconciliation:

- Agent A: interpretation/significance
- Agent B: correctness/evidence sufficiency

Goal: consensus, not unilateral generation.

Write:

- `REVIEW/FINAL_CONSENSUS.md`

Pipeline ends only when key claim disputes are either resolved or explicitly deferred with rationale.

## Suggested Artifact Layout

```text
project/
├── PROBLEM.md
├── HYPOTHESIS.md
├── FINAL_PROPOSAL.md
├── EXPERIMENT_PLAN.md
├── CODE/
├── LOGS/
├── EXPERIMENT_TRACKER.md
├── EXPERIMENT_RESULTS.md
├── FAILURE_ANALYSIS.md
├── NEXT_PROPOSAL.md
├── PAPER_DRAFT.md
└── REVIEW/
    ├── CODE_REVIEW.md
    ├── CONSISTENCY_REPORT.md
    ├── CLAIM_CHECK.md
    └── FINAL_CONSENSUS.md
```

## Closed-Loop Engine

`Problem → Proposal → Code → Run → Analyze → Refine → Paper → Debate → Loop`

Key principle: **Convergence > Generation**.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Guardrails

- Never skip Stage 1/2/4 mandatory checks.
- Never let the same model family self-certify integrity-critical artifacts.
- Fail loudly on unresolved critical mismatches.
- Preserve existing ARIS skills and strengths; this pipeline is a chain refactor, not a rewrite.
