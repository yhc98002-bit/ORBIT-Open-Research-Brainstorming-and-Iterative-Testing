---
id: diagnostic-to-review.stop-c-review.v1
used_by: diagnostic-to-review phase 5
purpose: Produce STOP C human-decision review without prematurely invoking paper writing.
inputs:
  - diagnostic context
  - result interpretation
  - claim ledger when paper-bearing
  - red-team review when paper-bearing
outputs:
  - STOP_C_REVIEW.md
  - HUMAN_DECISION_NOTE.template.md
---

### Phase 5: STOP C Review

Always write:

```text
orbit-research/diagnostics/<diagnostic_id>/STOP_C_REVIEW.md
orbit-research/diagnostics/<diagnostic_id>/HUMAN_DECISION_NOTE.template.md
```

`STOP_C_REVIEW.md` must summarize:

- diagnostic ID and input hash;
- exact run ID and result paths;
- run audit verdict and G12 structured interpretation;
- result interpretation;
- decision log route;
- claim ledger path, claim support statuses, and forbidden overclaims if paper-bearing;
- red-team final verdict if paper-bearing;
- blockers and required fixes;
- safe next human action.
