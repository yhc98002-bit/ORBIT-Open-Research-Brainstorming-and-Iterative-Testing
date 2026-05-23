# Output Manifest Protocol

After writing any output file, append an entry to `MANIFEST.md` in the project root.

## Format

If `MANIFEST.md` does not exist, create it with this header:

```markdown
# Research Output Manifest

> Auto-maintained by ORBIT skills. Tracks all generated artifacts across the research lifecycle.

| Timestamp | Skill | File | Stage | Description |
|-----------|-------|------|-------|-------------|
```

Then append one row per output file written:

```
| 2025-06-15 14:30 | /idea-creator | idea-stage/IDEA_REPORT.md | discovery | 12 ideas generated from "LLM reasoning" direction |
| 2025-06-15 14:30 | /idea-to-proposal | orbit-research/ASSUMPTION_LEDGER.md | grounding | central assumptions and critical hypotheses |
| 2025-06-15 14:30 | /run-experiment | orbit-research/RUN_LEDGER.jsonl | experiment-run | appended run-start/run-final records |
```

## Stage Values

| Stage | Skills |
|-------|--------|
| `discovery` | /idea-discovery, /idea-creator, /research-lit, /novelty-check, /research-review |
| `grounding` | /idea-to-proposal, /research-pipeline stages 4/5/7, assumption/baseline/problem-selection artifacts |
| `innovation` | /idea-to-proposal stages 8/9/10, /research-refine, /research-refine-pipeline |
| `validation` | /experiment-plan, /experiment-bridge, /experiment-audit, plan-code and diagnostic design artifacts |
| `experiment-run` | /run-experiment, /experiment-queue, /monitor-experiment |
| `interpretation` | /analyze-results, /diagnostic-to-review, RESULT_INTERPRETATION and RESEARCH_DECISION_LOG |
| `claim` | /result-to-claim, /auto-review-loop, CLAIM_CONSTRUCTION and RED_TEAM_REVIEW |
| `paper` | /paper-writing, /paper-write, /paper-compile |
| `maintenance` | /proposal-revise, /research-doc-hygiene, state cleanup, manifest repair |

Backward-compatible legacy values may appear in older manifests:

- `idea-discovery` -> `discovery`
- `implementation` -> `innovation`, `validation`, or `experiment-run` depending on artifact
- `review` -> `claim` for research claim review, or `paper` for paper review loops

## Pre-flight Check

Before writing output, if the skill depends on a prerequisite file from a previous stage:
1. Check if the prerequisite file exists at its expected stage-scoped path (e.g., `idea-stage/IDEA_REPORT.md`, `review-stage/AUTO_REVIEW.md`)
2. If not found at the stage-scoped path, check the legacy root-level path (e.g., `./IDEA_REPORT.md`, `./AUTO_REVIEW.md`) — see [Path Fallback Rule](output-versioning.md#path-fallback-rule-backward-compatibility)
3. If not found at either path, warn: "⚠️ Expected {file} (from {skill}) but not found. Run {skill} first?"
4. Do not block — the user may have the file elsewhere or want to proceed anyway
