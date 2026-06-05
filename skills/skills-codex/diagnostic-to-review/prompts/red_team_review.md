---
id: diagnostic-to-review.red-team-review.v1
used_by: diagnostic-to-review phase 4
purpose: Run paper-bearing claim red-team review using final verdict tokens, not score-only gates.
inputs:
  - claims/claim_ledger.json
  - diagnostic_id
outputs:
  - RED_TEAM_REVIEW.md
  - parsed final verdict
---

### Phase 4: Red-team Review

Run only for paper-bearing diagnostics where `claims/claim_ledger.json` produced a claim
chain that needs paper-readiness review.

```bash
/auto-review-loop "claims/claim_ledger.json for <diagnostic_id>" -- difficulty: hard -- orbit-red-team: true
```

Write:

```text
orbit-research/diagnostics/<diagnostic_id>/RED_TEAM_REVIEW.md
```

Do not use a numeric score threshold as the happy path. Parse the final
verdict token at the end of `RED_TEAM_REVIEW.md`:

```text
READY_FOR_PAPER
REQUIRES_FIXES
REDESIGN_REQUIRED
HUMAN_DECISION_REQUIRED
```

Only `READY_FOR_PAPER` may be marked paper-ready. Other verdicts produce STOP C review
outcomes and next actions:

| Final verdict | STOP C outcome |
| --- | --- |
| `READY_FOR_PAPER` | Claim chain is red-team ready; still requires human `HUMAN_DECISION_NOTE.md` before paper-writing or scale-up. |
| `REQUIRES_FIXES` | Pause with targeted fixes; write them into `STOP_C_REVIEW.md`. |
| `REDESIGN_REQUIRED` | Pause; route narrowly to diagnostic redesign, mechanism patch, or experiment-pack patch. |
| `HUMAN_DECISION_REQUIRED` | Pause for explicit human decision. |

If Codex-native sub-agent fails in Phase 4, write:

```text
orbit-research/codex-prompts/<diagnostic_id>.phase-4-review.md
```

Then write `awaiting_user_action` state and stop. Do not fabricate
`RED_TEAM_REVIEW.md`.
