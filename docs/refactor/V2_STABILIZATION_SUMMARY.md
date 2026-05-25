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

## Release Checks

Fast v2.1 stabilization release gate:

```bash
make release-check
```

This expands to the repository audit/static checks plus the fast stabilization target:

```bash
python tools/orbit_repo_audit.py --repo . --out docs/refactor
python tools/list_skill_profiles.py --repo . --check
python tools/check_skill_mirror.py --repo .
python tools/check_prompt_assets.py --repo .
python tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all
make test-fast
```

`make test-fast` is intentionally split so core semantic checks avoid subprocess-heavy
tool launches:

```bash
make test-core    # direct-import unit tests for status, STOP C approval, sessions, packs, handoff
make test-cli     # minimal CLI smoke tests for the public tools
make test-static  # mirror, prompt asset, catalog, and static skill integrity checks
```

The core tests import helper functions directly, for example
`evaluate_stop_c_approval`, `diagnostic_session` functions, and
`validate_orbit_pack.validate_selection`. CLI coverage is kept to smoke tests for
`orbit_status.py`, `validate_orbit_pack.py`, `check_stop_c_approval.py`,
`codex_review_handoff.py`, and `diagnostic_session.py`.

Full `pytest -q` remains useful for broader local or CI coverage when the environment has
adequate timeout and optional dependencies for unrelated MCP/server tests. It is not the
fast release gate.

## Final Release-Blocker Audit

Status: **ORBIT v2.1 stable candidate**.

Checks run on 2026-05-25:

| Check | Status |
|---|---|
| `python tools/orbit_repo_audit.py --repo . --out docs/refactor` | pass |
| `python tools/list_skill_profiles.py --repo . --check` | pass |
| `python tools/check_skill_mirror.py --repo .` | pass, 0 unexpected drift |
| `python tools/check_prompt_assets.py --repo .` | pass |
| `python tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all` | pass, 6 ok |
| `make test-core` | pass, 70 passed / 3 CLI tests deselected |
| `make test-cli` | pass |
| `make test-static` | pass, 19 passed / 3 installer tests deselected |
| `make test-fast` | pass, composed from `test-core`, `test-cli`, and `test-static` |

Release-blocker checklist:

- STOP C approval/readiness: per-diagnostic `RED_TEAM_REVIEW.md` is authoritative when
  `diagnostic_id` is present; invalid claim ledgers block approval; missing diagnostic or
  ledger identity blocks by default; draft, pending, degraded, and non-gating claim
  ledgers are blocked; human decision must parse as `PROCEED`; Markdown single-token
  verdicts are accepted; candidate-list/template verdicts are rejected.
- `/orbit-status`: blocked paper packages are not reported completed; STOP/HOLD/template
  human decisions do not route to paper handoff; stale `ORBIT_STATE.json` cannot override
  validation; ready paper packages require validator pass; per-diagnostic red-team
  reviews are recognized; v2 public paper skill names are used instead of
  `/paper-writing`.
- Codex handoff: generated prompts preserve producer STOP, skill, phase, diagnostic id,
  target artifact, and resume command; imports update `ORBIT_STATE.json` with the resume
  command; verdict-required handoffs validate exactly one final token; imported Codex
  review does not fabricate human approval.
- Package validation: ready paper packages require a declared PDF that exists, referenced
  verified figure outputs that exist, verified citation keys, a valid claim ledger, and
  strict STOP C approval.
- Diagnostic sessions: terminal sessions are not silently reused; active sessions can be
  resumed by matching `input_hash`; fresh reruns require explicit `create --fresh`.
- Docs: `/paper-writing` is compatibility only; `claims/claim_ledger.json` is canonical;
  `CLAIM_CONSTRUCTION.md` is legacy/compatibility view only; v1.3 methodology vs v2.1
  runtime version semantics are documented.

No P0 release blockers remain in the scoped v2.1 stabilization checklist.

## Remaining Known Limitations

- Validators are intentionally lightweight and stdlib-based; they catch contract
  contradictions but do not replace full scientific review.
- Legacy Markdown artifacts remain during migration, so consumers must prefer packs when
  both exist.
- Reviewer overlays are intentionally different from canonical skills and must stay
  catalog-marked.
- External API, GPU, and live MCP behavior is not exercised by the golden fixture.
- Full `pytest -q` is broader coverage and should be run in CI or local environments with
  adequate timeout; `make test-fast` is the release-blocker gate and is optimized to stay
  fast by avoiding subprocess-heavy core tests.
