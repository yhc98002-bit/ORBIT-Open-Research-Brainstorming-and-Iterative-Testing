# ORBIT — AI 辅助科研流水线

Release status: **ORBIT v2.2 stable candidate**. Methodology contract remains the
ORBIT v1.3 stage/gate model; runtime architecture is the ORBIT v2.2 pack/status workflow;
legacy Markdown artifacts are compatibility views.

ORBIT 是一套给 **Claude Code + Codex** 使用的科研工作流技能包。它的目标不是让 agent 盲目从 idea 一路跑到论文，而是帮你把科研过程拆成几个清楚的阶段：

1. 找方向、形成 proposal
2. 做实验计划和少量预实验
3. 跑正式诊断实验并解释结果
4. 把结果变成有证据支持的 claim
5. 写论文草稿、生成 submission package

你可以把 Claude Code 当成主控，让 Codex 作为独立 reviewer / auditor。这样可以降低单模型自嗨、漏看错误、过度 claim 的风险。

---

## 适合谁

适合你如果想做：

- AI / ML 研究 idea 发现
- proposal 打磨
- 实验设计
- 实验结果解释
- claim / evidence 对齐
- 论文草稿和投稿前检查

不适合你如果想要：

- 完全无人值守自动发 paper
- 不经过人工决策直接 scale up
- 不经过 Codex / reviewer 审查直接写 submission

ORBIT 的设计理念是：

> AI 可以推进流程，但高风险决策要让人确认。

---

## 推荐安装方式

最简单方式：

```bash
bash tools/install_aris.sh
```

这会把 ORBIT skills 安装到当前项目的 Claude Code skill 目录里。

如果你只想装轻量版本，可以使用 profile。但新用户建议先用默认完整安装，避免缺少 paper 或 Codex recovery 相关 skill。

可选的完整 idea-to-paper 精简安装：

```bash
bash tools/install_aris.sh --profile research-paper
```

`orbit-core` 只覆盖 STOP A 到 STOP C 的核心研究流程和 Codex recovery；它不包含
paper drafting / submission skills。`--profile` 是 reconcile 到指定 profile，不是叠加安装。

---

## Codex 设置

ORBIT 默认把 Codex 当成独立 reviewer。你需要先设置 Codex CLI / MCP：

```bash
npm install -g @openai/codex
codex setup
claude mcp add codex -s user -- codex mcp-server
```

如果 Codex MCP 临时不可用，ORBIT 不会默认降级成 Claude 单模型 review。它会生成一个 standalone Codex prompt，你可以复制到 Codex 终端运行，然后用：

```text
/import-codex-review "orbit-research/codex-imports/xxx.response.md"
```

导入结果。

---

## 你真正需要记住的命令

大部分情况下，你只需要这几个：

```text
/orbit-status
/idea-to-proposal
/experiment-bridge
/diagnostic-to-review
/paper-draft
/paper-from-claims
/submission-package
/import-codex-review
```

如果卡住，先运行：

```text
/orbit-status
```

它会告诉你：

- 当前在 STOP A/B/C/D 哪一步
- 缺什么 artifact
- 哪个 gate 没过
- 下一条安全命令是什么

---

## 完整使用流程

### 0. 随时查看状态

```text
/orbit-status
```

当你不知道下一步该干什么时，先用它。

---

### 1. 从研究方向到 proposal

```text
/idea-to-proposal "你的研究方向或想法"
```

例子：

```text
/idea-to-proposal "Discrete Diffusion VLA post-training"
```

它会做：

- idea discovery
- literature grounding
- assumption ledger
- mechanism ideation
- algorithm tournament
- proposal refinement

主要输出：

```text
proposal/proposal_pack.json
proposal/PROPOSAL.md
proposal/METHOD_SPEC.md
refine-logs/FINAL_PROPOSAL.md        # legacy compatibility view
```

结束后进入：

```text
STOP A：人类审阅 proposal
```

你要判断：

> 这个 proposal 值得进入实验计划阶段吗？

---

### 2. 从 proposal 到实验计划、代码、预实验

```text
/experiment-bridge "proposal/proposal_pack.json"
```

或旧路径：

```text
/experiment-bridge "refine-logs/FINAL_PROPOSAL.md"
```

它会做：

- 实验计划
- implementation bridge
- plan-code audit
- implementation smoke test
- headroom / probe（可选）

主要输出：

```text
experiment/experiment_pack.json
experiment/EXPERIMENT_PLAN.md
experiment/EXPERIMENT_PLAN_EXEC.md
experiment/PROBE_REPORT.md
experiment/HEADROOM_NOTE.md
```

注意：这里的 probe 不是正式 paper evidence。正式 diagnostic 由下一步负责。

结束后进入：

```text
STOP B：审阅实验计划、代码和预实验结果
```

---

### 3. 跑正式诊断实验并解释结果

```text
/diagnostic-to-review "experiment/experiment_pack.json"
```

或者传入一个明确的 diagnostic command：

```text
/diagnostic-to-review "python train.py --config configs/diag_main.yaml"
```

它会做：

- formal diagnostic run
- result interpretation
- claim relevance 判断
- result-to-claim
- red-team review
- STOP C review package

主要输出：

```text
orbit-research/diagnostics/<diagnostic_id>/DIAGNOSTIC_CONTEXT.json
orbit-research/diagnostics/<diagnostic_id>/RESULT_INTERPRETATION.md
claims/claim_ledger.json
claims/CLAIM_LEDGER.md
orbit-research/diagnostics/<diagnostic_id>/RED_TEAM_REVIEW.md
orbit-research/diagnostics/<diagnostic_id>/STOP_C_REVIEW.md
```

结束后进入：

```text
STOP C：人类审阅结果、claim 和 red-team review
```

你要决定：

- 继续写 paper？
- 先修实验？
- 重新设计 diagnostic？
- 缩小 claim？
- archive 这个方向？

如果要继续写 evidence-bound paper，通常需要一个：

```text
orbit-research/HUMAN_DECISION_NOTE.md
```

并且 final decision 是：

```text
PROCEED
```

---

### 4. 快速写草稿

如果你只是想先看论文长什么样：

```text
/paper-draft "proposal/PROPOSAL.md"
```

或者：

```text
/paper-draft "claims/claim_ledger.json"
```

这一步比较轻，不要求完整 submission gate。输出是 draft，不等于可投稿版本。

---

### 5. 从 claim ledger 写 evidence-bound paper

如果 STOP C 已经通过：

```text
/paper-from-claims "claims/claim_ledger.json"
```

它会严格按照 claim ledger 写，不应该发明 claim ledger 之外的新主张。

它要求：

- claim ledger ready
- Codex review passed / imported
- red-team verdict = READY_FOR_PAPER
- human decision = PROCEED

如果这些没满足，它会拒绝继续，并让你回到 `/orbit-status` 或 STOP C review。

---

### 6. 生成 submission package

```text
/submission-package "paper/"
```

它会检查：

- LaTeX 编译
- PDF 是否存在
- claim audit
- citation audit
- figures 是否存在
- references 是否 verified
- STOP C approval 是否成立

主要输出：

```text
paper/paper_package.json
paper/main.pdf
```

这是投稿前的严格检查阶段。

---

## 四个 STOP 是什么

ORBIT 的 human-in-the-loop 主要集中在四个地方：

| Stop | 阶段 | 你要判断什么 |
|---|---|---|
| STOP A | proposal 后 | 这个想法值得做实验计划吗？ |
| STOP B | experiment bridge 后 | 实验计划、代码、probe 是否足够进入正式 diagnostic？ |
| STOP C | diagnostic/review 后 | 结果和 claim 是否值得写 paper / scale up？ |
| STOP D | submission 前 | paper package 是否可以提交？ |

---

## Codex review 失败怎么办

如果 Claude Code 调 Codex MCP 失败，ORBIT 会生成类似：

```text
orbit-research/codex-prompts/<phase>.md
```

你可以：

1. 打开这个 prompt
2. 复制到 standalone Codex terminal
3. 保存 Codex 输出到：

```text
orbit-research/codex-imports/<phase>.response.md
```

4. 导入：

```text
/import-codex-review "orbit-research/codex-imports/<phase>.response.md"
```

导入 Codex review 不等于人类批准。它只是补上 Codex review 这个环节。

---

## 常见问题

### Q: 我卡住了，不知道下一步怎么走

运行：

```text
/orbit-status
```

不要先随便 prompt vibe coding。

---

### Q: 我只是想快速写个 paper 草稿

用：

```text
/paper-draft
```

不要直接用 `/paper-from-claims`，后者是 evidence-bound paper，需要 STOP C approval。

---

### Q: 我想从 idea 一路到 paper，应该装哪个 profile？

新用户建议直接完整安装：

```bash
bash tools/install_aris.sh
```

如果你使用 profile，请确认你的 profile 包含：

```text
orbit-status
idea-to-proposal
experiment-bridge
diagnostic-to-review
paper-draft
paper-from-claims
submission-package
import-codex-review
```

否则完整 idea-to-paper flow 可能缺命令。

推荐的精简完整 profile 是：

```bash
bash tools/install_aris.sh --profile research-paper
```

`orbit-core` 不是完整 paper workflow；它只覆盖 STOP A 到 STOP C 和 Codex recovery。

---

### Q: `CLAIM_CONSTRUCTION.md` 还重要吗？

在 v2 工作流里，canonical source 是：

```text
claims/claim_ledger.json
```

`CLAIM_CONSTRUCTION.md` 只是 legacy / compatibility view。

---

### Q: `paper-writing` 还能用吗？

`/paper-writing` 现在主要是 compatibility router。新流程推荐：

```text
/paper-draft
/paper-from-claims
/submission-package
```

---

## 目录结构简化理解

你主要会看到这些目录：

```text
proposal/
  proposal_pack.json
  PROPOSAL.md
  METHOD_SPEC.md

experiment/
  experiment_pack.json
  EXPERIMENT_PLAN.md
  EXPERIMENT_PLAN_EXEC.md
  PROBE_REPORT.md
  HEADROOM_NOTE.md

claims/
  claim_ledger.json
  CLAIM_LEDGER.md

orbit-research/
  ORBIT_STATE.json
  diagnostics/
  codex-prompts/
  codex-imports/

paper/
  main.tex
  main.pdf
  paper_package.json
```

其中：

```text
*.json = AI / workflow source of truth
*.md   = human-readable view
```

---

## 最小记忆版

如果你只想记住一条流程：

```text
/idea-to-proposal "方向"
/experiment-bridge "proposal/proposal_pack.json"
/diagnostic-to-review "experiment/experiment_pack.json"
/paper-draft "claims/claim_ledger.json"
/paper-from-claims "claims/claim_ledger.json"
/submission-package "paper/"
```

任何时候卡住：

```text
/orbit-status
```

Codex MCP 坏了：

```text
/import-codex-review "orbit-research/codex-imports/xxx.response.md"
```
