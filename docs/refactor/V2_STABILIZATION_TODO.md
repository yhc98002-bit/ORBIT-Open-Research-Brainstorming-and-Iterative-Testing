# ORBIT v2.1 Stabilization TODO

Generated for the v2.1 stabilization baseline. This file records current blockers only;
it does not change workflow behavior.

## Current Baseline

- Canonical skills: 77
- All `SKILL.md` files: 254
- `skills/skills-codex` full mirror status: no unexpected drift
- `.agents/skills` full mirror status: no unexpected drift
- Review overlays remain intentionally partial and catalog-governed
- Prompt assets: 16 references, 16 assets, no missing prompt files
- Golden minimal project pack validation: 6 ok, 0 warning, 0 error

## Closed in v2.1 Stabilization

1. STOP C approval checker must reject draft, pending, or non-gating claim ledgers.
   - Status: fixed by `fix(approval): harden STOP C readiness and verdict parsing`.
   - `tools/check_stop_c_approval.py` and `tools/validate_orbit_pack.py` now block
     `draft`, `pending`, `degraded`, and `gating: false` claim ledgers by default.

2. Verdict parser must support Markdown single-token verdicts and reject candidate
   lists/templates.
   - Status: fixed by `fix(approval): harden STOP C readiness and verdict parsing`.
   - Markdown single-token verdicts such as `Final verdict: **READY_FOR_PAPER**` are
     accepted, while candidate lists containing `|` or multiple allowed tokens are ignored
     as templates.

3. `/orbit-status` must parse paper package status and human decision verdicts instead
   of relying on file presence.
   - Status: fixed by `fix(status): correct STOP C and STOP D readiness inference`.
   - Status inference now reads `paper_package.status`, validates ready packages, reuses
     STOP C approval semantics, recognizes per-diagnostic red-team reviews, and refuses
     paper handoff when `HUMAN_DECISION_NOTE.md` does not end `PROCEED`.

## Current Unresolved Stabilization Blockers

1. Codex standalone handoff must preserve and restore producer workflow context.
   - Current risk: imported Codex responses may validate review text but lose the
     producing phase, target artifact, pack field, or expected destination.
   - Expected stabilization: exported prompts and imports should carry enough structured
     context to resume the original workflow safely.

2. Diagnostic sessions need clearer rerun, resume, and fresh-run semantics.
   - Current risk: completed diagnostic sessions may be silently reused when a fresh run
     is needed, or old fixed-path artifacts may influence a new diagnostic.
   - Expected stabilization: require explicit user intent for rerun vs resume vs fresh
     session, using `diagnostic_id`, `input_hash`, `run_id`, and result paths.

3. Residual pre-v2 paper-writing / CLAIM_CONSTRUCTION wording must be cleaned or
   archived.
   - Current risk: compatibility references are mostly labeled, but residual prose can
     still imply `/paper-writing` or `CLAIM_CONSTRUCTION.md` is canonical.
   - Expected stabilization: keep only explicit compatibility-router or compatibility-view
     references in current docs; move historical language to archived notes if needed.

4. Test suite needs a fast stabilization test target.
   - Current risk: `pytest -q` passes, but it includes unrelated MCP-server tests and
     external-service-adjacent suites.
   - Expected stabilization: add a documented fast command that runs only ORBIT
     stabilization tests without broad unrelated coverage.

5. Version terminology needs one documented convention.
   - Current risk: docs mention v1.3, v1.4, v2, v2.0, and v2.1 in overlapping ways.
   - Expected stabilization: document which labels mean architecture generation,
     compatibility version, and stabilization patch line.

## Baseline Validation Notes

- `python3 tools/orbit_repo_audit.py --repo . --out docs/refactor`: pass
- `python3 tools/list_skill_profiles.py --repo . --check`: pass
- `python3 tools/check_skill_mirror.py --repo .`: pass
- `python3 tools/check_prompt_assets.py --repo .`: pass
- `python3 tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all`: pass

## Historical v2.0 Stabilization Work

The v2.0 stabilization pass added the current pack layer, `/orbit-status`, STOP C session
helper, Codex handoff path, split paper entries, mirror policy, and golden fixture tests.
Those changes remain the baseline for v2.1, but they do not close the blockers listed
above.

Final v2.0 release details are summarized in
`docs/refactor/V2_STABILIZATION_SUMMARY.md`.
