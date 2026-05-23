# STOP A Migration

STOP A now uses `proposal/proposal_pack.json` as the canonical proposal artifact.
Markdown remains readable, but it is a view or compatibility layer.

## New Source Of Truth

`/idea-to-proposal` should write:

```text
proposal/proposal_pack.json
```

The pack carries the scientific structure that was previously spread across many
first-class Markdown files:

- `problem_selection`
- `assumptions`
- `abstract_task`
- `baseline_headroom`
- `candidate_mechanisms`
- `selected_sketch`
- `open_risks`

The helper surface is in `tools/orbit_pack.py`. It can create/update a proposal
pack and render Markdown views from it.

## Markdown Views

Primary human-readable views:

- `proposal/PROPOSAL.md`
- `proposal/METHOD_SPEC.md` when implementation-level detail is useful at STOP A

Legacy compatibility views may still be written:

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/FINAL_PROPOSAL_SHORT.md`
- `refine-logs/METHOD_SPEC.md`
- existing `orbit-research/*.md` grounding and innovation artifacts

These files remain useful for people and older tools, but they are not the
canonical AI resume/gate source once `proposal/proposal_pack.json` exists.

## STOP A State

At the STOP A terminal checkpoint, `/idea-to-proposal` should write
`orbit-research/ORBIT_STATE.json` with:

```json
{
  "schema_version": "0.1",
  "current_stop": "STOP_A",
  "current_skill": "idea-to-proposal",
  "current_phase": "phase-5-summary",
  "status": "paused",
  "pause_reason": "stop_review",
  "blockers": [],
  "canonical_packs": {
    "proposal_pack": "proposal/proposal_pack.json",
    "experiment_pack": "experiment/experiment_pack.json",
    "claim_ledger": "claims/claim_ledger.json",
    "paper_package": "paper/paper_package.json"
  },
  "legacy_artifacts_detected": [
    "refine-logs/FINAL_PROPOSAL.md"
  ],
  "safe_next_command": "/experiment-bridge \"proposal/proposal_pack.json\"",
  "updated_at": "2026-05-23T00:00:00Z"
}
```

`/orbit-status` also recognizes `proposal/proposal_pack.json` directly when
`ORBIT_STATE.json` is absent and reports STOP A as paused for review.

## Compatibility Boundary

This prompt does not change `/experiment-bridge`. The new documented next
command is:

```text
/experiment-bridge "proposal/proposal_pack.json"
```

Experiment-bridge support for pack input lands in a later migration. Until then,
legacy callers may still use `refine-logs/FINAL_PROPOSAL.md`, but STOP A should
keep that file synchronized as a view of the pack.
