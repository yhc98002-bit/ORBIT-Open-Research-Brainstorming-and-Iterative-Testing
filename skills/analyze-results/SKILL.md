---
name: analyze-results
description: Analyze ML experiment results, compute statistics, generate comparison tables and insights. Use when user says "analyze results", "compare", or needs to interpret experimental data.
argument-hint: [results-path-or-description]
allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit, Agent
---

# Analyze Experiment Results

Analyze: $ARGUMENTS

## ORBIT Result Interpretation Gate

This gate is always-on. Load `shared-references/research-agent-pipeline.md` before analysis.
Also load `shared-references/run-ledger.md` and read
`orbit-research/RUN_LEDGER.jsonl` when present.
Do not stop at comparison tables. Run `mkdir -p orbit-research/`, then write or update
`orbit-research/RESULT_INTERPRETATION.md` with:

- ledger coverage: which `run_id`s were analyzed, missing, failed, or orphaned
- expected vs observed result
- whether the expected signal appeared
- supported and weakened hypotheses
- most likely explanation and alternatives
- whether the issue is mechanism, benchmark, baseline ceiling, implementation, evaluation,
  task ontology, hyperparameters, or missing control
- the next diagnostic experiment
- decision: continue, narrow, redesign, re-read literature, change benchmark, change control, or stop

The next experiment must depend on this interpretation.

## Workflow

### Step 1: Locate Results and Verify Provenance
Find all relevant JSON/CSV result files:
- Check `figures/`, `results/`, or project-specific output directories
- Parse JSON results into structured data

Before computing metrics, verify that result files correspond to
`orbit-research/RUN_LEDGER.jsonl` entries:

- Match each result file to a `run_id` by explicit `run_id` field, path in a `run-final`
  `result_files` list, W&B run id, or command/config/seed match.
- Warn if a result file is older than its matching `timestamp_start`.
- Warn if a result file has no matching `run_id` (orphan result).
- Warn if multiple ledger runs claim the same result file (duplicate result).
- Report expected seeds/jobs with terminal ledger status `failed`, `oom`, `timeout`,
  `killed`, `no_result`, or `partial`; do not silently ignore them.
- Report missing seeds/config cells by comparing the experiment plan / queue manifest /
  ledger start records against final records and discovered results.

Write a `## Ledger Coverage` section in `RESULT_INTERPRETATION.md`:

```markdown
## Ledger Coverage
| run_id | seed/config | ledger status | result files | included in metrics? | notes |
|---|---|---|---|---|---|
| run_... | seed=42 | completed | results/x.json | yes | |
| run_... | seed=43 | oom | none | no | counted as failed run |

Warnings:
- [orphan / stale / duplicate / missing seed warning]
```

### Step 2: Build Comparison Table
Organize results by:
- **Independent variables**: model type, hyperparameters, data config
- **Dependent variables**: primary metric (e.g., perplexity, accuracy, loss), secondary metrics
- **Delta vs baseline**: always compute relative improvement

### Step 3: Statistical Analysis
- If multiple seeds: report mean +/- std, check reproducibility
- If sweeping a parameter: identify trends (monotonic, U-shaped, plateau)
- Flag outliers or suspicious results

### Step 4: Generate Insights
For each finding, structure as:
1. **Observation**: what the data shows (with numbers)
2. **Interpretation**: why this might be happening
3. **Implication**: what this means for the research question
4. **Next step**: what experiment would test the interpretation

### Step 5: Update Documentation
If findings are significant:
- Propose updates to project notes or experiment reports
- Draft a concise finding statement (1-2 sentences)

## Output Format
Always include:
1. Raw data table
2. Key findings (numbered, concise)
3. Suggested next experiments (if any)
