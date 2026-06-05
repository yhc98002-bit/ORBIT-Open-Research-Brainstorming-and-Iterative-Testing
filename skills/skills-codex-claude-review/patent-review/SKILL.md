---
name: "patent-review"
description: "Get an external patent examiner review of a patent application. Use when user says \"专利审查\", \"patent review\", \"审查意见\", \"examiner review\", or wants critical feedback on patent claims and specification."
allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit, Agent
---

> Override for Codex users who want **Claude Code CLI**, not a second Codex agent, to act as the reviewer/helper. Install this package **after** `skills/skills-codex/*`.

Whenever the upstream skill asks for an external reviewer/helper, write the complete focused prompt to `$PROMPT_FILE`. For a one-shot independent review, run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

For multi-round reviewer discussion, keep automation non-interactive but preserve continuity with `--session-id` on the first call and `--resume` on follow-up calls; see `../shared-references/claude-cli-review.md`.

# Patent Examiner Review via Claude CLI reviewer (xhigh reasoning)

Get a multi-round patent examiner review of the patent application based on: **$ARGUMENTS**

Adapted from `/research-review`. The reviewer persona is a patent examiner, not a paper reviewer.

## Constants

- `REVIEWER_MODEL = claude-cli` — Model used via Claude CLI reviewer
- `REVIEW_ROUNDS = 2` — Number of review rounds
- `EXAMINER_PERSONA = "patent-examiner"` — GPT-5.5 persona

## Prerequisites

- Install the base Codex-native skills first: copy `skills/skills-codex/*` into `~/.codex/skills/`.
- Then install this overlay package: copy `skills/skills-codex-claude-review/*` into `~/.codex/skills/` and allow it to overwrite the same skill names.
- Ensure the `claude` CLI is available:
  ```bash
  claude --version
  ```
- Reviews and helper critiques use direct `claude -p` calls. Use fresh calls for independent review and `--session-id` / `--resume` for multi-round discussion; see `../shared-references/claude-cli-review.md`.

  ```bash
  make the `claude` CLI available and authenticated
  ```

## Inputs

1. `patent/CLAIMS.md` — all drafted claims
2. `patent/specification/` — all specification sections
3. `patent/figures/numeral_index.md` — reference numeral mapping
4. `patent/PRIOR_ART_REPORT.md` — known prior art
5. `patent/INVENTION_DISCLOSURE.md` — invention structure

## Workflow

### Step 1: Gather Patent Context

Before calling the external reviewer, compile a comprehensive briefing:
1. Read all claims (independent + dependent)
2. Read specification sections (at least summary and detailed description)
3. Read prior art report for context
4. Identify: core inventive concept, claim scope, known prior art, target jurisdiction

### Step 2: Round 1 — Full Examiner Review

Send to `REVIEWER_MODEL` via `claude -p` with xhigh reasoning:

```text
Write the complete fresh Claude review/help prompt to `$PROMPT_FILE`.
Preserve the role, files-to-read, objective, and required output schema from this original call shape.

If this review may need later follow-up, create and save a Claude CLI session ID on this first call.

prompt: |
    You are a senior patent examiner at the [USPTO/CNIPA/EPO].
    Examine this patent application and issue a detailed office action.

    CLAIMS:
    [all claims]

    SPECIFICATION SUMMARY:
    [key sections: title, technical field, background, summary, abstract]

    PRIOR ART KNOWN:
    [prior art references]

    PATENTABILITY STANDARDS TO APPLY:
    [US: 35 USC 101/102/103/112 | CN: Articles 22, 26 | EP: Articles 54, 56, 83, 84]

    Please issue an office action covering:

    1. CLAIM CLARITY (112(b)/Art 84):
       - Are all terms definite?
       - Any indefinite functional language?
       - Antecedent basis issues?

    2. WRITTEN DESCRIPTION (112(a)/Art 83 first para):
       - Does the spec support ALL claim scope?
       - Any claim elements without spec support?

    3. ENABLEMENT (112(a)/Art 83):
       - Can a POSITA practice the invention?
       - Any missing algorithm/structure for functional claims?

    4. NOVELTY (102/Art 54):
       - Would any known reference anticipate any claim?
       - Identify the closest single reference.

    5. NON-OBVIOUSNESS (103/Art 56):
       - Would any combination render claims obvious?
       - What is the motivation to combine?

    6. CLAIM SCOPE:
       - Are independent claims broad enough to be commercially valuable?
       - Do dependent claims provide meaningful fallback positions?
       - Any claims that are too broad (likely rejected) or too narrow (not valuable)?

    7. SPECIFICATION QUALITY:
       - Language issues (subjective terms, relative terms, result-to-be-achieved)
       - Reference numeral consistency
       - Missing embodiments

    Format your response as a formal office action with:
    - GROUNDS OF REJECTION for each issue (cite statute)
    - SUGGESTED AMENDMENTS for each issue
    - OVERALL PATENTABILITY SCORE: 1-10

    Be rigorous and specific. This is a real examination.
```

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(python -c 'import uuid; print(uuid.uuid4())')}"
CLAUDE_SESSION_ID_FILE="${CLAUDE_SESSION_ID_FILE:-.aris/review-outputs/claude-session-id.txt}"
printf "%s\n" "$CLAUDE_SESSION_ID" > "$CLAUDE_SESSION_ID_FILE"
claude -p --session-id "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

### Step 3: Implement Fixes (Round 1)

Based on the examiner's office action:

1. **CRITICAL issues** (102 rejection, 112 indefiniteness, missing enablement):
   - Must be fixed before proceeding
   - Amend claims or add specification support

2. **MAJOR issues** (103 obviousness, weak claim scope, missing support):
   - Should be fixed or argued
   - Consider claim amendments or specification additions

3. **MINOR issues** (language quality, numeral consistency, formatting):
   - Fix if time permits
   - Document in output for later cleanup

For each fix:
- Show the specific change (old claim -> new claim)
- Explain how the fix addresses the examiner's concern

### Step 4: Round 2 — Follow-Up Review

Use `claude -p` with the Claude session ID from Round 1:

```text
Write the complete fresh Claude review/help prompt to `$PROMPT_FILE`.
Preserve the role, files-to-read, objective, and required output schema from this original call shape.

If this review may need later follow-up, create and save a Claude CLI session ID on this first call.

Claude session ID: [from Round 1]
  prompt: |
    Here is the revised patent application after addressing your office action.

    CHANGES MADE:
    [list of all changes with rationale]

    REVISED CLAIMS:
    [updated claims]

    REVISED SPECIFICATION EXCERPTS:
    [changed sections]

    Please re-examine:
    1. Are the previous rejections overcome?
    2. Are there new issues introduced by the amendments?
    3. What is the updated patentability score?
    4. Any remaining grounds for rejection?
```

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
CLAUDE_SESSION_ID="${CLAUDE_SESSION_ID:-$(python -c 'import uuid; print(uuid.uuid4())')}"
CLAUDE_SESSION_ID_FILE="${CLAUDE_SESSION_ID_FILE:-.aris/review-outputs/claude-session-id.txt}"
printf "%s\n" "$CLAUDE_SESSION_ID" > "$CLAUDE_SESSION_ID_FILE"
claude -p --session-id "$CLAUDE_SESSION_ID" --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

### Step 5: Generate Improvement Report

Write `patent/PATENT_REVIEW.md`:

```markdown
## Patent Review Report

### Application Summary
[Title, claims count, jurisdiction]

### Review Round 1
#### Office Action Summary
[Key findings from examiner]

#### Issues Found
| # | Type | Severity | Claim/Section | Issue | Citation | Fix Applied |
|---|------|----------|--------------|-------|----------|-------------|
| 1 | Clarity | CRITICAL | Claim 3 | Indefinite term "rapid" | 112(b) | Defined in spec |
| 2 | Novelty | MAJOR | Claim 1 | Ref X anticipates element C | 102 | Amended claim |

#### Score After Round 1: [X]/10

### Review Round 2
#### Follow-Up Assessment
[Are previous rejections overcome?]

#### Remaining Issues
[Any issues still outstanding]

#### Score After Round 2: [X]/10

### Recommendations
[Final recommendations before proceeding to jurisdiction formatting]
- [ ] All CRITICAL issues resolved
- [ ] All MAJOR issues resolved or argued
- [ ] Specification supports all claim amendments
- [ ] Ready for jurisdiction formatting
```

## Key Rules

- The reviewer persona must be a patent examiner, not a paper reviewer or academic.
- Always use `Claude CLI `--effort max`: "xhigh"` for maximum analysis depth.
- Address CRITICAL and MAJOR issues before proceeding to the next phase.
- Document all changes in the review report for traceability.
- If the patentability score is below 5/10 after Round 2, recommend significant rework before filing.
- The review is advisory -- actual prosecution may proceed differently.
