# ORBIT Pack Contracts

The pack layer introduces machine-readable JSON sources of truth for ORBIT while
keeping existing Markdown artifacts readable during migration.

## Principle

JSON is the source of truth. Markdown is a view.

Legacy Markdown files are not deleted by this migration. During the transition,
skills and tools may read old Markdown artifacts to bootstrap packs, but new
state, gates, resume decisions, and cross-skill handoffs should move toward the
canonical JSON packs.

## Canonical Packs

| Stop | Pack | Path | Schema |
| --- | --- | --- | --- |
| STOP A | Proposal pack | `proposal/proposal_pack.json` | `schemas/proposal_pack.schema.json` |
| STOP B | Experiment pack | `experiment/experiment_pack.json` | `schemas/experiment_pack.schema.json` |
| STOP C | Claim ledger | `claims/claim_ledger.json` | `schemas/claim_ledger.schema.json` |
| STOP D | Paper package | `paper/paper_package.json` | `schemas/paper_package.schema.json` |
| Support | Figure manifest | `figures/figure_manifest.json` | `schemas/figure_manifest.schema.json` |
| Support | Citation cache | `references/citation_cache.json` | `schemas/citation_cache.schema.json` |

Every pack includes:

```json
{
  "schema_version": "0.1",
  "status": "draft",
  "updated_at": "2026-05-23T00:00:00Z",
  "source_markdown": [],
  "generated_views": []
}
```

Allowed pack statuses are:

- `draft`
- `ready`
- `blocked`
- `deprecated`

Unknown fields are allowed. This is intentional so the old Markdown-heavy
pipeline can migrate incrementally.

## Minimum Contents

`proposal/proposal_pack.json` records:

- `problem_selection`
- `assumptions`
- `abstract_task`
- `baseline_headroom`
- `candidate_mechanisms`
- `selected_sketch`
- `open_risks`

`experiment/experiment_pack.json` records:

- `proposal_ref`
- `decision_tree`
- `controls`
- `null_result_contract`
- `component_ladder`
- `algorithmic_formalization`
- `probes`
- `formal_diagnostics`

`claims/claim_ledger.json` records:

- `claims`
- `result_refs`

Each claim should include `id`, `statement`, `status`, `evidence_refs`,
`controls`, `scope`, `limitations`, `forbidden_overclaims`, and
`allowed_paper_sections`. Valid claim support statuses are `supported`,
`partial`, `unsupported`, and `exploratory`.

`figures/figure_manifest.json` records `figures`. Each figure should include
`id`, `type`, `supports_claims`, `data_source`, `generator`, `output`,
`latex_label`, and `status`. Valid figure statuses are `draft`, `verified`, and
`needs_redesign`.

`references/citation_cache.json` records `citations`. Each citation should
include `key`, `title`, `authors`, `venue`, `year`, `source`, `verified`,
`used_for`, and `contexts`.

`paper/paper_package.json` records:

- `claim_ledger_ref`
- `figure_manifest_ref`
- `citation_cache_ref`
- `compile_status`
- `audits`

## Markdown During Migration

Old Markdown artifacts remain useful as:

- human-readable views;
- migration inputs;
- audit trails;
- generated summaries for review.

They should stop being the only gate source once the corresponding pack exists.
For example, after `claims/claim_ledger.json` exists, claim status should be read
from the ledger, while `CLAIM_CONSTRUCTION.md` becomes a legacy compatibility view.

`source_markdown` lists Markdown or text artifacts used to create the pack.
`generated_views` lists Markdown views generated from the pack.

## Tools

Validate all canonical pack paths:

```bash
python tools/validate_orbit_pack.py --repo . --all
```

Missing packs are warnings, not fatal errors. Existing pack files are validated
against the schema subset supported by the standard-library validator.

Bootstrap a draft pack from legacy Markdown inventory without perfect parsing:

```bash
python tools/orbit_pack.py bootstrap --repo . --pack proposal_pack --write
```

The bootstrap helper records source paths and snippets under `legacy_bootstrap`.
It does not claim to understand all legacy prose.
