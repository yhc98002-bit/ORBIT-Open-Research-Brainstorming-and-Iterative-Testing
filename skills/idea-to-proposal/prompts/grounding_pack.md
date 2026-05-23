---
id: idea-to-proposal.grounding-pack.v1
used_by: idea-to-proposal phase 2
purpose: Produce STOP A grounding artifacts and normalize them into proposal_pack.
inputs:
  - phase 1 proposal
  - research-harness-prompts.md sections 4, 5, and 7
outputs:
  - orbit-research/ASSUMPTION_LEDGER.md
  - orbit-research/ABSTRACT_TASK_MECHANISM.md
  - orbit-research/BASELINE_CEILING.md
  - proposal/proposal_pack.json updates
---

### Phase 2: Grounding — Stages 4 → 5 → 7

For each stage below, use the exact harness prompt from
`../shared-references/research-harness-prompts.md`. Read the proposal from Phase 1 as input
context. Codex performs calibration here; it should classify risks and assumptions
without acting as an automatic rejection reviewer.

#### Phase 2a — Stage 4: Assumption Ledger

Use harness §4. List assumptions behind the Phase 1 proposal's central factual, method,
benchmark, and paper-bearing claims. Tag each as `factual` (citable) or `working` (must be
tested). Cover at minimum: data availability, mechanism plausibility, baseline behaviour,
evaluator validity, scale regime, infrastructure cost, time horizon. Do not ledger every
background sentence unless it is used to justify the method, benchmark, or paper-level
claim.

Write `orbit-research/ASSUMPTION_LEDGER.md`. It must include a
`## Critical Hypotheses` section before or after the assumption table:

| ID | Hypothesis | Role | Confidence | Cheapest diagnostic | If false | Linked assumption/block |
|----|------------|------|------------|----------------------|----------|-------------------------|
| H1 | [central hypothesis] | paper-breaking/supporting/optional | low/medium/high | [diagnostic] | continue/weaken/reframe/archive | A<n> / B<n> |

This is a risk register, not a pre-proposal gate. Do not block proposal generation because
a critical hypothesis is uncertain; record the risk and make the cheapest diagnostic
explicit.

**Inline G2 reminder:** central factual, method, benchmark, and paper-bearing
"is/will/always" claims in downstream artifacts must trace to a row in this ledger or get
demoted. Background context can stay readable without row-by-row tracing unless it carries
the argumentative weight of the proposal.

Also normalize the ledger rows into `proposal/proposal_pack.json` under `assumptions[]`.

#### Phase 2b — Stage 5: Abstract Task / Mechanism Framing

Use harness §5. Strip the problem to: input space, output space, decision structure,
information bottleneck, primary failure modes, candidate mechanism families (3–5).

Write `orbit-research/ABSTRACT_TASK_MECHANISM.md`.

Also normalize the abstract task, information bottleneck, failure modes, and mechanism
families into `proposal/proposal_pack.json` under `abstract_task`.

#### Phase 2c — Stage 7: Baseline Ceiling / Headroom Audit

Use harness §7. If Phase 1 output already mentions baselines, deepen them; otherwise
estimate from scratch. List relevant simple-strong baselines, their estimated ceiling,
benchmark saturation risk, highest-headroom regime.

Write `orbit-research/BASELINE_CEILING.md`.

Also normalize the baseline/headroom findings into `proposal/proposal_pack.json` under
`baseline_headroom`.

**Note:** headroom is a *reference*, not a veto. A low ceiling does not block the
pipeline; it calibrates how loud Phase 4's claim wording can be.

**Write STATE** at end of Phase 2:

```jsonc
{
  "phase": "phase-2-grounding",
  "status": "in_progress",
  "next_action": "phase-3-innovation",  // or "phase-5-summary" if STOP_AT_GROUNDING
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + proposal/proposal_pack.json + ASSUMPTION_LEDGER.md, ABSTRACT_TASK_MECHANISM.md, BASELINE_CEILING.md compatibility views */]
}
```

If `— human checkpoint: true`, write `awaiting_human_continue` and stop; resume on next call.

**Stop here if `STOP_AT_GROUNDING = true`.** Skip to Phase 5.
