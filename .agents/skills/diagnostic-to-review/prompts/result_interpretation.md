---
id: diagnostic-to-review.result-interpretation.v1
used_by: diagnostic-to-review phase 2
purpose: Analyze exact diagnostic outputs and write the narrow research decision log.
inputs:
  - DIAGNOSTIC_CONTEXT.json
  - RUN_REPORT.md
  - RUN_AUDIT.md
  - RUN_LEDGER.jsonl
outputs:
  - RESULT_INTERPRETATION.md
  - RESEARCH_DECISION_LOG.md
---

### Phase 2: Analyze Exact Results

Do not call `/analyze-results` on the top-level results directory by default.

Instead derive exact result paths in this order:

1. `DIAGNOSTIC_CONTEXT.json.expected_result_paths` and `result_candidates`.
2. `RUN_REPORT.md` result file/path fields.
3. `orbit-research/RUN_LEDGER.jsonl` final record for the matching `run_id`.
4. W&B run ID or dashboard from `RUN_REPORT.md`.
5. `results/` only if exactly one candidate result directory exists and it matches the
   current `run_id`.

Then call:

```bash
/analyze-results "<exact result path(s) or W&B run id>"
```

Write:

```text
orbit-research/diagnostics/<diagnostic_id>/RESULT_INTERPRETATION.md
```

If no parseable result exists, still write a no-result interpretation from
`RUN_REPORT.md`, `RUN_AUDIT.md`, logs, and `RUN_LEDGER.jsonl`. Classify the outcome as
`no_result`, `oom`, `timeout`, `killed`, `failed`, or `blocked`, then write
`RESEARCH_DECISION_LOG.md`.

Only abort Phase 2 for invalid/corrupt evidence or integrity failure, such as fake ground
truth, score normalization fraud, phantom results, or scope inflation. Negative,
unsupported, tied, or mixed scientific outcomes are STOP C outcomes, not runtime aborts.

### Phase 2 Decision Log

For failed, mixed, contradictory, surprising, no-result, or unsupported outcomes, write:

```text
orbit-research/diagnostics/<diagnostic_id>/RESEARCH_DECISION_LOG.md
```

Use this structure:

```markdown
# Research Decision Log

- Diagnostic ID: <diagnostic_id>
- Input hash: <input_hash>
- Run ID: <run_id>
- Result paths: <exact paths>
- Result pattern: positive | negative | mixed | tie | surprising | no_result | invalid
- Affected hypotheses: H1-Hk
- Failure type: implementation/config issue | invalid diagnostic | mechanism issue | benchmark/headroom issue | central paper-breaking hypothesis false | literature conflict | inconclusive | integrity failure
- Decision: <ONE_DECISION_TOKEN>
- Allowed decision tokens:
  - continue
  - local patch
  - change diagnostic
  - re-read literature
  - failure-to-innovation
  - proposal-revise
  - archive
  - human decision
- Local patch target: experiment-bridge | experiment-plan | proposal-revise | research-lit | failure-to-innovation | manual
- Proposal revision needed: no | proposal-only | plan-only | both | assumption-only | mechanism-only | benchmark/control-only | diagnostic-branch-only
- Next skill hint: <exact skill or human decision>
- Human decision required: yes/no

## Rationale
Short evidence-based reason citing RESULT_INTERPRETATION, NULL_RESULT_CONTRACT,
experiment_pack decision tree, and affected H-IDs.
```

Failure routing remains narrow:

| Failure type | Route | Rule |
| --- | --- | --- |
| implementation/config issue | `/experiment-bridge` fix loop | Patch implementation/config and re-run plan-code audit; do not revise proposal. |
| invalid diagnostic | `/experiment-plan -- mode: diagnostic-branch-only` | Patch only diagnostic branch/run card; do not mark mechanism false. |
| mechanism issue | `/proposal-revise -- mode: mechanism-only` or failure-to-innovation | Revise mechanism artifacts only unless the log explicitly says broader. |
| benchmark/headroom issue | `/experiment-plan -- mode: benchmark/control-only` or `/proposal-revise -- mode: benchmark/control-only` | Patch controls, benchmark, or claim scope only. |
| central paper-breaking hypothesis false | human decision | Patch proposal status to `REFRAMED` or `ARCHIVED` only after human choice. |
| literature conflict | `/research-lit` then targeted revise | Re-read literature before changing mechanism or claims. |
| inconclusive | continue or change diagnostic | Follow the decision tree; avoid proposal revision unless required. |

`/idea-to-proposal -- fresh: true` is never the default failed-diagnostic recovery. Use it
only after explicit human decision to abandon the current problem/method.
