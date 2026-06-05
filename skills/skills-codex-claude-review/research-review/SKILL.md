---
name: "research-review"
description: "Get a deep critical review of research from Claude Code CLI via Claude Code CLI. Use when user says \"review my research\", \"help me review\", \"get external review\", or wants critical feedback on research ideas, papers, or experimental results."
allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit, Agent
---

> Override for Codex users who want **Claude Code CLI**, not a second Codex agent, to act as the reviewer/helper. Install this package **after** `skills/skills-codex/*`.

Whenever the upstream skill asks for an external reviewer/helper, write the complete focused prompt to `$PROMPT_FILE` and run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

# Research Review via Claude CLI reviewer (xhigh reasoning)

Get a multi-round critical review of research work from an external LLM with maximum reasoning depth.

## Constants

- **REVIEWER_MODEL = `claude-cli`** — Claude reviewer invoked through direct `claude -p` CLI calls following `../shared-references/claude-cli-review.md`.
- **REVIEWER_BACKEND = `codex`** — Default: Claude CLI reviewer (xhigh). Override with `— reviewer: oracle-pro` for GPT-5.5 Pro via Oracle MCP. See `../shared-references/reviewer-routing.md`.
- **PAPER_MODE = `normal`** — Default review target is a normal publishable AI paper,
  not breakthrough-only.
- **REVIEW_POSTURE = `collaborator` before STOP A/B; `adversarial` after STOP C** —
  Load `../shared-references/research-posture.md`.

## Context: $ARGUMENTS

## Prerequisites

- Install the base Codex-native skills first: copy `skills/skills-codex/*` into `~/.codex/skills/`.
- Then install this overlay package: copy `skills/skills-codex-claude-review/*` into `~/.codex/skills/` and allow it to overwrite the same skill names.
- Ensure the `claude` CLI is available:
  ```bash
  claude --version
  ```
- Reviews and helper critiques use direct `claude -p` calls; see `../shared-references/claude-cli-review.md`.

  ```bash
  make the `claude` CLI available and authenticated
  ```
- This gives Codex access to `claude -p` and a new `claude -p` invocation tools

## Workflow

### Review Posture Modes

- **development / collaborator** (default before STOP A and STOP B): act as a
  constructive research collaborator or paper director. Preserve promising ideas,
  classify risks, propose positioning routes, and identify the minimum evidence needed.
  Do not recommend abandonment unless a true `STRONG_BLOCKER` is present.
- **acceptance / adversarial** (default after STOP C, result-to-claim,
  auto-review-loop, and paper-writing): act as a senior adversarial reviewer. Stress-test
  claims, evidence, baselines, controls, and overclaiming.

### Step 1: Gather Research Context
Before calling the external reviewer, compile a comprehensive briefing:
1. Read project narrative documents (e.g., STORY.md, README.md, paper drafts)
2. Read any memory/notes files for key findings and experiment history
3. Identify: core claims, methodology, key results, known weaknesses

### Step 2: Initial Review (Round 1)
Send a detailed prompt with xhigh reasoning:

```text
Write the complete fresh Claude review/help prompt to `$PROMPT_FILE`.
Preserve the role, files-to-read, objective, and required output schema from this original call shape.


prompt: |
    [Full research context + specific questions]
    Use REVIEW_POSTURE from the current ORBIT stop boundary.

    If before STOP A or STOP B:
    You are a constructive research collaborator. Preserve promising ideas. Classify
    risks, propose positioning routes, and help turn the idea into a normal publishable
    paper. Do not simulate acceptance-stage red-team review unless explicitly asked. Do not recommend
    abandonment unless a true STRONG_BLOCKER is present.

    If after STOP C:
    You are a senior adversarial reviewer. Stress-test claims, evidence, baselines,
    controls, reproducibility, and overclaiming.

    Identify:
    1. Logical gaps or unjustified claims
    2. Minimal evidence needed for the selected paper mode
    3. Narrative weaknesses and positioning fixes
    4. Whether the work can survive as normal / benchmark / reproduction-plus / system / audit
```

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

### Step 3: Iterative Dialogue (Rounds 2-N)
Use a new `claude -p` invocation with the returned `claude_review_json_path` to continue the conversation:

For each round:
1. **Respond** to criticisms with evidence/counterarguments
2. **Ask targeted follow-ups** on the most actionable points
3. **Request specific deliverables**: experiment designs, paper outlines, claims matrices

Key follow-up patterns:
- "If we reframe X as Y, does that change your assessment?"
- "What's the minimum experiment to satisfy concern Z?"
- "Please design the minimal additional experiment package (highest acceptance lift per GPU week)"
- "Please write a mock NeurIPS/ICML review with scores"
- "Give me a results-to-claims matrix for possible experimental outcomes"

### Step 4: Convergence
Stop iterating when:
- Both sides agree on the core claims and their evidence requirements
- A concrete experiment plan is established
- The narrative structure is settled

### Step 5: Document Everything
Save the full interaction and conclusions to a review document in the project root:
- Round-by-round summary of criticisms and responses
- Final consensus on claims, narrative, and experiments
- Claims matrix (what claims are allowed under each possible outcome)
- Prioritized TODO list with estimated compute costs
- Paper outline if discussed

Update project memory/notes with key review conclusions.

## Key Rules

- ALWAYS use `config: {"Claude CLI `--effort max`": "xhigh"}` for reviews
- Send comprehensive context in Round 1 — the external model cannot read your files
- Be honest about weaknesses — hiding them leads to worse feedback
- Before STOP A/B, preserve promising ideas and include a survival route for every major
  concern.
- After STOP C, adversarial review is appropriate for paper-level claims.
- Push back on criticisms you disagree with, but accept valid ones
- Focus on ACTIONABLE feedback — "what experiment would fix this?"
- Document the agent id for potential future resumption
- The review document should be self-contained (readable without the conversation)

## Prompt Templates

### For initial development review:
"I'm going to present an early ML research direction. Please act as a constructive
research collaborator. Preserve promising ideas, classify risks, propose positioning
routes, and identify the minimal evidence needed for a normal publishable paper..."

### For post-STOP-C acceptance review:
"I'm going to present paper-level claims and evidence. Please act as a senior adversarial
ML reviewer and stress-test claims, baselines, controls, reproducibility, and overclaiming..."

### For experiment design:
"Please design the minimal additional experiment package that gives the highest acceptance lift per GPU week. Our compute: [describe]. Be very specific about configurations."

### For paper structure:
"Please turn this into a concrete paper outline with section-by-section claims and figure plan."

### For claims matrix:
"Please give me a results-to-claims matrix: what claim is allowed under each possible outcome of experiments X and Y?"

### For mock review:
"Please write a mock NeurIPS review with: Summary, Strengths, Weaknesses, Questions for Authors, Score, Confidence, and What Would Move Toward Accept."

## Review Tracing

After each `claude -p` or a new `claude -p` invocation reviewer call, save the trace following `../shared-references/review-tracing.md`. Resolve `save_trace.sh` via that shared resolver, or write files directly to `.aris/traces/<skill>/<date>_run<NN>/`. Respect the `--- trace:` parameter (default: `full`).
