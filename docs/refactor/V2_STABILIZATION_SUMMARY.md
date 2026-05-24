# ORBIT v2 / v2.1 Stabilization Summary

This release gate summarizes the v2 architecture and v2.1 stabilization pass. It does not
introduce a new architecture; it verifies that the v2 contracts are internally consistent
and that legacy surfaces are clearly marked as compatibility paths.

Version terminology: methodology contract = ORBIT v1.3 stage/gate model; runtime
architecture = ORBIT v2.1 pack/status workflow; legacy Markdown compatibility = v1.x
artifacts remain readable as compatibility views.

## What Changed

- Refreshed the repository baseline audit: 77 canonical skills and 254 total `SKILL.md`
  files.
- Added and enforced machine-readable pack contracts for proposal, experiment, claim,
  figure, citation, and paper package artifacts.
- Made `/orbit-status` the read-only status doctor for current STOP, blockers, and safe
  next command.
- Split paper work into public entries for draft, evidence-bound writing, and strict
  submission packaging.
- Added STOP C diagnostic session identity through `diagnostic_id`, `input_hash`, and
  per-session diagnostic directories.
- Added standalone Codex review handoff so Codex remains required even when MCP transport
  fails.
- Stabilized Codex handoff context restore: imports preserve producer STOP, skill, phase,
  diagnostic id, target artifact, and resume command without counting as human approval.
- Stabilized diagnostic session rerun semantics: active sessions may resume, while
  terminal sessions require explicit `resume` or `create --fresh`.
- Synced full mirrors and made mirror drift CI-checkable.

## Public Entrypoints

Canonical v2 flow:

```text
/idea-to-proposal
/experiment-bridge
/diagnostic-to-review
/paper-draft OR /paper-from-claims
/submission-package
/orbit-status whenever stuck
```

`/paper-writing`, `/research-pipeline`, and `/research-refine-pipeline` remain
compatibility routers or legacy wrappers. New user-facing docs should prefer the public
entries in `skills/skill_catalog.yaml`.

## Canonical Packs

JSON packs are the source of truth; Markdown is a generated or compatibility view:

- STOP A: `proposal/proposal_pack.json`
- STOP B: `experiment/experiment_pack.json`
- STOP C: `claims/claim_ledger.json`
- STOP D: `paper/paper_package.json`
- Figures: `figures/figure_manifest.json`
- Citations: `references/citation_cache.json`

Legacy Markdown artifacts such as `orbit-research/CLAIM_CONSTRUCTION.md` remain readable
only as compatibility views.

## Paper Path

- `/paper-draft` can create a fast draft or skeleton without STOP C gates and must mark
  unaudited claims as draft/TODO material.
- `/paper-from-claims` is evidence-bound and requires `claims/claim_ledger.json`,
  `RED_TEAM_REVIEW.md` ending `READY_FOR_PAPER`, and
  `orbit-research/HUMAN_DECISION_NOTE.md` ending `PROCEED`.
- `/submission-package` owns strict compile, claim audit, citation audit, proof/package
  checks, and `paper/paper_package.json`. Claim-bearing ready packages require STOP C
  approval.

## STOP C Diagnostic Sessions

Formal diagnostics use per-session paths under
`orbit-research/diagnostics/<diagnostic_id>/`. Resume safety depends on matching
`diagnostic_id`, `input_hash`, `run_id`, and result paths; fixed legacy paths such as
`orbit-research/DIAGNOSTIC_RUN_REPORT.md` are compatibility latest copies only.

Experiment-bridge probes remain implementation/headroom aids and must not create formal
diagnostic artifacts, claim ledgers, or red-team reviews. Formal diagnostics are handed to
`/diagnostic-to-review` through `experiment/experiment_pack.json`.

## Codex Handoff

Codex review remains required by default. MCP/auth/sandbox failure exports a standalone
prompt under `orbit-research/codex-prompts/` and waits for a response imported through
`/import-codex-review`. A single-model fallback does not satisfy commitment gates unless
the user explicitly requests degraded mode and later accepts degraded artifacts.
Importing a standalone response repairs the Codex transport gap only; it does not create
`HUMAN_DECISION_NOTE.md`, does not approve STOP C, and resumes the producer skill using
the handoff metadata.

## Mirror Policy

`skills/` is canonical. `.agents/skills` and `skills/skills-codex` are full generated
mirrors and must match canonical. `skills/skills-codex-claude-review` and
`skills/skills-codex-gemini-review` are catalog-governed overlays and may intentionally
differ.

## Release Gate Result

- `python3 tools/orbit_repo_audit.py --repo . --out docs/refactor`: pass
- `python3 tools/list_skill_profiles.py --repo . --check`: pass
- `python3 tools/check_skill_mirror.py --repo .`: pass
- `python3 tools/check_prompt_assets.py --repo .`: pass
- `python3 tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all`: pass
- `pytest -q`: pass after installing the test dependencies used by existing MCP-server
  tests (`pytest`, `httpx`)

## Remaining Known Limitations

- Validators are intentionally lightweight and stdlib-based; they catch contract
  contradictions but do not replace full scientific review.
- Legacy Markdown artifacts remain during migration, so consumers must prefer packs when
  both exist.
- Reviewer overlays are intentionally different from canonical skills and must stay
  catalog-marked.
- External API, GPU, and live MCP behavior is not exercised by the golden fixture.
