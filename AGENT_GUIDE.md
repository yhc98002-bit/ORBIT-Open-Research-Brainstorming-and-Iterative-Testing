# BRIS Agent Guide

> **For AI agents reading this repo.** If you are a human, see [README.md](README.md).

BRIS (Better Research in Sleep) is a research harness built on the original ARIS skills.
It keeps ARIS's mature infrastructure — literature search, idea discovery, experiment
deployment, auto review, paper writing, claim and citation audits — but the control flow is
the diagnostic 0A–15 pipeline defined in
`skills/shared-references/research-agent-pipeline.md`.

The job of a BRIS agent is not "run experiments and write a paper". It is to behave like a
careful junior research scientist: define the problem, audit the data, measure baseline
ceilings, build a diagnosable experiment, audit the code against the plan, and only then
turn results into scoped claims.

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

## The BRIS Pipeline

```text
0A. Seed Framing
1.  Question-driven Literature Map
0B. Problem Selection
2.  Task Ontology / Data Audit
3.  Baseline Ceiling / Headroom Audit
4.  Hypothesis-Mechanism-Benchmark-Control Matrix
5.  Null-result Contract
6.  Progressive Component Ladder
7.  Minimal Diagnostic Experiment Design
7.5 Plan-Code Consistency Audit
8.  Tiny Run / Sanity Run
8.5 Tiny Run Audit
9.  Result Interpretation Loop
10. Re-read Literature After Early Results
11. Scale-up Experiment
12. Result-to-Claim Construction
13. Tie / Negative Result Strategy
14. Reviewer Red-team
15. Human Decision / Next Research Loop
```

Read `skills/shared-references/research-agent-pipeline.md` for stage responsibilities and
hard gates. Read `skills/shared-references/research-harness-prompts.md` for the canonical
per-stage prompt. Read `skills/shared-references/semantic-code-audit.md` before any
plan-code review.

## Hard Gates (always-on)

These are enforced inside the skill bodies; they are not conditional on being called by
`/research-pipeline`. A user invoking a skill standalone gets the same gates.

Each gate parses the artifact's verdict line, not just file presence.

- No method design before `bris-research/TASK_ONTOLOGY.md`.
- No proposed method run before `bris-research/BASELINE_CEILING.md`.
- No experiment without an interpretable `bris-research/NULL_RESULT_CONTRACT.md`.
- No full system before `bris-research/COMPONENT_LADDER.md`.
- No GPU scale-up unless `bris-research/PLAN_CODE_AUDIT.md` verdict line is `MATCHES_PLAN`
  or a scoped `PARTIAL_MISMATCH` whose missing pieces are irrelevant to this wave.
  `CRITICAL_MISMATCH` blocks unconditionally. `ERROR` (Codex unavailable, audit could not
  complete) is advisory at tiny / sanity run (proceed, surface reason) and blocks at
  scale-up pending explicit human acknowledgement.
- No full run unless `bris-research/TINY_RUN_AUDIT.md` verdict line is `PASS`.
  `FIX_BEFORE_GPU` and `REDESIGN_EXPERIMENT` block — fix code or redesign and rerun
  the tiny run before launching the full sweep.
- After every experiment, update `bris-research/RESULT_INTERPRETATION.md`.
- After tie or failure, write `bris-research/NEGATIVE_RESULT_STRATEGY.md`.
- No paper claim before `bris-research/CLAIM_CONSTRUCTION.md`.
- No "submission-ready" label until reviewer red-team
  (`bris-research/RED_TEAM_REVIEW.md`), `bris-research/HUMAN_DECISION_NOTE.md`, and the
  paper-writing audit verifier (`tools/verify_paper_audits.sh`) are all green.

## Workflow Index

### Full Pipeline

```
/research-pipeline "direction" → 0A → 1 → 0B → 2 → 3 → 4–7 → 7.5 → 8–8.5 → 9–11 → 12–13 → 14 → 15
```

`/research-pipeline` initializes `bris-research/` and walks every stage. It calls into
ARIS-derived sub-skills, each of which enforces its own BRIS gate even when invoked
directly.

### Individual Workflows

| Workflow | Invoke | Input | Output | When to use |
|----------|--------|-------|--------|-------------|
| Stages 0A–0B: Discovery | `/idea-discovery "direction"` | research direction | SEED_FRAMING.md, LITERATURE_MAP.md, PROBLEM_SELECTION.md, IDEA_REPORT.md | Frame problem and pick candidate |
| Stages 2–7: Plan | `/research-refine` then `/experiment-plan` | problem + rough method | TASK_ONTOLOGY, BASELINE_CEILING, CONTROL_DESIGN, NULL_RESULT_CONTRACT, COMPONENT_LADDER, DIAGNOSTIC_EXPERIMENT_PLAN, FINAL_PROPOSAL.md, EXPERIMENT_PLAN.md | Turn idea into a diagnosable experiment design |
| Stage 7.5: Plan-Code Audit | `/experiment-bridge` | EXPERIMENT_PLAN.md | running code + PLAN_CODE_AUDIT.md (verdict line) | Implement and verify code matches plan |
| Stages 8–8.5: Tiny + Audit | `/run-experiment "tiny diagnostic"` | sanity command | TINY_RUN_REPORT.md, TINY_RUN_AUDIT.md (verdict line) | Tiny run before scaling |
| Stage 11: Scale | `/experiment-queue` or `/run-experiment` | manifest | LOGS/, EXPERIMENT_TRACKER.md | Full sweep after tiny run passes |
| Stages 9, 12–13: Interpret + Claim | `/analyze-results` then `/result-to-claim` | logs + results | RESULT_INTERPRETATION.md, CLAIM_CONSTRUCTION.md, NEGATIVE_RESULT_STRATEGY.md, HUMAN_DECISION_NOTE.md | Decide what claim the data supports |
| Stage 14: Red-team | `/auto-review-loop` | project state | RED_TEAM_REVIEW.md, AUTO_REVIEW.md | Final adversarial review before paper |
| Paper writing | `/paper-writing "NARRATIVE_REPORT.md"` | narrative report | paper/, PAPER_CLAIM_AUDIT, CITATION_AUDIT | Draft paper after CLAIM_CONSTRUCTION + RED_TEAM_REVIEW exist |
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

## BRIS Artifact Contracts

Skills communicate through plain-text files under `bris-research/` (BRIS-specific) and
`refine-logs/` / `paper/` / `review-stage/` (inherited from ARIS).

| Artifact | Created by | Consumed by |
|----------|-----------|-------------|
| `bris-research/SEED_FRAMING.md` | research-pipeline / research-lit | idea-discovery, research-refine |
| `bris-research/LITERATURE_MAP.md` | research-lit, research-pipeline | idea-discovery, research-refine |
| `bris-research/PROBLEM_SELECTION.md` | idea-discovery, research-pipeline | research-refine, experiment-plan |
| `bris-research/TASK_ONTOLOGY.md` | research-refine, experiment-plan | experiment-bridge, run-experiment |
| `bris-research/BASELINE_CEILING.md` | research-refine, experiment-plan | experiment-bridge, result-to-claim |
| `bris-research/CONTROL_DESIGN.md` | research-refine, experiment-plan | experiment-bridge, experiment-queue |
| `bris-research/NULL_RESULT_CONTRACT.md` | research-refine, experiment-plan | experiment-bridge, run-experiment |
| `bris-research/COMPONENT_LADDER.md` | research-refine, experiment-plan | experiment-bridge, run-experiment |
| `bris-research/DIAGNOSTIC_EXPERIMENT_PLAN.md` | experiment-plan | experiment-bridge, run-experiment |
| `bris-research/PLAN_CODE_AUDIT.md` | experiment-bridge (always) | run-experiment, experiment-queue |
| `bris-research/TINY_RUN_REPORT.md` | run-experiment | tiny-run audit |
| `bris-research/TINY_RUN_AUDIT.md` | run-experiment / monitor-experiment | experiment-queue |
| `bris-research/RESULT_INTERPRETATION.md` | analyze-results, monitor-experiment | result-to-claim |
| `bris-research/SCALEUP_DECISION.md` | research-pipeline | experiment-queue |
| `bris-research/CLAIM_CONSTRUCTION.md` | result-to-claim | paper-plan, paper-write, paper-writing |
| `bris-research/NEGATIVE_RESULT_STRATEGY.md` | result-to-claim | paper-plan, paper-write |
| `bris-research/RED_TEAM_REVIEW.md` | auto-review-loop | paper-writing |
| `bris-research/HUMAN_DECISION_NOTE.md` | result-to-claim, research-pipeline | paper-writing |
| `EXPERIMENT_AUDIT.{md,json}` | experiment-audit | result-to-claim |
| `PAPER_CLAIM_AUDIT.{md,json}` | paper-claim-audit | paper-writing Phase 5.5 gate |
| `CITATION_AUDIT.{md,json}` | citation-audit | paper-writing Phase 5.8 gate |
| `research-wiki/` | research-wiki | idea-creator, research-lit, result-to-claim |

Every audit verdict (`PLAN_CODE_AUDIT`, `TINY_RUN_AUDIT`, `result-to-claim` output) is a
single canonical token on its own line — `MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`,
`PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT`, or `yes | partial | no`. Downstream skills
parse the verdict, not the artifact's presence.

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

The pipeline runs adversarial debate at:

```
Problem Selection · Literature Map · Task Ontology · Baseline Ceiling ·
Hypothesis-Mechanism-Benchmark-Control · Null-result Contract ·
Component Ladder · Algorithm Design · Plan-Code Audit · Tiny Run Audit ·
Result-to-Claim · Reviewer Red-team
```

Protocol:

```
Claude: propose → Codex: critique → Claude: revise → Codex: final objections →
Claude: consensus decision → Human: approve / redirect
```

Cap at two rounds. End with one of `CONSENSUS | DISAGREEMENT | HUMAN_DECISION_REQUIRED`.

## Shared References

Read these before invoking review-related skills:

- `skills/shared-references/research-agent-pipeline.md` — 0A–15 stage map and hard gates
- `skills/shared-references/research-harness-prompts.md` — per-stage canonical prompt
- `skills/shared-references/semantic-code-audit.md` — Codex semantic audit protocol
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
