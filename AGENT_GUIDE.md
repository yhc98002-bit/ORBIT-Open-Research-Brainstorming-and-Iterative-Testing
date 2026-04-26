# BRIS Agent Guide

> **For AI agents reading this repo.** If you are a human, see [README.md](README.md).

BRIS (Better Research in Sleep) v1.3 is a research-methodology routing harness built on
ARIS execution skills. It routes through 26 stages organised into four spines (Discovery /
Grounding / Innovation / Validation) by mode (EXPLORATION / INNOVATION / COMMITMENT) and
risk score (1–5). Canonical contracts live in
`skills/shared-references/research-agent-pipeline.md`.

The job of a BRIS agent is not "run experiments and write a paper". It is to behave like a
careful research scientist: classify the user's input shape, route through the minimum
stages needed, expand the candidate space during innovation (Codex collaborative), pin
down assumptions / abstract task / baseline ceiling during grounding, enforce verdict-line
gates at commitment, and only then turn results into scoped, evidence-bound claims.

## How to Invoke Skills

**Claude Code / Cursor / Trae:**
```
/skill-name "arguments" — key: value, key2: value2
```

**Codex CLI:**
```
/skill-name "arguments" — key: value
```

The argument separator is em-dash `—`, not single `-`.

## Common Parameters

```
— effort: lite | balanced | max | beast      # work intensity (default: balanced)
— human checkpoint: true | false             # pause for approval (default: false)
— AUTO_PROCEED: true | false                 # auto-continue at gates (default: true)
— assurance: draft | submission              # paper-writing audit gate level
— difficulty: medium | hard | nightmare      # reviewer adversarial level
— venue: ICLR | NeurIPS | ICML | ...         # target venue
— sources: web, zotero, deepxiv, ...         # literature sources
— gpu: local | remote | vast | modal         # GPU backend
— reviewer: codex | oracle-pro               # reviewer backend (default: codex)
```

Codex review reasoning is always `xhigh`. Codex sandbox mode is set in `~/.codex/config.toml`
as `sandbox_mode = "danger-full-access"`; it is not overridable per call.

## The BRIS v1.3 Pipeline

```text
Discovery   → 0   Mode & Risk Routing
              1   Seed Framing
              2   Question-driven Literature Map        (loop)
              2.5 Problem Reframing Loop
              3   Problem Taste / Selection

Grounding   → 4   Assumption Ledger
              5   Abstract Task / Mechanism Framing
              6   Artifact-triggered Audit              (only when artifact exists)
              7   Baseline Ceiling / Headroom Audit

Innovation  → 8   Mechanism Invention Loop              (Codex collaborative)
              9   Analogy / Cross-pollination Loop      (Codex collaborative)
              10  Algorithm Sketch Tournament           (Codex collaborative; adversarial on adjudication)
              18.5 Failure-to-Innovation Loop           (Codex collaborative)

Validation  → 11  Hypothesis-Mechanism-Benchmark-Control Matrix
              12  Null-result Contract
              13  Progressive Component / Minimal Mechanism Bundle
              14  Algorithmic Formalization
              15  Plan-Code Consistency Loop            (audit → fix → re-audit)
              16  Cheapest Valid Diagnostic
              17  Diagnostic Run Audit
              18  Result Interpretation Loop
              19  Re-read Literature Loop
              20  Scale-up Decision
              21  Result-to-Claim Construction
              22  Tie / Negative Result / Reframing Strategy
              23  Reviewer Red-team Loop                (review → fix → re-review)
              24  Paper Writing / Improvement Loop      (delegates to ARIS chain)
              25  Human Decision / Next Loop
```

Grounding (4–7) is *diagnostic support* for Innovation, not innovation itself. Innovation
loops produce candidates; commitment gates pick what runs.

Read `skills/shared-references/research-agent-pipeline.md` for stage responsibilities,
four-spine framing, mode & risk routing rules, and hard gates G0–G19. Read
`skills/shared-references/research-harness-prompts.md` for the canonical per-stage prompt.
Read `skills/shared-references/innovation-loops.md` before invoking Stages 8/9/10/18.5.
Read `skills/shared-references/semantic-code-audit.md` before any plan-code review (Stage
15) or diagnostic-run audit (Stage 17).

## Hard Gates (always-on, v1.3)

These are enforced inside the skill bodies; they are not conditional on being called by
`/research-pipeline`. A user invoking a skill standalone gets the same gates.

Each gate parses the artifact's verdict line, not just file presence. Producers emit v1.3
artifact names; consumers accept either v1.3 or v1.0 alias names (preferring v1.3).

- **G0** — Mode & Risk Routing required at high-risk transitions; auto-stub for low-risk.
- **G1** — Method commitment / official planning / GPU run requires `PROBLEM_SELECTION.md`.
  Stages 8/9/10 brainstorming allowed in EXPLORATION/INNOVATION with candidates marked.
- **G2** — Downstream "is/will/always" claims must trace to `ASSUMPTION_LEDGER.md` row, OR
  demote to "assume/hypothesise", OR cite external evidence.
- **G3** — Stage 11+ (commitment) requires `ABSTRACT_TASK_MECHANISM.md`.
- **G4** — `ARTIFACT_AUDIT.md` only required after the data/env/benchmark/evaluator artifact
  actually exists. Do NOT force the audit before then.
- **G5** — "outperforms / beats / improves over" claims require `BASELINE_CEILING.md`,
  unless mode = EXPLORATION AND no paper claim is being made.
- **G6** — Method commitment requires ≥1 of `MECHANISM_IDEATION` / `ANALOGY_TRANSFER` /
  `ALGORITHM_TOURNAMENT`. Exception: explicit single-method confirmatory mode.
- **G7** — Result feeding paper claims requires `CONTROL_DESIGN.md`. No exception.
- **G8** — Diagnostic / confirmatory experiments require `NULL_RESULT_CONTRACT.md`, unless
  run is explicitly marked "exploratory probe" (no paper claim allowed).
- **G9** — Official (full-system) run with new composed method requires
  `COMPONENT_BUNDLE_LADDER.md` (single justified rung acceptable). Exception: baseline
  reproduction or single-component runs with no new composed mechanism.
- **G10** — Scale-up to official experiments requires `ALGORITHMIC_FORMALIZATION.md`,
  unless mode = EXPLORATION AND no scale-up requested.
- **G11** — `PLAN_CODE_AUDIT.md` verdict `CRITICAL_MISMATCH` blocks scale-up unconditionally.
  Loop fix → re-audit until `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH`. `ERROR` advisory
  at diagnostic stage, blocks at scale-up pending human acknowledgement.
- **G12** — Diagnostic run failure that violated mechanism preconditions does NOT kill the
  mechanism; require diagnostic redesign to a regime where the mechanism could manifest.
- **G13** — Test set isolation: no tuning / selection on test set. No exception.
- **G14** — `NULL_RESULT_CONTRACT`-triggered tie/failure cannot have positive framing in
  `RESULT_INTERPRETATION` / `CLAIM_CONSTRUCTION`. No exception.
- **G15** — Scale-up in mode = COMMITMENT OR risk ≥ 4 requires `HUMAN_DECISION_NOTE.md`
  before `SCALEUP_DECISION = PROCEED`. No exception.
- **G16** — Stage 24 (paper writing) requires `CLAIM_CONSTRUCTION.md`. No exception.
- **G17** — Post-hoc reframings must be labelled "exploratory finding, not pre-planned
  hypothesis" in `CLAIM_CONSTRUCTION.md` and the paper. No exception.
- **G18** — `/paper-writing` inline guard: refuse without `CLAIM_CONSTRUCTION.md`. No exception.
- **G19** — Scale-up (Stage 20), paper writing (Stage 24), and any public-release transition
  require `HUMAN_DECISION_NOTE.md`. No exception.

Full canonical text in `skills/shared-references/research-agent-pipeline.md` §6. v1.0
gates "tiny run before scale-up always" and "data audit before any other stage" are
intentionally **removed** in v1.3, replaced by G11/G12 (regime-aware) and G4 (artifact-triggered).

## Workflow Index

### Full Pipeline

```
/research-pipeline "input" → Stage 0 routing → minimum stages needed for the inferred mode/risk
```

`/research-pipeline` first classifies the user's input shape into one of 7 routing
categories (broad area / concrete idea / concrete data / new method / official experiments
/ running / results-failed) and writes `MODE_ROUTING.md`. It then routes through only the
stages relevant to that input shape — it does **not** force a linear walk through all 26
stages. Sub-skills enforce their own v1.3 gates even when invoked directly.

### 7 routing categories (Stage 0 input classification)

| Input shape | Suggested mode | Initial risk | First stages |
|---|---|---|---|
| Broad area | EXPLORATION | 1–2 | 1 → 2 → 2.5 → 3 |
| Concrete idea, no artifact | INNOVATION | 2–3 | 4 → 5 → 7 → 8/9/10 |
| Concrete data / env / sim / reward in hand | INNOVATION/COMMITMENT | 2–4 | 6 → 7 → 11+ |
| Designing new method | INNOVATION | 2–3 | 4 → 5 → 8 → 9 → 10 |
| Implementing official experiments | COMMITMENT | 4 | 11 → 12 → 13 → 14 → 15 → 16 |
| Running experiments | COMMITMENT | 3–4 | 16 → 17 → 18 |
| Results failed / surprised | INNOVATION | 2–3 | 18 → 18.5 → 19 → (back to 8 or 11) |

### Individual Workflows

| Workflow | Invoke | Input | Output | When to use |
|----------|--------|-------|--------|-------------|
| Stages 1–3: Discovery | `/idea-discovery "direction"` | research direction | SEED_FRAMING.md, LITERATURE_MAP.md, PROBLEM_REFRAMING.md, PROBLEM_SELECTION.md | Frame problem and pick candidate |
| Stages 4–7 + 8–10: Grounding + Innovation | `/research-refine` then `/experiment-plan` | problem + rough method | ASSUMPTION_LEDGER, ABSTRACT_TASK_MECHANISM, BASELINE_CEILING, MECHANISM_IDEATION, ANALOGY_TRANSFER, ALGORITHM_TOURNAMENT, FINAL_PROPOSAL.md, EXPERIMENT_PLAN.md | Turn idea into diagnosable design with innovation candidates |
| Stages 11–15: Validation prerequisites | continued in `/experiment-plan` + `/experiment-bridge` | proposal + plan | CONTROL_DESIGN, NULL_RESULT_CONTRACT, COMPONENT_BUNDLE_LADDER, ALGORITHMIC_FORMALIZATION, PLAN_CODE_AUDIT.md (verdict line) | Implement and verify code matches v1.3 contract |
| Stages 16–17: Diagnostic + Audit | `/run-experiment "diagnostic command"` | diagnostic command | DIAGNOSTIC_EXPERIMENT_PLAN, DIAGNOSTIC_RUN_REPORT, DIAGNOSTIC_RUN_AUDIT.md (verdict line) | Cheapest valid diagnostic before scale-up |
| Stage 20: Scale | `/experiment-queue` or `/run-experiment` | manifest | LOGS/, EXPERIMENT_TRACKER.md, SCALEUP_DECISION.md | Full sweep after diagnostic passes + HUMAN_DECISION_NOTE |
| Stages 18, 21–22: Interpret + Claim | `/analyze-results` then `/result-to-claim` | logs + results | RESULT_INTERPRETATION.md, CLAIM_CONSTRUCTION.md, NEGATIVE_RESULT_STRATEGY.md, HUMAN_DECISION_NOTE.md | Decide what claim the data supports |
| Stage 23: Red-team Loop | `/auto-review-loop` | project state | RED_TEAM_REVIEW.md, AUTO_REVIEW.md | Iterative adversarial review before paper |
| Stage 24: Paper writing | `/paper-writing "NARRATIVE_REPORT.md"` | narrative report | paper/, PAPER_IMPROVEMENT_LOG.md, PAPER_CLAIM_AUDIT, CITATION_AUDIT | Draft paper after CLAIM_CONSTRUCTION + RED_TEAM_REVIEW exist (G16, G18) |
| Rebuttal (W4) | `/rebuttal "paper/ + reviews"` | paper + reviews | PASTE_READY.txt | Reviews received |

### Standalone Skills

| Skill | What it does |
|-------|-------------|
| `/alphaxiv "arxiv-id"` | LLM-optimized single-paper summary |
| `/research-lit "topic"` | Question-driven literature map (Stage 1) |
| `/idea-creator "direction"` | Brainstorm + rank ideas |
| `/novelty-check "idea"` | Verify against existing work |
| `/research-review "draft"` | Codex GPT-5.5 xhigh deep critique |
| `/experiment-audit` | Cross-model integrity audit of eval code |
| `/result-to-claim` | Verdict on whether results support claims |
| `/paper-claim-audit "paper/"` | Numerical claim audit |
| `/citation-audit "paper/"` | Bibliography audit |
| `/overleaf-sync setup\|pull\|push\|status` | Two-way Overleaf sync |
| `/paper-plan "topic"` | Outline + claims matrix |
| `/paper-figure "plan"` | Plots from data |
| `/paper-write "plan"` | Section-by-section LaTeX |
| `/paper-compile "paper/"` | Multi-pass PDF build |
| `/research-wiki init` | Persistent project knowledge base |
| `/meta-optimize` | Analyze usage, propose skill edits |
| `/analyze-results` | Statistics + comparison |
| `/ablation-planner` | Reviewer-perspective ablations |

## BRIS v1.3 Artifact Contracts

Skills communicate through plain-text files under `bris-research/` (BRIS-specific) and
`refine-logs/` / `paper/` / `review-stage/` (inherited from ARIS). v1.3 producers emit
v1.3 names; consumers accept the v1.0 alias for one major version (preferring v1.3 if
both exist).

| v1.3 Artifact | v1.0 alias | Created by | Consumed by |
|---|---|---|---|
| `bris-research/MODE_ROUTING.md` | — | research-pipeline (Stage 0) | all downstream stages |
| `bris-research/SEED_FRAMING.md` | (was 0A) | research-pipeline / research-lit | research-refine, experiment-plan |
| `bris-research/LITERATURE_MAP.md` | — | research-lit, research-pipeline | idea-discovery, research-refine, Stage 19 re-read |
| `bris-research/PROBLEM_REFRAMING.md` | — | research-pipeline (Stage 2.5) | research-pipeline (Stage 3) |
| `bris-research/PROBLEM_SELECTION.md` | — | idea-discovery, research-pipeline | research-refine, experiment-plan |
| `bris-research/ASSUMPTION_LEDGER.md` | — | research-pipeline (Stage 4) | downstream claim wording (G2), semantic-code-audit |
| `bris-research/ABSTRACT_TASK_MECHANISM.md` | (part of TASK_ONTOLOGY split) | research-pipeline (Stage 5) | innovation loops, experiment-bridge, semantic-code-audit |
| `bris-research/ARTIFACT_AUDIT.md` | (was TASK_ONTOLOGY's data block) | research-pipeline (Stage 6) | experiment-bridge, run-experiment |
| `bris-research/BASELINE_CEILING.md` | — | research-refine, experiment-plan | experiment-bridge, result-to-claim |
| `bris-research/MECHANISM_IDEATION.md` | — | research-pipeline (Stage 8, Codex collaborative) | Stages 9, 10, 11, 18.5 |
| `bris-research/ANALOGY_TRANSFER.md` | — | research-pipeline (Stage 9) | Stages 10, 11 |
| `bris-research/ALGORITHM_TOURNAMENT.md` | — | research-pipeline (Stage 10) | Stages 11, 14, 18.5 |
| `bris-research/CONTROL_DESIGN.md` | — | research-refine, experiment-plan | experiment-bridge, experiment-queue |
| `bris-research/NULL_RESULT_CONTRACT.md` | — | research-refine, experiment-plan | experiment-bridge, run-experiment |
| `bris-research/COMPONENT_BUNDLE_LADDER.md` | `COMPONENT_LADDER.md` | research-refine, experiment-plan | experiment-bridge, run-experiment |
| `bris-research/ALGORITHMIC_FORMALIZATION.md` | — | research-pipeline (Stage 14) | semantic-code-audit, experiment-bridge |
| `bris-research/PLAN_CODE_AUDIT.md` (verdict line) | — | experiment-bridge (always) | run-experiment, experiment-queue |
| `bris-research/DIAGNOSTIC_EXPERIMENT_PLAN.md` | `TINY_RUN_PLAN.md` | experiment-plan | experiment-bridge, run-experiment |
| `bris-research/DIAGNOSTIC_RUN_REPORT.md` | `TINY_RUN_REPORT.md` | run-experiment | diagnostic-run audit |
| `bris-research/DIAGNOSTIC_RUN_AUDIT.md` (verdict line) | `TINY_RUN_AUDIT.md` | run-experiment / monitor-experiment | experiment-queue, research-pipeline |
| `bris-research/RESULT_INTERPRETATION.md` | — | analyze-results, monitor-experiment | result-to-claim, Stage 18.5 |
| `bris-research/FAILURE_TO_INNOVATION.md` | — | research-pipeline (Stage 18.5) | Stages 19, 20 |
| `bris-research/LITERATURE_REREAD_NOTE.md` | — | research-lit (Stage 19 loop) | research-pipeline |
| `bris-research/SCALEUP_DECISION.md` (verdict line) | — | research-pipeline | experiment-queue |
| `bris-research/CLAIM_CONSTRUCTION.md` | — | result-to-claim | paper-plan, paper-write, paper-writing (G16, G18) |
| `bris-research/NEGATIVE_RESULT_STRATEGY.md` | — | result-to-claim | paper-plan, paper-write |
| `bris-research/RED_TEAM_REVIEW.md` | — | auto-review-loop | paper-writing |
| `bris-research/PAPER_IMPROVEMENT_LOG.md` | — | paper-writing chain | (audit log) |
| `bris-research/HUMAN_DECISION_NOTE.md` (verdict line) | — | result-to-claim, research-pipeline | paper-writing, scale-up gate (G15, G19) |
| `EXPERIMENT_AUDIT.{md,json}` | — | experiment-audit | result-to-claim |
| `PAPER_CLAIM_AUDIT.{md,json}` | — | paper-claim-audit | paper-writing Phase 5.5 gate |
| `CITATION_AUDIT.{md,json}` | — | citation-audit | paper-writing Phase 5.8 gate |
| `research-wiki/` | — | research-wiki | idea-creator, research-lit, result-to-claim |

Every audit verdict (`PLAN_CODE_AUDIT`, `DIAGNOSTIC_RUN_AUDIT`, `SCALEUP_DECISION`,
`HUMAN_DECISION_NOTE`, `result-to-claim` output) is a single canonical token on its own
line:

- `PLAN_CODE_AUDIT.md`: `MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`
- `DIAGNOSTIC_RUN_AUDIT.md`: `PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT`
- `SCALEUP_DECISION.md`: `PROCEED | HOLD | REDESIGN | HUMAN_DECISION_REQUIRED`
- `HUMAN_DECISION_NOTE.md`: `PROCEED | NARROW | REDESIGN | RE-READ | CHANGE BENCHMARK | STOP | HUMAN_DECISION_REQUIRED`
- `result-to-claim` output: `yes | partial | no`

Downstream skills parse the verdict, not the artifact's presence.

`TASK_ONTOLOGY.md` (v1.0) has no alias — its content maps to four v1.3 artifacts (Stages
0/1/4/5) and must be split manually. See `skills/shared-references/research-agent-pipeline.md`
migration appendix.

## Cross-Model Protocol

- **Executor** (Claude/Codex): writes code, runs experiments, drafts papers.
- **Reviewer** (Codex GPT-5.5 xhigh, optionally GPT-5.5 Pro via Oracle): critiques,
  scores, demands revisions.
- Executor and reviewer must be different model families.
- Reviewer independence: pass file paths only, never executor summaries or interpretations.
  See `skills/shared-references/reviewer-independence.md`.
- Experiment integrity: the executor must NOT judge its own eval code — `/experiment-audit`
  reads the eval source directly.

## Claude vs Codex Debate Nodes

In v1.3, Codex switches mode based on stage. Innovation stages use **collaborative**
mode (no veto, only adds candidates — see `skills/shared-references/innovation-loops.md`
§7). Commitment / validation stages use **adversarial** mode.

**Innovation nodes (Codex collaborative — no debate, additive contribution):**

```
Stage 2.5  Problem Reframing Loop
Stage 8    Mechanism Invention Loop
Stage 9    Analogy / Cross-pollination Loop
Stage 10   Algorithm Sketch Tournament  (collaborative on sketch quality;
                                         adversarial only on tournament adjudication)
Stage 18.5 Failure-to-Innovation Loop
```

**Adversarial debate nodes (Codex challenges; Claude defends or revises):**

```
Stage 3   Problem Taste / Selection
Stage 6   Artifact-triggered Data / Environment / Benchmark Audit
Stage 7   Baseline Ceiling / Headroom Audit
Stage 11  Hypothesis-Mechanism-Benchmark-Control Matrix
Stage 12  Null-result Contract
Stage 13  Progressive Component / Minimal Mechanism Bundle
Stage 14  Algorithmic Formalization
Stage 15  Plan-Code Consistency Loop
Stage 17  Diagnostic Run Audit / Cheapest Valid Diagnostic
Stage 21  Result-to-Claim Construction
Stage 23  Reviewer Red-team Loop
```

Protocol (adversarial mode only):

```
Claude: propose → Codex: critique → Claude: revise → Codex: final objections →
Claude: consensus decision → Human: approve / redirect
```

Cap at two rounds. End with one of `CONSENSUS | DISAGREEMENT | HUMAN_DECISION_REQUIRED`.

Innovation mode follows a different protocol (see `innovation-loops.md` §7.1):
Codex appends candidates / blind spots / alternative framings to Claude's output. No
veto. Convergence is gated to Stage 11 (HMBC), Stage 14 (Formalization), and Stage 15
(Plan-Code Audit) — never inside an innovation loop.

## Shared References

Read these before invoking review-related skills:

- `skills/shared-references/research-agent-pipeline.md` — v1.3 canonical 0–25 stage map, four-spine framing, mode & risk routing rules, 19 hard gates G0–G19, v1.0 → v1.3 migration appendix
- `skills/shared-references/research-harness-prompts.md` — per-stage canonical prompt (v1.3 stages 0–25)
- `skills/shared-references/innovation-loops.md` — Stages 8/9/10/18.5 procedures + Collaborative Claude-Codex Innovation Mode
- `skills/shared-references/semantic-code-audit.md` — Stage 15 Codex plan-code audit + Stage 17 diagnostic-run audit (v1.3 contract artifact set)
- `skills/shared-references/reviewer-independence.md` — cross-model review rules
- `skills/shared-references/reviewer-routing.md` — Codex / Oracle routing
- `skills/shared-references/experiment-integrity.md` — prohibited fraud patterns
- `skills/shared-references/effort-contract.md` — effort level specifications
- `skills/shared-references/citation-discipline.md` — citation rules
- `skills/shared-references/writing-principles.md` — writing standards
- `skills/shared-references/venue-checklists.md` — venue formatting
- `skills/shared-references/assurance-contract.md` — paper-writing audit gate schema

## Research Wiki (Optional)

If `research-wiki/` exists in the project:

- `/research-lit` auto-ingests discovered papers
- `/idea-creator` reads wiki before ideation, writes ideas back after
- `/result-to-claim` updates claim status
- Failed ideas become anti-repetition memory

Initialize with `/research-wiki init`.

## Effort Levels

| Level | Tokens | What changes |
|-------|:------:|-------------|
| `lite` | 0.4× | Fewer papers, ideas, rounds |
| `balanced` | 1× | Default |
| `max` | 2.5× | More papers, deeper review |
| `beast` | 5–8× | Every knob to maximum |

Codex reasoning is always `xhigh` regardless of effort.

## Source of Truth

- Each skill's behavior: read its `skills/<name>/SKILL.md`.
- BRIS-wide rules: read `skills/shared-references/*.md`.
- This guide is a routing index, not the specification.
