---
name: idea-discovery
description: "Workflow 1: Full idea discovery pipeline. Orchestrates research-lit → idea-creator → novelty-check → research-review to go from a broad research direction to ranked, non-experimental idea candidates. Use when user says \"找idea全流程\", \"idea discovery pipeline\", \"从零开始找方向\", or wants the complete idea exploration workflow."
argument-hint: [research-direction]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill, mcp__codex__codex, mcp__codex__codex-reply
---

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
- **PAPER_MODE = `normal`** — Default to normal publishable AI paper mode; breakthrough
  mode is explicit opt-in only.
- **NOVELTY_POLICY = `positioning-first`** — Similar work is classified for positioning
  before any idea is discarded.
- **REVIEW_POSTURE = `collaborator`** — Before STOP A, reviewers act as constructive
  collaborators, not automatic rejection gatekeepers.
- **IDEA_RANKING_CRITERIA** — Rank by literature grounding, novelty posture, feasibility,
  mechanism plausibility, baseline/headroom reasoning, expected diagnostic clarity,
  paper-mode fit, and reviewer critique.
- **AUTO_PROCEED = true** — If user doesn't respond at a checkpoint, automatically proceed with the best option after presenting results. Set to `false` to always wait for explicit user confirmation.
- **REVIEWER_MODEL = `gpt-5.5`** — Model used via Codex MCP. ORBIT default is `gpt-5.5` with xhigh reasoning. Passed to sub-skills.
- **OUTPUT_DIR = `idea-stage/`** — All idea-stage outputs go here. Create the directory if it doesn't exist.
- **ARXIV_DOWNLOAD = false** — When `true`, `/research-lit` downloads the top relevant arXiv PDFs during Phase 1. When `false` (default), only fetches metadata. Passed through to `/research-lit`.
- **COMPACT = false** — When `true`, generate compact summary files for short-context models and session recovery. Writes `idea-stage/IDEA_CANDIDATES.md` (top 3-5 ideas only) at the end of this workflow. Downstream skills read this instead of the full `idea-stage/IDEA_REPORT.md`.
- **REF_PAPER = false** — Reference paper to base ideas on. Accepts: local PDF path, arXiv URL, or any paper URL. When set, the paper is summarized first (`idea-stage/REF_PAPER_SUMMARY.md`), then idea generation uses it as context. Combine with `base repo` for "improve this paper with this codebase" workflows.
- **REVIEW_DIFFICULTY = `medium`** — Accept `— difficulty: <medium|hard|nightmare>`
  or alias `— review-difficulty: <medium|hard|nightmare>`. Forward this only to
  downstream adversarial review/refinement stages (`/research-refine`); do not apply
  `hard` / `nightmare` to literature search, idea
  generation, novelty checks, feasibility ranking, or innovation loops.

> 💡 These are defaults. Override by telling the skill, e.g., `/idea-discovery "topic" — ref paper: https://arxiv.org/abs/2406.04329` or `/idea-discovery "topic" — compact: true`.

## ORBIT Problem Selection Gate

This gate is always-on. Before brainstorming, load:

- `shared-references/research-agent-pipeline.md`
- `shared-references/research-posture.md`
- `shared-references/research-harness-prompts.md` sections `0A`, `1`, and `0B`

This workflow must explicitly separate three things:

1. seed framing for broad areas
2. question-driven literature mapping
3. problem taste / problem selection

Run `mkdir -p orbit-research/`. Before finalizing the top idea, write
`orbit-research/PROBLEM_SELECTION.md` and evaluate each candidate by importance, audience,
concreteness, novelty, feasibility, benchmark availability, baseline ceiling risk, expected
headroom, diagnostic clarity, and paper survivability if the method fails or ties. End with
`PROCEED`, `NARROW`, or `RETHINK`.

## Pipeline

### Phase 0: Load Research Brief (if available)

Before starting any other phase, check for a detailed research brief in the project:

1. Look for `RESEARCH_BRIEF.md` in the project root (or path passed as `$ARGUMENTS`)
2. If found, read it and extract:
   - Problem statement and context
   - Constraints (compute, data, timeline, venue)
   - What the user already tried / what didn't work
   - Domain knowledge and non-goals
   - Existing results (if any)
3. Use this as the primary context for all subsequent phases — it replaces the one-line prompt
4. If both `RESEARCH_BRIEF.md` and a one-line `$ARGUMENTS` exist, merge them (brief takes priority for details, argument sets the direction)

If no brief exists, proceed normally with `$ARGUMENTS` as the research direction.

> 💡 Create a brief from the template: `cp templates/RESEARCH_BRIEF_TEMPLATE.md RESEARCH_BRIEF.md`

### Phase 0.5: Reference Paper Summary (when REF_PAPER is set)

**Skip entirely if `REF_PAPER` is `false`.**

Summarize the reference paper before searching the literature:

1. **If arXiv URL** (e.g., `https://arxiv.org/abs/2406.04329`):
   - Invoke `/arxiv "ARXIV_ID" — download` to fetch the PDF
   - Read the first 5 pages (title, abstract, intro, method overview)

2. **If local PDF path** (e.g., `papers/reference.pdf`):
   - Read the PDF directly (first 5 pages)

3. **If other URL**:
   - Fetch and extract content via WebFetch

4. **Generate `idea-stage/REF_PAPER_SUMMARY.md`**:

```markdown
# Reference Paper Summary

**Title**: [paper title]
**Authors**: [authors]
**Venue**: [venue, year]

## What They Did
[2-3 sentences: core method and contribution]

## Key Results
[Main quantitative findings]

## Limitations & Open Questions
[What the paper didn't solve, acknowledged weaknesses, future work suggestions]

## Potential Improvement Directions
[Based on the limitations, what could be improved or extended?]

## Codebase
[If `base repo` is also set: link to the repo and note which parts correspond to the paper]
```

**🚦 Checkpoint:** Present the summary to the user:

```
📄 Reference paper summarized:
- Title: [title]
- Key limitation: [main gap]
- Improvement directions: [2-3 bullets]

Proceeding to literature survey with this as context.
```

Phase 1 and Phase 2 will use `idea-stage/REF_PAPER_SUMMARY.md` as additional context — `/research-lit` searches for related and competing work, `/idea-creator` generates ideas that build on or improve the reference paper.

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

Invoke `/idea-creator` with the landscape context (and `idea-stage/REF_PAPER_SUMMARY.md` if available):

```
/idea-creator "$ARGUMENTS"
```

**What this does:**
- If `idea-stage/REF_PAPER_SUMMARY.md` exists, include it as context — ideas should build on, improve, or extend the reference paper
- Brainstorm 8-12 concrete ideas via GPT-5.5 xhigh
- Filter by feasibility, compute cost, quick novelty-posture search, and diagnostic clarity
- Deep screen top ideas (full novelty positioning check + collaborator critique)
- Rank by literature grounding, novelty posture, feasibility, mechanism plausibility,
  baseline/headroom, expected diagnostic clarity, paper-mode fit, and reviewer critique
- Output `idea-stage/IDEA_REPORT.md`

No experiments are run in `/idea-discovery`. No GPU is used in `/idea-discovery`.
Formal experiment planning begins in `/experiment-bridge` after STOP A.

**🚦 Checkpoint:** Present `idea-stage/IDEA_REPORT.md` ranked ideas to the user. Ask:

```
💡 Generated X ideas, filtered to Y. Top results:

1. [Idea 1] — Novelty posture: CLEAR_SPACE; Feasibility: HIGH; Expected diagnostic clarity: HIGH; Reviewer risk: LOW
2. [Idea 2] — Novelty posture: RELATED_BUT_DIFFERENT; Feasibility: MEDIUM; Expected diagnostic clarity: MEDIUM; Reviewer risk: MEDIUM
3. [Idea 3] — Novelty posture: WEAK_BLOCKER; Feasibility: LOW; Expected diagnostic clarity: LOW; Reviewer risk: HIGH

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
- Cross-verify with GPT-5.5 xhigh
- Check for concurrent work (last 3-6 months)
- Identify closest existing work and differentiation points

**Update `idea-stage/IDEA_REPORT.md`** with deep novelty positioning results. Eliminate
an idea only if `/novelty-check` classifies a true `STRONG_BLOCKER` or if feasibility /
diagnostic clarity fails. Route recent non-blocking work to
`orbit-research/CONCURRENT_WORK_WATCHLIST.md`.

### Phase 4: External Critical Review

For the surviving top idea(s), get constructive collaborator feedback:

```
/research-review "[top idea with hypothesis + literature/novelty/feasibility evidence]"
```

**What this does:**
- GPT-5.5 xhigh acts as a constructive research collaborator before STOP A
- Classifies risks, proposes positioning fixes, and identifies minimum evidence
- Provides concrete feedback on the expected diagnostic design after STOP A

**Update `idea-stage/IDEA_REPORT.md`** with reviewer feedback and revised plan.

### Phase 4.5: Method Refinement

After review, refine the top idea into a concrete proposal:

```
/research-refine "[top idea description + literature/novelty/feasibility evidence + reviewer feedback]" \
  — difficulty: <parsed difficulty or review-difficulty>
```

**What this does:**
- Freeze a **Problem Anchor** to prevent scope drift
- Iteratively refine the method via GPT-5.5 review (up to 5 rounds, until score ≥ 9)
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
- **User requests changes** → pass feedback to `/research-refine` for another round,
  forwarding `— difficulty` / `— review-difficulty` if the user set it.
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
[2-3 sentences: best idea, key literature/novelty-posture/feasibility/reviewer basis, recommended next step]

## Literature Landscape
[from Phase 1]

## Ranked Ideas
[from Phase 2, updated with Phase 3-4 results]

### 🏆 Idea 1: [title] — RECOMMENDED
- Novelty posture: CLEAR_SPACE / RELATED_BUT_DIFFERENT / CONCURRENT_WORK / WEAK_BLOCKER / POSITIONING_TARGET / REPRODUCTION_TARGET / STRONG_BLOCKER
- Feasibility: HIGH / MEDIUM / LOW
- Reviewer score: X/10
- Reviewer risk: LOW / MEDIUM / HIGH
- Expected diagnostic: [what would be tested later in /experiment-bridge]
- Paper-mode fit: normal / benchmark / reproduction-plus / system / focused mechanism / breakthrough
- Next step: STOP A review, then `/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"`

### Idea 2: [title] — BACKUP
...

## Eliminated Ideas
[ideas rejected at each phase, with reasons; related-but-different ideas should be positioned unless a STRONG_BLOCKER exists]

## Refined Proposal
- Proposal: `refine-logs/FINAL_PROPOSAL.md`

## Next Steps
- [ ] /experiment-bridge "refine-logs/FINAL_PROPOSAL.md" after STOP A approval
- [ ] /diagnostic-to-review after STOP B
- [ ] Or invoke /research-pipeline for the complete end-to-end flow
```

### Phase 5.5: Write Compact Files (when COMPACT = true)

**Skip entirely if `COMPACT` is `false`.**

Write `idea-stage/IDEA_CANDIDATES.md` — a lean summary of the top 3-5 surviving ideas:

```markdown
# Idea Candidates

| # | Idea | Novelty posture | Feasibility | Paper-mode fit | Diagnostic clarity | Reviewer risk | Status |
|---|------|-----------------|-------------|----------------|--------------------|---------------|--------|
| 1 | [title] | CLEAR_SPACE | HIGH | normal | HIGH | LOW | RECOMMENDED |
| 2 | [title] | RELATED_BUT_DIFFERENT | MEDIUM | reproduction-plus | MEDIUM | MEDIUM | BACKUP |
| 3 | [title] | WEAK_BLOCKER | LOW | unclear | LOW | HIGH | ELIMINATED |

## Active Idea: #1 — [title]
- Hypothesis: [one sentence]
- Key evidence: literature + novelty posture + feasibility + reviewer assessment
- Expected diagnostic: [what would be tested later in /experiment-bridge]
- Next step: /experiment-bridge "refine-logs/FINAL_PROPOSAL.md" or /research-refine
```

This file is intentionally small (~30 lines) so downstream skills and session recovery can read it without loading the full `idea-stage/IDEA_REPORT.md` (~200+ lines).

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — apply selective milestone timestamping rules
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Large file handling**: If the Write tool fails due to file size, immediately retry using Bash (`cat << 'EOF' > file`) to write in chunks. Do NOT ask the user for permission — just do it silently.

- **Don't skip phases.** Each phase filters and validates — skipping leads to wasted effort later.
- **Checkpoint between phases.** Briefly summarize what was found before moving on.
- **Preserve opportunity early.** It is better to reposition promising ideas than to
  discard them prematurely for normal related work.
- **Do not confuse plausible idea-selection evidence with experimental evidence.**
- **Before STOP A, rank ideas by literature grounding, novelty posture, feasibility,
  mechanism plausibility, baseline/headroom, expected diagnostic clarity, and paper-mode
  fit.**
- **Do not abandon merely because related or concurrent work exists.** Use
  `CONCURRENT_WORK_WATCHLIST.md` and positioning unless a true `STRONG_BLOCKER` is found.
- **Experimental evidence begins only after `/experiment-bridge` defines a valid
  experiment plan and `/diagnostic-to-review` runs formal diagnostics.**
- **Document everything.** Dead ends are just as valuable as successes for future reference.
- **Be honest with the reviewer.** Include known risks, rejected ideas, and reviewer
  concerns in the review prompt.
- **Feishu notifications are optional.** If `~/.claude/feishu.json` exists, send `checkpoint` at each phase transition and `pipeline_done` at final report. If absent/off, skip silently.

## Composing with Workflow 2

After this pipeline produces a ranked top idea:

```
/idea-discovery "direction"         ← you are here (Workflow 1, includes method refinement)
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"  ← STOP B plan + implement + audit
/diagnostic-to-review "<diagnostic command>"         ← formal diagnostic + review routing

Or use /research-pipeline for the full end-to-end flow.
```

## Stage-Chain Integration (Stage 0-1 Contract)

This integration is always-on (no longer conditional on `/research-pipeline` invocation).
Always emit these normalized stage artifacts so downstream skills (experiment-bridge,
result-to-claim, paper-writing) can pick them up regardless of how the user enters the
pipeline:

- `PROBLEM.md` — distilled from idea-stage findings + refined problem anchor
- `HYPOTHESIS.md` — hypothesis space, assumptions, and failure signals
- `FINAL_PROPOSAL.md` — copy/normalize from `refine-logs/FINAL_PROPOSAL.md`
- `REVIEW/CONSISTENCY_REPORT.md` — structured Stage-1 check report

Use this mandatory check template before handing off to STOP A / experiment planning:

```text
Check FINAL_PROPOSAL.md against PROBLEM_SELECTION.md and ASSUMPTION_LEDGER.md.
Check:
1. Is the proposal anchored to the selected problem?
2. Are variables and method scope clearly defined?
3. Are central factual/method/benchmark/paper-bearing claims represented in the ledger?
4. Is this proposal worth formal experiment planning?
Return structured inconsistencies.
```
