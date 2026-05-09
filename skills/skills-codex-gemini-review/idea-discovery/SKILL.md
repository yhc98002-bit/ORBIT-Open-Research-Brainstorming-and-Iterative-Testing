---
name: "idea-discovery"
description: "Workflow 1: Full idea discovery pipeline. Orchestrates research-lit \u2192 idea-creator \u2192 novelty-check \u2192 research-review to go from a broad research direction to ranked, non-experimental idea candidates. Use when user says \\\"\u627eidea\u5168\u6d41\u7a0b\\\", \\\"idea discovery pipeline\\\", \\\"\u4ece\u96f6\u5f00\u59cb\u627e\u65b9\u5411\\\", or wants the complete idea exploration workflow."
---

> Override for Codex users who want **Gemini**, not a second Codex agent, to act as the reviewer. Install this package **after** `skills/skills-codex/*`.

# Workflow 1: Idea Discovery Pipeline

Orchestrate a complete idea discovery workflow for: **$ARGUMENTS**

## Overview

This skill chains sub-skills into a single automated pipeline:

```
/research-lit → /idea-creator → /novelty-check → /research-review → /research-refine
  (survey)      (brainstorm)    (verify novel)    (critical feedback)  (refine proposal)
```

Each phase builds on the previous one's output. The final deliverables are a ranked
`idea-stage/IDEA_REPORT.md` with candidate ideas plus a refined proposal
(`refine-logs/FINAL_PROPOSAL.md`) for the top idea. Experiment planning happens later in
`/experiment-bridge` after STOP A.

## Constants

- **NO_PRE_STOP_A_EXPERIMENTS = true** — ORBIT v1.4+ idea discovery is non-experimental.
  Do not run experiments, do not use GPU, and do not call `/run-experiment` before STOP A.
  Formal experiment planning begins in `/experiment-bridge` after STOP A.
- **IDEA_RANKING_CRITERIA** — Rank by literature grounding, novelty, feasibility,
  mechanism plausibility, baseline/headroom reasoning, expected diagnostic clarity, and
  reviewer critique.
- **AUTO_PROCEED = true** — If user doesn't respond at a checkpoint, automatically proceed with the best option after presenting results. Set to `false` to always wait for explicit user confirmation.
- **OUTPUT_DIR = `idea-stage/`** — All idea-stage outputs go here. Create the directory if it doesn't exist.
- **REVIEWER_MODEL = `gemini-review`** — Gemini reviewer invoked through the local `gemini-review` MCP bridge. Passed to the reviewer-aware sub-skills installed by this overlay.
- **ARXIV_DOWNLOAD = false** — When `true`, `/research-lit` downloads the top relevant arXiv PDFs during Phase 1. When `false` (default), only fetches metadata. Passed through to `/research-lit`.

> 💡 These are defaults. Override by telling the skill, e.g., `/idea-discovery "topic" — arxiv download: true`.

## Pipeline

### Phase 1: Literature Survey

Invoke `/research-lit` to map the research landscape:

```
/research-lit "$ARGUMENTS"
```

**What this does:**
- Search arXiv, Google Scholar, Semantic Scholar for recent papers
- Build a landscape map: sub-directions, approaches, open problems
- Identify structural gaps and recurring limitations
- Output a literature summary (saved to working notes)

**🚦 Checkpoint:** Present the landscape summary to the user. Ask:

```
📚 Literature survey complete. Here's what I found:
- [key findings, gaps, open problems]

Does this match your understanding? Should I adjust the scope before generating ideas?
(If no response, I'll proceed with the top-ranked direction.)
```

- **User approves** (or no response + AUTO_PROCEED=true) → proceed to Phase 2 with best direction.
- **User requests changes** (e.g., "focus more on X", "ignore Y", "too broad") → refine the search with updated queries, re-run `/research-lit` with adjusted scope, and present again. Repeat until the user is satisfied.

### Phase 2: Idea Generation + Filtering

Invoke `/idea-creator` with the landscape context:

```
/idea-creator "$ARGUMENTS"
```

**What this does:**
- Brainstorm 8-12 concrete ideas via the Gemini-backed `/idea-creator` overlay
- Filter by feasibility, compute cost, quick novelty search
- Deep screen top ideas (full novelty check + devil's advocate)
- Rank by literature grounding, novelty, feasibility, mechanism plausibility,
  baseline/headroom, expected diagnostic clarity, and reviewer critique
- Output `idea-stage/IDEA_REPORT.md`

No experiments are run in `/idea-discovery`. No GPU is used in `/idea-discovery`.
Formal experiment planning begins in `/experiment-bridge` after STOP A.

**🚦 Checkpoint:** Present `idea-stage/IDEA_REPORT.md` ranked ideas to the user. Ask:

```
💡 Generated X ideas, filtered to Y. Top results:

1. [Idea 1] — Novelty: CONFIRMED; Feasibility: HIGH; Expected diagnostic clarity: HIGH; Reviewer risk: LOW
2. [Idea 2] — Novelty: UNCLEAR; Feasibility: MEDIUM; Expected diagnostic clarity: MEDIUM; Reviewer risk: MEDIUM
3. [Idea 3] — Novelty: CONFLICTING; Feasibility: LOW; Expected diagnostic clarity: LOW; Reviewer risk: HIGH

Which ideas should I check further? Or should I regenerate with different constraints?
(If no response, I'll proceed with the top-ranked ideas.)
```

- **User picks ideas** (or no response + AUTO_PROCEED=true) → proceed to Phase 3 with top-ranked ideas.
- **User unhappy with all ideas** → collect feedback ("what's missing?", "what direction do you prefer?"), update the prompt with user's constraints, and re-run Phase 2 (idea generation). Repeat until the user selects at least 1 idea.
- **User wants to adjust scope** → go back to Phase 1 with refined direction.

### Phase 3: Deep Novelty Verification

For each top idea that passes novelty and feasibility filters, run a thorough novelty
check:

```
/novelty-check "[top idea 1 description]"
/novelty-check "[top idea 2 description]"
```

**What this does:**
- Multi-source literature search (arXiv, Scholar, Semantic Scholar)
- Cross-verify with the Gemini-backed `/novelty-check` overlay
- Check for concurrent work (last 3-6 months)
- Identify closest existing work and differentiation points

**Update `idea-stage/IDEA_REPORT.md`** with deep novelty results. Eliminate any idea that turns out to be already published.

### Phase 4: External Critical Review

For the surviving top idea(s), get brutal feedback:

```
/research-review "[top idea with hypothesis + literature/novelty/feasibility evidence]"
```

**What this does:**
- Gemini acts as a senior reviewer (NeurIPS/ICML level) via the local `gemini-review` MCP bridge
- Scores the idea, identifies weaknesses, suggests minimum viable improvements
- Provides concrete feedback on experimental design

**Update `idea-stage/IDEA_REPORT.md`** with reviewer feedback and revised plan.

### Phase 4.5: Method Refinement

After review, refine the top idea into a concrete proposal:

```
/research-refine "[top idea description + literature/novelty/feasibility evidence + reviewer feedback]"
```

**What this does:**
- Freeze a **Problem Anchor** to prevent scope drift
- Iteratively refine the method via Gemini review (up to 5 rounds, until score ≥ 9)
- Output: `refine-logs/FINAL_PROPOSAL.md`, `refine-logs/FINAL_PROPOSAL_SHORT.md`, and
  `refine-logs/METHOD_SPEC.md` when useful

**🚦 Checkpoint:** Present the refined proposal summary:

```
Method refined and proposal ready:
- Problem anchor: [anchored problem]
- Method thesis: [one sentence]
- Dominant contribution: [what's new]

Proceed to STOP A review, then /experiment-bridge if approved? Or adjust the proposal?
```

- **User approves** (or AUTO_PROCEED=true) → proceed to Final Report.
- **User requests changes** → pass feedback to `/research-refine` for another round.
- **Legacy full-planning mode:** If the user explicitly asks for the old one-shot
  proposal+plan package, use `/research-refine-pipeline`; otherwise keep planning in
  `/experiment-bridge` after STOP A.

### Phase 5: Final Report

Finalize `idea-stage/IDEA_REPORT.md` with all accumulated information:

```markdown
# Idea Discovery Report

**Direction**: $ARGUMENTS
**Date**: [today]
**Pipeline**: research-lit → idea-creator → novelty-check → research-review → research-refine

## Executive Summary
[2-3 sentences: best idea, key literature/novelty/feasibility/reviewer basis, recommended next step]

## Literature Landscape
[from Phase 1]

## Ranked Ideas
[from Phase 2, updated with Phase 3-4 results]

### 🏆 Idea 1: [title] — RECOMMENDED
- Novelty: CONFIRMED / UNCLEAR / CONFLICTING (closest: [paper], differentiation: [what's different])
- Feasibility: HIGH / MEDIUM / LOW
- Reviewer score: X/10
- Reviewer risk: LOW / MEDIUM / HIGH
- Expected diagnostic: [what would be tested later in /experiment-bridge]
- Next step: STOP A review, then `/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"`

### Idea 2: [title] — BACKUP
...

## Eliminated Ideas
[ideas killed at each phase, with reasons]

## Refined Proposal
- Proposal: `refine-logs/FINAL_PROPOSAL.md`

## Next Steps
- [ ] /experiment-bridge "refine-logs/FINAL_PROPOSAL.md" after STOP A approval
- [ ] /diagnostic-to-review after STOP B
- [ ] Or invoke /research-pipeline for the complete end-to-end flow
```

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../../shared-references/output-versioning.md)** — follow selective milestone timestamping rules
> - **[Output Manifest Protocol](../../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Large file handling**: If the Write tool fails due to file size, immediately retry using Bash (`cat << 'EOF' > file`) to write in chunks. Do NOT ask the user for permission — just do it silently.

- **Don't skip phases.** Each phase filters and validates — skipping leads to wasted effort later.
- **Checkpoint between phases.** Briefly summarize what was found before moving on.
- **Kill ideas early.** It's better to kill 10 bad ideas in Phase 3 than to implement one and fail.
- **Do not confuse plausible idea-selection evidence with experimental evidence.**
- **Before STOP A, rank ideas by literature grounding, novelty, feasibility, mechanism
  plausibility, baseline/headroom, and expected diagnostic clarity.**
- **Experimental evidence begins only after `/experiment-bridge` defines a valid
  experiment plan and `/diagnostic-to-review` runs formal diagnostics.**
- **Document everything.** Dead ends are just as valuable as successes for future reference.
- **Be honest with the reviewer.** Include known risks, rejected ideas, and reviewer
  concerns in the review prompt.
- **Feishu notifications are optional.** If `~/.codex/feishu.json` exists, send `checkpoint` at each phase transition and `pipeline_done` at final report. If absent/off, skip silently.

## Composing with Workflow 2

After this pipeline produces a ranked top idea:

```
/idea-discovery "direction"         ← you are here (Workflow 1, includes method refinement)
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"  ← STOP B plan + implement + audit
/diagnostic-to-review "<diagnostic command>"         ← formal diagnostic + review routing

Or use /research-pipeline for the full end-to-end flow.
```
