# Skill Profiles

ORBIT now has a small public skill surface layered over the full skill repository.
No skill is deleted. Profiles only define what should be visible first during
installation, documentation, and agent routing.

## Catalog

The source of truth is `skills/skill_catalog.yaml`.

Each catalog entry records:

- `name`
- `category`
- `public_entry`
- `profiles`
- `canonical_source`
- optional `legacy`

`public_entry: true` means the skill is intended as a user-facing command. Internal
skills can still be called directly by advanced users or by other skills.

`import-codex-review` is a public recovery utility included in `orbit-core` and
`research-paper`. It is shown primarily when a Codex MCP/auth/sandbox failure has exported
a standalone review prompt.

## Profiles

### orbit-core

Public:

- `orbit-status`
- `idea-to-proposal`
- `experiment-bridge`
- `diagnostic-to-review`
- `proposal-revise`
- `import-codex-review`

Internal:

- `research-lit`
- `idea-discovery`
- `research-refine`
- `experiment-plan`
- `run-experiment`
- `analyze-results`
- `result-to-claim`
- `auto-review-loop`

`orbit-core` covers STOP A through STOP C and Codex standalone recovery. It does not
include paper drafting or submission packaging; use `research-paper` or the default full
install for complete idea-to-paper workflows.

### paper-pack

Public:

- `paper-draft`
- `paper-from-claims`
- `submission-package`

Internal:

- `paper-plan`
- `paper-figure`
- `paper-write`
- `paper-compile`
- `auto-paper-improvement-loop`
- `paper-claim-audit`
- `citation-audit`

### research-paper

Public:

- `orbit-status`
- `idea-to-proposal`
- `experiment-bridge`
- `diagnostic-to-review`
- `paper-draft`
- `paper-from-claims`
- `submission-package`
- `import-codex-review`

Internal:

- `proposal-revise`
- `research-lit`
- `idea-discovery`
- `research-refine`
- `experiment-plan`
- `run-experiment`
- `analyze-results`
- `result-to-claim`
- `auto-review-loop`
- `paper-plan`
- `paper-figure`
- `paper-write`
- `paper-compile`
- `auto-paper-improvement-loop`
- `paper-claim-audit`
- `citation-audit`

### patent-pack

Public:

- `patent-pipeline`

Internal:

- `prior-art-search`
- `claims-drafting`
- `specification-writing`

### presentation-pack

Public:

- `paper-slides`
- `paper-poster`
- `grant-proposal`

### infra-pack

Public:

- `run-experiment`
- `vast-gpu`
- `serverless-modal`
- `experiment-queue`

## Install Behavior

Default install remains unchanged and installs all top-level skills:

```bash
bash tools/install_aris.sh
```

To install or reconcile only one profile:

```bash
bash tools/install_aris.sh --profile orbit-core
```

For a lean idea-to-paper workflow:

```bash
bash tools/install_aris.sh --profile research-paper
```

Profile installs still include shared support references. `--profile` is not additive:
re-running the installer with a profile reconciles managed symlinks to exactly that
profile's set. Running without a profile returns to the full default install.

## Legacy Wrappers

Legacy wrappers remain callable for compatibility but are not preferred public entries:

- `paper-writing` routes to `paper-draft`, `paper-from-claims`, or `submission-package`.
- `research-refine-pipeline` remains for older one-shot refine-and-plan usage.
- `research-pipeline` remains as the older full routing harness surface.

New docs should point users to profile public entries first and describe internal
subskills only as implementation details or advanced overrides.
