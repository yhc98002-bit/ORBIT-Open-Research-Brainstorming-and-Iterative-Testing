---
id: idea-to-proposal.innovation-loops.v1
used_by: idea-to-proposal phase 3
purpose: Run collaborative mechanism invention, analogy transfer, and algorithm tournament without premature convergence.
inputs:
  - grounding artifacts
  - innovation-loops.md
  - research-harness-prompts.md sections 8, 9, and 10
outputs:
  - orbit-research/MECHANISM_IDEATION.md
  - orbit-research/ANALOGY_TRANSFER.md
  - orbit-research/ALGORITHM_TOURNAMENT.md
  - proposal/proposal_pack.json updates
---

### Phase 3: Innovation — Stages 8 → 9 → 10 (Codex COLLABORATIVE)

Switch Codex to **collaborative mode** for all three stages (template in
`../shared-references/innovation-loops.md` §7.1). Codex appends candidates / blind spots /
alternative framings; it does NOT veto, prune, or converge.

#### Phase 3a — Stage 8: Mechanism Invention Loop

Use harness §8 + procedure in `innovation-loops.md` §2. Generate 5–10 candidate
mechanisms aimed at the abstract task from Phase 2b. Score each on novelty / feasibility /
falsifiability (1–5 each). Aim for breadth — at least one obvious, one borrowed-from-
another-field, one minimal, one complex/composite, one wild card. Append a "Codex
collaborative additions" section after Codex returns.

Write `orbit-research/MECHANISM_IDEATION.md`. Mark a tentative top-3 for Phase 3b.
Also normalize the candidate mechanisms into `proposal/proposal_pack.json` under
`candidate_mechanisms[]`.

#### Phase 3b — Stage 9: Analogy / Cross-pollination Loop

Use harness §9 + procedure in `innovation-loops.md` §3. For each top-3 candidate, name ≥1
analogous solved problem from another field. Map *what transfers / what doesn't / what
new constraint*. Codex collaborative additions append more analogies.

Write `orbit-research/ANALOGY_TRANSFER.md`.
Also attach key analogy transfer notes to the relevant `candidate_mechanisms[]` entries
in `proposal/proposal_pack.json`.

#### Phase 3c — Stage 10: Algorithm Sketch Tournament

Use harness §10 + procedure in `innovation-loops.md` §4. Write 1-page sketches per top
candidate (3–5 sketches). Round-robin pairwise on diagnosability / fidelity /
falsifiability / integration cost. Mark a TENTATIVE_PREFERRED_SKETCH_ID for Phase 4.
Keep alternates with their scores.

Codex on sketch quality is collaborative; on tournament adjudication Codex switches to
calibration mode (this is the one place inside innovation loops where Codex challenges
Claude's pairwise picks, but it must still preserve viable alternatives — see
`innovation-loops.md` §4 for the contract).

Write `orbit-research/ALGORITHM_TOURNAMENT.md` ending with the canonical line:

```
TENTATIVE_PREFERRED_SKETCH_ID: S<id>
ALTERNATES: S<id>, S<id>
ABSTAIN_REASONS: <if Codex objected>
NOT_FINAL_NOTE: Stage 10 selects candidates for Stage 11 HMBC review (not run by this
skill). The tentative pick is not a method commitment.
```

Also normalize the tentative winner and alternates into `proposal/proposal_pack.json`
under `selected_sketch` and `candidate_mechanisms[]`.

**Write STATE** at end of Phase 3:

```jsonc
{
  "phase": "phase-3-innovation",
  "status": "in_progress",
  "next_action": "phase-4-final-refinement",
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + proposal/proposal_pack.json + MECHANISM_IDEATION, ANALOGY_TRANSFER, ALGORITHM_TOURNAMENT compatibility views */]
}
```
