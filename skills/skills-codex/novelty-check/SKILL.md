---
name: novelty-check
description: Verify research idea novelty against recent literature. Use when user says "查新", "novelty check", "有没有人做过", "check novelty", or wants to verify a research idea is novel before implementing.
argument-hint: [method-or-idea-description]
allowed-tools: WebSearch, WebFetch, Grep, Read, Glob, mcp__codex__codex
---

# Novelty Check Skill

Classify novelty risk and positioning routes for: **$ARGUMENTS**

## Constants

- REVIEWER_MODEL = `gpt-5.5` — Model used via Codex MCP. Must be an OpenAI model (e.g., `gpt-5.5`, `o3`, `gpt-4o`)
- **NOVELTY_POLICY = `positioning-first`** — Load `../shared-references/research-posture.md`
  before judging novelty. Similar work is not automatically fatal.
- **CONCURRENT_WORK_WINDOW = `3 months`** — Recent work goes to
  `orbit-research/CONCURRENT_WORK_WATCHLIST.md` by default.

## Instructions

Given a method description, systematically classify its novelty posture:

### Phase A: Extract Key Claims
1. Read the user's method description
2. Identify 3-5 central factual/method/benchmark/paper-bearing claims whose novelty matters:
   - What is the method?
   - What problem does it solve?
   - What is the mechanism?
   - What makes it different from obvious baselines?
   - What contribution type is being attempted: normal method, empirical finding,
     benchmark/baseline, reproduction-plus, system, focused mechanism, or breakthrough?

### Phase B: Multi-Source Literature Search
For EACH core claim, search using ALL available sources:

1. **Web Search** (via `WebSearch`):
   - Search arXiv, Google Scholar, Semantic Scholar
   - Use specific technical terms from the claim
   - Try at least 3 different query formulations per claim
   - Include year filters for 2024-2026

2. **Known paper databases**: Check against:
   - ICLR 2025/2026, NeurIPS 2025, ICML 2025/2026
   - Recent arXiv preprints (2025-2026)

3. **Read abstracts**: For each potentially overlapping paper, WebFetch its abstract and related work section

### Phase C: Cross-Model Positioning Review
Call REVIEWER_MODEL via Codex MCP (`mcp__codex__codex`) with xhigh reasoning:
```
config: {"model_reasoning_effort": "xhigh"}
```
Prompt should include:
- The proposed method description
- All papers found in Phase B
- The default posture from `../shared-references/research-posture.md`
- Ask:
  "Classify novelty posture using CLEAR_SPACE / RELATED_BUT_DIFFERENT /
  CONCURRENT_WORK / WEAK_BLOCKER / STRONG_BLOCKER / POSITIONING_TARGET /
  REPRODUCTION_TARGET. What is the closest prior work, what overlaps, how reliable is
  it, and what survival/positioning route remains?"

### Phase D: Positioning Report
Output a structured report:

```markdown
## Novelty Positioning Report

### Proposed Method
[1-2 sentence description]

### Core Claims
1. [Claim 1] — Novelty Posture: [class] — Closest: [paper] — Survival route: [route]
2. [Claim 2] — Novelty Posture: [class] — Closest: [paper] — Survival route: [route]
...

### Closest Prior Work
| Paper | Date | Venue / Status | Overlap Dimensions | Reliability | Code/Data | Reproducible? | Novelty Posture |
|-------|------|----------------|--------------------|-------------|-----------|---------------|-----------------|

### Overall Novelty Posture
- Score: X/10
- Novelty Posture: CLEAR_SPACE / RELATED_BUT_DIFFERENT / CONCURRENT_WORK / WEAK_BLOCKER / STRONG_BLOCKER / POSITIONING_TARGET / REPRODUCTION_TARGET
- Blocker strength: NONE / WEAK / STRONG
- Strong blocker criteria met: YES / NO
- Key differentiator: [what makes this unique, if anything]
- Risk: [what a reviewer would cite as prior work]
- Prior-work reliability: peer-reviewed / arXiv-only / recent concurrent / unpublished / partially open
- Public detail: sufficient / partial / missing
- Code/data availability: available / partial / unavailable

### Positioning Route
[How to frame the contribution without overclaiming]

### Survival Route
[For every non-strong-blocker, at least one viable route: narrower regime, stronger
evidence, reproduction-plus, benchmark/baseline, system, mechanism analysis, or
conditional empirical finding]

### Concurrent Work Watchlist
[If any work is from the last 3 months, add or recommend adding it to
orbit-research/CONCURRENT_WORK_WATCHLIST.md. Do not rewrite the proposal unless it is a
STRONG_BLOCKER.]
```

### Important Rules
- Be honest but opportunity-preserving. Your job is to classify novelty risk and find
  viable positioning, not to kill promising ideas prematurely.
- Do not recommend abandonment unless the `STRONG_BLOCKER` criteria in
  `../shared-references/research-posture.md` are met.
- For every non-strong-blocker, propose at least one positioning strategy.
- "Applying X to Y" can be a valid normal-paper route when the setting, evidence, control
  design, or finding is interesting and honest.
- Check both the method AND the experimental setting for novelty
- If the method overlaps prior work but the FINDING would be differentiated, say so explicitly
- Always check the most recent 6 months of arXiv; treat work from the last 3 months as
  concurrent by default and add it to the watchlist
- After STOP A, ordinary new related work should not destabilize a frozen proposal. Use
  the watchlist unless the work is a `STRONG_BLOCKER`.

## Review Tracing

After each `mcp__codex__codex` or `mcp__codex__codex-reply` reviewer call, save the trace following `../shared-references/review-tracing.md`. Resolve `save_trace.sh` via that shared resolver, or write files directly to `.aris/traces/<skill>/<date>_run<NN>/`. Respect the `--- trace:` parameter (default: `full`).
