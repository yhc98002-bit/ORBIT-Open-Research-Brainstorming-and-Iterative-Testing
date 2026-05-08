# Experiment Plan — Index

> **Template for Workflow 1.5 (`/experiment-bridge`).** Save this file as
> `refine-logs/EXPERIMENT_PLAN.md`. Put executable details in
> `refine-logs/EXPERIMENT_PLAN_EXEC.md` and run-card files.

**Purpose**: this file is an **index**. The actual execution plan is split into
agent-actionable run cards and protocol files. Downstream skills should read this
index, then follow the cross-references.

**Project**: [one-line project / method / venue / budget status]

## Files

| Stage | File | What it contains | When to read |
|---|---|---|---|
| Method spec | `FINAL_PROPOSAL.md` | Proposal index and method cross-references | always |
| Main exec plan | `EXPERIMENT_PLAN_EXEC.md` | Claim map; compact block cards; run order; gates; budget; risks | always |
| Current immediate task | `[MILESTONE]_RUN_CARD.md` | The next action only: command surface, success gate, halt rule | now, if present |
| Failure routing | `NULL_RESULT_CONTRACT.md` | NEGATIVE / TIE interpretation and paper-pivot rules | when any block fails or ties |
| Optional protocols | `[PROTOCOL].md` | Dataset mapping, baseline protocol, figure plan, or other scoped details | only when referenced |

## Phased Flow

```text
Phase 0 — Sanity / diagnostic gate
  -> [current milestone or gate]
Phase 1 — Baselines and main method
  -> EXPERIMENT_PLAN_EXEC.md Run Order
Phase 2 — Decisive ablations
  -> halt at each registered decision gate
Phase 3 — Appendix / qualitative / write-up support
  -> run only after main evidence is secured
```

## Key Constraints

- [Hard stop / budget / data constraint that downstream agents must enforce]
- [No silent threshold relaxation; no unregistered experiment launch]
- [Nice-to-have runs must not delay must-run evidence]

## Downstream Skill

`/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"` reads this index, follows
the cross-references, and implements the milestones in `EXPERIMENT_PLAN_EXEC.md`
order. The bridge skill must not auto-launch a milestone past a hard stop without
explicit human approval.
