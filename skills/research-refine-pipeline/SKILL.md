---
name: research-refine-pipeline
description: 'Run an end-to-end workflow that chains `research-refine` and `experiment-plan`. Use when the user wants a one-shot pipeline from vague research direction to focused final proposal plus detailed experiment roadmap, or asks to "串起来", build a pipeline, do it end-to-end, or generate both the method and experiment plan together.'
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, mcp__codex__codex, mcp__codex__codex-reply
---

# Research Refine Pipeline: End-to-End Method and Experiment Planning

Refine and concretize: **$ARGUMENTS**

## Overview

Use this skill when the user does not want to stop at a refined method. The goal is to produce a coherent package that includes:

- a problem-anchored, elegant final proposal
- the review history explaining why the method is focused
- a detailed experiment roadmap tied to candidate claims, evidence targets, and research decisions
- a compact pipeline summary that says what to run next

This skill composes two existing workflows:

1. `research-refine` for method refinement
2. `experiment-plan` for decision-driven validation planning

For stage-specific detail, read these sibling skills only when needed:

- `../research-refine/SKILL.md`
- `../experiment-plan/SKILL.md`
- `../shared-references/document-hygiene.md`

## Core Rule

Do not plan a large experiment suite on top of an unstable method. First stabilize the thesis. Then turn the stable thesis into experiments.

## Supported Flags

- `— difficulty: <medium|hard|nightmare>` — forwarded to `/research-refine`.
- `— review-difficulty: <medium|hard|nightmare>` — alias for `— difficulty`.

Difficulty affects adversarial review/refinement only. Do not apply `hard` or `nightmare`
settings to discovery, ideation, or innovation loops.

## Default Outputs

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/REVIEW_SUMMARY.md`
- `refine-logs/REFINEMENT_REPORT.md`
- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_TRACKER.md`
- `orbit-research/PIPELINE_SUMMARY.md`
- `refine-logs/PIPELINE_SUMMARY.md` only as a legacy/local wrapper summary when needed

## Workflow

### Phase 0: Triage the Starting Point

- Extract the problem, rough approach, constraints, resources, and target venue.
- Check whether `refine-logs/FINAL_PROPOSAL.md` already exists and still matches the current request.
- If the proposal is missing, stale, or materially different from the current request, run the full `research-refine` stage.
- If the proposal is already strong and aligned, reuse it and jump to experiment planning.
- If in doubt, prefer re-running `research-refine` rather than planning experiments for the wrong method.

### Phase 1: Method Refinement Stage

Run the `research-refine` workflow and keep its ORBIT philosophy intact. Forward
`— difficulty` / `— review-difficulty` to `/research-refine`:

```bash
/research-refine "$ARGUMENTS" — difficulty: <parsed difficulty or review-difficulty>
```

- preserve the Problem Anchor
- prefer the smallest adequate mechanism
- keep one dominant contribution
- modernize only when it improves the paper
- keep `FINAL_PROPOSAL` readable per `document-hygiene.md`

Exit this stage only when these are explicit:

- the final method thesis
- the dominant contribution
- the complexity intentionally rejected
- the candidate claims / evidence targets and must-run decision-changing experiments
- `Proposal Status` and `Critical Hypotheses` in the proposal artifacts
- the remaining risks, if any

If the verdict is still `REVISE`, continue into experiment planning only if the remaining weaknesses are clearly documented.

### Phase 2: Planning Gate

Before the experiment stage, write a short gate check:

- What is the final method thesis?
- What is the dominant contribution?
- What complexity was intentionally rejected?
- Which reviewer concerns still matter for validation?
- Is a frontier primitive central, optional, or absent?

If these answers are not crisp, tighten the final proposal first.

### Phase 3: Experiment Planning Stage

Run the `experiment-plan` workflow grounded in:

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/REVIEW_SUMMARY.md`
- `refine-logs/REFINEMENT_REPORT.md`

Ensure the experiment plan covers:

- candidate claims / evidence targets
- the main anchor result
- novelty isolation
- a simplicity or deletion check
- a frontier necessity check if applicable
- run order, budget, and decision gates
- `Decision Tree / Branch Table` in `EXPERIMENT_PLAN_EXEC.md`
- paper-claim defense only for paper-bearing experiments

### Phase 4: Integration Summary

Write `orbit-research/PIPELINE_SUMMARY.md` as the ORBIT global summary. If you also write
`refine-logs/PIPELINE_SUMMARY.md`, mark it explicitly as a legacy/local wrapper summary
that points to `orbit-research/PIPELINE_SUMMARY.md`.

```markdown
# Pipeline Summary

**Problem**: [problem]
**Final Method Thesis**: [one sentence]
**Final Verdict**: [READY / REVISE / RETHINK]
**Date**: [today]

## Final Deliverables
- Proposal: `refine-logs/FINAL_PROPOSAL.md`
- Proposal status: [PROPOSAL_READY / EXPERIMENT_PLAN_READY / SCALE_READY / SUPPORTED / REFRAMED / ARCHIVED]
- Critical hypotheses: `refine-logs/FINAL_PROPOSAL_SHORT.md` / `orbit-research/ASSUMPTION_LEDGER.md`
- Review summary: `refine-logs/REVIEW_SUMMARY.md`
- Experiment plan: `refine-logs/EXPERIMENT_PLAN.md`
- Executable decision tree: `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- Experiment tracker: `refine-logs/EXPERIMENT_TRACKER.md`

## Contribution Snapshot
- Dominant contribution:
- Optional supporting contribution:
- Explicitly rejected complexity:

## Candidate Claims / Evidence Targets
- [Candidate claim or evidence target 1]
- [Candidate claim or evidence target 2]

## First Runs to Launch
1. [Run]
2. [Run]
3. [Run]

## Main Risks
- [Risk]:
- [Mitigation]:

## Next Action
- Proceed to `/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"` for implementation and plan-code audit
```

### Phase 5: Present a Brief Summary to the User

```
Pipeline complete.

Method output:
- refine-logs/FINAL_PROPOSAL.md

Experiment output:
- refine-logs/EXPERIMENT_PLAN.md
- refine-logs/EXPERIMENT_TRACKER.md

Pipeline summary:
- orbit-research/PIPELINE_SUMMARY.md

Best next step:
- /experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
```

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — apply selective milestone timestamping rules
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Large file handling**: If the Write tool fails due to file size, immediately retry using Bash (`cat << 'EOF' > file`) to write in chunks. Do NOT ask the user for permission — just do it silently.

- Follow `document-hygiene.md`: proposals must not read like disclaimers, rebuttals, or
  audit logs. Preserve uncertainty in the correct artifact layer.
- Do not let the experiment plan override the Problem Anchor.
- Do not widen the paper story after method refinement unless a missing validation block is truly necessary.
- Keep candidate claims / evidence targets consistent across `FINAL_PROPOSAL.md`,
  `EXPERIMENT_PLAN.md`, and `orbit-research/PIPELINE_SUMMARY.md`.
- Keep the main paper story compact.
- If the method is intentionally simple, test that simplicity in the experiment plan rather than adding new components.
- If the method uses a modern LLM / VLM / Diffusion / RL primitive, make its necessity test explicit.
- If the method does not need a frontier primitive, say that clearly and avoid forcing one.
- Prefer the staged skills when the user only needs one stage; use this skill for the integrated flow.

## Composing with Other Skills

```
/research-refine-pipeline -> one-shot method + experiment planning
/research-refine   -> method refinement only
/experiment-plan   -> experiment planning only
/experiment-bridge -> implementation + plan-code audit before execution
```
