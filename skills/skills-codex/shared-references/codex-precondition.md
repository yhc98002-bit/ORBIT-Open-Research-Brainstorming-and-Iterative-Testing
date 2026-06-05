# Codex-Native Reviewer Precondition + Loud-Stop Contract

> Single source of truth for Codex-native ORBIT skills that require an
> independent reviewer. In Codex CLI, the reviewer transport is a secondary
> Codex sub-agent through `spawn_agent`; follow-up reviewer turns use
> `send_input`.

## Entry-Time Precondition

Do not run a shell helper and do not reference Claude Code plugin-root
variables. Codex-native skills do not use a plugin-root probe.

At skill entry, confirm from the current session that the Codex-native
multi-agent tools are available:

- `spawn_agent` for fresh independent reviewer calls;
- `send_input` for reviewer follow-up turns when the skill explicitly requires
  same-thread continuity.

If those tools are not available and the skill marks reviewer participation as
load-bearing, write STATE with:

```jsonc
{
  "phase": "phase-0-precondition",
  "status": "awaiting_user_action",
  "next_action": "fix-codex-native-reviewer-then-reinvoke",
  "reviewer_unavailable_reason": {
    "ready": false,
    "transport": "codex-native-subagent",
    "detail": "<spawn_agent/send_input unavailable or failed>"
  }
}
```

Then stop before writing proposal, plan, diagnostic, claim, or paper artifacts.

## Reviewer Call Protocol

For a fresh independent review, call:

```text
spawn_agent:
  message: |
    [Full review prompt and required output schema]
```

For a continuation in the same reviewer conversation, call:

```text
send_input:
  target: <agent id returned by spawn_agent>
  message: |
    [Follow-up prompt]
```

Save the returned agent id when continuity is required. If a skill requires
fresh-context independence, start a new `spawn_agent` call instead of using
`send_input`.

## Mid-Run Failure

If a required reviewer call fails, preserve upstream artifacts already written,
write STATE with `status: "awaiting_user_action"` and a
`reviewer_call_failure` block, and stop. Do not produce a single-model
substitute artifact for a reviewer-required gate unless the user explicitly
passes `-- reviewer-required: false` or the skill documents an equivalent
degraded-mode override.
