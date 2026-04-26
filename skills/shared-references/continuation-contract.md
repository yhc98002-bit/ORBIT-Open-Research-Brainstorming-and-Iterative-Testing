# ORBIT v1.3 Continuation Contract

> **Canonical state-aware continuation protocol for ORBIT skills.** This file unifies how
> any long-running skill records progress, pauses for human review, recovers from
> interruption, and signals downstream skills that it is ready to be resumed. Every skill
> that emits a `*_STATE.json` file should follow this contract.

## Why this exists

Two real failure modes were colliding in v1.0/v1.1:

1. **Deliberate human checkpoint** — the user wants to inspect a milestone artifact (e.g.
   the proposal) before authorising the next phase. Without a "pause" status, the skill
   either runs through (defeating the checkpoint) or stops without leaving a re-entry signal.
2. **Unintended interruption** — Codex API timeout, context compaction, terminated SSH
   session, kernel restart. Without a state file, the next invocation re-runs completed
   phases and burns tokens / GPU hours.

Both reduce to the same primitive: **the next caller (whether it is the same skill, a
different skill, or a human re-invoking) must be able to look at on-disk state and
correctly decide what to do.**

## STATE.json schema (canonical)

Every skill that participates in the contract writes a single JSON file at a stable path:

```
<output-dir>/<SKILL_NAME>_STATE.json
```

Schema:

```jsonc
{
  "skill": "idea-to-proposal",                 // skill name (must match the invocation handle)
  "phase": "innovation",                       // last COMPLETED phase
  "round": 0,                                  // optional, for loop skills (auto-review-loop, auto-paper-improvement-loop, research-refine)
  "status": "awaiting_human_continue",         // one of: in_progress | awaiting_human_continue | completed
  "next_action": "phase-4-final-refinement",   // free-text hint for the same skill on resume
  "next_skill_hint": "/research-pipeline OR /experiment-plan",  // free-text hint for downstream
  "timestamp": "2026-04-26T15:30:00Z",         // ISO 8601 UTC, when this state was last written
  "artifact_inventory": [                      // every output artifact this skill has produced so far
    "orbit-research/PROBLEM_SELECTION.md",
    "orbit-research/ASSUMPTION_LEDGER.md",
    "refine-logs/FINAL_PROPOSAL.md"
  ],
  "notes": "Optional free-text — e.g. context compaction summary, reviewer thread id"
}
```

**Required fields:** `skill`, `phase`, `status`, `timestamp`, `artifact_inventory`.
**Recommended:** `next_action`, `next_skill_hint`.
**Optional:** `round`, `notes`, plus any skill-specific fields (e.g. `threadId`,
`pending_experiments`).

Skills MAY add their own fields. Contract consumers MUST tolerate unknown fields.

## status enum (three states)

| status | Meaning | Set when | Re-invocation behavior |
|---|---|---|---|
| `in_progress` | Skill is mid-execution OR has been interrupted mid-execution | Written at every phase boundary while phases still remain | If `timestamp < 24h` → resume from `phase + 1` (or replay current phase if its output artifact is incomplete). If `timestamp ≥ 24h` → treat as stale, prompt user, default to fresh start. |
| `awaiting_human_continue` | Skill paused at an intentional human checkpoint and is waiting for explicit go-ahead | Written when the skill reaches a stop point that is meant to be reviewed by a human (e.g. proposal complete, before downstream commitment) | Same skill re-invoked: ask user "continue past last checkpoint?" then resume. Downstream skill invoked: treat as "human approved continue", load `artifact_inventory`, route past the completed phases. |
| `completed` | Skill finished its full lifecycle | Written at the end of the last phase | Re-invocation = fresh start (with a one-line warning "previous run completed; existing artifacts will be overwritten unless `— resume: true` is passed"). |

The third state (`awaiting_human_continue`) is what the v1.0/v1.1 schema lacked. Without
it, "user manually paused for review" was indistinguishable from "skill is mid-execution",
forcing skills to either always pause (defeating automation) or never pause (defeating
human review).

## Lifecycle rules

1. **Write at every phase boundary.** Overwrite the same path each time — only the latest
   state matters. State files are not append-only logs.

2. **`in_progress` is the default during execution.** Do not write `completed` until the
   final phase actually finishes. Do not write `awaiting_human_continue` unless the skill
   reached a designed checkpoint (typically the last phase before a downstream skill must
   be invoked).

3. **24-hour staleness rule.** When a re-invocation finds `status = "in_progress"` AND
   `timestamp` is more than 24 hours old, treat it as stale. Default action: warn user,
   delete the file, fresh start. Reason: a `in_progress` state older than 24h almost
   certainly means a killed/abandoned run, not a real pause.

4. **Idempotent stage skip.** Each phase should first check whether its expected output
   artifact already exists AND the STATE entry says this phase is complete. If both
   conditions hold, skip the phase, log "skipped (already done from prior run)". This
   protects against partial-overwrite when a phase gets interrupted halfway through
   writing its output.

5. **Status transitions are unidirectional within a run.**
   `in_progress` → `awaiting_human_continue` → `in_progress` (next call) → `completed`.
   `awaiting_human_continue` → `completed` is allowed when the human only wanted to inspect
   without continuing (the next invocation can flip to completed if all required phases
   are done).

## Resume semantics

When a skill is invoked and finds an existing STATE file, the decision tree is:

```
1. Read STATE. Validate schema.
   - If schema invalid: warn, treat as fresh start.
2. status = "completed":
   - Without — resume: true → fresh start (warn: "overwriting prior run's artifacts").
   - With — resume: true → no-op, exit (already done).
3. status = "in_progress":
   - timestamp ≥ 24h → stale. Prompt user. Default: delete STATE, fresh start.
   - timestamp <  24h → resume. Find next phase to run (after STATE.phase). For each
     phase already in STATE, idempotent skip if artifact present. Replay current phase
     if its artifact is incomplete or missing.
4. status = "awaiting_human_continue":
   - Same skill being re-invoked → ask "continue past human checkpoint?" Default to yes
     under AUTO_PROCEED=true. On yes, transition to in_progress and continue.
   - Downstream skill being invoked (different skill name) → treat as "human approved
     continue", load artifact_inventory, route past the upstream skill's completed phases.
```

## Cross-skill resume semantics

Downstream skills MUST inspect upstream STATE files when their input could be a
continuation rather than a fresh start. The mechanism:

1. **Conventional STATE locations** — every skill writes its STATE in a predictable path:
   - `orbit-research/<SKILL>_STATE.json` for v1.3 ORBIT-Spine skills
   - `refine-logs/REFINE_STATE.json` for /research-refine (legacy path, preserved)
   - `review-stage/REVIEW_STATE.json` for /auto-review-loop (legacy path, preserved)
   - `paper/.aris/IMPROVEMENT_STATE.json` for /auto-paper-improvement-loop (legacy)

2. **Glob discovery on entry** — orchestrator skills (e.g. `/research-pipeline`) glob
   `orbit-research/*_STATE.json` and `refine-logs/*_STATE.json` and `review-stage/*_STATE.json`
   to enumerate any prior continuation that might apply.

3. **Routing by status:**
   - If any upstream STATE has `status = "awaiting_human_continue"` and its
     `artifact_inventory` covers the prerequisites for a downstream stage → route
     directly to that stage. The user's act of invoking the downstream skill is the
     "approve" signal.
   - If any upstream STATE has `status = "in_progress"` and `timestamp < 24h` → warn the
     user that an upstream skill was mid-execution; offer to resume the upstream first.
   - Otherwise → treat user input as a fresh `$ARGUMENTS` and run the orchestrator's
     normal routing.

4. **Artifact-presence override** — even without a STATE file, if the orchestrator finds
   v1.3 artifacts already on disk (e.g. `orbit-research/PROBLEM_SELECTION.md` +
   `ASSUMPTION_LEDGER.md` + `ABSTRACT_TASK_MECHANISM.md` + `ALGORITHM_TOURNAMENT.md` all
   present), it should infer "Discovery+Grounding+Innovation already done" and route to
   commitment stages, regardless of whether a STATE file is present.

## Override flags (user-facing)

Every skill that supports the contract MUST honour these inline flags:

| Flag | Meaning |
|---|---|
| `— resume: true` | Force resume even if STATE looks ambiguous (e.g. > 24h stale). |
| `— fresh: true` | Ignore any STATE / existing artifacts. Delete STATE first, run from phase 0. Warns about overwrite. |
| `— from-phase: <N>` | Start from a specific phase (skill-specific naming; orchestrators may use `— from-stage: <N>` instead). |
| `— human checkpoint: true` | Force pause-and-write `awaiting_human_continue` after every phase boundary, not just at the designed checkpoint. |
| `— no-checkpoint: true` | Override skill's default `awaiting_human_continue` exit and run straight through to `completed`. |

Flag precedence (highest first): `— fresh:` > `— from-phase:` > `— resume:` > STATE-based default.

## Artifact-presence idempotency

Before running any phase whose output artifact has a deterministic path:

```text
expected_artifact = <output-dir>/<PHASE_OUTPUT>.md
if expected_artifact exists AND STATE says this phase is "completed":
    skip phase, log "skipped (artifact + state both indicate completed)"
elif expected_artifact exists AND STATE absent or older:
    warn "artifact present but STATE inconsistent; running phase to refresh"
    run phase, overwrite artifact
else:
    run phase normally
```

This protects against:
- Partial writes where the artifact was created but STATE didn't update before crash
- Re-runs where the user expected idempotency but the skill rewrote a file unnecessarily
- Orphan artifacts left over from a `— fresh:` user that wants a clean rerun

## Skill author checklist

When adding a new skill or upgrading an existing one to follow this contract:

- [ ] Define the STATE.json path (one per skill, predictable location).
- [ ] Write STATE at every phase boundary (after the phase completes, before the next
      phase begins).
- [ ] On entry, read STATE and apply the resume decision tree.
- [ ] Implement idempotent stage skip per the artifact-presence rule.
- [ ] Honour `— resume:`, `— fresh:`, and (where it makes sense) `— human checkpoint:` flags.
- [ ] On the last phase, set `status = "completed"`.
- [ ] If the skill has a designed human checkpoint (e.g. before downstream commitment),
      set `status = "awaiting_human_continue"` at that point and include `next_skill_hint`.
- [ ] Add the skill's STATE path to `next_skill_hint` of upstream skills if applicable.
- [ ] Document the STATE schema in the skill's SKILL.md, referencing this contract by
      name rather than redefining.

## Backward compatibility

Skills that already had STATE.json schemas before this contract (`/research-refine`,
`/auto-review-loop`, `/auto-paper-improvement-loop`, `/experiment-queue`) keep their
existing paths and field names. The schema upgrade adds:

- `status` enum gains `awaiting_human_continue` (previously only `in_progress` /
  `completed`).
- `next_action` / `next_skill_hint` / `artifact_inventory` fields are recommended but
  optional. Old STATE files without them still parse.
- Resume decision tree above replaces the per-skill ad-hoc resume logic. Old skills'
  current logic already implements steps 1–3 of the tree; they just need step 4 added
  for the new `awaiting_human_continue` state.

Old skill consumers (e.g. `/research-pipeline` v1.2 routing) that did NOT inspect
upstream STATE files continue to work — they just won't benefit from cross-skill resume
until they're upgraded. There is no breaking change.

## Anti-patterns

- **Append-only STATE log.** STATE.json is overwritten each phase. Use a separate
  `<SKILL>_LOG.md` if you want a history.
- **Status = "running" or "active".** Use `in_progress` exactly. Three-state enum is
  fixed: `in_progress | awaiting_human_continue | completed`.
- **Multiple STATE files per skill.** One skill, one STATE file. If a skill has nested
  loops with their own state, persist them in the parent STATE under sub-fields, not
  separate files.
- **Silent overwrite of `completed` STATE.** If a re-invocation finds `completed` and the
  user did not pass `— resume:` or `— fresh:`, warn before overwriting; do not silently
  re-run.
- **Reading STATE without writing it.** Orchestrator skills MAY read upstream STATE for
  routing purposes without writing their own STATE; but any skill that runs phases must
  write STATE per the contract.
