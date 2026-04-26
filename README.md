<p align="center">
  <img src="assets/ORBIT.png" alt="ORBIT — Open Research Brainstorming and Iterative Testing" width="640">
</p>

# ORBIT — Open Research Brainstorming and Iterative Testing

**v1.3 — research-methodology routing harness.** ORBIT routes you through 26 stages organised
into four spines (Discovery / Grounding / Innovation / Validation) by mode (EXPLORATION /
INNOVATION / COMMITMENT) and risk score. It moves fast in exploration, slows down before
commitment, encourages divergent mechanism invention before converging, and only enforces
heavy gates before high-risk irreversible transitions. Built on ARIS execution skills —
ORBIT reuses them rather than reimplementing.

> 中文版 README 见 [README_CN.md](./README_CN.md)（v1.3 简明中文入口）。

## What v1.3 Is

v1.0 was a strict diagnostic harness with 16 forced stages (0A–15) that prevented bad
experiments by forcing data audits, baseline ceilings, and tiny runs upfront. That worked
for routine validation but it (a) blocked creative method invention behind upfront audits,
(b) demanded a tiny run even when a tiny run could not falsify the central claim, and
(c) required data audits before there was any data.

v1.3 keeps the diagnostic discipline at commitment time and adds:

- **mode & risk routing** — exploration vs. innovation vs. commitment, risk 1–5
- **assumption ledger** as a first-class artifact
- **artifact-triggered audits** (data audit fires only after the data exists)
- **innovation loops** — divergent mechanism invention, analogy transfer, algorithm sketch
  tournament, failure-to-innovation
- **cheapest valid diagnostic** instead of "always tiny run"
- **component / minimal mechanism bundle ladder** instead of "always one component at a time"
- **plan-code consistency loop** and **reviewer red-team loop** — explicit audit → fix → re-audit
- **Codex collaborative mode** during innovation; adversarial mode at commitment gates
- explicit reuse of mature ARIS execution skills (`/auto-review-loop`, `/paper-writing`,
  `/auto-paper-improvement-loop`, `/paper-claim-audit`, `/citation-audit`,
  `/experiment-audit`, `/experiment-bridge`)

## Four Spines

ORBIT organises the 26 stages into four spines. They are **not strictly sequential** — the
orchestrator routes by mode and risk; many stages are loops; some stages skip in
EXPLORATION mode and only fire before COMMITMENT.

| Spine | Stages | Purpose |
|---|---|---|
| **Discovery** | 0, 1, 2, 2.5, 3 | Frame the problem and select a target. Routing, seed framing, literature mapping, problem reframing, problem selection. |
| **Grounding** | 4, 5, 6, 7 | *Diagnostic support* for innovation, not innovation itself. Assumption ledger, abstract task / mechanism framing, artifact-triggered audit (only when data/env/benchmark exists), baseline ceiling. |
| **Innovation** | 8, 9, 10, 18.5 | Divergent mechanism invention, analogy / cross-pollination, algorithm sketch tournament, failure-to-innovation. **Codex switches to collaborative mode here** — see `skills/shared-references/innovation-loops.md`. |
| **Validation** | 11–25 | Hypothesis-mechanism-benchmark-control matrix, null-result contract, component bundle, formalization, plan-code audit, cheapest valid diagnostic, diagnostic run audit, result interpretation, scale-up, claim construction, tie / negative strategy, reviewer red-team, paper writing, human decision. |

Grounding (4–7) is the calibration layer that makes Innovation actually diagnosable. It is
*not* where new methods are invented; it is where assumptions, abstract task framing,
available artifacts, and baseline headroom get pinned down so that Innovation produces
candidates and Validation can tell whether they work.

## Mode & Risk Routing

The orchestrator's first action is to classify your input and write `MODE_ROUTING.md`.

**Modes:**
- `EXPLORATION` — broad area, unclear problem, no committed artifact. Move fast, low gate
  intensity, candidates allowed everywhere, no paper claims yet.
- `INNOVATION` — concrete problem, no committed method. Innovation loops fire (Stages 8/9/10);
  Grounding (4–7) provides calibration without blocking ideation.
- `COMMITMENT` — committed method, official experiments, scale-up, paper writing.
  Full Validation Spine engaged with all hard gates active.

**Risk score (1–5):** local/reversible (1–2) → non-trivial GPU (3) → official runs / paper
claims (4) → public release / submission (5).

Not every stage runs every time. The orchestrator runs the minimum stages needed to satisfy
the hard gates that apply at your risk level. Full per-mode routing rules in
`skills/shared-references/research-agent-pipeline.md`.

## Quick Start

In Claude Code (or another supported client):

**Broad area (EXPLORATION mode):**
```text
/research-pipeline "Discrete Diffusion VLA post-training"
```

ORBIT routes through Discovery: seed framing → literature map → problem reframing → problem
selection. No methods committed, no experiments run.

**Concrete idea (INNOVATION mode):**
```text
/research-pipeline "problem | rough method idea"
```

ORBIT routes through Grounding (assumption ledger, abstract task, baseline ceiling) and
into Innovation Spine (mechanism invention, analogy transfer, algorithm sketch tournament).

**Implementing official experiments (COMMITMENT mode):**
```text
/research-pipeline "refine-logs/EXPERIMENT_PLAN.md"
```

ORBIT routes through Validation Spine: HMBC matrix, null-result contract, component bundle,
formalization, plan-code audit, cheapest valid diagnostic.

**From results to paper:**
```text
/result-to-claim "main result on benchmark X with method Y"
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
```

`/result-to-claim` accepts an experiment description (not a path); it reads from `results/`,
W&B, `EXPERIMENT_LOG.md`, etc. The argument separator is em-dash `—`, not single `-`.

## Install

Project-level install (recommended; avoids polluting global skills):

```bash
bash tools/install_aris.sh
```

Manual copy fallback:

```bash
mkdir -p .claude/skills
cp -r skills/* .claude/skills/
```

Codex reviewer requires Codex CLI / MCP:

```bash
npm install -g @openai/codex
codex setup
claude mcp add codex -s user -- codex mcp-server
```

ORBIT default Codex reviewer config:

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
sandbox_mode = "danger-full-access"
```

## v1.3 Pipeline at a Glance

```text
Discovery   → 0  Mode & Risk Routing
              1  Seed Framing
              2  Question-driven Literature Map         (loop)
              2.5 Problem Reframing Loop
              3  Problem Taste / Selection

Grounding   → 4  Assumption Ledger
              5  Abstract Task / Mechanism Framing
              6  Artifact-triggered Audit               (only when artifact exists)
              7  Baseline Ceiling / Headroom Audit

Innovation  → 8  Mechanism Invention Loop               (Codex collaborative)
              9  Analogy / Cross-pollination Loop       (Codex collaborative)
              10 Algorithm Sketch Tournament            (Codex collaborative)
              18.5 Failure-to-Innovation Loop           (Codex collaborative; triggered after Stage 18)

Validation  → 11 Hypothesis-Mechanism-Benchmark-Control Matrix
              12 Null-result Contract
              13 Progressive Component / Minimal Mechanism Bundle
              14 Algorithmic Formalization
              15 Plan-Code Consistency Loop             (audit → fix → re-audit)
              16 Cheapest Valid Diagnostic
              17 Diagnostic Run Audit
              18 Result Interpretation Loop
              19 Re-read Literature Loop
              20 Scale-up Decision
              21 Result-to-Claim Construction
              22 Tie / Negative Result / Reframing Strategy
              23 Reviewer Red-team Loop                 (review → fix → re-review)
              24 Paper Writing / Improvement Loop       (delegates to ARIS chain)
              25 Human Decision / Next Loop
```

Full canonical map with per-stage responsibilities, required artifacts, and verdict
endings: `skills/shared-references/research-agent-pipeline.md`.

## Hard Gates

v1.3 enforces 19 gates (G0–G19). They are verdict-line gates: each gate parses a single
canonical token in the audit artifact, not file presence. Producers emit v1.3 artifact
names; consumers accept either v1.0 or v1.3 names (preferring v1.3 if both exist).

A few highlights:

- **G6** — method commitment requires ≥1 of `MECHANISM_IDEATION` / `ANALOGY_TRANSFER` /
  `ALGORITHM_TOURNAMENT` (no method commit without at least one innovation artifact)
- **G8** — diagnostic / confirmatory experiments require `NULL_RESULT_CONTRACT.md`
- **G11** — `PLAN_CODE_AUDIT.md` verdict `CRITICAL_MISMATCH` blocks scale-up unconditionally
- **G12** — diagnostic run failure that violated the mechanism's necessary preconditions
  does NOT kill the mechanism (replaces v1.0 "tiny-run failure → kill idea")
- **G14** — no positive framing after `NULL_RESULT_CONTRACT`-triggered tie/failure
- **G15 + G19** — scale-up, paper writing, public release require `HUMAN_DECISION_NOTE.md`
- **G17** — post-hoc reframings must be labelled "exploratory finding, not pre-planned hypothesis"

Full canonical text: `skills/shared-references/research-agent-pipeline.md` §6.

v1.0 gates "tiny run before scale-up always" and "data audit before any other stage" are
intentionally **removed** in v1.3, replaced by G11/G12 (regime-aware) and G4
(artifact-triggered).

## Innovation Loops

Stages 8, 9, 10, 18.5, and 19 each delegate to a named loop in
`skills/shared-references/innovation-loops.md`:

- **Loop A** — Mechanism Invention (5–10 candidates, no convergence inside the loop)
- **Loop B** — Analogy / Cross-pollination (≥1 analogous solved problem per candidate)
- **Loop C** — Algorithm Sketch Tournament (round-robin pairwise; keep alternates)
- **Loop D** — Failure-to-Innovation (revive alternates after a failed run)
- **Loop E** — Re-read Literature (targeted question-driven queries)

Plus the **Collaborative Claude-Codex Innovation Mode** spec: during innovation loops
Codex switches to no-veto, add-only mode (so it expands the candidate space rather than
prunes it). Codex switches back to adversarial mode at commitment gates.

## Standard HITL Flow — 4 Stops

ORBIT v1.3 is built around **human-in-the-loop at 4 designed checkpoints**, not full
automation. Within each segment the agent runs continuously; between segments it pauses
(`status = awaiting_human_continue` per the [continuation contract](skills/shared-references/continuation-contract.md))
so a human can review the milestone artifact and decide whether to continue, revise, or
abandon.

```
1. /idea-to-proposal "<keyword OR draft-idea.md>"
   Discovery → Grounding → Innovation → final refinement → experiment plan
   ⏸ STOP A: review FINAL_PROPOSAL.md + EXPERIMENT_PLAN.md + claim map together
              (single combined "is this worth GPU?" decision)

2. /experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
   Implementation + plan-code consistency loop (Stage 15)
   ⏸ STOP B: review PLAN_CODE_AUDIT.md verdict — last gate before GPU spending

3. /diagnostic-to-review "<diagnostic command OR manifest>"
   /run-experiment (auto-routes single vs queue-batch) → /analyze-results →
   /result-to-claim → /auto-review-loop
   Aborts cleanly on any verdict-line bottleneck (FIX_BEFORE_GPU, claim_supported=no,
   irrecoverable review score, G14/G17 violations) — abort is awaiting_human_continue
   with clear next_action, never a silent failure
   ⏸ STOP C: review CLAIM_CONSTRUCTION + RED_TEAM_REVIEW + HUMAN_DECISION_NOTE jointly

4. /paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
   Paper writing chain (G16+G18 enforced — needs CLAIM_CONSTRUCTION.md from STOP C)
   ⏸ STOP D (implicit): submission-readiness review before push to Overleaf / arXiv
```

**Within-segment behavior:** AUTO_PROCEED = true by default. Pass `— human checkpoint: true`
to any skill to pause at every internal phase. Pass `— no-checkpoint: true` to skip the
designed `awaiting_human_continue` exit (only sane in dev / demo).

**Resume behavior:** every skill in this flow follows the
[continuation contract](skills/shared-references/continuation-contract.md). If a skill
crashes mid-execution, just re-invoke it — STATE.json on disk decides resume vs fresh
based on phase progress, artifact presence, and 24h staleness.

## Common Workflows

### Standard 4-stop end-to-end (recommended)

```text
/idea-to-proposal "Discrete Diffusion VLA post-training"   # STOP A: review proposal + experiment plan
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"        # STOP B: review PLAN_CODE_AUDIT
/diagnostic-to-review "[diagnostic command]"               # STOP C: review claim + red-team
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR         # STOP D: ship paper
```

### Just want a proposal (no experiment plan yet)

```text
/idea-to-proposal "..." — stop-at-proposal: true
```

Pauses at Phase 5 with FINAL_PROPOSAL.md + Discovery/Grounding/Innovation artifacts. Run
`/experiment-plan` separately when ready.

### Already have proposal, want experiment plan only

```text
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

This will read v1.3 grounding/innovation artifacts (assumption ledger, abstract task,
algorithm tournament) when present and write a v1.3-aware EXPERIMENT_PLAN.md.

### From plan to running diagnostic (auto-routes solo vs queue)

```text
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
/run-experiment "[command OR manifest path OR grid spec]"
/monitor-experiment "[run id or server]"
```

`/run-experiment` auto-routes: ≤5 jobs runs inline, ≥10 jobs auto-delegates to
`/experiment-queue`. Override with `— queue: true` / `— solo: true`. `/experiment-queue`
itself defaults `max_parallel: auto` — when running on an exclusive 8-GPU box it parallels
across all 8; on a shared box it conservatively uses only the truly idle GPUs.

Before scale-up: `PLAN_CODE_AUDIT.md` must be `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH`;
`DIAGNOSTIC_RUN_AUDIT.md` must be `PASS` (or `TINY_RUN_AUDIT.md` if v1.0 alias).

### From results to claims (chained)

```text
/diagnostic-to-review "[diagnostic command OR manifest]"
```

Runs run-experiment → analyze-results → result-to-claim → auto-review-loop as one chain;
aborts cleanly with awaiting_human_continue + next_action on any bottleneck.

Or invoke each individually:

```text
/analyze-results "results/"
/result-to-claim "main result on benchmark X with method Y"
/auto-review-loop "<scope>" — difficulty: hard
```

### Paper writing (delegates to ARIS chain)

```text
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
```

Argument separator is em-dash `—`, not single `-`. ARIS chain remains intact:
`/paper-plan`, `/paper-figure`, `/figure-spec` or `/paper-illustration` or
`/paper-illustration-image2`, `/paper-write`, `/paper-compile`,
`/auto-paper-improvement-loop`, `/paper-claim-audit`, `/citation-audit`.

Phase 2b illustration backends: `figurespec` (default, deterministic JSON→SVG) /
`gemini` (AI via `/paper-illustration`, needs `GEMINI_API_KEY`) / `codex-image2`
(AI via `/paper-illustration-image2` through the local Codex native image bridge —
no external API key, uses your ChatGPT Plus/Pro quota; experimental) / `mermaid`
(Mermaid syntax, free) / `false` (manual). Override inline with `— illustration: <name>`.

ORBIT additional requirement: `CLAIM_CONSTRUCTION.md` must exist before `/paper-writing`
will start (G16 + G18).

## Codex availability — degradation, not silent skip

Codex (gpt-5.5 xhigh) is the cross-model reviewer everywhere in ORBIT. When unavailable
(MCP unreachable, sandbox issue, etc.), **the system reports the degradation explicitly
in three tiers**, never skips silently:

| Tier | Behavior | Where it shows up |
|---|---|---|
| **Advisory** (proceed) | Innovation loops (Stages 8/9/10/18.5) collaborative additions; Stage 15 PLAN_CODE_AUDIT at diagnostic stage; `/idea-to-proposal` Phase 4 final review | Footer of the relevant artifact: `Codex collaborative additions: NOT_AVAILABLE (codex_mcp_unreachable)` or `Phase X review: SKIPPED (codex_mcp_unreachable)` |
| **Block pending human ack** | Stage 15 PLAN_CODE_AUDIT at scale-up (G11 ERROR rule); Stage 17 G12 regime check unanswerable | DIAGNOSTIC_RUN_AUDIT.verdict = ERROR with reason; orchestrator surfaces "human-must-acknowledge-codex-down" |
| **Load-bearing degradation** | `/auto-review-loop` (Stage 23) → single-model review only; `/paper-writing` Phase 5.5/5.8 audits → BLOCKED | RED_TEAM_REVIEW.md header `⚠️ degraded: codex_mcp_unreachable, single-model review only`; PAPER_CLAIM_AUDIT / CITATION_AUDIT verdict = BLOCKED |

Full degradation contract: each skill's "ARIS / Sub-skill Unavailability" section.

## Important Files

- `skills/research-pipeline/SKILL.md` — v1.3 routing orchestrator
- `skills/idea-to-proposal/SKILL.md` — STOP A: from area/idea to proposal + experiment plan (no GPU)
- `skills/diagnostic-to-review/SKILL.md` — STOP C: chains run → analyze → claim → review
- `skills/shared-references/research-agent-pipeline.md` — canonical 0–25 stage map + 19 hard gates
- `skills/shared-references/research-harness-prompts.md` — per-stage canonical prompts
- `skills/shared-references/innovation-loops.md` — Stages 8/9/10/18.5 procedures + Codex collaborative mode
- `skills/shared-references/semantic-code-audit.md` — Stage 15 plan-code audit + Stage 17 diagnostic-run audit
- `skills/shared-references/continuation-contract.md` — STATE.json schema, three-state enum, cross-skill resume
- `skills/shared-references/reviewer-routing.md` — Codex / Oracle reviewer defaults
- `AGENT_GUIDE.md` — agent-facing routing index

## Design Principles

```text
Move fast in exploration. Slow down before commitment.
Bold ideas are allowed. Undiagnosable experiments are not.
Failure is allowed. Failure without interpretation is not.
Runnable code is not success. Code that faithfully implements the v1.3 contract is.
Innovation loops produce candidates. Commitment gates pick what runs.
Reuse ARIS execution skills. Do not reimplement them.
Preserve human judgment at high-risk irreversible transitions.
```

## Migration from v1.0

Existing user projects with v1.0 artifact names continue to work — consumers accept either
v1.0 or v1.3 names for one major version (preferring v1.3 if both exist):

| v1.0 name | v1.3 canonical |
|---|---|
| `COMPONENT_LADDER.md` | `COMPONENT_BUNDLE_LADDER.md` |
| `TINY_RUN_PLAN.md` | `DIAGNOSTIC_EXPERIMENT_PLAN.md` |
| `TINY_RUN_REPORT.md` | `DIAGNOSTIC_RUN_REPORT.md` |
| `TINY_RUN_AUDIT.md` | `DIAGNOSTIC_RUN_AUDIT.md` |

`TASK_ONTOLOGY.md` (v1.0) has no alias — its content maps to four v1.3 artifacts and must
be split manually:

- mode flag → `MODE_ROUTING.md`
- framing prose → `SEED_FRAMING.md`
- inputs/assumptions block → `ASSUMPTION_LEDGER.md`
- task/mechanism block → `ABSTRACT_TASK_MECHANISM.md`

Full migration appendix: `skills/shared-references/research-agent-pipeline.md` (v1.0 → v1.3).

Removal of v1.0 aliases is deferred to v2.0.

## Migration from BRIS (the previous name of this project)

ORBIT was previously named **BRIS — Better Research in Sleep**. Existing projects that
created artifacts under `bris-research/` should rename the directory:

```bash
# in your project root
git mv bris-research orbit-research
```

(Or `mv bris-research orbit-research` if not using git.) The `install_aris.sh` script
also accepts the legacy `BRIS_REPO` environment variable and `<!-- BRIS:BEGIN -->` /
`<!-- BRIS:END -->` markers in `CLAUDE.md` for one major version, so existing project
installs continue to work without changes; the next install run will upgrade the markers
to `<!-- ORBIT:BEGIN -->` / `<!-- ORBIT:END -->` automatically.

## License

See [LICENSE](./LICENSE).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) ([中文版](./CONTRIBUTING_CN.md)).
