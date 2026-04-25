# Semantic Plan-Code Audit

This reference defines the BRIS code review gate. It is stricter than ordinary code review.
The reviewer checks whether the implementation reflects the scientific plan.

## Reviewer Defaults

- Reviewer: Codex
- Model: `gpt-5.5`
- Reasoning: `xhigh`
- Sandbox: disabled / `danger-full-access`
- Role: independent semantic implementation auditor

If the available MCP or CLI cannot verify this exact configuration, write the actual backend
in the audit artifact and mark the review `PARTIAL` if the mismatch affects trust.

## Independence Rule

The executor must pass file paths and review objectives, not a curated summary. The reviewer
must read primary artifacts directly.

Good prompt shape:

```text
You are an independent semantic implementation auditor.

Read these files directly:
- refine-logs/FINAL_PROPOSAL.md
- refine-logs/EXPERIMENT_PLAN.md
- BASELINE_CEILING.md
- CONTROL_DESIGN.md
- NULL_RESULT_CONTRACT.md
- COMPONENT_LADDER.md
- src/train.py
- src/eval.py
- configs/main.yaml
- scripts/launch.sh

Do not rely on executor summaries.
Compare plan to implementation and report semantic mismatches.
```

Bad prompt shape:

```text
I implemented the verifier and the ablation is probably fine. Please check quickly.
```

## Required Inputs

Plan artifacts:

- `FINAL_PROPOSAL.md`
- `EXPERIMENT_PLAN.md`
- `BASELINE_CEILING.md`
- `CONTROL_DESIGN.md`
- `NULL_RESULT_CONTRACT.md`
- `COMPONENT_LADDER.md`
- `DIAGNOSTIC_EXPERIMENT_PLAN.md`

Implementation artifacts:

- training scripts
- evaluation scripts
- data loaders
- config files
- launch scripts
- result parsers
- experiment tracker
- tiny-run logs and outputs, for Stage 8.5

## Plan-Code Audit Prompt

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

## Traceability Matrix

Every audit should include:

```text
Experiment Plan Item | Expected Implementation | Actual Code | Status | Fix
```

Example rows:

```text
vanilla-GRPO control | train_grpo.py without verifier | missing | CRITICAL | implement no-verifier control
BoN baseline | bon_eval.py with N=8/16/32 | only N=8 | PARTIAL | add N sweep
confidence-rank baseline | rank by model confidence | not implemented | CRITICAL | add confidence ranking
hard subset eval | evaluate on high-uncertainty split | using full test only | MISMATCH | add subset filter
```

## Tiny Run Audit Prompt

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

## Blocking Rules

- `CRITICAL_MISMATCH` blocks GPU scale-up.
- `PARTIAL_MISMATCH` may allow a tiny run only if the missing pieces are irrelevant to that tiny run.
- `FIX_BEFORE_GPU` blocks full run.
- `REDESIGN_EXPERIMENT` sends the project back to experiment design.
- A run that compiles but does not implement the intended algorithm is a failed audit.
