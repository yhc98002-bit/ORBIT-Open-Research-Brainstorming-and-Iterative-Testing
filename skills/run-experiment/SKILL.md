---
name: run-experiment
description: Deploy and run ML experiments on local, remote, Vast.ai, or Modal serverless GPU. Auto-routes to /experiment-queue for batches of ≥10 jobs. Resumes interrupted single runs by attaching to a still-alive screen or replaying from the last log offset. Use when user says "run experiment", "deploy to server", "跑实验", or needs to launch training jobs.
argument-hint: [experiment-description-or-manifest-path]
allowed-tools: Bash(*), Read, Grep, Glob, Edit, Write, Agent, Skill(serverless-modal), Skill(experiment-queue)
---

# Run Experiment

Deploy and run ML experiment: $ARGUMENTS

## Auto-routing (Step 0 — runs before everything else)

This skill is the single entry point for "run an experiment", regardless of size. It
auto-routes between inline single-run execution and `/experiment-queue` batch orchestration
based on input shape.

**Constants:**

- `SOLO_THRESHOLD = 5` — jobs ≤ this run inline (this skill).
- `QUEUE_THRESHOLD = 10` — jobs ≥ this auto-delegate to `/experiment-queue`.
- Gray zone (6 ≤ jobs ≤ 9) → default inline parallel; user may force with `— queue: true`.
- Override: `— queue: true` forces `/experiment-queue` regardless of count;
  `— solo: true` forces inline regardless of count.

**Detection rules** (in order — first match wins):

| `$ARGUMENTS` shape | Detection | Routing |
|---|---|---|
| Path ending in `.yaml` / `.yml` / `.json` AND parses as a manifest | `yq` / `jq` count `jobs[]` array length | by count |
| Grid spec string with `×` or `N=[...]` patterns | Expand the Cartesian product, count | by count |
| Natural-language batch description (e.g., "21 seeds × 12 cells") | Claude estimates count | by count |
| Single command (contains `python ` / `bash ` / `torchrun ` / etc., no batch markers) | count = 1 | inline (SOLO) |
| Anything else | count = 1 | inline (SOLO) |

**Decision:**

```text
if user passed `— queue: true` → delegate to /experiment-queue
elif user passed `— solo: true` → run inline
elif count >= QUEUE_THRESHOLD → delegate to /experiment-queue
elif count <= SOLO_THRESHOLD → run inline (sequential or parallel up to MAX_PARALLEL_RUNS)
else (gray zone 6-9) → run inline parallel; log "moderate batch, /experiment-queue available via — queue: true"
```

**Delegation:**

```bash
/experiment-queue "$ARGUMENTS"
```

When delegating, this skill writes a routing breadcrumb to
`orbit-research/RUN_EXPERIMENT_STATE.json` (status = `completed`, `next_action = "delegated-to-experiment-queue"`,
`next_skill_hint = "/experiment-queue"`) so the orchestrator and downstream skills can
trace what happened. The actual job state is then owned by `queue_state.json`.

**The orchestrator (`/research-pipeline` Stage 17) only ever calls `/run-experiment`** —
it does not need to decide between solo and queue. This skill handles routing. Same when
a user invokes manually.

## State Persistence (Continuation Contract)

This skill follows `shared-references/continuation-contract.md`.

**STATE file:** `orbit-research/RUN_EXPERIMENT_STATE.json`

Schema:

```jsonc
{
  "skill": "run-experiment",
  "phase": "step-5-launched" | "step-6-monitoring" | "step-7-completed",
  "status": "in_progress" | "awaiting_human_continue" | "completed",
  "run_id": "exp_<timestamp>_<short-hash-of-cmd>",
  "command": "<verbatim command sent to the GPU>",
  "server": "<ssh alias OR local OR vast:<id> OR modal:<app>>",
  "screen_name": "<screen session name on the remote>",
  "log_path": "<absolute path on the remote where stdout/stderr is tee'd>",
  "log_offset": 12345,                       // last byte we read; replay from here on resume
  "wandb_run_id": "<optional>",
  "next_action": "monitor | delegated-to-experiment-queue | done",
  "next_skill_hint": "/monitor-experiment OR /experiment-queue",
  "timestamp": "<ISO 8601 UTC>",
  "artifact_inventory": [
    "orbit-research/DIAGNOSTIC_RUN_REPORT.md",
    "orbit-research/DIAGNOSTIC_RUN_AUDIT.md"
  ]
}
```

### On entry — resume decision tree

1. Read STATE if it exists.
2. If `status = "completed"` AND user did not pass `— resume:` / `— fresh:` → ask "previous
   run completed; new run with same command, or fresh?" Default fresh under AUTO_PROCEED.
3. If `status = "in_progress"`:
   - `timestamp ≥ 24h` → stale; warn; default fresh start.
   - `timestamp < 24h` → **resume**, with this attach algorithm:
     ```text
     a. SSH to STATE.server, run: screen -ls | grep STATE.screen_name
        - If screen alive AND attached to a python process → log "resuming attached to live screen <name>"; tail STATE.log_path from STATE.log_offset; do not relaunch.
        - If screen exists but python died → log "screen orphaned, python exited"; tail log to capture exit reason; mark STATE.status = "completed" with notes; ask user whether to restart.
        - If screen gone, log file present → log "screen gone, log preserved"; tail log from STATE.log_offset to capture trailing output; ask user whether to relaunch with same command.
        - If screen gone AND log gone → log "no trace; safe to relaunch"; replay STATE.command (after user confirms unless AUTO_PROCEED).
     b. After attach/replay, continue from Step 6 (Monitor) below.
     ```
4. If `status = "awaiting_human_continue"` → re-invocation = approval; transition to in_progress and continue from `next_action`.

### Override flags

- `— resume: true` — force resume even if STATE looks ambiguous.
- `— fresh: true` — delete STATE; start fresh.
- `— queue: true` — force route to `/experiment-queue` regardless of detected job count.
- `— solo: true` — force inline run regardless of detected job count.

### Phase artifact map (for idempotent skip)

| Phase | Expected artifact |
|---|---|
| step-5-launched | `orbit-research/RUN_EXPERIMENT_STATE.json` with `screen_name` set |
| step-6-monitoring | `orbit-research/DIAGNOSTIC_RUN_REPORT.md` (interim updates) |
| step-7-completed | `orbit-research/DIAGNOSTIC_RUN_REPORT.md` finalised + `DIAGNOSTIC_RUN_AUDIT.md` written |

## ORBIT v1.3 Run Gates

These gates are always-on. Load:

- `shared-references/research-agent-pipeline.md` — v1.3 stage map and hard gates G0–G19
- `shared-references/semantic-code-audit.md` — Stage 17 diagnostic-run audit + G12 regime check
- `shared-references/continuation-contract.md` — STATE.json schema and resume rules (used by Step 0 + State Persistence above)

Run `mkdir -p orbit-research/`. Before launching anything broader than a diagnostic /
sanity run, verify:

- `orbit-research/PLAN_CODE_AUDIT.md` exists and its verdict line is `MATCHES_PLAN` or a
  scoped `PARTIAL_MISMATCH` whose missing pieces are irrelevant to this run (G11).
  `CRITICAL_MISMATCH` blocks. `ERROR` (Codex unavailable, audit could not complete) is
  **advisory at the diagnostic / sanity run stage**: surface the reason but proceed,
  because the diagnostic run is cheap. Scale-up via `/experiment-queue` will re-check and
  require explicit human acknowledgement before launching expensive runs.
- `orbit-research/DIAGNOSTIC_EXPERIMENT_PLAN.md` (v1.0 alias accepted: `TINY_RUN_PLAN.md`)
  names the exact diagnostic run.
- The first run is a diagnostic / sanity run unless the user explicitly overrides.

After the diagnostic run, write or update `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
(v1.0 alias on read: `TINY_RUN_REPORT.md`). Always write `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`
(v1.0 alias on read: `TINY_RUN_AUDIT.md`) with the verdict line `PASS`, `FIX_BEFORE_GPU`,
or `REDESIGN_EXPERIMENT`. Do not proceed to full runs until the verdict is `PASS`.

**G12 regime-aware failure interpretation (mandatory):** if the diagnostic run failed in
a regime that violates the mechanism's necessary preconditions (e.g. scale-dependent
emergent behaviour ablated by running at too small a scale, or a precondition from
`ABSTRACT_TASK_MECHANISM.md` / `MECHANISM_IDEATION.md` that the diagnostic regime
ablated), do NOT issue `REDESIGN_EXPERIMENT`. Instead, recommend redesigning the
diagnostic to a regime where the mechanism could in principle manifest, and document
the regime check explicitly in `DIAGNOSTIC_RUN_AUDIT.md`. If the regime check is
unanswerable, return `ERROR` with reason `regime_check_unanswerable` and escalate to
`HUMAN_DECISION_REQUIRED` rather than rejecting the mechanism. (See
`shared-references/semantic-code-audit.md` §5.)

**v1.0 alias note:** producers in v1.3 emit `DIAGNOSTIC_RUN_REPORT.md` and
`DIAGNOSTIC_RUN_AUDIT.md`; consumers (`/experiment-queue`, `/research-pipeline`) accept
either v1.3 or v1.0 alias names for one major version, preferring v1.3 if both exist.

## Workflow

### Step 1: Detect Environment

Read the project's `CLAUDE.md` to determine the experiment environment:

- **Local GPU** (`gpu: local`): Look for local CUDA/MPS setup info
- **Remote server** (`gpu: remote`): Look for SSH alias, conda env, code directory
- **Vast.ai** (`gpu: vast`): Check for `vast-instances.json` at project root — if a running instance exists, use it. Also check `CLAUDE.md` for a `## Vast.ai` section.
- **Modal** (`gpu: modal`): Serverless GPU via Modal. No SSH, no Docker, auto scale-to-zero. Delegate to `/serverless-modal`.

**Modal detection:** If `CLAUDE.md` has `gpu: modal` or a `## Modal` section, the entire deployment is handled by `/serverless-modal`. Jump to **Step 4: Deploy (Modal)** — Steps 2-3 are not needed (Modal handles code sync and GPU allocation automatically).

**Vast.ai detection priority:**
1. If `CLAUDE.md` has `gpu: vast` or a `## Vast.ai` section:
   - If `vast-instances.json` exists and has a running instance → use that instance
   - If no running instance → call `/vast-gpu provision` which analyzes the task, presents cost-optimized GPU options, and rents the user's choice
2. If no server info is found in `CLAUDE.md`, ask the user.

### Step 2: Pre-flight Check

Check GPU availability on the target machine:

**Remote (SSH):**
```bash
ssh <server> nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
```

**Remote (Vast.ai):**
```bash
ssh -p <PORT> root@<HOST> nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
```
(Read `ssh_host` and `ssh_port` from `vast-instances.json`, or run `vastai ssh-url <INSTANCE_ID>` which returns `ssh://root@HOST:PORT`)

**Local:**
```bash
nvidia-smi --query-gpu=index,memory.used,memory.total --format=csv,noheader
# or for Mac MPS:
python -c "import torch; print('MPS available:', torch.backends.mps.is_available())"
```

Free GPU = memory.used < 500 MiB.

### Step 3: Sync Code (Remote Only)

Check the project's `CLAUDE.md` for a `code_sync` setting. If not specified, default to `rsync`.

#### Option A: rsync (default)

Only sync necessary files — NOT data, checkpoints, or large files:
```bash
rsync -avz --include='*.py' --exclude='*' <local_src>/ <server>:<remote_dst>/
```

#### Option B: git (when `code_sync: git` is set in CLAUDE.md)

Push local changes to remote repo, then pull on the server:
```bash
# 1. Push from local
git add -A && git commit -m "sync: experiment deployment" && git push

# 2. Pull on server
ssh <server> "cd <remote_dst> && git pull"
```

Benefits: version-tracked, multi-server sync with one push, no rsync include/exclude rules needed.

#### Option C: Vast.ai instance

Sync code to the vast.ai instance (always rsync, code dir is `/workspace/project/`):
```bash
rsync -avz -e "ssh -p <PORT>" \
  --include='*.py' --include='*.yaml' --include='*.yml' --include='*.json' \
  --include='*.txt' --include='*.sh' --include='*/' \
  --exclude='*.pt' --exclude='*.pth' --exclude='*.ckpt' \
  --exclude='__pycache__' --exclude='.git' --exclude='data/' \
  --exclude='wandb/' --exclude='outputs/' \
  ./ root@<HOST>:/workspace/project/
```

If `requirements.txt` exists, install dependencies:
```bash
scp -P <PORT> requirements.txt root@<HOST>:/workspace/
ssh -p <PORT> root@<HOST> "pip install -q -r /workspace/requirements.txt"
```

### Step 3.5: W&B Integration (when `wandb: true` in CLAUDE.md)

**Skip this step entirely if `wandb` is not set or is `false` in CLAUDE.md.**

Before deploying, ensure the experiment scripts have W&B logging:

1. **Check if wandb is already in the script** — look for `import wandb` or `wandb.init`. If present, skip to Step 4.

2. **If not present, add W&B logging** to the training script:
   ```python
   import wandb
   wandb.init(project=WANDB_PROJECT, name=EXP_NAME, config={...hyperparams...})

   # Inside training loop:
   wandb.log({"train/loss": loss, "train/lr": lr, "step": step})

   # After eval:
   wandb.log({"eval/loss": eval_loss, "eval/ppl": ppl, "eval/accuracy": acc})

   # At end:
   wandb.finish()
   ```

3. **Metrics to log** (add whichever apply to the experiment):
   - `train/loss` — training loss per step
   - `train/lr` — learning rate
   - `eval/loss`, `eval/ppl`, `eval/accuracy` — eval metrics per epoch
   - `gpu/memory_used` — GPU memory (via `torch.cuda.max_memory_allocated()`)
   - `speed/samples_per_sec` — throughput
   - Any custom metrics the experiment already computes

4. **Verify wandb login on the target machine:**
   ```bash
   ssh <server> "wandb status"  # should show logged in
   # If not logged in:
   ssh <server> "wandb login <WANDB_API_KEY>"
   ```

> The W&B project name and API key come from `CLAUDE.md` (see example below). The experiment name is auto-generated from the script name + timestamp.

### Step 4: Deploy

#### Remote (via SSH + screen)

For each experiment, create a dedicated screen session with GPU binding:
```bash
ssh <server> "screen -dmS <exp_name> bash -c '\
  eval \"\$(<conda_path>/conda shell.bash hook)\" && \
  conda activate <env> && \
  CUDA_VISIBLE_DEVICES=<gpu_id> python <script> <args> 2>&1 | tee <log_file>'"
```

#### Vast.ai instance

No conda needed — the Docker image has the environment. Use `/workspace/project/` as working dir:
```bash
ssh -p <PORT> root@<HOST> "screen -dmS <exp_name> bash -c '\
  cd /workspace/project && \
  CUDA_VISIBLE_DEVICES=<gpu_id> python <script> <args> 2>&1 | tee /workspace/<log_file>'"
```

After launching, update the `experiment` field in `vast-instances.json` for this instance.

#### Modal (serverless)

When `gpu: modal` is detected, delegate to `/serverless-modal`:

1. **Analyze task** — determine VRAM needs, choose GPU, estimate cost
2. **Generate launcher** — create a `modal_launcher.py` that wraps the training script using `modal.Mount.from_local_dir` for code and `modal.Volume` for results
3. **Run** — `modal run modal_launcher.py` (runs locally, GPU executes remotely)
4. **Collect results** — results return via Volume or stdout, no manual download needed

Key Modal settings from `CLAUDE.md`:
- `modal_gpu`: GPU override (default: auto-select based on VRAM analysis)
- `modal_timeout`: Max seconds (default: 21600 = 6 hours)
- `modal_volume`: Named volume for persistent results

No SSH, no code sync, no screen sessions needed. Modal handles everything.

#### Local

```bash
# Linux with CUDA
CUDA_VISIBLE_DEVICES=<gpu_id> python <script> <args> 2>&1 | tee <log_file>

# Mac with MPS (PyTorch uses MPS automatically)
python <script> <args> 2>&1 | tee <log_file>
```

For local long-running jobs, use `run_in_background: true` to keep the conversation responsive.

### Step 5: Verify Launch

**Remote (SSH):**
```bash
ssh <server> "screen -ls"
```

**Remote (Vast.ai):**
```bash
ssh -p <PORT> root@<HOST> "screen -ls"
```

**Modal:**
```bash
modal app list         # Check app is running
modal app logs <app>   # Stream logs
```

**Local:**
Check process is running and GPU is allocated.

### Step 6: Feishu Notification (if configured)

After deployment is verified, check `~/.claude/feishu.json`:
- Send `experiment_done` notification: which experiments launched, which GPUs, estimated time
- If config absent or mode `"off"`: skip entirely (no-op)

### Step 7: Auto-Destroy Vast.ai Instance (when `gpu: vast` and `auto_destroy: true`)

**Skip this step if not using vast.ai or `auto_destroy` is `false`.**

After the experiment completes (detected via `/monitor-experiment` or screen session ending):

1. **Download results** from the instance:
   ```bash
   rsync -avz -e "ssh -p <PORT>" root@<HOST>:/workspace/project/results/ ./results/
   ```

2. **Download logs**:
   ```bash
   scp -P <PORT> root@<HOST>:/workspace/*.log ./logs/
   ```

3. **Destroy the instance** to stop billing:
   ```bash
   vastai destroy instance <INSTANCE_ID>
   ```

4. **Update `vast-instances.json`** — mark status as `destroyed`.

5. **Report cost**:
   ```
   Vast.ai instance <ID> auto-destroyed.
   - Duration: ~X.X hours
   - Estimated cost: ~$X.XX
   - Results saved to: ./results/
   ```

> This ensures users are never billed for idle instances. When `auto_destroy: true` (the default), the full lifecycle is automatic: rent → setup → run → collect → destroy.

## Key Rules

- ALWAYS check GPU availability first — never blindly assign GPUs (except Modal, which manages allocation automatically)
- Each experiment gets its own screen session + GPU (remote) or background process (local)
- Use `tee` to save logs for later inspection
- Run deployment commands with `run_in_background: true` to keep conversation responsive
- Report back: which GPU, which screen/process, what command, estimated time
- If multiple experiments, launch them in parallel on different GPUs
- **Vast.ai cost awareness**: When using `gpu: vast`, always report the running cost. If `auto_destroy: true`, destroy the instance as soon as all experiments on it complete
- **Modal cost awareness**: Always estimate and display cost before running. Modal auto-scales to zero — no idle billing, no manual cleanup

## CLAUDE.md Example

Users should add their server info to their project's `CLAUDE.md`:

```markdown
## Remote Server
- gpu: remote               # use pre-configured SSH server
- SSH: `ssh my-gpu-server`
- GPU: 4x A100 (80GB each)
- Conda: `eval "$(/opt/conda/bin/conda shell.bash hook)" && conda activate research`
- Code dir: `/home/user/experiments/`
- code_sync: rsync          # default. Or set to "git" for git push/pull workflow
- wandb: false              # set to "true" to auto-add W&B logging to experiment scripts
- wandb_project: my-project # W&B project name (required if wandb: true)
- wandb_entity: my-team     # W&B team/user (optional, uses default if omitted)

## Vast.ai
- gpu: vast                  # rent on-demand GPU from vast.ai
- auto_destroy: true         # auto-destroy after experiment completes (default: true)
- max_budget: 5.00           # optional: max total $ to spend per experiment

## Modal
- gpu: modal                 # serverless GPU via Modal (no SSH, auto scale-to-zero)
- modal_gpu: A100-80GB       # optional: override GPU selection (default: auto-select)
- modal_timeout: 21600       # optional: max seconds (default: 6 hours)
- modal_volume: my-results   # optional: named volume for results persistence

## Local Environment
- gpu: local                 # use local GPU
- Mac MPS / Linux CUDA
- Conda env: `ml` (Python 3.10 + PyTorch)
```

> **Vast.ai setup**: Run `pip install vastai && vastai set api-key YOUR_KEY`. Upload your SSH public key at https://cloud.vast.ai/manage-keys/. Set `gpu: vast` in your `CLAUDE.md` — `/run-experiment` will automatically rent an instance, run the experiment, and destroy it when done.

> **Modal setup**: Run `pip install modal && modal setup`. Bind a payment method at https://modal.com/settings (NEVER through CLI) to unlock the full $30/month free tier (without card: $5/month only). Set a workspace spending limit to prevent accidental charges. Set `gpu: modal` in your `CLAUDE.md` — ideal for users without a local GPU who need to debug code or run small-scale tests.

> **W&B setup**: Run `wandb login` on your server once (or set `WANDB_API_KEY` env var). The skill reads project/entity from CLAUDE.md and adds `wandb.init()` + `wandb.log()` to your training scripts automatically. Dashboard: `https://wandb.ai/<entity>/<project>`.
