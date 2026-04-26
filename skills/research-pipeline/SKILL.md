---
name: research-pipeline
description: "ORBIT v1.3 research-methodology routing harness built on ARIS skills. Routes by mode (EXPLORATION/INNOVATION/COMMITMENT) and risk (1-5) through 26 stages organised into four spines (Discovery/Grounding/Innovation/Validation). Innovation loops for divergent mechanism invention; artifact-triggered audits; cheapest valid diagnostic; verdict-line gates only at high-risk transitions. Reuses mature ARIS execution skills (/auto-review-loop, /paper-writing, /experiment-bridge, etc.) instead of reimplementing them. Use when user says 全流程/full pipeline/end-to-end research/从问题到论文/ORBIT/自动科研流水线/ORBIT v1.3."
argument-hint: [research-area-or-problem-or-artifact-path]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

# ORBIT Research Pipeline — v1.3 Routing Orchestrator

Run the v1.3 research-methodology workflow for: **$ARGUMENTS**

This is the ORBIT control skill. It does **not** force every stage on every request. It
routes by user input shape, mode, and risk, and only enforces hard gates before high-risk
irreversible transitions. It preserves and reuses mature ARIS execution skills (do not
reimplement them).

## Load First

Before executing the pipeline, read:

- `shared-references/research-agent-pipeline.md` — v1.3 canonical stage map, hard gates G0–G19
- `shared-references/research-harness-prompts.md` — per-stage canonical prompt
- `shared-references/innovation-loops.md` — Stages 8/9/10/18.5 procedures + Codex collaborative mode
- `shared-references/semantic-code-audit.md` — Stage 15 plan-code audit + Stage 17 diagnostic-run audit
- `shared-references/continuation-contract.md` — STATE.json schema, three-state enum, cross-skill resume rules (used by Stage 0 routing)
- `shared-references/reviewer-independence.md`
- `shared-references/reviewer-routing.md`

## Constants

- **OUTPUT_ROOT = `orbit-research/`** — v1.3 artifacts live here unless the project already
  has a better convention.
- **CODEX_REVIEW_MODEL = `gpt-5.5`** — Default Codex reviewer for ORBIT.
- **CODEX_REVIEW_EFFORT = `xhigh`** — Mandatory for all ORBIT review gates.
- **CODEX_SANDBOX_MODE = `danger-full-access`** — Set globally in `~/.codex/config.toml`,
  not per call. Codex MCP `config` only accepts `model_reasoning_effort`; do not try to
  pass `sandbox` per call.
- **REVIEWER_INDEPENDENCE = on** — Pass file paths and objective, not executor summaries.
- **CODEX_INNOVATION_MODE** — `COLLABORATIVE` at Stages 8, 9, 10, 18.5 (use template in
  `innovation-loops.md` §7.1); `ADVERSARIAL` everywhere else (use templates in
  `semantic-code-audit.md` and `research-harness-prompts.md`).
- **MAX_DEBATE_ROUNDS = 2** — Prevent infinite Claude vs Codex debate loops.
- **AUTO_WRITE = false** — If true, run `/paper-writing` after CLAIM_CONSTRUCTION and
  RED_TEAM_REVIEW gates pass.
- **VENUE = `ICLR`** — Used when paper writing is enabled.
- **AUTO_PROCEED = false** for irreversible actions: GPU scale-up, final paper claims,
  stopping a project.

## Canonical Outputs (v1.3)

Create or update these artifacts as the project progresses. Producers emit v1.3 names
only; consumers (this orchestrator, experiment-queue, semantic audit) accept v1.0 aliases
where noted, preferring v1.3 if both exist.

```text
orbit-research/MODE_ROUTING.md
orbit-research/SEED_FRAMING.md
orbit-research/LITERATURE_MAP.md
orbit-research/PROBLEM_REFRAMING.md           (when triggered)
orbit-research/PROBLEM_SELECTION.md
orbit-research/ASSUMPTION_LEDGER.md
orbit-research/ABSTRACT_TASK_MECHANISM.md
orbit-research/ARTIFACT_AUDIT.md              (when an artifact actually exists)
orbit-research/BASELINE_CEILING.md
orbit-research/MECHANISM_IDEATION.md          (innovation: Codex collaborative)
orbit-research/ANALOGY_TRANSFER.md            (innovation: Codex collaborative)
orbit-research/ALGORITHM_TOURNAMENT.md        (innovation: Codex collaborative)
orbit-research/CONTROL_DESIGN.md
orbit-research/NULL_RESULT_CONTRACT.md
orbit-research/COMPONENT_BUNDLE_LADDER.md     (v1.0 alias: COMPONENT_LADDER.md)
orbit-research/ALGORITHMIC_FORMALIZATION.md
orbit-research/PLAN_CODE_AUDIT.md             (verdict line: MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR)
orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md  (v1.0 alias: TINY_RUN_PLAN.md)
orbit-research/DIAGNOSTIC_RUN_REPORT.md       (v1.0 alias: TINY_RUN_REPORT.md)
orbit-research/DIAGNOSTIC_RUN_AUDIT.md        (v1.0 alias: TINY_RUN_AUDIT.md; verdict: PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT)
orbit-research/RESULT_INTERPRETATION.md
orbit-research/FAILURE_TO_INNOVATION.md       (when triggered, innovation: Codex collaborative)
orbit-research/LITERATURE_REREAD_NOTE.md
orbit-research/SCALEUP_DECISION.md            (verdict line: PROCEED | HOLD | REDESIGN | HUMAN_DECISION_REQUIRED)
orbit-research/CLAIM_CONSTRUCTION.md
orbit-research/NEGATIVE_RESULT_STRATEGY.md    (when tie/failure)
orbit-research/RED_TEAM_REVIEW.md             (loop output from /auto-review-loop)
orbit-research/PAPER_IMPROVEMENT_LOG.md       (loop output from /paper-writing chain)
orbit-research/HUMAN_DECISION_NOTE.md         (verdict line: PROCEED | NARROW | REDESIGN | RE-READ | CHANGE BENCHMARK | STOP | HUMAN_DECISION_REQUIRED)
```

Also reuse existing ARIS outputs when present:

- `idea-stage/IDEA_REPORT.md`
- `idea-stage/IDEA_CANDIDATES.md`
- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/EXPERIMENT_PLAN.md`
- `refine-logs/EXPERIMENT_TRACKER.md`
- `review-stage/AUTO_REVIEW.md`
- `NARRATIVE_REPORT.md`
- `paper/`

## Stage 00: Initialize Workspace

Before any other stage:

```bash
mkdir -p orbit-research/
```

Idempotent. Every downstream skill assumes `orbit-research/` exists; create it once at the
controller level so artifact writes never silently fail on a fresh project.

## Stage 0: Mode & Risk Routing (FIRST ACTION)

The orchestrator's first action — before anything else.

### Step 0a: Cross-skill continuation check (NEW — runs before input classification)

Per the canonical contract in `shared-references/continuation-contract.md`, look for any
upstream `*_STATE.json` produced by a prior skill that may want this orchestrator to
continue from a known point. Glob:

```bash
ls orbit-research/*_STATE.json refine-logs/*_STATE.json review-stage/*_STATE.json paper/.aris/*_STATE.json 2>/dev/null
```

For each STATE file found, read it and apply the cross-skill resume rules:

| Upstream STATE | Action |
|---|---|
| `status = "awaiting_human_continue"` AND user invoked `/research-pipeline` (downstream of this skill) | **Treat as approval to continue.** Load `artifact_inventory`. Use the artifact-presence routing path below to skip already-completed stages. Note this in `MODE_ROUTING.md` as "Continuing from <skill> output (artifacts loaded)." |
| `status = "in_progress"` AND `timestamp < 24h` | Warn user the upstream skill was mid-execution. Ask: "resume `<upstream skill>` first?" If yes, exit and direct user to that skill. If no, proceed with fresh routing on `$ARGUMENTS`. |
| `status = "in_progress"` AND `timestamp ≥ 24h` | Stale; ignore (or offer cleanup). Proceed with fresh routing. |
| `status = "completed"` | Treat as historical context only. Proceed with fresh routing on `$ARGUMENTS` unless `— resume: true` is passed. |

### Step 0b: Artifact-presence routing (works even without STATE files)

Glob `orbit-research/*.md` to enumerate v1.3 artifacts already on disk. Map artifact
presence → suggested first stage:

| Artifacts present | Inferred starting stage | Suggested mode |
|---|---|---|
| `PROBLEM_SELECTION.md` + `ASSUMPTION_LEDGER.md` + `ABSTRACT_TASK_MECHANISM.md` + `ALGORITHM_TOURNAMENT.md` (all present) | **Stage 11** (commitment) — Discovery + Grounding + Innovation already done by upstream | COMMITMENT (risk 4) |
| `PROBLEM_SELECTION.md` + `ASSUMPTION_LEDGER.md` + `ABSTRACT_TASK_MECHANISM.md` only (no Innovation artifacts) | **Stage 8** (Innovation entry) — Grounding done, Innovation needed | INNOVATION (risk 2–3) |
| `PROBLEM_SELECTION.md` only | **Stage 4** (Grounding entry) | INNOVATION (risk 2) |
| `MODE_ROUTING.md` + `SEED_FRAMING.md` only | **Stage 2** (Literature Map continuation) | EXPLORATION (risk 1–2) |
| `PLAN_CODE_AUDIT.md` verdict = `MATCHES_PLAN` + `DIAGNOSTIC_RUN_AUDIT.md` absent | **Stage 16/17** (run diagnostic) | COMMITMENT (risk 3–4) |
| `DIAGNOSTIC_RUN_AUDIT.md` verdict = `PASS` + `SCALEUP_DECISION.md` absent | **Stage 20** (scale-up decision) | COMMITMENT (risk 4) |
| `CLAIM_CONSTRUCTION.md` + `RED_TEAM_REVIEW.md` + `HUMAN_DECISION_NOTE.md` all present | **Stage 24** (paper writing) | COMMITMENT (risk 4–5) |
| (none of the above) | Fall through to Step 0c input-shape classification | (decide below) |

When this routing applies, **bypass** the input-shape table and write `MODE_ROUTING.md`
with both the inferred routing AND the trigger artifacts:

```
EXPLORATION | INNOVATION | COMMITMENT + risk: <N>
trigger: artifact-presence (loaded: <comma-separated artifact basenames>)
upstream-state: <SKILL>_STATE.json: <status>
first-stage: <stage number>
```

### Step 0c: Input-shape classification (fallback when no continuation applies)

If neither Step 0a nor Step 0b matched a continuation, classify `$ARGUMENTS` into one of
these categories:

| Category | Trigger | Suggested mode | Initial risk | First stages to run |
|---|---|---|---|---|
| Broad area | `$ARGUMENTS` is a research domain | EXPLORATION | 1–2 | 1 → 2 → 2.5 → 3 |
| Concrete idea, no artifact | `$ARGUMENTS` is a problem statement, no data/code yet | INNOVATION | 2–3 | 4 → 5 → 7 → 8/9/10 |
| Concrete data / benchmark / sim / reward in hand | `$ARGUMENTS` references an artifact path | INNOVATION/COMMITMENT | 2–4 | 6 (artifact-triggered audit) → 7 → 11+ |
| Designing new method | user explicitly wants ideation | INNOVATION | 2–3 | 4 → 5 → 8 → 9 → 10 |
| Implementing official experiments | proposal + plan exist | COMMITMENT | 4 | 11 → 12 → 13 → 14 → 15 → 16 |
| Running experiments | implementation exists | COMMITMENT | 3–4 | 16 → 17 → 18 |
| Results failed / surprised | result interpretation says tie or failure | INNOVATION | 2–3 | 18 → 18.5 → 19 → (back to 8 or 11) |

**Action:**

1. Use the Stage 0 harness from `research-harness-prompts.md`.
2. Apply Step 0a (continuation check) → Step 0b (artifact-presence routing) →
   Step 0c (input-shape classification), in order. The first one that matches wins.
3. Write `orbit-research/MODE_ROUTING.md` ending with one canonical line:
   `EXPLORATION | INNOVATION | COMMITMENT + risk: <1-5>`.
4. **Auto-stub for low-risk single-stage commands:** when this orchestrator is invoked
   with no `MODE_ROUTING.md` and the requested action is low-risk single-stage work
   (no scale-up, no paper writing), default to `EXPLORATION + risk: 1` and write a stub.
   Continue without blocking.
5. **Honour `— from-stage: N` override:** if the user passes an explicit stage number
   inline, that wins over Step 0a/b/c. Still write MODE_ROUTING.md noting the override.

**Gate G0:** for high-risk transitions (scale-up, paper writing, public release, official
experiment planning), if mode/risk cannot be inferred from upstream STATE, prior artifacts,
or an inline `— mode:` flag, block; require explicit Stage 0 routing.

**After Stage 0,** run only the stages relevant to the user's input shape OR the inferred
continuation point. Do not force a linear walk through 0–25.

## Per-stage orchestration blocks

Each block: when to run, which sub-skill to invoke, required input artifacts, output
artifact + verdict expected, gate(s) checked. Inline accept-either parsing reads the v1.3
name first, falls back to v1.0 alias.

### Stage 1: Seed Framing

**When:** category = broad area, or `SEED_FRAMING.md` is missing and the user's input is
a domain rather than a concrete problem.

**Action:**

1. Use the Stage 1 harness from `research-harness-prompts.md`.
2. Write `orbit-research/SEED_FRAMING.md`.

### Stage 2: Question-driven Literature Map (loop)

**When:** category = broad area, or before problem selection. Re-fires at Stage 19 after
early results.

**Sub-skill invocation:**

```bash
/research-lit "$ARGUMENTS"
```

Optionally use `/arxiv`, `/semantic-scholar`, `/exa-search`, `/deepxiv`, Zotero, Obsidian,
local PDFs.

**Action:** write `orbit-research/LITERATURE_MAP.md`.

**Codex (adversarial):** checks missing papers, missing baselines, overclaimed assumptions,
claim-evidence gaps, benchmark saturation.

### Stage 2.5: Problem Reframing Loop

**When:** literature map suggests the problem-as-stated is the wrong cut.

**Action:** use the Stage 2.5 harness from `research-harness-prompts.md`. Write
`orbit-research/PROBLEM_REFRAMING.md` ending with `KEEP | REFRAME | SPLIT`.

### Stage 3: Problem Taste / Problem Selection

**When:** before any commitment. Required by **G1** for method commitment, official
experiment planning, or GPU run (unless mode = EXPLORATION/INNOVATION and outputs are
clearly marked as candidates).

**Action:**

1. Run Claude vs Codex debate (adversarial). Codex attacks feasibility, baseline risk,
   paper value if the method ties.
2. Write `orbit-research/PROBLEM_SELECTION.md` ending with `PROCEED | NARROW | RETHINK`.

### Stage 4: Assumption Ledger

**When:** before mechanism invention OR before any committed experiment. Required by
**G2** (downstream "is/will/always" claims must trace to a ledger entry).

**Action:** use the Stage 4 harness. Write `orbit-research/ASSUMPTION_LEDGER.md` with rows
tagged `factual` (citable) or `working` (must be tested).

### Stage 5: Abstract Task / Mechanism Framing

**When:** before mechanism invention (Stage 8). Required by **G3** at commitment time
(Stage 11+); not strictly required at Stage 8/9/10 in EXPLORATION/INNOVATION mode.

**Action:** use the Stage 5 harness. Write `orbit-research/ABSTRACT_TASK_MECHANISM.md`.

### Stage 6: Artifact-triggered Data / Env / Benchmark Audit

**When:** **only when** a concrete data set, environment, simulator, reward function,
evaluator, or split actually exists or has been fetched. **Gate G4:** do NOT force this
audit before such an artifact exists. Re-emit whenever the audited artifact changes.

**Action:** use the Stage 6 harness. Write `orbit-research/ARTIFACT_AUDIT.md`.

**Codex (adversarial):** acts as data/task ontology auditor; tries to find category errors
or leakage.

### Stage 7: Baseline Ceiling / Headroom Audit

**When:** before any "outperforms / beats / improves over" claim (G5), unless mode =
EXPLORATION AND no paper claim is being made.

**Action:** use the Stage 7 harness. Write `orbit-research/BASELINE_CEILING.md`.

**Codex (adversarial):** argues whether the simple baseline is already too strong or
whether the benchmark/claim must change. Headroom is a reference, not a veto.

### Stage 8: Mechanism Invention Loop  *(Codex COLLABORATIVE)*

**When:** category = designing new method, OR before commitment in INNOVATION mode.

**Codex mode switch:** `CODEX_INNOVATION_MODE = COLLABORATIVE`. Use template in
`innovation-loops.md` §7.1. Codex appends candidates; does NOT veto.

**Action:** use the Stage 8 harness. See `innovation-loops.md` §2 for the full procedure.
Write `orbit-research/MECHANISM_IDEATION.md` with all candidates visible (none pruned),
top-3 marked for Stage 9, and a "Codex collaborative additions" section.

### Stage 9: Analogy / Cross-pollination Loop  *(Codex COLLABORATIVE)*

**When:** after `MECHANISM_IDEATION.md` exists.

**Codex mode:** COLLABORATIVE.

**Action:** use the Stage 9 harness. See `innovation-loops.md` §3. Write
`orbit-research/ANALOGY_TRANSFER.md`.

### Stage 10: Algorithm Sketch Tournament  *(Codex COLLABORATIVE on sketch / ADVERSARIAL on adjudication)*

**When:** after `MECHANISM_IDEATION.md` and `ANALOGY_TRANSFER.md` exist.

**Codex mode:** COLLABORATIVE on sketch quality; ADVERSARIAL on tournament adjudication.

**Action:** use the Stage 10 harness. See `innovation-loops.md` §4. Write
`orbit-research/ALGORITHM_TOURNAMENT.md` ending with
`TENTATIVE_PREFERRED_SKETCH_ID + ALTERNATES + ABSTAIN_REASONS`. The tentative pick is
**not** a method commitment — Stage 11 (HMBC matrix) reviews it and may switch to an
alternate or send the project back to Stage 8.

### Stage 11: Hypothesis-Mechanism-Benchmark-Control Matrix  *(Codex switches BACK to ADVERSARIAL)*

**When:** committing to an experiment plan. Required by **G6** (≥1 of MECHANISM_IDEATION
/ ANALOGY_TRANSFER / ALGORITHM_TOURNAMENT must exist before commitment).

**Sub-skill invocation:**

```bash
/research-refine "$ARGUMENTS"
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

**Action:** use the Stage 11 harness. Write `orbit-research/CONTROL_DESIGN.md`.

**Codex (adversarial):** attacks control isolation, null-result interpretability, component
attribution, rollback conditions, algorithmic self-consistency.

### Stage 12: Null-result Contract

**When:** before any diagnostic/confirmatory experiment. Required by **G8** unless run is
explicitly marked "exploratory probe" (no paper claim allowed).

**Action:** use the Stage 12 harness. Write `orbit-research/NULL_RESULT_CONTRACT.md`.

### Stage 13: Progressive Component / Minimal Mechanism Bundle

**When:** before any official (full-system) run with a new composed method. Required by
**G9** unless run is a baseline reproduction or single-component run.

**Action:** use the Stage 13 harness. Write `orbit-research/COMPONENT_BUNDLE_LADDER.md`
(consumers also read v1.0 alias `COMPONENT_LADDER.md`). Bundle entries must include
indivisibility justification.

### Stage 14: Algorithmic Formalization

**When:** before official experiments. Required by **G10** unless mode = EXPLORATION AND
no scale-up requested.

**Action:** use the Stage 14 harness. Write `orbit-research/ALGORITHMIC_FORMALIZATION.md`.

### Stage 15: Plan-Code Consistency Loop

**When:** after implementation lands; loops audit → fix → re-audit until verdict is
`MATCHES_PLAN` or scoped `PARTIAL_MISMATCH`.

**Sub-skill invocation:**

```bash
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
```

Then run semantic audit per `shared-references/semantic-code-audit.md`.

**Action:**

1. Codex reads v1.3 plan artifacts (ASSUMPTION_LEDGER, ABSTRACT_TASK_MECHANISM,
   ALGORITHM_TOURNAMENT TENTATIVE_PREFERRED_SKETCH_ID, ALGORITHMIC_FORMALIZATION, COMPONENT_BUNDLE_LADDER,
   CONTROL_DESIGN, NULL_RESULT_CONTRACT, DIAGNOSTIC_EXPERIMENT_PLAN, FINAL_PROPOSAL,
   EXPERIMENT_PLAN) and implementation files directly.
2. Always write `orbit-research/PLAN_CODE_AUDIT.md` with the verdict line on its own line:
   one of `MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`.

**Gate G11:**

- `MATCHES_PLAN` proceeds.
- `PARTIAL_MISMATCH` proceeds only if the missing pieces are irrelevant to the next run.
- `CRITICAL_MISMATCH` blocks scale-up unconditionally; loop fix → re-audit.
- `ERROR` (Codex unavailable, audit could not complete) is **advisory at the diagnostic /
  sanity run stage** (proceed, surface the reason code) and **blocks at scale-up pending
  explicit human acknowledgement** (scale-up is irreversible; do not launch without a
  person on the loop).
- Compile success is not enough.

### Stage 16: Cheapest Valid Diagnostic

**When:** before scale-up. Designed to be the cheapest run that could **falsify the
central claim** — not necessarily a tiny run.

**Action:** use the Stage 16 harness. Write `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`
(consumers also read v1.0 alias `TINY_RUN_PLAN.md`).

### Stage 17: Diagnostic Run Audit

**Sub-skill invocation:**

```bash
/run-experiment "[diagnostic command OR manifest OR grid]"
/monitor-experiment "[run id or server]"
```

`/run-experiment` auto-routes by input shape:
- single command / ≤5 jobs → runs inline (with STATE-based resume if interrupted)
- ≥10 jobs / multi-seed sweep / wave dependencies → auto-delegates to `/experiment-queue`
- 6–9 jobs (gray zone) → inline parallel; user can force `— queue: true`

The orchestrator does not need to choose between `/run-experiment` and `/experiment-queue`.
Pass the diagnostic spec to `/run-experiment` and it handles routing. Override flags:
`— queue: true` / `— solo: true` if the user wants to force a path.

**Action:**

1. Run the cheapest valid diagnostic via `/run-experiment` (it routes if needed).
2. Write `orbit-research/DIAGNOSTIC_RUN_REPORT.md` (consumers also read v1.0 alias
   `TINY_RUN_REPORT.md`).
3. Codex audits outputs against the plan with **G12 regime check**: if the run failed,
   did the failure regime preserve the mechanism's necessary preconditions? If not,
   recommend redesign rather than reject the mechanism.
4. Write `orbit-research/DIAGNOSTIC_RUN_AUDIT.md` (consumers also read v1.0 alias
   `TINY_RUN_AUDIT.md`) with verdict line: `PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT`.

**Gate:** do not full-run unless `DIAGNOSTIC_RUN_AUDIT.md` (or `TINY_RUN_AUDIT.md`) verdict
is `PASS`. `FIX_BEFORE_GPU` and `REDESIGN_EXPERIMENT` block.

### Stage 18: Result Interpretation Loop

**Sub-skill invocation:**

```bash
/analyze-results "[results path]"
```

**Action:** write `orbit-research/RESULT_INTERPRETATION.md` after every experiment.

**Gate G14:** if NULL_RESULT_CONTRACT triggered tie/failure, frame the result honestly —
do not write positive narrative. Route to Stage 22 if writing a paper from a tie/failure.

### Stage 18.5: Failure-to-Innovation Loop  *(Codex COLLABORATIVE)*

**When:** RESULT_INTERPRETATION shows tie or failure, OR Stage 17 returned
`REDESIGN_EXPERIMENT` (with a regime that preserved mechanism preconditions — otherwise
G12 routes back to Stage 16, not here).

**Codex mode:** COLLABORATIVE.

**Action:** use the Stage 18.5 harness. See `innovation-loops.md` §5. Write
`orbit-research/FAILURE_TO_INNOVATION.md`.

### Stage 19: Re-read Literature Loop

**When:** RESULT_INTERPRETATION or FAILURE_TO_INNOVATION raises a question literature
might answer.

**Sub-skill invocation:** targeted `/research-lit` calls per question.

**Action:** see `innovation-loops.md` §6. Write `orbit-research/LITERATURE_REREAD_NOTE.md`.

### Stage 20: Scale-up Decision

**Sub-skill invocation:**

```bash
/result-to-claim "[experiment description]"
```

**Action:**

1. Verify Stage 20 preconditions (per harness §20): ARTIFACT_AUDIT (when applicable),
   BASELINE_CEILING, CONTROL_DESIGN, NULL_RESULT_CONTRACT, DIAGNOSTIC_RUN_AUDIT verdict,
   PLAN_CODE_AUDIT verdict, ALGORITHMIC_FORMALIZATION (if scaling official),
   COMPONENT_BUNDLE_LADDER (if new composed method).
2. **Gate G15:** if mode = COMMITMENT or risk_score ≥ 4, require `HUMAN_DECISION_NOTE.md`
   before SCALEUP_DECISION = PROCEED.
3. **Gate G19:** scale-up is a "high-risk transition" — `HUMAN_DECISION_NOTE.md` required.
4. Write `orbit-research/SCALEUP_DECISION.md` ending with
   `PROCEED | HOLD | REDESIGN | HUMAN_DECISION_REQUIRED`.

### Stage 21: Result-to-Claim Construction

**Sub-skill invocation:** `/result-to-claim` (already invoked at Stage 20 — reuse output).

**Action:**

1. Build claim → evidence → control → scope → limitation chain.
2. **Gate G17:** label exploratory findings explicitly as "exploratory finding, not
   pre-planned hypothesis." Do not present post-hoc reframings as pre-planned hypotheses.
3. Write `orbit-research/CLAIM_CONSTRUCTION.md`.

**Gate G16:** Stage 24 (paper writing) refuses to start without `CLAIM_CONSTRUCTION.md`.

### Stage 22: Tie / Negative Result / Reframing Strategy

**When:** result ties or fails.

**Action:** use the Stage 22 harness. Write `orbit-research/NEGATIVE_RESULT_STRATEGY.md`.
Apply G17 anti-post-hoc check.

### Stage 23: Reviewer Red-team Loop

**Sub-skill invocation:**

```bash
/auto-review-loop "$ARGUMENTS" — difficulty: hard
/experiment-audit "[results and code]"
```

**Action:** review → fix → re-review iterations managed by `/auto-review-loop`. Output
rolls up into `orbit-research/RED_TEAM_REVIEW.md` (the ARIS skill writes here directly per
its inline gate; this orchestrator does not duplicate the writing).

### Stage 24: Paper Writing / Paper Improvement Loop

**Gate G16 + G18:** refuse start if `CLAIM_CONSTRUCTION.md` is absent (also enforced
inline in `paper-writing/SKILL.md`).

**Sub-skill invocation chain (delegated to ARIS):**

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: $VENUE, assurance: submission
```

`/paper-writing` transitively invokes: `/paper-plan`, `/paper-figure`, `/figure-spec` or
`/paper-illustration`, `/paper-write`, `/paper-compile`, `/auto-paper-improvement-loop`,
`/paper-claim-audit`, `/citation-audit`.

**Action:** track all improvement-loop iterations in
`orbit-research/PAPER_IMPROVEMENT_LOG.md`. Each entry: round number, reviewer feedback,
fix applied, audit verdicts (`PAPER_CLAIM_AUDIT`, `CITATION_AUDIT`).

**ARIS unavailability handling** — for any ARIS slash invocation in this stage:

```text
For each ARIS skill call (/paper-writing, /paper-plan, /paper-figure, /paper-write,
/paper-compile, /auto-paper-improvement-loop, /paper-claim-audit, /citation-audit):
  - Try slash invocation.
  - If skill not registered: print
        "ARIS skill <name> unavailable. Stage 24 degraded: <fallback action or
         HUMAN_DECISION_REQUIRED>."
    Continue gracefully.
  - If the missing skill was load-bearing for a hard gate (e.g. /paper-claim-audit for
    submission readiness): escalate to HUMAN_DECISION_REQUIRED.
```

### Stage 25: Human Decision / Next Loop

**Action:**

1. Write `orbit-research/HUMAN_DECISION_NOTE.md` ending with one of
   `PROCEED | NARROW | REDESIGN | RE-READ | CHANGE BENCHMARK | STOP | HUMAN_DECISION_REQUIRED`.
2. **Gate G19:** required at all "high-risk transitions" (scale-up, paper writing, public
   release).

## Innovation Loop Dispatch

Stages 8, 9, 10, 18.5 are **innovation loops**. Different from the rest of the pipeline:

- `CODEX_INNOVATION_MODE = COLLABORATIVE` for these stages. Use prompt template in
  `innovation-loops.md` §7.1 — no veto, only adds candidates / blind spots / alternatives.
- Convergence is **forbidden** inside the loop. Output keeps all candidates visible.
- Codex switches back to `ADVERSARIAL` at Stages 11, 14, 15, 17, 21, 23.

Mode-switching rule (orchestrator-side):

```
IF current_stage IN {8, 9, 10, 18.5}:
    codex_mode = COLLABORATIVE
    use prompt template innovation-loops.md §7.1
ELSE IF current_stage IN {11, 14, 15, 17, 21, 23}:
    codex_mode = ADVERSARIAL
    use semantic-code-audit.md template (audit gates) or research-harness-prompts.md
    template (debate gates)
ELSE:
    codex is not invoked at this stage
```

## Hard Gates Enforcement (G0–G19)

The orchestrator enforces every gate at the point the next stage would otherwise begin.
Each gate parses verdict lines, not file presence. Inline accept-either logic reads v1.3
artifact name first; falls back to v1.0 alias.

```text
G0  Mode & Risk Routing required. Auto-stub for low-risk single-stage; block at high-risk
    transitions when mode/risk cannot be inferred.

G1  Method commitment, official experiment planning, or GPU run requires
    PROBLEM_SELECTION.md. Mechanism brainstorming (Stages 8/9/10) allowed in
    EXPLORATION/INNOVATION before final selection if outputs marked as candidates and
    assumptions go to ASSUMPTION_LEDGER.md.

G2  Downstream "is/will/always" claims must trace to ASSUMPTION_LEDGER.md row, OR demote
    to "assume/hypothesise", OR cite external evidence.

G3  Stage 11+ (commitment) requires ABSTRACT_TASK_MECHANISM.md. Stage 8/9/10 mechanism
    invention may run without it in EXPLORATION/INNOVATION mode if candidates marked as
    such and assumptions go to ledger.

G4  ARTIFACT_AUDIT.md only required after the data/env/benchmark/evaluator artifact
    actually exists. Do NOT force the audit before then.

G5  "outperforms / beats / improves over" claims require BASELINE_CEILING.md, unless mode
    = EXPLORATION AND no paper claim is being made.

G6  Method commitment (Stage 11+) requires ≥1 of {MECHANISM_IDEATION, ANALOGY_TRANSFER,
    ALGORITHM_TOURNAMENT}. Exception: explicit single-method confirmatory mode.

G7  Result feeding paper claims requires CONTROL_DESIGN.md. No exception.

G8  Diagnostic/confirmatory experiments require NULL_RESULT_CONTRACT.md, unless run is
    explicitly marked "exploratory probe" (no paper claim allowed).

G9  Official (full-system) run with a new composed method requires
    COMPONENT_BUNDLE_LADDER.md (a single justified rung is acceptable). Exception:
    baseline reproduction or single-component runs with no new composed mechanism.

G10 Scale-up to official experiments requires ALGORITHMIC_FORMALIZATION.md, unless mode
    = EXPLORATION AND no scale-up requested.

G11 PLAN_CODE_AUDIT.md verdict = CRITICAL_MISMATCH blocks scale-up unconditionally. Loop
    fix → re-audit until MATCHES_PLAN or scoped PARTIAL_MISMATCH. ERROR: advisory at
    diagnostic stage; blocks at scale-up pending human acknowledgement.

G12 If a tiny / diagnostic run failed in a regime that violated the mechanism's necessary
    preconditions, do NOT reject the mechanism — require diagnostic redesign to a regime
    where the mechanism could in principle manifest. Replaces v1.0 "tiny-run failure →
    kill idea."

G13 Test set isolation: experiments using test set anywhere in tuning/selection are blocked.
    No exception.

G14 NULL_RESULT_CONTRACT-triggered tie/failure cannot have positive framing in
    RESULT_INTERPRETATION/CLAIM_CONSTRUCTION. No exception.

G15 Scale-up in mode = COMMITMENT OR risk ≥ 4 requires HUMAN_DECISION_NOTE.md before
    SCALEUP_DECISION = PROCEED. No exception.

G16 Stage 24 (paper writing) requires CLAIM_CONSTRUCTION.md. No exception.

G17 Post-hoc result framings must be labelled "exploratory finding, not pre-planned
    hypothesis" in CLAIM_CONSTRUCTION.md and the paper. No exception.

G18 /paper-writing inline guard: refuse start if CLAIM_CONSTRUCTION.md absent. No exception.

G19 Scale-up (Stage 20), paper writing (Stage 24), and any public-release transition
    require HUMAN_DECISION_NOTE.md. No exception.
```

## Paper Writing Integration

Paper writing is **not** reimplemented. It is delegated to ARIS via Stage 24 (above):

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: $VENUE, assurance: submission
```

Before invoking, this orchestrator verifies the v1.3 hard preconditions (G16, G18, G19):

- `orbit-research/CLAIM_CONSTRUCTION.md` (written by `/result-to-claim` at Stage 21)
- `orbit-research/HUMAN_DECISION_NOTE.md` (written by `/result-to-claim` and Stage 25 of
  this pipeline)
- `orbit-research/RED_TEAM_REVIEW.md` (written by `/auto-review-loop` at Stage 23)
- `orbit-research/NEGATIVE_RESULT_STRATEGY.md` if `result-to-claim` returned `partial` or `no`

These match the hard preconditions in `skills/paper-writing/SKILL.md`. If any are missing,
do not invoke `/paper-writing`; route the user back to the producing skill.

During paper writing, the ARIS chain runs (do not duplicate):

- `/paper-plan`
- `/paper-figure`
- `/figure-spec` or `/paper-illustration`
- `/paper-write`
- `/paper-compile`
- `/auto-paper-improvement-loop`
- `/paper-claim-audit`
- `/citation-audit`

Track the iteration log in `orbit-research/PAPER_IMPROVEMENT_LOG.md`.

## Final Rule

```text
Move fast in exploration. Slow down before commitment.
Bold ideas are allowed. Undiagnosable experiments are not.
Failure is allowed. Failure without interpretation is not.
Runnable code is not success. Code that faithfully implements the v1.3 contract is.
Innovation loops produce candidates. Commitment gates pick what runs.
Reuse ARIS execution skills. Do not reimplement them.
Preserve human judgment at high-risk irreversible transitions.
```
