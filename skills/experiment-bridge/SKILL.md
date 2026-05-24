---
name: experiment-bridge
description: "ORBIT v1.4 STOP B wrapper. Turns an approved proposal pack or legacy proposal into experiment/experiment_pack.json, implements the planned code, runs semantic plan-code audit, and may run limited implementation/headroom probes with distinct PROBE artifacts. Accepts proposal/proposal_pack.json, FINAL_PROPOSAL.md, FINAL_PROPOSAL_SHORT.md, METHOD_SPEC.md, or existing legacy EXPERIMENT_PLAN.md. Does not create paper claims or run auto-review-loop; formal diagnostics and claim/review routing belong to /diagnostic-to-review."
argument-hint: [approved-proposal-or-experiment-plan-path]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /experiment-bridge — v1.4 Proposal → Plan → Code → Audit → Probe

Bridge an approved proposal into implementation readiness for: **$ARGUMENTS**

## Overview

This is a wrapper skill, not a code-only atomic step. It owns STOP B:

1. read the approved proposal and ORBIT grounding/innovation artifacts;
2. call or perform `/experiment-plan` to write `experiment/experiment_pack.json` plus
   generated plan views;
3. implement the planned code;
4. run semantic plan-code audit and write `PLAN_CODE_AUDIT.md`;
5. run limited implementation/headroom probes when mode allows, using probe-specific
   artifacts only;
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
/experiment-bridge "proposal/proposal_pack.json"
  -> /experiment-plan
  -> experiment/experiment_pack.json
  -> implementation
  -> PLAN_CODE_AUDIT.md
  -> experiment/PROBE_REPORT.md + experiment/PROBE_AUDIT.md when mode allows
  -> STOP B plan/code/probe review
/diagnostic-to-review "<diagnostic command>"    -> STOP C results + claim/review when paper-bearing
```

## Modes

- **`plan-only`**: approved proposal -> experiment plan artifacts only.
- **`audit-only`**: experiment plan -> implementation -> `PLAN_CODE_AUDIT.md`, no GPU/probe.
- **`probe`**: default. Plan -> implementation -> audit -> limited sanity/probe.
- **`full-bridge`**: explicit opt-in only. After plan/audit/probe, call
  `/diagnostic-to-review` for formal diagnostic execution only when the user passes
  `— confirm-stop-b-reviewed: true`. This mode must not call `/auto-review-loop`
  directly.

Parse mode from `— mode: <plan-only|audit-only|probe|full-bridge>`. Default: `probe`.
If `— mode: full-bridge` is present without `— confirm-stop-b-reviewed: true`, treat it
as normal STOP B handoff: write the pack/views/probe outputs, stop, and set the safe next
command to `/diagnostic-to-review "experiment/experiment_pack.json"`.

## Inputs

Canonical inputs after STOP A:

- `proposal/proposal_pack.json`

Backward-compatible proposal inputs:

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

Canonical STOP B outputs:

- `experiment/experiment_pack.json`
- `experiment/EXPERIMENT_PLAN.md` — generated human-readable plan view
- `experiment/EXPERIMENT_PLAN_EXEC.md` — generated execution view when useful

Compatibility planning views may still be written:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- `refine-logs/EXPERIMENT_TRACKER.md`

Structured planning sections stored in `experiment_pack` and optionally rendered to
compatibility views:

- `orbit-research/CONTROL_DESIGN.md`
- `orbit-research/NULL_RESULT_CONTRACT.md`
- `orbit-research/COMPONENT_BUNDLE_LADDER.md`
- `orbit-research/ALGORITHMIC_FORMALIZATION.md`
- `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`
- `experiment_pack.formal_diagnostics[]` entries with `id`, `kind`,
  `claim_relevance`, a `command` or manifest path, `expected_result_paths[]`,
  `success_signal`, and `null_result_interpretation`.

Implementation/audit outputs:

- code/config/scripts needed by the plan
- `orbit-research/PLAN_CODE_AUDIT.md` with verdict:
  `MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`
- `experiment_pack.plan_code_audit` with the same verdict and audit artifact path

Probe outputs when implementation/headroom probes are used:

- `experiment/PROBE_REPORT.md`
- `experiment/PROBE_AUDIT.md`
- `experiment/HEADROOM_NOTE.md` when the probe informs baseline/headroom expectations
- `experiment_pack.probes[]`
- concise probe notes in `refine-logs/EXPERIMENT_TRACKER.md` or `orbit-research/PIPELINE_SUMMARY.md`

Formal diagnostic outputs are **not** produced by this skill. STOP B probes are
implementation/headroom aids; formal diagnostics belong to `/diagnostic-to-review`:

- `orbit-research/RUN_LEDGER.jsonl`
- `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`

Legacy note: if an older STOP B run created `DIAGNOSTIC_RUN_REPORT.md` or
`DIAGNOSTIC_RUN_AUDIT.md` for a probe, treat those files as legacy probe evidence and
interpret them carefully. New STOP B probes must use `experiment/PROBE_*` names.

## Phase 0: Load Context And Decide Resume Point

Create `orbit-research/` and `refine-logs/` if needed.

Create `experiment/` as the STOP B pack/view root. Read `$ARGUMENTS` first. If it points
to `proposal/proposal_pack.json`, treat it as the approved proposal pack. If it points to
`FINAL_PROPOSAL.md`, `FINAL_PROPOSAL_SHORT.md`, or `METHOD_SPEC.md`, treat it as a legacy
approved proposal view and plan to write/update `experiment/experiment_pack.json`. If it
points to `experiment/experiment_pack.json`, `EXPERIMENT_PLAN.md`, or
`EXPERIMENT_PLAN_EXEC.md`, verify whether a plan already exists and resume from
implementation.

Read `orbit-research/IDEA_TO_PROPOSAL_STATE.json` when present. If it has
`status = "awaiting_human_continue"`, treat this invocation as the human's STOP A
approval signal.

Read `RESEARCH_DECISION_LOG.md` when present. If it says the failure type is
`implementation/config issue`, patch only the local implementation/config surface it
names. If it names another failure type, do not broaden the implementation task; route to
the indicated skill.

## Phase 1: Experiment Planning From The Approved Proposal

Load and follow [planning_contract.md](prompts/planning_contract.md). Run or perform
`/experiment-plan` from `proposal/proposal_pack.json`, then write/update
`experiment/experiment_pack.json` and render the experiment plan views. Validate with
`python3 tools/validate_orbit_pack.py --repo . --pack experiment_pack` when the pack exists.

## Phase 2: Implement The Planned Code

Load and follow [implementation_scope.md](prompts/implementation_scope.md). Read
`experiment/experiment_pack.json` first, use Markdown views as human-readable context, and
do not add unregistered experiments without first patching the pack/plan.

## Phase 3: Semantic Plan-Code Audit

Load and follow [semantic_plan_code_audit.md](prompts/semantic_plan_code_audit.md) and
`../shared-references/semantic-code-audit.md`. Codex review remains required; if MCP fails,
use `tools/codex_review_handoff.py` and `/import-codex-review` exactly as specified in the asset.

## Phase 4: Limited Implementation / Headroom Probe

Load and follow [probe_headroom.md](prompts/probe_headroom.md). Preserve the STOP B probe
capability, but keep probe artifacts under `experiment/` and never create formal diagnostic
or claim artifacts from a probe.

## Phase 5: Handoff

Write or update `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /experiment-bridge Summary

- Input: $ARGUMENTS
- Mode: plan-only | audit-only | probe | full-bridge
- Proposal: proposal/proposal_pack.json
- Experiment pack: experiment/experiment_pack.json
- Plan view: experiment/EXPERIMENT_PLAN.md
- Exec plan view: experiment/EXPERIMENT_PLAN_EXEC.md
- Audit: orbit-research/PLAN_CODE_AUDIT.md
- Probe reports: experiment/PROBE_REPORT.md / experiment/PROBE_AUDIT.md / experiment/HEADROOM_NOTE.md or NONE
- Formal diagnostics: NOT RUN BY THIS SKILL

## STOP B

Review:
- experiment/experiment_pack.json
- experiment/EXPERIMENT_PLAN.md
- experiment/EXPERIMENT_PLAN_EXEC.md
- orbit-research/PLAN_CODE_AUDIT.md
- experiment/PROBE_REPORT.md and `experiment_pack.probes[]`, if any

Human question:
Is this code/plan/probe status good enough for formal diagnostics?

## Next

/diagnostic-to-review "experiment/experiment_pack.json"
```

If mode is `full-bridge`, call `/diagnostic-to-review` after writing the STOP B summary.
This call is allowed only when `— confirm-stop-b-reviewed: true` is present, meaning the
user explicitly approved STOP B plan/code/probe status for formal diagnostics. Without
that confirmation, do not call `/diagnostic-to-review`; leave the safe next command as:

```text
/diagnostic-to-review "experiment/experiment_pack.json"
```

Do not call `/auto-review-loop` directly; `/diagnostic-to-review` owns
conditional-required claim/review routing.

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — apply selective milestone timestamping rules
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- Keep `/experiment-bridge` as the STOP B wrapper: planning, implementation, audit, probe,
  and handoff.
- Experiment planning belongs here after STOP A; it must not pollute `FINAL_PROPOSAL.md`.
- `experiment/experiment_pack.json` is the STOP B source of truth; Markdown plan files are
  generated views or compatibility copies.
- Probe artifacts are `experiment/PROBE_REPORT.md`, `experiment/PROBE_AUDIT.md`, and
  `experiment/HEADROOM_NOTE.md`; formal diagnostic artifacts are not probe artifacts.
- `experiment_pack.formal_diagnostics[]` is the only handoff list for formal diagnostics.
  Probe entries in `experiment_pack.probes[]` do not satisfy formal diagnostics.
- `full-bridge` must not bypass STOP B review; it requires
  `— confirm-stop-b-reviewed: true`.
- Every committed experiment must change a research decision. Paper-claim defense applies
  only to paper-bearing experiments.
- Never compare predictions against another model's output as ground truth; use dataset
  labels/targets or official eval scripts.
- Do not create paper claims, claim construction, red-team reviews, or paper-writing
  artifacts in this skill.
- Formal diagnostic execution, scientific interpretation, decision logging after results,
  and paper-level claim/review belong to `/diagnostic-to-review`.
- Old probe outputs named `DIAGNOSTIC_RUN_REPORT.md` or `DIAGNOSTIC_RUN_AUDIT.md` are
  legacy and should not be treated as successful formal diagnostics without checking
  whether `/diagnostic-to-review` actually produced them.

## Composing With Other Skills

```text
/idea-to-proposal      -> proposal candidate + STOP A
/experiment-bridge     -> experiment plan + implementation + PLAN_CODE_AUDIT + STOP B
/diagnostic-to-review  -> formal diagnostic + interpretation + decision log + conditional-required claim/review
/paper-draft           -> fast draft, no submission gates
/paper-from-claims     -> evidence-bound paper after STOP C approval and claims/claim_ledger.json
/submission-package    -> strict compile/audit/package readiness after STOP C approval
```

`/paper-writing` is only a compatibility router for the three paper entries above.
`orbit-research/CLAIM_CONSTRUCTION.md` is a legacy compatibility view generated alongside
or from `claims/claim_ledger.json`, not the canonical v2 source of truth.
