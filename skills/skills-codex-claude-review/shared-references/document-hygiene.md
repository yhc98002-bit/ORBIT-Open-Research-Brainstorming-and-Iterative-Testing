# Document Hygiene

Core principle:

A proposal document should not read like a disclaimer, rebuttal, or audit log. A proposal
should present the current research direction clearly. Risks, limitations, negative
results, and historical decisions must be preserved, but they should live in the right
artifact.

Do not erase uncertainty. Do not repeat uncertainty defensively. Move uncertainty to the
correct artifact.

## Layer Map

- `refine-logs/FINAL_PROPOSAL.md`: index, proposal status, critical hypotheses summary,
  next gate. No rebuttal text, audit logs, or historical caveat accumulation.
- `refine-logs/FINAL_PROPOSAL_SHORT.md`: readable pitch: problem, thesis, method, central
  claims, strongest baselines, main risks, next gate.
- `refine-logs/METHOD_SPEC.md`: implementation details, formulas, module boundaries,
  training/inference protocol.
- `orbit-research/ASSUMPTION_LEDGER.md`: central factual, method, benchmark, and
  paper-bearing assumptions and critical hypotheses.
- `orbit-research/RESEARCH_DECISION_LOG.md`: failed/surprising diagnostic classification,
  routing decisions, and proposal status changes.
- `claims/claim_ledger.json`: canonical paper-level claim support, limitations, and
  negative/tie framing.
- `claims/CLAIM_LEDGER.md` and `orbit-research/CLAIM_CONSTRUCTION.md` legacy
  compatibility view: generated/readable views of the claim ledger.
- `orbit-research/RED_TEAM_REVIEW.md`: reviewer concerns and unresolved critique.
- `orbit-research/RUN_LEDGER.jsonl`: canonical factual run provenance.
- `refine-logs/EXPERIMENT_LOG.md`: human-readable run narrative, not factual authority.

## Bloat Signals

- Reviewer objections pasted into `FINAL_PROPOSAL` as defensive paragraphs.
- Repeated caveats that say the same uncertainty in several sections.
- Revision history, round logs, or "we previously tried" narratives in the proposal.
- Claim audit, result interpretation, or red-team review content inside the proposal.
- Deferred-scope ideas that no longer affect the next research decision.

## Rewrite Rule

Move content; do not silently delete it. When a paragraph is true but belongs elsewhere,
replace it in the proposal with a short pointer to the canonical artifact.
