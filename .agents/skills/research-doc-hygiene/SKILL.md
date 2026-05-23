---
name: research-doc-hygiene
description: "Clean ORBIT research documents when FINAL_PROPOSAL or related artifacts have accumulated defensive bloat, repeated caveats, embedded revision history, claim-audit text, or stale deferred-scope material. Moves content to the correct artifact layer instead of deleting it. Use when the user asks for document hygiene, proposal cleanup, defensive bloat removal, or FINAL_PROPOSAL readability repair."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# /research-doc-hygiene

Clean research documents for: **$ARGUMENTS**

## Load First

- `../shared-references/document-hygiene.md`
- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/FINAL_PROPOSAL_SHORT.md`, if present
- `orbit-research/ASSUMPTION_LEDGER.md`, `RESEARCH_DECISION_LOG.md`,
  `CLAIM_CONSTRUCTION.md`, `RED_TEAM_REVIEW.md`, if present

## Checklist

Scan proposal-facing files for:

- defensive rebuttal paragraphs or reviewer-objection replies
- repeated caveats or repeated uncertainty statements
- historical revision logs inside the proposal
- claim audit, result interpretation, or red-team-review content inside the proposal
- stale deferred-scope ideas that do not affect the next research decision

## Rewrite Policy

- Move, do not silently delete.
- Keep `FINAL_PROPOSAL.md` as an index and `FINAL_PROPOSAL_SHORT.md` as the readable pitch.
- Move failed/surprising diagnostic history to `RESEARCH_DECISION_LOG.md`.
- Move paper-claim support and limitations to `CLAIM_CONSTRUCTION.md`.
- Move reviewer concerns to `RED_TEAM_REVIEW.md`.
- Move assumption tracing to `ASSUMPTION_LEDGER.md`.
- Replace moved proposal text with a short pointer only when the pointer helps navigation.

## Output

Write `refine-logs/DOC_HYGIENE_REPORT.md` with:

- verdict line: `PASS` / `NEEDS_CLEANUP` / `ROLE_CONFUSION` / `DEFENSIVE_BLOAT`
- files inspected
- bloat found
- content moved and destination artifact
- content left in place with rationale
- follow-up actions, if any

The verdict is advisory. It is not a hard gate; use it to decide whether to clean the
document now or defer cleanup until the next proposal revision.
