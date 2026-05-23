---
id: paper-writing.routing-decision.v1
used_by: paper-writing compatibility router
purpose: Route legacy paper-writing requests to draft, claim-bound writing, submission packaging, or legacy chain.
inputs:
  - user paper request
  - claims/claim_ledger.json when present
  - paper/ directory when present
outputs:
  - selected public paper skill
---

## Routing Rules

1. If the user asks for a quick draft, skeleton, rough paper, proposal-to-paper, or notes
   to draft, route to:

   ```text
   /paper-draft "$ARGUMENTS"
   ```

2. If `claims/claim_ledger.json` exists, or the user says claim-bound, evidence-bound,
   STOP C, validated claims, or paper from claims, route to:

   ```text
   /paper-from-claims "claims/claim_ledger.json"
   ```

   For legacy STOP C projects, require `orbit-research/RED_TEAM_REVIEW.md`  *(must end `READY_FOR_PAPER`)
   before treating the handoff as paper-ready. Other red-team verdicts route back to
   `/diagnostic-to-review` or `/auto-review-loop`.
   When present, `figures/figure_manifest.json` and `references/citation_cache.json` are
   passed as structured paper inputs rather than scanning figure/citation files ad hoc.

3. If the user says submission, final checks, assurance, package, camera-ready, audit,
   compile strictly, claim audit, citation audit, proof audit, or arXiv/venue package,
   route to:

   ```text
   /submission-package "paper/"
   ```

4. If the request explicitly says "use legacy paper-writing" or depends on the old
   one-shot chain, run the legacy chain:

   ```text
   /paper-plan -> /paper-figure -> /paper-write -> /paper-compile -> /auto-paper-improvement-loop
   ```

   Then direct strict assurance to `/submission-package`.
