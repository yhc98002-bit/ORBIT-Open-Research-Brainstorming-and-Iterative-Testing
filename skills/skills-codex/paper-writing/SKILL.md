---
name: paper-writing
description: "Compatibility router for the old all-in-one paper-writing workflow. Prefer /paper-draft for quick drafts, /paper-from-claims for evidence-bound papers from claims/claim_ledger.json, and /submission-package for strict compile/audit/submission packaging."
argument-hint: [paper-input-or-paper-directory]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill
---

# /paper-writing Compatibility Router

Route the paper request for: **$ARGUMENTS**

## Preferred Public Entries

Use these instead of the old overloaded `/paper-writing` surface:

| User intent | Preferred skill |
| --- | --- |
| Fast draft, outline, skeleton, rough LaTeX, notes-to-paper | `/paper-draft` |
| Evidence-bound paper after STOP C approval | `/paper-from-claims` |
| Final compile, audits, proof/citation/claim assurance, submission package after STOP C approval | `/submission-package` |

## Routing Rules

Load and follow [routing_decision.md](prompts/routing_decision.md). Route by the user's
requested outcome first: quick drafts go to `/paper-draft`, evidence-bound STOP C writing
goes to `/paper-from-claims`, strict assurance goes to `/submission-package`, and only
explicit legacy requests use the old one-shot chain.

Legacy STOP C readiness still requires `orbit-research/RED_TEAM_REVIEW.md`  *(must end `READY_FOR_PAPER`) and `orbit-research/HUMAN_DECISION_NOTE.md` ending `PROCEED` before treating the handoff as paper-ready.

For `/paper-from-claims`, run:

```bash
python tools/check_stop_c_approval.py --repo . --claim-ledger claims/claim_ledger.json
```

If the checker blocks, route to `/paper-draft "claims/claim_ledger.json"` for an
unaudited draft or tell the user to review `STOP_C_REVIEW.md` and write
`orbit-research/HUMAN_DECISION_NOTE.md` ending `PROCEED`.

## Compatibility Notes

The old `/paper-writing` mixed drafting, claim gates, audits, compilation, and submission
readiness. That behavior is retained only for backward compatibility. New ORBIT flows
should use:

```text
/paper-draft "<proposal or notes>"
/paper-from-claims "claims/claim_ledger.json"  # only after STOP C approval
/submission-package "paper/"                  # only after STOP C approval for claim-bearing papers
```

## Guardrail

Do not force draft users through submission gates. Do not let submission users miss the
strict audit/package step. Do not imply `/paper-writing` can bypass STOP C approval for
claim-bearing paper generation or submission readiness. When in doubt, route by the
user's requested outcome rather than by artifact presence alone.
