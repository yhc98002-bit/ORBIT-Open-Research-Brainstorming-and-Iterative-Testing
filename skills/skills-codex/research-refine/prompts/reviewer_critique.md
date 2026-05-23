---
id: research-refine.reviewer-critique.v1
used_by: research-refine phase 2
purpose: Run the Codex/GPT-5.5 elegance-first method review without weakening difficulty routing.
inputs:
  - full initial or revised proposal
  - venue
  - paper_mode
  - reviewer_difficulty
outputs:
  - refine-logs/round-N-review.md
  - parsed score and verdict
---

### Phase 2: External Method Review (Round 1)

Send the full proposal to GPT-5.5 for an **elegance-first, frontier-aware, method-first** review. The reviewer should spend most of the critique budget on the method itself, not on expanding the experiment menu.

If the Codex MCP call fails, do not produce a local substitute review. Export a standalone
handoff prompt per `../shared-references/codex-precondition.md` §5.5 using
`tools/codex_review_handoff.py`, write it under
`orbit-research/codex-prompts/<phase-id>.md`, and require the user to save the standalone
Codex response to `orbit-research/codex-imports/<phase-id>.response.md` before importing
with `/import-codex-review`.

**Route by REVIEWER_DIFFICULTY and REVIEW_POSTURE** before composing the prompt:
- `medium` (default): use the collaborator prompt below as-is.
- `hard`: before STOP A, use stronger collaborator review and require survival routes;
  raise the verdict bar from "score ≥ 9" to "score ≥ 9.5"; allow up to MAX_ROUNDS = 7
  rounds.
- `nightmare`: before STOP A, interpret as strong collaborator review unless the user
  explicitly sets `— review-posture: adversarial` or the workflow is after STOP C. In
  adversarial mode, add per-dimension vetoes.

```
mcp__codex__codex:
  model: REVIEWER_MODEL
  config: {"model_reasoning_effort": REVIEWER_EFFORT}     // honors `— effort:` flag; default "xhigh"
  prompt: |
    You are a constructive senior ML research collaborator and paper director for {VENUE_PHRASE}.
    This is an early-stage, method-first research proposal.
    Default paper mode is {PAPER_MODE}. In normal mode, judge against a clean,
    honest, publishable AI paper bar, not a breakthrough-only bar.

    [INSERT difficulty-escalation paragraph here when REVIEWER_DIFFICULTY ∈ {hard, nightmare}]
    [INSERT per-dimension veto clause here only when REVIEW_POSTURE = adversarial]

    Your job is NOT to reward extra modules, contribution sprawl, or a giant benchmark checklist.
    Your job IS to stress-test whether the proposed method:
    (1) still solves the original anchored problem,
    (2) is concrete enough to implement,
    (3) presents a focused, elegant contribution,
    (4) uses foundation-model-era techniques appropriately when they are the natural fit.

    Review principles:
    - Prefer the smallest adequate mechanism over a larger system.
    - Penalize parallel contributions that make the paper feel unfocused.
    - Similar work is not fatal by default; classify novelty risk and propose positioning.
    - For every major criticism, include a survival route and the minimal evidence needed.
    - Do not recommend abandonment unless a true STRONG_BLOCKER is present.
    - If a modern LLM / VLM / Diffusion / RL route would clearly produce a better paper, say so concretely.
    - If the proposal is already modern enough, do NOT force trendy components.
    - Do not ask for extra experiments unless they are needed to prove the core claims.

    Read the Problem Anchor first. If your suggested fix would change the problem being solved,
    call that out explicitly as drift instead of treating it as a normal revision request.

    === PROPOSAL ===
    [Paste the FULL proposal from Phase 1]
    === END PROPOSAL ===

    Score these 7 dimensions from 1-10:

    1. **Problem Fidelity**: Does the method still attack the original bottleneck, or has it drifted into solving something easier or different?

    2. **Method Specificity**: Are the interfaces, representations, losses, training stages, and inference path concrete enough that an engineer could start implementing?

    3. **Contribution Quality**: Is there one dominant mechanism-level contribution with real novelty, good parsimony, and no obvious contribution sprawl?

    4. **Frontier Leverage**: Does the proposal use current foundation-model-era primitives appropriately when they are the right tool, instead of defaulting to old-school module stacking?

    5. **Feasibility**: Can this method be trained and integrated with the stated resources and data assumptions?

    6. **Validation Focus**: Are the proposed experiments minimal but sufficient to validate the core claims? Is there unnecessary experimental bloat?

    7. **Paper-Mode Fit**: If executed well, would the contribution survive as a normal / benchmark / reproduction-plus / system / focused mechanism paper under {VENUE_PHRASE} expectations?

    **OVERALL SCORE** (1-10): Weighted toward Problem Fidelity, Method Specificity, Contribution Quality, and Frontier Leverage.
    Use this weighting: Problem Fidelity 15%, Method Specificity 25%, Contribution Quality 25%, Frontier Leverage 15%, Feasibility 10%, Validation Focus 5%, Paper-Mode Fit 5%.

    For each dimension scoring < 7, provide:
    - The specific weakness
    - A concrete fix at the method level (interface / loss / training recipe / integration point / deletion of unnecessary parts)
    - A survival route, unless the issue is a true STRONG_BLOCKER
    - Priority: CRITICAL / IMPORTANT / MINOR

    Then add:
    - **Simplification Opportunities**: 1-3 concrete ways to delete, merge, or reuse components while preserving the main claim. Write "NONE" if already tight.
    - **Modernization Opportunities**: 1-3 concrete ways to replace old-school pieces with more natural foundation-model-era primitives if genuinely better. Write "NONE" if already modern enough.
    - **Drift Warning**: "NONE" if the proposal still solves the anchored problem; otherwise explain the drift clearly.
    - **Verdict**: READY / REVISE / RETHINK

    Verdict rule:
    - READY: overall score >= SCORE_THRESHOLD, no meaningful drift, one focused dominant contribution, and no obvious complexity bloat remains
    - REVISE: the direction is promising but not yet at READY bar
    - RETHINK: the core mechanism or framing is still fundamentally off
    [If REVIEW_POSTURE = adversarial and REVIEWER_DIFFICULTY = nightmare, additionally
    return REVISE when any single dimension scores < 8 even if overall >= SCORE_THRESHOLD.]
```

**Variable substitution before sending the prompt**:
- `{VENUE_PHRASE}` = `VENUE` if `VENUE != ""` else `"a normal ML venue target (NeurIPS/ICML/ICLR-style expectations without breakthrough-only assumptions)"`.
  Examples: `VENUE = "ICLR"` → `"ICLR"`; `VENUE = "IEEE_JOURNAL"` → `"IEEE_JOURNAL"`;
  `VENUE = ""` → `"a normal ML venue target (NeurIPS/ICML/ICLR-style expectations without breakthrough-only assumptions)"`.
- `SCORE_THRESHOLD` = the difficulty-derived numeric threshold (medium = 9, hard /
  nightmare = 9.5).
- `REVIEWER_EFFORT` = the effort level parsed from `— effort:` (default `xhigh`).
- `PAPER_MODE` = parsed from `— paper-mode:` (default `normal`).
- `REVIEW_POSTURE` = parsed from `— review-posture:` or inferred from stop boundary.

### REVIEWER_DIFFICULTY routing — escalation paragraphs

Insert the relevant block(s) into the reviewer prompt depending on
`REVIEWER_DIFFICULTY`:

**For `hard` and `nightmare` before STOP A — strong collaborator paragraph:**

```
DIFFICULTY: HARD. Apply a stronger collaborator review. Specifically:
- Do not let "interesting" carry weight against "focused"; sprawl is the
  primary failure mode at this bar and must be flagged in the Verdict, not
  buried in Simplification Opportunities.
- Frontier-leverage incompleteness must be called out: if the proposal could
  be strengthened by a foundation-model-era primitive that is currently
  missing, that is a CRITICAL issue, not a Modernization Opportunity.
- Validation focus: a single non-decisive experiment in the validation plan
  must be flagged CRITICAL — every claim must have a falsifiable predicate
  with a Cohen's-d threshold or equivalent.
- Raise the verdict bar to overall score >= 9.5 for READY.
- Still provide a positioning fix and survival route for every major concern.
```

**For adversarial `nightmare` only — per-dimension veto clause (added after STOP C or explicit request):**

```
DIFFICULTY: NIGHTMARE with REVIEW_POSTURE = adversarial. Every individual
dimension (Problem Fidelity, Method Specificity, Contribution Quality,
Frontier Leverage, Feasibility, Validation Focus, Paper-Mode Fit) must
independently score >= 8 for READY — overall score >= 9.5 is necessary but
not sufficient. If any single dimension is < 8, the verdict must be REVISE
or RETHINK regardless of the overall score, and the reviewer must list the
specific dimension(s) below 8 in the Verdict line.
```

**CRITICAL: Save the `threadId`** from this call for all later rounds.

**CRITICAL: Save the FULL raw response** verbatim.

Save review to `refine-logs/round-1-review.md` with the raw response in a `<details>` block.

**Checkpoint:** Update `refine-logs/REFINE_STATE.json` with `{"phase": "review", "round": 1, "threadId": "<saved>", "last_score": <parsed>, "last_verdict": "<parsed>", ...}`.
