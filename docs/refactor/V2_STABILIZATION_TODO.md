# ORBIT v2 Stabilization TODO

Generated for the v2 stabilization baseline refresh. This file records known
stabilization areas only; it does not change workflow behavior.

## Current Baseline

- Canonical skills: 77
- All `SKILL.md` files: 254
- `skills/skills-codex` full mirror status: no drift detected by the baseline audit
- `.agents/skills` full mirror status: drift remains in 3 skills
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
   - Confirm `tools/orbit_status.py` reports the safe STOP C handoff.
   - The safe next command should point to the human decision step until a valid `HUMAN_DECISION_NOTE.md` exists.

4. Shared references still using old paper-writing / CLAIM_CONSTRUCTION semantics
   - Audit shared references for stale `paper-writing` and `CLAIM_CONSTRUCTION.md` language.
   - Replace stale source-of-truth language with `claim_ledger.json` and the split paper paths where appropriate.

5. Mirror drift
   - `python tools/check_skill_mirror.py --repo .` currently reports unexpected `.agents/skills` drift in:
     - `auto-paper-improvement-loop`
     - `novelty-check`
     - `research-review`
   - Do not edit `.agents/skills` by hand; resolve through the documented mirror policy or sync tooling in a dedicated prompt.

6. Diagnostic session helper missing
   - Add or document helper support for `diagnostic_id`, `input_hash`, diagnostic context, and per-diagnostic artifact paths.
   - Keep `/diagnostic-to-review` recoverable without reusing stale fixed-path artifacts.

7. Run-experiment fixed-path diagnostic artifacts
   - Audit `/run-experiment` for old `DIAGNOSTIC_RUN_REPORT.md` and `DIAGNOSTIC_RUN_AUDIT.md` fixed-path assumptions.
   - Ensure experiment-bridge probes remain separate from formal diagnostic artifacts.

8. G12 semantics consistency
   - Ensure regime-check semantics consistently distinguish `regime_preserved=false` from mechanism rejection.
   - Route failed regime checks to diagnostic redesign, not automatic mechanism rejection.

9. Claim ledger negative result semantics
   - Ensure unsupported or partial claims become structured claim ledger states and STOP C decisions.
   - Do not treat `claim_supported=no` as a default runtime abort unless evidence integrity is invalid.

10. Result-to-claim Codex handoff consistency
    - Ensure Codex required remains intact.
    - If Codex MCP/auth/sandbox fails, export a standalone review prompt and require import before marking review complete.

11. Auto-review-loop red-team mode separation
    - Keep research review, claim ledger review, paper claim audit, and red-team STOP C review distinct.
    - Avoid treating red-team prose or scores as equivalent to a structured STOP C verdict.

## Baseline Validation Notes

- `tools/check_skill_mirror.py` is expected to fail until `.agents/skills` drift is resolved.
- This baseline refresh intentionally does not fix mirror drift, schema issues, skill behavior, or shared-reference semantics.
