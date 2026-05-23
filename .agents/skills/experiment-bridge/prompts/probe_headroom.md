---
id: experiment-bridge.probe-headroom.v1
used_by: experiment-bridge phase 4
purpose: Run limited implementation/headroom probes without conflating them with formal diagnostics.
inputs:
  - experiment/experiment_pack.json
  - PLAN_CODE_AUDIT verdict
outputs:
  - experiment/PROBE_REPORT.md
  - experiment/PROBE_AUDIT.md
  - experiment/HEADROOM_NOTE.md
  - experiment_pack.probes[]
---

## Phase 4: Limited Implementation / Headroom Probe

Probe runs are allowed by default in `probe` mode, but they are not paper evidence. They
exist to validate implementation feasibility:

- environment check
- dataloader / metric parser sanity
- one-batch or tiny overfit
- logging / W&B / result path validation
- diagnostic command smoke test
- minimal local mechanism probe whose purpose is implementation readiness
- baseline/headroom probe whose purpose is deciding whether formal diagnostics are worth
  launching

Probe runs may call `/run-experiment` only as a local implementation helper. STOP B must
translate the outcome into probe-specific artifacts:

- `experiment/PROBE_REPORT.md`
- `experiment/PROBE_AUDIT.md`
- `experiment/HEADROOM_NOTE.md` when relevant
- `experiment_pack.probes[]`

Do not write new `orbit-research/DIAGNOSTIC_RUN_REPORT.md` or
`orbit-research/DIAGNOSTIC_RUN_AUDIT.md` for STOP B probes. Those names are reserved for
formal diagnostics owned by `/diagnostic-to-review`.

Probe results must not directly create paper claims:

- do not write `claims/claim_ledger.json`
- do not write `CLAIM_CONSTRUCTION.md`
- do not write `RED_TEAM_REVIEW.md`
- do not run `/auto-review-loop`
- do not perform formal scientific result interpretation beyond implementation/probe
  status

If a probe unexpectedly affects paper-level claim scope, stop and hand off to:

```bash
/diagnostic-to-review "experiment/experiment_pack.json"
```
