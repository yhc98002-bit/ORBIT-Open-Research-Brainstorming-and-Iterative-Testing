---
name: idea-to-proposal
description: "ORBIT v1.3 thin pipeline from a research-area keyword OR a draft idea .md file all the way to a v1.3-complete proposal AND experiment plan — everything you need before touching GPU. Chains existing /idea-discovery (for keywords) or /research-refine (for .md), then runs Stage 4/5/7 (Grounding) + Stage 8/9/10 (Innovation, Codex collaborative) + a final /research-refine pass that integrates the tentative sketch winner + /experiment-plan to produce EXPERIMENT_PLAN + Validation prereqs. Outputs FINAL_PROPOSAL.md, EXPERIMENT_PLAN.md, plus the v1.3 Discovery/Grounding/Innovation artifact set. Does NOT touch GPU. Use when user says \"领域到proposal\", \"出proposal\", \"想法到方案\", \"idea-to-proposal\", \"proposal pipeline\", \"从领域跑到方案\", or wants the full pre-implementation package in one call."
argument-hint: [research-area-keyword OR path/to/draft-idea.md]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# /idea-to-proposal — v1.3 Discovery → Grounding → Innovation → Proposal → Experiment Plan

Run a v1.3-complete pre-implementation pipeline for: **$ARGUMENTS**

## Overview

This skill chains existing skills + the v1.3 Grounding, Innovation, and Validation-prereq
phases into one pipeline. It produces:
- a problem-anchored proposal (FINAL_PROPOSAL.md)
- the v1.3 artifact set: assumption ledger, abstract task / mechanism, baseline ceiling,
  mechanism ideation, analogy transfer, algorithm sketch tournament
- a claim-driven experiment plan (EXPERIMENT_PLAN.md) with control design, null-result
  contract, component bundle ladder, algorithmic formalization, diagnostic experiment plan

**Scope boundary** — this skill stops *before* GPU. It produces every artifact required
for `/experiment-bridge` to start writing code, but does not write code itself, does not
run any experiment, does not write a paper. To take the plan further, hand off to
`/experiment-bridge` (Stage 15) or `/research-pipeline` from Stage 15 onward.

```
Input:        Phase 1 (Discovery)    Phase 2 (Grounding)   Phase 3 (Innovation, Codex collab)   Phase 4               Phase 5      Phase 6
keyword ────► /idea-discovery ──┐
.md file ───► /research-refine ─┴► Stage 4 → 5 → 7 ─────► Stage 8 → 9 → 10 ─────────────────► /research-refine ──► PIPELINE_   ──► /experiment-plan
                                  (assumption,            (mechanism, analogy,                 final pass            SUMMARY        Stage 11/12/13/14/16
                                   abstract, baseline)     sketch tournament)                  (winner integrated)                  prereqs
                                                                                                                                    │
                                                                                                                                    ▼
                                                                                                                          ⏸ STOP awaiting_human_continue
                                                                                                                          (or earlier with --stop-at-proposal)
```

## Constants

- **OUTPUT_ROOT_V13 = `orbit-research/`** — v1.3 grounding + innovation artifacts.
- **OUTPUT_ROOT_PROPOSAL = `refine-logs/`** — the existing FINAL_PROPOSAL.md location.
- **CODEX_REVIEW_MODEL = `gpt-5.5`**, **CODEX_REVIEW_EFFORT = `xhigh`**.
- **CODEX_INNOVATION_MODE** — `COLLABORATIVE` for Phase 3 (Stages 8/9/10); `ADVERSARIAL`
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
  - `hard`: stricter reviewer (push back on sprawl, frontier-leverage incompleteness,
    unfocused validation); SCORE_THRESHOLD = 9.5, MAX_ROUNDS = 7.
  - `nightmare`: `hard` + reject-by-default per-dimension veto (every individual
    dimension must score ≥ 8 for READY); SCORE_THRESHOLD = 9.5, MAX_ROUNDS = 7.
  Override with `— difficulty: <level>`. Forwarded verbatim to `/research-refine`.
- **STOP_AT_GROUNDING = false** — if `true`, skip Phase 3 and Phase 4 (produce only the
  Grounding artifacts on top of Phase 1 output).
- **STOP_AT_PROPOSAL = false** — if `true`, skip Phase 6 (do NOT invoke `/experiment-plan`).
  Stops at Phase 5 with `awaiting_human_continue` after producing FINAL_PROPOSAL +
  v1.3 Discovery/Grounding/Innovation artifacts only. Conservative users who want to review
  the proposal before committing to an experiment plan use this. Default is to chain
  through Phase 6 because the experiment plan still costs no GPU and gives the user one
  combined STOP point with everything pre-implementation in hand.

## Load First

- `shared-references/research-agent-pipeline.md` — v1.3 stage definitions for the
  Grounding (Stages 4/5/7) and Innovation (Stages 8/9/10) blocks
- `shared-references/research-harness-prompts.md` — sections `4`, `5`, `7`, `8`, `9`, `10`
  (the canonical prompt body for each stage this skill triggers)
- `shared-references/innovation-loops.md` — Loop A/B/C procedures (sections §2/§3/§4) +
  Codex collaborative-mode prompt template (§7.1)
- `shared-references/continuation-contract.md` — STATE.json schema, three-state enum,
  resume/idempotency rules, override flags
- `shared-references/reviewer-independence.md`

## State Persistence (Continuation Contract)

This skill follows the ORBIT v1.3 continuation contract — read
`shared-references/continuation-contract.md` for the canonical schema.

**STATE file:** `orbit-research/IDEA_TO_PROPOSAL_STATE.json`

Written at every phase boundary with overwrite semantics. Schema:

```jsonc
{
  "skill": "idea-to-proposal",
  "phase": "phase-3-innovation",         // last completed phase (one of:
                                          //   phase-0-intake, phase-0-5-literature-prefetch,
                                          //   phase-1-discovery, phase-2-grounding,
                                          //   phase-3-innovation, phase-4-final-refinement,
                                          //   phase-5-summary, phase-6-experiment-plan)
  "input_mode": "keyword" | "idea",      // detected at Phase 0
  "input_value": "$ARGUMENTS",           // verbatim
  "status": "in_progress" | "awaiting_human_continue" | "completed",
  "next_action": "phase-4-final-refinement",        // for same-skill resume
  "next_skill_hint": "/research-pipeline OR /experiment-plan",  // for downstream after Phase 5
  "timestamp": "<ISO 8601 UTC>",
  "artifact_inventory": [               // every output produced so far
    "orbit-research/PROBLEM_SELECTION.md",
    "orbit-research/ASSUMPTION_LEDGER.md",
    "orbit-research/ABSTRACT_TASK_MECHANISM.md",
    "orbit-research/BASELINE_CEILING.md",
    "orbit-research/MECHANISM_IDEATION.md",
    "orbit-research/ANALOGY_TRANSFER.md",
    "orbit-research/ALGORITHM_TOURNAMENT.md",
    "refine-logs/FINAL_PROPOSAL.md"
  ],
  "notes": "Optional — e.g. mode-detection rationale, Codex unavailability events"
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
   - Same skill being re-invoked (this case) → ask "continue past human checkpoint?"
     Default yes under AUTO_PROCEED. On yes, transition to `in_progress` and resume.
   - (Downstream skill case is handled by `/research-pipeline` Stage 0.)

### Idempotent phase skip

Before running each phase, check whether its expected output artifact already exists AND
the STATE entry says this phase completed. If both hold, skip the phase and log
"skipped (already done)". Phase artifact map:

| Phase | Expected artifact(s) |
|---|---|
| phase-0-intake | `orbit-research/PIPELINE_INTAKE.md` |
| phase-0-5-literature-prefetch | `papers/` non-empty (≥ 1 PDF) AND `STATE.literature_pre_fetched == true` AND STATE timestamp within last 24 h. Skipped silently when `parsed_flags.arxiv_download == false`. |
| phase-1-discovery | `refine-logs/FINAL_PROPOSAL.md` + `orbit-research/PROBLEM_SELECTION.md` |
| phase-2-grounding | `orbit-research/ASSUMPTION_LEDGER.md` + `ABSTRACT_TASK_MECHANISM.md` + `BASELINE_CEILING.md` |
| phase-3-innovation | `orbit-research/MECHANISM_IDEATION.md` + `ANALOGY_TRANSFER.md` + `ALGORITHM_TOURNAMENT.md` |
| phase-4-final-refinement | `refine-logs/FINAL_PROPOSAL.md` updated (mtime > Phase 1's write) |
| phase-5-summary | `orbit-research/PIPELINE_SUMMARY.md` |
| phase-6-experiment-plan | `refine-logs/EXPERIMENT_PLAN.md` + `orbit-research/CONTROL_DESIGN.md` + `NULL_RESULT_CONTRACT.md` + `COMPONENT_BUNDLE_LADDER.md` + `ALGORITHMIC_FORMALIZATION.md` + `DIAGNOSTIC_EXPERIMENT_PLAN.md` |

If artifact present but STATE entry missing/older, replay phase with a "refreshing
inconsistent state" warning.

### Override flags

| Flag | Effect |
|---|---|
| `— resume: true` | Force resume even if STATE looks ambiguous |
| `— fresh: true` | Delete STATE first; ignore existing artifacts; run from Phase 0 |
| `— from-phase: <N>` | Force start from the specified phase (1–5) |
| `— human checkpoint: true` | Pause at every phase boundary (write `awaiting_human_continue` after each), not just at Phase 5 |
| `— no-checkpoint: true` | Skip the Phase 6 `awaiting_human_continue` exit; transition straight to `completed` |
| `STOP_AT_GROUNDING: true` | Skip Phase 3 + Phase 4 + Phase 6; produce only Grounding artifacts; awaiting_human_continue at Phase 5 |
| `STOP_AT_PROPOSAL: true` | Skip Phase 6; produce proposal + Discovery/Grounding/Innovation artifacts only; awaiting_human_continue at Phase 5 |
| `— arxiv download: <bool>` | When `true`, run **Phase 0.5 (Literature Pre-fetch)** before Phase 1: delegates to `/research-lit` to populate `papers/` and `research-wiki/papers/` so downstream skills (especially `/research-refine`'s "Check `papers/` first" step in Phase 1b, and the Stage-4/5/7 grounding harness prompts in Phase 2) have local PDFs to scan. Default `false` (preserves prior behavior — grounding runs off whatever the LLM already knows). Without this flag, the literature pre-fetch is skipped silently. |
| `— sources: <list>` | Comma-separated source list for Phase 0.5. Subset of: `arxiv`, `web`, `semantic-scholar`, `deepxiv`, `exa`, `alphaxiv`, `local`, `all`. Default `arxiv`. Forwarded verbatim to `/research-lit — sources: <list>`. Has no effect if `— arxiv download: false`. |
| `— arxiv max download: <N>` | Cap on PDFs downloaded by Phase 0.5. Default `LITERATURE_PRE_FETCH_MAX_DEFAULT = 10`. Forwarded to `/research-lit — max download: <N>`. |
| `— venue: <name>` | Target venue (e.g. `iclr`, `icml`, `neurips`, `cvpr`, `naacl`). Recorded in `PIPELINE_INTAKE.md` and forwarded as `— venue: <name>` to `/research-refine`, `/research-pipeline`, and `/experiment-plan` so their reviewer prompts can name the venue specifically rather than the hardcoded "top venue". Default: unset. |
| `— effort: <level>` | Codex effort level: `low`, `medium`, `high`, `xhigh`, or `max` (alias for `xhigh`). Sets the per-call `model_reasoning_effort` for Codex MCP invocations across this skill (overrides `CODEX_REVIEW_EFFORT = xhigh` constant for this run). The actual effort honored is subject to Codex MCP environment availability — if the requested level is unavailable, Codex falls back to the next lower available level and the fallback (e.g. `gpt-5.2 high`) is logged in `STATE.notes`. |
| `— difficulty: <level>` | Calibrates the downstream `/research-refine` (Phase 1b idea-mode + Phase 4 final refinement) reviewer behavior + READY threshold + MAX_ROUNDS. Three levels (mirror upstream `/auto-review-loop` + `/research-pipeline`): `medium` (default) = standard reviewer + ≥9.0 / 5 rounds; `hard` = stricter reviewer + ≥9.5 / 7 rounds; `nightmare` = `hard` + reject-by-default per-dimension veto (every dimension ≥ 8) + ≥9.5 / 7 rounds. Forwarded verbatim as `— difficulty: <level>` to `/research-refine` (which honors it natively per its own `REVIEWER_DIFFICULTY` constant). |

## Workflow

### Phase 0: Detect Input Type and Initialise

**Resume check first.** Apply the entry decision tree above. If resuming, skip to the
phase indicated by `STATE.phase + 1` and continue from there (each downstream phase
applies its own idempotent-skip check).

Otherwise (fresh start), inspect `$ARGUMENTS`:

- If it is a **path to an existing file** ending in `.md` → **idea-mode**.
- Otherwise → **keyword-mode** (research area, topic phrase).

```bash
mkdir -p orbit-research/ refine-logs/
```

Write a one-line classifier note to `orbit-research/PIPELINE_INTAKE.md`:

```markdown
# Pipeline Intake
- Input: $ARGUMENTS
- Mode: keyword | idea
- Started: <ISO timestamp>
- Stops at: proposal (Validation Spine NOT triggered)
```

**Parse inline flags** from `$ARGUMENTS` and record them in
`orbit-research/PIPELINE_INTAKE.md` AND in the STATE block below. Flags
recognised by this skill (see Override flags table above for full list):
`AUTO_PROCEED`, `human checkpoint`, `STOP_AT_GROUNDING`, `STOP_AT_PROPOSAL`,
`arxiv download`, `sources`, `arxiv max download`, `venue`, `effort`,
`difficulty`, `from-phase`, `resume`, `fresh`, `no-checkpoint`.

Unknown flags are recorded in `PIPELINE_INTAKE.md` with a `⚠️ unknown flag —
will not be honored` annotation rather than silently dropped. **This is a
contract: a flag that survives parsing must either be honored or be flagged as
unknown — never silently captured-but-ignored.**

**Write STATE** at end of Phase 0:

```jsonc
{
  "skill": "idea-to-proposal",
  "phase": "phase-0-intake",
  "input_mode": "keyword | idea",
  "input_value": "$ARGUMENTS",
  "parsed_flags": {                      // every flag parsed in Phase 0
    "auto_proceed": true,
    "human_checkpoint": false,
    "arxiv_download": false,             // ← Phase 0.5 trigger
    "sources": "arxiv",
    "arxiv_max_download": 10,
    "venue": null,                        // forwarded to downstream reviewer prompts
    "effort": "xhigh",                    // CODEX_REVIEW_EFFORT for this run
    "difficulty": "medium"                // /research-refine threshold + MAX_ROUNDS
  },
  "status": "in_progress",
  "next_action": "phase-0-5-literature-prefetch | phase-1-discovery",   // depends on arxiv_download
  "timestamp": "<now>",
  "artifact_inventory": ["orbit-research/PIPELINE_INTAKE.md"]
}
```

### Phase 0.5: Literature Pre-fetch (conditional)

**Trigger condition**: `parsed_flags.arxiv_download == true` (i.e. user passed
`— arxiv download: true`). If false, **skip this phase silently** and proceed to
Phase 1 — the historical default behavior is preserved when the flag is absent
or false.

**Why this phase exists** (the bug it fixes): `/research-refine` (Phase 1b
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
- **idea-mode** (input is `.md`): read the file's headline / "Direction" /
  "Tasks" sections and synthesise a 1-2 line query of key technical terms
  (e.g. for the round-5 example: "DiT rectified-flow image editing
  post-training RL EditScore DanceGRPO").
- **keyword-mode** (input is a topic phrase): use it directly as the query.

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
`tools/research_wiki.py ingest_paper`. This skill does not duplicate that
logic.

**Step 3 — Fallback ladder when `/research-lit` is unavailable** (per the
standard ARIS-fallback contract):
1. Try `/research-lit` first (the canonical multi-source entry point).
2. If `/research-lit` skill is not registered, try `/arxiv "<query>" — download:
   all — max: <N>` directly. `/arxiv` covers the arXiv-only path and includes
   wiki ingestion in its Step 6.
3. If `/arxiv` is also unavailable, fall back to direct invocation of
   `tools/arxiv_fetch.py search` + `tools/arxiv_fetch.py download` per ID + (if
   `research-wiki/` exists) `tools/research_wiki.py sync research-wiki/
   — arxiv-ids <comma-list>`.
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
    — difficulty: <parsed_flags.difficulty>
```

(`/idea-discovery` itself internally calls `/research-refine-pipeline` →
`/research-refine`; the flags propagate through that chain. Omit any flag
whose parsed value is null / default.)

This produces:
- `idea-stage/IDEA_REPORT.md` (ranked candidates)
- `refine-logs/FINAL_PROPOSAL.md` (top idea, refined via `/research-refine-pipeline`)
- `refine-logs/EXPERIMENT_PLAN.md` (preliminary — will be **regenerated** when the user
  later commits to the Validation Spine; do NOT treat as canonical)
- `refine-logs/EXPERIMENT_TRACKER.md`
- `orbit-research/PROBLEM_SELECTION.md`

When `/idea-discovery` reaches its post-Phase-2 user checkpoint, pass through with the
top-ranked candidate unless the user passed `— human checkpoint: true`.

#### Phase 1b — idea-mode

Read the user's draft `.md` file, then invoke `/research-refine` with the
parsed flags forwarded:

```bash
/research-refine "$ARGUMENTS" \
    — venue: <parsed_flags.venue> \
    — effort: <parsed_flags.effort> \
    — difficulty: <parsed_flags.difficulty>
```

(Forward `venue` / `effort` / `difficulty` so `/research-refine`'s reviewer
prompt names the venue specifically rather than the hardcoded "top venue", and
so the Phase 4 READY threshold + MAX_ROUNDS match the user's difficulty
calibration. Omit a flag if its parsed value is null / default.)

If Phase 0.5 ran (`STATE.literature_pre_fetched == true`), `papers/` is now
populated with up to `parsed_flags.arxiv_max_download` PDFs and
`/research-refine`'s "Check `papers/` and `literature/` first" step (its
SKILL.md L181) will scan them as the grounding base — closing the loop that
this skill's `— arxiv download:` flag was originally promised to enable. If
Phase 0.5 was skipped (the flag was false or absent), `/research-refine` falls
back to whatever the LLM already knows about the area, as it always has.

This produces `refine-logs/FINAL_PROPOSAL.md`. Then derive `orbit-research/PROBLEM_SELECTION.md`
manually by extracting the Problem Anchor from `FINAL_PROPOSAL.md` and writing a brief
selection rationale (importance / audience / feasibility / headroom / paper survivability)
ending with `PROCEED | NARROW | RETHINK`. If `RETHINK`, stop here and surface the issue.

**Write STATE** at end of Phase 1 (both modes):

```jsonc
{
  "phase": "phase-1-discovery",
  "status": "in_progress",
  "next_action": "phase-2-grounding",
  "timestamp": "<now>",
  "artifact_inventory": [
    "orbit-research/PIPELINE_INTAKE.md",
    "refine-logs/FINAL_PROPOSAL.md",
    "orbit-research/PROBLEM_SELECTION.md"
    // + idea-stage/IDEA_REPORT.md if keyword-mode
  ]
}
```

If `— human checkpoint: true` is set, write `status: "awaiting_human_continue"` here too
and stop; resume on next invocation.

### Phase 2: Grounding — Stages 4 → 5 → 7

For each stage below, use the exact harness prompt from
`shared-references/research-harness-prompts.md`. Read the proposal from Phase 1 as input
context. Codex stays in adversarial mode here (Grounding is calibration, not invention).

#### Phase 2a — Stage 4: Assumption Ledger

Use harness §4. List every assumption the Phase 1 proposal depends on. Tag each as
`factual` (citable) or `working` (must be tested). Cover at minimum: data availability,
mechanism plausibility, baseline behaviour, evaluator validity, scale regime,
infrastructure cost, time horizon.

Write `orbit-research/ASSUMPTION_LEDGER.md`.

**Inline G2 reminder:** any "is/will/always" claim in downstream artifacts must trace
to a row in this ledger or get demoted.

#### Phase 2b — Stage 5: Abstract Task / Mechanism Framing

Use harness §5. Strip the problem to: input space, output space, decision structure,
information bottleneck, primary failure modes, candidate mechanism families (3–5).

Write `orbit-research/ABSTRACT_TASK_MECHANISM.md`.

#### Phase 2c — Stage 7: Baseline Ceiling / Headroom Audit

Use harness §7. If Phase 1 output already mentions baselines, deepen them; otherwise
estimate from scratch. List relevant simple-strong baselines, their estimated ceiling,
benchmark saturation risk, highest-headroom regime.

Write `orbit-research/BASELINE_CEILING.md`.

**Note:** headroom is a *reference*, not a veto. A low ceiling does not block the
pipeline; it calibrates how loud Phase 4's claim wording can be.

**Write STATE** at end of Phase 2:

```jsonc
{
  "phase": "phase-2-grounding",
  "status": "in_progress",
  "next_action": "phase-3-innovation",  // or "phase-5-summary" if STOP_AT_GROUNDING
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + ASSUMPTION_LEDGER.md, ABSTRACT_TASK_MECHANISM.md, BASELINE_CEILING.md */]
}
```

If `— human checkpoint: true`, write `awaiting_human_continue` and stop; resume on next call.

**Stop here if `STOP_AT_GROUNDING = true`.** Skip to Phase 5.

### Phase 3: Innovation — Stages 8 → 9 → 10 (Codex COLLABORATIVE)

Switch Codex to **collaborative mode** for all three stages (template in
`shared-references/innovation-loops.md` §7.1). Codex appends candidates / blind spots /
alternative framings; it does NOT veto, prune, or converge.

#### Phase 3a — Stage 8: Mechanism Invention Loop

Use harness §8 + procedure in `innovation-loops.md` §2. Generate 5–10 candidate
mechanisms aimed at the abstract task from Phase 2b. Score each on novelty / feasibility /
falsifiability (1–5 each). Aim for breadth — at least one obvious, one borrowed-from-
another-field, one minimal, one complex/composite, one wild card. Append a "Codex
collaborative additions" section after Codex returns.

Write `orbit-research/MECHANISM_IDEATION.md`. Mark a tentative top-3 for Phase 3b.

#### Phase 3b — Stage 9: Analogy / Cross-pollination Loop

Use harness §9 + procedure in `innovation-loops.md` §3. For each top-3 candidate, name ≥1
analogous solved problem from another field. Map *what transfers / what doesn't / what
new constraint*. Codex collaborative additions append more analogies.

Write `orbit-research/ANALOGY_TRANSFER.md`.

#### Phase 3c — Stage 10: Algorithm Sketch Tournament

Use harness §10 + procedure in `innovation-loops.md` §4. Write 1-page sketches per top
candidate (3–5 sketches). Round-robin pairwise on diagnosability / fidelity /
falsifiability / integration cost. Mark a TENTATIVE_PREFERRED_SKETCH_ID for Phase 4.
Keep alternates with their scores.

Codex on sketch quality is collaborative; on tournament adjudication Codex switches to
adversarial (this is the one place inside innovation loops where Codex challenges Claude's
pairwise picks — see `innovation-loops.md` §4 for the contract).

Write `orbit-research/ALGORITHM_TOURNAMENT.md` ending with the canonical line:

```
TENTATIVE_PREFERRED_SKETCH_ID: S<id>
ALTERNATES: S<id>, S<id>
ABSTAIN_REASONS: <if Codex objected>
NOT_FINAL_NOTE: Stage 10 selects candidates for Stage 11 HMBC review (not run by this
skill). The tentative pick is not a method commitment.
```

**Write STATE** at end of Phase 3:

```jsonc
{
  "phase": "phase-3-innovation",
  "status": "in_progress",
  "next_action": "phase-4-final-refinement",
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + MECHANISM_IDEATION, ANALOGY_TRANSFER, ALGORITHM_TOURNAMENT */]
}
```

### Phase 4: Integrated Final Refinement (Codex ADVERSARIAL)

Codex switches **back to adversarial mode**.

Feed the Phase 3c winner sketch back into `/research-refine`:

```bash
/research-refine "refine-logs/FINAL_PROPOSAL.md + orbit-research/ALGORITHM_TOURNAMENT.md TENTATIVE_PREFERRED_SKETCH_ID + orbit-research/ABSTRACT_TASK_MECHANISM.md + orbit-research/ASSUMPTION_LEDGER.md"
```

Goal: regenerate `refine-logs/FINAL_PROPOSAL.md` so it (a) anchors on the Phase 1 problem,
(b) declares the Phase 3c tentative sketch as the proposed method, (c) cites
ASSUMPTION_LEDGER row IDs for every "is/will" claim, (d) cites the abstract task framing,
(e) acknowledges the alternate sketches kept on the table for later revival.

If Codex flags a serious problem with the winner sketch, the integrated proposal MAY pick
an alternate from `ALGORITHM_TOURNAMENT.md` instead — record this in the proposal's
`## Method Selection Rationale` section.

The output is a **v1.3-aware FINAL_PROPOSAL.md**, not a brand-new file.

**Write STATE** at end of Phase 4:

```jsonc
{
  "phase": "phase-4-final-refinement",
  "status": "in_progress",
  "next_action": "phase-5-summary",
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + refine-logs/FINAL_PROPOSAL.md (regenerated, v1.3-aware) */]
}
```

### Phase 5: Pipeline Summary

Write `orbit-research/PIPELINE_SUMMARY.md`:

```markdown
# /idea-to-proposal Pipeline Summary

- Input: $ARGUMENTS
- Mode: keyword | idea
- Completed: <ISO timestamp>
- Validation Spine triggered: NO

## Artifact map (Discovery + Grounding + Innovation)

### Discovery (from /idea-discovery or /research-refine)
- refine-logs/FINAL_PROPOSAL.md           — final proposal index (v1.3-integrated)
- refine-logs/FINAL_PROPOSAL_SHORT.md     — clean short proposal
- refine-logs/METHOD_SPEC.md              — implementation-level method contract
- idea-stage/IDEA_REPORT.md                — (keyword mode only)
- orbit-research/PROBLEM_SELECTION.md      — problem selection verdict

### Grounding (Phase 2)
- orbit-research/ASSUMPTION_LEDGER.md      — every assumption tagged factual / working
- orbit-research/ABSTRACT_TASK_MECHANISM.md — abstract task + mechanism families
- orbit-research/BASELINE_CEILING.md       — simple-strong baseline reference

### Innovation (Phase 3, Codex collaborative)
- orbit-research/MECHANISM_IDEATION.md     — 5–10 candidate mechanisms
- orbit-research/ANALOGY_TRANSFER.md       — cross-domain analogies
- orbit-research/ALGORITHM_TOURNAMENT.md   — tentative preferred sketch + alternates

### Validation Prereqs (Phase 6 — pre-implementation, no GPU)
- refine-logs/EXPERIMENT_PLAN.md           — experiment-plan index (v1.3-aware)
- refine-logs/EXPERIMENT_PLAN_EXEC.md      — claim map, blocks, run order, gates, budget
- orbit-research/CONTROL_DESIGN.md         — required controls
- orbit-research/NULL_RESULT_CONTRACT.md   — what null/tie/fail means
- orbit-research/COMPONENT_BUNDLE_LADDER.md — progressive component / bundle order
- orbit-research/ALGORITHMIC_FORMALIZATION.md — pseudocode + loss + update rule
- orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md — cheapest valid diagnostic spec

(Skipped if --stop-at-proposal: true.)

## Next steps (NOT run by this skill — first GPU touch begins here)

1. /experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
   → implements code + writes PLAN_CODE_AUDIT.md (Stage 15 loop)
   → STOP B in the 4-stop HITL flow: review PLAN_CODE_AUDIT verdict before GPU

2. /diagnostic-to-review "[diagnostic command OR manifest]"
   → chains run-experiment → analyze-results → result-to-claim → auto-review-loop
   → auto-routes single command vs queue-batch
   → STOP C: any abort condition (verdict != PASS, claim_supported = no, etc.)
              surfaces as awaiting_human_continue with clear next_action

3. /paper-writing "NARRATIVE_REPORT.md" — venue: ICLR
   → final paper writing (G16/G18 enforced — needs CLAIM_CONSTRUCTION.md)

4. Or use /research-pipeline — Stage 0 reads IDEA_TO_PROPOSAL_STATE.json
   awaiting_human_continue + artifact_inventory and routes directly to
   Stage 15 (plan-code audit), skipping all the work this skill already did.
```

**Write STATE** at end of Phase 5:

If `STOP_AT_GROUNDING = true` OR `STOP_AT_PROPOSAL = true`:

```jsonc
{
  "phase": "phase-5-summary",
  "status": "awaiting_human_continue",     // designed checkpoint when STOP_AT_PROPOSAL set
  "next_action": "human-must-confirm-then-call-/experiment-plan-or-/research-pipeline",
  "next_skill_hint": "/experiment-plan OR /research-pipeline",
  "timestamp": "<now>",
  "artifact_inventory": [/* prior 9 v1.3 artifacts + PIPELINE_SUMMARY.md */]
}
```

Otherwise (default — chain to Phase 6):

```jsonc
{
  "phase": "phase-5-summary",
  "status": "in_progress",
  "next_action": "phase-6-experiment-plan",
  "timestamp": "<now>",
  "artifact_inventory": [/* prior + PIPELINE_SUMMARY.md */]
}
```

### Phase 6: Validation Prereqs — invoke `/experiment-plan`

**Skip this phase if `STOP_AT_PROPOSAL = true` or `STOP_AT_GROUNDING = true`.** Otherwise
chain to `/experiment-plan` to produce the EXPERIMENT_PLAN.md index, EXPERIMENT_PLAN_EXEC.md,
and Stage 11/12/13/14/16
prerequisites. This still costs **zero GPU**; it is the final pre-implementation step.

```bash
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

`/experiment-plan` (T4-upgraded) reads the v1.3 grounding/innovation artifacts produced in
Phases 2–4 (ASSUMPTION_LEDGER, ABSTRACT_TASK_MECHANISM, ALGORITHM_TOURNAMENT) and writes a
v1.3-aware `refine-logs/EXPERIMENT_PLAN.md` index plus `refine-logs/EXPERIMENT_PLAN_EXEC.md`
and:

- `orbit-research/CONTROL_DESIGN.md`
- `orbit-research/NULL_RESULT_CONTRACT.md`
- `orbit-research/COMPONENT_BUNDLE_LADDER.md`
- `orbit-research/ALGORITHMIC_FORMALIZATION.md`
- `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`

If `/experiment-plan` returns an unrecoverable error (proposal too vague, claim map
unfillable, etc.), surface to user and write Phase 6 STATE with `status = "in_progress"` +
`next_action = "experiment-plan-failed:<reason>"` so the user can fix and re-invoke.

**Write final STATE** at end of Phase 6 with **`awaiting_human_continue`** (this is now
the designed human checkpoint of this skill — combined STOP A: proposal index + experiment plan index + execution plan
reviewed together):

```jsonc
{
  "skill": "idea-to-proposal",
  "phase": "phase-6-experiment-plan",
  "input_mode": "keyword | idea",
  "input_value": "$ARGUMENTS",
  "status": "awaiting_human_continue",
  "next_action": "human-must-confirm-then-call-/experiment-bridge-or-/research-pipeline",
  "next_skill_hint": "/experiment-bridge OR /research-pipeline",
  "timestamp": "<now>",
  "artifact_inventory": [
    "orbit-research/PIPELINE_INTAKE.md",
    "orbit-research/PROBLEM_SELECTION.md",
    "orbit-research/ASSUMPTION_LEDGER.md",
    "orbit-research/ABSTRACT_TASK_MECHANISM.md",
    "orbit-research/BASELINE_CEILING.md",
    "orbit-research/MECHANISM_IDEATION.md",
    "orbit-research/ANALOGY_TRANSFER.md",
    "orbit-research/ALGORITHM_TOURNAMENT.md",
    "orbit-research/CONTROL_DESIGN.md",
    "orbit-research/NULL_RESULT_CONTRACT.md",
    "orbit-research/COMPONENT_BUNDLE_LADDER.md",
    "orbit-research/ALGORITHMIC_FORMALIZATION.md",
    "orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md",
    "orbit-research/PIPELINE_SUMMARY.md",
    "refine-logs/FINAL_PROPOSAL.md",
    "refine-logs/FINAL_PROPOSAL_SHORT.md",
    "refine-logs/METHOD_SPEC.md",
    "refine-logs/EXPERIMENT_PLAN.md",
    "refine-logs/EXPERIMENT_PLAN_EXEC.md"
    // + idea-stage/IDEA_REPORT.md if keyword-mode
  ]
}
```

`awaiting_human_continue` is the **deliberate** terminal state for this skill. The user
inspects the artifacts (especially `FINAL_PROPOSAL.md` + `EXPERIMENT_PLAN.md` together —
the combined "is this worth GPU?" decision point) and decides:

- **Continue to implementation** — invoke `/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"`.
  The next skill reads `IDEA_TO_PROPOSAL_STATE.json`, sees `awaiting_human_continue`, and
  treats invocation as the human's "approve continue" signal.

- **Continue via orchestrator** — invoke `/research-pipeline`. Stage 0 detects this STATE
  and routes directly to Stage 15 (plan-code audit) skipping Discovery/Grounding/Innovation/
  validation-prereqs, all of which are already done.

- **Iterate experiment plan** — invoke `/experiment-plan "refine-logs/FINAL_PROPOSAL.md" — fresh: true`
  to regenerate Phase 6 outputs only.

- **Iterate proposal** — invoke `/idea-to-proposal "..." — fresh: true` (full rerun) or
  manual edit `FINAL_PROPOSAL.md` then `/idea-to-proposal "..." — from-phase: 6` to
  re-invoke just the experiment-plan phase on the edited proposal.

- **Abandon** — leave it. STATE stays `awaiting_human_continue` indefinitely.

To skip this checkpoint and run straight through to `completed`, pass `— no-checkpoint: true`.

### Conservative variant (early STOP at proposal)

If you want to review the proposal *before* generating the experiment plan (the original
5-stop flow), pass `— stop-at-proposal: true`. This gives you Phase 1–5 only; Phase 6 is
not invoked. After your review, manually run `/experiment-plan` to get the validation
prereqs.

## ARIS / Sub-skill Unavailability

For each delegated invocation (`/idea-discovery`, `/research-refine`, `/research-refine-pipeline`),
follow the standard fallback pattern:

```text
Try slash invocation.
If skill not registered:
  Print "ORBIT skill <name> unavailable. Phase <N> degraded: <fallback or HUMAN_DECISION_REQUIRED>."
  Continue gracefully.
If the missing skill was load-bearing for a v1.3 artifact (e.g. /research-refine for
FINAL_PROPOSAL.md):
  Escalate — do not silently produce an incomplete proposal.
```

For Codex MCP unavailability during Phase 3 (Innovation):
- The collaborative-mode addition is **enrichment**, not load-bearing. Mark each affected
  artifact with `## Codex collaborative additions: NOT_AVAILABLE (codex_mcp_unreachable)`
  and continue. Do not block the pipeline.
- For Phase 3c tournament adjudication (where Codex is adversarial), if Codex is down,
  proceed with Claude's pairwise picks but mark `ABSTAIN_REASONS: codex_mcp_unreachable —
  tournament adjudication is single-model only this round`.

For Codex MCP unavailability during Phase 4 (final refinement adversarial review):
- Skip Codex review, mark proposal `## Phase 4 review: SKIPPED (codex_mcp_unreachable)`,
  and continue. The integrated FINAL_PROPOSAL.md still gets written.

## What This Skill Deliberately Does NOT Do

- Does **not** invoke `/experiment-plan`, `/experiment-bridge`, `/run-experiment`,
  `/experiment-queue`, `/result-to-claim`, `/auto-review-loop`, `/paper-writing`, or any
  Validation Spine skill.
- Does **not** write `CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`,
  `COMPONENT_BUNDLE_LADDER.md`, `ALGORITHMIC_FORMALIZATION.md`, `PLAN_CODE_AUDIT.md`, or
  any DIAGNOSTIC_RUN_*.md.
- Does **not** touch GPUs.
- Does **not** finalise method commitment — Stage 10's pick is explicitly tentative
  (`TENTATIVE_PREFERRED_SKETCH_ID`); convergence happens at Stage 11 HMBC, run by
  `/research-pipeline` or `/experiment-plan`.

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Final Rule

```text
Discover then ground then invent then write a proposal — no implementation, no GPU.
Innovation produces candidates; this skill stops before commitment picks one for real.
The proposal carries the tentative sketch ID forward; downstream skills can switch.
```
