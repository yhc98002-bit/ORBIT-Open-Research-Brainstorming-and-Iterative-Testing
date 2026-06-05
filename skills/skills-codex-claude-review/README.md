# skills-codex-claude-review

This package is a **thin override layer** for users who want:

- **Codex** as the main executor
- **Claude Code** as the reviewer
- direct Claude Code CLI review/help calls instead of a second Codex reviewer

It is designed to sit on top of the upstream Codex-native package at `skills/skills-codex/`.

## What this package contains

- Overrides for every `skills/skills-codex/` skill whose Markdown contains
  `spawn_agent` or `send_input`
- Transformed prompt files for those overridden skills when they contain
  reviewer/helper transport instructions
- No replacement for the base `skills/skills-codex/` installation

Regenerate the override set with:

```bash
python tools/generate_codex_claude_review_overrides.py
```

## Install

1. Install the base Codex-native skills first:

```bash
mkdir -p ~/.codex/skills
cp -a skills/skills-codex/* ~/.codex/skills/
```

2. Install the Claude-review overrides second:

```bash
cp -a skills/skills-codex-claude-review/* ~/.codex/skills/
```

3. Ensure the Claude Code CLI is available:

```bash
claude --version
```

The override skills invoke Claude review/help using this protocol.

For one-shot independent review:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max "your focused review or help prompt"
```

For automated multi-round review/discussion, keep `-p` but preserve session
continuity:

```bash
claude -p --session-id "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE"
claude -p --resume "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$NEXT_PROMPT_FILE"
```

Use fully interactive `claude --model opus --effort max` only for human-in-the-loop
discussion, not for autonomous skill phases.

## Why this exists

The upstream `skills/skills-codex/` path already supports Codex-native
execution with a second Codex reviewer/helper via `spawn_agent` and
`send_input`.

This package adds a different split:

- executor: Codex
- reviewer/helper: Claude Code CLI
- transport: direct `claude -p` CLI calls, with `--session-id` / `--resume`
  when the upstream skill expects multi-round reviewer continuity

For long paper and review prompts, write the full prompt to a temporary prompt
file and pass it to the CLI command. See
`shared-references/claude-cli-review.md`.

This avoids depending on a local Codex MCP bridge for Claude review.
