---
name: "idea-to-proposal"
description: "ORBIT v1.4 proposal wrapper that turns a research-area keyword, long context .md, or draft idea .md into an approved-proposal candidate. Runs non-experimental Discovery, Grounding, Innovation, and final proposal refinement, then stops before experiment planning. Canonical STOP A output is proposal/proposal_pack.json; Markdown proposal files are generated or legacy compatibility views. Does NOT write canonical EXPERIMENT_PLAN.md / EXPERIMENT_PLAN_EXEC.md, implement formal experiment code, run experiments, use GPU, or produce paper-level diagnostic evidence. Use when user says \"领域到proposal\", \"出proposal\", \"想法到方案\", \"idea-to-proposal\", \"proposal pipeline\", or \"从领域跑到方案\"."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill
---

> Override for Codex users who want **Claude Code CLI**, not a second Codex agent, to act as the reviewer/helper. Install this package **after** `skills/skills-codex/*`.

Whenever the upstream skill asks for an external reviewer/helper, write the complete focused prompt to `$PROMPT_FILE`. For a one-shot independent review, run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

For multi-round reviewer discussion, keep automation non-interactive but preserve continuity with `--session-id` on the first call and `--resume` on follow-up calls; see `../shared-references/claude-cli-review.md`.

# /idea-to-proposal — v1.4 Discovery → Grounding → Innovation → Proposal

Run a proposal-generation pipeline for: **$ARGUMENTS**

## Overview

This skill chains existing skills plus the ORBIT Grounding and Innovation phases into a
proposal wrapper. It produces `proposal/proposal_pack.json` as the STOP A source of
truth, then renders human-readable proposal views from that pack:
- `proposal/PROPOSAL.md`
- `proposal/METHOD_SPEC.md` when implementation-level detail is useful
- legacy compatibility copies under `refine-logs/` when needed

The Discovery/Grounding/Innovation structure is preserved inside the pack:
problem selection, assumption ledger, abstract task / mechanism, baseline ceiling,
mechanism ideation, analogy transfer, and algorithm sketch tournament. Old
`orbit-research/*.md` artifacts may still be generated during migration, but they are
compatibility views and audit breadcrumbs, not the canonical AI source of truth.

Version note: `v1.4` names this STOP wrapper behavior. The underlying artifact names,
stage numbers, and hard gates remain the ORBIT v1.3 contract in
`../shared-references/research-agent-pipeline.md`.

**Scope boundary** — this skill stops before formal experiment planning. It does not write
canonical `EXPERIMENT_PLAN.md` / `EXPERIMENT_PLAN_EXEC.md`, does not implement formal
experiment code, does not run experiments, does not use GPU, and does not produce
paper-level diagnostic evidence. When delegating to `/idea-discovery`, no experiments are
run; idea discovery is non-experimental in ORBIT v1.4+. After STOP A, hand the
approved proposal pack to `/experiment-bridge "proposal/proposal_pack.json"` (the
experiment-bridge pack input is enabled in a follow-on migration prompt).

```
Input:          Phase 1 (Discovery)      Phase 2 (Grounding)   Phase 3 (Innovation, Codex collab)   Phase 4               Phase 5
keyword ──────► /idea-discovery ────┐
context .md ──► /idea-discovery ────┤
draft idea .md ─► /research-refine ─┴► Stage 4 → 5 → 7 ─────► Stage 8 → 9 → 10 ─────────────────► /research-refine ──► PIPELINE_
                                      (assumption,            (mechanism, analogy,                 final pass            SUMMARY
                                       abstract, baseline)     sketch tournament)                  (winner integrated)
                                                                                                                       │
                                                                                                                       ▼
                                                                                                             ⏸ STOP A: human-review-proposal
```

## Constants

- **OUTPUT_ROOT_V13 = `orbit-research/`** — v1.3 grounding + innovation compatibility views.
- **OUTPUT_ROOT_PROPOSAL = `proposal/`** — canonical STOP A pack and primary Markdown views.
- **OUTPUT_ROOT_PROPOSAL_LEGACY = `refine-logs/`** — compatibility copies such as
  `FINAL_PROPOSAL.md`, `FINAL_PROPOSAL_SHORT.md`, and `METHOD_SPEC.md`.
- **CLAUDE_REVIEW_MODEL = `claude-cli`**, **CLAUDE_REVIEW_EFFORT = `xhigh`**.
- **PAPER_MODE = `normal`** — Default to a normal publishable AI paper; breakthrough
  mode is explicit opt-in only.
- **NOVELTY_POLICY = `positioning-first`** — Similar/concurrent work is classified and
  positioned before any proposal rewrite or abandonment.
- **REVIEW_POSTURE = `collaborator` before STOP A** — Early review preserves promising
  directions and proposes survival routes. Use adversarial posture only after STOP C or
  explicit user request.
- **CLAUDE_INNOVATION_MODE** — `COLLABORATIVE` for Phase 3 (Stages 8/9/10); `CALIBRATION`
  for the Phase 4 final refinement review.
- **AUTO_PROCEED = true** — chain phases without prompting unless user passes
  `— human checkpoint: true`.
- **LITERATURE_PRE_FETCH_DEFAULT = false** — when `— arxiv download: true` is passed,
  set to true and run **Phase 0.5 (Literature Pre-fetch)** before Phase 1. Default false
  preserves prior behavior of running grounding off whatever the LLM already knows
  about the area.
- **LITERATURE_PRE_FETCH_SOURCES_DEFAULT = `"arxiv"`** — default sources for Phase 0.5;
  override with `— sources: <list>` (any subset of `arxiv`, `web`, `semantic-scholar`,
  `deepxiv`, `exa`, `alphaxiv`, `local`, `all`).
- **LITERATURE_PRE_FETCH_MAX_DEFAULT = 10** — default cap on PDFs downloaded by
  Phase 0.5; override with `— arxiv max download: <N>`.
- **DIFFICULTY_DEFAULT = `"medium"`** — calibrates downstream `/research-refine`
  reviewer behavior, READY threshold, and MAX_ROUNDS via the canonical upstream three
  levels (mirrors `/auto-review-loop`'s `REVIEWER_DIFFICULTY` and
  `/research-pipeline`'s `REVIEWER_DIFFICULTY` so the same flag string propagates):
  - `medium` (default): standard reviewer prompt; SCORE_THRESHOLD = 9, MAX_ROUNDS = 5.
  - `hard`: stricter collaborator review (push back on sprawl, weak mechanism
    specificity, unfocused validation); SCORE_THRESHOLD = 9.5, MAX_ROUNDS = 7.
  - `nightmare`: before STOP A, interpret as strong collaborator review unless the user
    explicitly requests adversarial review; adversarial veto semantics belong after STOP C.
  Override with `— difficulty: <level>`. Forwarded verbatim to `/research-refine`.
- **STOP_AT_GROUNDING = false** — if `true`, skip Phase 3 and Phase 4 (produce only the
  Grounding artifacts on top of Phase 1 output).
- **WITH_EXPERIMENT_PLAN = false** — legacy compatibility only. Default `false` stops at
  STOP A after proposal refinement. If the user explicitly passes
  `— with-experiment-plan: true` or `— legacy-full-preimplementation: true`, the skill may
  invoke `/experiment-plan` after STOP A semantics, but this path is not recommended for
  new canonical ORBIT runs.
- **NO_PRE_STOP_A_EXPERIMENTS = true** — keyword/context mode may delegate to
  `/idea-discovery`, but `/idea-discovery` is non-experimental in ORBIT v1.4+. Do not run
  experiments, do not use GPU, and do not call `/run-experiment` before STOP A.

## Load First

- `../shared-references/research-agent-pipeline.md` — v1.3 stage definitions for the
  Grounding (Stages 4/5/7) and Innovation (Stages 8/9/10) blocks
- `../shared-references/research-harness-prompts.md` — sections `4`, `5`, `7`, `8`, `9`, `10`
  (the canonical prompt body for each stage this skill triggers)
- `../shared-references/innovation-loops.md` — Loop A/B/C procedures (sections §2/§3/§4) +
  Claude CLI collaborative-mode prompt template (§7.1)
- `../shared-references/continuation-contract.md` — STATE.json schema, four-state enum,
  resume/idempotency rules, override flags
- `../shared-references/reviewer-independence.md`
- `../shared-references/document-hygiene.md` — keep `FINAL_PROPOSAL` readable; route
  uncertainty and audit history to the correct artifacts
- `../shared-references/research-posture.md` — normal paper mode, positioning-first novelty,
  collaborator review before STOP A, concurrent-work watchlist, and proposal stability

## State Persistence (Continuation Contract)

This skill follows the ORBIT v1.3 continuation contract — read
`../shared-references/continuation-contract.md` for the canonical schema.

## STOP A Pack Contract

The canonical STOP A artifact is:

```text
proposal/proposal_pack.json
```

Populate it by calling or following the helper contract in `tools/orbit_pack.py`:

```bash
python tools/orbit_pack.py bootstrap --repo . --pack proposal_pack --write
python tools/orbit_pack.py render-proposal --repo . --write --legacy
```

The helper bootstrap is only an implementation aid; the skill must still place the
scientific content from Phases 1-4 into the structured pack fields:

- `problem_selection`
- `assumptions[]`
- `abstract_task`
- `baseline_headroom`
- `candidate_mechanisms[]`
- `selected_sketch`
- `open_risks[]`

Render human-readable views after the pack is updated:

- `proposal/PROPOSAL.md`
- `proposal/METHOD_SPEC.md` if method details are useful at STOP A
- `refine-logs/FINAL_PROPOSAL.md`, `refine-logs/FINAL_PROPOSAL_SHORT.md`, and
  `refine-logs/METHOD_SPEC.md` as legacy compatibility views only

Do not treat the legacy Markdown files as primary state once
`proposal/proposal_pack.json` exists.

At the STOP A terminal checkpoint, also write `orbit-research/ORBIT_STATE.json`:

```jsonc
{
  "schema_version": "0.1",
  "current_stop": "STOP_A",
  "current_skill": "idea-to-proposal",
  "current_phase": "phase-5-summary",
  "status": "paused",
  "pause_reason": "stop_review",
  "blockers": [],
  "canonical_packs": {
    "proposal_pack": "proposal/proposal_pack.json",
    "experiment_pack": "experiment/experiment_pack.json",
    "claim_ledger": "claims/claim_ledger.json",
    "paper_package": "paper/paper_package.json"
  },
  "legacy_artifacts_detected": ["refine-logs/FINAL_PROPOSAL.md"],
  "safe_next_command": "/experiment-bridge \"proposal/proposal_pack.json\"",
  "updated_at": "<ISO 8601 UTC>"
}
```

**STATE file:** `orbit-research/IDEA_TO_PROPOSAL_STATE.json`

Written at every phase boundary with overwrite semantics. Schema:

```jsonc
{
  "skill": "idea-to-proposal",
  "phase": "phase-3-innovation",         // last completed phase (one of:
                                          //   phase-0-intake, phase-0-5-literature-prefetch,
                                          //   phase-1-discovery, phase-2-grounding,
                                          //   phase-3-innovation, phase-4-final-refinement,
                                          //   phase-5-summary)
  "input_mode": "keyword" | "context" | "idea",      // detected at Phase 0
  "input_value": "$ARGUMENTS",           // verbatim
  "status": "in_progress" | "awaiting_human_continue" | "awaiting_user_action" | "completed",
  "next_action": "phase-4-final-refinement",        // for same-skill resume
  "next_skill_hint": "/experiment-bridge \"proposal/proposal_pack.json\"",  // downstream after STOP A
  "timestamp": "<ISO 8601 UTC>",
  "artifact_inventory": [               // every output produced so far
    "orbit-research/PROBLEM_SELECTION.md",
    "orbit-research/ASSUMPTION_LEDGER.md",
    "orbit-research/ABSTRACT_TASK_MECHANISM.md",
    "orbit-research/BASELINE_CEILING.md",
    "orbit-research/MECHANISM_IDEATION.md",
    "orbit-research/ANALOGY_TRANSFER.md",
    "orbit-research/ALGORITHM_TOURNAMENT.md",
    "proposal/proposal_pack.json",
    "proposal/PROPOSAL.md",
    "refine-logs/FINAL_PROPOSAL.md" // legacy compatibility view
  ],
  "notes": "Free-form notes — e.g. mode-detection rationale, Claude CLI reviewer unavailability events"
}
```

### On entry — resume decision tree

Apply the canonical decision tree from `continuation-contract.md`:

1. Read `orbit-research/IDEA_TO_PROPOSAL_STATE.json` (if exists) and `STATE.phase`,
   `STATE.status`, `STATE.timestamp`.
2. If absent → fresh start (Phase 0).
3. If `status = "completed"`:
   - Without `— resume:` flag → ask user "previous run completed; overwrite artifacts?"
     Default to fresh start under AUTO_PROCEED. With `— fresh: true` → delete STATE,
     fresh start.
   - With `— resume: true` → no-op exit (everything already done).
4. If `status = "in_progress"`:
   - `timestamp ≥ 24h` → stale; warn user; default fresh start (delete STATE first).
   - `timestamp < 24h` → resume from `STATE.phase + 1`. For each phase ≤ STATE.phase,
     apply the artifact-presence skip rule (next section).
5. If `status = "awaiting_human_continue"`:
   - This is the designed STOP A terminal state. Re-invoking the same skill without
     `— fresh: true` or `— from-phase:` should summarize the existing proposal artifacts
     and return the next skill hint:
     `/experiment-bridge "proposal/proposal_pack.json"`.
   - Downstream invocation of `/experiment-bridge` is treated as the human's approval to
     continue after STOP A.

### Idempotent phase skip

Before running each phase, check whether its expected output artifact already exists AND
the STATE entry says this phase completed. If both hold, skip the phase and log
"skipped (already done)". Phase artifact map:

| Phase | Expected artifact(s) |
|---|---|
| phase-0-intake | `orbit-research/PIPELINE_INTAKE.md` |
| phase-0-5-literature-prefetch | `papers/` non-empty (≥ 1 PDF) AND `STATE.literature_pre_fetched == true` AND STATE timestamp within last 24 h. Skipped silently when `parsed_flags.arxiv_download == false`. |
| phase-1-discovery | proposal draft content captured for `proposal/proposal_pack.json` + compatibility `refine-logs/FINAL_PROPOSAL.md` + `orbit-research/PROBLEM_SELECTION.md` |
| phase-2-grounding | `orbit-research/ASSUMPTION_LEDGER.md` + `ABSTRACT_TASK_MECHANISM.md` + `BASELINE_CEILING.md` |
| phase-3-innovation | `orbit-research/MECHANISM_IDEATION.md` + `ANALOGY_TRANSFER.md` + `ALGORITHM_TOURNAMENT.md` |
| phase-4-final-refinement | `proposal/proposal_pack.json` updated with the selected sketch and refined proposal fields |
| phase-5-summary | `proposal/proposal_pack.json` + `proposal/PROPOSAL.md` + `orbit-research/ORBIT_STATE.json` |

If artifact present but STATE entry missing/older, replay phase with a "refreshing
inconsistent state" warning.

### Override flags

| Flag | Effect |
|---|---|
| `— resume: true` | Force resume even if STATE looks ambiguous |
| `— fresh: true` | Delete STATE first; ignore existing artifacts; run from Phase 0 |
| `— from-phase: <N>` | Force start from the specified phase (1–5) |
| `— human checkpoint: true` | Pause at every phase boundary (write `awaiting_human_continue` after each), not just at Phase 5 |
| `— no-checkpoint: true` | Skip the STOP A `awaiting_human_continue` exit; transition straight to `completed` |
| `STOP_AT_GROUNDING: true` | Skip Phase 3 + Phase 4; produce only Grounding artifacts; awaiting_human_continue at Phase 5 |
| `STOP_AT_PROPOSAL: true` | Legacy no-op alias. Proposal-only is now the default behavior. |
| `— with-experiment-plan: true` | Legacy explicit opt-in: after proposal summary, invoke `/experiment-plan` and add planning artifacts. Not recommended for new canonical ORBIT runs. |
| `— legacy-full-preimplementation: true` | Alias for `— with-experiment-plan: true`. |
| `— arxiv download: <bool>` | When `true`, run **Phase 0.5 (Literature Pre-fetch)** before Phase 1: delegates to `/research-lit` to populate `papers/` and `research-wiki/papers/` so downstream skills (especially `/research-refine`'s "Check `papers/` first" step in Phase 1c, and the Stage-4/5/7 grounding harness prompts in Phase 2) have local PDFs to scan. Default `false` (preserves prior behavior — grounding runs off whatever the LLM already knows). Without this flag, the literature pre-fetch is skipped silently. |
| `— sources: <list>` | Comma-separated source list for Phase 0.5. Subset of: `arxiv`, `web`, `semantic-scholar`, `deepxiv`, `exa`, `alphaxiv`, `local`, `all`. Default `arxiv`. Forwarded verbatim to `/research-lit — sources: <list>`. Has no effect if `— arxiv download: false`. |
| `— arxiv max download: <N>` | Cap on PDFs downloaded by Phase 0.5. Default `LITERATURE_PRE_FETCH_MAX_DEFAULT = 10`. Forwarded to `/research-lit — max download: <N>`. |
| `— venue: <name>` | Target venue (e.g. `iclr`, `icml`, `neurips`, `cvpr`, `naacl`). Recorded in `PIPELINE_INTAKE.md` and forwarded as `— venue: <name>` to `/research-refine` so reviewer prompts can name the venue specifically rather than using a generic venue phrase. Default: unset. |
| `— effort: <level>` | Claude CLI effort level: `low`, `medium`, `high`, `xhigh`, or `max` (alias for `xhigh`). Sets the per-call `Claude CLI `--effort max`` for Claude CLI reviewer invocations across this skill (overrides `CLAUDE_REVIEW_EFFORT = xhigh` constant for this run). The actual effort honored is subject to Claude CLI reviewer environment availability — if the requested level is unavailable, the skill must record a Claude CLI availability/configuration issue to the next lower available level and the fallback (e.g. `gpt-5.2 high`) is logged in `STATE.notes`. |
| `— difficulty: <level>` | Calibrates downstream `/research-refine` strictness (Phase 1c idea-mode + Phase 4 final refinement) plus READY threshold and MAX_ROUNDS. Three levels: `medium` = standard collaborator review + ≥9.0 / 5 rounds; `hard` = stricter collaborator review + ≥9.5 / 7 rounds; `nightmare` before STOP A = strong collaborator review unless `— review-posture: adversarial` is explicit. Forwarded verbatim as `— difficulty: <level>` to `/research-refine`. |
| `— input-mode: keyword\|context\|idea` | Override Phase 0 input classification. Use `context` for long notes/background `.md` files that should still run `/idea-discovery`; use `idea` only for an already committed method/direction draft that should skip discovery and go straight to `/research-refine`. |
| `— context: true` | Alias for `— input-mode: context`. Explicitly treat a `.md` file as contextual material, not as a final idea. |
| `— idea: true` | Alias for `— input-mode: idea`. Explicitly treat a `.md` file as a draft idea/method proposal and skip discovery. |
| `— claude-required: false` | **Default `true`.** Claude CLI reviewer is load-bearing for Phase 3 (innovation) and Phase 4 (calibration); see `../shared-references/claude-cli-review.md`. With the default, a failed precondition or mid-run Codex error causes a **LOUD STOP** (STATE = `awaiting_user_action`, no artifacts written for the failed phase). Pass `false` to deliberately run in single-model mode; every Phase 3/Phase 4 artifact then carries a visible degraded-mode header at the top of the file. `AUTO_PROCEED` does not select this flag. |

## Workflow

### Phase 0: Detect Input Type and Initialise

**Claude CLI precondition first.** Before *anything* else — before the resume check,
before reading `$ARGUMENTS`, before `mkdir` — run the Claude CLI availability probe
from [`../shared-references/claude-cli-review.md`](../shared-references/claude-cli-review.md) §3:

```bash
# Claude CLI: no shell helper is run. Run `claude --version` to confirm Claude CLI is available.
```

If the Claude CLI reviewer transport is unavailable, apply the LOUD STOP
protocol (§4 of that contract):

- Write `orbit-research/IDEA_TO_PROPOSAL_STATE.json` with
  `phase: "phase-0-precondition"`, `status: "awaiting_user_action"`,
  `next_action: "fix-claude-cli-reviewer-then-reinvoke"`, and the full
  `reviewer_unavailable_reason` block from §4.
- Print the verbatim user-facing message from §4 (Claude CLI reviewer required, remediation
  steps, override flag).
- Exit. Do not `mkdir`, do not write `PIPELINE_INTAKE.md`, do not invoke
  `/idea-discovery` or `/research-refine`, do not run Phase 0.5 literature
  pre-fetch.

If the user passed `— claude-required: false`, reviewer transport failure becomes
a single warning + a degraded-mode header on every Phase 3/Phase 4 artifact.

Log a successful precondition as a `claude_cli_precondition` block in the Phase 0
STATE (see Phase 0 STATE schema below).

**Resume check second.** Apply the entry decision tree above. If resuming, skip to the
phase indicated by `STATE.phase + 1` and continue from there (each downstream phase
applies its own idempotent-skip check).

Otherwise (fresh start), inspect `$ARGUMENTS`:

1. Explicit mode flags win:
   - `— input-mode: keyword` → **keyword-mode**.
   - `— input-mode: context` or `— context: true` → **context-mode**.
   - `— input-mode: idea` or `— idea: true` → **idea-mode**.
2. If the input is a **path to an existing file** ending in `.md`, classify it by intent:
   - **context-mode** when the filename or headings indicate notes/background/context,
     e.g. `context`, `background`, `notes`, `reading`, `survey`, `constraints`,
     `requirements`, `方向`, `背景`, `上下文`, `阅读笔记`, `约束`.
   - **idea-mode** when the filename or headings indicate a committed method/proposal,
     e.g. `proposal`, `method`, `approach`, `experiment plan`, `hypothesis`, `idea`,
     `方案`, `方法`, `假设`, `实验计划`, `研究想法`.
   - If ambiguous, default to **context-mode**. A long `.md` should not silently skip
     discovery just because it is a file.
3. Otherwise → **keyword-mode** (research area, topic phrase).

```bash
mkdir -p orbit-research/ refine-logs/
```

Write a one-line classifier note to `orbit-research/PIPELINE_INTAKE.md`:

```markdown
# Pipeline Intake
- Input: $ARGUMENTS
- Mode: keyword | context | idea
- Started: <ISO timestamp>
- Stops at: proposal (Validation Spine NOT triggered)
```

**Parse inline flags** from `$ARGUMENTS` and record them in
`orbit-research/PIPELINE_INTAKE.md` AND in the STATE block below. Flags
recognised by this skill (see Override flags table above for full list):
`AUTO_PROCEED`, `human checkpoint`, `STOP_AT_GROUNDING`, `STOP_AT_PROPOSAL`,
`with-experiment-plan`, `legacy-full-preimplementation`,
`arxiv download`, `sources`, `arxiv max download`, `venue`, `effort`,
`difficulty`, `input-mode`, `context`, `idea`, `from-phase`, `resume`, `fresh`,
`no-checkpoint`, `claude-required`.

Unknown flags are recorded in `PIPELINE_INTAKE.md` with a `⚠️ unknown flag —
will not be honored` annotation rather than silently dropped. **This is a
contract: a flag that survives parsing must either be honored or be flagged as
unknown — never silently captured-but-ignored.**

**Write STATE** at end of Phase 0:

```jsonc
{
  "skill": "idea-to-proposal",
  "phase": "phase-0-intake",
  "input_mode": "keyword | context | idea",
  "input_value": "$ARGUMENTS",
  "parsed_flags": {                      // every flag parsed in Phase 0
    "auto_proceed": true,
    "human_checkpoint": false,
    "arxiv_download": false,             // ← Phase 0.5 trigger
    "sources": "arxiv",
    "arxiv_max_download": 10,
    "venue": null,                        // forwarded to downstream reviewer prompts
    "effort": "xhigh",                    // CLAUDE_REVIEW_EFFORT for this run
    "difficulty": "medium",               // /research-refine threshold + MAX_ROUNDS
    "claude_required": true                // §6 of claude-cli-review.md; false = degraded-mode opt-in
  },
  "claude_cli_precondition": {                 // result of the entry-time check; see claude-cli-review.md §3
    "checked_at": "<ISO 8601>",
    "ready": true,
    "codex_cli_version": "<from .codex.detail>",
    "auth_method": "<from .auth.authMethod>",
    "session_runtime_mode": "<from .sessionRuntime.mode>"
  },
  "status": "in_progress",
  "next_action": "phase-0-5-literature-prefetch | phase-1-discovery",   // depends on arxiv_download
  "timestamp": "<now>",
  "artifact_inventory": ["orbit-research/PIPELINE_INTAKE.md"]
}
```

If the Phase 0 precondition failed and `— claude-required: false` was NOT
passed, STATE looks like this instead (and the skill exits without writing
`PIPELINE_INTAKE.md`):

```jsonc
{
  "skill": "idea-to-proposal",
  "phase": "phase-0-precondition",
  "status": "awaiting_user_action",
  "next_action": "fix-claude-cli-reviewer-then-reinvoke",
  "reviewer_unavailable_reason": {
    "ready": false,
    "codex_available": false,
    "auth_logged_in": false,
    "detail": "<raw .detail string from the failing field>",
    "raw_setup_json": "<entire JSON for debugging>"
  },
  "timestamp": "<ISO 8601>",
  "artifact_inventory": []
}
```

### Phase 0.5: Literature Pre-fetch (conditional)

**Trigger condition**: `parsed_flags.arxiv_download == true` (i.e. user passed
`— arxiv download: true`). If false, **skip this phase silently** and proceed to
Phase 1 — the historical default behavior is preserved when the flag is absent
or false.

**Why this phase exists** (the bug it fixes): `/research-refine` (Phase 1c
idea-mode) and the Stage-4/5/7 grounding harness prompts (Phase 2) both check
`papers/` and `literature/` for local PDFs first (per `research-refine
SKILL.md` L181: "Check `papers/` and `literature/` first"). Without a
populated `papers/`, those checks return empty and grounding falls back to
whatever the LLM already knows about the area — which is often outdated for
fast-moving fields and silently misses concurrent work that the user expected
the pipeline to find. Before this patch the `— arxiv download: true` flag was
captured into `PIPELINE_INTAKE.md` but never honored anywhere downstream, so
`papers/` stayed empty even when explicitly requested. Phase 0.5 closes that
loop by delegating to `/research-lit` (which orchestrates arXiv + Semantic
Scholar + DeepXiv + Exa + Zotero + Obsidian per `— sources:`) and downloading
the top-N most relevant PDFs into `papers/` plus ingesting them into
`research-wiki/papers/` (when `research-wiki/` exists in the project root).

**Step 1 — Derive a focused query from the input**:
- **keyword-mode** (input is a topic phrase): use it directly as the query.
- **context-mode** (input is a context `.md`): read the file and synthesize a
  1-2 line query from the domain, goals, constraints, mentioned papers/systems,
  and tentative directions. Ignore long prose that is only background.
- **idea-mode** (input is a draft idea `.md`): read the file's headline /
  "Direction" / "Tasks" sections and synthesize a 1-2 line query of key technical
  terms (e.g. for the round-5 example: "DiT rectified-flow image editing
  post-training RL EditScore DanceGRPO").

Record the derived query in `PIPELINE_INTAKE.md` under a "Phase 0.5 query"
field for transparency and reproducibility.

**Step 2 — Invoke `/research-lit`** with the parsed flags:

```bash
/research-lit "<derived query>" \
    — sources: <parsed_flags.sources> \
    — arxiv download: true \
    — max download: <parsed_flags.arxiv_max_download>
```

`/research-lit` itself handles the multi-source fan-out, rate limiting
(`time.sleep(1)` between consecutive arXiv API calls), dedup against
already-present `papers/*.pdf`, PDF download into `papers/`, and (when
`research-wiki/` exists) automatic ingest into `research-wiki/papers/` via
`python3 "$WIKI_SCRIPT" ingest_paper` after resolving `$WIKI_SCRIPT` via
`../shared-references/wiki-helper-resolution.md`. This skill does not
duplicate that logic.

**Step 3 — Fallback ladder when `/research-lit` is unavailable** (per the
standard ARIS-fallback contract):
1. Try `/research-lit` first (the canonical multi-source entry point).
2. If `/research-lit` skill is not registered, try `/arxiv "<query>" — download:
   all — max: <N>` directly. `/arxiv` covers the arXiv-only path and includes
   wiki ingestion in its Step 6.
3. If `/arxiv` is also unavailable, fall back to direct invocation of
   `tools/arxiv_fetch.py search` + `tools/arxiv_fetch.py download` per ID + (if
   `research-wiki/` exists) resolve `$WIKI_SCRIPT`, then run
   `python3 "$WIKI_SCRIPT" sync research-wiki/ --arxiv-ids <comma-list>`.
4. If the helper scripts are also missing, log
   `PHASE_0_5_DEGRADED (literature_prefetch_unavailable)` in `STATE.notes`,
   warn the user, and proceed to Phase 1 anyway (Phase 0.5 is best-effort —
   never block proposal generation on a missing literature pre-fetch).

**Step 4 — Append to PIPELINE_INTAKE.md** under a new
`## Phase 0.5: Literature pre-fetch` section:
- Sources requested + sources actually used (after fallback if any).
- Number of PDFs downloaded into `papers/` (with size).
- Number of papers ingested into `research-wiki/papers/`.
- Any rate-limit / API-error events with affected arXiv IDs.

**Write STATE** at end of Phase 0.5:

```jsonc
{
  "phase": "phase-0-5-literature-prefetch",
  "status": "in_progress",
  "next_action": "phase-1-discovery",
  "literature_pre_fetched": true,
  "literature_pre_fetch_count": <N>,
  "literature_pre_fetch_partial_failures": <K>,    // arXiv IDs that failed (rate limit, 429, etc.)
  "timestamp": "<now>",
  "artifact_inventory": [
    "orbit-research/PIPELINE_INTAKE.md",
    "papers/ (<N> PDFs, <total size>)",
    "research-wiki/papers/ (<N> ingested)"          // only if research-wiki/ exists
  ]
}
```

**Idempotency**: if `papers/` already contains ≥ `parsed_flags.arxiv_max_download / 2`
PDFs AND `STATE.literature_pre_fetched == true` from a prior run within the
last 24 h, skip Phase 0.5 with a "skipped (already pre-fetched within 24 h)"
log line. To force a re-fetch, pass `— fresh: true` (which deletes STATE) or
manually delete `papers/`. This protects against duplicate downloads when the
user re-invokes the skill to resume from a later phase.

### Phase 1: Discovery — produce a baseline proposal + problem selection

#### Phase 1a — keyword-mode

Invoke the existing Workflow 1, forwarding the parsed flags:

```bash
/idea-discovery "$ARGUMENTS" \
    — venue: <parsed_flags.venue> \
    — effort: <parsed_flags.effort> \
    — difficulty: <parsed_flags.difficulty> \
    — paper-mode: normal \
    — review-posture: collaborator
```

(`/idea-discovery` itself refines the selected idea through `/research-refine`; the flags
propagate to collaborator refinement before STOP A. Omit any flag whose parsed value is
null / default.)

This produces:
- `idea-stage/IDEA_REPORT.md` (ranked candidates)
- proposal draft content for `proposal/proposal_pack.json`
- `refine-logs/FINAL_PROPOSAL.md` as a legacy compatibility view from the draft proposal
- `orbit-research/PROBLEM_SELECTION.md`

When delegating to `/idea-discovery`, no experiments are run. Idea ranking
comes from literature grounding, novelty posture, feasibility, mechanism plausibility,
baseline/headroom reasoning, expected diagnostic clarity, paper-mode fit, and
collaborator critique.

If legacy sub-skills emit `refine-logs/EXPERIMENT_PLAN.md` as a side effect, do not list
it as a canonical `/idea-to-proposal` output. Mark it as legacy/pre-STOP-A and let
`/experiment-bridge` reuse or refresh it after the human approves STOP A.

When `/idea-discovery` reaches its post-Phase-2 user checkpoint, pass through with the
top-ranked candidate unless the user passed `— human checkpoint: true`.

#### Phase 1b — context-mode

Read the user's context `.md` file and extract a compact discovery brief into
`orbit-research/PIPELINE_INTAKE.md` under `## Context-mode discovery brief`.
The brief should contain only decision-relevant material:

- domain / research area
- goals and non-goals
- hard constraints, available resources, datasets, codebases, venues, or deadlines
- cited papers/systems/negative examples
- tentative directions, explicitly marked as tentative rather than committed ideas

Then invoke `/idea-discovery` with the original file path plus the brief location,
forwarding parsed flags:

```bash
/idea-discovery "$ARGUMENTS + context-mode discovery brief in orbit-research/PIPELINE_INTAKE.md" \
    — venue: <parsed_flags.venue> \
    — effort: <parsed_flags.effort> \
    — difficulty: <parsed_flags.difficulty>
```

The instruction to `/idea-discovery` is: treat the `.md` as context and constraints,
not as the selected solution. It must still generate and compare candidate ideas before
choosing one.

This produces the same artifact set as keyword-mode:
- `idea-stage/IDEA_REPORT.md` (ranked candidates)
- proposal draft content for `proposal/proposal_pack.json`
- `refine-logs/FINAL_PROPOSAL.md` as a legacy compatibility view from the draft proposal
- `orbit-research/PROBLEM_SELECTION.md`

If legacy sub-skills emit an experiment plan as a side effect, treat it as legacy context,
not as the canonical post-STOP-A plan.

When delegating to `/idea-discovery`, no experiments are run. Neither
`proposal/proposal_pack.json` nor its Markdown views may cite pre-STOP-A runs as evidence.

When `/idea-discovery` reaches its post-Phase-2 user checkpoint, pass through with the
top-ranked candidate unless the user passed `— human checkpoint: true`.

#### Phase 1c — idea-mode

Read the user's draft `.md` file, then invoke `/research-refine` with the
parsed flags forwarded:

```bash
/research-refine "$ARGUMENTS" \
    — venue: <parsed_flags.venue> \
    — effort: <parsed_flags.effort> \
    — difficulty: <parsed_flags.difficulty>
```

(Forward `venue` / `effort` / `difficulty` so `/research-refine`'s reviewer
prompt names the venue specifically rather than a generic venue phrase, and
so the Phase 4 READY threshold + MAX_ROUNDS match the user's difficulty
calibration. Omit a flag if its parsed value is null / default.)

If Phase 0.5 ran (`STATE.literature_pre_fetched == true`), `papers/` is now
populated with up to `parsed_flags.arxiv_max_download` PDFs and
`/research-refine`'s "Check `papers/` and `literature/` first" step (its
SKILL.md L181) will scan them as the grounding base — closing the loop that
this skill's `— arxiv download:` flag was originally promised to enable. If
Phase 0.5 was skipped (the flag was false or absent), `/research-refine` falls
back to whatever the LLM already knows about the area, as it always has.

This produces a refined proposal draft. Capture it in `proposal/proposal_pack.json`, then
render `proposal/PROPOSAL.md` and legacy `refine-logs/FINAL_PROPOSAL.md` views. Derive
`orbit-research/PROBLEM_SELECTION.md` manually by extracting the Problem Anchor from the
pack and writing a brief selection rationale (importance / audience / feasibility /
headroom / paper survivability) ending with `PROCEED | NARROW | RETHINK`. If `RETHINK`,
stop here and surface the issue.

**Write STATE** at end of Phase 1 (both modes):

```jsonc
{
  "phase": "phase-1-discovery",
  "status": "in_progress",
  "next_action": "phase-2-grounding",
  "timestamp": "<now>",
  "artifact_inventory": [
    "orbit-research/PIPELINE_INTAKE.md",
    "proposal/proposal_pack.json",
    "proposal/PROPOSAL.md",
    "refine-logs/FINAL_PROPOSAL.md", // compatibility view
    "orbit-research/PROBLEM_SELECTION.md"
    // + idea-stage/IDEA_REPORT.md if keyword-mode or context-mode
  ]
}
```

If `— human checkpoint: true` is set, write `status: "awaiting_human_continue"` here too
and stop; resume on next invocation.

### Phase 2: Grounding — Stages 4 → 5 → 7

Load and follow [grounding_pack.md](prompts/grounding_pack.md). It preserves the Stage 4
assumption ledger, Stage 5 abstract task/mechanism framing, and Stage 7 baseline/headroom
instructions, including proposal_pack normalization and STOP_AT_GROUNDING behavior.

### Phase 3: Innovation — Stages 8 → 9 → 10 (Codex COLLABORATIVE)

Load and follow [innovation_loops.md](prompts/innovation_loops.md). Keep Claude CLI reviewer in
collaborative mode for candidate generation, preserve viable alternatives, and normalize
MECHANISM_IDEATION, ANALOGY_TRANSFER, and ALGORITHM_TOURNAMENT into proposal_pack.

### Phase 4: Integrated Final Refinement (Collaborator Calibration)

Load and follow [integrated_final_refinement.md](prompts/integrated_final_refinement.md).
This asset preserves the collaborator-calibration handoff to `/research-refine`, the
`PROPOSAL_READY` semantics, and the v1.4 proposal_pack plus compatibility-view contract.

### Phase 5: Pipeline Summary

Write `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /idea-to-proposal Pipeline Summary

- Input: $ARGUMENTS
- Mode: keyword | context | idea
- Completed: <ISO timestamp>
- Validation Spine triggered: NO

## Artifact map (Discovery + Grounding + Innovation)

### Canonical STOP A pack
- proposal/proposal_pack.json             — source of truth for STOP A
- proposal/PROPOSAL.md                    — generated human-readable proposal view
- proposal/METHOD_SPEC.md                 — generated method view when useful

### Legacy compatibility views
- refine-logs/FINAL_PROPOSAL.md           — compatibility proposal view
- refine-logs/FINAL_PROPOSAL_SHORT.md     — compatibility short proposal view
- refine-logs/METHOD_SPEC.md              — compatibility method view

### Discovery (from /idea-discovery or /research-refine)
- idea-stage/IDEA_REPORT.md                — (keyword/context mode only)
- orbit-research/PROBLEM_SELECTION.md      — compatibility view of problem selection

### Grounding (Phase 2)
- orbit-research/ASSUMPTION_LEDGER.md      — compatibility view of pack assumptions
- orbit-research/ABSTRACT_TASK_MECHANISM.md — compatibility view of abstract task + mechanism families
- orbit-research/BASELINE_CEILING.md       — compatibility view of simple-strong baseline reference

### Innovation (Phase 3, Claude CLI collaborative)
- orbit-research/MECHANISM_IDEATION.md     — compatibility view of candidate mechanisms
- orbit-research/ANALOGY_TRANSFER.md       — compatibility view of cross-domain analogies
- orbit-research/ALGORITHM_TOURNAMENT.md   — compatibility view of tentative preferred sketch + alternates

## STOP A

Human review question:

> Is this proposal worth formal experiment planning?

If approved, record the freeze in `orbit-research/PROPOSAL_STABILITY.md`. After STOP A,
ordinary related or concurrent work goes to
`orbit-research/CONCURRENT_WORK_WATCHLIST.md`; reopen `proposal/proposal_pack.json` only
for a `STRONG_BLOCKER`, explicit human instruction, or a result-backed decision in
`RESEARCH_DECISION_LOG.md`. Regenerate Markdown views from the pack after any approved
change.

Review:
- `proposal/proposal_pack.json`
- `proposal/PROPOSAL.md`
- `proposal/METHOD_SPEC.md` if present
- legacy `refine-logs/` views if collaborators still rely on them
- the key `orbit-research/` Discovery/Grounding/Innovation artifacts above

## Next steps (NOT run by this skill)

1. /experiment-bridge "proposal/proposal_pack.json"
   → turns the approved proposal into `EXPERIMENT_PLAN.md` and
     `EXPERIMENT_PLAN_EXEC.md`
   → implements code + writes `PLAN_CODE_AUDIT.md`
   → may run limited implementation-facing probes
   → STOP B: review plan + audit + probe reports before formal diagnostics
   → Note: experiment-bridge pack input is documented here before its implementation
     migration; legacy callers may still pass `refine-logs/FINAL_PROPOSAL.md`.

2. /diagnostic-to-review "[diagnostic command OR manifest]"
   → owns formal diagnostic execution, result interpretation, decision log, and
     conditional-required claim/review for paper-bearing diagnostics
   → STOP C: review claim/review/decision artifacts when paper-bearing

3. /paper-writing "NARRATIVE_REPORT.md" — venue: ICLR
   → final paper writing (G16/G18 enforced — needs CLAIM_CONSTRUCTION.md)
```

**Write STATE** at end of Phase 5:

```jsonc
{
  "phase": "phase-5-summary",
  "status": "awaiting_human_continue",
  "next_action": "human-review-proposal",
  "next_skill_hint": "/experiment-bridge \"proposal/proposal_pack.json\"",
  "timestamp": "<now>",
  "artifact_inventory": [
    "proposal/proposal_pack.json",
    "proposal/PROPOSAL.md",
    "proposal/METHOD_SPEC.md",
    "orbit-research/PIPELINE_INTAKE.md",
    "orbit-research/PROBLEM_SELECTION.md",
    "orbit-research/ASSUMPTION_LEDGER.md",
    "orbit-research/ABSTRACT_TASK_MECHANISM.md",
    "orbit-research/BASELINE_CEILING.md",
    "orbit-research/MECHANISM_IDEATION.md",
    "orbit-research/ANALOGY_TRANSFER.md",
    "orbit-research/ALGORITHM_TOURNAMENT.md",
    "orbit-research/PIPELINE_SUMMARY.md",
    "orbit-research/ORBIT_STATE.json",
    "refine-logs/FINAL_PROPOSAL.md",       // legacy compatibility view
    "refine-logs/FINAL_PROPOSAL_SHORT.md", // legacy compatibility view
    "refine-logs/METHOD_SPEC.md"           // legacy compatibility view
    // + idea-stage/IDEA_REPORT.md if keyword-mode or context-mode
  ]
}
```

Also write `orbit-research/ORBIT_STATE.json` with `current_stop = STOP_A`,
`status = paused`, `pause_reason = stop_review`, and
`safe_next_command = /experiment-bridge "proposal/proposal_pack.json"`.

`awaiting_human_continue` is the deliberate terminal state for this skill. The user
inspects the proposal artifacts and decides:

- **Continue to experiment planning and implementation** — invoke
  `/experiment-bridge "proposal/proposal_pack.json"`.
- **Iterate proposal** — invoke `/proposal-revise` for targeted edits or
  `/idea-to-proposal "..." — fresh: true` for a full rerun.
- **Abandon** — leave it. STATE stays `awaiting_human_continue` indefinitely.

To skip this checkpoint and run straight through to `completed`, pass `— no-checkpoint: true`.

### Legacy add-on: explicit experiment planning from this skill

Pre-patch `/idea-to-proposal` generated experiment plans. In the new canonical flow,
experiment planning moves to `/experiment-bridge` after STOP A. Existing
`EXPERIMENT_PLAN.md` files remain readable, but new canonical runs generate them in
`/experiment-bridge`.

If the user explicitly passes `— with-experiment-plan: true` or
`— legacy-full-preimplementation: true`, invoke `/experiment-plan "proposal/proposal_pack.json"`
after writing the proposal summary. Mark the output as legacy compatibility in STATE
notes and still recommend `/experiment-bridge "proposal/proposal_pack.json"` as the
next canonical wrapper.

## ARIS / Sub-skill Unavailability

For each delegated invocation (`/idea-discovery`, `/research-refine`),
follow the standard fallback pattern:

```text
Try slash invocation.
If skill not registered:
  Print "ORBIT skill <name> unavailable. Phase <N> degraded: <fallback or HUMAN_DECISION_REQUIRED>."
  Continue gracefully.
If the missing skill was load-bearing for a STOP A artifact (e.g. /research-refine for
proposal/proposal_pack.json):
  Escalate — do not silently produce an incomplete proposal.
```

## Codex Unavailability — LOUD STOP, not silent skip

**Policy change (was: silent fallback; now: precondition halt).**
Codex is the load-bearing collaborator/adversary that prevents single-AI
local optima during Phase 3 (innovation) and Phase 4 (final refinement
calibration). Producing a proposal *without* Claude CLI reviewer contribution and then
quietly continuing is exactly the failure mode this skill exists to avoid;
the user only discovered it post-hoc by reading STATE notes.

This skill therefore follows the **Claude CLI Review Transport + Loud-Stop Contract**
in [`../shared-references/claude-cli-review.md`](../shared-references/claude-cli-review.md):

1. **Phase 0 precondition (§3 of that contract).** Before any artifact is
   written, run:

   ```bash
   # Claude CLI: no shell helper is run. Run `claude --version` to confirm Claude CLI is available.
   ```

   Verify `claude --version` exits successfully. Log the result in
   STATE under `claude_cli_precondition`. If the check fails, apply §4 of the
   contract:
   - Write STATE with `status: "awaiting_user_action"`,
     `next_action: "fix-claude-cli-reviewer-then-reinvoke"`, and the full
     `reviewer_unavailable_reason` block.
   - Surface the verbatim user-facing message from §4 (`claude --version` / Claude CLI authentication,
     `make the `claude` CLI available and authenticated`, and the
     `— claude-required: false` override).
   - **Stop the skill.** Do not run Phase 0.5 literature pre-fetch, do not
     invoke `/idea-discovery`, do not write `PIPELINE_INTAKE.md`.

2. **Mid-run Claude CLI review call failures (§5 of that contract).** If a
   `claude -p` invocation fails during Phase 3 or Phase 4
   (network, auth-expired, sandbox rejection, etc.), the skill writes
   STATE `status: "awaiting_user_action"` with `claude_cli_call_failure`,
   prints the same loud message naming the failing phase, and stops.
   Upstream artifacts that were already written stay on disk; the next
   invocation resumes from the failed phase. A `## Claude CLI collaborative
   additions: NOT_AVAILABLE` substitute is **not** an acceptable output.
   Also export a standalone handoff prompt per §5.5:
   `.aris/review-prompts/<phase-id>.md`, with expected response path
   `.aris/review-outputs/<phase-id>.response.md`. Set ORBIT_STATE
   `pause_reason: "claude_review_needed"` and
After fixing Claude CLI access, rerun the blocked skill with its documented resume flag.

3. **Override.** A user who explicitly wants a degraded run can pass
   `— claude-required: false`. Every Phase 3/Phase 4 artifact then carries
   the visible degraded-mode header at the top of the file (per §6 of the
   contract). `AUTO_PROCEED` does not select this override; it must come
   from the user.

The previous silent-fallback policy (mark
`NOT_AVAILABLE (codex_mcp_unreachable)` and continue; skip Phase 4 review
with `SKIPPED`; emit `ABSTAIN_REASONS: codex_mcp_unreachable` for the
tournament) is **deprecated** and must not be applied by this skill.

## What This Skill Deliberately Does NOT Do

- Does **not** invoke `/experiment-plan` in the canonical default path; that is allowed
  only through the explicit legacy flags documented above.
- Does **not** invoke `/experiment-bridge`, `/experiment-queue`, `/result-to-claim`,
  `/auto-review-loop`, `/paper-writing`, or any formal diagnostic/claim/paper skill.
- Does **not** run experiments or use GPU, including when keyword/context mode delegates
  to `/idea-discovery`.
- Does **not** write `CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`,
  `COMPONENT_BUNDLE_LADDER.md`, `ALGORITHMIC_FORMALIZATION.md`, `PLAN_CODE_AUDIT.md`, or
  any DIAGNOSTIC_RUN_*.md in the canonical default path.
- Does **not** finalise method commitment — Stage 10's pick is explicitly tentative
  (`TENTATIVE_PREFERRED_SKETCH_ID`); experiment planning and implementation happen after
  STOP A through `/experiment-bridge`.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Final Rule

```text
Discover then ground then invent then write a proposal — no canonical plan, formal
implementation, or paper-level diagnostic evidence.
Innovation produces candidates; this skill stops before commitment picks one for real.
The proposal carries the tentative sketch ID forward; downstream skills can switch.
```
