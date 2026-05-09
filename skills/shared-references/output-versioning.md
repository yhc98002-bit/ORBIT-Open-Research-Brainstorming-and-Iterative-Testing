# Output Versioning Protocol

Do not timestamp every intermediate artifact. Timestamp only major human-facing proposal,
plan, claim, and paper artifacts where preserving milestone snapshots is useful. Most
operational files should use a fixed canonical path, append-only logging, or state
overwrite semantics.

When a file is in the timestamped set and would overwrite an existing file, use
timestamped filename + fixed-name latest copy:

1. Write output to timestamped file: `{FILENAME}_{YYYYMMDD_HHmmss}.md` (or `.json`, `.tex` as appropriate)
   - Timestamp precision to seconds to reduce collisions. In the rare case of sub-second conflicts, append `_2`, `_3` etc.
   - Place the timestamped file in the same directory as the fixed-name file
2. Copy the same content to the fixed-name file: `{FILENAME}.md` (overwrites the previous latest copy)
3. Downstream skills always read the fixed-name file — they do not need to know about timestamps

When a file is not in the timestamped set, write or append to its canonical fixed path
only. Use `MANIFEST.md`, Git history, `RUN_LEDGER.jsonl`, and `RESEARCH_DECISION_LOG.md`
for provenance instead of timestamped copies.

## Directory Structure

All ARIS output files are organized by workflow stage:

```
project/
├── CLAUDE.md                              # Dashboard (root — read by all stages)
├── findings.md                            # Cross-stage discovery log (root — append-only)
├── MANIFEST.md                            # Output tracking manifest (root)
│
├── idea-stage/                            # W1: Idea Discovery
│   ├── IDEA_REPORT.md                     # Latest copy
│   ├── IDEA_CANDIDATES.md
│   ├── REF_PAPER_SUMMARY.md
│   └── docs/
│       └── research_contract.md
│
├── refine-logs/                           # W1.5: Experiment Planning & Refinement
│   ├── EXPERIMENT_PLAN.md
│   ├── EXPERIMENT_PLAN_EXEC.md
│   ├── EXPERIMENT_TRACKER.md
│   ├── EXPERIMENT_RESULTS.md
│   ├── FINAL_PROPOSAL.md
│   ├── FINAL_PROPOSAL_SHORT.md
│   ├── METHOD_SPEC.md
│   ├── PIPELINE_SUMMARY.md
│   ├── REFINE_STATE.json
│   ├── REVIEW_SUMMARY.md
│   ├── REFINEMENT_REPORT.md
│   └── round_N_*.md
│
├── review-stage/                          # W2: Auto Review
│   ├── AUTO_REVIEW.md
│   └── REVIEW_STATE.json
│
├── paper/                                 # W3: Paper Writing
│   ├── main.tex
│   └── roundN/
│
└── research-wiki/                         # Persistent knowledge base
```

## What to Timestamp

Timestamp only major milestone artifacts:

- Proposal / method milestones: `FINAL_PROPOSAL.md`, `FINAL_PROPOSAL_SHORT.md`,
  `FINAL_PROPOSAL_FULL.md`, `METHOD_SPEC.md` when it is a committed method snapshot.
- Plan milestones: `EXPERIMENT_PLAN.md`, `EXPERIMENT_PLAN_EXEC.md` when the plan is being
  promoted for human review or paper-level execution.
- Claim / review milestones: `CLAIM_CONSTRUCTION.md`, `RED_TEAM_REVIEW.md`,
  `PIPELINE_SUMMARY.md` when they summarize a paper-bearing diagnostic chain.
- Paper artifacts: `paper/main.tex`, `PAPER_PLAN.md`, `NARRATIVE_REPORT.md`, or other
  submission-facing documents.

## What NOT to Timestamp

- **Append-only files**: `findings.md`, `research-wiki/log.md`,
  `orbit-research/RUN_LEDGER.jsonl`, `MANIFEST.md` — these accumulate entries, not
  overwrite
- **Per-round files**: `refine-logs/round_N_*.md` — already versioned by round number
- **Dashboard**: `CLAUDE.md` — single source of truth, always latest
- **Routing / decision logs**: `orbit-research/RESEARCH_DECISION_LOG.md`,
  `orbit-research/RESULT_INTERPRETATION.md`, `orbit-research/DIAGNOSTIC_RUN_REPORT.md`,
  `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`
- **State files**: `*_STATE.json`, `queue_state.json`, `RUN_EXPERIMENT_STATE.json` —
  overwrite the fixed path; state is not archival history
- **Execution summaries**: `EXPERIMENT_LOG.md`, `EXPERIMENT_TRACKER.md`,
  `EXPERIMENT_RESULTS.md` — use `RUN_LEDGER.jsonl` for factual provenance

Never delete timestamped major milestone files. They are milestone history. Do not create
timestamped copies of append-only ledgers, routing logs, or state files.

## Path Fallback Rule (Backward Compatibility)

Skills that **read** stage-scoped files must fall back to the old root-level location for projects created before this layout was introduced:

```
# For idea-stage files:
Read from idea-stage/IDEA_REPORT.md
If not found → fall back to ./IDEA_REPORT.md

Read from idea-stage/IDEA_CANDIDATES.md
If not found → fall back to ./IDEA_CANDIDATES.md

# For review-stage files:
Read from review-stage/AUTO_REVIEW.md
If not found → fall back to ./AUTO_REVIEW.md

Read from review-stage/REVIEW_STATE.json
If not found → fall back to ./REVIEW_STATE.json
```

Skills that **write** always use the stage-scoped path (never write to root). This ensures new runs migrate output forward while old projects continue to work.

## Migration for Existing Projects

If you find root-level files (`IDEA_REPORT.md`, `AUTO_REVIEW.md`, etc.) and the stage directories do not yet exist, you may optionally offer to migrate:

```
📁 Found legacy root-level files. Migrate to stage directories?
  mv IDEA_REPORT.md idea-stage/IDEA_REPORT.md
  mv AUTO_REVIEW.md review-stage/AUTO_REVIEW.md
  (etc.)
Only do this if the user confirms — do not auto-migrate silently.
```

## Stale State Detection

Before reading a state file (`REFINE_STATE.json`, `REVIEW_STATE.json`, `DSE_STATE.json`):
1. Check the file's last modified time via `ls -la` or `stat`
2. Default staleness threshold: **24 hours** (individual skills may override — e.g., `auto-review-loop` uses 24h, `research-refine` uses 24h). If a skill defines its own threshold, that takes precedence.
3. If older than the threshold, warn the user:
   "⚠️ State file {filename} is {N} hours/days old. It may be from a previous research direction. Continue with this state, or start fresh?"
4. If the user chooses to start fresh, do not create a timestamped state copy. Ignore or
   overwrite the fixed-name state file according to the skill's resume policy, and record
   the decision in `MANIFEST.md` or the relevant decision log when useful.
