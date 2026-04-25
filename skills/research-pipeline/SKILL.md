---
name: research-pipeline
description: "Better BRIS end-to-end research pipeline built on the original ARIS skills. Runs the 0A-15 diagnostic research flow: seed framing, question-driven literature map, problem selection, task ontology/data audit, baseline ceiling, null-result contract, component ladder, diagnostic experiment, semantic plan-code audit, tiny-run audit, result interpretation, scale-up, claim construction, negative-result strategy, reviewer red-team, and paper writing. Use when user says 全流程/full pipeline/end-to-end research/从问题到论文/Better BRIS/自动科研流水线."
argument-hint: [research-area-or-problem]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# Better BRIS Research Pipeline

Run the full diagnostic research workflow for: **$ARGUMENTS**

This is the BRIS control skill. It preserves mature ARIS infrastructure while enforcing the
research process in `shared-references/research-agent-pipeline.md`.

## Load First

Before executing the pipeline, read:

- `shared-references/research-agent-pipeline.md`
- `shared-references/research-harness-prompts.md`
- `shared-references/semantic-code-audit.md`
- `shared-references/reviewer-independence.md`
- `shared-references/reviewer-routing.md`

## Constants

- **OUTPUT_ROOT = `bris-research/`** — Better BRIS stage artifacts live here unless a project already has a better convention.
- **CODEX_REVIEW_MODEL = `gpt-5.5`** — Default Codex reviewer for BRIS.
- **CODEX_REVIEW_EFFORT = `xhigh`** — Mandatory for all BRIS review gates.
- **CODEX_SANDBOX = `disabled`** — Equivalent to `sandbox_mode = danger-full-access`.
- **REVIEWER_INDEPENDENCE = on** — Pass file paths and objective, not executor summaries.
- **MAX_DEBATE_ROUNDS = 2** — Prevent infinite Claude vs Codex debate loops.
- **AUTO_WRITE = false** — If true, run `/paper-writing` after claim construction and red-team gates.
- **VENUE = `ICLR`** — Used when paper writing is enabled.
- **AUTO_PROCEED = false** for irreversible actions: expensive GPU scale-up, final paper claims, stopping a project.

## Canonical Outputs

Create or update these artifacts as the project progresses:

```text
bris-research/SEED_FRAMING.md
bris-research/LITERATURE_MAP.md
bris-research/PROBLEM_SELECTION.md
bris-research/TASK_ONTOLOGY.md
bris-research/BASELINE_CEILING.md
bris-research/CONTROL_DESIGN.md
bris-research/NULL_RESULT_CONTRACT.md
bris-research/COMPONENT_LADDER.md
bris-research/DIAGNOSTIC_EXPERIMENT_PLAN.md
bris-research/PLAN_CODE_AUDIT.md
bris-research/TINY_RUN_REPORT.md
bris-research/TINY_RUN_AUDIT.md
bris-research/RESULT_INTERPRETATION.md
bris-research/LITERATURE_REREAD_NOTE.md
bris-research/SCALEUP_DECISION.md
bris-research/CLAIM_CONSTRUCTION.md
bris-research/NEGATIVE_RESULT_STRATEGY.md
bris-research/RED_TEAM_REVIEW.md
bris-research/HUMAN_DECISION_NOTE.md
```

Also reuse existing ARIS outputs when present:

- `idea-stage/IDEA_REPORT.md`
- `idea-stage/IDEA_CANDIDATES.md`
- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_TRACKER.md`
- `review-stage/AUTO_REVIEW.md`
- `NARRATIVE_REPORT.md`
- `paper/`

## Pipeline

### Stage 0A: Seed Framing

Use when `$ARGUMENTS` is a broad area rather than a concrete problem.

Action:

1. Use the Stage 0A harness from `research-harness-prompts.md`.
2. Write `bris-research/SEED_FRAMING.md`.
3. Define research area, constraints, 3-5 initial questions, search terms, subfields, adjacent areas, and paper classes.

Gate:

- Do not propose final methods.
- Do not commit to a benchmark.
- Do not write an experiment plan.

### Stage 1: Question-driven Literature Map

Invoke existing ARIS literature tools:

```bash
/research-lit "$ARGUMENTS"
```

Optionally use `/arxiv`, `/semantic-scholar`, `/exa-search`, `/deepxiv`, Zotero, Obsidian, and local PDFs.

Action:

1. Read papers as a research scientist, not as a summarizer.
2. Extract claim, mechanism, benchmark, evidence, weak assumption, missing control, failure regime, claim-evidence gap, and follow-up question.
3. Synthesize field consensus, bottlenecks, overclaims, saturation risks, missing controls, underexplored regimes, and candidate problems.
4. Write `bris-research/LITERATURE_MAP.md`.

Codex debate:

- Codex checks missing papers, missing baselines, overclaimed assumptions, claim-evidence gaps, and benchmark saturation.

Gate:

- Do not generate final methods yet. Generate candidate problems.

### Stage 0B: Problem Selection

Action:

1. Evaluate candidate problems by importance, audience, concreteness, novelty, feasibility, benchmark availability, baseline ceiling risk, expected headroom, diagnostic clarity, and paper survivability.
2. Run Claude vs Codex debate. Codex should attack feasibility, baseline risk, and paper value if the method ties.
3. Write `bris-research/PROBLEM_SELECTION.md`.

Required ending:

```text
PROCEED / NARROW / RETHINK
```

Gate:

- Do not select a problem only because it sounds novel.

### Stage 2: Task Ontology / Data Audit

Action:

1. Define prediction target, inputs, labels, data units, modalities, vendors/devices, acquisition protocols, domains, splits, and confounders.
2. Search for category errors, label/source confounds, patient leakage, shortcut features, and split pathologies.
3. Write `bris-research/TASK_ONTOLOGY.md`.

Codex debate:

- Codex acts as data/task ontology auditor and tries to find category errors or leakage.

Gate:

- Do not proceed to method design until task ontology is stable enough.

### Stage 3: Baseline Ceiling / Headroom Audit

Action:

1. Estimate the simplest strong baseline ceiling.
2. Consider zero-shot, few-shot, Best-of-N, confidence-rank, reranking, DINGO-style search, vanilla GRPO/PPO/RL, vanilla SFT, ERM, modality-specific, majority-domain, heuristic, and public SOTA baselines.
3. Identify benchmark saturation risk and highest-headroom regime.
4. Write `bris-research/BASELINE_CEILING.md`.

Codex debate:

- Codex argues whether the simple baseline is already too strong or whether the benchmark/claim must change.

Gate:

- Do not run the proposed method before baseline ceiling is known or explicitly estimated.

### Stages 4-7: Diagnostic Experiment Design

Use existing ARIS refinement and planning skills after the Better BRIS gates are explicit:

```bash
/research-refine "$ARGUMENTS"
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

Action:

1. Fill the hypothesis-mechanism-benchmark-control matrix.
2. Write `bris-research/CONTROL_DESIGN.md`.
3. Write `bris-research/NULL_RESULT_CONTRACT.md`.
4. Build `bris-research/COMPONENT_LADDER.md` from Component 0: simplest strong baseline.
5. Write `bris-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`.

Codex debate:

- Codex attacks control isolation, null-result interpretability, component attribution, rollback conditions, and algorithmic self-consistency.

Gate:

- Reject non-diagnostic experiments.
- Do not run full systems before each major component is justified.
- Do not run broad grids before the minimal diagnostic experiment.

### Stage 7.5: Semantic Plan-Code Consistency Audit

Use `/experiment-bridge` for implementation only after the planning gates exist:

```bash
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
```

Then run semantic audit using `shared-references/semantic-code-audit.md`.

Action:

1. Codex reads plan artifacts and implementation files directly.
2. Codex checks whether code implements the intended baselines, controls, ablations, datasets, splits, metrics, regimes, config defaults, and outputs.
3. Write `bris-research/PLAN_CODE_AUDIT.md`.

Gate:

- `CRITICAL_MISMATCH` blocks GPU scale-up.
- Compile success is not enough.

### Stages 8-8.5: Tiny Run And Tiny Run Audit

Use ARIS execution infrastructure:

```bash
/run-experiment "[tiny diagnostic command]"
/monitor-experiment "[run id or server]"
```

For many jobs, route through:

```bash
/experiment-queue "[manifest or grid]"
```

Action:

1. Run the smallest sanity experiment.
2. Write `bris-research/TINY_RUN_REPORT.md`.
3. Codex or Claude audits outputs against the plan.
4. Write `bris-research/TINY_RUN_AUDIT.md`.

Gate:

- Do not full-run unless tiny-run audit returns `PASS`.

### Stages 9-11: Interpret, Re-read, Scale

Use ARIS result tools:

```bash
/analyze-results "[results path]"
/result-to-claim "[experiment description]"
```

Action:

1. Write `bris-research/RESULT_INTERPRETATION.md` after every experiment.
2. If early results change the question, write `bris-research/LITERATURE_REREAD_NOTE.md`.
3. Before scale-up, write `bris-research/SCALEUP_DECISION.md`.

Gate:

- The next experiment must depend on current interpretation.
- Do not scale because the original plan said so; scale because diagnostic evidence justifies it.

### Stages 12-13: Claim Construction And Negative Strategy

Action:

1. Build claim -> evidence -> control -> scope -> limitation chain.
2. Write `bris-research/CLAIM_CONSTRUCTION.md`.
3. If the method ties or fails, write `bris-research/NEGATIVE_RESULT_STRATEGY.md`.
4. Use `/result-to-claim` as the ARIS claim gate.

Gate:

- Do not generalize beyond tested benchmark, regime, or control set.
- Do not force a positive story after tie or failure.

### Stage 14: Reviewer Red-team

Use existing ARIS review skills:

```bash
/auto-review-loop "$ARGUMENTS" — difficulty: hard
/experiment-audit "[results and code]"
/paper-claim-audit "paper/"
/citation-audit "paper/"
```

Action:

1. Codex and Claude independently attack the project.
2. Write `bris-research/RED_TEAM_REVIEW.md`.
3. Record top 5 rejection risks, required fixes, essential pre-submission fixes, claims to weaken, and submit-readiness.

Gate:

- Do not mark submission-ready while high-severity rejection risks remain unresolved.

### Stage 15: Human Decision / Next Research Loop

Action:

1. Write `bris-research/HUMAN_DECISION_NOTE.md`.
2. Summarize current belief, evidence, uncertainty, recommendation, and required human judgment.

Required ending:

```text
PROCEED / NARROW / REDESIGN / RE-READ / CHANGE BENCHMARK / STOP / HUMAN_DECISION_REQUIRED
```

## Paper Writing Integration

Paper writing is not replaced. It is inherited from ARIS:

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: $VENUE, assurance: submission
```

Before invoking `/paper-writing`, require:

- `bris-research/CLAIM_CONSTRUCTION.md`
- `bris-research/RED_TEAM_REVIEW.md`
- supported or downgraded claims from `/result-to-claim`

During paper writing, keep ARIS gates:

- `/paper-plan`
- `/paper-figure`
- `/figure-spec` or `/paper-illustration`
- `/paper-write`
- `/paper-compile`
- `/auto-paper-improvement-loop`
- `/paper-claim-audit`
- `/citation-audit`

## Final Rule

Creative Mode allows bold mechanisms. Commitment Mode requires diagnostics.

```text
Bold ideas are allowed.
Undiagnosable experiments are not.

Failure is allowed.
Failure without interpretation is not.

Runnable code is not success.
Code that faithfully implements the experiment plan is success.
```
