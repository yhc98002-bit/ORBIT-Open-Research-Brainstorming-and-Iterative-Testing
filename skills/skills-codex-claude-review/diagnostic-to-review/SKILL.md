---
name: "diagnostic-to-review"
description: "ORBIT v1.5 STOP C diagnostic session orchestrator. Runs one formal diagnostic session from a diagnostic command, manifest, grid spec, or experiment/experiment_pack.json; analyzes exact run outputs; writes/consumes claims/claim_ledger.json for paper-bearing results; conditionally red-teams; then stops at STOP C human decision. Uses per-diagnostic artifacts under orbit-research/diagnostics/<diagnostic_id>/ and writes legacy latest copies only for compatibility. Does not consume experiment-bridge probe artifacts as formal diagnostics, does not invoke paper-writing, does not fabricate HUMAN_DECISION_NOTE, and keeps Codex review required."
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, WebSearch, WebFetch, Agent, Skill
---

> Override for Codex users who want **Claude Code CLI**, not a second Codex agent, to act as the reviewer/helper. Install this package **after** `skills/skills-codex/*`.

Whenever the upstream skill asks for an external reviewer/helper, write the complete focused prompt to `$PROMPT_FILE`. For a one-shot independent review, run:

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"
```

For multi-round reviewer discussion, keep automation non-interactive but preserve continuity with `--session-id` on the first call and `--resume` on follow-up calls; see `../shared-references/claude-cli-review.md`.

# /diagnostic-to-review -- STOP C Formal Diagnostic Session

Run a recoverable STOP C diagnostic session for: **$ARGUMENTS**

## Overview

This skill owns STOP C. It runs formal diagnostics, analyzes results, conditionally
constructs claims, conditionally runs red-team review, and then stops for human STOP C
decision. It does not invoke `/paper-writing`, does not decide scale-up, and does not
write `HUMAN_DECISION_NOTE.md` except when the user explicitly supplies that decision.

The design is session-based. Every invocation gets a `diagnostic_id` and `input_hash`.
Canonical outputs live under:

```text
orbit-research/diagnostics/<diagnostic_id>/
```

Legacy fixed-path artifacts may still be written as **latest compatibility copies**, but
they must never be used for idempotent skip unless they match the current
`diagnostic_id`, `input_hash`, and run/result references.

## Ownership Boundary

This skill owns:

- formal diagnostic execution via `/run-experiment`;
- per-diagnostic `RUN_REPORT.md` and `RUN_AUDIT.md`;
- `RESULT_INTERPRETATION.md`;
- `RESEARCH_DECISION_LOG.md`;
- `claims/claim_ledger.json` as the canonical paper-bearing claim/evidence ledger;
- `claims/CLAIM_LEDGER.md` as the generated ledger view;
- `CLAIM_CONSTRUCTION.md` only as a per-diagnostic or legacy compatibility view for
  paper-bearing diagnostics;
- `NEGATIVE_RESULT_STRATEGY.md` when the result is unsupported, tied, or reframed;
- `RED_TEAM_REVIEW.md` only for paper-bearing diagnostics;
- `STOP_C_REVIEW.md`;
- `HUMAN_DECISION_NOTE.template.md`.

This skill does not own:

- STOP B implementation/headroom probes from `/experiment-bridge`;
- paper-writing;
- scale-up approval;
- human approval fabrication.

## Formal Diagnostic vs STOP B Probe

`/experiment-bridge` may produce implementation/headroom probes:

- `experiment/PROBE_REPORT.md`
- `experiment/PROBE_AUDIT.md`
- `experiment/HEADROOM_NOTE.md`
- `experiment_pack.probes[]`

Those are not formal diagnostic artifacts. This skill must not treat them as
`RUN_REPORT.md`, `RUN_AUDIT.md`, claim evidence, or red-team input. If `$ARGUMENTS`
points only to probe artifacts, write a blocked Phase 0 context explaining that a formal
diagnostic command/manifest is required.

Formal diagnostics use:

- `orbit-research/diagnostics/<diagnostic_id>/RUN_REPORT.md`
- `orbit-research/diagnostics/<diagnostic_id>/RUN_AUDIT.md`
- `orbit-research/diagnostics/<diagnostic_id>/RESULT_INTERPRETATION.md`
- `orbit-research/RUN_LEDGER.jsonl`

Compatibility latest copies may also be written to:

- `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`
- `orbit-research/RESULT_INTERPRETATION.md`
- `orbit-research/RESEARCH_DECISION_LOG.md`
- `orbit-research/CLAIM_CONSTRUCTION.md`
- `orbit-research/NEGATIVE_RESULT_STRATEGY.md`
- `orbit-research/RED_TEAM_REVIEW.md`

Paper-bearing STOP C also uses:

- `claims/claim_ledger.json` -- canonical claim/evidence/source-of-truth ledger
- `claims/CLAIM_LEDGER.md` -- generated human-readable ledger view

## Load First

- `../shared-references/research-agent-pipeline.md` -- Stages 17/18/21/23 and hard gates.
- `../shared-references/research-harness-prompts.md` -- sections `17`, `18`, `21`, `22`, `23`.
- `../shared-references/semantic-code-audit.md` -- Stage 17 audit and G12 regime check.
- `../shared-references/experiment-integrity.md` -- metric/data fraud signals.
- `../shared-references/claude-cli-review.md` -- Claude CLI reviewer required loud-stop contract.
- `../shared-references/continuation-contract.md` -- resume states.
- `../shared-references/document-hygiene.md`.

Also inspect when present:

- `experiment/experiment_pack.json`
- `orbit-research/PLAN_CODE_AUDIT.md`
- `orbit-research/RUN_LEDGER.jsonl`
- `experiment/EXPERIMENT_PLAN_EXEC.md` or legacy `refine-logs/EXPERIMENT_PLAN_EXEC.md`
- `orbit-research/NULL_RESULT_CONTRACT.md`
- `orbit-research/COMPONENT_BUNDLE_LADDER.md`
- `orbit-research/ASSUMPTION_LEDGER.md`

## Session Identity

Phase 0 creates a deterministic context for this run:

- `input_hash`: SHA-256 over normalized formal diagnostic input. The executable helper
  computes it so repeated invocations do not drift by prompt interpretation.
- `diagnostic_id`: `diag_<UTC YYYYMMDD_HHMMSS>_<input_hash prefix>` for a fresh run.
  Normal invocation may reuse an existing `diagnostic_id` only when the newest matching
  `DIAGNOSTIC_CONTEXT.json` is active/incomplete and its `input_hash` matches the current
  input. Terminal sessions such as `reviewed`, `stop_c_ready`, `completed`, or `archived`
  are not silently reused.
- `diagnostic_kind`: one of
  `implementation_smoke | headroom_probe | local_mechanism_probe | paper_bearing_main |
  paper_bearing_ablation | scaleup_candidate | unknown`.
- `claim_relevance`: one of
  `none | local | paper_scope_affecting | primary_evidence | unknown`.

Use the helper instead of hand-rolling these fields:

```bash
python3 tools/diagnostic_session.py create --repo . --input "$ARGUMENTS"
```

If the user explicitly resumes a known diagnostic command, use:

```bash
python3 tools/diagnostic_session.py resume --repo . --input "$ARGUMENTS"
```

If the user wants a fresh rerun of the same command after a terminal STOP C session, use:

```bash
python3 tools/diagnostic_session.py create --repo . --input "$ARGUMENTS" --fresh
```

## Phase 0: Context, Preflight, Codex Precondition

Phase 0 happens before Phase 1. It must not write `status = in_progress` for blocked
preflight failures.

Steps:

1. Parse `$ARGUMENTS` as a diagnostic command, manifest path, grid spec, or
   `experiment/experiment_pack.json`.
2. Create or reuse only an active/incomplete matching session context with:

   ```bash
   python3 tools/diagnostic_session.py create --repo . --input "$ARGUMENTS"
   ```

   If this returns `terminal_session_exists`, stop and ask for an explicit choice:
   `-- resume:true` to inspect/recover that session, or `-- fresh:true` to rerun the
   same diagnostic command with a new `diagnostic_id`.

   If the user explicitly resumes, first run:

   ```bash
   python3 tools/diagnostic_session.py resume --repo . --input "$ARGUMENTS"
   ```

   `validate-resume` remains a compatibility alias for the same input-hash check.
   Treat a nonzero result as a resume blocker; do not fall back to old fixed paths.

   If the user explicitly requests a fresh rerun, run:

   ```bash
   python3 tools/diagnostic_session.py create --repo . --input "$ARGUMENTS" --fresh
   ```
3. Read `diagnostic_id`, `input_hash`, `diagnostic_kind`, and `claim_relevance` from
   `orbit-research/diagnostics/<diagnostic_id>/DIAGNOSTIC_CONTEXT.json`.
4. Create:

   ```text
   orbit-research/diagnostics/<diagnostic_id>/
   .aris/review-prompts/
   ```

5. Verify prerequisites:
   - G11: `orbit-research/PLAN_CODE_AUDIT.md` verdict is `MATCHES_PLAN` or scoped
     `PARTIAL_MISMATCH` irrelevant to this diagnostic.
   - G8: null-result interpretation exists in `experiment_pack.null_result_contract` or
     `orbit-research/NULL_RESULT_CONTRACT.md`.
   - G9: component ladder/control structure exists in `experiment_pack.component_ladder`
     or `orbit-research/COMPONENT_BUNDLE_LADDER.md`, unless this is an explicitly declared
     single-component baseline reproduction.
   - The input resolves to a formal diagnostic command/manifest/grid, not only STOP B
     probe artifacts.
6. Check Claude CLI precondition using `claude-cli-review.md` section 3.
7. Update `DIAGNOSTIC_CONTEXT.json` only through `tools/diagnostic_session.py` when
   recording run or audit state.

`DIAGNOSTIC_CONTEXT.json` must include:

```jsonc
{
  "schema_version": "0.1",
  "diagnostic_id": "<diagnostic_id>",
  "input": "$ARGUMENTS",
  "input_hash": "<sha256>",
  "diagnostic_kind": "paper_bearing_main",
  "claim_relevance": "primary_evidence",
  "status": "initialized",
  "run_id": null,
  "result_paths": [],
  "audit": {
    "verdict": null,
    "regime_preserved": "unknown",
    "mechanism_rejected": false
  },
  "artifact_inventory": []
}
```

### Phase 0 Blocked State

If any prereq or Claude CLI precondition fails, write
`orbit-research/DIAGNOSTIC_TO_REVIEW_STATE.json` and
`orbit-research/ORBIT_STATE.json` with `awaiting_user_action`, not `in_progress`:

```jsonc
{
  "status": "awaiting_user_action",
  "pause_reason": "missing_prereq",
  "blockers": [
    {
      "id": "G11",
      "kind": "missing_artifact|bad_verdict|codex_unavailable|legacy_conflict",
      "artifact": "orbit-research/PLAN_CODE_AUDIT.md",
      "message": "short blocker",
      "safe_next_command": "/experiment-bridge \"experiment/experiment_pack.json\" -- mode: audit-only"
    }
  ],
  "safe_next_command": "<exact recovery command>"
}
```

For Claude CLI reviewer unavailability or mid-run Codex failure, also export a standalone review
prompt before stopping:

```text
.aris/review-prompts/<diagnostic_id>.<phase>.md
```

The prompt must include the diagnostic context, required Codex role, expected verdict
format, source artifacts to review, and instructions for the user to paste it into Codex
manually. This prompt is recovery metadata; it is not a substitute audit/review verdict.

## State Persistence

State file:

```text
orbit-research/DIAGNOSTIC_TO_REVIEW_STATE.json
```

Required fields:

```jsonc
{
  "skill": "diagnostic-to-review",
  "diagnostic_id": "<diagnostic_id>",
  "input_hash": "<sha256>",
  "phase": "phase-0-context|phase-1-run|phase-2-analyze|phase-3-claim|phase-4-review|phase-5-stop-c-review",
  "status": "in_progress|awaiting_human_continue|awaiting_user_action|completed",
  "pause_reason": null,
  "next_action": "<same-skill resume or human action>",
  "next_skill_hint": "<narrow recovery skill or null>",
  "safe_next_command": "<exact command or human instruction>",
  "timestamp": "<ISO 8601 UTC>",
  "artifact_inventory": [],
  "run_id": null,
  "result_paths": [],
  "claude_session_id": null,
  "notes": ""
}
```

## Resume And Idempotent Skip

Do not skip a phase merely because a fixed legacy path exists.

Before approving a resume, run:

```bash
python3 tools/diagnostic_session.py resume --repo . --input "$ARGUMENTS"
```

`validate-resume` is accepted as a compatibility alias. Resume is approved only when the
input hash matches an existing diagnostic context; it must never be inferred from fixed
latest paths. Fresh reruns of the same command require `create --fresh`.

A phase may be skipped only if all of these are true:

1. `DIAGNOSTIC_CONTEXT.json.diagnostic_id` and
   `DIAGNOSTIC_TO_REVIEW_STATE.json.diagnostic_id` match the current `diagnostic_id`.
2. `DIAGNOSTIC_CONTEXT.json.input_hash` and
   `DIAGNOSTIC_TO_REVIEW_STATE.json.input_hash` match the current `input_hash`.
3. The required per-diagnostic artifact exists under
   `orbit-research/diagnostics/<diagnostic_id>/`.
4. The artifact references the same `run_id` or exact result path recorded in
   `DIAGNOSTIC_CONTEXT.json`.

If any condition fails, replay the phase and overwrite only the current
per-diagnostic artifacts plus compatibility latest copies.

Phase artifact map:

| Phase | Required per-diagnostic artifacts |
| --- | --- |
| phase-0-context | `DIAGNOSTIC_CONTEXT.json` |
| phase-1-run | `RUN_REPORT.md`, `RUN_AUDIT.md`, `DIAGNOSTIC_CONTEXT.json` updated with `run_id` and result candidates |
| phase-2-analyze | `RESULT_INTERPRETATION.md`, `RESEARCH_DECISION_LOG.md` when failed/mixed/surprising/no-result |
| phase-3-claim | `claims/claim_ledger.json` plus `claims/CLAIM_LEDGER.md` for paper-bearing diagnostics; per-diagnostic/legacy `CLAIM_CONSTRUCTION.md` remains a compatibility view; `NEGATIVE_RESULT_STRATEGY.md` when unsupported/tie/reframed |
| phase-4-review | `RED_TEAM_REVIEW.md` for paper-bearing diagnostics |
| phase-5-stop-c-review | `STOP_C_REVIEW.md`, `HUMAN_DECISION_NOTE.template.md` |

## Workflow

### Phase 1: Formal Run

Read `diagnostic_id` and `output_root` from
`orbit-research/diagnostics/<diagnostic_id>/DIAGNOSTIC_CONTEXT.json`. Call
`/run-experiment` with that diagnostic_id and output_root so the run writes into the
session directory, not only legacy fixed paths.

Preferred call:

```text
/run-experiment "<formal command or manifest from DIAGNOSTIC_CONTEXT.json>" — diagnostic-id: "<diagnostic_id>" — output-root: "orbit-research/diagnostics/<diagnostic_id>/"
```

Equivalent environment form:

```bash
ORBIT_DIAGNOSTIC_ID="<diagnostic_id>" \
ORBIT_DIAGNOSTIC_OUTPUT_ROOT="orbit-research/diagnostics/<diagnostic_id>" \
/run-experiment "<formal command or manifest from DIAGNOSTIC_CONTEXT.json>"
```

`/run-experiment` writes the run ledger and formal diagnostic report/audit directly into:

```text
orbit-research/diagnostics/<diagnostic_id>/RUN_REPORT.md
orbit-research/diagnostics/<diagnostic_id>/RUN_AUDIT.md
```

Update `DIAGNOSTIC_CONTEXT.json` with:

- `run_id`
- `screen_name` if any
- exact result files/directories
- W&B run IDs or dashboard URLs
- log paths
- ledger start/final record references

Record the run in executable session state:

```bash
python3 tools/diagnostic_session.py update-run \
  --repo . \
  --diagnostic-id "<diagnostic_id>" \
  --run-id "<run_id>" \
  --result-path "<exact result path>"
```

Compatibility latest copies may be written to:

- `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`

### Phase 1 Audit And G12 Semantics

`RUN_AUDIT.md` must use this structured interpretation:

```yaml
verdict: PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT | ERROR
regime_preserved: true | false | unknown
mechanism_rejected: true | false
reason: <short reason>
```

Routing:

| Audit interpretation | Route |
| --- | --- |
| `verdict: PASS` | Continue to Phase 2. |
| `verdict: FIX_BEFORE_GPU` | Pause with `awaiting_user_action`; route to `/experiment-bridge "experiment/experiment_pack.json" -- mode: audit-only`. |
| `verdict: REDESIGN_EXPERIMENT` and `regime_preserved: true` | Pause; route to `/experiment-plan -- mode: diagnostic-branch-only` or STOP B pack patch. |
| `verdict: REDESIGN_EXPERIMENT` and `regime_preserved: false` | Pause; redesign diagnostic regime; explicitly set `mechanism_rejected: false`. |
| `verdict: ERROR` or `regime_preserved: unknown` | Pause for human or missing-input recovery; do not reject the mechanism. |

There is no route where G12 regime failure rejects the mechanism. If the diagnostic regime
did not preserve mechanism preconditions, the diagnostic is invalid for mechanism rejection.
If `regime_preserved=false`, do not reject the mechanism. Route to diagnostic redesign in
a regime where the mechanism could manifest, and keep `mechanism_rejected=false`.

Future v2.1 may split `REDESIGN_EXPERIMENT` into `REDESIGN_DIAGNOSTIC` and
`MECHANISM_NOT_SUPPORTED`. For v2.0, keep the legacy verdict token but require structured
regime fields.

After parsing `RUN_AUDIT.md`, record the structured audit fields:

```bash
python3 tools/diagnostic_session.py update-audit \
  --repo . \
  --diagnostic-id "<diagnostic_id>" \
  --verdict PASS \
  --regime-preserved true \
  --mechanism-rejected false
```

### Phase 2: Analyze Exact Results

Load and follow [result_interpretation.md](prompts/result_interpretation.md). Derive exact
result paths from the session context, run report, and ledger; never default blindly to
`results/`. Write `RESULT_INTERPRETATION.md` and the narrow `RESEARCH_DECISION_LOG.md`.

### Phase 3: Claim Relevance Gate

Load and follow [claim_relevance.md](prompts/claim_relevance.md). Local diagnostics stop
after interpretation and decision log; paper-bearing diagnostics must update
`claims/claim_ledger.json`. Validate with `python3 tools/validate_orbit_pack.py --repo . --pack claim_ledger`.

For negative or unsupported outcomes, do not treat `claim_supported=no` as a runtime abort
by default. Encode the failed original hypothesis as `claim_role: "original_hypothesis"`,
`status: "unsupported"`, and `paper_use: "do_not_claim"` or `limitations_only`; encode any
supported negative-result contribution as a separate `claim_role: "negative_result_claim"`
row. Abort only for invalid/corrupt evidence, missing provenance, or integrity failure.

### Phase 4: Red-team Review

Load and follow [red_team_review.md](prompts/red_team_review.md). Parse the final verdict
token (`READY_FOR_PAPER`, `REQUIRES_FIXES`, `REDESIGN_REQUIRED`, or
`HUMAN_DECISION_REQUIRED`) rather than treating a numeric score as sufficient.

### Phase 5: STOP C Review

Load and follow [stop_c_review.md](prompts/stop_c_review.md). Always write the STOP C
review and `HUMAN_DECISION_NOTE.template.md`; final safe next action is human STOP C
decision unless a human-authored `HUMAN_DECISION_NOTE.md` already exists and ends PROCEED.

The human template must ask for an explicit final decision.

Allowed final decision tokens:

- `PROCEED`
- `FIX_FIRST`
- `REDESIGN_DIAGNOSTIC`
- `REFRAME_CLAIM`
- `ARCHIVE`
- `SCALE_UP`

At the very end, the human must write exactly:
`Final decision: <ONE_TOKEN>`.

Example template:

```markdown
# HUMAN_DECISION_NOTE

- Diagnostic ID:
- Reviewed STOP_C_REVIEW.md: yes/no
- Rationale:

Allowed final decision tokens:
- PROCEED
- FIX_FIRST
- REDESIGN_DIAGNOSTIC
- REFRAME_CLAIM
- ARCHIVE
- SCALE_UP

Final decision: <ONE_TOKEN>
```

Compatibility latest copies:

- `orbit-research/STOP_C_REVIEW.md`
- `orbit-research/HUMAN_DECISION_NOTE.template.md`
- `orbit-research/PIPELINE_SUMMARY.md`

Final state must be a STOP C human checkpoint:

```jsonc
{
  "skill": "diagnostic-to-review",
  "diagnostic_id": "<diagnostic_id>",
  "input_hash": "<sha256>",
  "phase": "phase-5-stop-c-review",
  "status": "awaiting_human_continue",
  "pause_reason": "stop_review",
  "next_action": "review STOP_C_REVIEW.md, then write orbit-research/HUMAN_DECISION_NOTE.md",
  "next_skill_hint": null,
  "safe_next_command": "Review orbit-research/diagnostics/<diagnostic_id>/STOP_C_REVIEW.md, then write orbit-research/HUMAN_DECISION_NOTE.md",
  "timestamp": "<now>",
  "artifact_inventory": [
    "claims/claim_ledger.json",
    "claims/CLAIM_LEDGER.md",
    "orbit-research/diagnostics/<diagnostic_id>/RED_TEAM_REVIEW.md",
    "orbit-research/diagnostics/<diagnostic_id>/STOP_C_REVIEW.md"
  ]
}
```

Do not set final next action to paper writing or `/run-experiment` unless
`orbit-research/HUMAN_DECISION_NOTE.md` already exists, references this `diagnostic_id`,
and ends with final verdict `PROCEED`. Even then, report it as a permitted next step, not
as an automatic action. When a valid `claims/claim_ledger.json` exists, the permitted
paper-writing command is:

```bash
/paper-from-claims "claims/claim_ledger.json"
```

Do not use legacy `/paper-writing "orbit-research/CLAIM_CONSTRUCTION.md"` as the STOP C
state safe next command once the ledger exists.

## Claude CLI Reviewer Required And Standalone Prompt Export

Claude CLI reviewer remains required by default. This skill follows
`../shared-references/claude-cli-review.md`.

Additional STOP C recovery rule: when Claude CLI reviewer is unavailable at precondition time or
fails during Phase 1 audit / Phase 4 red-team review, write a standalone prompt:

```text
.aris/review-prompts/<diagnostic_id>.<phase>.md
.aris/review-prompts/<diagnostic_id>.<phase>.json
```

The prompt should contain:

- diagnostic context JSON;
- relevant artifacts and snippets;
- exact reviewer role (Stage 17 audit or Stage 23 red-team);
- required verdict format;
- instruction that the user can paste the prompt into Codex manually and then place the
  response at `.aris/review-outputs/<diagnostic_id>.<phase>.response.md`.

Use `direct Claude CLI prompt/raw-JSON files generate` when possible so the prompt, metadata,
expected import path, producer context, and ORBIT_STATE are consistent. Include the
diagnostic session context when generating the prompt:

```bash
python3 direct Claude CLI prompt/raw-JSON files generate \
  --repo . \
  --phase-id "<diagnostic_id>.<phase>" \
  --role "<Stage 17 audit or Stage 23 red-team Codex role>" \
  --file "orbit-research/diagnostics/<diagnostic_id>/DIAGNOSTIC_CONTEXT.json" \
  --file "<artifact requiring Claude CLI review>" \
  --objective "<phase-specific review objective>" \
  --output-format "<required verdict schema>" \
  --required-section "VERDICT" \
  --verdict-required \
  --expected-verdict-token "<PHASE_TOKEN_1>" \
  --expected-verdict-token "<PHASE_TOKEN_2>" \
  --output-artifact "orbit-research/diagnostics/<diagnostic_id>/<review-artifact>.md" \
  --current-stop "STOP_C" \
  --producer-skill "diagnostic-to-review" \
  --producer-phase "<phase>" \
  --diagnostic-id "<diagnostic_id>" \
  --resume-command "/diagnostic-to-review \"$ARGUMENTS\" -- resume:true" \
  --write-orbit-state
```

For Phase 1 diagnostic audit, use expected verdict tokens:
`PASS`, `FIX_BEFORE_GPU`, `REDESIGN_EXPERIMENT`, `ERROR`.

For Phase 4 STOP C red-team review, use expected verdict tokens:
`READY_FOR_PAPER`, `REQUIRES_FIXES`, `REDESIGN_REQUIRED`, `HUMAN_DECISION_REQUIRED`.
The imported standalone response must contain exactly one final verdict token. Candidate
lists with pipe separators and vague `# VERDICT` prose are blockers.
Importing a Codex response satisfies only the Codex transport gap; it is not
`HUMAN_DECISION_NOTE.md` approval.

Set `pause_reason: claude_review_needed` and safe next command:

```text
After fixing Claude CLI access, rerun the blocked skill with its documented resume flag.
```

This prompt does not satisfy the gate by itself. The gate is satisfied only after a valid
Codex-backed artifact exists, either from MCP or imported standalone response, or the user
explicitly passes `-- claude-required: false`, which must mark downstream artifacts as
degraded.
After successful import, `ORBIT_STATE.json` should preserve `STOP_C`,
`diagnostic-to-review`, the original phase, and the resume command with
`pause_reason: codex_review_imported`; this still does not create
`HUMAN_DECISION_NOTE.md` or authorize paper handoff.

## What This Skill Deliberately Does Not Do

- Does not consume STOP B probe artifacts as formal diagnostic evidence.
- Does not invoke `/paper-writing`, `/auto-paper-improvement-loop`, `/paper-claim-audit`,
  or `/citation-audit`.
- Does not auto-decide scale-up.
- Does not fabricate `HUMAN_DECISION_NOTE.md`.
- Does not modify `PLAN_CODE_AUDIT.md`; route code/plan mismatch back to
  `/experiment-bridge`.
- Does not modify `experiment/experiment_pack.json` except to read diagnostic commands and
  decision tree context; route diagnostic redesign back to STOP B planning tools.
- Does not default to `/idea-to-proposal -- fresh: true` for failed diagnostics.

## Final Rule

```text
One diagnostic session, one diagnostic_id, one input_hash.
Run exact evidence, analyze exact outputs, route failures narrowly, and stop at STOP C for
human decision. Negative evidence is an outcome, not an orchestration abort.
```
