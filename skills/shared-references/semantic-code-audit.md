# Semantic Plan-Code Audit — v1.3

This reference defines the ORBIT code review gate. It is stricter than ordinary code review.
The reviewer checks whether the implementation reflects the v1.3 scientific contract — not
just the proposal, but the full set of v1.3 artifacts (assumptions, abstract task,
mechanism, formalization, controls, null-result contract, component bundle).

In v1.3 this audit is also explicitly a **loop** (Stage 15: audit → fix → re-audit) until
the verdict is `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH` with documented justification.
See `research-agent-pipeline.md` Stage 15 and `research-harness-prompts.md` §15 for the
loop contract.

## Reviewer Defaults

- Reviewer: Codex
- Model: `gpt-5.5`
- Reasoning: `xhigh`
- Sandbox: disabled / `danger-full-access`
- Role: independent semantic implementation auditor (adversarial mode — see
  `innovation-loops.md` §7 for when Codex is collaborative instead)

If the available MCP or CLI cannot verify this exact configuration, write the actual
backend in the audit artifact and mark the review `PARTIAL` if the mismatch affects trust.

## Independence Rule

The executor must pass file paths and review objectives, not a curated summary. The
reviewer must read primary artifacts directly.

Good prompt shape:

```text
You are an independent semantic implementation auditor.

Read these files directly:
- orbit-research/ASSUMPTION_LEDGER.md
- orbit-research/ABSTRACT_TASK_MECHANISM.md
- orbit-research/ALGORITHM_TOURNAMENT.md           (which sketch is being implemented?)
- orbit-research/COMPONENT_BUNDLE_LADDER.md        (or COMPONENT_LADDER.md if v1.0)
- orbit-research/ALGORITHMIC_FORMALIZATION.md
- orbit-research/CONTROL_DESIGN.md
- orbit-research/NULL_RESULT_CONTRACT.md
- orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md     (or TINY_RUN_PLAN.md if v1.0)
- refine-logs/FINAL_PROPOSAL.md
- refine-logs/EXPERIMENT_PLAN.md
- src/train.py
- src/eval.py
- configs/main.yaml
- scripts/launch.sh
- src/data/loaders.py
- src/eval/parsers.py

Do not rely on executor summaries.
Compare plan to implementation and report semantic mismatches.
```

Bad prompt shape:

```text
I implemented the verifier and the ablation is probably fine. Please check quickly.
```

## Required Inputs

### v1.3 plan / contract artifacts (canonical)

- `ASSUMPTION_LEDGER.md`
- `ABSTRACT_TASK_MECHANISM.md`
- `MECHANISM_IDEATION.md` (when relevant — which candidate is being implemented?)
- `ANALOGY_TRANSFER.md` (when relevant)
- `ALGORITHM_TOURNAMENT.md` (which sketch — the tentative preferred sketch from Stage 10 or an alternate that Stage 11 picked instead — is being implemented?)
- `COMPONENT_BUNDLE_LADDER.md`  *(v1.0 alias accepted: `COMPONENT_LADDER.md`)*
- `ALGORITHMIC_FORMALIZATION.md`
- `CONTROL_DESIGN.md`
- `NULL_RESULT_CONTRACT.md`
- `DIAGNOSTIC_EXPERIMENT_PLAN.md`  *(v1.0 alias accepted: `TINY_RUN_PLAN.md`)*

### Legacy plan / proposal artifacts (still load-bearing)

- `FINAL_PROPOSAL.md`
- `EXPERIMENT_PLAN.md`

### Implementation artifacts (code surface the audit reads)

- training scripts
- evaluation scripts
- data loaders
- configs (yaml/json/toml)
- launch scripts
- result parsers
- experiment tracker
- diagnostic-run logs and outputs (formerly tiny-run logs)

The reviewer must read **every applicable artifact above that exists**. A v1.3 audit that
ignores `ASSUMPTION_LEDGER` or `ALGORITHMIC_FORMALIZATION` is incomplete and must mark its
verdict `ERROR` with the reason code "incomplete_input_set."

## Plan-Code Audit Prompt (v1.3)

```text
You are not reviewing this code for syntax or style.

You are reviewing whether the implementation faithfully matches the v1.3 research contract.

Compare the code against (every artifact that exists below — the ORBIT v1.3 contract set):
1. ASSUMPTION_LEDGER.md          — what working assumptions does the code rely on; are they
                                   surfaced or silently broken?
2. ABSTRACT_TASK_MECHANISM.md    — does the implementation realise the abstract task and
                                   target the named mechanism family?
3. MECHANISM_IDEATION.md         — which candidate (M<id>) is being implemented; does the
                                   code match its declared necessary preconditions?
4. ALGORITHM_TOURNAMENT.md       — which sketch (S<id>) was committed at Stage 11 (not
                                   necessarily Stage 10's tentative preferred sketch); does
                                   the code match its update rule, loss, decision rule?
5. COMPONENT_BUNDLE_LADDER.md    — which rung is being run; are components/bundles run in
   (or COMPONENT_LADDER.md)        the planned order; is any component silently skipped?
6. ALGORITHMIC_FORMALIZATION.md  — does the pseudocode match what the code actually does?
                                   Loss / reward / objective formula? Update rule?
                                   Decision rule? Evaluation predicate?
7. CONTROL_DESIGN.md             — are required controls implemented?
8. NULL_RESULT_CONTRACT.md       — would the implementation's outputs be interpretable
                                   per the contract's distinguishing causes?
9. DIAGNOSTIC_EXPERIMENT_PLAN.md — is the run cheap enough; does it operate in a regime
   (or TINY_RUN_PLAN.md)           where the mechanism could in principle manifest?
10. FINAL_PROPOSAL.md            — does the high-level proposal match the implementation?
11. EXPERIMENT_PLAN.md           — does the experiment plan match the launch script?

Check whether the scripts actually implement the intended experiments.

Focus on:
- Are the correct baselines implemented (per BASELINE_CEILING / EXPERIMENT_PLAN)?
- Are the required controls implemented (per CONTROL_DESIGN)?
- Are ablations implemented as specified (per COMPONENT_BUNDLE_LADDER)?
- Are the same datasets, splits, metrics, and regimes used (per FINAL_PROPOSAL +
  ABSTRACT_TASK_MECHANISM)?
- Does the code test the claimed mechanism (per MECHANISM_IDEATION + ALGORITHMIC_FORMALIZATION)?
- Are any components missing, silently changed, or merged together (vs.
  COMPONENT_BUNDLE_LADDER)?
- Are there shortcuts that make the experiment non-diagnostic?
- Are config defaults inconsistent with the experiment plan?
- Are outputs sufficient to interpret positive, negative, and tied results
  (per NULL_RESULT_CONTRACT)?
- Does the code respect each entry in ASSUMPTION_LEDGER (or at least surface where it
  diverges)?
- Is the test set isolated from tuning/selection (G13)?

Do not only report compile errors. Report semantic mismatches between plan and
implementation.

Return:
1. Verdict on its own line, exactly one of:
   MATCHES_PLAN | PARTIAL_MISMATCH | CRITICAL_MISMATCH | ERROR
   (use ERROR only if the audit could not be completed — Codex MCP unavailable, missing
   required input — and include a reason code such as "incomplete_input_set" or
   "codex_mcp_unavailable")
2. Missing experiments
3. Missing controls
4. Missing ablations / bundle rungs
5. Missing or unsupported assumptions (cross-reference ASSUMPTION_LEDGER row IDs)
6. Algorithm fidelity issues (cross-reference ALGORITHMIC_FORMALIZATION sections)
7. Incorrect defaults
8. Plan-code mismatches
9. Required fixes before GPU
```

## Traceability Matrix

Every audit should include:

```text
Plan Artifact | Plan Item | Expected Implementation | Actual Code | Status | Fix
```

Example rows (v1.3):

```text
ASSUMPTION_LEDGER       | A3 (working: scale-dependent emergent) | scale ≥ 7B in launch.sh | currently 1.3B | CRITICAL | run at ≥ 7B or surface assumption violation
ABSTRACT_TASK_MECHANISM | bottleneck = retrieval failure          | retrieval module in src/retrieve.py | not implemented | CRITICAL | add retrieval module
ALGORITHM_TOURNAMENT    | Stage 11 picked S2 (tentative was S1; HMBC switched to S2's distillation analogy) | distillation loss in train.py | placeholder cross-entropy | CRITICAL | implement S2 distillation loss per ALGORITHMIC_FORMALIZATION §3
COMPONENT_BUNDLE_LADDER | rung 2 = base + verifier                | run_rung2.sh | only base implemented | PARTIAL | add verifier; reorder ladder runs
ALGORITHMIC_FORMALIZATION | loss = L_ce + α * L_kl, α=0.7         | configs/main.yaml α=0.5 | mismatched | MISMATCH | set α=0.7 or document why divergence
CONTROL_DESIGN          | vanilla-GRPO control                    | train_grpo.py without verifier | missing | CRITICAL | implement no-verifier control
BASELINE_CEILING        | BoN baseline N=8/16/32                  | bon_eval.py with N=8 only | partial | PARTIAL | add N sweep
NULL_RESULT_CONTRACT    | distinguish mechanism vs metric mismatch | logs include per-domain accuracy | aggregate only | MISMATCH | add per-domain logging
DIAGNOSTIC_EXPERIMENT_PLAN | hard-subset eval                     | using full test only | MISMATCH | add subset filter
```

## Diagnostic Run Audit Prompt (v1.3)

> Renamed from "Tiny Run Audit" in v1.0. The verdict contract is preserved verbatim.

```text
Audit the diagnostic-run outputs against the experiment plan.

Check:
1. Did the expected script run?
2. Did it use the intended dataset, split, metric, and config?
3. Did it run the intended baseline / component / bundle?
4. Are outputs saved in the expected format?
5. Are metric values plausible?
6. Are logs sufficient to diagnose null results per NULL_RESULT_CONTRACT?
7. Does the diagnostic run reveal implementation mismatch?
8. **G12 regime check (mandatory):** if the run failed, did the failure regime preserve
   the mechanism's necessary preconditions (per ABSTRACT_TASK_MECHANISM and the chosen
   candidate from MECHANISM_IDEATION / ALGORITHM_TOURNAMENT)? If the regime ablated a
   precondition the mechanism needs (e.g. scale-dependent emergent behaviour ablated by
   running at too small a scale), do NOT recommend REDESIGN_EXPERIMENT — recommend
   redesigning the diagnostic to a regime where the mechanism could in principle manifest.
   Document the regime check explicitly in the audit body. If you cannot determine
   whether the regime was preserved, return ERROR with reason "regime_check_unanswerable"
   and escalate to HUMAN_DECISION_REQUIRED.
9. Should we proceed, fix code, or redesign?

Return on its own line, exactly one of:
PASS | FIX_BEFORE_GPU | REDESIGN_EXPERIMENT
```

The audit artifact is named `DIAGNOSTIC_RUN_AUDIT.md` in v1.3. Consumers (experiment-queue,
research-pipeline) accept the v1.0 alias `TINY_RUN_AUDIT.md` for one major version.

## Blocking Rules (v1.3)

- `CRITICAL_MISMATCH` blocks GPU scale-up unconditionally (G11). The Stage 15 loop must
  iterate fix → re-audit until `MATCHES_PLAN` or scoped `PARTIAL_MISMATCH` is reached.
- `PARTIAL_MISMATCH` may allow a diagnostic run only if the missing pieces are irrelevant
  to that diagnostic. Scale-up requires explicit justification of why the missing pieces
  are irrelevant to the scale-up wave.
- `FIX_BEFORE_GPU` (Diagnostic Run Audit) blocks full run; loop fix → re-audit.
- `REDESIGN_EXPERIMENT` (Diagnostic Run Audit) sends the project back to Stage 16
  (Cheapest Valid Diagnostic) — but only if G12's regime check passed; otherwise the
  audit should have recommended diagnostic redesign without rejecting the mechanism.
- `ERROR` (audit could not complete — Codex unavailable, incomplete input set, regime
  check unanswerable) is **advisory at the diagnostic / sanity run stage** (proceed,
  surface the reason) and **blocks at scale-up pending explicit human acknowledgement**
  (scale-up is the expensive irreversible step; never launch without a person on the loop).
- Missing required v1.3 artifact at audit time → audit returns `ERROR` with reason
  `incomplete_input_set`; the orchestrator escalates per G3 / G6 / G10 as applicable.
- A run that compiles but does not implement the intended algorithm is a failed audit
  (verdict `CRITICAL_MISMATCH`).

## Footer — Alias / Compat Note

Producers in the v1.3 pipeline emit v1.3 artifact names only (`COMPONENT_BUNDLE_LADDER.md`,
`DIAGNOSTIC_EXPERIMENT_PLAN.md`, `DIAGNOSTIC_RUN_REPORT.md`, `DIAGNOSTIC_RUN_AUDIT.md`).
Consumers (this audit, experiment-queue, research-pipeline) parse either the v1.3 name or
the v1.0 alias for one major version (preferring v1.3 if both exist):

| v1.0 alias | v1.3 canonical |
|---|---|
| `COMPONENT_LADDER.md` | `COMPONENT_BUNDLE_LADDER.md` |
| `TINY_RUN_PLAN.md` | `DIAGNOSTIC_EXPERIMENT_PLAN.md` |
| `TINY_RUN_REPORT.md` | `DIAGNOSTIC_RUN_REPORT.md` |
| `TINY_RUN_AUDIT.md` | `DIAGNOSTIC_RUN_AUDIT.md` |

`TASK_ONTOLOGY.md` has no alias — see `research-agent-pipeline.md` migration appendix for
the manual split into MODE_ROUTING / SEED_FRAMING / ASSUMPTION_LEDGER / ABSTRACT_TASK_MECHANISM.
