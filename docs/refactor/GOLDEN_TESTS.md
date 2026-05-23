# Golden Minimal ORBIT Workflow Tests

The golden fixture at `tests/fixtures/golden_minimal_project/` is a toy project that
exercises the refactored contracts without running experiments, GPUs, network calls, or
external APIs.

It includes:

- `proposal/proposal_pack.json`
- `proposal/PROPOSAL.md`
- `experiment/experiment_pack.json`
- `experiment/EXPERIMENT_PLAN.md`
- `experiment/PROBE_REPORT.md`
- `claims/claim_ledger.json`
- `claims/CLAIM_LEDGER.md`
- `figures/figure_manifest.json`
- `references/citation_cache.json`
- `paper/paper_package.json`
- `orbit-research/ORBIT_STATE.json`

Run the focused regression suite:

```bash
python3 -m unittest tests.test_golden_orbit_workflow
```

Useful direct checks:

```bash
python3 tools/validate_orbit_pack.py --repo tests/fixtures/golden_minimal_project --all
python3 tools/orbit_status.py --repo tests/fixtures/golden_minimal_project --pretty
python3 tools/check_skill_mirror.py --repo . --json
```

The tests cover:

- all canonical packs validate on the golden fixture
- `/orbit-status` tooling reports the expected STOP D state and safe next command
- a ready claim ledger rejects unsupported claims
- figure manifest schema checks catch missing `output` and `status`
- a submission-ready paper package rejects unverified citations
- the mirror checker can emit a machine-readable drift report
