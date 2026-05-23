# Run Ledger Protocol

`orbit-research/RUN_LEDGER.jsonl` is the canonical append-only provenance record for
experiment execution. Every launched run gets at least one `run-start` record before
execution and one terminal `run-final` record after completion, failure, timeout, OOM,
kill, or no-result detection.

## Record Rules

- Use JSON Lines: one valid JSON object per line.
- Never rewrite old lines. If status changes, append a new record with the same `run_id`.
- Consumers reconstruct the latest state by grouping by `run_id` and taking the newest
  `event`/timestamp.
- Failed, OOM, timeout, killed, stale-screen, and no-result runs are first-class records.
- `run_id` must appear in `DIAGNOSTIC_RUN_REPORT.md`, `queue_state.json` jobs, and any
  `EXPERIMENT_LOG.md` entry that refers to the run.

## Run Start Record

```json
{
  "event": "run-start",
  "run_id": "run_YYYYMMDDTHHMMSSZ_<shortid>",
  "timestamp_start": "<ISO 8601 UTC>",
  "skill": "run-experiment|experiment-queue|serverless-modal|manual",
  "command": "<exact command>",
  "cwd": "<working directory>",
  "git_commit": "<sha or unknown>",
  "git_diff_status": "clean|dirty|unknown",
  "config_path": "<path or null>",
  "config_hash": "<sha256 or null>",
  "dataset": "<dataset or null>",
  "split": "<split or null>",
  "seed": "<seed or null>",
  "host": "<hostname/server/local/modal>",
  "gpu": "<gpu id/list or null>",
  "screen_name": "<screen session or null>",
  "process_id": "<pid or null>",
  "wandb_run_id": "<id or null>",
  "queue_job_id": "<queue job id or null>",
  "queue_state_path": "<queue_state.json path or null>",
  "attempt": "<integer or null>",
  "diagnostic_plan": "orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md",
  "plan_code_audit_verdict": "<MATCHES_PLAN|PARTIAL_MISMATCH|CRITICAL_MISMATCH|ERROR|unknown>"
}
```

## Run Final Record

```json
{
  "event": "run-final",
  "run_id": "run_YYYYMMDDTHHMMSSZ_<shortid>",
  "timestamp_end": "<ISO 8601 UTC>",
  "status": "completed|failed|oom|timeout|killed|no_result|partial",
  "stdout_log": "<path or null>",
  "stderr_log": "<path or null>",
  "result_files": ["<path>", "..."],
  "primary_metric": {"name": "<metric>", "value": 0.0},
  "baseline_metric": {"name": "<metric>", "value": 0.0},
  "diagnostic_run_audit_verdict": "<PASS|FIX_BEFORE_GPU|REDESIGN_EXPERIMENT|ERROR|unknown>",
  "failure_type": "<oom|timeout|killed|stale_screen|config|implementation|data|metric|no_result|unknown|null>",
  "notes": "<short free text>"
}
```

## Integrity Expectations

- Result files used by `/analyze-results`, `/result-to-claim`, or paper-writing must be
  traceable to a `run_id`.
- If result files are missing, duplicated, older than their run start, or not linked to a
  ledger entry, the analysis must warn and report the affected seeds/runs.
- A paper claim should not use an experiment-audit `FAIL` result unless it is explicitly
  marked as proxy/invalid evidence and excluded from primary support.
