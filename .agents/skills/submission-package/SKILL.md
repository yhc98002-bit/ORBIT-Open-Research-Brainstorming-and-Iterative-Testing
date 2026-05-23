---
name: submission-package
description: "Strict submission package builder for paper/. Runs or requests compile, paper claim audit, citation audit, proof audit when relevant, and writes paper/paper_package.json. Use when the user asks for submission readiness, final checks, camera-ready package, or assurance."
argument-hint: [paper-directory]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, Skill
---

# /submission-package

Build a strict submission package for: **$ARGUMENTS**

## Purpose

This is the assurance path. It does not invent paper content. It compiles, audits, records
verdicts, and writes the machine-readable STOP D package.

## Inputs

Required:

- `paper/` with `main.tex`

Expected when the paper is claim-bearing:

- `claims/claim_ledger.json`
- `figures/figure_manifest.json` when generated figures are used
- `references/citation_cache.json` when a citation cache exists

## Required Outputs

- `paper/main.pdf` or a compile failure record
- `paper/PAPER_CLAIM_AUDIT.json` and `paper/PAPER_CLAIM_AUDIT.md`
- `paper/CITATION_AUDIT.json` and `paper/CITATION_AUDIT.md`
- proof audit artifacts when the paper contains theorem/proof content
- `paper/paper_package.json`

`paper/paper_package.json` must follow `schemas/paper_package.schema.json`:

```jsonc
{
  "schema_version": "0.1",
  "status": "draft|ready|blocked|deprecated",
  "updated_at": "<ISO-8601 UTC>",
  "source_markdown": [],
  "generated_views": [],
  "claim_ledger_ref": "claims/claim_ledger.json",
  "figure_manifest_ref": "figures/figure_manifest.json",
  "citation_cache_ref": "references/citation_cache.json",
  "compile_status": {},
  "audits": []
}
```

## Workflow

1. Run or request `/paper-compile "paper/"`.
2. Run `/paper-claim-audit "paper/"`.
3. Run `/citation-audit "paper/"`.
4. If theorem, lemma, proof, derivation, or formal guarantee content exists, run
   `/proof-checker "paper/"` or record why proof audit is not applicable.
5. If `tools/verify_paper_audits.sh` exists, run it and record the result.
6. Write `paper/paper_package.json`.

## Status Rules

- `ready`: compile succeeds and required audits are `PASS` or accepted `WARN`.
- `blocked`: compile fails, an audit is `FAIL`, `BLOCKED`, or `ERROR`, or required input
  evidence is missing.
- `draft`: checks ran but the user has not requested strict submission finalization.
- `deprecated`: package is stale relative to changed paper or pack inputs.

## Key Rules

- Do not silently skip audits. If an audit is not applicable, write a machine-readable
  `NOT_APPLICABLE` record.
- If `claims/claim_ledger.json` is absent for a claim-bearing paper, record a blocker; do
  not claim full rigor.
- Do not mutate scientific claims except for mechanical audit fixes approved by the user.
- Do not label the package submission-ready unless `paper/paper_package.json.status` is
  `ready`.
