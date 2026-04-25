# Better BRIS Research Agent Pipeline

This shared reference is the load-bearing research contract for BRIS. It adapts the
`how_to_improve_skills.md` workflow into the original ARIS skill ecosystem instead of
replacing mature ARIS skills with a lightweight fork.

## Design Target

BRIS should behave less like an automatic experiment executor and more like a junior research
scientist:

- discovers concrete problems instead of rushing to methods
- reads papers with questions instead of summarizing
- audits task/data ontology before designing models
- estimates simple strong baseline ceilings before proposed methods
- designs experiments that are diagnostic when they fail
- builds complex systems component by component
- audits whether code implements the intended algorithm
- turns results into scoped claims rather than inflated stories
- uses cross-model debate to avoid single-model local optima

## Canonical Stage Map

```text
0A. Seed Framing
1. Question-driven Literature Map
0B. Problem Taste / Problem Selection
2. Task Ontology / Data Audit
3. Baseline Ceiling / Headroom Audit
4. Hypothesis-Mechanism-Benchmark-Control Matrix
5. Null-result Contract
6. Progressive Component Ladder
7. Minimal Diagnostic Experiment Design
7.5 Plan-Code Consistency Audit
8. Tiny Run / Sanity Run
8.5 Tiny Run Audit
9. Result Interpretation Loop
10. Re-read Literature After Early Results
11. Scale-up Experiment
12. Result-to-Claim Construction
13. Tie / Negative Result Strategy
14. Reviewer Red-team
15. Human Decision / Next Research Loop
```

This is a loop:

```text
literature -> problem -> data audit -> baseline ceiling -> mechanism/control design
       ^                                                        |
       |                                                        v
re-read literature <- result interpretation <- tiny run <- component ladder
```

## Stage Responsibilities

### 0A. Seed Framing

Use when the user gives only a research area. The agent must define the search boundary:
field, constraints, initial questions, keywords, subfields, adjacent areas, and paper types
to read first. It must not propose final methods, commit to benchmarks, or write experiments.

Required artifact: `SEED_FRAMING.md`

### 1. Question-driven Literature Map

Read papers to find claim-evidence gaps, missing controls, benchmark saturation, failure
regimes, weak assumptions, strong baselines, and underexplored settings.

Recommended first pass:

- 2 survey or benchmark papers
- 5 recent SOTA papers
- 3 foundation papers
- 3 analysis, negative, or ablation papers
- 3 closest baseline papers

Required artifact: `LITERATURE_MAP.md`

### 0B. Problem Taste / Problem Selection

Select a problem only after the literature map exists. Score candidates by importance,
audience, concreteness, novelty, feasibility, benchmark availability, baseline ceiling risk,
expected headroom, diagnostic clarity, and paper survivability if the method fails or ties.

Required artifact: `PROBLEM_SELECTION.md`

Required ending: `PROCEED`, `NARROW`, or `RETHINK`

### 2. Task Ontology / Data Audit

Before method design, define prediction target, inputs, labels, patient/eye/visit/image/report
units, modalities, vendors, devices, acquisition protocols, domains, splits, and confounders.
Actively search for category errors such as vendor treated as modality, modality treated as
domain, source treated as label, patient leakage, shortcut features, or label/device confounds.

Required artifact: `TASK_ONTOLOGY.md`

### 3. Baseline Ceiling / Headroom Audit

Before proposed methods, estimate the ceiling of simple strong baselines and whether the
benchmark has real headroom. Consider zero-shot, few-shot, Best-of-N, confidence-rank,
reranking, DINGO-style search, vanilla GRPO/PPO/RL, vanilla SFT, ERM, modality-specific,
majority-domain, heuristic, and public SOTA baselines.

Required artifact: `BASELINE_CEILING.md`

### 4. Hypothesis-Mechanism-Benchmark-Control Matrix

Every experiment must specify hypothesis, mechanism, target failure mode, benchmark rationale,
highest-headroom regime, required controls, possible confounders, positive signal, and
falsifying signal.

Required artifact: `CONTROL_DESIGN.md`

### 5. Null-result Contract

Before running, define what positive, negative, tied, noisy, or chaotic outcomes mean. If a
failure would not distinguish mechanism failure, benchmark saturation, implementation bug,
metric mismatch, missing control, task ontology error, or convergence issue, the experiment is
invalid.

Required artifact: `NULL_RESULT_CONTRACT.md`

### 6. Progressive Component Ladder

Complex systems are allowed, but must be built gradually. Start with Component 0: simplest
strong baseline. Add one component at a time, each with target failure mode, expected signal,
control, null-result interpretation, rollback condition, and interaction risk.

Required artifact: `COMPONENT_LADDER.md`

### 7. Minimal Diagnostic Experiment Design

Before full benchmark runs, design the cheapest informative test: tiny subset, one seed,
hard subset, highest-headroom regime, oracle upper bound, tiny overfit, known baseline
reproduction, metric sanity, verifier ranking sanity, or control-only experiment.

Required artifact: `DIAGNOSTIC_EXPERIMENT_PLAN.md`

### 7.5 Plan-Code Consistency Audit

Codex reviews implementation as a semantic auditor. It checks whether training/eval scripts,
configs, launch scripts, datasets, splits, metrics, baselines, controls, and ablations match
the research plan. It is not primarily a syntax/style review.

Required artifact: `PLAN_CODE_AUDIT.md`

### 8. Tiny Run / Sanity Run

Before full GPU runs, verify data loading, label alignment, split correctness, metric range,
loss/reward behavior, tiny overfit, known baseline reproduction, output files, and logging.

Required artifact: `TINY_RUN_REPORT.md`

### 8.5 Tiny Run Audit

Audit tiny-run outputs against the plan. A tiny run that merely executes is insufficient; it
must run the intended script, dataset, split, metric, baseline/component, config, and produce
logs sufficient for null-result diagnosis.

Required artifact: `TINY_RUN_AUDIT.md`

Required ending: `PASS`, `FIX_BEFORE_GPU`, or `REDESIGN_EXPERIMENT`

### 9. Result Interpretation Loop

After every experiment, interpret before launching the next run. The next experiment must
depend on the current result interpretation.

Required artifact: `RESULT_INTERPRETATION.md`

### 10. Re-read Literature After Early Results

After early diagnostic results, re-read the closest papers for the now-visible failure mode,
baseline ceiling, hard subset, controls, benchmark headroom, and mechanism assumptions.

Required artifact: `LITERATURE_REREAD_NOTE.md`

### 11. Scale-up Experiment

Scale only after task ontology, baseline ceiling, headroom regime, diagnostic signal, controls,
null-result contract, sanity checks, and plan-code audit are all satisfactory.

Required artifact: `SCALEUP_DECISION.md`

### 12. Result-to-Claim Construction

Build paper claims as claim -> evidence -> control -> scope -> limitation. Downgrade claims
when evidence is partial.

Required artifact: `CLAIM_CONSTRUCTION.md`

### 13. Tie / Negative Result Strategy

If the method ties or fails, do not force a positive story. Evaluate benchmark diagnosis,
baseline ceiling analysis, failure taxonomy, negative result, regime map, evaluation protocol,
task ontology contribution, or controlled reproduction. Stop if no contribution remains.

Required artifact: `NEGATIVE_RESULT_STRATEGY.md`

### 14. Reviewer Red-team

Run a skeptical reviewer attack on importance, novelty, task definition, benchmark validity,
baselines, controls, null-result interpretation, evidence, overclaiming, reproducibility, and
limitations.

Required artifact: `RED_TEAM_REVIEW.md`

### 15. Human Decision / Next Research Loop

Before major transitions, write what is believed, what evidence supports it, what remains
uncertain, what the agent recommends next, and what requires human judgment.

Required artifact: `HUMAN_DECISION_NOTE.md`

Required ending: `PROCEED`, `NARROW`, `REDESIGN`, `RE-READ`, `CHANGE BENCHMARK`, `STOP`, or
`HUMAN_DECISION_REQUIRED`

## Hard Gates

Each artifact below is a verdict-bearing file. Downstream skills parse its verdict line
and enforce the gate; mere file existence is not enough.

- No method design before `TASK_ONTOLOGY.md` exists and stabilizes.
- No proposed method run before `BASELINE_CEILING.md` exists and lists the simplest strong
  baselines and headroom regime.
- No experiment without an interpretable `NULL_RESULT_CONTRACT.md`.
- No full system before `COMPONENT_LADDER.md` exists and justifies the proposed component
  order.
- No GPU scale-up unless `PLAN_CODE_AUDIT.md` verdict line is `MATCHES_PLAN` or a scoped
  `PARTIAL_MISMATCH` whose missing pieces are irrelevant to this scale-up wave.
  `CRITICAL_MISMATCH` blocks unconditionally. `ERROR` (Codex unavailable, audit could not
  complete) is **advisory at tiny / sanity run** (proceed, surface the reason) and
  **blocks at scale-up pending explicit human acknowledgement** (scale-up is the
  expensive irreversible step; never launch without a person on the loop).
- No full run unless `TINY_RUN_AUDIT.md` verdict line is `PASS`.
  `FIX_BEFORE_GPU` and `REDESIGN_EXPERIMENT` block.
- No blind continuation after results; update `RESULT_INTERPRETATION.md`.
- No paper claim before `CLAIM_CONSTRUCTION.md`.
- No positive story after tie/failure before `NEGATIVE_RESULT_STRATEGY.md`.
- No `submission-ready` label before reviewer red-team (`RED_TEAM_REVIEW.md`) and paper
  audits (`PAPER_CLAIM_AUDIT.json`, `CITATION_AUDIT.json`) all pass.

## Claude + Codex Debate Nodes

Use debate at these stages:

- Problem Selection
- Literature Map
- Task Ontology / Data Audit
- Baseline Ceiling / Headroom
- Hypothesis-Mechanism-Benchmark-Control
- Null-result Contract
- Progressive Component Ladder
- Algorithm Design
- Plan-Code Consistency Audit
- Tiny Run Audit
- Result-to-Claim
- Final Reviewer Red-team

Debate protocol:

```text
Claude: propose
Codex: critique
Claude: revise
Codex: final objections
Claude: consensus decision
Human: approve / redirect
```

At most two rounds. End with exactly one:

- `CONSENSUS`
- `DISAGREEMENT`
- `HUMAN_DECISION_REQUIRED`

## Reviewer Defaults

For BRIS, Codex review defaults are:

- `model = gpt-5.5`
- `reasoning_effort = xhigh`
- sandbox disabled, equivalent to `sandbox_mode = danger-full-access`
- reviewer role: independent semantic auditor

Reviewer independence is mandatory: pass file paths and review objectives, not executor
summaries or leading interpretations.
