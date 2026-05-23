# Codex Standalone Review Handoff

Codex remains required for ORBIT review gates. This handoff exists only for cases where
the Codex MCP/auth/sandbox path fails but the user can still run Codex manually in a
terminal.

## Paths

- Prompt export: `orbit-research/codex-prompts/<phase-id>.md`
- Prompt metadata: `orbit-research/codex-prompts/<phase-id>.json`
- Manual response import path: `orbit-research/codex-imports/<phase-id>.response.md`

## Producer Flow

When a Codex MCP call fails, the producing skill writes a standalone prompt:

```bash
python3 tools/codex_review_handoff.py generate \
  --repo . \
  --phase-id "<phase-id>" \
  --role "<required Codex role>" \
  --file "<artifact to read>" \
  --objective "<review objective>" \
  --output-format "<required schema/verdict format>" \
  --required-section "VERDICT" \
  --output-artifact "<expected review artifact>" \
  --write-orbit-state
```

`ORBIT_STATE.json` should be `blocked` or `paused`, with:

```json
{
  "pause_reason": "codex_review_needed",
  "safe_next_command": "/import-codex-review orbit-research/codex-imports/<phase-id>.response.md"
}
```

## User Flow

1. Open `orbit-research/codex-prompts/<phase-id>.md`.
2. Paste/run it in standalone Codex.
3. Save the complete response to:

   ```text
   orbit-research/codex-imports/<phase-id>.response.md
   ```

4. Run:

   ```text
   /import-codex-review orbit-research/codex-imports/<phase-id>.response.md
   ```

## Import Rules

The import path is conservative:

- Missing required sections or verdict tokens blocks import.
- A response saying it could not access/read the files blocks import.
- A short/non-substantive response blocks import.
- Import copies the response into the expected review artifact only after validation.

This is not a single-model fallback. Review is marked satisfied only when an MCP Codex
response or an imported standalone Codex response exists.
