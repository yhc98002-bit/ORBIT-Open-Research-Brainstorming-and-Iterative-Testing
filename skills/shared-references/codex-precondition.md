# Codex Precondition + Loud-Stop Contract

> Single source of truth for **how every ORBIT skill that invokes
> `mcp__codex__codex` checks Codex availability**, and **what it must do when
> Codex is unavailable or fails mid-run**.
>
> The default behavior is **LOUD STOP** — never silently fall back to
> single-model output. The whole point of the Codex collaborator/adversarial
> pattern is to prevent single-AI local optima; silently dropping Codex defeats
> the design. If the user explicitly wants single-model mode they must pass
> `— codex-required: false`.

## §1 Why this contract exists

Before this contract, the canonical fallback policy across skills was
"mark the artifact `NOT_AVAILABLE (codex_mcp_unreachable)` and continue."
That meant a skill could complete its full pipeline with **zero** Codex
contribution and the user would only discover it by reading STATE notes
after the fact. This contract replaces that policy with an entry-time
precondition check and an explicit mid-run failure protocol so the user
always knows when Codex did or did not participate.

## §2 When to apply

Every skill whose `allowed-tools` frontmatter contains `mcp__codex__codex`
or `mcp__codex__codex-reply` MUST apply this contract:

1. **At skill entry** (before Phase 0 writes any artifact): run the
   precondition check in §3.
2. **At every Codex call site** during the run: wrap the MCP call in the
   mid-run failure protocol in §5.

## §3 Entry-time precondition check

Run this bash one-liner as the first action in Phase 0, **before** the
skill writes any artifact and **before** any sub-skill delegation:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" setup --json
```

Parse the JSON. Codex is considered **ready** iff all of the following are
true:

| Field | Required value |
|---|---|
| `.ready` | `true` |
| `.codex.available` | `true` |
| `.auth.available` | `true` |
| `.auth.loggedIn` | `true` |

If any field is missing or false, apply §4 (loud stop).

A successful precondition check should be logged once in STATE:

```jsonc
{
  "codex_precondition": {
    "checked_at": "<ISO 8601>",
    "ready": true,
    "codex_cli_version": "<from .codex.detail>",
    "auth_method": "<from .auth.authMethod>",
    "session_runtime_mode": "<from .sessionRuntime.mode>"
  }
}
```

## §4 Loud-stop protocol (precondition failure)

When the precondition fails, the skill MUST:

1. **Not write any artifact for the current run.** No partial proposal, no
   half-grounding, no STATE.status = `in_progress`. The user must see a
   clean stop, not a half-finished bundle they have to clean up.
2. **Write STATE with `status: "awaiting_user_action"`** and an explicit
   `codex_unavailable_reason` block:

   ```jsonc
   {
     "skill": "<skill-name>",
     "phase": "phase-0-precondition",
     "status": "awaiting_user_action",
     "next_action": "fix-codex-then-reinvoke",
     "codex_unavailable_reason": {
       "ready": false,
       "codex_available": <bool>,
       "auth_logged_in": <bool>,
       "detail": "<raw .detail string from the failing field>",
       "raw_setup_json": "<entire JSON for debugging>"
     },
     "timestamp": "<ISO 8601>"
   }
   ```

3. **Print a user-facing message** (not just STATE; the user must see it):

   ```text
   ⛔ Codex is required for this skill but is not available.

   Reason: <one-line summary derived from the failing field>

   Fix steps:
     1. Run `/codex:setup` to install/login Codex CLI.
     2. If Codex CLI is installed but the MCP server isn't registered:
        `claude mcp add -s user codex -- codex mcp-server`
     3. After fixing, re-invoke this skill. STATE is preserved at
        awaiting_user_action so the rerun starts cleanly.

   Why no single-model fallback: ORBIT skills deliberately use Codex as
   collaborator/adversary to prevent single-AI local optima. Silently
   dropping Codex would defeat the design. Pass
   `— codex-required: false` if you explicitly want a degraded run.
   ```

4. **Exit the skill.** Do not invoke any sub-skill, do not run Phase 0.5
   literature pre-fetch (those are wasted work if the run will never
   complete), do not mkdir output directories.

## §5 Mid-run failure protocol

If `mcp__codex__codex` is callable at precondition time but a specific
invocation fails mid-run (network error, auth expired, sandbox rejection,
tool-call timeout, etc.):

1. **Capture the error** (the tool-call error message and any partial
   output).
2. **Update STATE** with the current phase, `status: "awaiting_user_action"`,
   and a `codex_call_failure` block:

   ```jsonc
   {
     "phase": "<current phase id>",
     "status": "awaiting_user_action",
     "next_action": "fix-codex-then-resume",
     "codex_call_failure": {
       "where": "<phase-3a-mechanism-ideation | phase-4-final-refinement | ...>",
       "mode": "COLLABORATIVE | ADVERSARIAL",
       "error": "<error string>",
       "attempt_count": <int>
     },
     "timestamp": "<ISO 8601>"
   }
   ```

3. **Preserve artifacts produced before this point.** Unlike the
   precondition failure (which never writes), a mid-run failure may have
   written upstream artifacts. Leave them on disk; do not roll back.
4. **Print the same loud message as §4**, adapted to mid-run: name the
   phase that failed, name the artifact that was NOT written, and tell the
   user that re-invoking the skill will resume from the failed phase.
5. **Do not retry silently.** A single automatic retry is fine *if and only
   if* the error is clearly transient (e.g. HTTP 429); always log the
   retry and its outcome. Do not auto-retry on auth, sandbox, or model
   errors.
6. **Do not produce a single-model substitute artifact for this phase.**
   The point of Codex participation is non-negotiable for the gates that
   require it; substituting a Claude-only artifact and marking it
   `degraded` is exactly the silent-skip behavior this contract replaces.

## §6 Override: `— codex-required: false`

The only way to deliberately run a Codex-using skill without Codex is to
pass `— codex-required: false` in `$ARGUMENTS`. When this flag is present:

- The precondition check still runs, but a failure logs a single warning
  and continues.
- Every artifact that would have included Codex output gets a clearly
  visible degraded-mode header **at the top of the file** (not at the
  bottom in STATE notes):

  ```markdown
  > ⚠️ CODEX_REQUIRED=false — this artifact was produced in single-model
  > mode. Treat all collaborator suggestions, adversarial findings, and
  > tournament adjudications as unaudited. Re-run with Codex available
  > before relying on this artifact for downstream commitment gates.
  ```

- STATE records `codex_required: false` and `codex_skipped_in_phases: [...]`
  so downstream skills can decide whether the upstream artifact is
  trustworthy enough to consume.

This flag is for the rare case where the user wants the pipeline to run
*at all* despite Codex being broken — e.g. while a fix is in flight. It
is NOT the default and it is NOT the fallback path for Codex-call errors.

## §7 What this contract deliberately does NOT do

- Does NOT define the Codex prompt templates. Those live in
  `innovation-loops.md §7.1/§7.2` (collaborative/adversarial bodies) and
  `semantic-code-audit.md` (audit bodies). This contract is only about
  availability + failure semantics.
- Does NOT switch invocation paths. The canonical invocation is still
  `mcp__codex__codex` (the MCP tool). If the underlying transport ever
  changes (e.g. to the `codex:` plugin runtime), update §3's setup probe
  and the invocation tool name in one place; do not duplicate the change
  across every skill.
- Does NOT relax mode-switching. Stages 8/9/10/18.5 are COLLABORATIVE,
  Stages 11/14/15/17/21/23 are ADVERSARIAL, per
  `innovation-loops.md §7`. The precondition check is mode-independent.

## §8 Implementation checklist for skill authors

When adding `mcp__codex__codex` to a new skill:

- [ ] Frontmatter `allowed-tools:` lists `mcp__codex__codex` (and
      `mcp__codex__codex-reply` if multi-turn).
- [ ] Skill body has a "## Codex Precondition" section near the top
      pointing at this file (`shared-references/codex-precondition.md`).
- [ ] Phase 0 instructions include the §3 setup check as the first step.
- [ ] Every `mcp__codex__codex` call site references the §5 mid-run
      protocol.
- [ ] STATE schema includes `codex_precondition` (§3) and
      `codex_call_failure` (§5) fields.
- [ ] User-facing override flag `— codex-required: false` is honored
      and propagated to any sub-skill that also uses Codex.

## §9 Diagnostic command for the user

If a user is unsure whether Codex is ready, they can run the same check
this contract uses, without invoking any skill:

```bash
node "${CLAUDE_PLUGIN_ROOT}/scripts/codex-companion.mjs" setup --json
```

Or the equivalent slash command:

```text
/codex:setup
```

Both report the same `ready: true|false` verdict.
