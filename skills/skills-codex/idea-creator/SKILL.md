---
name: idea-creator
description: Generate and rank research ideas given a broad direction. Use when user says "找idea", "brainstorm ideas", "generate research ideas", "what can we work on", or wants to explore a research area for publishable directions.
argument-hint: [research-direction]
allowed-tools: Bash(*), Read, Write, Grep, Glob, WebSearch, WebFetch, Agent, mcp__codex__codex, mcp__codex__codex-reply
---

# Research Idea Creator

Generate publishable research ideas for: $ARGUMENTS

## Overview

Given a broad research direction from the user, systematically generate, screen, and rank
concrete research ideas. This skill composes with `/research-lit`, `/novelty-check`, and
`/research-review` to form a non-experimental idea discovery pipeline.

Load `../shared-references/research-posture.md` before screening. Default to normal paper
mode, positioning-first novelty, and collaborator review before STOP A.

## Constants

- **NO_PRE_STOP_A_EXPERIMENTS = true** — ORBIT v1.4+ idea creation is non-experimental.
  Do not run experiments, do not use GPU, and do not call `/run-experiment` before STOP A.
- **PAPER_MODE = `normal`** — Breakthrough novelty is explicit opt-in only.
- **NOVELTY_POLICY = `positioning-first`** — Related work is classified for positioning
  before any idea is dropped.
- **REVIEW_POSTURE = `collaborator`** — Before STOP A, review should preserve promising
  directions and propose survival routes.
- **IDEA_RANKING_CRITERIA** — Literature grounding, novelty posture, feasibility,
  mechanism plausibility, baseline/headroom, expected diagnostic clarity, paper-mode fit,
  and reviewer critique.
- **REVIEWER_MODEL = `gpt-5.5`** — Model used via Codex MCP for brainstorming and review. Must be an OpenAI model (e.g., `gpt-5.5`, `o3`, `gpt-4o`).
- **REVIEWER_BACKEND = `codex`** — Default: Codex MCP (xhigh). Override with `— reviewer: oracle-pro` for GPT-5.5 Pro via Oracle MCP. See `../shared-references/reviewer-routing.md`.
- **OUTPUT_DIR = `idea-stage/`** — All idea-stage outputs go here. Create the directory if it doesn't exist.

> 💡 This skill does not run experiments. Formal experiment planning starts in
> `/experiment-bridge` after STOP A.

## Workflow

### Phase 0: Load Research Wiki (if active)

**Skip this phase entirely if `research-wiki/` does not exist.**

If `research-wiki/` exists, resolve the canonical helper using the
shared resolution chain (see `../research-wiki/SKILL.md` for the
contract):

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1
if [ -z "${ARIS_REPO:-}" ] && [ -f .aris/installed-skills.txt ]; then
  ARIS_REPO=$(awk -F'\t' '$1=="repo_root"{print $2; exit}' .aris/installed-skills.txt 2>/dev/null) || true
fi
WIKI_SCRIPT=".aris/tools/research_wiki.py"
[ -f "$WIKI_SCRIPT" ] || WIKI_SCRIPT="tools/research_wiki.py"
if [ ! -f "$WIKI_SCRIPT" ]; then
  if [ -n "${ORBIT_REPO:-}" ] && [ -f "$ORBIT_REPO/tools/research_wiki.py" ]; then
    WIKI_SCRIPT="$ORBIT_REPO/tools/research_wiki.py"
  elif [ -n "${ARIS_REPO:-}" ] && [ -f "$ARIS_REPO/tools/research_wiki.py" ]; then
    WIKI_SCRIPT="$ARIS_REPO/tools/research_wiki.py"
  fi
fi
[ -f "$WIKI_SCRIPT" ] || {
  echo "WARN: research_wiki.py not found at .aris/tools/, tools/, \$ORBIT_REPO/tools/, or \$ARIS_REPO/tools/." >&2
  echo "      The idea-creation primary output (idea ranking) will still be produced." >&2
  echo "      Wiki integration (load query_pack, write idea pages, add edges, rebuild query_pack) will be skipped." >&2
  echo "      Fix: rerun 'bash tools/install_aris.sh', export ORBIT_REPO/ARIS_REPO, or 'cp <ARIS-repo>/tools/research_wiki.py tools/'." >&2
  WIKI_SCRIPT=""
}
```

```
if research-wiki/query_pack.md exists AND is less than 7 days old:
    Read query_pack.md and use it as initial landscape context:
    - Treat listed gaps as priority search seeds
    - Treat failed ideas as a banlist (do NOT regenerate similar ideas)
    - Treat top papers as known prior work (do not re-search them)
    Still run Phase 1 below for papers from the last 3-6 months (wiki may be stale)
else if research-wiki/ exists but query_pack.md is stale or missing:
    if [ -n "$WIKI_SCRIPT" ]: python3 "$WIKI_SCRIPT" rebuild_query_pack research-wiki/
    Then read query_pack.md as above
```

### Phase 1: Landscape Survey (5-10 min)

Map the research area to understand what exists and where the gaps are.

1. **Scan local paper library first**: Check `papers/` and `literature/` in the project directory for existing PDFs. Read first 3 pages of relevant papers to build a baseline understanding before searching online. This avoids re-discovering what the user already knows.

2. **Search recent literature** using WebSearch:
   - Top venues in the last 2 years (NeurIPS, ICML, ICLR, ACL, EMNLP, etc.)
   - Recent arXiv preprints (last 6 months)
   - Use 5+ different query formulations
   - Read abstracts and introductions of the top 10-15 papers

2. **Build a landscape map**:
   - Group papers by sub-direction / approach
   - Identify what has been tried and what hasn't
   - Note recurring limitations mentioned in "Future Work" sections
   - Flag any open problems explicitly stated by multiple papers

3. **Identify structural gaps**:
   - Methods that work in domain A but haven't been tried in domain B
   - Contradictory findings between papers (opportunity for resolution)
   - Assumptions that everyone makes but nobody has tested
   - Scaling regimes that haven't been explored
   - Diagnostic questions that nobody has asked

### Phase 2: Idea Generation (brainstorm with external LLM)

Use the external LLM via Codex MCP for divergent thinking:

```
mcp__codex__codex:
  model: REVIEWER_MODEL
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    You are a senior ML researcher brainstorming research ideas.

    Research direction: [user's direction]

    Here is the current landscape:
    [paste landscape map from Phase 1]

    Key gaps identified:
    [paste gaps from Phase 1]

    Generate 8-12 concrete research ideas. For each idea:
    1. One-sentence summary
    2. Core hypothesis (what you expect to find and why)
    3. Expected diagnostic after STOP A (what would be tested later?)
    4. Expected contribution type: empirical finding / method combination / benchmark + baseline / reproduction-plus / system / focused mechanism / theoretical result
    5. Risk level: LOW (likely works) / MEDIUM (50-50) / HIGH (speculative)
    6. Estimated effort: days / weeks / months

    Prioritize ideas that are:
    - Plausibly testable after formal planning with moderate compute
    - Likely to produce a clear positive OR negative result (both are publishable)
    - Compatible with normal publishable AI paper mode; no breakthrough requirement by default
    - Not eliminated merely because related work exists or the method is a simple combination
    - "Apply X to Y" is acceptable when the setting, evidence, or finding would be interesting
    - Differentiated from the 10-15 papers above

    Filter intelligently; preserve promising directions with viable positioning. A great
    idea is one where the answer matters regardless of which way it goes.
```

Save the threadId for follow-up.

### Phase 3: First-Pass Filtering

For each generated idea, quickly evaluate:

1. **Feasibility check**: Could this become a valid experiment after STOP A with available resources?
   - Compute requirements (estimate total cost and likely hardware class)
   - Data availability
   - Implementation complexity
   - Skip ideas requiring excessive compute or unavailable datasets

2. **Novelty quick-check**: For each idea, do 2-3 targeted searches and classify novelty
   posture: CLEAR_SPACE / RELATED_BUT_DIFFERENT / CONCURRENT_WORK / WEAK_BLOCKER /
   STRONG_BLOCKER / POSITIONING_TARGET / REPRODUCTION_TARGET. Full `/novelty-check`
   comes later for survivors.

3. **Impact estimation**: Would a reviewer care about the result?
   - "So what?" test: if the later diagnostic succeeds, does it change how people think?
   - Is the finding actionable or just interesting?

Eliminate only ideas that fail feasibility/diagnostic clarity or have a true
`STRONG_BLOCKER`. Related-but-different ideas should be repositioned, not discarded.
Typically 8-12 ideas reduce to 4-6.

### Phase 4: Deep Screening (for top ideas)

For each surviving idea, run a deeper evaluation:

1. **Novelty check**: Use the `/novelty-check` workflow (multi-source search + GPT-5.5 cross-verification) for each idea

2. **Critical review**: Use GPT-5.5 via `mcp__codex__codex-reply` (same thread):
   ```
   Here are our top ideas after filtering:
   [paste surviving ideas with novelty check results]

   For each, act as a constructive research collaborator:
   - What's the strongest concern, and what positioning fix would address it?
   - What's the most likely failure mode?
   - What minimum evidence would make this a normal publishable paper?
   - Could it survive as method combination, empirical finding, benchmark + baseline,
     reproduction-plus, system, or focused mechanism paper?
   - Which 2-3 would you actually work on?
   ```

3. **Combine rankings**: Merge your assessment with GPT-5.5's ranking. Select top 2-3
   ideas for proposal refinement using literature grounding, novelty posture, feasibility,
   mechanism plausibility, baseline/headroom, expected diagnostic clarity, paper-mode fit,
   and collaborator critique.

### Phase 5: Decision-Ready Ranking (no experiments)

Before STOP A, do not run experiments. At this stage the project usually lacks selected
model files/checkpoints, dataset paths/splits, evaluator definitions, baseline commands,
control design, null-result contract, experiment plan, and implementation contract.

1. **Define expected diagnostics**: For each top idea, state the cheapest diagnostic that
   would be designed later in `/experiment-bridge`.
   - What model/data/evaluator assumptions would need to become explicit?
   - What baseline or control would make the result interpretable?
   - What null result would weaken or reframe the idea?
   - What result pattern would be diagnostic rather than anecdotal?

2. **Score diagnostic clarity**:
   - HIGH: clear measurable contrast, available benchmark/control, interpretable failure.
   - MEDIUM: plausible contrast but missing some setup details.
   - LOW: result would be ambiguous, uncontrolled, or mostly anecdotal.

3. **Re-rank without execution**: Update the idea ranking from the combined literature,
   novelty posture, feasibility, mechanism, baseline/headroom, diagnostic-clarity,
   paper-mode fit, and collaborator-review evidence.

Do not use `/run-experiment`, `/monitor-experiment`, or GPU resources in this phase.

### Phase 6: Output — Ranked Idea Report

Write a structured report to `idea-stage/IDEA_REPORT.md`:

```markdown
# Research Idea Report

**Direction**: [user's research direction]
**Generated**: [date]
**Ideas evaluated**: X generated → Y survived filtering → W recommended

## Landscape Summary
[3-5 paragraphs on the current state of the field]

## Recommended Ideas (ranked)

### Idea 1: [title]
- **Hypothesis**: [one sentence]
- **Expected diagnostic after STOP A**: [what would be designed later in /experiment-bridge]
- **Expected outcome pattern**: [what success/failure would look like later]
- **Novelty posture**: [class] — closest work: [paper] — positioning route: [route]
- **Feasibility**: [compute, data, implementation estimates]
- **Baseline/headroom**: [simple strong baseline and expected ceiling]
- **Expected diagnostic clarity**: HIGH/MEDIUM/LOW
- **Risk**: LOW/MEDIUM/HIGH
- **Contribution type**: empirical / method combination / benchmark + baseline / reproduction-plus / system / focused mechanism / theory
- **Reviewer's likely objection**: [strongest counterargument]
- **Why we should do this**: [1-2 sentences]

### Idea 2: [title]
...

## Eliminated Ideas (for reference)
| Idea | Reason eliminated |
|------|-------------------|
| ... | Strong blocker: [paper] |
| ... | Requires unavailable data or excessive compute |
| ... | Result wouldn't be interesting either way |

## Ranking Rationale
| Idea | Novelty posture | Feasibility | Paper-mode fit | Baseline/headroom | Diagnostic clarity | Reviewer risk |
|------|-----------------|-------------|----------------|-------------------|--------------------|---------------|
| Idea 1 | CLEAR_SPACE | HIGH | normal | GOOD | HIGH | LOW |
| Idea 2 | RELATED_BUT_DIFFERENT | MEDIUM | reproduction-plus | MEDIUM | MEDIUM | MEDIUM |
| Idea 3 | WEAK_BLOCKER | LOW | unclear | LOW | LOW | HIGH |

## Suggested Execution Order
1. Start with Idea 1 (best novelty/feasibility/diagnostic-clarity tradeoff)
2. Keep Idea 2 as backup if novelty can be clarified
3. Archive Idea 3 unless new literature changes the assessment

## Next Steps
- [ ] STOP A: review whether the top idea is worth formal experiment planning
- [ ] If approved, invoke /experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
- [ ] Use /diagnostic-to-review later for formal diagnostics and any paper-level evidence
```

## Phase 7: Write Ideas to Research Wiki (if active)

**Skip this phase entirely if `research-wiki/` does not exist.**

This is critical for spiral learning — without it, `ideas/` stays empty and re-ideation has no memory.

`$WIKI_SCRIPT` was resolved in Phase 0 above. If Phase 0 did not run
(no `research-wiki/`), this phase is skipped. If Phase 0 ran but the
resolution chain failed to find the helper (`$WIKI_SCRIPT` is empty),
the page-write step still runs (idea pages are plain markdown the
agent writes directly), but the edge / query-pack / log steps that
require the helper are skipped with a single warning.

```
if research-wiki/ exists:
    for each idea in recommended_ideas + eliminated_ideas:
        1. Create page: research-wiki/ideas/<idea_id>.md
           - node_id: idea:<id>
           - stage: proposed (or: archived)
           - outcome: unknown
           - based_on: [paper:<slug>, ...]
           - target_gaps: [gap:<id>, ...]
           - Include: hypothesis, proposed method, expected outcome

        2. Add edges (only if $WIKI_SCRIPT resolved):
           [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" add_edge research-wiki/ --from "idea:<id>" --to "paper:<slug>" --type inspired_by --evidence "..."
           [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" add_edge research-wiki/ --from "idea:<id>" --to "gap:<id>" --type addresses_gap --evidence "..."

    Rebuild query pack (only if $WIKI_SCRIPT resolved):
        [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" rebuild_query_pack research-wiki/
    Log (only if $WIKI_SCRIPT resolved):
        [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" log research-wiki/ "idea-creator wrote N ideas (M recommended, K eliminated)"

    if [ -z "$WIKI_SCRIPT" ]:
        echo "WARN: idea pages were written but edges / query_pack / log were skipped because research_wiki.py is unreachable (see Phase 0 warning above)." >&2
```

## Output Protocols

> Follow these shared protocols for all output files:
> - **[Output Versioning Protocol](../shared-references/output-versioning.md)** — apply selective milestone timestamping rules
> - **[Output Manifest Protocol](../shared-references/output-manifest.md)** — log every output to MANIFEST.md
> - **[Output Language Protocol](../shared-references/output-language.md)** — respect the project's language setting

## Key Rules

- **Large file handling**: If the Write tool fails due to file size, immediately retry using Bash (`cat << 'EOF' > file`) to write in chunks. Do NOT ask the user for permission — just do it silently.

- The user provides a DIRECTION, not an idea. Your job is to generate the ideas.
- Quantity first, quality second: brainstorm broadly, then filter intelligently; preserve
  promising directions with viable positioning.
- A good negative result is just as publishable as a positive one. Prioritize ideas where the answer matters regardless of direction.
- Do not confuse plausible idea-selection evidence with experimental evidence.
- Do not eliminate an idea merely because it is not a breakthrough, related work exists,
  it is a simple combination, or it applies X to Y. Drop it only for infeasibility,
  poor diagnostic clarity, or a true `STRONG_BLOCKER`.
- Always estimate compute cost. An idea that needs excessive compute is not actionable for most researchers.
- "Apply X to Y" needs a real setting/evidence/finding argument, but it is not
  automatically disqualifying in normal paper mode.
- Include eliminated ideas in the report — they save future time by documenting dead ends.
- **If the user's direction is too broad (e.g., "NLP", "computer vision", "reinforcement learning"), STOP and ask them to narrow it.** A good direction is 1-2 sentences specifying the problem, domain, and constraint — e.g., "factorized gap in discrete diffusion LMs" or "sample efficiency of offline RL with image observations". Without sufficient specificity, generated ideas will be too vague to run experiments on.

## Composing with Other Skills

After this skill produces the ranked report:
```
/idea-creator "direction"     → ranked ideas
/novelty-check "top idea"     → deep novelty verification (already done in Phase 4, but user can re-run)
/research-review "top idea"   → external critical feedback
/idea-to-proposal "top idea"  → proposal candidate
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md" → plan + implement after STOP A
/diagnostic-to-review "<command OR manifest>"       → formal diagnostics after STOP B
```

## Review Tracing

After each `mcp__codex__codex` or `mcp__codex__codex-reply` reviewer call, save the trace following `../shared-references/review-tracing.md`. Resolve `save_trace.sh` via that shared resolver, or write files directly to `.aris/traces/<skill>/<date>_run<NN>/`. Respect the `--- trace:` parameter (default: `full`).
