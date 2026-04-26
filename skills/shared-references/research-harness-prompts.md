# ORBIT Harness Prompts — v1.3

> **v1.3 — supersedes v1.0 (0A–15).** Use these prompts as canonical stage harnesses.
> Skills may add file paths, output paths, and project-local constraints, but should
> preserve the scientific checks, the verdict tokens, and (for innovation stages) the
> Codex collaborative-mode delegation. See the v1.0 → v1.3 alias appendix at the end.
>
> Reviewer routing default: Codex MCP, `model = gpt-5.5`, `reasoning_effort = xhigh`,
> sandbox `danger-full-access` (see `reviewer-routing.md`).

## 0. Mode & Risk Routing

```text
You are the orchestrator's first action. Classify the user's input shape and write
MODE_ROUTING.md before running anything else.

Inputs to read:
- The user's request (a slash-command argument, a research direction, an artifact path,
  or a description of an in-flight project).
- Whatever artifacts already exist under orbit-research/ — they constrain the routing.
- Any explicit `— mode:` or `— risk:` flag passed inline.

Decide:
1. Mode (one of):
   - EXPLORATION — broad area, unclear problem, no committed artifact in hand.
   - INNOVATION — concrete problem, no committed method.
   - COMMITMENT — committed method, official experiments, scale-up, paper writing.
2. Risk score (one of 1, 2, 3, 4, 5):
   - 1–2 — local, reversible, no GPU spend, no public release.
   - 3 — non-trivial GPU spend, internal results.
   - 4 — official benchmark runs, paper-bearing claims.
   - 5 — public release, submission, high-cost irreversible commitment.
3. Which stages should run next, mapped from the user's input shape:
   - broad area               → 1 → 2 → 2.5 → 3
   - concrete idea no artifact → 4 → 5 → 7 → 8/9/10
   - concrete data in hand    → 6 → 7 → 11+
   - designing new method     → 4 → 5 → 8 → 9 → 10
   - implementing experiments → 11 → 12 → 13 → 14 → 15 → 16
   - running experiments      → 16 → 17 → 18
   - results failed/surprised → 18 → 18.5 → 19

Write MODE_ROUTING.md ending with one canonical line of the form:
    EXPLORATION | INNOVATION | COMMITMENT + risk: <1-5>

Do not force every stage on every request. Run the minimum needed to satisfy the gates
that apply at this risk level.

When MODE_ROUTING.md is missing and the command is low-risk single-stage work, write a
stub (default EXPLORATION, risk=1) and continue without blocking. Block only at high-risk
transitions when neither prior artifacts nor an inline flag give enough information.
```

## 1. Seed Framing

```text
You are given a research area, not yet a concrete research problem.

Do not propose final methods yet.
Do not commit to a benchmark yet.
Do not write an experiment plan yet.

First produce a Seed Framing brief:
1. What is the research area?
2. What are the user's constraints: compute, data, timeline, expertise, and publication target?
3. What are 3-5 initial research questions?
4. What are the key terms, subfields, and adjacent areas to search?
5. What kinds of papers must be read first: survey, benchmark, recent SOTA, foundation, analysis/negative/ablation, and closest baseline papers?

Output a search-oriented brief, not a proposal. Write SEED_FRAMING.md.
```

## 2. Question-driven Literature Map

```text
Read papers as a research scientist, not as a summarizer. This stage is a LOOP — it fires
again at Stage 19 after early results land.

For each important paper, extract:
1. main claim;
2. mechanism;
3. benchmark;
4. strongest evidence;
5. weakest assumption;
6. missing control;
7. likely failure regime;
8. claim-evidence gap;
9. follow-up question for our project.

Then synthesize:
- field consensus;
- unresolved bottlenecks;
- overclaimed assumptions;
- benchmark saturation risks;
- missing controls across the field;
- promising underexplored regimes;
- candidate research problems.

Do not generate final methods yet. Generate candidate problems. Write LITERATURE_MAP.md.
```

## 2.5 Problem Reframing Loop

```text
You have a candidate problem and a literature map. Before selecting, ask whether the
problem-as-stated is the wrong cut.

Triggers to reframe:
- The named problem is a symptom of a deeper one.
- The same mechanism solves a broader class.
- The benchmark conflates two distinct phenomena.
- A synonym in another subfield already has solid solutions, suggesting the real cut is
  different.
- The user's framing assumes a constraint that is not actually load-bearing.

Decide one of:
- KEEP the problem as stated.
- REFRAME to a different cut (write the new framing in 1 paragraph).
- SPLIT the problem into 2+ separable sub-problems (write each as 1 paragraph).

End with one of: KEEP | REFRAME | SPLIT. Write PROBLEM_REFRAMING.md.
```

## 3. Problem Taste / Problem Selection

```text
Now that the literature map exists, select the most promising concrete research problem.

For each candidate problem, evaluate:
1. importance;
2. audience;
3. concreteness;
4. novelty;
5. feasibility with our data, compute, time, and expertise;
6. benchmark availability;
7. baseline ceiling risk;
8. expected headroom;
9. diagnostic clarity;
10. paper value if the method fails or ties.

Do not select a problem only because it sounds novel.

Select the problem with the best combination of importance, feasibility, headroom,
diagnostic clarity, and paper survivability.

End with one of: PROCEED | NARROW | RETHINK. Write PROBLEM_SELECTION.md.
```

## 4. Assumption Ledger

```text
List every assumption the proposed work depends on. Treat assumptions as first-class
objects — never let them silently become facts.

For each assumption, record:
1. ID (A1, A2, ...).
2. The assumption itself, in one declarative sentence.
3. Tag: `factual` (citable to evidence — include the citation) or `working` (not yet
   tested; must be acknowledged as a risk).
4. If `working`: which stage / experiment would test it, and what falsification looks like.
5. If `factual`: source citation.

Cover at minimum:
- data availability and quality;
- mechanism plausibility (why we think the proposed mechanism could work);
- baseline behaviour (what the simplest baselines achieve);
- evaluator validity (does the metric measure what we claim);
- scale regime (what compute / data scale is required for the mechanism to manifest);
- infrastructure cost;
- time horizon.

Downstream artifacts will be required to trace any "is/will/always" claim back to a row
in this ledger (G2). Write ASSUMPTION_LEDGER.md.
```

## 5. Abstract Task / Mechanism Framing

```text
Strip the problem to its abstract form. This is the calibration substrate the Innovation
Spine reads when generating mechanism candidates.

Define:
1. Input space — what does the model see, formally (shape, distribution, modality)?
2. Output space — what does the model produce (decision, label, sequence, ranking)?
3. Decision structure — single-step, multi-step, sequential, hierarchical, planning?
4. Information bottleneck — where in the pipeline does information degrade or get lost?
5. Primary failure modes — what goes wrong in current solutions?
6. Mechanism families that could plausibly solve it — list 3–5 mechanism families
   (representation learning, search/planning, reward shaping, retrieval, distillation,
   verifier-based, ensemble, etc.) with one line each on why they apply.

This is not a method commitment. It is the abstract substrate. Stage 8 will use this to
seed mechanism invention. Write ABSTRACT_TASK_MECHANISM.md.
```

## 6. Artifact-triggered Data / Env / Benchmark Audit

```text
Run this audit ONLY when a concrete data set, environment, simulator, reward function,
evaluator, or train/val/test split actually exists or has been fetched. If the artifact
does not yet exist, do NOT force this audit — return without writing the file. Re-emit
the audit whenever the audited artifact changes.

When the artifact exists, define:
1. prediction target;
2. inputs;
3. labels;
4. data units: patient, eye, visit, image, sequence, report, episode, trajectory;
5. modalities;
6. vendors and devices;
7. acquisition / generation protocols;
8. domains;
9. train / validation / test splits (and whether the test split has been touched);
10. confounders.

Actively search for category errors:
- vendor treated as modality;
- modality treated as domain;
- dataset source treated as clinical or task label;
- binary split hiding a multi-modal or multi-domain problem;
- disease / outcome label confounded with device or protocol;
- patient or episode leakage across splits;
- shortcut features that make the benchmark artificial;
- evaluator reward hacking opportunities.

If ontology is ambiguous, stop and produce:
- concern;
- why it matters;
- possible fixes;
- recommended next step.

Write ARTIFACT_AUDIT.md. Do not block on the audit before the artifact exists; this
replaces the v1.0 "data audit must occur early" rule.
```

## 7. Baseline Ceiling / Headroom Audit

```text
Estimate the ceiling of simple strong baselines and whether the benchmark has real
headroom. Headroom is a REFERENCE, not a veto — a low ceiling does not block innovation;
it calibrates how loud a claim can later be.

Identify the relevant simple strong baselines:
- zero-shot prompting;
- few-shot prompting;
- Best-of-N sampling;
- confidence-rank selection;
- reranking baseline;
- DINGO-style search or selection;
- vanilla GRPO / PPO / RL;
- vanilla SFT;
- ERM baseline;
- modality-specific baseline;
- majority-domain baseline;
- heuristic or rule-based baseline;
- known public SOTA if available.

Answer:
1. What is the simplest strong baseline?
2. What is its known or estimated ceiling?
3. Is the benchmark already saturated?
4. Where is the largest remaining headroom?
5. Which subset, split, or regime should be tested first?
6. Which baseline must run before the proposed method?
7. If the baseline is too strong, should we change benchmark, metric, split, target regime,
   or paper claim?

The proposed method does not need to beat the strongest baseline to be valuable; it needs
to teach us something the baseline cannot. Write BASELINE_CEILING.md.
```

## 8. Mechanism Invention Loop

```text
You are at Stage 8. Codex is in COLLABORATIVE mode. Do NOT converge inside this loop.

Inputs:
- ABSTRACT_TASK_MECHANISM.md
- ASSUMPTION_LEDGER.md
- LITERATURE_MAP.md

Procedure: see skills/shared-references/innovation-loops.md §2 for the full template.

Brief: generate 5–10 candidate mechanisms aimed at the abstract task. Aim for breadth —
include at least one obvious, one borrowed-from-another-field, one minimal, one
complex/composite, and one wild card. Score each on novelty / feasibility / falsifiability
(1–5 each). Then invoke Codex (collaborative-mode template, see innovation-loops.md §7.1)
which APPENDS additions; it does NOT veto Claude's candidates.

Output: MECHANISM_IDEATION.md with all candidates visible (none pruned), a tentative
top-3 marked for Stage 9 expansion, and a "Codex collaborative additions" section.

Anti-pattern: do not pick a single winner here. Convergence is gated to Stage 11.
```

## 9. Analogy / Cross-pollination Loop

```text
You are at Stage 9. Codex is in COLLABORATIVE mode.

Inputs:
- MECHANISM_IDEATION.md (top-3 candidates from Stage 8)
- 1–3 analogous-domain papers from /research-lit if needed.

Procedure: see skills/shared-references/innovation-loops.md §3 for the full template.

Brief: for each top candidate, name ≥1 analogous solved problem from another field. Map
*what transfers*, *what does not transfer*, *what new constraint the transfer introduces*.
Bold analogies welcome. Codex collaborative additions append more analogies.

Output: ANALOGY_TRANSFER.md with the mapping table, hybrid mechanisms suggested by the
analogies, and a Codex collaborative additions section.

Anti-pattern: do not declare an analogy "wrong" if it does not transfer cleanly. The
partial transfer is often the most informative outcome — label what does and does not
transfer rather than rejecting.
```

## 10. Algorithm Sketch Tournament

```text
You are at Stage 10. Codex is in COLLABORATIVE mode for sketch quality, ADVERSARIAL for
tournament adjudication (the one place inside innovation loops where Codex may challenge
Claude's pairwise picks).

Inputs:
- MECHANISM_IDEATION.md, ANALOGY_TRANSFER.md
- Optional: hybrid candidates synthesised in Stage 9.

Procedure: see skills/shared-references/innovation-loops.md §4 for the full template.

Brief: write a 1-page algorithm sketch per top candidate (3–5 sketches total). Each sketch:
input/output signature, core update rule (pseudocode acceptable), loss / reward / objective,
decision rule, evaluator predicate, integration cost estimate.

Then run a round-robin pairwise comparison on four criteria:
- Diagnosability of failure
- Mechanism fidelity
- Falsifiability
- Integration cost

Tally pairwise wins; mark a TENTATIVE_PREFERRED_SKETCH_ID for Stage 11 commitment review.
This is **not a final method commitment** — Stage 10 selects candidates for Stage 11 HMBC
review, it does not bind the project to a method. KEEP ALTERNATES with their pairwise
scores — they may revive in Stage 11 if HMBC exposes a problem with the tentative pick,
or in Stage 18.5 if the tentative pick survives Stage 11 but fails downstream.

Output: ALGORITHM_TOURNAMENT.md ending with one canonical line:
    TENTATIVE_PREFERRED_SKETCH_ID + ALTERNATES + ABSTAIN_REASONS
```

## 11. Hypothesis-Mechanism-Benchmark-Control Matrix

```text
You are at Stage 11. Codex switches BACK to ADVERSARIAL mode for all stages from here on.

Before writing an experiment plan, fill the Hypothesis-Mechanism-Benchmark-Control Matrix.

For each proposed experiment, specify:
1. Hypothesis: What scientific claim is being tested?
2. Mechanism: What mechanism should make the method work? (Cite the candidate from
   MECHANISM_IDEATION / ALGORITHM_TOURNAMENT.)
3. Target failure mode: What failure mode of existing methods does this mechanism address?
4. Benchmark: Why should this benchmark expose the mechanism?
5. Highest-headroom regime: In which subset or regime should the mechanism help most?
6. Required controls: Which controls isolate the mechanism?
7. Possible confounders: What else could explain success or failure?
8. Positive signal: What result would support the hypothesis?
9. Falsifying signal: What result would weaken or falsify the hypothesis?

Reject experiments where hypothesis, mechanism, benchmark, and controls could all be wrong
at the same time.

Write CONTROL_DESIGN.md. Do not proceed with non-diagnostic experiments.
```

## 12. Null-result Contract

```text
Before running the experiment, write a Null-Result Contract.

Answer:
1. If the result is positive, what exactly do we learn?
2. If the result is negative, what exactly do we learn?
3. If the method ties the control, what exactly do we learn?
4. If results are noisy, unstable, or chaotic, what are the top possible causes?
5. Which causes must this experiment be able to distinguish?
   - mechanism failure;
   - benchmark saturation;
   - baseline too strong;
   - implementation bug;
   - evaluation metric mismatch;
   - missing control;
   - data/task ontology problem;
   - hyperparameter or convergence issue.
6. What follow-up diagnostic experiment would distinguish these causes?
7. What is the stop condition?

If the null result only says:
"We do not know whether the mechanism, benchmark, implementation, or evaluation failed,"
then the experiment is invalid. Redesign before running.

Write NULL_RESULT_CONTRACT.md.
```

## 13. Progressive Component / Minimal Mechanism Bundle

```text
Bold mechanisms and complex systems are welcome, but validate them progressively.

Default: one component at a time. When components are genuinely synergistic and cannot
be tested in isolation, the smallest MECHANISM-PRESERVING BUNDLE is acceptable — but
the artifact must justify *why* the bundle is indivisible (not just convenient).

Start with:
Component 0: simplest strong baseline

Then add one component (or one minimal mechanism-preserving bundle) at a time.

For each component or bundle, specify:
1. Component / bundle name: What is being added?
2. Indivisibility justification (bundles only): Why can't this be tested as separate
   components? What synergy would be destroyed?
3. Target failure mode: What problem does this component / bundle address?
4. Expected signal: What metric, subset, or behavior should improve?
5. Control: What comparison isolates this component / bundle?
6. Null-result interpretation: If it does not help, what does that mean?
7. Rollback condition: When should this be removed or redesigned?
8. Interaction risk: Could this component hide or confound the effect of another?

Do not run the full system until each major component (or bundle) has shown at least one of:
- measurable performance gain;
- attribution value;
- diagnostic insight.

A complex method is allowed only if its complexity is progressively justified.

Write COMPONENT_BUNDLE_LADDER.md (v1.0 alias: COMPONENT_LADDER.md).
```

## 14. Algorithmic Formalization

```text
Before official experiments, formalize the algorithm. This is the contract the plan-code
audit reads against.

Provide:
1. Pseudocode at function-level granularity (not high-level prose).
2. Loss / reward / objective formula.
3. Optimisation step (the exact update rule).
4. Decision rule (how outputs are selected at inference).
5. Evaluation predicate (what counts as "correct" for the metric).
6. Hyperparameter ranges and their interpretations.
7. Inputs / outputs of every component (with shapes, distributions, modalities).
8. Cross-references to ASSUMPTION_LEDGER entries each design choice depends on.

The formalization must be detailed enough that a fresh reader could re-implement the
algorithm without consulting Claude. It must also be tight enough that Codex can verify
code against it without ambiguity.

Write ALGORITHMIC_FORMALIZATION.md.
```

## 15. Plan-Code Consistency Loop

```text
You are not reviewing this code for syntax or style.

You are reviewing whether the implementation faithfully matches the v1.3 research contract.

This is a LOOP: audit → fix → re-audit until verdict is MATCHES_PLAN or scoped
PARTIAL_MISMATCH with documented justification.

Compare the code against:
1. ASSUMPTION_LEDGER.md
2. ABSTRACT_TASK_MECHANISM.md
3. MECHANISM_IDEATION.md (if relevant — which candidate is being implemented?)
4. ANALOGY_TRANSFER.md (if relevant)
5. ALGORITHM_TOURNAMENT.md (which sketch is being implemented?)
6. CONTROL_DESIGN.md
7. NULL_RESULT_CONTRACT.md
8. COMPONENT_BUNDLE_LADDER.md (or v1.0 COMPONENT_LADDER.md)
9. ALGORITHMIC_FORMALIZATION.md
10. DIAGNOSTIC_EXPERIMENT_PLAN.md
11. FINAL_PROPOSAL.md / EXPERIMENT_PLAN.md (legacy proposal/plan artifacts)
12. Training / eval scripts, configs, launch scripts, data loaders, result parsers.

Check whether the scripts actually implement the intended experiments.

Focus on:
- Are the correct baselines implemented?
- Are the required controls implemented?
- Are ablations implemented as specified?
- Are the same datasets, splits, metrics, and regimes used?
- Does the code test the claimed mechanism (per ALGORITHMIC_FORMALIZATION)?
- Are any components missing, silently changed, or merged together?
- Are there shortcuts that make the experiment non-diagnostic?
- Are config defaults inconsistent with the experiment plan?
- Are outputs sufficient to interpret positive, negative, and tied results?
- Would a null result from this code be interpretable per NULL_RESULT_CONTRACT?
- Does the code respect each entry in ASSUMPTION_LEDGER (or at least surface where it
  diverges)?

Do not only report compile errors. Report semantic mismatches between plan and
implementation.

Return:
1. Verdict on its own line, exactly one of:
   MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR
   (use ERROR only if the audit could not be completed, with a reason code)
2. Missing experiments
3. Missing controls
4. Incorrect defaults
5. Plan-code mismatches
6. Required fixes before GPU
```

## 16. Cheapest Valid Diagnostic

```text
Design the cheapest run that could FALSIFY the central claim — not the smallest run.
This replaces v1.0's "tiny run" framing.

This experiment should answer:
1. Does the mechanism have any signal in a regime where the mechanism could in principle
   manifest? (Do not run the diagnostic in a regime that violates the mechanism's
   necessary preconditions — see G12.)
2. Does the metric detect the intended improvement?
3. Does the baseline actually fail in this regime?
4. Does the control isolate the component / bundle?
5. Can we reproduce a known baseline?
6. Can the implementation pass basic sanity checks?
   - data loading;
   - label alignment;
   - metric range;
   - tiny overfit;
   - deterministic small run;
   - known baseline reproduction.
7. Is this experiment cheap enough to run before full GPU scaling?

The diagnostic does not have to be tiny — it has to be the cheapest run that could
falsify the central claim. Sometimes that is a 1-seed mini run; sometimes it is a
single hard-subset evaluation at full scale; sometimes it is a control-only run with
the proposed method ablated.

Write DIAGNOSTIC_EXPERIMENT_PLAN.md (v1.0 alias: TINY_RUN_PLAN.md).
```

## 17. Diagnostic Run Audit

```text
Audit the diagnostic-run outputs against the plan. A run that merely executes is
insufficient; it must run the intended script, dataset, split, metric,
baseline/component/bundle, config, and produce logs sufficient for null-result diagnosis.

Check:
1. Did the expected script run?
2. Did it use the intended dataset, split, metric, and config?
3. Did it run the intended baseline / component / bundle?
4. Are outputs saved in the expected format?
5. Are metric values plausible?
6. Are logs sufficient to diagnose null results per NULL_RESULT_CONTRACT?
7. Does the run reveal implementation mismatch?
8. **G12 regime check (mandatory):** if the run failed, did the failure regime preserve
   the mechanism's necessary preconditions (per ABSTRACT_TASK_MECHANISM and
   MECHANISM_IDEATION)? If the regime ablated a precondition the mechanism needs, do
   NOT recommend REDESIGN_EXPERIMENT — recommend redesigning the diagnostic to a regime
   where the mechanism could in principle manifest. Document the regime check explicitly.
9. Should we proceed, fix code, or redesign?

Return on its own line, exactly one of:
PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT

Write DIAGNOSTIC_RUN_AUDIT.md (v1.0 alias: TINY_RUN_AUDIT.md).
```

## 18. Result Interpretation Loop

```text
After every diagnostic or scale-up run, do not immediately proceed to the next planned run.

Write a Result Interpretation Note:

1. What was the expected result?
2. What was the observed result?
3. Did the expected signal appear?
4. Which hypothesis is supported?
5. Which hypothesis is weakened?
6. What is the most likely explanation?
7. What are alternative explanations?
8. Is the issue more likely due to:
   - mechanism;
   - benchmark;
   - baseline ceiling;
   - implementation;
   - evaluation;
   - data/task ontology;
   - hyperparameters;
   - missing control?
9. What is the next diagnostic experiment?
10. Decision:
   - continue;
   - narrow;
   - redesign;
   - re-read literature;
   - change benchmark;
   - change control;
   - failure-to-innovation (route to Stage 18.5);
   - stop.

If NULL_RESULT_CONTRACT triggered tie or failure, you MUST frame the result honestly —
do not write a positive narrative (G14). Route to Stage 22 if writing a paper from a
tie/failure.

The next experiment must depend on the interpretation of the current result. Write
RESULT_INTERPRETATION.md.
```

## 18.5 Failure-to-Innovation Loop

```text
You are at Stage 18.5. Codex is in COLLABORATIVE mode.

Trigger: RESULT_INTERPRETATION shows tie or failure, or Stage 17 returned
REDESIGN_EXPERIMENT (with a regime that DID preserve mechanism preconditions — otherwise
G12 routes back to Stage 16, not here).

Inputs:
- RESULT_INTERPRETATION.md
- ASSUMPTION_LEDGER.md (look for falsified entries)
- ALGORITHM_TOURNAMENT.md (alternates kept from Stage 10)
- MECHANISM_IDEATION.md (unranked candidates)

Procedure: see skills/shared-references/innovation-loops.md §5 for the full template.

Brief:
1. Find the falsified assumption — mark which ledger entries the failure refutes (or add
   a new entry if none covered it).
2. Ask the inversion question — given the observed failure mode, what new mechanism does
   it suggest?
3. Revive alternates — re-read tournament alternates and unranked candidates under the
   new constraints introduced by the failure.
4. Decide: refine the committed mechanism, switch to an alternate, or re-enter Stage 8.
5. Codex collaborative additions append revival candidates and identify alternates now
   strengthened by the failure mode.

Output: FAILURE_TO_INNOVATION.md.

Anti-pattern (G17): the new mechanism that emerges here is NOT a pre-planned hypothesis.
It is an exploratory finding that must be validated by a fresh diagnostic before any
paper claim. Stage 21 must label it as such.
```

## 19. Re-read Literature Loop

```text
After early diagnostic results or after Failure-to-Innovation, re-read targeted
literature with question-driven queries. This is a LOOP — fires whenever results raise
a question literature might answer.

For each surfaced question:
1. Convert the question into a literature query (be specific — avoid generic re-reading).
2. Pull 2–5 papers per question via /research-lit.
3. Record:
   - the question;
   - the papers found;
   - the answer the literature gave (or NO ANSWER FOUND);
   - implication for the next decision (revive a mechanism, refine a control, change a
     benchmark, abandon a direction).

Also:
- Did prior work observe the same failure mode?
- Did they report the same baseline ceiling?
- Did they test the same hard subset or regime?
- Did they include the controls we now think are necessary?
- Did their claimed mechanism actually isolate the effect?
- Did their benchmark have more headroom than ours?
- Does our early result change the research question?
- Should we revise hypothesis / mechanism / benchmark / controls / component bundle /
  paper claim?

See skills/shared-references/innovation-loops.md §6.

Output: LITERATURE_REREAD_NOTE.md.

Do not continue scaling if the early result suggests the original research question is wrong.
```

## 20. Scale-up Decision

```text
Scale only after the relevant Validation prerequisites are satisfied.

Before scaling, confirm:
1. ARTIFACT_AUDIT.md exists if a data/env/benchmark/evaluator artifact is being scaled
   against (G4 only requires audit when artifact exists).
2. BASELINE_CEILING.md is known — claim wording will be calibrated against it (G5).
3. Highest-headroom regime is identified.
4. The core mechanism has shown a diagnostic signal in DIAGNOSTIC_RUN_REPORT /
   DIAGNOSTIC_RUN_AUDIT.
5. CONTROL_DESIGN.md isolates the mechanism (G7).
6. NULL_RESULT_CONTRACT.md is clear (G8).
7. DIAGNOSTIC_RUN_AUDIT.md verdict line is `PASS`. `FIX_BEFORE_GPU` and
   `REDESIGN_EXPERIMENT` block. (Accept-either: also reads TINY_RUN_AUDIT.md if
   DIAGNOSTIC_RUN_AUDIT.md is absent.)
8. PLAN_CODE_AUDIT.md verdict line is `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH` whose
   missing pieces are irrelevant to this scale-up wave (G11). `CRITICAL_MISMATCH` blocks
   unconditionally. `ERROR` blocks scale-up pending explicit human acknowledgement.
9. ALGORITHMIC_FORMALIZATION.md exists if scaling official experiments (G10).
10. COMPONENT_BUNDLE_LADDER.md exists if running a new composed method (G9).
11. The next scaled experiment supports a specific paper claim from CLAIM_CONSTRUCTION
    (or a planned future claim in CONTROL_DESIGN).
12. **G15 + G19**: If mode = COMMITMENT or risk_score ≥ 4, HUMAN_DECISION_NOTE.md is
    required before SCALEUP_DECISION = PROCEED.

Then expand carefully:
- more seeds;
- more datasets;
- more splits;
- more domains;
- more ablations;
- full benchmark comparison;
- stronger baselines;
- robustness checks.

Do not scale just because the original plan said so. Scale because the diagnostic
evidence justifies it.

Return on its own line, exactly one of:
PROCEED | HOLD | REDESIGN | HUMAN_DECISION_REQUIRED

Write SCALEUP_DECISION.md.
```

## 21. Result-to-Claim Construction

```text
Build the paper as a claim-evidence chain, not an experiment dump. Each claim is
explicitly evidence-bound: claim → evidence → control → scope → limitation.

For each claim, specify:
1. Claim: What exactly do we claim?
2. Evidence: Which results (run id, file path, table cell) support it?
3. Control: Which controls (run id, file path) isolate the effect?
4. Scope: In which regime does the claim hold (dataset, split, metric, model size,
   compute scale)?
5. Limitation: What does the evidence not prove?
6. Risk of overclaiming: Could a reviewer say the claim is stronger than the evidence?
7. Required additional experiment: What evidence is still missing?
8. **G17 anti-post-hoc check:** is this claim a pre-planned hypothesis (registered in
   CONTROL_DESIGN before the run) or an exploratory finding (emerged from
   FAILURE_TO_INNOVATION or RESULT_INTERPRETATION)? Label exploratory findings explicitly
   as "exploratory finding, not pre-planned hypothesis." Do not present post-hoc
   reframings as pre-planned hypotheses.

Downgrade claims when evidence is partial.

Do not generalize beyond the tested benchmark, regime, or control set.

Write CLAIM_CONSTRUCTION.md.
```

## 22. Tie / Negative Result / Reframing Strategy

```text
If the proposed method ties or fails, do not force a positive story (G14).

Evaluate whether the project still contributes through:
1. Benchmark diagnosis: Did we discover that the benchmark is saturated or misaligned?
2. Baseline ceiling analysis: Did we show that simple baselines are stronger than expected?
3. Failure-mode taxonomy: Did we identify where and why methods fail?
4. Negative result: Did we falsify a common assumption (cite ASSUMPTION_LEDGER entries)?
5. Regime map: Did we show where the method helps and where it does not?
6. Evaluation protocol: Did we improve how the field should evaluate this problem?
7. Data/task ontology: Did we clarify a previously confused task definition?
8. Controlled reproduction: Did we produce a useful reproducibility finding?

If a result is being reframed post-hoc as the new contribution, label it explicitly as
"exploratory finding, not pre-planned hypothesis" in NEGATIVE_RESULT_STRATEGY.md and in
the paper. Do not present post-hoc reframing as a pre-planned hypothesis (G17).

If no contribution remains, recommend stopping or reframing — do not continue expensive
experiments only to rescue a weak story.

Write NEGATIVE_RESULT_STRATEGY.md.
```

## 23. Reviewer Red-team Loop

```text
Act as a skeptical top-tier reviewer. This is a LOOP: review → fix → re-review until
issues are addressed or explicitly accepted as residual risk.

Attack the project on:
1. Problem importance: Is the problem worth solving?
2. Novelty: Is the contribution actually new?
3. Task definition: Are inputs, labels, domains, modalities, vendors, and splits well-defined?
4. Benchmark validity: Does the benchmark actually test the claim?
5. Baselines: Are the baselines strong enough?
6. Controls: Do the controls isolate the mechanism?
7. Null-result interpretation: Would failure be interpretable per NULL_RESULT_CONTRACT?
8. Evidence: Do the results support the claims (cross-check against CLAIM_CONSTRUCTION)?
9. Overclaiming: Are conclusions stronger than evidence (G17)?
10. Reproducibility: Are data, code, metrics, and settings clear enough?
11. Limitations: Are limitations honest and specific?

Per round, return:
- top 5 rejection risks;
- required fixes;
- which fixes are essential before submission;
- which claims should be weakened;
- whether the paper is currently submit-ready.

The orchestrator dispatches this stage to ARIS /auto-review-loop, which manages the
review → fix → re-review iterations. Output rolls up into RED_TEAM_REVIEW.md.
```

## 24. Paper Writing / Paper Improvement Loop

```text
Stage 24 is delegated to ARIS skills:

1. Refuse start if CLAIM_CONSTRUCTION.md is absent (G16, G18). The /paper-writing skill
   has an inline guard for this.
2. Invoke /paper-writing with the existing CLAIM_CONSTRUCTION.md, NEGATIVE_RESULT_STRATEGY.md
   (if applicable), and RED_TEAM_REVIEW.md as inputs. /paper-writing transitively invokes
   /paper-plan, /paper-figure, /paper-write, /paper-compile, /auto-paper-improvement-loop,
   /paper-claim-audit, and /citation-audit.
3. Track all improvement-loop iterations in PAPER_IMPROVEMENT_LOG.md. Each entry: round
   number, reviewer feedback, fix applied, audit verdicts (PAPER_CLAIM_AUDIT,
   CITATION_AUDIT).
4. If any ARIS skill is unavailable, print:
       "ARIS skill <name> unavailable. Stage 24 degraded: <fallback or HUMAN_DECISION_REQUIRED>."
   and continue gracefully. If the missing skill was load-bearing for a hard gate
   (e.g. /paper-claim-audit for G16-equivalent paper checks), escalate to
   HUMAN_DECISION_REQUIRED.

Output: PAPER_IMPROVEMENT_LOG.md + paper/ tree.
```

## 25. Human Decision / Next Loop

```text
Before proceeding to the next major stage, produce a Human Decision Note.

Summarize:
1. What we currently believe.
2. What evidence supports it.
3. What remains uncertain.
4. What the agent recommends next.
5. What decision requires human judgment.

End with one of:
- PROCEED;
- NARROW;
- REDESIGN;
- RE-READ;
- CHANGE BENCHMARK;
- STOP;
- HUMAN_DECISION_REQUIRED.

Write HUMAN_DECISION_NOTE.md.
```

## v1.0 → v1.3 Stage / Prompt Alias Appendix

This file's section numbers have shifted from v1.0 (0A–15) to v1.3 (0–25). Skill files
that hard-coded a v1.0 section reference should update to the v1.3 number below.
Verdict-token contracts are preserved verbatim where indicated.

| v1.0 section | v1.3 section | Notes |
|---|---|---|
| 0A | 1 | Same prompt body, renumbered |
| 1 | 2 | Now explicitly a loop (with Stage 19 re-read) |
| 0B | 3 | `PROCEED \| NARROW \| RETHINK` preserved |
| 2 | 4 + 5 + 6 | Split into Assumption Ledger + Abstract Task / Mechanism + Artifact-triggered Audit |
| 3 | 7 | Added "headroom is a reference, not a veto" |
| 4 | 11 | Codex switches back to adversarial here |
| 5 | 12 | Same prompt body |
| 6 | 13 | Generalised to bundle |
| 7 | 16 | "Cheapest valid diagnostic" framing |
| 7.5 | 15 | `MATCHES_PLAN \| PARTIAL_MISMATCH \| CRITICAL_MISMATCH \| ERROR` preserved; required artifacts list expanded to v1.3 set |
| 8 | (folded into 16/17) | "Tiny run" replaced by diagnostic run |
| 8.5 | 17 | `PASS \| FIX_BEFORE_GPU \| REDESIGN_EXPERIMENT` preserved; G12 regime check added |
| 9 | 18 | Same prompt body |
| 10 | 19 | Now explicitly a loop |
| 11 | 20 | + G15 + G19 (HUMAN_DECISION_NOTE) |
| 12 | 21 | + G17 anti-post-hoc check |
| 13 | 22 | + G17 reframing language |
| 14 | 23 | Now an explicit loop; calls ARIS /auto-review-loop |
| (new) | 24 | Paper writing — calls ARIS chain |
| 15 | 25 | 7-token verdict preserved |

### Wholly new prompts (no v1.0 ancestor)

Stage 0 (Mode & Risk Routing), Stage 2.5 (Problem Reframing), Stage 4 (Assumption Ledger),
Stage 5 (Abstract Task / Mechanism Framing), Stage 6 (Artifact-triggered Audit — explicit
"do not run if artifact does not yet exist" preamble), Stage 8 / 9 / 10 (delegate to
`innovation-loops.md` §2 / §3 / §4), Stage 14 (Algorithmic Formalization), Stage 18.5
(delegate to `innovation-loops.md` §5), Stage 24 (delegated to ARIS chain).

### Renamed artifacts referenced in prompts

- `COMPONENT_LADDER.md` → `COMPONENT_BUNDLE_LADDER.md` (consumers accept either)
- `TINY_RUN_PLAN.md` → `DIAGNOSTIC_EXPERIMENT_PLAN.md` (consumers accept either)
- `TINY_RUN_REPORT.md` → `DIAGNOSTIC_RUN_REPORT.md` (consumers accept either)
- `TINY_RUN_AUDIT.md` → `DIAGNOSTIC_RUN_AUDIT.md` (consumers accept either)
- `TASK_ONTOLOGY.md` — no alias; manual migration to MODE_ROUTING / SEED_FRAMING /
  ASSUMPTION_LEDGER / ABSTRACT_TASK_MECHANISM (see `research-agent-pipeline.md` migration
  appendix)
