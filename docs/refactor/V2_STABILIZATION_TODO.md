# ORBIT v2 Stabilization TODO

Generated for the v2 stabilization baseline refresh and updated by the final release
gate. This file now records which stabilization areas were closed for v2.0.

## Current Baseline

- Canonical skills: 77
- All `SKILL.md` files: 254
- `skills/skills-codex` full mirror status: no unexpected drift
- `.agents/skills` full mirror status: no unexpected drift
- Review overlays remain intentionally partial and catalog-governed

## Completed Stabilization Areas

1. Paper-from-claims gate
   - Status: completed. Prompt 1 adds explicit `/paper-from-claims` preflight text and
     `tools/check_stop_c_approval.py`.
   - `/paper-from-claims` cannot bypass `HUMAN_DECISION_NOTE.md` when moving from STOP C to paper generation.
   - Preserve the distinction between quick drafting and HITL-approved paper-bearing generation.

2. Submission-package gate
   - Status: completed. Prompt 1 makes ready claim-bearing `paper_package` validation require STOP C approval.
   - `/submission-package` requires the appropriate human decision and evidence-bound inputs before strict submission checks.
   - Keep compile, claim audit, citation audit, and package readiness separate from draft generation.

3. Orbit-status STOP C next command
   - Status: completed. Prompt 2 routes STOP C from `experiment/experiment_pack.json` formal diagnostics and blocks missing diagnostics instead of suggesting `PLAN_CODE_AUDIT.md`.
   - `tools/orbit_status.py` reports safe STOP C handoffs.
   - The safe next command should point to the human decision step until a valid `HUMAN_DECISION_NOTE.md` exists.

4. Shared references still using old paper-writing / CLAIM_CONSTRUCTION semantics
   - Status: completed. Prompt 3 aligns shared references around `claim_ledger.json`,
     `/paper-draft`, `/paper-from-claims`, and `/submission-package`.
   - Remaining `paper-writing` references describe it as a compatibility router.
   - Remaining `CLAIM_CONSTRUCTION.md` references describe it as a compatibility view or legacy artifact.

5. Mirror drift
   - Status: completed. Prompt 4 syncs `.agents/skills` from canonical and adds mirror policy regression tests.
   - Full mirrors must remain generated from canonical `skills/`; do not edit `.agents/skills` by hand.
   - CI should run `python tools/check_skill_mirror.py --repo .`.

6. Diagnostic session helper missing
   - Status: completed. Prompt 5 adds `tools/diagnostic_session.py` for `diagnostic_id`, `input_hash`, diagnostic context, run updates, and structured audit updates.
   - Keep `/diagnostic-to-review` recoverable without reusing stale fixed-path artifacts.

7. Run-experiment fixed-path diagnostic artifacts
   - Status: completed. Prompt 5 documents `ORBIT_DIAGNOSTIC_ID` / `ORBIT_DIAGNOSTIC_OUTPUT_ROOT` and per-session `RUN_REPORT.md` / `RUN_AUDIT.md` as preferred formal diagnostic outputs.
   - Status: Prompt 11 makes `/run-experiment` treat per-diagnostic output roots as canonical for formal diagnostics while retaining fixed legacy latest copies only for compatibility.
   - Ensure experiment-bridge probes remain separate from formal diagnostic artifacts.

8. G12 semantics consistency
   - Status: completed. Prompt 6 normalizes G12 around `verdict`, `regime_preserved`, and `mechanism_rejected`.
   - Route failed regime checks to diagnostic redesign, not automatic mechanism rejection.

9. Claim ledger negative result semantics
   - Status: completed. Prompt 7 adds `claim_role` and `paper_use` to claim ledger entries and validator checks that unsupported claims cannot become allowed main paper claims.
   - Ensure unsupported or partial claims become structured claim ledger states and STOP C decisions.
   - Do not treat `claim_supported=no` as a default runtime abort unless evidence integrity is invalid.

10. Result-to-claim Codex handoff consistency
    - Status: completed. Prompt 8 aligns `/result-to-claim` with the standalone Codex handoff contract and marks Codex-pending draft ledgers as non-gating.
    - Ensure Codex required remains intact.
    - If Codex MCP/auth/sandbox fails, export a standalone review prompt and require import before marking review complete.

11. Auto-review-loop red-team mode separation
    - Status: completed. Prompt 9 separates generic improvement mode from ORBIT red-team verdict mode and documents that STOP C readiness uses only the final verdict token.
    - Keep research review, claim ledger review, paper claim audit, and red-team STOP C review distinct.
    - Avoid treating red-team prose or scores as equivalent to a structured STOP C verdict.

12. Experiment-bridge formal diagnostic handoff
    - Status: completed. Prompt 12 makes `full-bridge` explicit opt-in only and
      strengthens `experiment_pack.formal_diagnostics[]`.
    - STOP B probes remain implementation/headroom aids; formal diagnostics are routed
      through `/diagnostic-to-review`.

## Baseline Validation Notes

- `tools/check_skill_mirror.py` passes; future nonzero exits indicate new mirror drift.
- Final release details are summarized in `docs/refactor/V2_STABILIZATION_SUMMARY.md`.
