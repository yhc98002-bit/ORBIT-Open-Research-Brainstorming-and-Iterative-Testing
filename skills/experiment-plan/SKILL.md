---
name: experiment-plan
description: 'Turn a refined research proposal or method idea into a detailed, claim-driven experiment roadmap. Use after `research-refine`, or when the user asks for a detailed experiment plan, ablation matrix, evaluation protocol, run order, compute budget, or paper-ready validation that supports the core problem, novelty, simplicity, and any LLM / VLM / Diffusion / RL-based contribution.'
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent
---

> **ORBIT v1.3 compatibility note:** This skill may contain legacy v1.0 artifact names
> (e.g. `TASK_ONTOLOGY.md`, `COMPONENT_LADDER.md`, `TINY_RUN_AUDIT.md`). In ORBIT v1.3,
> canonical artifacts are defined in
> [`skills/shared-references/research-agent-pipeline.md`](../shared-references/research-agent-pipeline.md);
> the legacy names are aliases only and consumers parse either form. Full v1.3 vocabulary
> propagation in this skill is deferred to a follow-on PR.

# Experiment Plan: Claim-Driven, Paper-Oriented Validation

Refine and concretize: **$ARGUMENTS**

## Overview

Use this skill after the method is stable enough that the next question becomes: **what exact experiments should we run, in what order, to defend the paper?** If the user wants the full chain in one request, prefer `/research-refine-pipeline`.

The goal is not to generate a giant benchmark wishlist. The goal is to turn a proposal into a **claim -> evidence -> run order** roadmap that supports four things:

1. the method actually solves the anchored problem
2. the dominant contribution is real and focused
3. the method is elegant enough that extra complexity is unnecessary
4. any frontier-model-era component is genuinely useful, not decorative

## Constants

- **OUTPUT_DIR = `refine-logs/`** — Default destination for experiment planning artifacts.
- **MAX_PRIMARY_CLAIMS = 2** — Prefer one dominant claim plus one supporting claim.
- **MAX_CORE_BLOCKS = 5** — Keep the must-run experimental story compact.
- **MAX_BASELINE_FAMILIES = 3** — Prefer a few strong baselines over many weak ones.
- **DEFAULT_SEEDS = 3** — Use 3 seeds when stochastic variance matters and budget allows.

## ORBIT Diagnostic Planning Gate

This gate is always-on. Before any planning work, load:

- `shared-references/research-agent-pipeline.md`
- `shared-references/research-harness-prompts.md` sections `4`, `5`, `7`, and `11`–`16`
  (v1.3 numbering — Grounding + Validation prerequisites)
- `shared-references/semantic-code-audit.md` (so this skill knows which v1.3 artifacts the
  downstream Stage 15 plan-code audit will require)

Run `mkdir -p orbit-research/`. Before writing or finalizing
`refine-logs/EXPERIMENT_PLAN.md`, create or update:

- `orbit-research/CONTROL_DESIGN.md`
- `orbit-research/NULL_RESULT_CONTRACT.md`
- `orbit-research/COMPONENT_BUNDLE_LADDER.md`  *(v1.0 alias accepted: `COMPONENT_LADDER.md`)*
- `orbit-research/ALGORITHMIC_FORMALIZATION.md`
- `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md`  *(v1.0 alias accepted: `TINY_RUN_PLAN.md`)*

If the project came through `/idea-to-proposal` or `/research-pipeline` Discovery+Grounding+Innovation,
these v1.3 artifacts will already exist (read them; do not regenerate):

- `orbit-research/PROBLEM_SELECTION.md`
- `orbit-research/ASSUMPTION_LEDGER.md`
- `orbit-research/ABSTRACT_TASK_MECHANISM.md`
- `orbit-research/BASELINE_CEILING.md`
- `orbit-research/MECHANISM_IDEATION.md`
- `orbit-research/ANALOGY_TRANSFER.md`
- `orbit-research/ALGORITHM_TOURNAMENT.md`

Hard gates:

- Do not design methods before the abstract task / mechanism framing is stable
  (`ABSTRACT_TASK_MECHANISM.md`).
- Do not run the proposed method before baseline ceiling is known or explicitly estimated
  (`BASELINE_CEILING.md`).
- Do not include experiments whose null result would be uninterpretable (G8).
- Do not plan a full system until each component or minimal mechanism-preserving bundle
  has a control, expected signal, and rollback condition (G9 — `COMPONENT_BUNDLE_LADDER.md`).
- Do not plan broad grids before the minimal diagnostic experiment.
- Do not write an `EXPERIMENT_PLAN.md` that fails to cite v1.3 grounding/innovation
  artifacts when they exist — the downstream Stage 15 plan-code audit
  (`semantic-code-audit.md` §3) will reject it as `incomplete_input_set`.

## Workflow

### Phase 0: Load the Proposal Context (and v1.3 grounding/innovation artifacts)

Read the most relevant existing files first if they exist:

**Proposal-side (existing):**
- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/REVIEW_SUMMARY.md`
- `refine-logs/REFINEMENT_REPORT.md`

**v1.3 grounding artifacts (read if present — do not regenerate):**
- `orbit-research/PROBLEM_SELECTION.md` — selection rationale + verdict
- `orbit-research/ASSUMPTION_LEDGER.md` — every assumption tagged factual / working
- `orbit-research/ABSTRACT_TASK_MECHANISM.md` — abstract task + mechanism families
- `orbit-research/BASELINE_CEILING.md` — simple-strong baseline reference

**v1.3 innovation artifacts (read if present):**
- `orbit-research/MECHANISM_IDEATION.md` — candidate mechanisms (M-IDs)
- `orbit-research/ANALOGY_TRANSFER.md` — cross-domain analogies
- `orbit-research/ALGORITHM_TOURNAMENT.md` — TENTATIVE_PREFERRED_SKETCH_ID + alternates

**v1.3 continuation hints (read if present):**
- `orbit-research/IDEA_TO_PROPOSAL_STATE.json` — if `status = "awaiting_human_continue"`,
  treat the user's invocation of this skill as the human's "approve continue" signal per
  `shared-references/continuation-contract.md` cross-skill resume rules. Do not redo
  Discovery / Grounding / Innovation.

Extract from the proposal-side files:

- **Problem Anchor**
- **Dominant contribution**
- **Optional supporting contribution**
- **Critical reviewer concerns**
- **Data / compute / timeline constraints**
- **Which frontier primitive is central, if any**

Extract from the v1.3 artifacts:

- **Selected problem ID + PROCEED/NARROW/RETHINK verdict** (from PROBLEM_SELECTION)
- **Working assumptions + their A-IDs** (from ASSUMPTION_LEDGER) — these become explicit
  rows in the Claim Map (Phase 1) so every claim cites the assumption it depends on
- **Abstract task signature + mechanism family** (from ABSTRACT_TASK_MECHANISM) — used in
  Experiment Block specifications (Phase 3)
- **Headroom / saturation status** (from BASELINE_CEILING) — calibrates how loud the
  paper claim wording can be (G5)
- **Implemented mechanism candidate** (from ALGORITHM_TOURNAMENT
  TENTATIVE_PREFERRED_SKETCH_ID, plus alternates) — referenced by every "Compared systems"
  field in Phase 3 so the experiment plan and the v1.3 contract agree on which sketch is
  being tested

If the proposal-side files do not exist, derive the same information from the user's prompt.
If the v1.3 artifacts do not exist (project pre-dates v1.3 or the user invoked this skill
directly without going through `/idea-to-proposal` / `/research-pipeline`), surface a
warning to the user:

```
⚠️  v1.3 grounding/innovation artifacts not found under orbit-research/.
   The EXPERIMENT_PLAN this skill produces will not be v1.3-aware, which means
   downstream Stage 15 plan-code audit (semantic-code-audit.md §3) will report
   ERROR with reason "incomplete_input_set" until ASSUMPTION_LEDGER,
   ABSTRACT_TASK_MECHANISM, and ALGORITHM_TOURNAMENT exist.

   To populate them, run:
       /idea-to-proposal "<your problem or .md path>"
   or:
       /research-pipeline "<your input>" — from-stage: 4

   Or proceed without (degraded mode) and accept the audit ERROR downstream.
```

Default action under AUTO_PROCEED = true: proceed in degraded mode but write a clear
warning into `EXPERIMENT_PLAN.md` header explaining which v1.3 artifacts are missing.

### Phase 1: Freeze the Paper Claims

Before proposing experiments, write down the claims that must be defended.

Use this structure:

- **Primary claim**: the main mechanism-level contribution
- **Supporting claim**: optional, only if it directly strengthens the main paper story
- **Anti-claim to rule out**: e.g. "the gain only comes from more parameters," "the gain only comes from a larger search space," or "the modern component is just decoration"
- **Minimum convincing evidence**: what would make each claim believable to a strong reviewer?
- **Assumptions cited** (v1.3 — required when `ASSUMPTION_LEDGER.md` exists): list the
  ASSUMPTION_LEDGER row IDs (A1, A2, ...) that this claim depends on. Per Hard Gate G2,
  every "is/will/always" wording must trace to a ledger row, otherwise it must be demoted
  to "we hypothesise" or cite external evidence.
- **Mechanism cited** (v1.3 — required when `ALGORITHM_TOURNAMENT.md` exists): the sketch
  ID (S<n>) being claimed. Usually the TENTATIVE_PREFERRED_SKETCH_ID from Stage 10, but
  Phase 1 of this skill is allowed to switch to an alternate from the tournament if the
  Claim Map exposes a fit problem — record this switch under "Method Selection Rationale".

Do not exceed `MAX_PRIMARY_CLAIMS` unless the paper truly has multiple inseparable claims.

### Phase 2: Build the Experimental Storyline

Design the paper around a compact set of experiment blocks. Default to the following blocks and delete any that are not needed:

1. **Main anchor result** — does the method solve the actual bottleneck?
2. **Novelty isolation** — does the dominant contribution itself matter?
3. **Simplicity / elegance check** — can a bigger or more fragmented version be avoided?
4. **Frontier necessity check** — if an LLM / VLM / Diffusion / RL-era component is central, is it actually the right tool?
5. **Failure analysis or qualitative diagnosis** — what does the method still miss?

For each block, decide whether it belongs in:

- **Main paper** — essential to defend the core claims
- **Appendix** — useful but non-blocking
- **Cut** — interesting, but not worth the paper budget

Prefer one strong baseline family over many weak baselines. If a stronger modern baseline exists, use it instead of padding the list.

### Phase 3: Specify Each Experiment Block

For every kept block, fully specify:

- **Claim tested** (cite C-IDs from Phase 1 Claim Map)
- **Dataset / split / task** (when `ARTIFACT_AUDIT.md` exists for the dataset, cite it)
- **Compared systems**: strongest baselines, ablations, and variants only
  - When `ALGORITHM_TOURNAMENT.md` exists, the proposed system is the
    `TENTATIVE_PREFERRED_SKETCH_ID` (or alternate, with rationale). Reference the sketch
    by S<id> so the downstream Stage 15 plan-code audit can verify implementation
    fidelity.
- **Mechanism family** (v1.3 — when `ABSTRACT_TASK_MECHANISM.md` exists): which mechanism
  family from the abstract framing this block is exercising. If the failure interpretation
  could be "wrong mechanism family", say so explicitly.
- **Metrics**: decisive metrics first, secondary metrics second
- **Setup details**: backbone, frozen vs trainable parts, key hyperparameters, training budget, seeds
- **Success criterion**: what outcome would count as convincing evidence?
- **Failure interpretation**: if the result is negative, what does it mean?
  - Cross-reference `NULL_RESULT_CONTRACT.md` if it has been written; this block's
    failure-mode list should be consistent with it (G8).
- **Assumptions exercised** (v1.3 — when `ASSUMPTION_LEDGER.md` exists): which A-IDs from
  the ledger this block tests. A `working` assumption that this block does not test should
  be documented as "still untested after this experiment".
- **Table / figure target**: where this result should appear in the paper

Special rules:

- A **simplicity check** should usually compare the final method against either an overbuilt variant or a tempting extra component that the paper intentionally rejects.
- A **frontier necessity check** should usually compare the chosen modern primitive against the strongest plausible simpler or older alternative.
- If the proposal is intentionally non-frontier, say so explicitly and skip the frontier block instead of forcing one.

### Phase 4: Turn the Plan Into an Execution Order

Build a realistic run order so the user knows what to do first.

Use this milestone structure:

1. **Sanity stage** — data pipeline, metric correctness, one quick overfit or toy split
2. **Baseline stage** — reproduce the strongest baseline(s)
3. **Main method stage** — run the final method on the primary setting
4. **Decision stage** — run the decisive ablations for novelty, simplicity, and frontier necessity
5. **Polish stage** — robustness, qualitative figures, appendix extras

For each milestone, estimate:

- compute cost
- expected turnaround time
- stop / go decision gate
- risk and mitigation

Separate **must-run** from **nice-to-have** experiments.

### Phase 5: Write the Outputs

#### Step 5.1: Write `refine-logs/EXPERIMENT_PLAN.md`

Write this file as a short **index**, not as the full experiment plan. It should tell
downstream agents which file to read for each task and preserve only the current status,
key constraints, and routing logic. Do not paste full claim maps, full experiment blocks,
round history, or repeated rationale into this index.

Use this structure:

```markdown
# Experiment Plan — Index

**Purpose**: this file is an **index**. The actual execution plan is split into agent-actionable run cards and protocol files. Each downstream skill reads this index and follows the relevant cross-reference.

**Project**: [one-line project / method / venue / budget status]

## Files

| Stage | File | What it contains | When to read |
|---|---|---|---|
| Method spec | `FINAL_PROPOSAL.md` | Proposal index and method cross-references | always |
| Main exec plan | `EXPERIMENT_PLAN_EXEC.md` | Claim Map; compact Block cards; Run Order; budget gates; risks; checklist | always |
| Current immediate task | `[MILESTONE]_RUN_CARD.md` | The next action only: command surface, success gate, halt rule | now, if present |
| Failure routing | `NULL_RESULT_CONTRACT.md` | NEGATIVE / TIE interpretation and paper-pivot rules | when any block fails or ties |
| Optional protocols | `[PROTOCOL].md` | Dataset mapping, baseline protocol, figure plan, or other scoped details | only when referenced by a run card |

## Phased flow

```text
Phase 0 — Sanity / diagnostic gate
  -> [current milestone or gate]
Phase 1 — Baselines and main method
  -> `EXPERIMENT_PLAN_EXEC.md` Run Order
Phase 2 — Decisive ablations
  -> halt at each registered decision gate
Phase 3 — Appendix / qualitative / write-up support
  -> run only after main evidence is secured
```

## Key constraints

- [Hard stop / budget / data constraint that downstream agents must enforce]
- [No silent threshold relaxation; no unregistered experiment launch]
- [Nice-to-have runs must not delay must-run evidence]

## Downstream skill

`/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"` reads this index, follows the cross-references, and implements the milestones in `EXPERIMENT_PLAN_EXEC.md` order. The bridge skill must not auto-launch a milestone past a hard stop without explicit human approval.
```

#### Step 5.2: Write `refine-logs/EXPERIMENT_PLAN_EXEC.md`

Write the executable plan here. Keep it compact and decision-oriented: every row should
either tell the implementer what to run, what result would change the paper, or when to
halt. Avoid prose introductions, repeated claim rationales, and broad benchmark wishlists.

Use this structure:

```markdown
# Experiment Plan Exec

## Claim Map
| Claim | Minimum Convincing Evidence | Linked Blocks | Assumptions / Sketch IDs |
|---|---|---|---|
| C1 | ... | B1, B2 | A1, S3 |

## Experiment Blocks

### Block A: [Name]
- Claim tested:
- Dataset / split / task:
- Compared systems:
- Metrics:
- Setup details:
- Success criterion:
- Failure interpretation:
- Table / figure target:
- Priority: MUST-RUN / NICE-TO-HAVE

### Block B: [Name]
...

## Run Order and Milestones
| Milestone | Goal | Runs | Decision Gate | Cost | Risk |
|-----------|------|------|---------------|------|------|
| M0        | ...  | ...  | ...           | ...  | ...  |

## Compute and Data Budget
- Total estimated GPU-hours:
- Data preparation needs:
- Human evaluation needs:
- Biggest bottleneck:

## Risks and Mitigations
- [Risk]:
- [Mitigation]:

## Final Checklist
- [ ] Main paper tables are covered
- [ ] Novelty is isolated
- [ ] Simplicity is defended
- [ ] Frontier contribution is justified or explicitly not claimed
- [ ] Nice-to-have runs are separated from must-run runs
```

#### Step 5.3: Write optional companion files only when useful

Create companion files only when the content would otherwise bloat the index or exec plan.
Common examples:

- `refine-logs/[MILESTONE]_RUN_CARD.md` — current active run or important completed predecessor.
- `refine-logs/CATEGORY_MAPPING_PROTOCOL.md` — dataset/task mapping that must be reused.
- `refine-logs/TIER2_BASELINE_CARD.md` — secondary baseline protocol and drop rules.
- `refine-logs/PAPER_FIGURE_PLAN.md` — figure/table sourcing plan.
- `refine-logs/EXPERIMENT_PLAN_FULL.md` — optional archive only when preserving a previous monolithic plan or revision history is useful.

#### Step 5.4: Write `refine-logs/EXPERIMENT_TRACKER.md`

Use this structure:

```markdown
# Experiment Tracker

| Run ID | Milestone | Purpose | System / Variant | Split | Metrics | Priority | Status | Notes |
|--------|-----------|---------|------------------|-------|---------|----------|--------|-------|
| R001   | M0        | sanity  | ...              | ...   | ...     | MUST     | TODO   | ...   |
```

Keep the tracker compact and execution-oriented.

#### Step 5.5: Present a Brief Summary to the User

```
Experiment plan ready.

Index: refine-logs/EXPERIMENT_PLAN.md
Execution plan: refine-logs/EXPERIMENT_PLAN_EXEC.md
Tracker: refine-logs/EXPERIMENT_TRACKER.md

Current next gate:
- [milestone / run card / halt condition]

First runs to launch:
1. [run]
2. [run]
3. [run]
```

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — write timestamped file first, then copy to fixed name
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Progressive disclosure.** Keep `EXPERIMENT_PLAN.md` as an index. Put executable detail in `EXPERIMENT_PLAN_EXEC.md`; put milestone-specific instructions in run cards; archive old monoliths only when they preserve useful history.

- **Every experiment must defend a claim.** If it does not change a reviewer belief, cut it.
- **Prefer a compact paper story.** Design the main table first, then add only the ablations that defend it.
- **Defend simplicity explicitly.** If complexity is a concern, include a deletion study or a stronger-but-bloated variant comparison.
- **Defend frontier choices explicitly.** If a modern primitive is central, prove why it is better than the strongest simpler alternative.
- **Prefer strong baselines over long baseline lists.** A short, credible comparison set is better than a padded one.
- **Separate must-run from nice-to-have.** Do not let appendix ideas delay the core paper evidence.
- **Reuse proposal constraints.** Do not invent unrealistic budgets or data assumptions.
- **Do not fabricate results.** Plan evidence; do not claim evidence.

## Composing with Other Skills

```
/research-refine-pipeline -> one-shot method + experiment planning
/research-refine   -> method and claim refinement
/experiment-plan   -> detailed experiment roadmap
/run-experiment    -> execute the runs
/auto-review-loop  -> react to results and iterate on the paper
```
