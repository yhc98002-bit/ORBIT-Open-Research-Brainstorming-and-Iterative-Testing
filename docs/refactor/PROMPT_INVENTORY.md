# Prompt Inventory

This inventory classifies the high-impact ORBIT skill files before and after the
prompt-preserving modularization pass. The purpose is to keep `SKILL.md` files readable
without deleting high-value research prompts.

## Classification Key

- `KEEP_IN_SKILL`: short routing, phase order, state behavior, and user-facing boundaries.
- `PROMPT_ASSET`: long phase prompts, review prompts, audit prompts, writing/routing
  prompts, and templates preserved under `skills/<skill>/prompts/*.md`.
- `CONTRACT`: schema, artifact, state, gate, or validator behavior that should point to
  schemas/tools/shared references.
- `LEGACY_COMPAT`: alias and migration behavior retained but isolated.
- `DUPLICATE`: content already canonical elsewhere and safe to replace with a pointer.

## research-refine

- `KEEP_IN_SKILL`: overview, constants, ORBIT refinement gates, checkpoint recovery,
  phase sequence, output protocols, composition rules.
- `PROMPT_ASSET`:
  - `skills/research-refine/prompts/problem_anchor.md`
  - `skills/research-refine/prompts/initial_proposal.md`
  - `skills/research-refine/prompts/reviewer_critique.md`
  - `skills/research-refine/prompts/anchor_simplicity_revision.md`
- `CONTRACT`: `refine-logs/REFINE_STATE.json`, score-history parsing, proposal bundle
  output names.
- `LEGACY_COMPAT`: `refine-logs/FINAL_PROPOSAL*.md` and old proposal bundle views.
- `DUPLICATE`: Codex handoff details point to `skills/shared-references/codex-precondition.md`
  and `tools/codex_review_handoff.py`.

## idea-to-proposal

- `KEEP_IN_SKILL`: input-mode detection, continuation behavior, STOP A pack contract,
  high-level phase order, STOP A state update, final non-goals.
- `PROMPT_ASSET`:
  - `skills/idea-to-proposal/prompts/grounding_pack.md`
  - `skills/idea-to-proposal/prompts/innovation_loops.md`
  - `skills/idea-to-proposal/prompts/integrated_final_refinement.md`
- `CONTRACT`: `proposal/proposal_pack.json`, `schemas/proposal_pack.schema.json`,
  `tools/orbit_pack.py`, `tools/validate_orbit_pack.py`, `orbit-research/ORBIT_STATE.json`.
- `LEGACY_COMPAT`: old `orbit-research/*` Markdown artifacts and `refine-logs/*`
  compatibility views remain readable but are not canonical state.
- `DUPLICATE`: Stage 4/5/7/8/9/10 harness prompt bodies remain canonical in
  `skills/shared-references/research-harness-prompts.md` and
  `skills/shared-references/innovation-loops.md`; the per-skill assets preserve the
  concrete orchestration wording.

## experiment-bridge

- `KEEP_IN_SKILL`: modes, accepted inputs, required outputs, resume rules, STOP B handoff,
  key rules, and composition boundaries.
- `PROMPT_ASSET`:
  - `skills/experiment-bridge/prompts/planning_contract.md`
  - `skills/experiment-bridge/prompts/implementation_scope.md`
  - `skills/experiment-bridge/prompts/semantic_plan_code_audit.md`
  - `skills/experiment-bridge/prompts/probe_headroom.md`
- `CONTRACT`: `experiment/experiment_pack.json`, `schemas/experiment_pack.schema.json`,
  `tools/validate_orbit_pack.py --pack experiment_pack`, semantic audit reference, Codex
  handoff tool.
- `LEGACY_COMPAT`: `refine-logs/EXPERIMENT_PLAN*.md` and old `orbit-research/*` planning
  views remain compatibility outputs.
- `DUPLICATE`: detailed semantic audit prompt remains in
  `skills/shared-references/semantic-code-audit.md`.

## diagnostic-to-review

- `KEEP_IN_SKILL`: STOP C ownership boundary, formal diagnostic vs probe distinction,
  session identity, preflight, idempotent skip, phase order, Codex required principle,
  final boundary.
- `PROMPT_ASSET`:
  - `skills/diagnostic-to-review/prompts/result_interpretation.md`
  - `skills/diagnostic-to-review/prompts/claim_relevance.md`
  - `skills/diagnostic-to-review/prompts/red_team_review.md`
  - `skills/diagnostic-to-review/prompts/stop_c_review.md`
- `CONTRACT`: per-diagnostic artifact root, `claims/claim_ledger.json`,
  `schemas/claim_ledger.schema.json`, `tools/validate_orbit_pack.py --pack claim_ledger`,
  `ORBIT_STATE.json`.
- `LEGACY_COMPAT`: latest copies at old `orbit-research/DIAGNOSTIC_*`,
  `CLAIM_CONSTRUCTION.md`, and `RED_TEAM_REVIEW.md` paths remain compatibility views.
- `DUPLICATE`: Codex standalone prompt export uses shared `codex-precondition.md` and
  `tools/codex_review_handoff.py`.

## paper-writing

- `KEEP_IN_SKILL`: compatibility-router purpose, preferred public paper entries, guardrail.
- `PROMPT_ASSET`:
  - `skills/paper-writing/prompts/routing_decision.md`
- `CONTRACT`: strict package checks live in `/submission-package`,
  `schemas/paper_package.schema.json`, claim/citation audit tools, and pack validators.
- `LEGACY_COMPAT`: old one-shot chain remains available only when explicitly requested.
- `DUPLICATE`: paper drafting, claim-bound writing, and submission assurance live in
  `/paper-draft`, `/paper-from-claims`, and `/submission-package`.

## research-pipeline

- `KEEP_IN_SKILL`: legacy v1.3 routing orchestrator, mode/risk routing, stage dispatch,
  hard gate sequencing, and backward-compatible artifact routing.
- `PROMPT_ASSET`: no per-skill assets were created in this pass because the pipeline already
  delegates prompt bodies to shared references.
- `CONTRACT`: stage map and gates point to
  `skills/shared-references/research-agent-pipeline.md`,
  `skills/shared-references/continuation-contract.md`, and current pack/status tools where
  newer public skills are used.
- `LEGACY_COMPAT`: retained as a callable legacy harness; public workflow docs now prefer
  `/idea-to-proposal`, `/experiment-bridge`, `/diagnostic-to-review`,
  `/paper-from-claims`, and `/submission-package`.
- `DUPLICATE`: shared prompt bodies remain in `research-harness-prompts.md`,
  `innovation-loops.md`, and `semantic-code-audit.md`; `research-pipeline/SKILL.md` now
  includes a prompt/contract library index instead of duplicating those prompt bodies.

## Regression Check

Run:

```bash
python3 tools/check_prompt_assets.py --repo .
```

The checker verifies that every `prompts/*.md` link from a canonical `SKILL.md` resolves,
every prompt asset has `id`, `used_by`, and `purpose` frontmatter, and no prompt asset body
is empty.
