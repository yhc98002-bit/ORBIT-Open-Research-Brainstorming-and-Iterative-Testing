---
name: "patent-novelty-check"
description: "Assess patent novelty and non-obviousness against prior art. Use when user says \"专利查新\", \"patent novelty\", \"可专利性评估\", \"patentability check\", or wants to evaluate if an invention is patentable."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch
---

> Override for Codex users who want **Claude Code CLI**, not a second Codex agent, to act as the reviewer/helper. Install this package **after** `skills/skills-codex/*`.

Whenever the upstream skill asks for an external reviewer/helper, write the complete focused prompt to `$PROMPT_FILE` and run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

# Patent Novelty and Non-Obviousness Check

Assess patentability of: **$ARGUMENTS**

Adapted from `/novelty-check` for patent legal standards. Research novelty is NOT the same as patent novelty.

## Constants

- `REVIEWER_MODEL = claude-cli` — Model used via Claude CLI reviewer for cross-model examiner verification
- `NOVELTY_STANDARD = patent` — Always use legal patentability standard, not research contribution standard

## Inputs

1. Invention description from `$ARGUMENTS`
2. `patent/PRIOR_ART_REPORT.md` (output of `/prior-art-search`)
3. `patent/INVENTION_BRIEF.md` if exists

## Shared References

Load `../shared-references/patent-writing-principles.md` for novelty/non-obviousness standards.
Load `../shared-references/patent-format-us.md` for 102/103 analysis framework.

## Workflow

### Step 1: Define Claim Elements

From the invention description, extract the key claim elements that would define the invention's scope:
1. List the technical features that make the invention novel
2. Identify which features are known from prior art vs. inventive
3. Draft preliminary claim language for 2-3 independent claims (method + system)

### Step 2: Anticipation Analysis (Novelty)

For each preliminary claim, test against EACH prior art reference in `PRIOR_ART_REPORT.md`:

**Single-reference test**: Does any single reference disclose ALL claim elements?

| Claim Element | Ref 1 | Ref 2 | Ref 3 | ... |
|--------------|-------|-------|-------|-----|
| Feature A | Yes/No + evidence | | | |
| Feature B | Yes/No + evidence | | | |
| Feature C | Yes/No + evidence | | | |
| Feature D | Yes/No + evidence | | | |

**Verdict per reference**:
- ANTICIPATED: One reference discloses every element → claim is not novel
- NOT ANTICIPATED: At least one element missing from every single reference → claim is novel

### Step 3: Obviousness Analysis (Inventive Step)

If the invention is novel (passes Step 2), test for obviousness:

**Two/three-reference combination test**: Can 2-3 references be combined to render the claim obvious?

For each combination of the top references:
1. **Primary reference**: Which reference is closest to the claimed invention?
2. **Secondary reference(s)**: Which reference(s) teach the missing element(s)?
3. **Motivation to combine**: Would a POSITA have reason to combine these references?
   - Explicit suggestion in the references themselves?
   - Same field, same problem?
   - Common design incentive?
   - Known technique for improving similar devices?

Format as a matrix:

| Combination | Primary | Secondary | Missing Elements | Motivation to Combine | Obvious? |
|-------------|---------|-----------|-----------------|----------------------|----------|
| Ref1 + Ref2 | Ref1 | Ref2 | Feature D | Same field, similar problem | Yes/No |

### Step 4: Cross-Model Examiner Verification

Call `REVIEWER_MODEL` via `claude -p` with xhigh reasoning:

```text
Write the complete fresh Claude review/help prompt to `$PROMPT_FILE`.
Preserve the role, files-to-read, objective, and required output schema from this original call shape.


prompt: |
    You are a senior patent examiner at the [USPTO/CNIPA/EPO].
    Examine the following invention for patentability.

    INVENTION: [invention description + preliminary claims]

    PRIOR ART: [prior art references with key teachings]

    Please analyze:
    1. Anticipation (novelty): Does any single reference anticipate any claim?
    2. Obviousness: Can any combination of references render claims obvious?
    3. Claim scope: Are the claims broad enough to be valuable?
    4. Recommended amendments if any claim is rejected.
    Be rigorous and cite specific references.
```

```bash
PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"
RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"
mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.

### Step 5: Jurisdiction-Specific Assessment

For each target jurisdiction, provide a patentability assessment:

**Under 35 USC 102/103 (US)**:
- Novelty: PASS / FAIL (cite specific reference if fail)
- Non-obviousness: PASS / FAIL (cite combination if fail)

**Under Article 22 CN Patent Law (CN)**:
- 新颖性 (Novelty): 通过 / 未通过
- 创造性 (Inventive Step): 通过 / 未通过

**Under Article 54/56 EPC (EP)**:
- Novelty: PASS / FAIL
- Inventive step: PASS / FAIL (problem-solution approach)

### Step 6: Output

Write `patent/NOVELTY_ASSESSMENT.md`:

```markdown
## Patentability Assessment

### Invention Summary
[description]

### Overall Assessment
[PATENTABLE / PATENTABLE WITH AMENDMENTS / NOT PATENTABLE]

### Anticipation Analysis
[claim-by-claim matrix against each reference]

### Obviousness Analysis
[combination analysis with motivation to combine]

### Cross-Model Examiner Review
[summary of GPT-5.5 examiner feedback]

### Recommended Claim Amendments
[If claims need modification to overcome prior art, suggest specific amendments]

### Risk Factors
[What could cause rejection during actual prosecution?]
```

## Key Rules

- Patent novelty is absolute: any public disclosure before the priority date counts as prior art, worldwide.
- Research novelty ("has anyone published this?") is NOT the same as patent novelty ("does any single reference teach every claim element?").
- Obviousness requires BOTH: (1) a combination of references AND (2) a motivation to combine them.
- Never assume the invention is patentable just because no identical patent exists.
- The assessment is advisory only -- actual prosecution may reveal different prior art.
- If `claude -p` is not available, skip cross-model examiner review and note it in the output.
