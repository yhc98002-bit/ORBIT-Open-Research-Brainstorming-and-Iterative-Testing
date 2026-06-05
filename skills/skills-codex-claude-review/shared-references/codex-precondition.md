# Claude CLI Reviewer Precondition + Loud-Stop Contract

This compatibility file intentionally replaces the upstream sub-agent precondition when `skills-codex-claude-review` is installed over `skills/skills-codex`.

## Entry-Time Precondition

Before any load-bearing review/helper call, verify the Claude CLI is available:

```bash
claude --version
```

If this fails, write the skill STATE as `awaiting_user_action` with `next_action: "fix-claude-cli-reviewer-then-reinvoke"` and stop before emitting downstream proposal, plan, diagnostic, claim, or paper artifacts.

## Reviewer Call Protocol

For every fresh review/helper call, write the complete focused prompt to `$PROMPT_FILE`. For one-shot independent review, run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

For a first call that may need follow-up discussion, create and save a session ID:

```bash
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(python -c 'import uuid; print(uuid.uuid4())')}"
CLAUDE_SESSION_ID_FILE="${CLAUDE_SESSION_ID_FILE:-.aris/review-outputs/claude-session-id.txt}"
printf "%s\n" "$CLAUDE_SESSION_ID" > "$CLAUDE_SESSION_ID_FILE"
claude -p --session-id "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

For follow-up rounds, resume that same Claude CLI session:

```bash
CLAUDE_SESSION_ID_FILE="${CLAUDE_SESSION_ID_FILE:-.aris/review-outputs/claude-session-id.txt}"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(cat "$CLAUDE_SESSION_ID_FILE")}"
test -n "$CLAUDE_SESSION_ID"
claude -p --resume "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

For follow-up rounds, include the previous raw Claude JSON/review, implemented changes, any pushback, and the current artifact in the prompt even though the session is resumed. The session provides conversational continuity; the artifacts provide auditability and recovery.

## Mid-Run Failure

If a required Claude CLI call fails, preserve upstream artifacts already written, write STATE with `status: "awaiting_user_action"` and a `reviewer_call_failure` block, and stop. Do not produce a single-model substitute artifact unless the skill documents and the user explicitly selects a degraded-mode override.
