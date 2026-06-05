# Claude CLI Review Transport

Use this transport when a Codex skill needs an independent Claude Code review.

Do not call `mcp__claude-review__review_start`,
`mcp__claude-review__review_reply_start`, or
`mcp__claude-review__review_status`. Do not require
`codex mcp add claude-review`.

Follow this exact command shape:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max "<focused review or help prompt>"
```

For long prompts, write the complete prompt to a temporary review prompt file
under `.aris/review-prompts/` or `review-stage/prompts/`, then pass the file
contents to the same command:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max "$(cat "$PROMPT_FILE")"
```

If the shell argument length would be unsafe, pipe the prompt through stdin
while keeping the same flags:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE"
```

Save the raw JSON output before summarizing it. Use paths such as
`review-stage/claude-review-round-N.json`,
`refine-logs/claude-review-round-N.json`, or the skill's existing review log
directory. Treat the response text inside the JSON as the reviewer output; if
the exact JSON field is uncertain, preserve the full JSON and quote/summarize
only from that saved artifact.

There is no MCP `threadId`, `jobId`, polling, or reply endpoint. For follow-up
rounds, start a new `claude -p` invocation and include the previous raw review,
the implemented changes, any pushback, and the current artifact in the prompt.
