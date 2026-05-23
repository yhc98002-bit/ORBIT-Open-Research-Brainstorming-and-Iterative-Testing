---
id: experiment-bridge.planning-contract.v1
used_by: experiment-bridge phase 1
purpose: Convert approved proposal input into experiment_pack and plan views without freezing paper claims.
inputs:
  - proposal/proposal_pack.json
  - legacy FINAL_PROPOSAL.md when needed
outputs:
  - experiment/experiment_pack.json
  - experiment/EXPERIMENT_PLAN.md
  - experiment/EXPERIMENT_PLAN_EXEC.md
---

## Phase 1: Experiment Planning From The Approved Proposal

If `EXPERIMENT_PLAN.md` and `EXPERIMENT_PLAN_EXEC.md` are missing, stale, or legacy,
invoke or perform `/experiment-plan` grounded in:

```bash
/experiment-plan "proposal/proposal_pack.json"
```

The plan must be decision-driven:

- candidate claims / evidence targets, not frozen paper claims
- every committed experiment must change a research decision
- paper-claim defense applies only to paper-bearing experiments
- do not force breakthrough-level evidence when `paper_mode = normal`
- allow normal-paper contribution types: empirical finding, method combination,
  benchmark + baseline, reproduction-plus, system, or focused mechanism
- controls must isolate the claim actually being made; null results must be interpretable
- `experiment/EXPERIMENT_PLAN.md` stays a short index view
- `experiment/EXPERIMENT_PLAN_EXEC.md` contains the executable run order and
  `Decision Tree / Branch Table`
- compatibility copies may be written to `refine-logs/EXPERIMENT_PLAN.md` and
  `refine-logs/EXPERIMENT_PLAN_EXEC.md`

Planning must write or update `experiment/experiment_pack.json` with:

- `proposal_ref`
- `decision_tree[]`
- `controls[]`
- `null_result_contract`
- `component_ladder[]`
- `algorithmic_formalization`
- `probes[]`
- `formal_diagnostics[]`

Then render:

- `experiment/EXPERIMENT_PLAN.md`
- `experiment/EXPERIMENT_PLAN_EXEC.md`
- optional compatibility copies in `refine-logs/`

The old `orbit-research/CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`,
`COMPONENT_BUNDLE_LADDER.md`, `ALGORITHMIC_FORMALIZATION.md`, and
`DIAGNOSTIC_EXPERIMENT_PLAN.md` may still be written during migration, but they are
compatibility views of `experiment_pack`, not primary state.

After `EXPERIMENT_PLAN_EXEC.md` exists and includes the decision tree, update only the
proposal status block in `FINAL_PROPOSAL.md` / `FINAL_PROPOSAL_SHORT.md` to
`EXPERIMENT_PLAN_READY` with evidence basis pointing to the plan artifacts. This means
"ready for plan-code bridge", not validated.

If mode is `plan-only`, stop here with STOP B planning summary and next action:
`/experiment-bridge "experiment/experiment_pack.json" — mode: audit-only` or `— mode: probe`.
