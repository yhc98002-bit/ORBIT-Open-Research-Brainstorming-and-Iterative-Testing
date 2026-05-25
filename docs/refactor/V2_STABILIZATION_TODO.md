# ORBIT v2.1 / v2.2 Stabilization TODO

Generated for the v2.1 stabilization baseline and v2.2 final stable regression pass. This
file records release blockers and known limitations; it does not change workflow behavior.

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

4. Codex standalone handoff must preserve and restore producer workflow context.
   - Status: fixed by `fix(codex): preserve workflow context across standalone review
     handoff`.
   - Handoff metadata now preserves producer STOP, skill, phase, diagnostic id, target
     artifact, and resume command; successful import updates `ORBIT_STATE.json` to
     `codex_review_imported` without treating import as human approval.

5. Diagnostic sessions need clearer rerun, resume, and fresh-run semantics.
   - Status: fixed by `fix(diagnostics): clarify session resume and fresh rerun
     semantics`.
   - `tools/diagnostic_session.py create` now reuses only active matching sessions,
     terminal sessions require explicit `resume` or `create --fresh`, and tests cover
     active reuse, terminal blocking, fresh rerun, and mismatched resume refusal.

6. Residual pre-v2 paper-writing / CLAIM_CONSTRUCTION wording must be cleaned or
   archived.
   - Status: fixed by `docs(v2): clean legacy paper-writing and version guidance`.
   - Current guidance describes `/paper-draft`, `/paper-from-claims`, and
     `/submission-package`; `/paper-writing` is compatibility only; the historical Chinese
     pipeline review is archived as pre-v2 guidance.

7. Version terminology needs one documented convention.
   - Status: fixed by `docs(v2): clean legacy paper-writing and version guidance`.
   - README now separates methodology contract (`ORBIT v1.3 stage/gate model`), runtime
     architecture (`ORBIT v2.1 pack/status workflow`), and legacy Markdown compatibility
     (`v1.x artifacts are compatibility views`).

8. Test suite needs a fast stabilization test target.
   - Status: fixed by `test(v2): add fast stabilization release checks`.
   - `make test-fast` runs the critical v2.1 stabilization tests, while `make
     release-check` runs static release checks plus `test-fast`.
   - Full `pytest -q` is documented as broader optional coverage that needs adequate
     timeout and optional test dependencies.

9. Final ORBIT v2.1 release-blocker audit.
   - Status: fixed by `chore(release): audit v2.1 stable candidate`.
   - Required static checks, `make test-core`, `make test-cli`, and `make test-fast`
     passed on 2026-05-25.
   - STOP C approval, `/orbit-status`, Codex handoff, package validation, diagnostic
     session, and legacy paper-path documentation blockers are recorded as closed in
     `docs/refactor/V2_STABILIZATION_SUMMARY.md`.

## Closed in v2.2 Final Stable Pass

1. Verdict parsers must reject unfinished templates such as allowed-token bullet lists
   followed by `Final verdict: <ONE_TOKEN>` or `Final decision: <ONE_TOKEN>`.
   - Status: fixed by `fix(approval): reject template verdicts and list-token approvals`.
   - Shared final-token parsing now rejects list items, placeholders, candidate lists,
     multiple allowed tokens on one line, and vague verdict-required Codex responses.

2. Bullet-list tokens such as `- PROCEED` or `- READY_FOR_PAPER` must never count as
   final approvals.
   - Status: fixed by `fix(approval): reject template verdicts and list-token approvals`.

3. Invalid semantic claim ledgers must route `/orbit-status` to `/result-to-claim` or
   claim-ledger repair, not to `/auto-review-loop`.
   - Status: fixed by `fix(status): route invalid claim ledgers to claim repair`.
   - Valid but unreviewed claim ledgers still route to ORBIT red-team review.

4. `orbit-core` profile installs must include Codex standalone recovery support, and the
   full idea-to-paper workflow must have a clear recommended profile.
   - Status: fixed by `fix(installer): add complete research-paper profile and Codex
     recovery utility`.
   - `orbit-core` includes `/import-codex-review`; `research-paper` includes the complete
     idea-to-paper public workflow.

5. Final ORBIT v2.2 release-blocker audit.
   - Status: fixed by `chore(release): complete ORBIT v2.2 stable audit`.
   - Required static checks and `make test-fast` passed on 2026-05-25.
   - Full `pytest -q` was not run in this audit; it remains broader optional coverage for
     environments with adequate timeout.

## Current Unresolved Stabilization Blockers

No known P0 parser, profile-install, STOP C approval, package-readiness, or
`/orbit-status` recovery blockers remain after the v2.2 fast/static release gate.

## Non-Blocking Known Limitations

- Validators remain lightweight and do not replace scientific or statistical review.
- Legacy Markdown artifacts remain readable during migration, so consumers must prefer
  JSON packs when both exist.
- External API, GPU, live MCP transport, and full paper compilation are outside the golden
  fixture and fast release gate.
- Full `pytest -q` is broader coverage and needs an environment with adequate timeout and
  optional dependencies; `make test-fast` is the v2.2 release-blocker gate.

## Baseline Validation Notes

- `python3 tools/orbit_repo_audit.py --repo . --out docs/refactor`: pass
- `python3 tools/list_skill_profiles.py --repo . --check`: pass
- `python3 tools/check_skill_mirror.py --repo .`: pass
- `python3 tools/check_prompt_assets.py --repo .`: pass
- `python3 tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all`: pass
- `make test-fast`: pass

## Historical v2.0 Stabilization Work

The v2.0 stabilization pass added the current pack layer, `/orbit-status`, STOP C session
helper, Codex handoff path, split paper entries, mirror policy, and golden fixture tests.
Those changes remain the baseline for v2.1, but they do not close the blockers listed
above.

Final v2.0 release details are summarized in
`docs/refactor/V2_STABILIZATION_SUMMARY.md`.
