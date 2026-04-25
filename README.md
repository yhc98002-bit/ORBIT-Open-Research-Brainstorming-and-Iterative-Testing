# BRIS: Better Research in Sleep

BRIS 是基于 ARIS 的自动科研 skill 组。它保留 ARIS 的成熟基础设施，例如文献检索、idea 发现、实验部署、自动审稿、论文写作、claim audit 和 citation audit，但把科研流程重构为更严格的 0A-15 诊断式流水线。

核心目标：让 agent 不只是自动推进实验，而是像 junior research scientist 一样先定义问题、看数据、测 baseline ceiling、设计可诊断实验、审计代码是否忠实实现计划，再把结果约束成合理论文 claim。

## 快速开始

在 Claude Code 中使用：

```text
/research-pipeline "你的研究方向"
```

如果已经有实验结果并准备写论文：

```text
/result-to-claim "results/"
/paper-writing "NARRATIVE_REPORT.md" - venue: ICLR, assurance: submission
```

如果只想跑某一段：

```text
/research-lit "topic"
/idea-discovery "topic"
/research-refine "problem | rough method"
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
/run-experiment "tiny diagnostic run"
/analyze-results "results/"
/auto-review-loop "paper or project"
```

## 安装到项目

推荐项目级安装，避免污染全局 skills：

```bash
bash tools/install_aris.sh
```

如果只想手动复制：

```bash
mkdir -p .claude/skills
cp -r skills/* .claude/skills/
```

Codex reviewer 需要安装 Codex CLI / MCP：

```bash
npm install -g @openai/codex
codex setup
claude mcp add codex -s user -- codex mcp-server
```

BRIS 默认 Codex reviewer 配置：

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
sandbox_mode = "danger-full-access"
```

## 完整科研流水线

BRIS 的主入口是 `/research-pipeline`。它按以下阶段推进：

```text
0A. Seed Framing
1. Question-driven Literature Map
0B. Problem Taste / Problem Selection
2. Task Ontology / Data Audit
3. Baseline Ceiling / Headroom Audit
4. Hypothesis-Mechanism-Benchmark-Control Matrix
5. Null-result Contract
6. Progressive Component Ladder
7. Minimal Diagnostic Experiment Design
7.5 Plan-Code Consistency Audit
8. Tiny Run / Sanity Run
8.5 Tiny Run Audit
9. Result Interpretation Loop
10. Re-read Literature After Early Results
11. Scale-up Experiment
12. Result-to-Claim Construction
13. Tie / Negative Result Strategy
14. Reviewer Red-team
15. Human Decision / Next Research Loop
```

这不是直线流程。每次实验后都要解释结果，再决定下一步：

```text
读文献 -> 发现问题 -> 看数据 -> 测 baseline -> 设计机制
   ^                                          |
   |                                          v
重新读文献 <- 解释结果 <- 小实验 <- 渐进加组件 <- 控制变量
```

## 强制门禁

BRIS 的关键价值不是多跑实验，而是阻止错误实验被自动放大。

必须遵守：

- 没有 `TASK_ONTOLOGY.md`，不得进入方法设计。
- 没有 `BASELINE_CEILING.md`，不得跑 proposed method。
- 没有可解释的 `NULL_RESULT_CONTRACT.md`，不得跑实验。
- 没有 `COMPONENT_LADDER.md`，不得直接跑 full system。
- 没有通过 `PLAN_CODE_AUDIT.md`，不得 GPU scale-up。
- 没有通过 `TINY_RUN_AUDIT.md`，不得 full run。
- 每次实验后必须更新 `RESULT_INTERPRETATION.md`。
- 打平或失败必须写 `NEGATIVE_RESULT_STRATEGY.md`，不能硬写成功故事。
- 写论文前必须有 `CLAIM_CONSTRUCTION.md` 和 `RED_TEAM_REVIEW.md`。

## 关键产物

完整流程会在 `bris-research/` 下积累这些文件：

```text
SEED_FRAMING.md
LITERATURE_MAP.md
PROBLEM_SELECTION.md
TASK_ONTOLOGY.md
BASELINE_CEILING.md
CONTROL_DESIGN.md
NULL_RESULT_CONTRACT.md
COMPONENT_LADDER.md
DIAGNOSTIC_EXPERIMENT_PLAN.md
PLAN_CODE_AUDIT.md
TINY_RUN_REPORT.md
TINY_RUN_AUDIT.md
RESULT_INTERPRETATION.md
LITERATURE_REREAD_NOTE.md
SCALEUP_DECISION.md
CLAIM_CONSTRUCTION.md
NEGATIVE_RESULT_STRATEGY.md
RED_TEAM_REVIEW.md
HUMAN_DECISION_NOTE.md
```

同时继续兼容原 ARIS 产物：

```text
idea-stage/IDEA_REPORT.md
idea-stage/IDEA_CANDIDATES.md
refine-logs/FINAL_PROPOSAL.md
refine-logs/EXPERIMENT_PLAN.md
refine-logs/EXPERIMENT_TRACKER.md
review-stage/AUTO_REVIEW.md
NARRATIVE_REPORT.md
paper/
```

## Claude vs Codex 辩论

BRIS 在关键节点使用 Claude vs Codex 多轮辩论，避免单一模型收敛到局部最优。

默认模式：

```text
Claude: propose
Codex: critique
Claude: revise
Codex: final objections
Claude: consensus decision
Human: approve / redirect
```

每个节点最多两轮，输出必须是：

```text
CONSENSUS
DISAGREEMENT
HUMAN_DECISION_REQUIRED
```

Codex 不只做代码风格审查。关键脚本必须经过 semantic implementation audit，检查代码是否真的实现了自然语言实验计划、baseline、control、ablation、dataset split、metric 和 component ladder。

## 常用工作流

### 1. 从领域词开始

```text
/research-pipeline "Discrete Diffusion VLA post-training"
```

BRIS 会先做 seed framing 和 literature map，不会直接生成方法。

### 2. 已经有 idea，想打磨成实验计划

```text
/research-refine "problem | rough method"
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

在 BRIS 模式下，`experiment-plan` 会补齐 task ontology、baseline ceiling、control design、null-result contract、component ladder 和 diagnostic experiment plan。

### 3. 从计划到代码和小跑

```text
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
/run-experiment "tiny diagnostic run"
/monitor-experiment "run id or server"
```

全量实验前必须通过 `PLAN_CODE_AUDIT.md` 和 `TINY_RUN_AUDIT.md`。

### 4. 结果解释和 claim 构造

```text
/analyze-results "results/"
/result-to-claim "results/"
```

BRIS 会判断结果支持什么、不支持什么、是否需要降级 claim，失败时是否能转成 negative result、benchmark diagnosis 或 failure taxonomy。

### 5. 论文写作

```text
/paper-writing "NARRATIVE_REPORT.md" - venue: ICLR, assurance: submission
```

原 ARIS 论文链条仍然保留：

```text
/paper-plan
/paper-figure
/figure-spec 或 /paper-illustration
/paper-write
/paper-compile
/auto-paper-improvement-loop
/paper-claim-audit
/citation-audit
```

BRIS 额外要求：论文写作前必须先有 claim construction 和 reviewer red-team，不能把失败结果包装成成功故事。

## 重要文件

- `skills/research-pipeline/SKILL.md`：BRIS 总控入口。
- `skills/shared-references/research-agent-pipeline.md`：0A-15 流程和硬门禁。
- `skills/shared-references/research-harness-prompts.md`：每阶段 harness prompt。
- `skills/shared-references/semantic-code-audit.md`：Codex 语义代码审查协议。
- `skills/shared-references/reviewer-routing.md`：reviewer 默认路由。

## 设计原则

```text
大胆想，谨慎跑。
先诊断，再放大。
先 baseline，再 method。
先控制变量，再 claim。
先小实验，再 full run。
代码能跑不是成功，代码忠实实现实验计划才是成功。
```
