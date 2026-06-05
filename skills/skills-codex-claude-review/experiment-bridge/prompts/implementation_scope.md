---
id: experiment-bridge.implementation-scope.v1
used_by: experiment-bridge phase 2
purpose: Implement only the planned code required by experiment_pack and executable plan views.
inputs:
  - experiment/experiment_pack.json
  - experiment/EXPERIMENT_PLAN_EXEC.md
  - proposal/METHOD_SPEC.md
outputs:
  - runnable planned implementation
  - parseable result outputs
---

## Phase 2: Implement The Planned Code

Read `experiment/experiment_pack.json` first. Use `experiment/EXPERIMENT_PLAN.md` only as
a human-readable view. Follow the pack's references and generated view `Files` table
before extracting implementation details:

- `experiment/EXPERIMENT_PLAN_EXEC.md` for claim/evidence targets, experiment blocks, run order,
  decision gates, budget, and risks
- current `[MILESTONE]_RUN_CARD.md` if marked as "NOW" or current immediate task
- `proposal/METHOD_SPEC.md` or legacy `METHOD_SPEC.md` for implementation-level method details
- `proposal/PROPOSAL.md` or legacy `FINAL_PROPOSAL_SHORT.md` for compact context
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
