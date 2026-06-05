# Claude CLI Review Protocol

Use this protocol when Codex is the main executor and Claude Code is the
reviewer/helper.

Do not call `mcp__claude-review__review_start`,
`mcp__claude-review__review_reply_start`, or
`mcp__claude-review__review_status`. Do not require
`codex mcp add claude-review`.

## Mode A: One-Shot Independent Review

Use this mode when the skill needs a single independent review, audit, or
sanity check and does not expect a follow-up conversation.

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max "<focused review or help prompt>"
```

For long prompts, write the complete prompt to a temporary review prompt file
under `.aris/review-prompts/` or `review-stage/prompts/`, then pipe the file
through stdin:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

## Mode B: Automated Multi-Round Review / Discussion

Use this mode when the original Codex-native skill would have used
`spawn_agent` followed by `send_input`, or when a stage expects iterative
review/refine/re-review.

The first reviewer/helper call creates and saves a Claude CLI session ID:

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-1.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-1.json}"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(python -c 'import uuid; print(uuid.uuid4())')}"
CLAUDE_SESSION_ID_FILE="${CLAUDE_SESSION_ID_FILE:-.aris/review-outputs/claude-session-id.txt}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
printf "%s\n" "$CLAUDE_SESSION_ID" > "$CLAUDE_SESSION_ID_FILE"

claude -p --session-id "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Every follow-up round resumes that session:

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
CLAUDE_SESSION_ID_FILE="${CLAUDE_SESSION_ID_FILE:-.aris/review-outputs/claude-session-id.txt}"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(cat "$CLAUDE_SESSION_ID_FILE")}"
test -n "$CLAUDE_SESSION_ID"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"

claude -p --resume "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

For follow-up rounds, include the previous raw Claude JSON/review, implemented
changes, any pushback, and the current artifact in the prompt even though the
session is resumed. The session provides conversational continuity; the
explicit artifacts provide auditability and recovery if session persistence is
unavailable.

Store both:

- `claude_session_id`: conversation continuity for `--resume`
- `RAW_REVIEW_JSON`: per-round immutable evidence for audit and parsing

## Mode C: Human Interactive Discussion

Use interactive Claude Code only when a human explicitly wants to discuss with
Claude live:

```bash
claude --dangerously-skip-permissions --model opus --effort max
```

Do not use interactive mode inside an autonomous skill phase, because it can
block Codex and does not produce stable JSON logs.

## Logging Rule

Save the raw JSON output before summarizing it. Use paths such as
`review-stage/claude-review-round-N.json`,
`refine-logs/claude-review-round-N.json`, or the skill's existing review log
directory. Treat the response text inside the JSON as the reviewer output; if
the exact JSON field is uncertain, preserve the full JSON and quote/summarize
only from that saved artifact.
