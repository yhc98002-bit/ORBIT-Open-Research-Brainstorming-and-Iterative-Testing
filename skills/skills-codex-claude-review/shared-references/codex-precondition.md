# Claude CLI Reviewer Precondition + Loud-Stop Contract

This compatibility file intentionally replaces the upstream sub-agent precondition when `skills-codex-claude-review` is installed over `skills/skills-codex`.

## Entry-Time Precondition

Before any load-bearing review/helper call, verify the Claude CLI is available:

```bash
claude --version
```

If this fails, write the skill STATE as `awaiting_user_action` with `next_action: "fix-claude-cli-reviewer-then-reinvoke"` and stop before emitting downstream proposal, plan, diagnostic, claim, or paper artifacts.

## Reviewer Call Protocol

For every fresh review/helper call, write the complete focused prompt to `$PROMPT_FILE`, then run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

For follow-up rounds, start a new `claude -p` invocation and include the previous raw Claude JSON/review, implemented changes, any pushback, and the current artifact in the prompt. Claude CLI has no persistent `threadId`.

## Mid-Run Failure

If a required Claude CLI call fails, preserve upstream artifacts already written, write STATE with `status: "awaiting_user_action"` and a `reviewer_call_failure` block, and stop. Do not produce a single-model substitute artifact unless the skill documents and the user explicitly selects a degraded-mode override.
