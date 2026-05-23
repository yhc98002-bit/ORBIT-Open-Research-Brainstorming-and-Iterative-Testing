---
id: idea-to-proposal.integrated-final-refinement.v1
used_by: idea-to-proposal phase 4
purpose: Convert the tentative tournament winner into a STOP A proposal_pack and compatibility views.
inputs:
  - proposal/proposal_pack.json
  - orbit-research/ALGORITHM_TOURNAMENT.md
  - orbit-research/ABSTRACT_TASK_MECHANISM.md
  - orbit-research/ASSUMPTION_LEDGER.md
outputs:
  - proposal/proposal_pack.json
  - proposal/PROPOSAL.md
  - refine-logs/FINAL_PROPOSAL_SHORT.md
---

### Phase 4: Integrated Final Refinement (Collaborator Calibration)

Codex switches to **collaborator calibration** before STOP A. The goal is a clean
proposal-worthy method and positioning route, not a hostile acceptance review.

Feed the Phase 3c winner sketch back into `/research-refine`:

```bash
/research-refine "proposal/proposal_pack.json + orbit-research/ALGORITHM_TOURNAMENT.md TENTATIVE_PREFERRED_SKETCH_ID + orbit-research/ABSTRACT_TASK_MECHANISM.md + orbit-research/ASSUMPTION_LEDGER.md" \
    — venue: <parsed_flags.venue> \
    — effort: <parsed_flags.effort> \
    — difficulty: <parsed_flags.difficulty> \
    — paper-mode: normal \
    — review-posture: collaborator
```

Forward `venue`, `effort`, `difficulty`, `paper-mode`, and `review-posture` explicitly
for this final refinement pass. Do not apply `hard` / `nightmare` difficulty to Stage
8/9/10 innovation loops; before STOP A, difficulty calibrates strict collaborator review,
not automatic acceptance-stage rejection review.

Goal: update `proposal/proposal_pack.json` so it (a) anchors on the Phase 1 problem,
(b) declares the Phase 3c tentative sketch as the proposed method, (c) cites
ASSUMPTION_LEDGER row IDs for central factual, method, benchmark, and paper-bearing
"is/will" claims, (d) cites the abstract task framing, (e) acknowledges the alternate
sketches kept on the table for later revival, and
(f) contains enough structured content to render `## Proposal Status` plus
`## Critical Hypotheses` in both `proposal/PROPOSAL.md` and legacy
`refine-logs/FINAL_PROPOSAL_SHORT.md`.

Keep `proposal/PROPOSAL.md` readable. Put dense assumption tracing in the pack's
`assumptions[]` plus `orbit-research/ASSUMPTION_LEDGER.md`, implementation detail in
`proposal/METHOD_SPEC.md`, and decision history in `orbit-research/RESEARCH_DECISION_LOG.md`.

At this phase the proposal status should be `PROPOSAL_READY`: the proposal is coherent
enough for STOP A human review. Use `EXPERIMENT_PLAN_READY` only after
`/experiment-bridge` has written `EXPERIMENT_PLAN_EXEC.md` and completed the plan/code
bridge checks. Do not over-repeat that the proposal is still hypothesis-bearing; preserve
uncertainty once in `## Critical Hypotheses` and `ASSUMPTION_LEDGER.md`.

If Codex flags a serious problem with the winner sketch, the integrated proposal MAY pick
an alternate from `ALGORITHM_TOURNAMENT.md` instead — record this in
`proposal/proposal_pack.json` under `selected_sketch` and render it in the proposal's
`## Method Selection Rationale` section.

The output is a **v1.4 proposal_pack**, plus rendered v1.3-compatible Markdown views.

**Write STATE** at end of Phase 4:

```jsonc
{
  "phase": "phase-4-final-refinement",
  "status": "in_progress",
  "next_action": "phase-5-summary",
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + proposal/proposal_pack.json (updated) + proposal/PROPOSAL.md + legacy refine-logs views */]
}
```
