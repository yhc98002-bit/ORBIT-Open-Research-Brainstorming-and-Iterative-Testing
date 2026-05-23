---
id: experiment-bridge.semantic-plan-code-audit.v1
used_by: experiment-bridge phase 3
purpose: Run required Codex semantic audit before probe or formal diagnostic.
inputs:
  - experiment/experiment_pack.json
  - implementation files
  - semantic-code-audit.md
outputs:
  - orbit-research/PLAN_CODE_AUDIT.md
  - experiment_pack.plan_code_audit
---

## Phase 3: Semantic Plan-Code Audit

Before any probe or formal diagnostic, run the semantic audit from
`../shared-references/semantic-code-audit.md`. The audit checks whether code implements the
intended algorithm, baselines, controls, ablations, datasets, splits, metrics, regimes,
seeds, config defaults, and result files.

Codex review remains required for this audit. If the Codex MCP/auth/sandbox path fails,
do not write a local substitute `PLAN_CODE_AUDIT.md`. Export a standalone prompt per
`../shared-references/codex-precondition.md` §5.5:

```bash
python3 tools/codex_review_handoff.py generate \
  --repo . \
  --phase-id "stop-b.plan-code-audit" \
  --role "Semantic plan-code audit reviewer" \
  --file "experiment/experiment_pack.json" \
  --file "experiment/EXPERIMENT_PLAN_EXEC.md" \
  --objective "Judge whether implementation matches the planned method, controls, metrics, and diagnostic regime." \
  --output-format "PLAN_CODE_AUDIT verdict: MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR, with rationale." \
  --required-section "VERDICT" \
  --output-artifact "orbit-research/PLAN_CODE_AUDIT.md" \
  --write-orbit-state
```

Then stop with `pause_reason: codex_review_needed` and safe next command
`/import-codex-review orbit-research/codex-imports/stop-b.plan-code-audit.response.md`.

Always write `orbit-research/PLAN_CODE_AUDIT.md` with a verdict line and mirror the
verdict into `experiment/experiment_pack.json` under `plan_code_audit`:

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
