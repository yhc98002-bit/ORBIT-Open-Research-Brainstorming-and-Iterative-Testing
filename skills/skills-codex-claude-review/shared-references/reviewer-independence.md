# Reviewer Independence Protocol

## Core Principle

**Content must reach the reviewer unfiltered. The executor points to files and sets the review task; the reviewer reads and judges independently.**

Cross-model adversarial collaboration only works if the reviewer forms its own assessment from primary artifacts. If the executor pre-digests, summarizes, or interprets content before passing it to the reviewer, the reviewer is evaluating the executor's framing — not the actual work. This re-introduces the correlated blind spots that heterogeneous review is designed to avoid.

## What CAN be passed to the reviewer

- **Role/persona** — e.g., "Review as a NeurIPS-level reviewer"
- **Review objective** — e.g., "Evaluate publishability", "Check code correctness", "Score 1-10 on clarity"
- **File paths** — let the reviewer read file contents directly
- **Structural metadata** — e.g., "The paper has 8 sections", "Experiments are in experiments/"
- **Venue constraints** — e.g., "ICLR format, 9-page limit"

## What CANNOT be passed (counts as "subjective interference")

- ❌ Executor's summary or paraphrase of file contents
- ❌ Executor's interpretation of results (e.g., "I think the problem is...", "This suggests...")
- ❌ Executor's recommendations or conclusions (e.g., "I suggest changing...", "The likely cause is...")
- ❌ Key findings or bullet points extracted by the executor
- ❌ Leading questions (e.g., "Is this publishable?", "Is this trade-off reasonable?")
- ❌ Previous review rounds' feedback or critique (let the reviewer assess the current state fresh)
- ❌ Executor's description of what was changed since last round (e.g., "I fixed X, Y, Z")
- ❌ Statements asserting the current approach's strengths

## Why this matters

| With filtering | Without filtering |
|---|---|
| Reviewer sees executor's framing | Reviewer sees raw artifacts |
| Correlated blind spots persist | Genuinely independent assessment |
| Executor can "coach" favorable review | Review probes real weaknesses |
| Defeats the purpose of cross-model | Achieves adversarial collaboration |

## Correct pattern

```text
Write the complete fresh Claude review/help prompt to `$PROMPT_FILE`.
Preserve the role, files-to-read, objective, and required output schema from this original call shape.


prompt: |
    Review the following research project as a senior ML reviewer.

    Files to read:
    - Proposal: /path/to/PROPOSAL.md
    - Experiment results: /path/to/EXPERIMENT_LOG.md
    - Paper draft: /path/to/paper/main.tex
    - Code: /path/to/src/

    Please read all files yourself and provide a complete review.
    Score 1-10 on: novelty, soundness, clarity, significance.
```

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

## Incorrect pattern

```text
Write the complete fresh Claude review/help prompt to `$PROMPT_FILE`.
Preserve the role, files-to-read, objective, and required output schema from this original call shape.


prompt: |
    The main contribution is a new loss function that improves by 15%.
    However, I noticed the ablation is incomplete.
    Here's my summary of the key results: [...]
    Please review whether this is publishable.
```

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

## When to apply

This protocol applies to ALL cross-model review calls in ARIS:
- `/research-review` — paper review
- `/auto-review-loop` — iterative review
- `/paper-plan` — outline review
- `/paper-write` — section review
- `/paper-figure` — figure quality review
- `/rebuttal` — stress test
- `/meta-optimize` — patch review
- Any skill that sends artifacts to `claude -p` or a new `claude -p` invocation

## Exception

Multi-round review within the SAME thread (a new `claude -p` invocation) may reference the reviewer's own previous feedback to check resolution — but still must not include executor interpretations of that feedback.
