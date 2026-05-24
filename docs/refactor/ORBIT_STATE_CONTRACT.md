# ORBIT_STATE Contract

`ORBIT_STATE.json` is the lightweight unified read model for ORBIT pipeline
status. It lives at:

```text
orbit-research/ORBIT_STATE.json
```

The JSON schema is [schemas/orbit_state.schema.json](../../schemas/orbit_state.schema.json).

## Purpose

ORBIT currently spreads resume state across legacy `STATE.json` files, Markdown
verdict artifacts, manifests, and human decision notes. `ORBIT_STATE.json` gives
tools one place to read:

- the current STOP;
- whether work is in progress, paused, blocked, or complete;
- blocker IDs and artifacts;
- the safest next command.

This contract is additive. Existing skills are not required to write
`ORBIT_STATE.json` yet.

## Stops

| Stop | Meaning |
| --- | --- |
| `NONE` | No ORBIT pipeline state is detected yet. |
| `STOP_A` | Proposal construction and refinement. |
| `STOP_B` | Proposal to experiment plan/code/audit bridge. |
| `STOP_C` | Diagnostic execution, result interpretation, claim construction, red-team review. |
| `STOP_D` | Paper writing and submission packaging. |
| `COMPLETED` | A paper package or equivalent final package is complete. |

## Required Fields

Every state object uses `schema_version: "0.1"` and includes:

- `current_stop`
- `current_skill`
- `current_phase`
- `status`
- `pause_reason`
- `blockers`
- `canonical_packs`
- `legacy_artifacts_detected`
- `safe_next_command`
- `updated_at`

`pause_reason` includes ordinary STOP waits plus recoverable Codex transport states:
`stop_review`, `missing_prereq`, `gate_failed`, `codex_review_needed`,
`codex_review_imported`, `ambiguous_resume`, `external_dependency`, or `null`.

Blockers use:

- `id`: gate or state identifier, such as `G11`;
- `kind`: `missing_artifact`, `bad_verdict`, `codex_unavailable`, `stale_state`, or `legacy_conflict`;
- `artifact`: the artifact that explains the blocker;
- `message`: short human-readable cause;
- `safe_next_command`: the safest command to run next, or `null`.

## Status Inference

`tools/orbit_status.py` is read-only. It first reads
`orbit-research/ORBIT_STATE.json` if present. If missing, it infers a compatible
state from legacy artifacts including:

- `orbit-research/IDEA_TO_PROPOSAL_STATE.json`
- `orbit-research/DIAGNOSTIC_TO_REVIEW_STATE.json`
- `refine-logs/REFINE_STATE.json`
- `orbit-research/PLAN_CODE_AUDIT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`
- `orbit-research/CLAIM_CONSTRUCTION.md`
- `orbit-research/RED_TEAM_REVIEW.md`
- `orbit-research/HUMAN_DECISION_NOTE.md`

Verdict parsing is conservative. Known positive verdicts advance the STOP.
Known negative verdicts produce `status: blocked` and `pause_reason:
gate_failed`. Missing or unclear verdicts produce `ambiguous_resume`, not
success.

## CLI

```bash
python tools/orbit_status.py --repo . --pretty
python tools/orbit_status.py --repo . --json
```

The `/orbit-status` skill delegates to this tool and does not duplicate gate
rules.
