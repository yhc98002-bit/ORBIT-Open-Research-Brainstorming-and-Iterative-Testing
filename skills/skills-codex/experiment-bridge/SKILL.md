---
name: experiment-bridge
description: "ORBIT v1.4 STOP B wrapper. Turns an approved proposal into decision-driven experiment-plan artifacts, implements the planned code, runs semantic plan-code audit, and may run limited implementation-facing probes. Accepts FINAL_PROPOSAL.md, FINAL_PROPOSAL_SHORT.md, METHOD_SPEC.md, or existing legacy EXPERIMENT_PLAN.md. Does not create paper claims or run auto-review-loop; formal diagnostics and claim/review routing belong to /diagnostic-to-review."
argument-hint: [approved-proposal-or-experiment-plan-path]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /experiment-bridge — v1.4 Proposal → Plan → Code → Audit → Probe

Bridge an approved proposal into implementation readiness for: **$ARGUMENTS**

## Overview

This is a wrapper skill, not a code-only atomic step. It owns STOP B:

1. read the approved proposal and ORBIT grounding/innovation artifacts;
2. call or perform `/experiment-plan` to write decision-driven experiment artifacts;
3. implement the planned code;
4. run semantic plan-code audit and write `PLAN_CODE_AUDIT.md`;
5. run limited implementation-facing probes when mode allows;
6. hand formal diagnostics to `/diagnostic-to-review`.

Version note: `v1.4` names this STOP B wrapper behavior. The underlying artifact names,
stage numbers, and hard gates remain the ORBIT v1.3 contract in
`../shared-references/research-agent-pipeline.md`.

Load `../shared-references/research-posture.md`. Preserve the proposal's `paper_mode`
(default `normal`) and design the smallest experiment package that can support the chosen
contribution type. Normal-paper evidence does not need to prove a breakthrough, but it
must isolate the claim actually being made.

Canonical flow:

```text
/idea-to-proposal "..."                         -> STOP A proposal review
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
  -> /experiment-plan
  -> implementation
  -> PLAN_CODE_AUDIT.md
  -> limited probe when mode allows
  -> STOP B plan/code/probe review
/diagnostic-to-review "<diagnostic command>"    -> STOP C results + claim/review when paper-bearing
```

## Modes

- **`plan-only`**: approved proposal -> experiment plan artifacts only.
- **`audit-only`**: experiment plan -> implementation -> `PLAN_CODE_AUDIT.md`, no GPU/probe.
- **`probe`**: default. Plan -> implementation -> audit -> limited sanity/probe.
- **`full-bridge`**: explicit opt-in. After plan/audit/probe, call
  `/diagnostic-to-review` for formal diagnostic execution. This mode must not call
  `/auto-review-loop` directly.

Parse mode from `— mode: <plan-only|audit-only|probe|full-bridge>`. Default: `probe`.

## Inputs

Canonical inputs after STOP A:

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/FINAL_PROPOSAL_SHORT.md`
- `refine-logs/METHOD_SPEC.md`
- `orbit-research/PROBLEM_SELECTION.md`
- `orbit-research/ASSUMPTION_LEDGER.md`
- `orbit-research/ABSTRACT_TASK_MECHANISM.md`
- `orbit-research/BASELINE_CEILING.md`
- `orbit-research/MECHANISM_IDEATION.md`
- `orbit-research/ANALOGY_TRANSFER.md`
- `orbit-research/ALGORITHM_TOURNAMENT.md`

Compatibility inputs:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- `refine-logs/EXPERIMENT_TRACKER.md`
- `orbit-research/RESEARCH_DECISION_LOG.md` for failed/surprising diagnostic recovery

Pre-patch `/idea-to-proposal` generated experiment plans. In the new flow, experiment
planning moves here after STOP A. Existing `EXPERIMENT_PLAN.md` files remain readable:
reuse them if they are current, refresh them if stale or inconsistent with the approved
proposal, and warn if they look like legacy pre-STOP-A plans.

## Required Outputs

Planning outputs:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- `refine-logs/EXPERIMENT_TRACKER.md`
- `orbit-research/CONTROL_DESIGN.md`
- `orbit-research/NULL_RESULT_CONTRACT.md`
- `orbit-research/COMPONENT_BUNDLE_LADDER.md`
- `orbit-research/ALGORITHMIC_FORMALIZATION.md`
- `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`

Implementation/audit outputs:

- code/config/scripts needed by the plan
- `orbit-research/PLAN_CODE_AUDIT.md` with verdict:
  `MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`

Probe outputs when `/run-experiment` is used:

- `orbit-research/RUN_LEDGER.jsonl`
- `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`
- concise probe notes in `refine-logs/EXPERIMENT_TRACKER.md` or
  `orbit-research/PIPELINE_SUMMARY.md`

## Phase 0: Load Context And Decide Resume Point

Create `orbit-research/` and `refine-logs/` if needed.

Read `$ARGUMENTS` first. If it points to `FINAL_PROPOSAL.md`,
`FINAL_PROPOSAL_SHORT.md`, or `METHOD_SPEC.md`, treat it as the approved proposal and
start with planning. If it points to `EXPERIMENT_PLAN.md` or `EXPERIMENT_PLAN_EXEC.md`,
verify whether a plan already exists and resume from implementation.

Read `orbit-research/IDEA_TO_PROPOSAL_STATE.json` when present. If it has
`status = "awaiting_human_continue"`, treat this invocation as the human's STOP A
approval signal.

Read `RESEARCH_DECISION_LOG.md` when present. If it says the failure type is
`implementation/config issue`, patch only the local implementation/config surface it
names. If it names another failure type, do not broaden the implementation task; route to
the indicated skill.

## Phase 1: Experiment Planning From The Approved Proposal

If `EXPERIMENT_PLAN.md` and `EXPERIMENT_PLAN_EXEC.md` are missing, stale, or legacy,
invoke or perform `/experiment-plan` grounded in:

```bash
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

The plan must be decision-driven:

- candidate claims / evidence targets, not frozen paper claims
- every committed experiment must change a research decision
- paper-claim defense applies only to paper-bearing experiments
- do not force breakthrough-level evidence when `paper_mode = normal`
- allow normal-paper contribution types: empirical finding, method combination,
  benchmark + baseline, reproduction-plus, system, or focused mechanism
- controls must isolate the claim actually being made; null results must be interpretable
- `EXPERIMENT_PLAN.md` stays a short index
- `EXPERIMENT_PLAN_EXEC.md` contains the executable run order and
  `Decision Tree / Branch Table`

Planning must write or update:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- `refine-logs/EXPERIMENT_TRACKER.md`
- `orbit-research/CONTROL_DESIGN.md`
- `orbit-research/NULL_RESULT_CONTRACT.md`
- `orbit-research/COMPONENT_BUNDLE_LADDER.md`
- `orbit-research/ALGORITHMIC_FORMALIZATION.md`
- `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`

After `EXPERIMENT_PLAN_EXEC.md` exists and includes the decision tree, update only the
proposal status block in `FINAL_PROPOSAL.md` / `FINAL_PROPOSAL_SHORT.md` to
`EXPERIMENT_PLAN_READY` with evidence basis pointing to the plan artifacts. This means
"ready for plan-code bridge", not validated.

If mode is `plan-only`, stop here with STOP B planning summary and next action:
`/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md" — mode: audit-only` or `— mode: probe`.

## Phase 2: Implement The Planned Code

Read `EXPERIMENT_PLAN.md` as an index. Follow its `Files` table and reading paths before
extracting implementation details:

- `EXPERIMENT_PLAN_EXEC.md` for claim/evidence targets, experiment blocks, run order,
  decision gates, budget, and risks
- current `[MILESTONE]_RUN_CARD.md` if marked as "NOW" or current immediate task
- `METHOD_SPEC.md` for implementation-level method details
- `FINAL_PROPOSAL_SHORT.md` for compact context
- ORBIT planning artifacts listed above for controls, null-result interpretation,
  formalization, and diagnostic design

Implement only what the plan requires:

- training/evaluation scripts with configurable arguments
- dataset loaders and preprocessing
- baseline/control variants named in the plan
- fixed and controllable seeds
- parseable JSON/CSV result output
- logging paths and W&B integration when configured
- config files or launch scripts needed by the diagnostic command

Do not add unregistered experiments because they are interesting. Add them to the plan
first or leave a note for a future plan patch.

## Phase 3: Semantic Plan-Code Audit

Before any probe or formal diagnostic, run the semantic audit from
`../shared-references/semantic-code-audit.md`. The audit checks whether code implements the
intended algorithm, baselines, controls, ablations, datasets, splits, metrics, regimes,
seeds, config defaults, and result files.

Always write `orbit-research/PLAN_CODE_AUDIT.md` with a verdict line:

```text
MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR
```

Rules:

- `MATCHES_PLAN` -> proceed to probe if mode allows.
- `PARTIAL_MISMATCH` -> proceed only if the mismatch is scoped and irrelevant to the
  immediate probe/formal diagnostic.
- `CRITICAL_MISMATCH` -> fix and re-audit; do not run probes or diagnostics.
- `ERROR` -> no formal diagnostic. A tiny implementation probe may proceed only if the
  user requested probe mode and the error is audit-tool availability, not known code/plan
  mismatch.

If mode is `audit-only`, stop after writing `PLAN_CODE_AUDIT.md`.

## Phase 4: Limited Implementation-Facing Probe

Probe runs are allowed by default in `probe` mode, but they are not paper evidence. They
exist to validate implementation feasibility:

- environment check
- dataloader / metric parser sanity
- one-batch or tiny overfit
- logging / W&B / result path validation
- diagnostic command smoke test
- minimal local mechanism probe whose purpose is implementation readiness

Probe runs may call `/run-experiment`. When they do, they must be ledgered through the
standard run provenance path:

- append start/final entries to `orbit-research/RUN_LEDGER.jsonl`
- write `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- write `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`

Probe results must not directly create paper claims:

- do not write `CLAIM_CONSTRUCTION.md`
- do not run `/auto-review-loop`
- do not perform formal scientific result interpretation beyond implementation/probe
  status

If a probe unexpectedly affects paper-level claim scope, stop and hand off to:

```bash
/diagnostic-to-review "<diagnostic command OR manifest>"
```

## Phase 5: Handoff

Write or update `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /experiment-bridge Summary

- Input: $ARGUMENTS
- Mode: plan-only | audit-only | probe | full-bridge
- Proposal: refine-logs/FINAL_PROPOSAL.md
- Plan: refine-logs/EXPERIMENT_PLAN.md
- Exec plan: refine-logs/EXPERIMENT_PLAN_EXEC.md
- Audit: orbit-research/PLAN_CODE_AUDIT.md
- Probe reports: [paths or NONE]

## STOP B

Review:
- refine-logs/EXPERIMENT_PLAN.md
- refine-logs/EXPERIMENT_PLAN_EXEC.md
- orbit-research/PLAN_CODE_AUDIT.md
- probe reports, if any

Human question:
Is this code/plan/probe status good enough for formal diagnostics?

## Next

/diagnostic-to-review "<diagnostic command OR manifest>"
```

If mode is `full-bridge`, call `/diagnostic-to-review` after writing the STOP B summary.
Do not call `/auto-review-loop` directly; `/diagnostic-to-review` owns conditional-required
claim/review routing.

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — apply selective milestone timestamping rules
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- Keep `/experiment-bridge` as the STOP B wrapper: planning, implementation, audit, probe,
  and handoff.
- Experiment planning belongs here after STOP A; it must not pollute `FINAL_PROPOSAL.md`.
- Every committed experiment must change a research decision. Paper-claim defense applies
  only to paper-bearing experiments.
- Never compare predictions against another model's output as ground truth; use dataset
  labels/targets or official eval scripts.
- Do not create paper claims, claim construction, red-team reviews, or paper-writing
  artifacts in this skill.
- Formal diagnostic execution, scientific interpretation, decision logging after results,
  and paper-level claim/review belong to `/diagnostic-to-review`.

## Composing With Other Skills

```text
/idea-to-proposal      -> proposal candidate + STOP A
/experiment-bridge     -> experiment plan + implementation + PLAN_CODE_AUDIT + STOP B
/diagnostic-to-review  -> formal diagnostic + interpretation + decision log + conditional-required claim/review
/paper-writing         -> manuscript after CLAIM_CONSTRUCTION exists
```
