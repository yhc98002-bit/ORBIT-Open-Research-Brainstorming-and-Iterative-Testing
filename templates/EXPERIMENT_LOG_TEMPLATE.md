# Experiment Log

> **Human-readable narrative summary of experiments run in this project.** Every experiment
> may get an entry — successful or not — but the canonical factual provenance record is
> `orbit-research/RUN_LEDGER.jsonl`.
>
> **How it differs from RUN_LEDGER.jsonl and EXPERIMENT_TRACKER.md:** `RUN_LEDGER.jsonl`
> is append-only factual provenance: run_id, exact command, config, commit, logs, result
> files, terminal status. The tracker is an execution checklist (TODO -> RUNNING -> DONE).
> This log is the readable narrative layer: what the run was meant to test and what we
> learned.
>
> **Update rule:** Write an entry immediately after each experiment completes. Do not batch entries or wait until "later."

## Experiment: [Descriptive Name]

**Run ID**: [run_YYYYMMDDTHHMMSSZ_xxxxx]
**Date**: YYYY-MM-DD
**Idea**: [Which idea from IDEA_CANDIDATES.md]
**Goal**: [What this experiment tests — link to claim if applicable]
**Ledger**: `orbit-research/RUN_LEDGER.jsonl`

### Setup
- **Method**: [Brief description of the approach]
- **Dataset**: [Name, split, size]
- **Baseline**: [What you compare against]
- **Hardware**: [Server, GPUs, time taken]
- **Config**: [Path to config file or key hyperparameters]
- **Config hash**: [sha256 if available]
- **Git commit**: [commit SHA]
- **Git diff status**: [clean / dirty / unknown]
- **Command**:
  ```bash
  [exact command]
  ```
- **Working directory**: [cwd]
- **Logs**: [stdout path] / [stderr path]
- **Result files**: [paths]

### Results

| Method | Dataset | Metric-1 | Metric-2 | Notes |
|--------|---------|----------|----------|-------|
| Baseline | [dataset] | [number] | [number] | [reproduced / from paper] |
| Ours | [dataset] | [number] | [number] | [seeds, std if applicable] |

### Verdict
- **Run status**: [completed / failed / oom / timeout / killed / no_result / partial]
- **Supports claim?** [Yes / Partially / No]
- **Diagnostic audit verdict**: [PASS / FIX_BEFORE_GPU / REDESIGN_EXPERIMENT / ERROR]
- **Failure type**: [if failed]
- **Key takeaway**: [One sentence — what did we learn?]
- **Decision log**: [`orbit-research/RESEARCH_DECISION_LOG.md`, if this run changed routing]

### Reproduction
```bash
# Command to reproduce this experiment
python train.py --config configs/exp01.yaml --seed 42
```

### WandB
- Run URL: [link]
- Run ID: [id]

---

## Experiment: [Next Experiment Name]

...
