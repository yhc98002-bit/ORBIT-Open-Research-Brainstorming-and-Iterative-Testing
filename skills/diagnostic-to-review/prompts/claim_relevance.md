---
id: diagnostic-to-review.claim-relevance.v1
used_by: diagnostic-to-review phase 3
purpose: Decide local vs paper-bearing diagnostic handling and update claim_ledger when needed.
inputs:
  - RESULT_INTERPRETATION.md
  - experiment_pack decision tree
outputs:
  - claims/claim_ledger.json when paper-bearing
  - NEGATIVE_RESULT_STRATEGY.md when needed
---

### Phase 3: Claim Relevance Gate

First classify the diagnostic:

- Local diagnostics stop after `RESULT_INTERPRETATION.md` and `RESEARCH_DECISION_LOG.md`.
- Paper-bearing diagnostics must run `/result-to-claim`.

Local diagnostics include sanity, provenance, implementation/config validation, benchmark
plumbing, evaluator validity, and local mechanism probes that do not change paper-level
claim scope.

Paper-bearing diagnostics include main benchmarks, paper ablations, critical hypotheses
whose truth changes claim wording, scale-up evidence, and negative/tie results that weaken
or reframe paper-bearing claims.

For paper-bearing diagnostics:

```bash
/result-to-claim "<diagnostic_id>: <one-line result description>"
```

This call must produce or update:

- `claims/claim_ledger.json` -- canonical claim/evidence ledger
- `claims/CLAIM_LEDGER.md` -- generated human-readable view
- `orbit-research/diagnostics/<diagnostic_id>/CLAIM_CONSTRUCTION.md` -- compatibility
  session view when useful
- `orbit-research/CLAIM_CONSTRUCTION.md` -- latest compatibility copy during migration
- `NEGATIVE_RESULT_STRATEGY.md` if `claim_supported = no`, tie, failure, or reframe
- `AGENT_DECISION_RECOMMENDATION.md` if produced by `/result-to-claim`

`claims/claim_ledger.json` must contain an entry for every claim affected by this
diagnostic. Each entry must include `id`, `statement`, `status` (`supported`, `partial`,
`unsupported`, or `exploratory`), `evidence_refs`, `controls`, `scope`, `limitations`,
`forbidden_overclaims`, and `allowed_paper_sections`.

Update `DIAGNOSTIC_CONTEXT.json`, `DIAGNOSTIC_TO_REVIEW_STATE.json`, and
`ORBIT_STATE.json` artifact inventories with `claims/claim_ledger.json` and
`claims/CLAIM_LEDGER.md`.

`claim_supported = no` is not an automatic runtime abort. It means:

1. Write unsupported claim status in `claims/claim_ledger.json`.
2. Write `NEGATIVE_RESULT_STRATEGY.md`.
3. Write/update `RESEARCH_DECISION_LOG.md`.
4. Continue to Phase 5 STOP C review, or run Phase 4 only if a red-team review is useful
   for deciding whether the negative/reframed claim is paper-ready.
5. Pause for human decision.

Abort only for invalid/corrupt evidence or integrity failure.

G14 and G17 remain hard gates:

- G14: tie/failure/null result must not be positively framed.
- G17: post-hoc claims must be labeled as exploratory, not pre-planned.
