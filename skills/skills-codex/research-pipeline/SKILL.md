---
name: "research-pipeline"
description: "Codex-CLI mirror of ORBIT v1.3 research-methodology routing harness. Routes by mode (EXPLORATION/INNOVATION/COMMITMENT) and risk (1-5) through 26 stages organised into four spines (Discovery/Grounding/Innovation/Validation). Innovation loops use Codex collaborative mode; commitment gates use Codex adversarial mode. Reuses ARIS execution skills. Use for 全流程/full pipeline/end-to-end research/ORBIT/ORBIT v1.3."
---

# ORBIT v1.3 Research Pipeline (Codex CLI dispatch mirror)

This is the Codex CLI dispatch mirror of `skills/research-pipeline/SKILL.md`. The two
variants share the same v1.3 stage skeleton so behaviour is consistent across CLIs. The
canonical contracts (stage definitions, harness prompts, gate rules, audit prompts) live
in `skills/shared-references/` — read those first.

End-to-end research workflow for: **$ARGUMENTS**

## Load First

- `../shared-references/research-agent-pipeline.md` — v1.3 canonical stage map, hard gates G0–G19
- `../shared-references/research-harness-prompts.md` — per-stage canonical prompt
- `../shared-references/innovation-loops.md` — Stages 8/9/10/18.5 procedures + Codex collaborative mode
- `../shared-references/semantic-code-audit.md` — Stage 15 plan-code audit + Stage 17 diagnostic-run audit
- `../shared-references/reviewer-independence.md`
- `../shared-references/reviewer-routing.md`

## Constants

- **OUTPUT_ROOT = `orbit-research/`** — v1.3 artifacts.
- **CLAUDE_EFFORT = `max`** — default planning/writing depth for the convergence pipeline.
- **CODEX_REVIEW_MODEL = `gpt-5.5`** — default Codex reviewer.
- **CODEX_REVIEW_EFFORT = `xhigh`** — mandatory for review gates.
- **CODEX_SANDBOX_MODE = `danger-full-access`** — set globally in `~/.codex/config.toml`.
- **CODEX_INNOVATION_MODE** — `COLLABORATIVE` at Stages 8, 9, 10, 18.5; `ADVERSARIAL` everywhere else.
- **MAX_DEBATE_ROUNDS = 2**
- **AUTO_PROCEED = false** for irreversible actions (GPU scale-up, paper, stop).
- **AUTO_WRITE = false** — if true, run `/paper-writing` after CLAIM_CONSTRUCTION + RED_TEAM_REVIEW gates pass.
- **VENUE = `ICLR`**.
- **HUMAN_CHECKPOINT = false** — if true, pause at major spine boundaries.

## Stage Map (v1.3 — same as Claude variant)

```text
Stage 0     Mode & Risk Routing
Stage 1     Seed Framing
Stage 2     Question-driven Literature Map                    (loop)
Stage 2.5   Problem Reframing Loop
Stage 3     Problem Taste / Problem Selection
Stage 4     Assumption Ledger
Stage 5     Abstract Task / Mechanism Framing
Stage 6     Artifact-triggered Data / Env / Benchmark Audit
Stage 7     Baseline Ceiling / Headroom Audit
Stage 8     Mechanism Invention Loop                          (Codex COLLABORATIVE)
Stage 9     Analogy / Cross-pollination Loop                  (Codex COLLABORATIVE)
Stage 10    Algorithm Sketch Tournament                       (Codex COLLABORATIVE on sketch / ADVERSARIAL on adjudication)
Stage 11    Hypothesis-Mechanism-Benchmark-Control Matrix
Stage 12    Null-result Contract
Stage 13    Progressive Component / Minimal Mechanism Bundle
Stage 14    Algorithmic Formalization
Stage 15    Plan-Code Consistency Loop                        (audit → fix → re-audit)
Stage 16    Cheapest Valid Diagnostic
Stage 17    Diagnostic Run Audit
Stage 18    Result Interpretation Loop
Stage 18.5  Failure-to-Innovation Loop                        (Codex COLLABORATIVE)
Stage 19    Re-read Literature Loop
Stage 20    Scale-up Decision
Stage 21    Result-to-Claim Construction
Stage 22    Tie / Negative Result / Reframing Strategy
Stage 23    Reviewer Red-team Loop                            (review → fix → re-review)
Stage 24    Paper Writing / Paper Improvement Loop
Stage 25    Human Decision / Next Loop
```

Four spines:
- **Discovery** (0, 1, 2, 2.5, 3) — frame the problem and select a target.
- **Grounding** (4, 5, 6, 7) — *diagnostic support* for innovation, not innovation itself.
- **Innovation** (8, 9, 10, 18.5) — divergent mechanism invention. Codex collaborative.
- **Validation** (11–25) — controls, formalization, audit, diagnostic, scale-up, claim, paper, decision.

## Pipeline (Codex-CLI dispatch)

### Stage 00 — Workspace init

```bash
mkdir -p orbit-research/
```

### Stage 0 — Mode & Risk Routing (FIRST ACTION)

Classify `$ARGUMENTS` into one of 7 routing categories:

| Category | Suggested mode | Initial risk | Stages to run |
|---|---|---|---|
| Broad area | EXPLORATION | 1–2 | 1 → 2 → 2.5 → 3 |
| Concrete idea, no artifact | INNOVATION | 2–3 | 4 → 5 → 7 → 8/9/10 |
| Concrete data / env / sim / reward in hand | INNOVATION/COMMITMENT | 2–4 | 6 → 7 → 11+ |
| Designing new method | INNOVATION | 2–3 | 4 → 5 → 8 → 9 → 10 |
| Implementing official experiments | COMMITMENT | 4 | 11 → 12 → 13 → 14 → 15 → 16 |
| Running experiments | COMMITMENT | 3–4 | 16 → 17 → 18 |
| Results failed/surprised | INNOVATION | 2–3 | 18 → 18.5 → 19 → (back to 8 or 11) |

Write `orbit-research/MODE_ROUTING.md` ending with one canonical line:
`EXPLORATION | INNOVATION | COMMITMENT + risk: <1-5>`

**Auto-stub for low-risk single-stage:** if missing, default `EXPLORATION + risk: 1`.

**Gate G0:** for high-risk transitions (scale-up, paper writing, public release, official
experiment planning), if mode/risk cannot be inferred, block; require explicit Stage 0
routing or `— mode:` flag.

### Stage 1 — Seed Framing

Write `orbit-research/SEED_FRAMING.md`. Use harness from `../shared-references/research-harness-prompts.md` §1.

### Stage 2 — Literature Map (loop)

Codex CLI invokes `/research-lit "$ARGUMENTS"`. Optionally `/arxiv`, `/semantic-scholar`,
`/exa-search`, `/deepxiv`. Write `orbit-research/LITERATURE_MAP.md`. Re-fires at Stage 19.

### Stage 2.5 — Problem Reframing Loop

Triggered when literature map suggests the problem-as-stated is the wrong cut. Write
`orbit-research/PROBLEM_REFRAMING.md` ending with `KEEP | REFRAME | SPLIT`.

### Stage 3 — Problem Selection

Required by **G1** for method commitment / official experiment planning / GPU run (unless
mode = EXPLORATION/INNOVATION with candidates marked as such).

Codex (adversarial) attacks feasibility, baseline risk, paper survivability. Write
`orbit-research/PROBLEM_SELECTION.md` ending with `PROCEED | NARROW | RETHINK`.

### Stage 4 — Assumption Ledger

Write `orbit-research/ASSUMPTION_LEDGER.md`. Each row: ID, assumption text, tag (`factual`/`working`),
test/citation. Required by **G2** for downstream claim wording.

### Stage 5 — Abstract Task / Mechanism Framing

Write `orbit-research/ABSTRACT_TASK_MECHANISM.md`. Required by **G3** at Stage 11+.

### Stage 6 — Artifact-triggered Audit

**G4:** only fires when a concrete data set / env / simulator / reward / evaluator / split
exists or has been fetched. Do NOT force this audit before then.

Write `orbit-research/ARTIFACT_AUDIT.md`. Re-emit whenever audited artifact changes.

### Stage 7 — Baseline Ceiling / Headroom Audit

Required by **G5** for "outperforms / beats / improves over" claims (unless mode =
EXPLORATION + no paper claim).

Write `orbit-research/BASELINE_CEILING.md`. Headroom is reference, not veto.

### Stage 8 — Mechanism Invention Loop  *(Codex COLLABORATIVE)*

Mode switch: `CODEX_INNOVATION_MODE = COLLABORATIVE`. Use template in
`../shared-references/innovation-loops.md` §7.1. Codex appends candidates; does NOT veto.

Procedure: see `innovation-loops.md` §2. Generate 5–10 candidates rated by
novelty/feasibility/falsifiability. Write `orbit-research/MECHANISM_IDEATION.md`.

### Stage 9 — Analogy / Cross-pollination Loop  *(Codex COLLABORATIVE)*

Procedure: see `innovation-loops.md` §3. For each top candidate, find ≥1 analogous solved
problem. Map *what transfers / what does not / what new constraint*. Write
`orbit-research/ANALOGY_TRANSFER.md`.

### Stage 10 — Algorithm Sketch Tournament  *(Codex COLLABORATIVE on sketch / ADVERSARIAL on adjudication)*

Procedure: see `innovation-loops.md` §4. 1-page sketch per candidate; round-robin pairwise
on diagnosability/fidelity/falsifiability/integration cost. Mark a TENTATIVE_PREFERRED_SKETCH_ID
for Stage 11 commitment review (this is **not** a final method commitment); **keep
ALTERNATES** for revival in Stage 11 review or in Stage 18.5.

Write `orbit-research/ALGORITHM_TOURNAMENT.md` ending with
`TENTATIVE_PREFERRED_SKETCH_ID + ALTERNATES + ABSTAIN_REASONS`.

### Stage 11 — HMBC Matrix  *(Codex switches BACK to ADVERSARIAL)*

Required by **G6** (≥1 of MECHANISM_IDEATION / ANALOGY_TRANSFER / ALGORITHM_TOURNAMENT
must exist before commitment).

Codex CLI invokes `/research-refine "$ARGUMENTS"` then `/experiment-plan "refine-logs/FINAL_PROPOSAL.md"`.

Write `orbit-research/CONTROL_DESIGN.md`. Codex (adversarial) attacks control isolation,
null-result interpretability, component attribution.

### Stage 12 — Null-result Contract

Required by **G8** for diagnostic/confirmatory experiments (unless explicitly "exploratory probe").

Write `orbit-research/NULL_RESULT_CONTRACT.md`.

### Stage 13 — Component / Bundle Ladder

Required by **G9** for new composed methods (single justified rung acceptable). Exception:
baseline reproduction or single-component runs.

Write `orbit-research/COMPONENT_BUNDLE_LADDER.md` (consumers also read v1.0 alias
`COMPONENT_LADDER.md`).

### Stage 14 — Algorithmic Formalization

Required by **G10** for scale-up to official experiments.

Write `orbit-research/ALGORITHMIC_FORMALIZATION.md`.

### Stage 15 — Plan-Code Consistency Loop

Codex CLI invokes `/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"`, then runs
semantic audit per `../shared-references/semantic-code-audit.md`.

Always write `orbit-research/PLAN_CODE_AUDIT.md` with verdict line on its own line:
`MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`.

**Gate G11:** `CRITICAL_MISMATCH` blocks scale-up; loop fix → re-audit. `ERROR` advisory
at diagnostic, blocks at scale-up pending human acknowledgement.

### Stage 16 — Cheapest Valid Diagnostic

Write `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md` (consumers also read v1.0 alias
`TINY_RUN_PLAN.md`). Cheapest run that could falsify the central claim — not necessarily tiny.

### Stage 17 — Diagnostic Run Audit

Codex CLI invokes `/run-experiment "[diagnostic command]"`, `/monitor-experiment`. For
many jobs, `/experiment-queue "[manifest]"`.

Write `orbit-research/DIAGNOSTIC_RUN_REPORT.md` (alias: `TINY_RUN_REPORT.md`) and
`orbit-research/DIAGNOSTIC_RUN_AUDIT.md` (alias: `TINY_RUN_AUDIT.md`) with verdict
`PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT`.

**Gate G12:** if diagnostic failed in a regime that violates mechanism preconditions, do
NOT reject the mechanism — recommend diagnostic redesign.

### Stage 18 — Result Interpretation Loop

Codex CLI invokes `/analyze-results "[results path]"`. Write
`orbit-research/RESULT_INTERPRETATION.md`.

**Gate G14:** if NULL_RESULT_CONTRACT triggered tie/failure, frame honestly — no positive
narrative.

### Stage 18.5 — Failure-to-Innovation Loop  *(Codex COLLABORATIVE)*

Procedure: see `innovation-loops.md` §5. Find falsified assumptions, ask the inversion
question, revive alternates from Stage 10. Write `orbit-research/FAILURE_TO_INNOVATION.md`.

### Stage 19 — Re-read Literature Loop

Targeted `/research-lit` calls per question. See `innovation-loops.md` §6. Write
`orbit-research/LITERATURE_REREAD_NOTE.md`.

### Stage 20 — Scale-up Decision

Codex CLI invokes `/result-to-claim "[experiment description]"`.

Verify Stage 20 preconditions (per harness §20). **Gate G15:** mode = COMMITMENT or
risk ≥ 4 requires `HUMAN_DECISION_NOTE.md`. **Gate G19:** scale-up is a high-risk
transition.

Write `orbit-research/SCALEUP_DECISION.md` ending with
`PROCEED | HOLD | REDESIGN | HUMAN_DECISION_REQUIRED`.

### Stage 21 — Result-to-Claim Construction

Build claim → evidence → control → scope → limitation chain.

**Gate G17:** label exploratory findings explicitly as "exploratory finding, not pre-planned hypothesis."

Write `orbit-research/CLAIM_CONSTRUCTION.md`. Required by **G16** for Stage 24.

### Stage 22 — Tie / Negative / Reframing

Write `orbit-research/NEGATIVE_RESULT_STRATEGY.md`. Apply G17 anti-post-hoc check.

### Stage 23 — Reviewer Red-team Loop

Codex CLI invokes `/auto-review-loop "$ARGUMENTS" — difficulty: hard`,
`/experiment-audit "[results and code]"`. The ARIS skill manages review → fix → re-review
iterations and writes `orbit-research/RED_TEAM_REVIEW.md` directly.

### Stage 24 — Paper Writing / Improvement Loop

**Gate G16 + G18:** refuse start if `CLAIM_CONSTRUCTION.md` absent (also enforced inline
in `paper-writing/SKILL.md`).

Codex CLI invokes:

```bash
/paper-writing "NARRATIVE_REPORT.md" — venue: $VENUE, assurance: submission
```

`/paper-writing` transitively invokes `/paper-plan`, `/paper-figure`, `/figure-spec` or
`/paper-illustration`, `/paper-write`, `/paper-compile`, `/auto-paper-improvement-loop`,
`/paper-claim-audit`, `/citation-audit`.

Track iterations in `orbit-research/PAPER_IMPROVEMENT_LOG.md`.

**ARIS unavailability:** if any ARIS slash invocation fails, print
"ARIS skill X unavailable. Stage 24 degraded: <fallback or HUMAN_DECISION_REQUIRED>."
Continue gracefully. If load-bearing for a hard gate, escalate to HUMAN_DECISION_REQUIRED.

### Stage 25 — Human Decision / Next Loop

Write `orbit-research/HUMAN_DECISION_NOTE.md` ending with
`PROCEED | NARROW | REDESIGN | RE-READ | CHANGE BENCHMARK | STOP | HUMAN_DECISION_REQUIRED`.

**Gate G19:** required at all "high-risk transitions."

## Innovation Loop Dispatch

Stages 8, 9, 10, 18.5 require Codex collaborative mode (no veto). See
`../shared-references/innovation-loops.md` §7.

```
IF current_stage IN {8, 9, 10, 18.5}:
    codex_mode = COLLABORATIVE; use innovation-loops.md §7.1 template
ELSE IF current_stage IN {11, 14, 15, 17, 21, 23}:
    codex_mode = ADVERSARIAL; use semantic-code-audit.md or research-harness-prompts.md template
```

## Hard Gates Enforcement (G0–G19)

Full canonical text in `../shared-references/research-agent-pipeline.md` §6. Compact
summary:

- **G0** Mode & Risk Routing required at high-risk transitions; auto-stub for low-risk.
- **G1** Method commitment / official planning / GPU run requires PROBLEM_SELECTION.
- **G2** Downstream "is/will" claims must trace to ASSUMPTION_LEDGER.
- **G3** Stage 11+ requires ABSTRACT_TASK_MECHANISM.
- **G4** ARTIFACT_AUDIT only required after the artifact exists.
- **G5** "outperforms" claims require BASELINE_CEILING.
- **G6** Method commitment requires ≥1 of MECHANISM_IDEATION / ANALOGY_TRANSFER / ALGORITHM_TOURNAMENT.
- **G7** Result feeding paper claims requires CONTROL_DESIGN.
- **G8** Diagnostic/confirmatory experiments require NULL_RESULT_CONTRACT.
- **G9** Official run with new composed method requires COMPONENT_BUNDLE_LADDER (single justified rung OK).
- **G10** Scale-up to official experiments requires ALGORITHMIC_FORMALIZATION.
- **G11** PLAN_CODE_AUDIT = CRITICAL_MISMATCH blocks scale-up unconditionally.
- **G12** Diagnostic failure that violated mechanism preconditions does NOT kill the mechanism.
- **G13** Test set isolation: no tuning/selection on test set.
- **G14** No positive framing after NULL_RESULT_CONTRACT-triggered tie/failure.
- **G15** Scale-up in COMMITMENT or risk ≥ 4 requires HUMAN_DECISION_NOTE.
- **G16** Stage 24 (paper) requires CLAIM_CONSTRUCTION.
- **G17** Post-hoc reframings must be labelled "exploratory finding, not pre-planned hypothesis."
- **G18** /paper-writing inline guard: refuse without CLAIM_CONSTRUCTION.
- **G19** Scale-up, paper, public release require HUMAN_DECISION_NOTE.

## Suggested Artifact Layout

```text
project/
├── orbit-research/
│   ├── MODE_ROUTING.md
│   ├── SEED_FRAMING.md
│   ├── LITERATURE_MAP.md
│   ├── PROBLEM_REFRAMING.md
│   ├── PROBLEM_SELECTION.md
│   ├── ASSUMPTION_LEDGER.md
│   ├── ABSTRACT_TASK_MECHANISM.md
│   ├── ARTIFACT_AUDIT.md
│   ├── BASELINE_CEILING.md
│   ├── MECHANISM_IDEATION.md
│   ├── ANALOGY_TRANSFER.md
│   ├── ALGORITHM_TOURNAMENT.md
│   ├── CONTROL_DESIGN.md
│   ├── NULL_RESULT_CONTRACT.md
│   ├── COMPONENT_BUNDLE_LADDER.md
│   ├── ALGORITHMIC_FORMALIZATION.md
│   ├── PLAN_CODE_AUDIT.md
│   ├── DIAGNOSTIC_EXPERIMENT_PLAN.md
│   ├── DIAGNOSTIC_RUN_REPORT.md
│   ├── DIAGNOSTIC_RUN_AUDIT.md
│   ├── RESULT_INTERPRETATION.md
│   ├── FAILURE_TO_INNOVATION.md
│   ├── LITERATURE_REREAD_NOTE.md
│   ├── SCALEUP_DECISION.md
│   ├── CLAIM_CONSTRUCTION.md
│   ├── NEGATIVE_RESULT_STRATEGY.md
│   ├── RED_TEAM_REVIEW.md
│   ├── PAPER_IMPROVEMENT_LOG.md
│   └── HUMAN_DECISION_NOTE.md
├── refine-logs/
│   ├── FINAL_PROPOSAL.md
│   └── EXPERIMENT_PLAN.md
├── CODE/
├── LOGS/
├── EXPERIMENT_TRACKER.md
└── paper/
```

## Output Protocols

> Follow shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)**
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)**
> - **[Output Language Protocol](../shared-references/output-language.md)**

## Guardrails

- Move fast in exploration; slow down before high-risk commitment.
- Innovation loops produce candidates; commitment gates pick what runs.
- Reuse ARIS execution skills (`/auto-review-loop`, `/paper-writing`, `/experiment-bridge`,
  `/auto-paper-improvement-loop`, `/paper-claim-audit`, `/citation-audit`,
  `/experiment-audit`); do not reimplement them.
- Convergence over volume: correctness before generation speed.
- Do not skip Stage 15 (plan-code audit) or Stage 17 (diagnostic-run audit) before scale-up.
- Do not self-certify integrity-critical artifacts with a single model family.
- Preserve human judgment at high-risk irreversible transitions (G15, G19).
