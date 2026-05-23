---
name: paper-from-claims
description: "Evidence-bound paper generation from claims/claim_ledger.json, optionally using figures/figure_manifest.json and references/citation_cache.json. Use after STOP C when the user wants a paper draft constrained by validated claims."
argument-hint: [claims/claim_ledger.json]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill
---

# /paper-from-claims

Generate an evidence-bound paper from: **$ARGUMENTS**

## Purpose

This is the STOP C to paper-writing handoff. The claim ledger is the source of truth; the
paper may explain and organize claims, but it must not invent new main claims.

## Required Input

- `claims/claim_ledger.json`

Optional support packs:

- `figures/figure_manifest.json`
- `references/citation_cache.json`
- `paper/PAPER_PLAN.md` if a plan already exists

When present, `figures/figure_manifest.json` and `references/citation_cache.json` are
first-class paper inputs. Do not discover figures by scanning `figures/` ad hoc until the
manifest has been read; do not build bibliography entries from search snippets when the
citation cache has verified metadata.

## Outputs

Write an evidence-bound paper draft under `paper/`:

- `paper/main.tex`
- `paper/sections/*.tex`
- `paper/references.bib` when citations are available
- `paper/CLAIM_TRACE.md` mapping each paper claim to ledger claim IDs

Compilation is useful but not the gate here. Strict submission assurance belongs to
`/submission-package`.

## Claim Rules

- Every main contribution, abstract claim, introduction contribution bullet, result claim,
  and conclusion claim must map to one or more `claim_ledger.claims[].id` values.
- Do not create new main claims that are absent from `claims/claim_ledger.json`.
- `unsupported` claims may appear only in limitations, negative-result discussion, or
  future work if allowed by `allowed_paper_sections`.
- `exploratory` claims must be labeled as exploratory and not pre-planned.
- Honor every `forbidden_overclaims` entry.
- Keep wording within each claim's `scope` and `limitations`.

## Figure And Citation Rules

- If `figures/figure_manifest.json` exists, every figure/table included in the paper must
  come from a manifest entry. Use `supports_claims`, `data_source`, `generator`, `output`,
  `latex_label`, and `status` to decide placement. Do not include entries marked
  `needs_redesign` except as TODOs.
- If `references/citation_cache.json` exists, build `paper/references.bib` and citation
  contexts from cache entries. Prefer `verified: true` entries. Unverified entries may be
  cited only with TODO/VERIFY markers unless the user explicitly accepts the risk.
- Missing figures or citations become TODOs, not invented evidence.

## Suggested Flow

1. Validate or at least parse `claims/claim_ledger.json`.
2. Read `figures/figure_manifest.json` and `references/citation_cache.json` when present.
3. Build `paper/CLAIM_TRACE.md` before drafting prose.
4. Run `/paper-plan "claims/claim_ledger.json"` to create or update the outline.
5. Run `/paper-write "paper/PAPER_PLAN.md"` or draft directly from the claim trace.
6. Optionally run `/paper-compile "paper/"` for a build check.

## Handoff

When the draft is ready for assurance, run:

```text
/submission-package "paper/"
```
