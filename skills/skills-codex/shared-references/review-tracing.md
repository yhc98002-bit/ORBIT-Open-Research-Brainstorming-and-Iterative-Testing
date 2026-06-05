# Review Tracing Protocol

## Purpose

Save full prompt/response pairs for every cross-model reviewer call, enabling:
- **Reviewer-independence audit**: verify the executor only passed file paths, not summaries
- **Reproducibility**: agent id preservation allows conversation continuation
- **Meta-optimize input**: richer data for harness improvement analysis

## When to Trace

After **every** `spawn_agent` or `send_input` call that serves a reviewer/critique function. This includes review scoring, experiment auditing, claim verification, idea critique, and patch gating.

Do NOT trace: purely informational LLM calls (e.g., `codex exec` for code generation that is not a review).

## Trace Directory

```
.aris/traces/<skill-name>/<YYYY-MM-DD>_run<NN>/
  ├── run.meta.json                      # Run-level metadata
  ├── 001-<purpose>.request.json         # Request snapshot
  ├── 001-<purpose>.response.md          # Full response text
  ├── 001-<purpose>.meta.json            # Response metadata
  ├── 002-<purpose>.request.json         # Second call (e.g., reply)
  └── ...
```

- `<skill-name>`: the ARIS skill that triggered this call (e.g., `auto-review-loop`)
- `<YYYY-MM-DD>_run<NN>`: date + sequential run number (start from `01`)
- `<purpose>`: short kebab-case label (e.g., `round-1-review`, `critique`, `ideation`, `audit`, `patch-gate`)

## How to Trace

After each reviewer MCP call, save the trace using the helper script:

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1
if [ -z "${ARIS_REPO:-}" ] && [ -f .aris/installed-skills.txt ]; then
  ARIS_REPO=$(awk -F'\t' '$1=="repo_root"{print $2; exit}' .aris/installed-skills.txt 2>/dev/null) || true
fi
SAVE_TRACE=".aris/tools/save_trace.sh"
[ -f "$SAVE_TRACE" ] || SAVE_TRACE="tools/save_trace.sh"
if [ ! -f "$SAVE_TRACE" ]; then
  if [ -n "${ORBIT_REPO:-}" ] && [ -f "$ORBIT_REPO/tools/save_trace.sh" ]; then
    SAVE_TRACE="$ORBIT_REPO/tools/save_trace.sh"
  elif [ -n "${ARIS_REPO:-}" ] && [ -f "$ARIS_REPO/tools/save_trace.sh" ]; then
    SAVE_TRACE="$ARIS_REPO/tools/save_trace.sh"
  else
    SAVE_TRACE=""
  fi
fi

[ -n "$SAVE_TRACE" ] && bash "$SAVE_TRACE" \
  --skill "<skill-name>" \
  --purpose "<purpose>" \
  --model "<model>" \
  --thread-id "<agent id from response>" \
  --prompt "<full prompt as sent>" \
  --response "<full response content>"
```

The script handles directory creation, run numbering, and file writing.

If `save_trace.sh` is not available at `.aris/tools/`, project `tools/`, or
`$ORBIT_REPO|$ARIS_REPO/tools/` (e.g., on Codex CLI), write the files directly
following the schema below.

## File Schemas

### `run.meta.json`
```json
{
  "skill": "auto-review-loop",
  "run_id": "2026-04-15_run01",
  "started_at": "2026-04-15T14:30:00+08:00",
  "executor": "claude-code",
  "project_dir": "/path/to/project"
}
```

### `NNN-<purpose>.request.json`
```json
{
  "call_number": 1,
  "purpose": "round-1-review",
  "timestamp": "2026-04-15T14:31:00+08:00",
  "tool": "spawn_agent",
  "model": "gpt-5.5",
  "config": {"model_reasoning_effort": "xhigh"},
  "files_referenced": ["paper/sections/3_method.tex", "results/table1.csv"],
  "prompt": "<full prompt text>"
}
```

### `NNN-<purpose>.response.md`
The reviewer's full response, verbatim. No truncation, no summarization.

### `NNN-<purpose>.meta.json`
```json
{
  "call_number": 1,
  "purpose": "round-1-review",
  "timestamp": "2026-04-15T14:33:00+08:00",
  "thread_id": "019d8fe0-b25d-...",
  "model": "gpt-5.5",
  "duration_ms": 142000,
  "status": "ok"
}
```

## Configuration

Tracing respects three modes, set via inline parameter `--- trace: off | meta | full`:
- **`full`** (default): save full prompt + full response
- **`meta`**: save metadata only (no prompt/response text), useful for sensitive projects
- **`off`**: disable tracing entirely

## Integration with events.jsonl

After writing a trace, append a compact summary event to `.aris/meta/events.jsonl`:

```json
{"event":"review_trace","skill":"auto-review-loop","purpose":"round-1-review","thread_id":"...","trace_path":".aris/traces/auto-review-loop/2026-04-15_run01/","status":"ok"}
```

This allows `/meta-optimize` to discover traces without reading the full trace files.

## Privacy

- `.aris/traces/` should be in `.gitignore` — traces are project-local, never committed
- Traces may contain sensitive research content; treat them as confidential
- Use `--- trace: off` for projects with strict confidentiality requirements
