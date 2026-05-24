# ORBIT v2 Stabilization TODO

Generated for the v2 stabilization baseline refresh. This file records known
stabilization areas only; it does not change workflow behavior.

## Current Baseline

- Canonical skills: 77
- All `SKILL.md` files: 254
- `skills/skills-codex` full mirror status: no drift detected by the baseline audit
- `.agents/skills` full mirror status: Prompt 4 syncs known drift back to canonical
- Review overlays remain intentionally partial and catalog-governed

## Known Stabilization Areas

1. Paper-from-claims gate
   - Status: Prompt 1 adds explicit `/paper-from-claims` preflight text and
     `tools/check_stop_c_approval.py`.
   - Ensure `/paper-from-claims` cannot bypass `HUMAN_DECISION_NOTE.md` when moving from STOP C to paper generation.
   - Preserve the distinction between quick drafting and HITL-approved paper-bearing generation.

2. Submission-package gate
   - Status: Prompt 1 makes ready claim-bearing `paper_package` validation require STOP C approval.
   - Ensure `/submission-package` requires the appropriate human decision and evidence-bound inputs before strict submission checks.
   - Keep compile, claim audit, citation audit, and package readiness separate from draft generation.

3. Orbit-status STOP C next command
   - Status: Prompt 2 routes STOP C from `experiment/experiment_pack.json` formal diagnostics and blocks missing diagnostics instead of suggesting `PLAN_CODE_AUDIT.md`.
   - Confirm `tools/orbit_status.py` reports the safe STOP C handoff.
   - The safe next command should point to the human decision step until a valid `HUMAN_DECISION_NOTE.md` exists.

4. Shared references still using old paper-writing / CLAIM_CONSTRUCTION semantics
   - Audit shared references for stale `paper-writing` and `CLAIM_CONSTRUCTION.md` language.
   - Replace stale source-of-truth language with `claim_ledger.json` and the split paper paths where appropriate.

5. Mirror drift
   - Status: Prompt 4 syncs `.agents/skills` from canonical and adds mirror policy regression tests.
   - Full mirrors must remain generated from canonical `skills/`; do not edit `.agents/skills` by hand.
   - CI should run `python tools/check_skill_mirror.py --repo .`.

6. Diagnostic session helper missing
   - Status: Prompt 5 adds `tools/diagnostic_session.py` for `diagnostic_id`, `input_hash`, diagnostic context, run updates, and structured audit updates.
   - Keep `/diagnostic-to-review` recoverable without reusing stale fixed-path artifacts.

7. Run-experiment fixed-path diagnostic artifacts
   - Status: Prompt 5 documents `ORBIT_DIAGNOSTIC_ID` / `ORBIT_DIAGNOSTIC_OUTPUT_ROOT` and per-session `RUN_REPORT.md` / `RUN_AUDIT.md` as preferred formal diagnostic outputs.
   - Status: Prompt 11 makes `/run-experiment` treat per-diagnostic output roots as canonical for formal diagnostics while retaining fixed legacy latest copies only for compatibility.
   - Ensure experiment-bridge probes remain separate from formal diagnostic artifacts.

8. G12 semantics consistency
   - Status: Prompt 6 normalizes G12 around `verdict`, `regime_preserved`, and `mechanism_rejected`.
   - Route failed regime checks to diagnostic redesign, not automatic mechanism rejection.

9. Claim ledger negative result semantics
   - Status: Prompt 7 adds `claim_role` and `paper_use` to claim ledger entries and validator checks that unsupported claims cannot become allowed main paper claims.
   - Ensure unsupported or partial claims become structured claim ledger states and STOP C decisions.
   - Do not treat `claim_supported=no` as a default runtime abort unless evidence integrity is invalid.

10. Result-to-claim Codex handoff consistency
    - Status: Prompt 8 aligns `/result-to-claim` with the standalone Codex handoff contract and marks Codex-pending draft ledgers as non-gating.
    - Ensure Codex required remains intact.
    - If Codex MCP/auth/sandbox fails, export a standalone review prompt and require import before marking review complete.

11. Auto-review-loop red-team mode separation
    - Status: Prompt 9 separates generic improvement mode from ORBIT red-team verdict mode and documents that STOP C readiness uses only the final verdict token.
    - Keep research review, claim ledger review, paper claim audit, and red-team STOP C review distinct.
    - Avoid treating red-team prose or scores as equivalent to a structured STOP C verdict.

## Baseline Validation Notes

- `tools/check_skill_mirror.py` should pass after Prompt 4; future nonzero exits indicate new mirror drift.
- This baseline refresh intentionally does not fix mirror drift, schema issues, skill behavior, or shared-reference semantics.
