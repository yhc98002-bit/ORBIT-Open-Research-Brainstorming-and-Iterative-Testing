---
name: import-codex-review
description: "Import a manually run standalone Codex review response after Codex MCP/auth/sandbox failure. Use when ORBIT wrote orbit-research/codex-prompts/<phase-id>.md and the user saved the standalone Codex output to orbit-research/codex-imports/<phase-id>.response.md."
argument-hint: [orbit-research/codex-imports/<phase-id>.response.md]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob
---

# /import-codex-review

Import standalone Codex review response: **$ARGUMENTS**

## Purpose

This skill completes a required Codex review when the MCP path failed but the user ran the
exported prompt in a standalone Codex terminal. It does not replace Codex with local
single-model judgment. Import satisfies only the Codex transport gap; it is not human
approval and does not authorize STOP C paper handoff by itself.

## Preconditions

- `orbit-research/codex-prompts/<phase-id>.md` exists.
- `orbit-research/codex-prompts/<phase-id>.json` exists when the producer recorded import
  metadata.
- `$ARGUMENTS` points to `orbit-research/codex-imports/<phase-id>.response.md`.

If any prerequisite is missing, stop with a blocker. Do not mark review passed.

## Workflow

1. Run conservative validation:

   ```bash
   python3 tools/codex_review_handoff.py validate "$ARGUMENTS" --repo .
   ```

   The validator reads `orbit-research/codex-prompts/<phase-id>.json`. If the metadata
   sets `verdict_required: true`, it must find exactly one final verdict token from
   `expected_verdict_tokens`. Markdown wrappers such as `Final verdict:
   **REQUIRES_FIXES**` are allowed. Candidate lists with pipe separators after
   `Final verdict:` and vague `# VERDICT` prose are rejected.

2. If validation fails, report the missing sections/tokens and keep ORBIT blocked or
   paused with `pause_reason: codex_review_needed`.

3. If validation passes, import through the recorded metadata:

   ```bash
   python3 tools/codex_review_handoff.py import "$ARGUMENTS" --repo .
   ```

4. Confirm the target artifact or pack field was written.

5. Confirm `orbit-research/ORBIT_STATE.json` now preserves the producer context from the
   handoff metadata:
   - review source: `standalone_codex_import`
   - imported response path: `$ARGUMENTS`
   - status: `paused`
   - `pause_reason: codex_review_imported`
   - safe next command: resume the producer skill, or `/orbit-status` if the original
     context was unknown

## Rules

- Do not accept a response that omits required sections from the exported prompt.
- For phase-specific load-bearing reviews, do not accept a response that lacks exactly
  one configured final verdict token.
- Do not summarize the response into a pass verdict by yourself.
- Do not fabricate missing reviewer findings or verdict tokens.
- Do not treat import as `HUMAN_DECISION_NOTE.md` approval or STOP C `PROCEED`.
- Do not continue downstream gates unless an MCP response or imported standalone response
  exists.
- After import, resume the producer skill or inspect the relevant STOP review. Do not jump
  directly to `/paper-from-claims` or `/submission-package` unless STOP C approval gates
  are already satisfied.

## Recovery

If import fails, ask the user to re-run standalone Codex with:

```text
orbit-research/codex-prompts/<phase-id>.md
```

and save the full response to:

```text
orbit-research/codex-imports/<phase-id>.response.md
```
