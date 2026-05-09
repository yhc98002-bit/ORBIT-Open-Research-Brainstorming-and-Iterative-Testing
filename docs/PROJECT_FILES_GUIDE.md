# Project Files Guide

[中文版](PROJECT_FILES_GUIDE_CN.md) | English

> How to organize project-level state files for ARIS research workflows — what each file does, when to write it, and how they relate to each other.

## The Problem

ARIS workflows generate a lot of information across multiple stages: ideas, experiment plans, results, review feedback, decisions. Without clear file conventions, this information gets scattered across chat sessions and lost on context compaction or new sessions.

This guide establishes a layered file system where each file has a clear purpose, update trigger, and relationship to other files.

## File Overview

```
project/
├── CLAUDE.md                              # Dashboard — Pipeline Status + project constraints
├── findings.md                            # Lightweight discovery log (experiments + debug)
├── MANIFEST.md                            # Output tracking manifest (auto-maintained)
│
├── idea-stage/                            # W1: Idea Discovery outputs
│   ├── IDEA_REPORT.md                     # Raw brainstorm output (from /idea-creator)
│   ├── IDEA_CANDIDATES.md                 # Curated pool of viable ideas (post-review)
│   ├── REF_PAPER_SUMMARY.md              # Reference paper summary (when REF_PAPER is set)
│   └── docs/
│       └── research_contract.md           # Focused context for the active idea
│
├── refine-logs/                           # W1.5: Experiment Planning & Refinement
│   ├── EXPERIMENT_PLAN.md                 # Experiment-plan index
│   ├── EXPERIMENT_PLAN_EXEC.md            # Claims + blocks + run order
│   ├── EXPERIMENT_TRACKER.md              # Execution checklist (TODO → DONE)
│   ├── EXPERIMENT_RESULTS.md              # Collected experiment results
│   ├── EXPERIMENT_LOG.md                  # Human-readable experiment summary
│   ├── FINAL_PROPOSAL.md                 # Proposal index
│   ├── FINAL_PROPOSAL_SHORT.md           # Clean short proposal
│   ├── METHOD_SPEC.md                    # Implementation-level method spec
│   ├── PIPELINE_SUMMARY.md               # Pipeline execution summary
│   ├── REFINE_STATE.json                  # Refinement recovery state
│   └── round_N_*.md                       # Per-round review/proposal files
│
├── review-stage/                          # W2: Auto Review outputs
│   ├── AUTO_REVIEW.md                     # Review loop log (from /auto-review-loop)
│   └── REVIEW_STATE.json                  # Review loop recovery state
│
├── paper/                                 # W3: Paper Writing outputs
│   ├── main.tex                           # LaTeX source
│   └── roundN/                            # Per-round PDF snapshots
│
└── research-wiki/                         # Persistent knowledge base
    ├── papers/ ideas/ experiments/ claims/
    └── graph/
```

### Existing ARIS Files (unchanged)

| File | Created by | Purpose |
|------|-----------|---------|
| `idea-stage/IDEA_REPORT.md` | `/idea-creator` | Raw brainstorm output: all 8-12 ideas + pilot results + eliminated ideas |
| `refine-logs/EXPERIMENT_PLAN.md` | `/experiment-plan` | Experiment-plan index and reading paths |
| `refine-logs/EXPERIMENT_PLAN_EXEC.md` | `/experiment-plan` | Executable experiment design: claim map, blocks, decision tree, run order, compute budget |
| `refine-logs/EXPERIMENT_TRACKER.md` | `/experiment-plan` | Execution checklist: run ID, status (TODO→DONE), one-line notes |
| `orbit-research/RUN_LEDGER.jsonl` | `/run-experiment`, `/experiment-queue` | Append-only run provenance: commands, configs, logs, result files, failures |
| `orbit-research/RESEARCH_DECISION_LOG.md` | `/diagnostic-to-review` | Failed/surprising diagnostic classification and local next-route decision |
| `review-stage/AUTO_REVIEW.md` | `/auto-review-loop` | Cumulative review log: scores, reviewer responses, actions taken |
| `review-stage/REVIEW_STATE.json` | `/auto-review-loop` | Recovery state for context compaction |

### New Files (this guide)

| File | Purpose | Template |
|------|---------|----------|
| `idea-stage/IDEA_CANDIDATES.md` | Curated pool of viable ideas that survived review — pick next idea from here when pivoting | [`IDEA_CANDIDATES_TEMPLATE.md`](../templates/IDEA_CANDIDATES_TEMPLATE.md) |
| `findings.md` | Lightweight discovery log — anomalies, debug root causes, key decisions during experiments | [`FINDINGS_TEMPLATE.md`](../templates/FINDINGS_TEMPLATE.md) |
| `refine-logs/EXPERIMENT_LOG.md` | Human-readable experiment narrative; canonical factual provenance lives in `RUN_LEDGER.jsonl` | [`EXPERIMENT_LOG_TEMPLATE.md`](../templates/EXPERIMENT_LOG_TEMPLATE.md) |
| `idea-stage/docs/research_contract.md` | Focused working document for the active idea (from [Session Recovery Guide](SESSION_RECOVERY_GUIDE.md)) | [`RESEARCH_CONTRACT_TEMPLATE.md`](../templates/RESEARCH_CONTRACT_TEMPLATE.md) |

## How They Relate

### Idea Flow

```
IDEA_REPORT.md                    (12 ideas, raw brainstorm)
  ↓ novelty-check + review
IDEA_CANDIDATES.md                (3-5 viable ideas, scored)
  ↓ select one
idea-stage/docs/research_contract.md         (active idea, focused context)
  ↓ idea fails?
IDEA_CANDIDATES.md → pick next → update contract
```

**Why three files?** Context pollution. Loading 12 raw ideas into every session wastes the LLM's working memory. The candidate pool is lean (3-5 entries), and the contract is focused (one idea). On session recovery, the LLM reads only the contract — not the full report.

### Experiment Flow

```
EXPERIMENT_PLAN.md                (what to run — design)
  ↓
EXPERIMENT_TRACKER.md             (execution status — TODO/RUNNING/DONE)
  ↓ experiment completes
RUN_LEDGER.jsonl                  (canonical facts — command/config/logs/results/status)
  ↓
EXPERIMENT_LOG.md                 (human-readable summary — what we learned)
  ↓ discover something unexpected
findings.md                       (one-line entry — anomaly, root cause, decision)
```

**Why separate tracker, ledger, and log?** Different audiences. The tracker is for
execution management ("what's left to run?"). `RUN_LEDGER.jsonl` is factual provenance
("what exactly ran?"). The log is for knowledge preservation ("what did we learn?").
The tracker can be reset between ideas; the ledger stays append-only.

### When to Write Each File

| File | Write when... | Update frequency |
|------|--------------|-----------------|
| `IDEA_CANDIDATES.md` | After `/idea-discovery` completes (initial creation); after idea kill/selection (update status) | Per idea transition |
| `findings.md` | Discover something non-obvious during experiments, debugging, or analysis | As discoveries happen (append) |
| `EXPERIMENT_LOG.md` | An experiment finishes (any experiment, successful or not) | After every experiment |
| `idea-stage/docs/research_contract.md` | Select an idea to work on; baseline reproduced; major results obtained | Per stage milestone |

### Session Recovery Priority

On new session or post-compaction, read files in this order:

1. `CLAUDE.md` → Pipeline Status (30 seconds: where am I?)
2. `idea-stage/docs/research_contract.md` (active idea context)
3. `findings.md` recent entries (what did I discover recently?)
4. `refine-logs/EXPERIMENT_LOG.md` (if needed: what experiments have been run?)

Do NOT read `IDEA_REPORT.md` or `IDEA_CANDIDATES.md` unless switching ideas.

## Separation Principles

| Question | Answer |
|----------|--------|
| Where does a brainstorm idea go? | `IDEA_REPORT.md` (raw) → `IDEA_CANDIDATES.md` (curated) |
| Where does the current idea's full context go? | `idea-stage/docs/research_contract.md` |
| Where does "experiment X is running" go? | `EXPERIMENT_TRACKER.md` |
| Where does "experiment X got accuracy 95.2" go? | `RUN_LEDGER.jsonl` for the factual metric path; `EXPERIMENT_LOG.md` for the readable interpretation |
| Where does "lr=1e-4 diverges on dataset-X" go? | `findings.md` |
| Where does "reviewer says add ablation" go? | `review-stage/AUTO_REVIEW.md` |
| Where does "chose approach A over B because Z" go? | `findings.md` |
| Where does "current stage is training" go? | `CLAUDE.md` Pipeline Status |

## Output Versioning

ORBIT uses selective timestamping. Major proposal/plan/claim/paper milestones may be
written twice:

1. **Timestamped file**: `{FILENAME}_{YYYYMMDD_HHmmss}.md` — permanent history
2. **Fixed-name file**: `{FILENAME}.md` — latest copy, read by downstream skills

```
refine-logs/
├── FINAL_PROPOSAL_SHORT_20250615_143022.md    ← milestone snapshot
├── FINAL_PROPOSAL_SHORT_20250616_090015.md    ← later milestone snapshot
├── FINAL_PROPOSAL_SHORT.md                    ← latest copy
```

**Not timestamped**: append-only files (`findings.md`, `RUN_LEDGER.jsonl`,
`MANIFEST.md`), routing/decision logs, state files, per-round files (`round_N_*.md`),
dashboard (`CLAUDE.md`), and human-readable execution summaries (`EXPERIMENT_LOG.md`).

See [shared-references/output-versioning.md](../skills/shared-references/output-versioning.md) for the full protocol.

## Output Manifest

`MANIFEST.md` in the project root tracks every file written by every skill:

| Timestamp | Skill | File | Stage | Description |
|-----------|-------|------|-------|-------------|
| 2025-06-15 14:30 | /idea-creator | idea-stage/IDEA_REPORT.md | idea | 12 ideas from "LLM reasoning" |

Skills append to this file after every write. It serves as a central index of all research artifacts and enables pre-flight checks (e.g., `/experiment-bridge` can verify that `refine-logs/EXPERIMENT_PLAN.md` exists before starting).

See [shared-references/output-manifest.md](../skills/shared-references/output-manifest.md) for the full protocol.
