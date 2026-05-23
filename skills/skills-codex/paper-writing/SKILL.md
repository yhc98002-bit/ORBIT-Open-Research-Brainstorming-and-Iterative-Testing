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
| Evidence-bound paper after STOP C claim ledger exists | `/paper-from-claims` |
| Final compile, audits, proof/citation/claim assurance, submission package | `/submission-package` |

## Routing Rules

Load and follow [routing_decision.md](prompts/routing_decision.md). Route by the user's
requested outcome first: quick drafts go to `/paper-draft`, evidence-bound STOP C writing
goes to `/paper-from-claims`, strict assurance goes to `/submission-package`, and only
explicit legacy requests use the old one-shot chain.

Legacy STOP C readiness still requires `orbit-research/RED_TEAM_REVIEW.md`  *(must end `READY_FOR_PAPER`) before treating the handoff as paper-ready.

## Compatibility Notes

The old `/paper-writing` mixed drafting, claim gates, audits, compilation, and submission
readiness. That behavior is retained only for backward compatibility. New ORBIT flows
should use:

```text
/paper-draft "<proposal or notes>"
/paper-from-claims "claims/claim_ledger.json"
/submission-package "paper/"
```

## Guardrail

Do not force draft users through submission gates. Do not let submission users miss the
strict audit/package step. When in doubt, route by the user's requested outcome rather
than by artifact presence alone.
