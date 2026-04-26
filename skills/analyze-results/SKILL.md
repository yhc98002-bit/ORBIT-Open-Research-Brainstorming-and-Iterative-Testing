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
Do not stop at comparison tables. Run `mkdir -p orbit-research/`, then write or update
`orbit-research/RESULT_INTERPRETATION.md` with:

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

### Step 1: Locate Results
Find all relevant JSON/CSV result files:
- Check `figures/`, `results/`, or project-specific output directories
- Parse JSON results into structured data

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
