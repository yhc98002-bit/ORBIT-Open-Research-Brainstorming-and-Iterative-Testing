---
name: "experiment-plan"
description: "Turn a refined research proposal or method idea into a detailed, decision-driven experiment roadmap. Use after `research-refine`, or when the user asks for a detailed experiment plan, ablation matrix, evaluation protocol, run order, compute budget, or paper-ready validation that supports the core problem, novelty, simplicity, and any LLM / VLM / Diffusion / RL-based contribution."
---

# Experiment Plan: Decision-Driven Validation

Refine and concretize: **$ARGUMENTS**

## Overview

Use this skill after the method is stable enough that the next question becomes: **what exact experiments should we run, in what order, to change the next research decision?** If the user wants the full chain in one request, prefer `/research-refine-pipeline`.

The goal is not to generate a giant benchmark wishlist. The goal is to turn a proposal into a **decision -> evidence target -> run order** roadmap that supports four things:

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

## Workflow

### Phase 0: Load the Proposal Context

Read the most relevant existing files first if they exist:

- `refine-logs/FINAL_PROPOSAL.md`
- `refine-logs/REVIEW_SUMMARY.md`
- `refine-logs/REFINEMENT_REPORT.md`

Extract:

- **Problem Anchor**
- **Dominant contribution**
- **Optional supporting contribution**
- **Critical reviewer concerns**
- **Data / compute / timeline constraints**
- **Which frontier primitive is central, if any**

If these files do not exist, derive the same information from the user's prompt.

### Phase 1: Define Candidate Claims / Evidence Targets

Before proposing experiments, write down the candidate claims or evidence targets whose
outcomes would change a research decision.

Use this structure:

- **Primary claim**: the main mechanism-level contribution
- **Supporting claim**: optional, only if it directly strengthens the main paper story
- **Anti-claim to rule out**: e.g. "the gain only comes from more parameters," "the gain only comes from a larger search space," or "the modern component is just decoration"
- **Minimum convincing evidence**: what would make the decision change? For paper-bearing
  experiments, what would make the claim believable to a strong reviewer?

Do not exceed `MAX_PRIMARY_CLAIMS` unless the paper truly has multiple inseparable claims.

### Phase 2: Build the Experimental Storyline

Design the paper around a compact set of experiment blocks. Default to the following blocks and delete any that are not needed:

1. **Main anchor result** — does the method solve the actual bottleneck?
2. **Novelty isolation** — does the dominant contribution itself matter?
3. **Simplicity / elegance check** — can a bigger or more fragmented version be avoided?
4. **Frontier necessity check** — if an LLM / VLM / Diffusion / RL-era component is central, is it actually the right tool?
5. **Failure analysis or qualitative diagnosis** — what does the method still miss?

For each block, decide whether it belongs in:

- **Paper-bearing** — essential only if this experiment supports paper-level claim scope
- **Appendix** — useful but non-blocking
- **Cut** — interesting, but not worth the paper budget

Prefer one strong baseline family over many weak baselines. If a stronger modern baseline exists, use it instead of padding the list.

### Phase 3: Specify Each Experiment Block

For every kept block, fully specify:

- **Claim tested**
- **Dataset / split / task**
- **Compared systems**: strongest baselines, ablations, and variants only
- **Metrics**: decisive metrics first, secondary metrics second
- **Setup details**: backbone, frozen vs trainable parts, key hyperparameters, training budget, seeds
- **Success criterion**: what outcome would count as convincing evidence?
- **Failure interpretation**: if the result is negative, what does it mean?
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
> - **[Output Versioning Protocol](../../shared-references/output-versioning.md)** — write timestamped file first, then copy to fixed name
> - **[Output Manifest Protocol](../../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Progressive disclosure.** Keep `EXPERIMENT_PLAN.md` as an index. Put executable detail in `EXPERIMENT_PLAN_EXEC.md`; put milestone-specific instructions in run cards; archive old monoliths only when they preserve useful history.

- **Every committed experiment must change a research decision.** Paper-claim defense is required only for paper-bearing experiments.
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
