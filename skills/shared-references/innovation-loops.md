# ORBIT Innovation Loops

> Five named loops that drive divergent mechanism invention before ORBIT commits to an
> experiment, plus the Collaborative Claude-Codex Innovation Mode that powers them.
> Stages 8, 9, 10, 18.5, and 19 each delegate their procedure here.

## §1. Introduction

ORBIT v1.3's premise: research worth doing usually does not come from the first method that
fits the proposal. It comes from a **divergent search** that produces several plausible
mechanisms, then a **commitment process** that picks the one most worth running.

Innovation Loops produce **candidates**. They never converge. Convergence is the job of
the commitment gates downstream:

- Convergence happens at Stage 11 (Hypothesis-Mechanism-Benchmark-Control Matrix), Stage 14
  (Algorithmic Formalization), and Stage 15 (Plan-Code Consistency Loop).
- Until then, alternatives are kept on the table — they may revive in Stage 18.5 if the
  committed mechanism fails.

When invoked: Stages 8, 9, 10, 18.5, 19 — and any time the orchestrator dispatches an
explicit `/innovation-loop` call (e.g., when a Tier-A skill detects mode = INNOVATION and
no `MECHANISM_IDEATION.md` exists yet).

Reference back: `skills/shared-references/research-agent-pipeline.md` (full pipeline
context); `skills/shared-references/research-harness-prompts.md` (per-stage canonical prompts
that delegate to the sections below by anchor).

Key invariant: innovation loops produce candidates; commitment gates (G6, G11, G15) decide
what becomes method.

## §2. Loop A — Mechanism Invention (Stage 8)

**Trigger:** orchestrator routes to Stage 8 when mode = INNOVATION/EXPLORATION and either
(a) `ABSTRACT_TASK_MECHANISM.md` exists, or (b) the user explicitly asks for divergent
ideation seeded from a prior abstract task.

**Inputs:**
- `ABSTRACT_TASK_MECHANISM.md` (preferred) or a one-page abstract task description
- `ASSUMPTION_LEDGER.md` (so candidates know what the working hypotheses are)
- `LITERATURE_MAP.md` (for prior-art context)

**Procedure:**

1. **Diverge.** Generate 5–10 candidate mechanisms. Aim for breadth: include at least one
   "obvious" mechanism, one "borrowed from another field" mechanism, one "minimal" mechanism,
   one "complex/composite" mechanism, and one deliberate "wild card."
2. **Score each candidate** on three axes (1–5 each):
   - **Novelty** — how unobvious vs. existing literature
   - **Feasibility** — can it be implemented in the available compute / data budget
   - **Falsifiability** — does it make a sharp prediction whose failure points to a specific
     cause (rather than "method does not work")
3. **Codex collaborative pass** — Codex runs in collaborative mode (§7): no veto, only
   adds candidates Claude missed, identifies blind spots, suggests alternative framings.
4. **Synthesise** but **do not converge.** The output lists all candidates with scores and
   a brief rationale per candidate. Mark a tentative top-3 for Stage 9 to expand on, but
   keep the rest visible.

**Output artifact:** `MECHANISM_IDEATION.md` containing:

```markdown
# Mechanism Ideation

## Abstract task (1 line)
<the task this loop is searching mechanisms for>

## Candidates

| ID | Mechanism (1 line) | Novelty | Feasibility | Falsifiability | Notes |
|----|--------------------|---------|-------------|----------------|-------|
| M1 | ...                | 4       | 3           | 5              | ...   |
| M2 | ...                | ...     | ...         | ...            | ...   |
...

## Per-candidate detail (½ page each)

### M1 — <name>
- **Mechanism:** what the algorithm does
- **Why it might work:** the underlying intuition
- **Necessary preconditions:** what the regime / data / scale must look like for the
  mechanism to manifest
- **Diagnosable failure modes:** what failures would tell us, and which would be ambiguous
- **Required controls:** what comparisons would isolate this mechanism's contribution

### M2 — <name>
... (same template)

## Top-3 for Stage 9 expansion
- M<id>, M<id>, M<id>

## Codex collaborative additions
- <list of candidates / blind spots Codex contributed>
```

**Anti-pattern:** do not pick a single winner inside this loop. The temptation to "narrow
to the best one" defeats the purpose. Convergence is gated to Stage 11.

**Hard gate touched:** G6 (≥1 of `MECHANISM_IDEATION` / `ANALOGY_TRANSFER` /
`ALGORITHM_TOURNAMENT` required before commitment).

## §3. Loop B — Analogy / Cross-pollination (Stage 9)

**Trigger:** orchestrator routes to Stage 9 after `MECHANISM_IDEATION.md` exists and at
least one candidate looks worth deepening.

**Inputs:**
- `MECHANISM_IDEATION.md` (top-3 candidates from Stage 8)
- 1–3 analogous-domain literature pulls from `/research-lit` if needed (other fields where
  a structurally similar problem is already solved)

**Procedure:**

1. For each top candidate, name **≥1 analogous solved problem** from another field. Be
   generous with the analogy: a problem in distillation can borrow from compression; a
   problem in RL can borrow from planning; a problem in vision can borrow from speech.
2. Map the analogy in three columns: *what transfers*, *what does not transfer*, *what new
   constraint the transfer introduces*.
3. Bold analogies welcome — the goal is to surface mechanism families Claude might not have
   reached unaided.
4. **Codex collaborative** — adds analogies, identifies broken transfers, suggests cross-pollinations.

**Output artifact:** `ANALOGY_TRANSFER.md` containing:

```markdown
# Analogy / Cross-pollination

## Mapping table

| Candidate | Analogous solved problem | What transfers | What does not | New constraint introduced |
|-----------|--------------------------|----------------|---------------|---------------------------|
| M1        | ...                      | ...            | ...           | ...                       |
| M1        | (alt analogy)            | ...            | ...           | ...                       |
| M2        | ...                      | ...            | ...           | ...                       |
...

## Hybrid mechanisms suggested by the analogies
- H1 = M1 with constraint X borrowed from analog A
- H2 = M2's structure + M3's loss
- ...

## Codex collaborative additions
- ...
```

**Anti-pattern:** do not declare an analogy "wrong" if it does not transfer cleanly — the
*partial* transfer is often the most informative outcome. Just label what does and does not
transfer.

**Hard gate touched:** G6.

## §4. Loop C — Algorithm Sketch Tournament (Stage 10)

**Trigger:** after `MECHANISM_IDEATION.md` and `ANALOGY_TRANSFER.md` both exist and the
top candidate set has stabilised.

**Inputs:**
- `MECHANISM_IDEATION.md`, `ANALOGY_TRANSFER.md`
- Optional: hybrid candidates synthesised in Stage 9

**Procedure:**

1. **Sketch.** Write a 1-page algorithm sketch per top candidate (3–5 sketches total).
   Each sketch contains: input/output signature, core update rule (pseudocode acceptable),
   loss / reward / objective, decision rule, evaluator predicate, integration cost estimate.
2. **Round-robin pairwise comparison.** For every pair of sketches, decide which is better
   on four criteria:
   - **Diagnosability of failure** (does the sketch make failure interpretable?)
   - **Mechanism fidelity** (does the implementation actually realise the intended mechanism?)
   - **Falsifiability** (sharp prediction vs. squishy claim)
   - **Integration cost** (additional infrastructure / new dependencies)
3. Tally pairwise wins; mark a **tentative preferred sketch** for Stage 11 commitment
   review. **This is not a final commit** — Stage 10 selects candidates for Stage 11
   HMBC review, it does not bind the project to a method. **Keep alternates** with their
   pairwise scores — they will be needed in Stage 18.5 if the tentative pick fails or
   in Stage 11 if the HMBC matrix exposes a problem with it.
4. **Codex** — collaborative on sketch quality (suggests missing terms, points out
   under-specified update rules); **adversarial on tournament adjudication** (this is the
   one place inside innovation loops where Codex can challenge Claude's pairwise picks).
   Codex's challenge informs the tentative pick; it does not finalize it.

**Output artifact:** `ALGORITHM_TOURNAMENT.md` containing:

```markdown
# Algorithm Sketch Tournament

## Sketches

### Sketch S1 (← M<id>)
- Signature, update rule, loss, decision rule, evaluator, integration cost
- 1-page detail

### Sketch S2 (← M<id> + analogy A)
...

## Pairwise results

| Pair    | Diagnosability | Fidelity | Falsifiability | Integration cost | Winner |
|---------|----------------|----------|----------------|------------------|--------|
| S1 v S2 | S1             | S2       | S1             | S2               | S1 (2/4) |
| S1 v S3 | ...            | ...      | ...            | ...              | ...    |
...

## Verdict (non-binding — Stage 11 reviews and may revise)
TENTATIVE_PREFERRED_SKETCH_ID: S<id>
ALTERNATES: S<id>, S<id>
ABSTAIN_REASONS: <if Codex objected to the pick>
NOT_FINAL_NOTE: Stage 10 selects candidates for Stage 11 HMBC review. The tentative
pick is not a method commitment; Stage 11 may pick an alternate or send the project
back to Stage 8.
```

**Required ending (optional but recommended):**
`TENTATIVE_PREFERRED_SKETCH_ID + ALTERNATES + ABSTAIN_REASONS`. Convergence happens at
Stage 11 (HMBC matrix), Stage 14 (Algorithmic Formalization), and Stage 15 (Plan-Code
Audit) — never inside this loop.

**Hard gate touched:** G6.

## §5. Loop D — Failure-to-Innovation (Stage 18.5)

**Trigger:** orchestrator routes to Stage 18.5 when `RESULT_INTERPRETATION.md` shows tie
or failure, or when Stage 17 returned `REDESIGN_EXPERIMENT`.

**Inputs:**
- `RESULT_INTERPRETATION.md`
- `ASSUMPTION_LEDGER.md` (look for falsified entries)
- `ALGORITHM_TOURNAMENT.md` (revisit alternates)
- `MECHANISM_IDEATION.md` (revisit unranked candidates)

**Procedure:**

1. **Find the falsified assumption.** Mark which entries in `ASSUMPTION_LEDGER.md` the
   failure refutes. If none — the failure is informative about something *outside* the
   ledger and a new entry is required.
2. **Ask the inversion question.** Given the failure mode just observed, what new mechanism
   does it suggest? Often the failure points to a missing operator, an inverted objective,
   or a regime where the mechanism family is wrong.
3. **Revive alternates.** Re-read `ALGORITHM_TOURNAMENT.md` alternates and `MECHANISM_IDEATION.md`
   unranked candidates. Score them under the new constraints the failure introduced.
4. **Decide:** continue with a refined committed mechanism, switch to an alternate, or
   re-enter Stage 8 with new constraints.
5. **Codex collaborative** — adds revival candidates, identifies which alternates are now
   strengthened by the failure mode.

**Output artifact:** `FAILURE_TO_INNOVATION.md` containing:

```markdown
# Failure-to-Innovation

## What failed
- Run id, observed outcome, NULL_RESULT_CONTRACT category triggered

## Falsified assumptions
- Ledger entry A<id>: <text> — falsified because <reason>
- Ledger entry A<id>: ...
- (or: no ledger entry covered this; new entry A<new>: <text>)

## Inversion question
- Given <observed failure mode>, what mechanism family is now suggested?
- Candidate new mechanisms: <list>

## Revival evaluation
- Alternate S<id> from ALGORITHM_TOURNAMENT now scores higher on diagnosability because <...>
- Unranked candidate M<id> from MECHANISM_IDEATION now scores higher on falsifiability
  because <...>

## Decision
- (a) refine committed mechanism with constraint <X>
- (b) switch to alternate S<id>
- (c) re-enter Stage 8 with new constraints <list>

## Codex collaborative additions
- ...
```

**Anti-pattern (G17):** do **not** write the new mechanism into `CLAIM_CONSTRUCTION.md`
or the paper as if it were a pre-planned hypothesis. Failure-to-innovation outputs are
exploratory findings until they are validated by a fresh diagnostic; Stage 21 must label
them as such.

## §6. Loop E — Re-read Literature (Stage 19)

**Trigger:** orchestrator routes to Stage 19 when `RESULT_INTERPRETATION.md` or
`FAILURE_TO_INNOVATION.md` raises a question the literature might answer (e.g., "is this
failure mode known?", "has this regime been characterised?").

**Inputs:**
- `RESULT_INTERPRETATION.md` and/or `FAILURE_TO_INNOVATION.md`
- The questions surfaced in those artifacts

**Procedure:**

1. **Question-driven targeting.** Convert each surfaced question into a literature query.
   Avoid generic re-reading — be specific.
2. **Targeted /research-lit calls.** Use the existing `/research-lit` skill with the
   per-question queries. Pull 2–5 papers per question.
3. **Update `LITERATURE_REREAD_NOTE.md`** with: the question, the papers found, the answer
   the literature gave (or "no answer found"), and how the answer changes the next decision
   (revive a mechanism, refine a control, change a benchmark, abandon a direction).
4. **Reviewer:** none — the literature itself is the reviewer.

**Output artifact:** `LITERATURE_REREAD_NOTE.md` containing:

```markdown
# Literature Re-read Note

## Question 1
- Question: <text>
- Papers found: <list>
- Answer from literature: <text> | NO ANSWER FOUND
- Implication for next decision: <text>

## Question 2
...

## Decision impact
- Affects: which mechanism / control / benchmark
- Action: revive | refine | change | abandon
```

## §7. Collaborative Claude-Codex Innovation Mode

The default Codex mode in ORBIT is **adversarial**: Codex is the independent semantic auditor
defined in `semantic-code-audit.md`. That mode is right for commitment, plan-code audit,
red-team, and result-to-claim — gates where the executor must not judge its own work.

But adversarial review is the wrong shape for invention. During innovation loops Codex
**does not veto**. It contributes. The mode switch happens at Stages 8, 9, 10, and 18.5;
Codex switches back to adversarial at Stages 11, 14, 15, 17, 21, and 23.

### Mode switching rule (orchestrator-side)

```
IF current_stage IN {8, 9, 10, 18.5}:
    codex_mode = COLLABORATIVE
    use prompt template §7.1 below
ELSE IF current_stage IN {11, 14, 15, 17, 21, 23}:
    codex_mode = ADVERSARIAL
    use semantic-code-audit.md template
ELSE:
    codex_mode = (unused — these stages don't invoke Codex)
```

### §7.1 Collaborative-mode prompt template (Codex side)

Pass to `mcp__codex__codex` (model `gpt-5.5`, reasoning `xhigh`, sandbox
`danger-full-access`):

```
You are a collaborative research innovator working alongside Claude.

We are inventing, not committing. Your role is to expand the candidate space, not narrow it.

Rules:
- DO add candidate mechanisms / analogies / sketches Claude may have missed.
- DO identify blind spots — mechanism families neither of us has considered.
- DO suggest alternative framings that change what falsifiability looks like.
- DO NOT veto Claude's candidates. Convergence happens at the commitment gate downstream.
- DO NOT prune the candidate list. Add to it.
- DO mark each addition with: novelty (1-5), feasibility (1-5), falsifiability (1-5).

Inputs: <attached file paths to MECHANISM_IDEATION.md / ANALOGY_TRANSFER.md / etc.>

Output format: a list of additions only. Do not rewrite Claude's candidates. Append to
the existing artifact under a "## Codex collaborative additions" section.
```

### §7.2 Adversarial-mode prompt template (Codex side)

Adversarial-mode templates live in `semantic-code-audit.md` (plan-code audit, diagnostic-run
audit) and `research-harness-prompts.md` (red-team, result-to-claim debate). This file does
not redefine them; it only documents that adversarial mode resumes outside the innovation
loops.

### §7.3 Why this mode exists

A reviewer that vetoes during invention will collapse the candidate set to the one mechanism
that survives the strictest critique — usually the most conservative, least diagnostic
candidate. That is exactly the outcome v1.3 is trying to prevent. Collaborative mode keeps
the candidate set wide; the commitment gates downstream pick the one most worth running
under the (then-active) adversarial review.

### §7.4 Configuration

Codex defaults are unchanged across modes:

- `model = gpt-5.5`
- `reasoning_effort = xhigh`
- `sandbox_mode = danger-full-access`
- review reasoning is always `xhigh` regardless of effort axis

Only the prompt template changes between collaborative and adversarial modes. The MCP call
itself is identical.
