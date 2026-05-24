<p align="center">
  <img src="assets/ORBIT.png" alt="ORBIT — Open Research Brainstorming and Iterative Testing" width="640">
</p>

# ORBIT — Open Research Brainstorming and Iterative Testing

**Input-mode note:** `/idea-to-proposal` now distinguishes broad keywords,
long context `.md` files, and committed draft-idea `.md` files. Context docs still run
discovery; only explicit draft ideas skip directly to refinement.

**STOP-A boundary note:** `/idea-to-proposal` and `/idea-discovery` are non-experimental
in ORBIT v1.4+. They do not run experiments, do not use GPU, and do not call
`/run-experiment`. Idea ranking before STOP A uses literature grounding, novelty posture,
feasibility, mechanism plausibility, baseline/headroom, expected diagnostic clarity,
paper-mode fit, and collaborator critique.

**Default research posture:** ORBIT is not an automatic novelty veto. The default
mode is a normal publishable AI paper: preserve promising ideas, classify related work,
position rather than abandon, freeze the proposal after STOP A, and use adversarial review
later when paper-level claims exist. Similar or concurrent work goes to
`orbit-research/CONCURRENT_WORK_WATCHLIST.md` unless `/novelty-check` finds a true
`STRONG_BLOCKER`.

**Language note:** ORBIT's persistent research artifacts default to English even when the
chat is in Chinese. Chinese templates are manual opt-in only.

**Version terminology:** Methodology contract = ORBIT v1.3 stage/gate model. Runtime
architecture = ORBIT v2.1 pack/status workflow. Legacy Markdown compatibility = v1.x
artifacts are still read as compatibility views when needed.

## Public Entry Points

The full repository contains many specialist subskills, but new users should start with
the public entries below. The complete catalog lives in
[`skills/skill_catalog.yaml`](skills/skill_catalog.yaml); profile details are documented in
[`docs/refactor/SKILL_PROFILES.md`](docs/refactor/SKILL_PROFILES.md).

| Profile | Public entries | Purpose |
|---|---|---|
| `orbit-core` | `/orbit-status`, `/idea-to-proposal`, `/experiment-bridge`, `/diagnostic-to-review`, `/proposal-revise` | Research workflow from STOP A through STOP C |
| `paper-pack` | `/paper-draft`, `/paper-from-claims`, `/submission-package` | Drafting, evidence-bound writing, strict package checks |
| `patent-pack` | `/patent-pipeline` | Patent drafting workflow |
| `presentation-pack` | `/paper-slides`, `/paper-poster`, `/grant-proposal` | Talks, posters, and grant drafts |
| `infra-pack` | `/run-experiment`, `/vast-gpu`, `/serverless-modal`, `/experiment-queue` | GPU and experiment execution |

Internal skills remain available for advanced direct use and for orchestration, but they
are not the recommended first interaction surface. `/import-codex-review` is a public
recovery utility used only after a standalone Codex handoff is required.

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
- **Codex collaborative mode** during innovation; adversarial review for paper-level
  claims and late commitment gates
- explicit reuse of mature ARIS execution skills (`/auto-review-loop`, `/paper-draft`,
  `/paper-from-claims`, `/submission-package`, `/auto-paper-improvement-loop`,
  `/paper-claim-audit`, `/citation-audit`,
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
selection. No methods are committed, no experiments are run, and no GPU is used before
STOP A.

**Concrete idea (INNOVATION mode):**
```text
/research-pipeline "problem | rough method idea"
```

ORBIT routes through Grounding (assumption ledger, abstract task, baseline ceiling) and
into Innovation Spine (mechanism invention, analogy transfer, algorithm sketch tournament).

**Implementing official experiments (COMMITMENT mode):**
```text
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
```

ORBIT turns the approved proposal into experiment planning artifacts, implementation,
plan-code audit, and limited probes before formal diagnostics.

**From results to paper:**
```text
/result-to-claim "main result on benchmark X with method Y"
/paper-from-claims "claims/claim_ledger.json"
/submission-package "paper/"
```

`/result-to-claim` accepts an experiment description (not a path); it reads from `results/`,
W&B, `EXPERIMENT_LOG.md`, etc. The argument separator is em-dash `—`, not single `-`.

## Install

Claude project-level install (recommended; avoids polluting global skills):

```bash
bash tools/install_aris.sh
```

This creates flat per-skill symlinks under `.claude/skills/`, records the
managed entries in `.aris/installed-skills.txt`, and links `.aris/tools/` to
the repo helper scripts used by skills.

Install only a public profile plus its internal support skills:

```bash
bash tools/install_aris.sh --profile orbit-core
```

Running without `--profile` keeps the existing default behavior and installs all canonical
top-level skills.

Manual Claude copy fallback:

```bash
mkdir -p .claude/skills
find skills -mindepth 1 -maxdepth 1 -type d ! -name 'skills-codex*' \
  -exec cp -r {} .claude/skills/ \;
```

Codex skill mirror install is manual and flat:

```bash
mkdir -p .agents/skills
cp -a skills/skills-codex/* .agents/skills/
# Optional reviewer overlay, installed after the base mirror:
# cp -a skills/skills-codex-gemini-review/* .agents/skills/
# cp -a skills/skills-codex-claude-review/* .agents/skills/
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
prunes it). Before STOP A/B, review is collaborator-style; after STOP C, paper-level
claim review is adversarial.

## Standard HITL Flow — 4 Stops

ORBIT v2 preserves **human-in-the-loop at 4 designed checkpoints**, not full
automation. Within each segment the agent runs continuously; between segments it pauses
(`status = awaiting_human_continue` per the [continuation contract](skills/shared-references/continuation-contract.md))
so a human can review the milestone artifact and decide whether to continue, revise, or
abandon.

```
1. /idea-to-proposal "<keyword OR context.md OR draft-idea.md>"
   Discovery → Grounding → Innovation → final proposal refinement
   Outputs proposal only: FINAL_PROPOSAL.md, FINAL_PROPOSAL_SHORT.md, METHOD_SPEC.md
   and key orbit-research grounding/innovation artifacts.
   ⏸ STOP A: collaborator review; human asks "Is this proposal worth formal experiment planning?"

2. /experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
   Experiment planning → implementation → PLAN_CODE_AUDIT.md → limited probe when mode allows
   ⏸ STOP B: review EXPERIMENT_PLAN.md + EXPERIMENT_PLAN_EXEC.md +
              PLAN_CODE_AUDIT.md + any probe reports before formal diagnostics

3. /diagnostic-to-review "<diagnostic command OR manifest>"
   Formal /run-experiment → /analyze-results → RESULT_INTERPRETATION.md →
   RESEARCH_DECISION_LOG.md → conditional-required /result-to-claim + /auto-review-loop
   Local sanity/provenance/implementation/local-mechanism probes stop after
   RESULT_INTERPRETATION.md + RESEARCH_DECISION_LOG.md.
   Paper-bearing diagnostics must run /result-to-claim and /auto-review-loop,
   producing claims/claim_ledger.json, RED_TEAM_REVIEW.md, and HUMAN_DECISION_NOTE.md.
   Aborts cleanly on integrity bottlenecks (FIX_BEFORE_GPU, corrupt evidence,
   G14/G17 violations). Unsupported hypotheses become STOP C negative/reframe
   outcomes through the claim ledger and NEGATIVE_RESULT_STRATEGY, not default
   runtime aborts.
   ⏸ STOP C: adversarial paper-claim review when paper-bearing; review RESULT_INTERPRETATION + RESEARCH_DECISION_LOG;
              if paper-bearing, also review claims/claim_ledger.json +
              RED_TEAM_REVIEW + HUMAN_DECISION_NOTE jointly

4. /paper-from-claims "claims/claim_ledger.json"
   Evidence-bound paper generation from STOP C claim ledger
   /submission-package "paper/"
   Strict compile + claim/citation/proof audits + paper_package.json
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
/idea-to-proposal "Discrete Diffusion VLA post-training"   # STOP A: review proposal
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"         # STOP B: plan + code + audit + probe
/diagnostic-to-review "[diagnostic command]"               # STOP C: review decision; claim + red-team if paper-bearing
/paper-draft "proposal/proposal_pack.json"                 # optional fast draft, no submission gates
/paper-from-claims "claims/claim_ledger.json"              # STOP D draft: evidence-bound paper after STOP C approval
/submission-package "paper/"                               # STOP D package: strict submission assurance
/orbit-status                                              # read-only status doctor whenever stuck
```

For long notes where the idea is not settled yet, pass the file as context:
`/idea-to-proposal "path/to/context.md" — input-mode: context`. Use
`— input-mode: idea` only when the `.md` is already a committed method draft that should
skip discovery.

### Proposal only (default STOP A)

```text
/idea-to-proposal "..."
```

Pauses after `FINAL_PROPOSAL.md` + Discovery/Grounding/Innovation artifacts. Review STOP A,
then run `/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"` when the proposal is worth
planning experiments for.

### STOP A revision — proposal needs targeted fixes

```text
/proposal-revise "refine-logs/FINAL_PROPOSAL.md" \
  — critiques: "ALGORITHM_TOURNAMENT picks S2 but S5 has stronger falsifiability;
                also assumption A2 about iid data is wrong, we have temporal correlation"
```

After STOP A, if the user is dissatisfied with specific points, `/proposal-revise` accepts
user-authored critique, classifies each point by which v1.3 stage owns the underlying
decision, re-runs only the affected stages, then re-integrates via `/research-refine` for
proposal targets. Anchor + simplicity checks
catch revisions that drift from the original problem or add unnecessary complexity. Stops
at `awaiting_human_continue` with a diff report. Run multiple rounds until satisfied;
use `— fresh: true` to clear and start a different revision direction.

Pass `"both"` only when both FINAL_PROPOSAL.md and EXPERIMENT_PLAN.md genuinely need
revision. After failed diagnostics, `/diagnostic-to-review` writes
`orbit-research/RESEARCH_DECISION_LOG.md`; `/proposal-revise` reads that log and defaults
to the narrowest patch mode (`mechanism-only`, `diagnostic-branch-only`,
`benchmark/control-only`, etc.) instead of revising both artifacts.

### Already have proposal, want experiment plan only

```text
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md" — mode: plan-only
```

This reads v1.3 grounding/innovation artifacts when present and writes a v1.4-aware
`EXPERIMENT_PLAN.md` index plus `EXPERIMENT_PLAN_EXEC.md` for executable details. Manual
`/experiment-plan "refine-logs/FINAL_PROPOSAL.md"` still works, but the canonical wrapper
after STOP A is `/experiment-bridge`.

### From proposal approval to formal diagnostic

```text
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"     # STOP B: plan + implementation + audit + probe
/diagnostic-to-review "[command OR manifest path]"      # formal diagnostic and interpretation
```

`/experiment-bridge` may run limited implementation-facing probes by calling
`/run-experiment`, and those probes are ledgered. Formal diagnostic execution, scientific
interpretation, decision logging, and paper-level claim/review belong to
`/diagnostic-to-review`.

Before scale-up: `PLAN_CODE_AUDIT.md` must be `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH`;
`DIAGNOSTIC_RUN_AUDIT.md` must be `PASS` (or `TINY_RUN_AUDIT.md` if v1.0 alias).
Every launched run appends provenance to `orbit-research/RUN_LEDGER.jsonl`, including
failed/OOM/timeout/no-result runs, exact commands, configs, logs, result files, and
audit verdicts.

### Migration note

Pre-patch `/idea-to-proposal` generated experiment plans. In the new flow, experiment
planning moves to `/experiment-bridge` after STOP A. Existing `EXPERIMENT_PLAN.md` files
remain readable, but new canonical runs generate them in `/experiment-bridge`.

### From results to claims (chained)

```text
/diagnostic-to-review "[diagnostic command OR manifest]"
```

Runs run-experiment → analyze-results, then applies conditional-required
`/result-to-claim` + `/auto-review-loop`: not triggered for local diagnostics, but
required for paper-bearing diagnostics. Sanity, provenance, implementation, and local
mechanism probes stop after `RESULT_INTERPRETATION.md` +
`orbit-research/RESEARCH_DECISION_LOG.md`. Diagnostics that affect paper-level claim
scope must produce `claims/claim_ledger.json`, `RED_TEAM_REVIEW.md`, and
`HUMAN_DECISION_NOTE.md` for STOP C. Failed, mixed, or surprising diagnostics write the
decision log first, then route to a local patch, diagnostic change,
failure-to-innovation, scoped proposal-revise, or archive decision.

Or invoke each individually:

```text
/analyze-results "results/"
/result-to-claim "main result on benchmark X with method Y"
/auto-review-loop "<scope>" — difficulty: hard
```

### Paper paths

```text
/paper-draft "proposal/proposal_pack.json"                 # fast draft, no submission gates
/paper-from-claims "claims/claim_ledger.json"              # evidence-bound paper after STOP C approval
/submission-package "paper/"                               # strict compile + audits + package after STOP C approval
```

`/paper-writing` remains as a compatibility router. Argument separator is em-dash `—`,
not single `-`. The underlying ARIS subskills remain intact: `/paper-plan`,
`/paper-figure`, `/figure-spec` or `/paper-illustration` or
`/paper-illustration-image2`, `/paper-write`, `/paper-compile`,
`/auto-paper-improvement-loop`, `/paper-claim-audit`, `/citation-audit`.

Phase 2b illustration backends: `figurespec` (default, deterministic JSON→SVG) /
`gemini` (AI via `/paper-illustration`, needs `GEMINI_API_KEY`) / `codex-image2`
(AI via `/paper-illustration-image2` through the local Codex native image bridge —
no external API key, uses your ChatGPT Plus/Pro quota; experimental) / `mermaid`
(Mermaid syntax, free) / `false` (manual). Override inline with `— illustration: <name>`.

ORBIT additional requirement: paper-bearing STOP D should start from
`claims/claim_ledger.json` and STOP C approval (`RED_TEAM_REVIEW.md` ending
`READY_FOR_PAPER` plus `HUMAN_DECISION_NOTE.md` ending `PROCEED`). Legacy
`CLAIM_CONSTRUCTION.md` is a compatibility view.

## Codex Availability

Codex review is required by default. MCP transport, auth, or sandbox failure does not
create a valid single-model substitute for ORBIT commitment gates. Instead, the producing
skill exports a standalone Codex review prompt under `orbit-research/codex-prompts/`, sets
`ORBIT_STATE.json` to `codex_review_needed`, and tells the user to import the standalone
response with `/import-codex-review`.

No single-model fallback satisfies commitment gates unless the user explicitly passes
`codex-required: false` and later accepts degraded artifacts. The standard recovery path
keeps Codex required; it only changes the transport from MCP to a manual Codex terminal.

Full contract: `skills/shared-references/codex-precondition.md` and
`docs/refactor/CODEX_HANDOFF.md`.

## Release Checks

Use the fast stabilization target for v2.1 release sanity checks:

```bash
make release-check
```

This runs the repository audit, skill profile check, mirror drift check, prompt asset
check, golden pack validation, and `make test-fast`. Full `pytest -q` is still useful for
broader local or CI coverage when the environment has enough timeout and optional test
dependencies, but it is not the fast release gate.

## Important Files

- `skills/research-pipeline/SKILL.md` — v1.3 routing orchestrator
- `skills/idea-to-proposal/SKILL.md` — STOP A: from area/context/idea to proposal only
- `skills/experiment-bridge/SKILL.md` — STOP B: experiment planning + implementation + plan-code audit + limited probe when mode allows
- `skills/proposal-revise/SKILL.md` — STOP A revision loop: targeted edits driven by user critique
- `skills/diagnostic-to-review/SKILL.md` — STOP C: chains run → analyze, then conditional-required claim + review for paper-bearing diagnostics
- `skills/shared-references/research-agent-pipeline.md` — canonical 0–25 stage map + 19 hard gates
- `skills/shared-references/research-harness-prompts.md` — per-stage canonical prompts
- `skills/shared-references/innovation-loops.md` — Stages 8/9/10/18.5 procedures + Codex collaborative mode
- `skills/shared-references/research-posture.md` — default normal-paper, positioning-first, proposal-stability policy
- `skills/shared-references/semantic-code-audit.md` — Stage 15 plan-code audit + Stage 17 diagnostic-run audit
- `skills/shared-references/continuation-contract.md` — STATE.json schema, three-state enum, cross-skill resume
- `skills/shared-references/reviewer-routing.md` — Codex / Oracle reviewer defaults
- `AGENT_GUIDE.md` — agent-facing routing index
- `orbit-research/CONCURRENT_WORK_WATCHLIST.md` — related/concurrent work that should not destabilize proposals by default
- `orbit-research/PROPOSAL_STABILITY.md` — STOP A freeze record and proposal reopen rules

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
