---
name: result-to-claim
description: Use when experiments complete to judge what claims the results support, what they don't, and what evidence is still missing. Codex MCP evaluates results against intended claims, writes claims/claim_ledger.json as the canonical claim/evidence binding, and routes to next action. Use after formal diagnostics finish and before paper writing or ablations.
argument-hint: [experiment-description-or-wandb-run]
allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit, mcp__codex__codex, mcp__codex__codex-reply
---

# Result-to-Claim Gate

Experiments produce numbers; this gate decides what those numbers *mean*. Collect results from available sources, get a Codex judgment, then auto-route based on the verdict.

## Context: $ARGUMENTS

## ORBIT Claim Construction Gate

This gate is always-on. Before paper writing, load:

- `../shared-references/research-agent-pipeline.md` — v1.3 stage map and hard gates G14, G16, G17, G18, G19
- `../shared-references/research-harness-prompts.md` sections `21`, `22`, and `25` (v1.3 numbering; old v1.0 sections `12`, `13`, `15` are mapped via the appendix)
- `../shared-references/reviewer-independence.md`
- `../shared-references/run-ledger.md` — verify evidence traces to ledgered `run_id`s

Run `mkdir -p claims orbit-research/`. Always write or update:

- `claims/claim_ledger.json` — canonical STOP C source of truth for claim → evidence →
  control → scope → limitation binding. Required before any paper-bearing diagnostic can
  hand off to paper writing.
- `claims/CLAIM_LEDGER.md` — human-readable generated view of the claim ledger.
- `orbit-research/CLAIM_CONSTRUCTION.md` — compatibility generated view during migration.
  It may be read by old skills, but it is not the source of truth when
  `claims/claim_ledger.json` exists.
- `orbit-research/AGENT_DECISION_RECOMMENDATION.md` — short note summarizing what is
  believed, what evidence supports it, what remains uncertain, agent's recommendation, and ending with one
  of `PROCEED / NARROW / REDESIGN / RE-READ / CHANGE BENCHMARK / STOP / HUMAN_DECISION_REQUIRED`.
  This is an agent recommendation, not a G15/G19 human gate artifact.
- `orbit-research/NEGATIVE_RESULT_STRATEGY.md` if the method ties, fails, or only partially
  supports the intended claim (Stage 22).

`claims/claim_ledger.json` must conform to `schemas/claim_ledger.schema.json` and include:

```jsonc
{
  "schema_version": "0.1",
  "status": "draft|ready|blocked|deprecated",
  "codex_review": "passed|pending|imported|degraded|not_required",
  "gating": true,
  "updated_at": "<ISO-8601 UTC>",
  "source_markdown": ["orbit-research/RESULT_INTERPRETATION.md"],
  "generated_views": ["claims/CLAIM_LEDGER.md", "orbit-research/CLAIM_CONSTRUCTION.md"],
  "result_refs": ["orbit-research/diagnostics/<diagnostic_id>/RUN_REPORT.md"],
  "claims": [
    {
      "id": "C1",
      "statement": "Evidence-bounded claim text.",
      "claim_role": "main_claim|supporting_claim|original_hypothesis|negative_result_claim|limitation|exploratory",
      "status": "supported|partial|unsupported|exploratory",
      "paper_use": "allowed|limitations_only|do_not_claim|future_work_only",
      "evidence_refs": ["run_id:<id>", "path/to/result.json"],
      "controls": ["baseline/control/run refs"],
      "scope": "datasets, regimes, metrics, and conditions where the claim is allowed",
      "limitations": ["known caveats"],
      "forbidden_overclaims": ["wording or scope that downstream paper writing must not use"],
      "allowed_paper_sections": ["results", "limitations"]
    }
  ]
}
```

Do **not** silently write `orbit-research/HUMAN_DECISION_NOTE.md` as if the user approved a
high-risk transition. G15/G19 require a human-authored or human-confirmed note with final
verdict `PROCEED` before scale-up, paper writing, or public release. If the user explicitly
supplies that decision in the current request, write `HUMAN_DECISION_NOTE.md` and include a
`Decision source:` line quoting/paraphrasing the user's approval.

Use the claim → evidence → control → scope → limitation chain in the ledger. Downgrade
claims when evidence is partial. If the result is negative, evaluate whether the contribution can
become benchmark diagnosis, baseline ceiling analysis, failure taxonomy, negative result,
regime map, evaluation protocol, task ontology contribution, or controlled reproduction.

**G14 inline check (mandatory):** if `orbit-research/NULL_RESULT_CONTRACT.md` triggered a
tie or failure outcome, **refuse to write positive framing** in `claims/claim_ledger.json`,
`CLAIM_LEDGER.md`, `CLAIM_CONSTRUCTION.md`, or `RESULT_INTERPRETATION.md`. Frame the result honestly per Stage 22 — invoke
`NEGATIVE_RESULT_STRATEGY.md` instead of forcing a success story. No exception.

**G17 inline check (mandatory):** if a result is being framed post-hoc as "what we
predicted" — i.e., the current claim emerged from `orbit-research/RESULT_INTERPRETATION.md`
or `orbit-research/FAILURE_TO_INNOVATION.md` rather than from a pre-registered hypothesis
in `orbit-research/CONTROL_DESIGN.md` — label it explicitly in `claims/claim_ledger.json`,
`CLAIM_LEDGER.md`, `CLAIM_CONSTRUCTION.md`, and any downstream paper as
**"exploratory finding, not pre-planned hypothesis."** Do NOT
present post-hoc reframings as pre-planned hypotheses. No exception.

## When to Use

- After a set of experiments completes (main results, not just sanity checks)
- Before committing to claims in a paper or review response
- When results are ambiguous and you need an objective second opinion

## Workflow

### Step 1: Collect Results

Gather experiment data from whatever sources are available in the project:

1. **RUN_LEDGER.jsonl**: canonical run provenance, terminal status, result files, logs,
   config, and `run_id`
2. **W&B**: `wandb.Api().run("<entity>/<project>/<run_id>").history()` — metrics, training curves, comparisons
3. **EXPERIMENT_LOG.md**: full results table with baselines and verdicts
4. **EXPERIMENT_TRACKER.md**: check which experiments are DONE vs still running
5. **Log files**: `ssh server "tail -100 /path/to/training.log"` if no other source
6. **docs/research_contract.md**: intended claims and experiment design

Assemble the key information:
- What experiments were run (method, dataset, config)
- Main metrics and baseline comparisons (deltas)
- The intended claim these experiments were designed to test
- Any known confounds or caveats
- Ledger coverage: which `run_id`s support this claim, which expected runs failed/OOMed,
  and whether any result file is orphaned or unledgered

### Step 2: Codex Judgment

Codex is required for the claim judgment. Follow
`../shared-references/codex-precondition.md`; do not accept a local
single-model substitute as satisfying this gate.

If Codex MCP/auth/sandbox is unavailable before or during this judgment, export a
standalone handoff prompt and pause:

```bash
python3 tools/codex_review_handoff.py generate \
  --repo . \
  --phase-id "result-to-claim.claim-evaluation" \
  --role "Independent Codex reviewer judging whether results support paper-bearing claims" \
  --file "claims/claim_ledger.json" \
  --file "RUN_LEDGER.jsonl" \
  --file "orbit-research/RESULT_INTERPRETATION.md" \
  --objective "Judge claim support from the available results and propose claim_ledger entries without overclaiming." \
  --output-format "Include VERDICT, claim_supported, confidence, claim_ledger_entries, missing_evidence, and forbidden_overclaims." \
  --required-section "VERDICT" \
  --required-section "claim_supported" \
  --required-section "claim_ledger_entries" \
  --output-artifact "orbit-research/CODEX_RESULT_TO_CLAIM_REVIEW.md" \
  --write-orbit-state
```

This writes `orbit-research/codex-prompts/result-to-claim.claim-evaluation.md`
and points `ORBIT_STATE.json` at:

```text
/import-codex-review orbit-research/codex-imports/result-to-claim.claim-evaluation.response.md
```

Do not mark `claims/claim_ledger.json` as `ready` until a Codex MCP response exists or
the standalone response has been imported with `/import-codex-review`.
Paper-bearing ledgers that satisfy downstream gates must keep `gating: true` and use
`codex_review: "passed"` or `"imported"`. If Codex is pending, degraded, or explicitly
not required, the ledger must remain non-gating (`status: "draft"` or `blocked`, or
`gating: false`) until the human explicitly accepts the degraded path.

Send the collected results to Codex for objective evaluation:

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  # Sandbox is set globally in ~/.codex/config.toml as sandbox_mode = "danger-full-access".
  # Codex MCP per-call config does not accept a sandbox key — see ../shared-references/reviewer-routing.md.
  prompt: |
    RESULT-TO-CLAIM EVALUATION

    I need you to judge whether experimental results support the intended claim.

    Intended claim: [the claim these experiments test]

    Experiments run:
    [list experiments with run_id, method, dataset, config, metrics]

    Results:
    [paste key numbers, comparison deltas, significance]

    Baselines:
    [baseline numbers and sources — reproduced or from paper]

    Known caveats:
    [any confounding factors, limited datasets, missing comparisons]

    Please evaluate:
    1. claim_supported: yes | partial | no
    2. what_results_support: what the data actually shows
    3. what_results_dont_support: where the data falls short of the claim
    4. missing_evidence: specific evidence gaps
    5. suggested_claim_revision: if the claim should be strengthened, weakened, or reframed
    6. next_experiments_needed: specific experiments to fill gaps (if any)
    7. confidence: high | medium | low
    8. claim_ledger_entries: proposed ledger rows with id, statement, claim_role
       (main_claim | supporting_claim | original_hypothesis | negative_result_claim |
       limitation | exploratory), support status (supported | partial | unsupported |
       exploratory), paper_use (allowed | limitations_only | do_not_claim |
       future_work_only), evidence_refs, controls, scope, limitations,
       forbidden_overclaims, and allowed_paper_sections

    Be honest. Do not inflate claims beyond what the data supports.
    A single positive result on one dataset does not support a general claim.
    If the method ties or fails, do not force a positive story. Encode the original
    unsupported hypothesis separately from any supported negative-result contribution.
```

### Step 3: Parse and Normalize

Extract structured fields from Codex response:

```markdown
- claim_supported: yes | partial | no
- support_status: supported | partial | unsupported | exploratory
- what_results_support: "..."
- what_results_dont_support: "..."
- missing_evidence: "..."
- suggested_claim_revision: "..."
- next_experiments_needed: "..."
- confidence: high | medium | low
- claim_ledger_entries:
  - id:
  - statement:
  - claim_role:
  - status:
  - paper_use:
  - evidence_refs:
  - controls:
  - scope:
  - limitations:
  - forbidden_overclaims:
  - allowed_paper_sections:
```

Normalize into `claims/claim_ledger.json`. Use:

- `status: "ready"` only when all `paper_use: "allowed"` primary paper-bearing claims
  are `supported` or intentionally `partial`/`exploratory` with explicit scope and
  forbidden overclaims.
- `status: "draft"` when evidence is still being reconciled or Codex review is pending.
- `status: "blocked"` only for invalid/corrupt evidence, missing provenance, or integrity
  failure that prevents a defensible ledger.
- If a draft ledger is written while waiting for standalone Codex import, it must include
  `codex_review: "pending"` and `gating: false`. This draft is a recovery aid, not a
  commitment artifact, and must not satisfy `/paper-from-claims` or `/submission-package`.
- If the user explicitly passes `— codex-required: false`, every output must carry visible
  degraded-mode markers, and the ledger must use `codex_review: "degraded"` and
  `gating: false` unless a later human decision explicitly accepts the degraded artifact.
- Unsupported original hypotheses are valid STOP C outcomes when encoded as
  `claim_role: "original_hypothesis"` with `paper_use: "do_not_claim"` or
  `paper_use: "limitations_only"`. They must not become main paper claims.
- Supported negative-result contributions must be separate rows with
  `claim_role: "negative_result_claim"` and may use `paper_use: "allowed"` only when the
  negative-result statement itself is supported by evidence.

Render `claims/CLAIM_LEDGER.md` from the JSON. During migration, also render
`orbit-research/CLAIM_CONSTRUCTION.md` from the same JSON instead of maintaining a
separate prose-only source.

### Step 3.5: Check Experiment Integrity (if audit exists)

**Skip this step if `EXPERIMENT_AUDIT.json` does not exist.**

```
if EXPERIMENT_AUDIT.json exists:
    read integrity_status from file
    attach to verdict output:
        integrity_status: pass | warn | fail

    if integrity_status == "fail":
        block claim_supported=yes for affected claims unless the result is explicitly
        marked proxy_evidence/invalid_evidence and excluded from primary support
        downgrade confidence to "low" regardless of Codex judgment

    if integrity_status == "warn":
        append to verdict: "[INTEGRITY: WARN] — audit flagged potential issues"
else:
    integrity_status = "unavailable"
    verdict is labeled "provisional — no integrity audit run"
    (this does NOT block anything — pipeline continues normally)
```

See `../shared-references/experiment-integrity.md` for the full integrity protocol.

If result files are not linked to `RUN_LEDGER.jsonl` run_ids, mark the evidence
`provisional_unledgered` and do not use it as primary claim support until the provenance is
reconciled.

### Step 4: Route Based on Verdict

#### `no` — Claim not supported

1. Write the original hypothesis as `claim_role: "original_hypothesis"`,
   `status: "unsupported"`, and `paper_use: "do_not_claim"` or
   `paper_use: "limitations_only"`.
2. If the run supports a bounded negative-result contribution, write a separate
   `claim_role: "negative_result_claim"` row with `status: "supported"` or
   `status: "partial"` and a narrow `scope`.
3. If only a reframed exploratory observation remains, mark it
   `claim_role: "exploratory"` and do not present it as pre-planned.
4. Add explicit `forbidden_overclaims` so downstream writing cannot imply the original
   claim was supported.
5. Record postmortem in findings.md (Research Findings section):
   - What was tested, what failed, hypotheses for why
   - Constraints for future attempts (what NOT to try again)
6. Write `orbit-research/NEGATIVE_RESULT_STRATEGY.md`.
7. Update CLAUDE.md Pipeline Status.
8. Stop for STOP C decision; do not treat unsupported hypotheses as a runtime abort unless
   evidence is invalid/corrupt.

#### `partial` — Claim partially supported

1. Write a ledger entry with `status: "partial"` and narrow `scope`.
2. Record the gap in findings.md.
3. Add `limitations`, `forbidden_overclaims`, and `allowed_paper_sections`.
4. Design supplementary experiments only if STOP C human decision requests them.
5. Re-run result-to-claim after supplementary experiments complete.
6. **Multiple rounds of `partial` on the same claim** → record analysis in findings.md,
   consider whether to narrow the claim scope or switch ideas.

#### `yes` — Claim supported

1. Write a ledger entry with `status: "supported"` and exact evidence refs.
2. Record confirmed claim in project notes.
3. If ablation studies are incomplete → trigger `/ablation-planner`.
4. If all evidence is in → ready for STOP C red-team and human decision; paper writing
   still requires `claims/claim_ledger.json`, `RED_TEAM_REVIEW.md` ending
   `READY_FOR_PAPER`, and `HUMAN_DECISION_NOTE.md` ending `PROCEED`.

### Step 5: Update Research Wiki (if active)

**Skip this step entirely if `research-wiki/` does not exist.**

If `research-wiki/` exists, resolve `$WIKI_SCRIPT` per the canonical
chain documented in
[`../shared-references/wiki-helper-resolution.md`](../shared-references/wiki-helper-resolution.md)
(Variant B — warn-and-skip for caller skills). The verdict / claim
status / idea-outcome page edits below run on raw markdown and don't
need the helper, but edges, query-pack rebuild, and the log line do.

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
  echo "WARN: research_wiki.py not found; verdict will be reported but wiki edges/query-pack/log will be skipped. Fix: bash tools/install_aris.sh, export ORBIT_REPO/ARIS_REPO, or cp <ARIS-repo>/tools/research_wiki.py tools/." >&2
  WIKI_SCRIPT=""
}
```

```
if research-wiki/ exists:
    # 1. Create experiment page
    Create research-wiki/experiments/<exp_id>.md with:
      - node_id: exp:<id>
      - idea_id: idea:<active_idea>
      - date, hardware, duration, metrics
      - verdict, confidence, reasoning summary

    # 2. Update claim status (page edits run unconditionally; edges only if $WIKI_SCRIPT resolved)
    for each claim resolved by this verdict:
        if verdict == "yes":
            Update claim page: status → supported
            [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" add_edge research-wiki/ --from "exp:<id>" --to "claim:<cid>" --type supports --evidence "<metric>"
        elif verdict == "partial":
            Update claim page: status → partial
            [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" add_edge research-wiki/ --from "exp:<id>" --to "claim:<cid>" --type supports --evidence "partial"
        else:
            Update claim page: status → invalidated
            [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" add_edge research-wiki/ --from "exp:<id>" --to "claim:<cid>" --type invalidates --evidence "<why>"

    # 3. Update idea outcome (raw markdown, helper-free)
    Update research-wiki/ideas/<idea_id>.md:
      - outcome: positive | mixed | negative
      - If negative: fill "Failure / Risk Notes" and "Lessons Learned"
      - If positive: fill "Actual Outcome" and "Reusable Components"

    # 4. Rebuild + log (only if $WIKI_SCRIPT resolved)
    [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" rebuild_query_pack research-wiki/
    [ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" log research-wiki/ "result-to-claim: exp:<id> verdict=<verdict> for idea:<idea_id>"

    # 5. Re-ideation suggestion
    Count failed/partial ideas since last /idea-creator run.
    If >= 3: print "💡 3+ ideas tested since last ideation. Consider re-running /idea-creator — the wiki now knows what doesn't work."
```

## Rules

- **Codex is the judge, not CC.** CC collects evidence and routes; Codex evaluates. This prevents post-hoc rationalization.
- Do not inflate claims beyond what the data supports. If Codex says "partial", do not round up to "yes".
- A single positive result on one dataset does not support a general claim. Be honest about scope.
- If `confidence` is low, treat the judgment as inconclusive and add experiments rather than committing to a claim.
- If Codex MCP is unavailable or a Codex call fails, use
  `tools/codex_review_handoff.py` and `/import-codex-review`; update
  `orbit-research/ORBIT_STATE.json` with `pause_reason: "codex_review_needed"` and the
  import command. A draft `claims/claim_ledger.json` is allowed only when it is
  explicitly non-gating: `status: "draft"`, `codex_review: "pending"`,
  `gating: false`.
- Do not let a non-gating or degraded draft ledger satisfy paper gates. Downstream
  `/paper-from-claims` and `/submission-package` still require Codex-reviewed claims,
  STOP C red-team `READY_FOR_PAPER`, and human `PROCEED`.
- Always record the verdict and reasoning in findings.md, regardless of outcome.
- Downstream paper writing must read `claims/claim_ledger.json` when it exists; Markdown
  claim files are views or compatibility artifacts.

## Review Tracing

After each `mcp__codex__codex` or `mcp__codex__codex-reply` reviewer call, save the trace following `../shared-references/review-tracing.md`. Resolve `save_trace.sh` via that shared resolver, or write files directly to `.aris/traces/<skill>/<date>_run<NN>/`. Respect the `--- trace:` parameter (default: `full`).
