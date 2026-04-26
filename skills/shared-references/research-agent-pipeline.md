# ORBIT Research Agent Pipeline — v1.3 Canonical

> **v1.3 — supersedes v1.0 (0A–15).** This shared reference is the load-bearing research
> contract for ORBIT. v1.3 replaces the rigid 0A–15 diagnostic harness with a research-methodology
> routing harness organised around four spines, mode & risk routing, innovation loops, and
> artifact-triggered audits. Old v1.0 artifact names are still parsed by consumers via
> accept-either logic — see the migration appendix at the end.

## Design Target

ORBIT guides research **judgment**, not just execution. The default behaviour is:

- move fast in exploration, slow down before high-risk commitment
- separate exploration / innovation / commitment modes; route by user intent and risk
- treat assumptions as first-class objects, never let them silently become facts
- encourage divergent mechanism invention before converging on experiments
- preserve creativity: bold methods, analogies, complex systems are welcome
- require diagnosis before commitment: every serious experiment must declare what success,
  failure, and tie would mean
- use the **cheapest valid diagnostic**, not always a tiny run
- validate complexity progressively: one component at a time, or the smallest
  mechanism-preserving bundle when synergy is required
- audit data / benchmark / simulator / reward / evaluator / split **only when those artifacts
  exist** — never demand a data audit before there is data
- use baselines to measure headroom, not to suppress new ideas
- use Codex as an independent semantic auditor at commitment gates and as a
  **collaborative innovator** during invention loops
- keep final claims evidence-bound: claim → evidence → control → scope → limitation
- preserve human judgment at high-risk irreversible transitions
- reuse mature ARIS execution skills (`/auto-review-loop`, `/paper-writing`,
  `/auto-paper-improvement-loop`, `/paper-claim-audit`, `/citation-audit`,
  `/experiment-audit`, `/experiment-bridge`); do not reimplement them

## Four-Spine Framing

ORBIT organises the 26 stages into four spines. They are **not strictly sequential** — the
orchestrator routes by mode/risk; many stages are loops; some stages skip in EXPLORATION mode
and only fire before COMMITMENT.

| Spine | Stages | Purpose |
|---|---|---|
| **Discovery** | 0, 1, 2, 2.5, 3 | Frame the problem and select a target. Routing, seed framing, literature mapping, problem reframing, problem selection. |
| **Grounding** | 4, 5, 6, 7 | *Diagnostic support* for innovation, not innovation itself. Assumption ledger, abstract task / mechanism framing, artifact-triggered audit (only when data/env/benchmark exists), baseline ceiling. |
| **Innovation** | 8, 9, 10, 18.5 | Divergent mechanism invention, analogy / cross-pollination, algorithm sketch tournament, failure-to-innovation. **Codex switches to collaborative mode here** — see `innovation-loops.md`. |
| **Validation** | 11–25 | Hypothesis-mechanism-benchmark-control matrix, null-result contract, component bundle, formalization, plan-code audit, cheapest valid diagnostic, diagnostic run audit, result interpretation, scale-up, claim construction, tie/negative strategy, reviewer red-team, paper writing, human decision. |

Grounding (4–7) is the calibration layer that makes Innovation actually diagnosable. It is
not where new methods are invented; it is where assumptions, abstract task framing, available
artifacts, and baseline headroom get pinned down so that Innovation produces candidates and
Validation can tell whether they work.

## Mode & Risk Routing (Stage 0)

The orchestrator's first action is to classify user intent and write `MODE_ROUTING.md`.

**Modes:**
- `EXPLORATION` — broad area, unclear problem, no artifact in hand. Move fast, low gate
  intensity, candidates allowed everywhere, no paper claims yet.
- `INNOVATION` — concrete problem, no committed method. Innovation loops fire (Stages 8/9/10);
  Grounding (4–7) provides calibration without blocking ideation.
- `COMMITMENT` — committed method, official experiments, scale-up, paper writing.
  Full Validation Spine engaged with all hard gates active.

**Risk score (1–5):**
- 1–2 — local, reversible, no GPU spend, no public release
- 3 — non-trivial GPU spend, internal results
- 4 — official benchmark runs, paper-bearing claims
- 5 — public release, submission, high-cost irreversible commitment

**Routing rules** (mapped from 7 input categories):

| User input shape | Suggested mode | Initial risk | First stages to run |
|---|---|---|---|
| Broad research area | EXPLORATION | 1–2 | 1 → 2 → 2.5 → 3 |
| Concrete idea, no artifacts | INNOVATION | 2–3 | 4 → 5 → 7 (skip 6) → 8/9/10 |
| Concrete data / benchmark / simulator / reward in hand | INNOVATION/COMMITMENT | 2–4 | 6 (artifact-triggered audit) → 7 → 11+ |
| Designing new method | INNOVATION | 2–3 | 4 → 5 → 8 → 9 → 10 (then 11+ on commitment) |
| Implementing official experiments | COMMITMENT | 4 | 11 → 12 → 13 → 14 → 15 → 16 |
| Running experiments | COMMITMENT | 3–4 | 16 → 17 → 18 |
| Results failed / surprised | INNOVATION | 2–3 | 18 → 18.5 → 19 → (back to 8 or 11 as needed) |

Do not force every stage on every request. Run the minimum stages needed to satisfy the
hard gates that apply at the user's risk level.

## Canonical Stage Map (v1.3)

```text
0     Mode & Risk Routing
1     Seed Framing
2     Question-driven Literature Map                  (loop)
2.5   Problem Reframing Loop
3     Problem Taste / Problem Selection
4     Assumption Ledger
5     Abstract Task / Mechanism Framing
6     Artifact-triggered Data / Env / Benchmark Audit (only when artifact exists)
7     Baseline Ceiling / Headroom Audit
8     Mechanism Invention Loop                        (innovation: Codex collaborative)
9     Analogy / Cross-pollination Loop                (innovation: Codex collaborative)
10    Algorithm Sketch Tournament                     (innovation: Codex collaborative)
11    Hypothesis-Mechanism-Benchmark-Control Matrix
12    Null-result Contract
13    Progressive Component / Minimal Mechanism Bundle
14    Algorithmic Formalization
15    Plan-Code Consistency Loop                      (audit → fix → re-audit)
16    Cheapest Valid Diagnostic
17    Diagnostic Run Audit
18    Result Interpretation Loop
18.5  Failure-to-Innovation Loop                      (innovation: Codex collaborative)
19    Re-read Literature Loop
20    Scale-up Decision
21    Result-to-Claim Construction
22    Tie / Negative Result / Reframing Strategy
23    Reviewer Red-team Loop                          (review → fix → re-review)
24    Paper Writing / Paper Improvement Loop
25    Human Decision / Next Loop
```

This is a routed graph, not a linear list. Loops feed back to earlier stages:

```text
Discovery -> Grounding -> Innovation -> Validation
   ^                          ^             |
   |                          |             v
re-read literature <-- failure-to-innovation <-- result interpretation
```

## Stage Responsibilities

### 0. Mode & Risk Routing

The orchestrator's first action. Classify the user's input into one of the 7 categories
above; pick a mode (EXPLORATION/INNOVATION/COMMITMENT) and a risk score (1–5); decide
which stages to run next; record the choice for downstream gates to read.

Required artifact: `MODE_ROUTING.md`

Required ending: `EXPLORATION | INNOVATION | COMMITMENT` + `risk: <1-5>`

If `MODE_ROUTING.md` is absent at the start of a low-risk single-stage command, the
orchestrator infers a default (EXPLORATION, risk=1) and writes a stub. Only high-risk
transitions require explicit Stage 0 routing.

### 1. Seed Framing

Use when the user gives only a research area. Define the search boundary: field,
constraints, initial questions, keywords, subfields, adjacent areas, and paper types
to read first. Do not propose final methods, commit to benchmarks, or write experiments.

Required artifact: `SEED_FRAMING.md`

### 2. Question-driven Literature Map

Read papers to find claim-evidence gaps, missing controls, benchmark saturation, failure
regimes, weak assumptions, strong baselines, and underexplored settings. Run as a **loop**
— literature reading happens again at Stage 19 after early results land.

Recommended first pass:
- 2 survey or benchmark papers
- 5 recent SOTA papers
- 3 foundation papers
- 3 analysis, negative, or ablation papers
- 3 closest baseline papers

Required artifact: `LITERATURE_MAP.md`

### 2.5 Problem Reframing Loop

If the literature map suggests the problem-as-stated is the wrong cut, reframe before
selecting. Common triggers: the named problem is a symptom of a deeper one; the same
mechanism solves a broader class; the benchmark conflates two distinct phenomena.

Required artifact: `PROBLEM_REFRAMING.md`

Required ending: `KEEP | REFRAME | SPLIT`

### 3. Problem Taste / Problem Selection

Score candidates by importance, audience, concreteness, novelty, feasibility, benchmark
availability, baseline ceiling risk, expected headroom, diagnostic clarity, and paper
survivability if the method fails or ties.

Required artifact: `PROBLEM_SELECTION.md`

Required ending: `PROCEED | NARROW | RETHINK`

### 4. Assumption Ledger

List every assumption the proposed work depends on: data availability, mechanism plausibility,
baseline behaviour, evaluator validity, scale regime, infrastructure cost, time horizon. Each
assumption is tagged `factual` (citable to evidence) or `working` (must be tested or accepted
as a risk). Downstream artifacts must trace any "is/will/always" claim to this ledger.

Required artifact: `ASSUMPTION_LEDGER.md`

### 5. Abstract Task / Mechanism Framing

Strip the problem to its abstract form: input space, output space, decision structure,
information bottleneck, primary failure modes, mechanism families that could solve it.
This is the calibration substrate Innovation Spine reads when generating candidates.

Required artifact: `ABSTRACT_TASK_MECHANISM.md`

### 6. Artifact-triggered Data / Env / Benchmark Audit

Fires **only when** a concrete data set, environment, simulator, reward function, evaluator,
or train/val/test split actually exists or has been fetched. Auditing things that do not
yet exist is forbidden. The audit checks: prediction target, inputs, labels, units,
modalities, vendors, devices, protocols, domains, splits, confounders, leakage, shortcut
features, label/device confounds, evaluator validity.

Required artifact: `ARTIFACT_AUDIT.md` (re-emitted whenever the audited artifact changes)

### 7. Baseline Ceiling / Headroom Audit

Estimate the ceiling of simple strong baselines and whether the benchmark has real headroom.
Consider zero-shot, few-shot, Best-of-N, confidence-rank, reranking, DINGO-style search,
vanilla GRPO/PPO/RL, vanilla SFT, ERM, modality-specific, majority-domain, heuristic, and
public SOTA baselines.

Headroom is a **reference**, not a veto. A low ceiling does not block innovation; it
calibrates how loud a claim can later be.

Required artifact: `BASELINE_CEILING.md`

### 8. Mechanism Invention Loop

Generate 5–10 candidate mechanisms aimed at the abstract task. Rate each by novelty,
feasibility, and falsifiability. Do **not** converge inside this loop — convergence is
gated to Stage 11. Codex is in **collaborative mode** here: no veto, only adds candidates,
identifies blind spots, suggests alternatives.

See `innovation-loops.md` §2 for the full procedure.

Required artifact: `MECHANISM_IDEATION.md`

### 9. Analogy / Cross-pollination Loop

For each top candidate from Stage 8, identify ≥1 analogous solved problem from another
field. Map what transfers, what does not, and what new constraint the transfer introduces.
Bold analogies welcome. Codex collaborative.

See `innovation-loops.md` §3.

Required artifact: `ANALOGY_TRANSFER.md`

### 10. Algorithm Sketch Tournament

Write a 1-page algorithm sketch per top candidate. Run round-robin pairwise comparison
on the criteria: diagnosability of failure, mechanism fidelity, falsifiability, integration
cost. Pick a winner but **keep the alternates** — they may revive in Stage 18.5.

See `innovation-loops.md` §4.

Required artifact: `ALGORITHM_TOURNAMENT.md`

Required ending (optional): `TENTATIVE_PREFERRED_SKETCH_ID + ALTERNATES + ABSTAIN_REASONS`
(non-binding — Stage 11 reviews and may revise)

### 11. Hypothesis-Mechanism-Benchmark-Control Matrix

Codex switches back to **adversarial mode**. Every committed experiment must specify
hypothesis, mechanism, target failure mode, benchmark rationale, highest-headroom regime,
required controls, possible confounders, positive signal, and falsifying signal.

Required artifact: `CONTROL_DESIGN.md`

### 12. Null-result Contract

Before running, define what positive, negative, tied, noisy, or chaotic outcomes mean.
If a failure cannot distinguish mechanism failure, benchmark saturation, implementation
bug, metric mismatch, missing control, task ontology error, or convergence issue, the
experiment is invalid — redesign before running.

Required artifact: `NULL_RESULT_CONTRACT.md`

### 13. Progressive Component / Minimal Mechanism Bundle

Complex systems are allowed but must be validated progressively. Default: one component
at a time. When components are genuinely synergistic and cannot be tested in isolation,
the smallest **mechanism-preserving bundle** is acceptable — the artifact must justify
why the bundle is indivisible.

Each component (or bundle) declares: target failure mode, expected signal, control,
null-result interpretation, rollback condition, interaction risk.

Required artifact: `COMPONENT_BUNDLE_LADDER.md`  *(v1.0 alias: `COMPONENT_LADDER.md`)*

### 14. Algorithmic Formalization

Before official experiments, write the algorithm in formal terms: pseudocode, loss /
reward / objective, optimisation step, decision rule, evaluation predicate. This is the
contract the plan-code audit reads against.

Required artifact: `ALGORITHMIC_FORMALIZATION.md`

### 15. Plan-Code Consistency Loop

Codex reviews the implementation as a semantic auditor. Checks whether training/eval
scripts, configs, launch scripts, datasets, splits, metrics, baselines, controls, and
ablations match the v1.3 contract artifacts (FORMALIZATION, COMPONENT_BUNDLE_LADDER,
ABSTRACT_TASK_MECHANISM, CONTROL_DESIGN, NULL_RESULT_CONTRACT, ASSUMPTION_LEDGER).

This is a **loop**: audit → fix → re-audit until verdict is `MATCHES_PLAN` or scoped
`PARTIAL_MISMATCH` with documented justification.

Required artifact: `PLAN_CODE_AUDIT.md`

Required ending: `MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR`

### 16. Cheapest Valid Diagnostic

Design the cheapest run that could **falsify the central claim** — not the smallest run.
Tiny subset, one seed, hard subset, highest-headroom regime, oracle upper bound, tiny
overfit, known baseline reproduction, metric sanity, or control-only experiment. The
diagnostic must operate in a regime where the mechanism could in principle manifest.

Required artifact: `DIAGNOSTIC_EXPERIMENT_PLAN.md`  *(v1.0 alias: `TINY_RUN_PLAN.md`)*

### 17. Diagnostic Run Audit

Run the diagnostic and audit its outputs against the plan. A run that merely executes is
insufficient; it must run the intended script, dataset, split, metric, baseline/component,
config, and produce logs sufficient for null-result diagnosis.

**G12 check (regime-aware):** if the run failed in a regime that violates the mechanism's
necessary preconditions (e.g., scale-dependent emergent behaviour ablated), do not reject
the mechanism — recommend redesign to a regime where the mechanism could manifest.

Required artifacts: `DIAGNOSTIC_RUN_REPORT.md` + `DIAGNOSTIC_RUN_AUDIT.md`
*(v1.0 aliases: `TINY_RUN_REPORT.md` + `TINY_RUN_AUDIT.md`)*

Required ending: `PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT`

### 18. Result Interpretation Loop

After every diagnostic or scale-up run, interpret before launching the next. The next
experiment must depend on the current interpretation. Honest tie/failure framing is
required if NULL_RESULT_CONTRACT triggered such an outcome.

Required artifact: `RESULT_INTERPRETATION.md`

### 18.5 Failure-to-Innovation Loop

When results tie or fail, re-examine ASSUMPTION_LEDGER for falsified entries; ask which
new mechanism the failure suggests; consider reviving alternates from ALGORITHM_TOURNAMENT.
Codex collaborative. Anti-pattern: presenting the new mechanism as a pre-planned hypothesis
(violates G17).

See `innovation-loops.md` §5.

Required artifact: `FAILURE_TO_INNOVATION.md`

### 19. Re-read Literature Loop

After early diagnostic results, re-read the closest papers for the now-visible failure
mode, baseline ceiling, hard subset, controls, benchmark headroom, and mechanism
assumptions. Targeted /research-lit calls with question-specific queries.

See `innovation-loops.md` §6.

Required artifact: `LITERATURE_REREAD_NOTE.md`

### 20. Scale-up Decision

Scale only after the relevant Validation prerequisites are satisfied: artifact audit (when
applicable), baseline ceiling, controls, null-result contract, plan-code audit verdict,
diagnostic-run audit verdict. For COMMITMENT mode or risk≥4, also requires
`HUMAN_DECISION_NOTE.md` (G15).

Required artifact: `SCALEUP_DECISION.md`

Required ending: `PROCEED | HOLD | REDESIGN | HUMAN_DECISION_REQUIRED`

### 21. Result-to-Claim Construction

Build paper claims as `claim → evidence → control → scope → limitation`. Downgrade claims
when evidence is partial. Each claim cites the specific artifact and run id that supports it.

Required artifact: `CLAIM_CONSTRUCTION.md`

### 22. Tie / Negative Result / Reframing Strategy

If the method ties or fails, do not force a positive story. Evaluate benchmark diagnosis,
baseline ceiling analysis, failure taxonomy, negative result, regime map, evaluation protocol,
task ontology contribution, or controlled reproduction.

If a result is being reframed post-hoc, label it explicitly as "exploratory finding, not
pre-planned hypothesis" in CLAIM_CONSTRUCTION.md and the paper (G17).

Stop if no contribution remains.

Required artifact: `NEGATIVE_RESULT_STRATEGY.md`

### 23. Reviewer Red-team Loop

Run a skeptical reviewer attack on importance, novelty, task definition, benchmark validity,
baselines, controls, null-result interpretation, evidence, overclaiming, reproducibility, and
limitations. This is a **loop**: review → fix → re-review until issues are addressed or
explicitly accepted as residual risk. Calls ARIS `/auto-review-loop`.

Required artifact: `RED_TEAM_REVIEW.md`

### 24. Paper Writing / Paper Improvement Loop

Calls ARIS `/paper-writing` which transitively invokes `/auto-paper-improvement-loop`,
`/paper-claim-audit`, `/citation-audit`. Refuses to start without `CLAIM_CONSTRUCTION.md`
(G16, G18).

Required artifact: `PAPER_IMPROVEMENT_LOG.md` + `paper/`

### 25. Human Decision / Next Loop

Before major transitions, write what is believed, what evidence supports it, what remains
uncertain, what the agent recommends next, and what requires human judgment.

Required artifact: `HUMAN_DECISION_NOTE.md`

Required ending: `PROCEED | NARROW | REDESIGN | RE-READ | CHANGE BENCHMARK | STOP | HUMAN_DECISION_REQUIRED`

## Hard Gates (v1.3)

Each gate is enforced by the orchestrator and (where applicable) inline by individual
skills. Gates parse verdict lines, not file presence. Producers emit v1.3 artifact names;
consumers accept either v1.0 or v1.3 names (prefer v1.3 if both exist).

```
G0  IF MODE_ROUTING.md absent:
      • Low-risk single-stage commands → orchestrator infers mode (default EXPLORATION,
        risk=1) and writes a stub MODE_ROUTING.md. Continue without blocking.
      • High-risk transitions (scale-up, paper writing, public release, official experiment
        planning) → if mode/risk cannot be inferred from prior artifacts or inline flag,
        block; require explicit Stage 0 routing or `— mode:` flag.

G1  IF method commitment, official experiment planning, or GPU run starts
    AND PROBLEM_SELECTION.md absent
    THEN block; require Stage 3.
    Mechanism brainstorming (Stages 8/9/10) is allowed in mode = EXPLORATION/INNOVATION
    before final problem selection, provided outputs are clearly marked as candidates and
    assumptions are recorded in ASSUMPTION_LEDGER.md.

G2  IF a downstream artifact contains "is/will/always" claims not traceable to
    ASSUMPTION_LEDGER.md
    THEN demote wording to "assume/hypothesise" or block until ledger entry added
    UNLESS claim cites external evidence.

G3  IF Stage 11+ (commitment) starts AND ABSTRACT_TASK_MECHANISM.md absent
    THEN block.
    Stage 8/9/10 mechanism invention may run without ABSTRACT_TASK_MECHANISM.md when
    mode = EXPLORATION/INNOVATION, candidates are marked as such, and assumptions go
    to ASSUMPTION_LEDGER.md.

G4  IF a stage references data/env/benchmark THAT does not yet exist
    THEN do NOT force ARTIFACT_AUDIT.md.
    Audit fires once the artifact is observable.   (Replaces v1.0 "data audit must occur
    early.")

G5  IF claim contains "outperforms / beats / improves over" baseline
    THEN BASELINE_CEILING.md required
    UNLESS mode = EXPLORATION AND no paper claim is being made.

G6  IF method commitment (Stage 11+) starts AND none of {MECHANISM_IDEATION,
    ANALOGY_TRANSFER, ALGORITHM_TOURNAMENT} exist
    THEN block; require ≥1 innovation artifact
    UNLESS user explicitly invokes single-method confirmatory mode.

G7  IF Stage 16/17 produces a result feeding paper claims AND CONTROL_DESIGN.md absent
    THEN block claim use; results are exploratory only.   (No exception.)

G8  IF Stage 16/17 starts as diagnostic/confirmatory AND NULL_RESULT_CONTRACT.md absent
    THEN block
    UNLESS run is explicitly marked "exploratory probe" (no paper claim allowed).

G9  IF official (full-system) run with a new composed method starts
    AND COMPONENT_BUNDLE_LADDER.md absent
    THEN block; require at least a short COMPONENT_BUNDLE_LADDER.md (a single rung is
    acceptable as long as it justifies why the components are bundled and what each
    contributes).
    UNLESS the run is a baseline reproduction or a single-component run with no new
    composed mechanism — then no COMPONENT_BUNDLE_LADDER.md is required.

G10 IF scale-up to official experiments AND ALGORITHMIC_FORMALIZATION.md absent
    THEN block
    UNLESS mode = EXPLORATION AND no scale-up requested.

G11 IF PLAN_CODE_AUDIT.md verdict = CRITICAL_MISMATCH
    THEN block scale-up; loop fix → re-audit until MATCHES_PLAN or scoped PARTIAL_MISMATCH.
    No exception. ERROR (Codex unavailable, audit could not complete) is advisory at
    diagnostic / sanity run (proceed, surface the reason) and blocks at scale-up pending
    explicit human acknowledgement.

G12 IF a tiny / diagnostic run failed in a regime that violates the mechanism's necessary
    preconditions
    THEN do NOT reject the mechanism; require diagnostic redesign to a regime where the
    mechanism could in principle manifest.   (Replaces v1.0 "tiny-run failure → kill idea.")

G13 IF experiment uses test set anywhere in tuning/selection
    THEN block; require held-out test isolation.   (No exception.)

G14 IF NULL_RESULT_CONTRACT triggered tie/failure AND RESULT_INTERPRETATION /
    CLAIM_CONSTRUCTION contains positive framing
    THEN block; require honest tie/failure framing or invoke Stage 22.   (No exception.)

G15 IF scale-up requested AND (mode = COMMITMENT OR risk_score ≥ 4)
    THEN HUMAN_DECISION_NOTE.md required before SCALEUP_DECISION = PROCEED.
    No exception.

G16 IF Stage 24 starts AND CLAIM_CONSTRUCTION.md absent
    THEN block.   (No exception.)

G17 IF a result is framed post-hoc as "what we predicted"
    THEN block; require explicit "exploratory finding, not pre-planned hypothesis"
    labelling in CLAIM_CONSTRUCTION.md and the paper.   (No exception.)

G18 IF /paper-writing is invoked and CLAIM_CONSTRUCTION.md absent
    THEN refuse start (inline guard in paper-writing/SKILL.md).   (No exception.)

G19 IF stage = 20 (scale-up), 24 (paper), or any "public release" transition
    THEN HUMAN_DECISION_NOTE.md required.   (No exception.)
```

v1.0 gates "tiny run before scale-up always" and "data audit before any other stage" are
intentionally **removed** in v1.3, replaced by G11/G12 (regime-aware) and G4 (artifact-triggered).

## Claude + Codex Debate Nodes

Use debate at these stages (commitment/validation, where Codex is **adversarial**):

- Stage 3: Problem Selection
- Stage 2: Literature Map (when controversial)
- Stage 6: Artifact-triggered Audit
- Stage 7: Baseline Ceiling / Headroom
- Stage 11: Hypothesis-Mechanism-Benchmark-Control
- Stage 12: Null-result Contract
- Stage 13: Component / Bundle Ladder
- Stage 14: Algorithmic Formalization
- Stage 15: Plan-Code Consistency Audit
- Stage 17: Diagnostic Run Audit
- Stage 21: Result-to-Claim Construction
- Stage 23: Reviewer Red-team

For Stages 8, 9, 10, 18.5 (Innovation), Codex switches to **collaborative mode** — see
`innovation-loops.md` §7.

Debate protocol:

```text
Claude: propose
Codex: critique
Claude: revise
Codex: final objections
Claude: consensus decision
Human: approve / redirect
```

At most two rounds. End with exactly one:

- `CONSENSUS`
- `DISAGREEMENT`
- `HUMAN_DECISION_REQUIRED`

## Reviewer Defaults

For ORBIT, Codex review defaults are:

- `model = gpt-5.5`
- `reasoning_effort = xhigh`
- sandbox disabled, equivalent to `sandbox_mode = danger-full-access`
- reviewer role: independent semantic auditor (commitment gates) /
  collaborative innovator (innovation loops, see `innovation-loops.md` §7)

Reviewer independence is mandatory at adversarial stages: pass file paths and review
objectives, not executor summaries or leading interpretations.

## v1.0 → v1.3 Migration Appendix

### Renamed artifacts (consumers accept either name)

| v1.0 name | v1.3 name | Notes |
|---|---|---|
| `COMPONENT_LADDER.md` | `COMPONENT_BUNDLE_LADDER.md` | Generalised: single component OR smallest mechanism-preserving bundle |
| `TINY_RUN_PLAN.md` | `DIAGNOSTIC_EXPERIMENT_PLAN.md` | Cheapest valid diagnostic, not always tiny |
| `TINY_RUN_REPORT.md` | `DIAGNOSTIC_RUN_REPORT.md` | Same role, regime-aware |
| `TINY_RUN_AUDIT.md` | `DIAGNOSTIC_RUN_AUDIT.md` | Same verdict tokens (`PASS \| FIX_BEFORE_GPU \| REDESIGN_EXPERIMENT`) |

### Stage renames (verdict tokens preserved)

| v1.0 stage | v1.3 stage | Notes |
|---|---|---|
| 0A Seed Framing | 1 | Same role |
| 1 Literature Map | 2 | Now explicitly a loop |
| 0B Problem Selection | 3 | Verdict tokens unchanged |
| 2 Task Ontology / Data Audit | 4 + 5 + 6 | Split into Assumption Ledger + Abstract Task / Mechanism + Artifact-triggered Audit |
| 3 Baseline Ceiling | 7 | Now explicitly a reference, not a veto |
| 4 HMBC Matrix | 11 | Same role |
| 5 Null-result Contract | 12 | Same role |
| 6 Component Ladder | 13 | Generalised to bundle |
| 7 Min Diagnostic Plan | 16 | "Cheapest valid diagnostic" |
| 7.5 Plan-Code Audit | 15 | Now an explicit loop; same verdict tokens |
| 8 Tiny Run | (folded into 16/17) | Diagnostic, not necessarily tiny |
| 8.5 Tiny Run Audit | 17 | Same verdict tokens; G12 added |
| 9 Result Interpretation | 18 | Same role |
| 10 Re-read Literature | 19 | Now explicitly a loop |
| 11 Scale-up | 20 | + G15 + G19 (HUMAN_DECISION_NOTE) |
| 12 Result-to-Claim | 21 | Same role |
| 13 Tie / Negative | 22 | + G17 anti-post-hoc reframing |
| 14 Reviewer Red-team | 23 | Now an explicit loop; calls ARIS `/auto-review-loop` |
| (new) | 24 | Paper writing — calls ARIS `/paper-writing` chain |
| 15 Human Decision | 25 | Same verdict tokens |

### Manual migration (no alias)

`TASK_ONTOLOGY.md` is superseded by Stages 0/1/4/5 (`MODE_ROUTING.md`, `SEED_FRAMING.md`,
`ASSUMPTION_LEDGER.md`, `ABSTRACT_TASK_MECHANISM.md`). Existing `TASK_ONTOLOGY.md` content
should be split manually:

- mode flag → `MODE_ROUTING.md`
- framing prose → `SEED_FRAMING.md`
- inputs/assumptions block → `ASSUMPTION_LEDGER.md`
- task/mechanism block → `ABSTRACT_TASK_MECHANISM.md`

### New artifacts (no v1.0 ancestor)

`MODE_ROUTING.md`, `PROBLEM_REFRAMING.md`, `ASSUMPTION_LEDGER.md`,
`ABSTRACT_TASK_MECHANISM.md`, `ARTIFACT_AUDIT.md`, `MECHANISM_IDEATION.md`,
`ANALOGY_TRANSFER.md`, `ALGORITHM_TOURNAMENT.md`, `ALGORITHMIC_FORMALIZATION.md`,
`FAILURE_TO_INNOVATION.md`, `PAPER_IMPROVEMENT_LOG.md`.

### Compat window

Accept-either parsing is supported for one major version. Removal of v1.0 aliases is
deferred to v2.0.
