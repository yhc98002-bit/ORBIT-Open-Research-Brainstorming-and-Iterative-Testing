---
name: paper-draft
description: "Fast paper draft or skeleton from a proposal pack, proposal Markdown, narrative report, or notes. Use when the user asks for a quick draft, paper skeleton, rough LaTeX, or wants to explore paper shape without STOP C submission gates."
argument-hint: [proposal-pack-or-notes]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill
---

# /paper-draft

Create a fast draft for: **$ARGUMENTS**

## Purpose

This is the lightweight paper entry. It helps the user get a readable structure,
section skeleton, or rough draft quickly. It is not a submission-readiness path.

## Inputs

Accept any of:

- `proposal/proposal_pack.json`
- `proposal/PROPOSAL.md`
- `refine-logs/FINAL_PROPOSAL.md`
- `NARRATIVE_REPORT.md`
- research notes or a user-supplied topic

Do not require `claims/claim_ledger.json`, `RED_TEAM_REVIEW.md`, or
`orbit-research/HUMAN_DECISION_NOTE.md`.

## Outputs

Write one or both:

- `paper/DRAFT.md` for a readable Markdown draft, outline, or TODO scaffold
- `paper/main.tex` plus `paper/sections/*.tex` when the user asks for LaTeX

Also write `paper/TODOS.md` when important claims, citations, figures, or evidence are
missing.

## Rules

- Unsupported or unverified claims must be marked `TODO(evidence)` or
  `TODO(claim-ledger)`; do not make them sound established.
- Citations may be placeholders only when marked `TODO(citation)`.
- Figures may be placeholders only when marked `TODO(figure)`.
- Do not run `/paper-claim-audit`, `/citation-audit`, `/proof-checker`, or
  submission verification.
- Do not label output submission-ready.

## Suggested Flow

1. Read the supplied proposal, narrative, or notes.
2. Extract the likely paper type, target venue if given, and section structure.
3. Draft `paper/DRAFT.md` first unless the user explicitly asks for LaTeX.
4. If LaTeX is requested, use `/paper-plan` and `/paper-write` as helpers, but keep all
   unsupported content marked as TODO.

## Handoff

- Use `/paper-from-claims "claims/claim_ledger.json"` after STOP C produces a claim
  ledger and the user wants an evidence-bound paper.
- Use `/submission-package "paper/"` only after the draft is ready for strict compile and
  audit packaging.
