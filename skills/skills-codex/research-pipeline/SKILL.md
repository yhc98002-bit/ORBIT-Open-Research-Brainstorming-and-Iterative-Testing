---
name: "research-pipeline"
description: "Codex-native Claude × Codex co-evolution research pipeline with mandatory cross-agent checks at critical stages: Stage 0 framing → Stage 1 proposal/plan consistency → Stage 2 implementation review → Stage 3 execution tracking → Stage 4 result audit → Stage 5 refinement → Stage 6 paper claim checks (optional) → Stage 7 convergence debate. Use for 全流程/full pipeline/end-to-end research with correctness gates."
---

# Full Research Pipeline: Convergence-First Chain

End-to-end research workflow for: **$ARGUMENTS**

This version keeps ARIS's original reusable skills but reorders the chain around explicit verification gates to prevent silent mismatch.

## Constants

- **CLAUDE_EFFORT = max** — Default planning/writing depth for this convergence pipeline.
- **CODEX_REVIEW_EFFORT = xhigh** — Mandatory reasoning depth for cross-agent verification stages.
- **AUTO_PROCEED = true** — If `false`, wait for user confirmation at Gate 0.
- **ARXIV_DOWNLOAD = false** — Passed through to discovery-related literature steps.
- **HUMAN_CHECKPOINT = false** — If `true`, pause at major stage boundaries.
- **REVIEWER_DIFFICULTY = medium** — Passed to review loops.
- **AUTO_WRITE = false** — If `true`, run writing stages automatically.
- **VENUE = ICLR** — Used when `AUTO_WRITE=true`.

## Stage Map

```text
Stage 0  Problem Discovery & Framing
Stage 1  Proposal & Experiment Design (mandatory consistency check)
Stage 2  Implementation (mandatory code/spec check)
Stage 3  Execution & Tracking
Stage 4  Result Analysis + Integrity Audit (mandatory)
Stage 5  Hypothesis Refinement / Pivot
Stage 6  Paper Framing & Writing (optional, claim check mandatory if enabled)
Stage 7  Multi-Agent Debate & Convergence
```

## Pipeline

### Stage 0 — Problem Discovery & Framing

```bash
/idea-discovery "$ARGUMENTS"
```

Produce:
- `PROBLEM.md`
- `HYPOTHESIS.md`

Gate 0 behavior:
- `AUTO_PROCEED=false` → wait for explicit user selection.
- `AUTO_PROCEED=true` → present options, then auto-select top candidate if user is silent.

### Stage 1 — Proposal & Experiment Design (mandatory Codex double-check)

Create:
- `FINAL_PROPOSAL.md`
- `EXPERIMENT_PLAN.md`

Then run:

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

Do not continue with unresolved high-severity mismatches.

### Stage 2 — Implementation (mandatory review gate)

Implement via existing bridge (`/experiment-bridge`) or direct coding from plan.

Then run:

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

### Stage 3 — Execution & Tracking

Use:
- `/run-experiment` (small job sets)
- `/experiment-queue` (large sweeps)
- `/monitor-experiment` (tracking)

Maintain:
- `LOGS/`
- `EXPERIMENT_TRACKER.md`

### Stage 4 — Result Analysis (mandatory integrity audit)

Write:
- `EXPERIMENT_RESULTS.md`
- `FAILURE_ANALYSIS.md`

Audit with:

```text
Given results + evaluation code:
Check:
1. Any metric computation errors?
2. Any data leakage?
3. Any unfair comparison?
4. Any inconsistent experiment setting?
Return critical issues.
```

Record findings in `REVIEW/` artifacts. Critical issues force loop-back to Stage 1/2.

### Stage 5 — Hypothesis Refinement / Pivot

Write:
- `NEXT_PROPOSAL.md`

Optionally invoke `/research-refine` for re-anchoring.

### Stage 6 — Paper Framing & Writing (optional)

Manual handoff when `AUTO_WRITE=false`:

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR
```

Auto path when enabled:

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: $VENUE
```

Run claim check before final draft:

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

### Stage 7 — Multi-Agent Debate & Convergence

Run final adversarial convergence pass:
- interpretation/significance side
- correctness/evidence side

Write:
- `REVIEW/FINAL_CONSENSUS.md`

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

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Guardrails

- Do not skip Stage 1/2/4 mandatory checks.
- Do not self-certify integrity-critical artifacts with a single model family.
- Convergence over volume: correctness before generation speed.
