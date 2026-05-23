# STOP B Migration

STOP B now uses `experiment/experiment_pack.json` as the canonical experiment
planning and bridge artifact. Markdown remains readable as generated views or
legacy compatibility files.

## New Source Of Truth

`/experiment-bridge` should write:

```text
experiment/experiment_pack.json
```

The pack stores:

- `proposal_ref`
- `decision_tree`
- `controls`
- `null_result_contract`
- `component_ladder`
- `algorithmic_formalization`
- `plan_code_audit`
- `probes`
- `formal_diagnostics`

Primary views:

- `experiment/EXPERIMENT_PLAN.md`
- `experiment/EXPERIMENT_PLAN_EXEC.md`

Legacy compatibility views may still be written:

- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- old `orbit-research/CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`,
  `COMPONENT_BUNDLE_LADDER.md`, `ALGORITHMIC_FORMALIZATION.md`, and
  `DIAGNOSTIC_EXPERIMENT_PLAN.md`

## Probe vs Formal Diagnostic

`/experiment-bridge` may run limited implementation/headroom probes. These are
not paper evidence and must use probe-specific artifacts:

- `experiment/PROBE_REPORT.md`
- `experiment/PROBE_AUDIT.md`
- `experiment/HEADROOM_NOTE.md`
- `experiment_pack.probes[]`

Formal diagnostics remain owned by `/diagnostic-to-review` and use:

- `orbit-research/RUN_LEDGER.jsonl`
- `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`

Old STOP B probe outputs named `DIAGNOSTIC_RUN_REPORT.md` or
`DIAGNOSTIC_RUN_AUDIT.md` are legacy. Treat them as probe evidence unless there
is clear evidence that `/diagnostic-to-review` produced them as formal
diagnostics.

## Boundary

`/experiment-bridge` must not create:

- `claims/claim_ledger.json`
- `CLAIM_CONSTRUCTION.md`
- `RED_TEAM_REVIEW.md`

If a probe changes paper-level claim scope, STOP B should stop and hand off to:

```text
/diagnostic-to-review "experiment/experiment_pack.json"
```

`/orbit-status` recognizes `experiment/experiment_pack.json` and reports plan,
audit, and probe status for STOP B.
