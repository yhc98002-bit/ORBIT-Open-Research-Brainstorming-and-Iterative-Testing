# Better BRIS Harness Prompts

Use these prompts as canonical stage harnesses. Skills may add file paths, output paths, and
project-local constraints, but should preserve the scientific checks.

## 0A. Seed Framing

```text
You are given a research area, not yet a concrete research problem.

Do not propose final methods yet.
Do not commit to a benchmark yet.
Do not write an experiment plan yet.

First produce a Seed Framing brief:
1. What is the research area?
2. What are the user's constraints: compute, data, timeline, expertise, and publication target?
3. What are 3-5 initial research questions?
4. What are the key terms, subfields, and adjacent areas to search?
5. What kinds of papers must be read first: survey, benchmark, recent SOTA, foundation, analysis/negative/ablation, and closest baseline papers?

Output a search-oriented brief, not a proposal.
```

## 1. Question-driven Literature Map

```text
Read papers as a research scientist, not as a summarizer.

For each important paper, extract:
1. main claim;
2. mechanism;
3. benchmark;
4. strongest evidence;
5. weakest assumption;
6. missing control;
7. likely failure regime;
8. claim-evidence gap;
9. follow-up question for our project.

Then synthesize:
- field consensus;
- unresolved bottlenecks;
- overclaimed assumptions;
- benchmark saturation risks;
- missing controls across the field;
- promising underexplored regimes;
- candidate research problems.

Do not generate final methods yet. Generate candidate problems.
```

## 0B. Problem Taste / Problem Selection

```text
Now that the literature map exists, select the most promising concrete research problem.

For each candidate problem, evaluate:
1. importance;
2. audience;
3. concreteness;
4. novelty;
5. feasibility with our data, compute, time, and expertise;
6. benchmark availability;
7. baseline ceiling risk;
8. expected headroom;
9. diagnostic clarity;
10. paper value if the method fails or ties.

Do not select a problem only because it sounds novel.

Select the problem with the best combination of importance, feasibility, headroom, diagnostic clarity, and paper survivability.

End with one of:
PROCEED / NARROW / RETHINK.
```

## 2. Task Ontology / Data Audit

```text
Before method design, perform a Task Ontology and Data Audit.

Define:
1. prediction target;
2. inputs;
3. labels;
4. data units: patient, eye, visit, image, sequence, report;
5. modalities;
6. vendors and devices;
7. acquisition protocols;
8. domains;
9. train / validation / test splits;
10. confounders.

Actively search for category errors:
- vendor treated as modality;
- modality treated as domain;
- dataset source treated as clinical label;
- binary split hiding a multi-modal or multi-domain problem;
- disease label confounded with device or protocol;
- patient leakage across splits;
- shortcut features that make the benchmark artificial.

If ontology is ambiguous, stop and produce:
- concern;
- why it matters;
- possible fixes;
- recommended next step.

Do not proceed to method design until the task ontology is stable enough.
```

## 3. Baseline Ceiling / Headroom Audit

```text
Before testing any proposed method, estimate the simplest strong baseline ceiling.

Identify the relevant simple strong baselines:
- zero-shot prompting;
- few-shot prompting;
- Best-of-N sampling;
- confidence-rank selection;
- reranking baseline;
- DINGO-style search or selection;
- vanilla GRPO / PPO / RL;
- vanilla SFT;
- ERM baseline;
- modality-specific baseline;
- majority-domain baseline;
- heuristic or rule-based baseline;
- known public SOTA if available.

Answer:
1. What is the simplest strong baseline?
2. What is its known or estimated ceiling?
3. Is the benchmark already saturated?
4. Where is the largest remaining headroom?
5. Which subset, split, or regime should be tested first?
6. Which baseline must run before the proposed method?
7. If the baseline is too strong, should we change benchmark, metric, split, target regime, or paper claim?

Do not run the proposed method before baseline ceiling is known or explicitly estimated.
```

## 4. Hypothesis-Mechanism-Benchmark-Control Matrix

```text
Before writing an experiment plan, fill the Hypothesis-Mechanism-Benchmark-Control Matrix.

For each proposed experiment, specify:
1. Hypothesis: What scientific claim is being tested?
2. Mechanism: What mechanism should make the method work?
3. Target failure mode: What failure mode of existing methods does this mechanism address?
4. Benchmark: Why should this benchmark expose the mechanism?
5. Highest-headroom regime: In which subset or regime should the mechanism help most?
6. Required controls: Which controls isolate the mechanism?
7. Possible confounders: What else could explain success or failure?
8. Positive signal: What result would support the hypothesis?
9. Falsifying signal: What result would weaken or falsify the hypothesis?

Reject experiments where hypothesis, mechanism, benchmark, and controls could all be wrong at the same time.

Do not proceed with non-diagnostic experiments.
```

## 5. Null-result Contract

```text
Before running the experiment, write a Null-Result Contract.

Answer:
1. If the result is positive, what exactly do we learn?
2. If the result is negative, what exactly do we learn?
3. If the method ties the control, what exactly do we learn?
4. If results are noisy, unstable, or chaotic, what are the top possible causes?
5. Which causes must this experiment be able to distinguish?
   - mechanism failure;
   - benchmark saturation;
   - baseline too strong;
   - implementation bug;
   - evaluation metric mismatch;
   - missing control;
   - data/task ontology problem;
   - hyperparameter or convergence issue.
6. What follow-up diagnostic experiment would distinguish these causes?
7. What is the stop condition?

If the null result only says:
"We do not know whether the mechanism, benchmark, implementation, or evaluation failed,"
then the experiment is invalid.

Redesign the experiment before running.
```

## 6. Progressive Component Ladder

```text
Bold mechanisms and complex systems are welcome, but build them progressively.

Create a Progressive Component Ladder.

Start with:
Component 0: simplest strong baseline

Then add one component at a time.

For each component, specify:
1. Component name: What is being added?
2. Target failure mode: What problem does this component address?
3. Expected signal: What metric, subset, or behavior should improve?
4. Control: What comparison isolates this component?
5. Null-result interpretation: If this component does not help, what does that mean?
6. Rollback condition: When should this component be removed or redesigned?
7. Interaction risk: Could this component hide or confound the effect of another component?

Do not run the full system until each major component has shown at least one of:
- measurable performance gain;
- attribution value;
- diagnostic insight.

A complex method is allowed only if its complexity is progressively justified.
```

## 7. Minimal Diagnostic Experiment Design

```text
Before full-scale experiments, design the smallest diagnostic experiment.

This experiment should answer:
1. Does the mechanism have any signal?
2. Does the metric detect the intended improvement?
3. Does the baseline actually fail in this regime?
4. Does the control isolate the component?
5. Can we reproduce a known baseline?
6. Can the implementation pass basic sanity checks?
   - data loading;
   - label alignment;
   - metric range;
   - tiny overfit;
   - deterministic small run;
   - known baseline reproduction.
7. Is this experiment cheap enough to run before full GPU scaling?

Do not run broad grids or expensive experiments before this diagnostic experiment.
```

## 7.5. Plan-Code Consistency Audit

```text
You are not reviewing this code for syntax or style.

You are reviewing whether the implementation faithfully matches the research plan.

Compare the code against:
1. FINAL_PROPOSAL.md
2. EXPERIMENT_PLAN.md
3. BASELINE_CEILING.md
4. CONTROL_DESIGN.md
5. NULL_RESULT_CONTRACT.md
6. COMPONENT_LADDER.md

Check whether the scripts actually implement the intended experiments.

Focus on:
- Are the correct baselines implemented?
- Are the required controls implemented?
- Are ablations implemented as specified?
- Are the same datasets, splits, metrics, and regimes used?
- Does the code test the claimed mechanism?
- Are any components missing, silently changed, or merged together?
- Are there shortcuts that make the experiment non-diagnostic?
- Are config defaults inconsistent with the experiment plan?
- Are outputs sufficient to interpret positive, negative, and tied results?
- Would a null result from this code be interpretable?

Do not only report compile errors.
Report semantic mismatches between plan and implementation.

Return:
1. MATCHES_PLAN / PARTIAL_MISMATCH / CRITICAL_MISMATCH
2. Missing experiments
3. Missing controls
4. Incorrect defaults
5. Plan-code mismatches
6. Required fixes before GPU
```

## 8. Tiny Run / Sanity Run

```text
Run a tiny sanity experiment before full GPU runs.

Check:
1. data loading;
2. label alignment;
3. split correctness;
4. metric range;
5. loss / reward behavior;
6. tiny overfit;
7. known baseline reproduction;
8. output files;
9. logging completeness;
10. whether the result is sufficient to debug implementation and evaluation.

Do not proceed to full runs if tiny sanity fails.
```

## 8.5. Tiny Run Audit

```text
Audit the tiny-run outputs against the experiment plan.

Check:
1. Did the expected script run?
2. Did it use the intended dataset, split, metric, and config?
3. Did it run the intended baseline or component?
4. Are outputs saved in the expected format?
5. Are metric values plausible?
6. Are logs sufficient to diagnose null results?
7. Does the tiny run reveal implementation mismatch?
8. Should we proceed, fix code, change experiment, or stop?

Return:
PASS / FIX_BEFORE_GPU / REDESIGN_EXPERIMENT.
```

## 9. Result Interpretation Loop

```text
After every experiment, do not immediately proceed to the next planned run.

Write a Result Interpretation Note:

1. What was the expected result?
2. What was the observed result?
3. Did the expected signal appear?
4. Which hypothesis is supported?
5. Which hypothesis is weakened?
6. What is the most likely explanation?
7. What are alternative explanations?
8. Is the issue more likely due to:
   - mechanism;
   - benchmark;
   - baseline ceiling;
   - implementation;
   - evaluation;
   - data/task ontology;
   - hyperparameters;
   - missing control?
9. What is the next diagnostic experiment?
10. Decision:
   - continue;
   - narrow;
   - redesign;
   - re-read literature;
   - change benchmark;
   - change control;
   - stop.

The next experiment must depend on the interpretation of the current result.
Do not blindly continue the original experiment plan.
```

## 10. Re-read Literature After Early Results

```text
After initial diagnostic experiments, re-read the most relevant papers.

Focus on:
1. Did prior work observe the same failure mode?
2. Did they report the same baseline ceiling?
3. Did they test the same hard subset or regime?
4. Did they include the controls we now think are necessary?
5. Did their claimed mechanism actually isolate the effect?
6. Did they use a benchmark that has more headroom than ours?
7. Does our early result change the research question?
8. Should we revise:
   - hypothesis;
   - mechanism;
   - benchmark;
   - controls;
   - component ladder;
   - paper claim?

Output an updated research direction note.

Do not continue scaling if the early result suggests the original research question is wrong.
```

## 11. Scale-up Experiment

```text
Scale only after the diagnostic stage passes.

Before scaling, confirm:
1. Task ontology is stable.
2. Baseline ceiling is known.
3. Highest-headroom regime is identified.
4. The core mechanism has shown a diagnostic signal.
5. Controls isolate the mechanism.
6. Null-result interpretation is clear.
7. Implementation sanity checks passed.
8. Plan-code consistency audit passed.
9. The next scaled experiment supports a specific paper claim.

Then expand carefully:
- more seeds;
- more datasets;
- more splits;
- more domains;
- more ablations;
- full benchmark comparison;
- stronger baselines;
- robustness checks.

Do not scale just because the original plan said so.
Scale because the diagnostic evidence justifies it.
```

## 12. Result-to-Claim Construction

```text
Build the paper as a claim-evidence chain, not an experiment dump.

For each claim, specify:
1. Claim: What exactly do we claim?
2. Evidence: Which results support it?
3. Control: Which controls isolate the effect?
4. Scope: In which regime does the claim hold?
5. Limitation: What does the evidence not prove?
6. Risk of overclaiming: Could a reviewer say the claim is stronger than the evidence?
7. Required additional experiment: What evidence is still missing?

Downgrade claims when evidence is partial.

Do not generalize beyond the tested benchmark, regime, or control set.
```

## 13. Tie / Negative Result Strategy

```text
If the proposed method ties or fails, do not force a positive story.

Evaluate whether the project still contributes through:
1. Benchmark diagnosis: Did we discover that the benchmark is saturated or misaligned?
2. Baseline ceiling analysis: Did we show that simple baselines are stronger than expected?
3. Failure-mode taxonomy: Did we identify where and why methods fail?
4. Negative result: Did we falsify a common assumption?
5. Regime map: Did we show where the method helps and where it does not?
6. Evaluation protocol: Did we improve how the field should evaluate this problem?
7. Data/task ontology: Did we clarify a previously confused task definition?
8. Controlled reproduction: Did we produce a useful reproducibility finding?

If no contribution remains, recommend stopping or reframing.

Do not continue expensive experiments only to rescue a weak story.
```

## 14. Reviewer Red-team

```text
Act as a skeptical top-tier reviewer.

Attack the project on:
1. Problem importance: Is the problem worth solving?
2. Novelty: Is the contribution actually new?
3. Task definition: Are inputs, labels, domains, modalities, vendors, and splits well-defined?
4. Benchmark validity: Does the benchmark actually test the claim?
5. Baselines: Are the baselines strong enough?
6. Controls: Do the controls isolate the mechanism?
7. Null-result interpretation: Would failure be interpretable?
8. Evidence: Do the results support the claims?
9. Overclaiming: Are conclusions stronger than evidence?
10. Reproducibility: Are data, code, metrics, and settings clear enough?
11. Limitations: Are limitations honest and specific?

Return:
- top 5 rejection risks;
- required fixes;
- which fixes are essential before submission;
- which claims should be weakened;
- whether the paper is currently submit-ready.
```

## 15. Human Decision / Next Research Loop

```text
Before proceeding to the next major stage, produce a Human Decision Note.

Summarize:
1. What we currently believe.
2. What evidence supports it.
3. What remains uncertain.
4. What the agent recommends next.
5. What decision requires human judgment.

Use one of:
- PROCEED;
- NARROW;
- REDESIGN;
- RE-READ;
- CHANGE BENCHMARK;
- STOP;
- HUMAN_DECISION_REQUIRED.
```
