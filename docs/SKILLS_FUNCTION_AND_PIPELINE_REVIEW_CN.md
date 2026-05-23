# ORBIT / ARIS Skills 功能与 Pipeline Review

**日期**：2026-05-08  
**范围**：本文件基于仓库当前 `skills/`、`skills/shared-references/`、`README.md`、`AGENT_GUIDE.md`、关键 orchestrator skill 与模板文件的实际内容整理。  
**结论**：这个仓库不是一组松散的工具 skill，而是一个以 **ORBIT v1.3 research-methodology routing harness** 为核心、复用 ARIS 执行技能的科研流水线系统。它的主线是：从研究方向/想法出发，经过 Discovery、Grounding、Innovation、Validation，再进入实验、结果解释、claim 构造、red-team 和论文写作。

---

## 1. 当前 Skills 组实际结构

仓库中当前存在：

- **71 个顶层 skill**：位于 `skills/<skill-name>/SKILL.md`。
- **72 个 `skills/skills-codex/` 镜像 skill**：面向 Codex CLI / Codex 使用场景的全量副本，由 `tools/sync_codex_mirror.py` 从顶层 `skills/` 同步生成。
- **8 个 `skills/skills-codex-claude-review/` 镜像 skill**：偏 Claude-review 集成。
- **15 个 `skills/skills-codex-gemini-review/` 镜像 skill**：偏 Gemini-review 集成。
- **24 个 shared reference 文档**：位于 `skills/shared-references/`，定义跨 skill 的协议、审计、输出、reviewer 独立性、paper writing 原则等。

顶层 `skills/` 是最完整、最主要的 skill 集合；`skills-codex/` 是全量镜像，`skills-codex-claude-review/` 与 `skills-codex-gemini-review/` 是 reviewer overlay。维护时先改顶层，再运行 `tools/sync_codex_mirror.py`，避免同名 skill 漂移。

---

## 2. 系统定位

ORBIT v1.3 的定位是：

> 一个按 **mode** 与 **risk** 路由的科研方法学 harness，用文件协议串联多个 skill，并通过 verdict-line gate 控制从 idea 到 GPU、从结果到 claim、从 claim 到论文的高风险转移。

它不是简单的“自动写论文”工具，也不是单纯“跑实验”工具。它更像一个科研项目操作系统：

- 在早期鼓励发散：找问题、查文献、提出机制、类比迁移、算法 tournament。
- 在承诺实验前收紧：假设 ledger、抽象任务、baseline ceiling、control/null-result/component/formalization。
- 在花 GPU 前审计：plan-code consistency audit，sanity/diagnostic first。
- 在写论文前收窄 claim：result-to-claim、negative/tie strategy、human decision、red-team。
- 在投稿前加固论文：paper claim audit、citation audit、proof audit、auto improvement loop。

---

## 3. 四条主 Spine

ORBIT v1.3 把科研流程拆成 4 条 spine，但并不强制每次线性跑完全部 26 个阶段。`/research-pipeline` 会先做 Stage 0 routing，再根据输入形态和已有 artifact 决定从哪里开始。

| Spine | Stage | 目标 | 主要产物 |
|---|---:|---|---|
| Discovery | 0, 1, 2, 2.5, 3 | 识别输入形态、文献定位、问题重构、问题选择 | `MODE_ROUTING.md`, `SEED_FRAMING.md`, `LITERATURE_MAP.md`, `PROBLEM_SELECTION.md` |
| Grounding | 4, 5, 6, 7 | 在创新前钉住假设、抽象任务、artifact audit、baseline ceiling | `ASSUMPTION_LEDGER.md`, `ABSTRACT_TASK_MECHANISM.md`, `ARTIFACT_AUDIT.md`, `BASELINE_CEILING.md` |
| Innovation | 8, 9, 10, 18.5 | 发散机制、类比迁移、算法 sketch tournament、失败后再创新 | `MECHANISM_IDEATION.md`, `ANALOGY_TRANSFER.md`, `ALGORITHM_TOURNAMENT.md`, `FAILURE_TO_INNOVATION.md` |
| Validation | 11-25 | 设计可诊断实验、实现、审计、运行、解释、构造 claim、写论文 | `CONTROL_DESIGN.md`, `NULL_RESULT_CONTRACT.md`, `PLAN_CODE_AUDIT.md`, `CLAIM_CONSTRUCTION.md`, `RED_TEAM_REVIEW.md`, `paper/` |

---

## 4. Mode 与 Risk Routing

`/research-pipeline` 的第一步是 Stage 0，写入 `orbit-research/MODE_ROUTING.md`。它根据用户输入与已有 artifact 判断模式：

| Mode | 典型输入 | 行为 |
|---|---|---|
| `EXPLORATION` | 一个研究方向、领域关键词 | 快速探索，不承诺方法，不强行跑实验 |
| `INNOVATION` | 有具体问题，但方法未定 | 运行 Grounding + Innovation loops，生成多个机制候选 |
| `COMMITMENT` | 已有 proposal/experiment plan/code/results | 启动 Validation gates，控制 GPU、scale-up、paper claim 等高风险动作 |

Risk 取值 1-5：

- 1-2：本地、可逆、探索性动作。
- 3：非平凡 GPU 或诊断实验。
- 4：正式实验、scale-up、paper claim。
- 5：公开发布、投稿、arXiv、正式对外结论。

高风险转移必须经过对应 gate；低风险探索不会被完整 gate 系统拖慢。

---

## 5. 标准 4-Stop Human-in-the-Loop 流程

仓库 README 定义了标准 4-stop 工作流。实际推荐把它当成主 pipeline：

```text
STOP A: /idea-to-proposal
  从方向/想法到 proposal index + experiment plan index + execution plan
  人类决定：是否值得开始写代码 / 花 GPU

STOP B: /experiment-bridge
  从计划到实验代码 + plan-code audit
  人类决定：PLAN_CODE_AUDIT 是否允许进入 GPU 诊断

STOP C: /diagnostic-to-review
  运行诊断实验 → 分析结果 → claim construction → red-team
  人类决定：scale-up、补实验、pivot，还是进入论文写作

STOP D: /paper-writing
  从 narrative/claim 到 paper/ PDF + audit + improvement
  人类决定：是否投稿 / push Overleaf / arXiv
```

每个 stop 之间，skill 可以自动连续运行；每个 stop 结束时写 `STATE.json`，通常以 `awaiting_human_continue` 停住。

---

## 6. 主 Pipeline：从 Idea 到 Proposal 与 Experiment Plan

### 推荐入口

```text
/idea-to-proposal "<research keyword OR path/to/context.md OR path/to/draft-idea.md>"
```

### 工作流

1. **Phase 0：输入识别**
   - keyword-mode：输入是研究方向或短语。
   - context-mode：输入是大量背景、约束、论文笔记、负例或资源说明的 `.md`；还没有选定 idea。
   - idea-mode：输入是已有 `.md` idea / method 草稿，表示已经选定方向。
   - 显式参数优先：`— input-mode: context` / `— context: true` 强制走 discovery；`— input-mode: idea` / `— idea: true` 才跳过 discovery。
   - 歧义 `.md` 默认按 context-mode 处理，避免用户只是传长上下文却意外跳过 discovery。
   - 写 `orbit-research/PIPELINE_INTAKE.md` 和 `IDEA_TO_PROPOSAL_STATE.json`。

2. **Phase 0.5：可选文献预抓取**
   - 由 `— arxiv download: true` 触发。
   - 委托 `/research-lit`，可用 arXiv / Semantic Scholar / DeepXiv / Exa 等。
   - 下载到 `papers/`，可同步到 `research-wiki/`。

3. **Phase 1：Discovery**
   - keyword-mode：调用 `/idea-discovery`。
   - context-mode：先把 `.md` 压缩成 `PIPELINE_INTAKE.md` 里的 discovery brief，再调用 `/idea-discovery`；原始 `.md` 只作为上下文和约束，不作为已选方案。
   - idea-mode：调用 `/research-refine`。
   - 产出 `refine-logs/FINAL_PROPOSAL.md` 与 `orbit-research/PROBLEM_SELECTION.md`。

4. **Phase 2：Grounding**
   - 写 `ASSUMPTION_LEDGER.md`。
   - 写 `ABSTRACT_TASK_MECHANISM.md`。
   - 写 `BASELINE_CEILING.md`。

5. **Phase 3：Innovation**
   - Stage 8：`MECHANISM_IDEATION.md`，生成 5-10 个机制候选。
   - Stage 9：`ANALOGY_TRANSFER.md`，做跨领域类比迁移。
   - Stage 10：`ALGORITHM_TOURNAMENT.md`，做 sketch tournament，输出 `TENTATIVE_PREFERRED_SKETCH_ID`。
   - 这里 Codex 是 collaborative mode：增加候选，不负责否决。

6. **Phase 4：Final Refinement**
   - 再次调用 `/research-refine`。
   - 把 tournament winner、assumption ledger、abstract mechanism 整合进最终 proposal。
   - 这里 Codex 回到 adversarial mode。

7. **Phase 5：Pipeline Summary**
   - 写 `orbit-research/PIPELINE_SUMMARY.md`。

8. **Phase 6：Experiment Planning**
   - 调用 `/experiment-plan "refine-logs/FINAL_PROPOSAL.md"`。
   - 生成 pre-GPU 的 validation prereqs。

### 主要交付物

`refine-logs/`：

- `FINAL_PROPOSAL.md`：proposal 索引，不再是长 proposal。
- `FINAL_PROPOSAL_SHORT.md`：2-4 页干净短 proposal。
- `METHOD_SPEC.md`：实现级方法规格。
- `EXPERIMENT_PLAN.md`：实验计划索引。
- `EXPERIMENT_PLAN_EXEC.md`：claim map、实验 blocks、run order、budget、gates。
- `EXPERIMENT_TRACKER.md`：运行清单。

`orbit-research/`：

- `PROBLEM_SELECTION.md`
- `ASSUMPTION_LEDGER.md`
- `ABSTRACT_TASK_MECHANISM.md`
- `BASELINE_CEILING.md`
- `MECHANISM_IDEATION.md`
- `ANALOGY_TRANSFER.md`
- `ALGORITHM_TOURNAMENT.md`
- `CONTROL_DESIGN.md`
- `NULL_RESULT_CONTRACT.md`
- `COMPONENT_BUNDLE_LADDER.md`
- `ALGORITHMIC_FORMALIZATION.md`
- `DIAGNOSTIC_EXPERIMENT_PLAN.md`
- `PIPELINE_SUMMARY.md`

---

## 7. Proposal 与 Experiment Plan 的渐进式披露格式

当前仓库已改为渐进式披露：

### Proposal

```text
refine-logs/FINAL_PROPOSAL.md        # 索引 / reading paths / status
refine-logs/FINAL_PROPOSAL_SHORT.md  # mentor/coauthor 快速阅读版本
refine-logs/METHOD_SPEC.md           # 实现所需公式、模块、数据流、超参
refine-logs/FAILURE_CONTRACT.md      # 可选，失败路由
refine-logs/FINAL_PROPOSAL_FULL.md   # 可选，历史长版归档
```

### Experiment Plan

```text
refine-logs/EXPERIMENT_PLAN.md       # 索引 / reading paths / constraints
refine-logs/EXPERIMENT_PLAN_EXEC.md  # 可执行实验设计
refine-logs/*_RUN_CARD.md            # 可选，当前或关键 milestone
refine-logs/*_PROTOCOL.md            # 可选，数据映射 / baseline / figure 等局部协议
refine-logs/EXPERIMENT_TRACKER.md    # run status
```

这样做的目的：

- 顶层文件不再堆满重复说明。
- 下游 agent 先读索引，再读自己需要的执行文件。
- 长历史只在有用时归档，不占默认上下文。
- `/experiment-bridge` 能跟随 `EXPERIMENT_PLAN.md -> EXPERIMENT_PLAN_EXEC.md -> run card -> METHOD_SPEC.md`。

---

## 8. 主 Pipeline：从 Plan 到 Code 与 Diagnostic

### 推荐入口

```text
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
```

### 工作流

1. **解析实验计划**
   - 先读 `EXPERIMENT_PLAN.md` 索引。
   - 再读 `EXPERIMENT_PLAN_EXEC.md`。
   - 如存在当前 run card，则 run card 优先。
   - 方法细节优先读 `METHOD_SPEC.md`。

2. **实现实验代码**
   - 扫描已有代码，优先复用。
   - 写训练、评估、数据加载、baseline、配置、日志、JSON/CSV 输出。
   - 所有超参要 argparse/config 化。

3. **Plan-Code Consistency Audit**
   - 调用 Codex GPT-5.5 xhigh 做语义审计。
   - 必须写 `orbit-research/PLAN_CODE_AUDIT.md`。
   - verdict 必须是：
     - `MATCHES_PLAN`
     - `PARTIAL_MISMATCH`
     - `CRITICAL_MISMATCH`
     - `ERROR`

4. **Sanity First**
   - 默认先跑最小 sanity。
   - sanity 失败时最多自动 debug 3 次。

5. **部署实验**
   - 小批量走 `/run-experiment`。
   - 大于等于 10 个 jobs、多 seed sweep、依赖 wave 走 `/experiment-queue`。

6. **收集初始结果**
   - 更新 `EXPERIMENT_TRACKER.md`。
   - 每个 run 都必须写入 `RUN_LEDGER.jsonl`：run_id、命令、config、commit、日志、结果文件、失败状态。
   - 写 `EXPERIMENT_RESULTS.md` 或相关 summary。
   - 若主结果为正，可触发 `/ablation-planner`，追加到 `EXPERIMENT_PLAN_EXEC.md`。

### STOP B

进入 GPU 前，人类应检查：

- `orbit-research/PLAN_CODE_AUDIT.md`
- 实验代码与 `METHOD_SPEC.md` 是否一致。
- `EXPERIMENT_PLAN_EXEC.md` 的当前 milestone 是否真的值得跑。

---

## 9. Run / Queue / Monitor 执行层

### `/run-experiment`

统一的实验启动入口。它会根据输入自动决定是否委托 `/experiment-queue`：

| 输入 | 行为 |
|---|---|
| 单条 command | inline run |
| <= 5 jobs | inline / parallel run |
| 6-9 jobs | 默认 inline parallel，可强制 `— queue: true` |
| >= 10 jobs | 自动委托 `/experiment-queue` |
| manifest / grid spec | 解析 job count 后路由 |

支持：

- local GPU
- remote SSH
- Vast.ai
- Modal serverless GPU
- screen resume
- W&B logging
- `RUN_EXPERIMENT_STATE.json`

诊断实验后必须产出：

- `orbit-research/DIAGNOSTIC_RUN_REPORT.md`
- `orbit-research/DIAGNOSTIC_RUN_AUDIT.md`

### `/experiment-queue`

面向大规模 grid / multi-seed / wave chain。它会：

- 检查 plan-code audit、diagnostic audit、scaleup decision、human decision。
- 自动检测 GPU 空闲情况。
- 处理 OOM retry。
- 清理 stale screen。
- 管理 wave transition。
- 持久化 `queue_state.json`。

这是 Stage 20 scale-up 的执行层，不应绕过前置 gates 直接用于正式大跑。

### `/monitor-experiment`

用于追踪正在运行的实验；在 queue 模式下读取 queue state，在普通模式下检查 screen/log/W&B。

---

## 10. 主 Pipeline：Diagnostic 到 Claim 与 Review

### 推荐入口

```text
/diagnostic-to-review "<diagnostic command OR manifest>"
```

### 前置条件

- `PLAN_CODE_AUDIT.md` verdict 是 `MATCHES_PLAN` 或可接受的 `PARTIAL_MISMATCH`。
- `NULL_RESULT_CONTRACT.md` 存在。
- `COMPONENT_BUNDLE_LADDER.md` 存在，除非明确是单组件 baseline 复现。

### 工作流

1. **Phase 1：Run**
   - 调用 `/run-experiment`。
   - 若 `DIAGNOSTIC_RUN_AUDIT != PASS`，停止并给出 next action。

2. **Phase 2：Analyze**
   - 调用 `/analyze-results`。
   - 先检查结果文件是否能对应到 `RUN_LEDGER.jsonl` 的 run_id；孤儿结果、缺 seed、失败 run 要报告。
   - 写 `RESULT_INTERPRETATION.md`。
   - 若结果失败、混合、矛盾或意外，先写 `RESEARCH_DECISION_LOG.md` 再路由。
   - 检查无结果、指标污染、评估欺诈等问题。

3. **Phase 3：Claim**
   - 调用 `/result-to-claim`。
   - 写 `CLAIM_CONSTRUCTION.md` 与 `HUMAN_DECISION_NOTE.md`。
   - 如果是负结果/打平，写 `NEGATIVE_RESULT_STRATEGY.md`。
   - 如果 `claim_supported = no`，按 `RESEARCH_DECISION_LOG.md` 决定局部 patch、改诊断、failure-to-innovation、scoped proposal-revise 或 archive；不默认重跑 `/idea-to-proposal` 或同时修改 proposal+plan。

4. **Phase 4：Red-team**
   - 调用 `/auto-review-loop`。
   - 写 `RED_TEAM_REVIEW.md`。

5. **Phase 5：Summary**
   - 写 `orbit-research/PIPELINE_SUMMARY.md`。
   - 以 `awaiting_human_continue` 停在 STOP C。

### STOP C

人类需要联合审查：

- `CLAIM_CONSTRUCTION.md`
- `RED_TEAM_REVIEW.md`
- `HUMAN_DECISION_NOTE.md`
- `RESEARCH_DECISION_LOG.md`（如果本轮诊断失败、混合或意外）
- 是否 scale-up、补实验、pivot、还是进入论文写作。

---

## 11. Result-to-Claim Gate

`/result-to-claim` 的职责是把会影响论文级 claim scope 的实验数字转成可审查的 claim support，
而不是把每个诊断结果包装成好故事。

它会：

- 汇总 W&B、`EXPERIMENT_LOG.md`、`EXPERIMENT_TRACKER.md`、日志、研究 contract。
- 调用 Codex 判断：
  - `claim_supported: yes | partial | no`
  - 支持什么，不支持什么。
  - 缺什么证据。
  - 是否需要补实验或缩小 claim。
- 写：
  - `CLAIM_CONSTRUCTION.md`
  - `HUMAN_DECISION_NOTE.md`
  - 必要时 `NEGATIVE_RESULT_STRATEGY.md`

关键规则：

- 如果 `NULL_RESULT_CONTRACT` 已经定义这是 tie/failure，不能写 positive framing。
- post-hoc reframing 必须标注为 exploratory finding。
- Codex 是 judge；执行 agent 只收集证据和路由。

---

## 12. 主 Pipeline：Paper Writing

### 推荐入口

```text
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
```

### 前置条件

paper-writing 有 ORBIT inline guard：

- 必须存在 `orbit-research/CLAIM_CONSTRUCTION.md`。
- 必须存在 `orbit-research/RED_TEAM_REVIEW.md`。
- 必须存在 `orbit-research/HUMAN_DECISION_NOTE.md`。
- 如果方法失败/打平/混合结果，还需要 `NEGATIVE_RESULT_STRATEGY.md`。

缺 `CLAIM_CONSTRUCTION.md` 时应直接拒绝启动。这是 G16/G18 的强制要求。

### 工作流

```text
/paper-plan
  -> PAPER_PLAN.md, claims-evidence matrix, figure/table plan

/paper-figure
  -> figures/, plots, tables, latex snippets

/figure-spec | /paper-illustration | /paper-illustration-image2 | /mermaid-diagram
  -> architecture / method illustration

/paper-write
  -> paper/main.tex, sections, references.bib

/paper-compile
  -> paper/main.pdf

/auto-paper-improvement-loop
  -> review/fix/recompile rounds

/paper-claim-audit
  -> numerical claim audit

/citation-audit
  -> citation correctness audit
```

`— assurance: submission` 或高 effort 时，最终 report 需要通过 `tools/verify_paper_audits.sh`。

---

## 13. 辅助 Skill 分组

### 文献与知识库

| Skill | 功能 |
|---|---|
| `/research-lit` | 多源文献检索与综述，支持 arXiv / Semantic Scholar / DeepXiv / Exa 等 |
| `/arxiv` | arXiv 检索、下载、摘要 |
| `/semantic-scholar` | 正式出版文献、引用、venue 信息 |
| `/deepxiv` | DeepXiv 风格论文分析 |
| `/exa-search` | Web / broader search |
| `/alphaxiv` | 单篇论文 LLM 优化摘要 |
| `/research-wiki` | 项目知识库、paper/idea/claim/experiment 图谱 |

### Idea / Proposal / Review

| Skill | 功能 |
|---|---|
| `/idea-creator` | 生成和排序研究 idea |
| `/idea-discovery` | research-lit -> idea-creator -> novelty-check -> research-review |
| `/novelty-check` | 查新 |
| `/research-review` | Codex GPT-5.5 xhigh 深度批评 |
| `/research-refine` | 迭代 reviewer loop，把粗 idea 打磨成 method spec |
| `/proposal-revise` | STOP A 后或失败诊断后，按 critique / RESEARCH_DECISION_LOG 定向 patch proposal / experiment plan |

### 实验与诊断

| Skill | 功能 |
|---|---|
| `/experiment-plan` | 生成实验计划索引、执行计划和 validation prereqs |
| `/experiment-bridge` | 计划到代码，plan-code audit，sanity，部署 |
| `/run-experiment` | 单入口运行实验，自动 solo/queue 路由 |
| `/experiment-queue` | 大批量实验队列 |
| `/monitor-experiment` | 监控实验 |
| `/training-check` | 训练健康检查 |
| `/experiment-audit` | 实验完整性审计 |
| `/analyze-results` | 统计分析与结果解释 |
| `/ablation-planner` | 正结果后的 ablation 设计 |

### Claim / Paper

| Skill | 功能 |
|---|---|
| `/result-to-claim` | 结果到 claim gate |
| `/auto-review-loop` | 多轮研究 review / fix |
| `/paper-plan` | 论文结构与 claims-evidence matrix |
| `/paper-figure` | 数据图表 |
| `/figure-spec` | 可复现 SVG 架构图 |
| `/paper-write` | LaTeX 写作 |
| `/paper-compile` | PDF 编译与修复 |
| `/paper-writing` | 论文全流程 orchestrator |
| `/paper-claim-audit` | 论文数值 claim 审计 |
| `/citation-audit` | 引用审计 |
| `/auto-paper-improvement-loop` | 自动论文改进循环 |

### 专利与其他输出

| Skill | 功能 |
|---|---|
| `/patent-pipeline` | 从 invention 到 CN/US/EP 申请文件 |
| `/invention-structuring` | 发明点结构化 |
| `/claims-drafting` | 权利要求书 |
| `/specification-writing` | 说明书 |
| `/jurisdiction-format` | 不同法域格式 |
| `/grant-proposal` | 基金申请 |
| `/rebuttal` | 审稿 rebuttal |
| `/overleaf-sync` | Overleaf 双向同步 |

---

## 14. 核心 Artifact 布局

```text
orbit-research/
  MODE_ROUTING.md
  PROBLEM_SELECTION.md
  ASSUMPTION_LEDGER.md
  ABSTRACT_TASK_MECHANISM.md
  BASELINE_CEILING.md
  MECHANISM_IDEATION.md
  ANALOGY_TRANSFER.md
  ALGORITHM_TOURNAMENT.md
  CONTROL_DESIGN.md
  NULL_RESULT_CONTRACT.md
  COMPONENT_BUNDLE_LADDER.md
  ALGORITHMIC_FORMALIZATION.md
  PLAN_CODE_AUDIT.md
  DIAGNOSTIC_EXPERIMENT_PLAN.md
  DIAGNOSTIC_RUN_REPORT.md
  DIAGNOSTIC_RUN_AUDIT.md
  RESULT_INTERPRETATION.md
  CLAIM_CONSTRUCTION.md
  HUMAN_DECISION_NOTE.md
  RED_TEAM_REVIEW.md
  *_STATE.json

refine-logs/
  FINAL_PROPOSAL.md
  FINAL_PROPOSAL_SHORT.md
  METHOD_SPEC.md
  EXPERIMENT_PLAN.md
  EXPERIMENT_PLAN_EXEC.md
  EXPERIMENT_TRACKER.md
  EXPERIMENT_RESULTS.md

idea-stage/
  IDEA_REPORT.md
  IDEA_CANDIDATES.md

paper/
  main.tex
  main.pdf
  sections/
  references.bib
  .aris/assurance.txt
```

---

## 15. Verdict-Line Gates

下游 skill 读 verdict line，不只看文件是否存在。

| Artifact | 合法 verdict | 用途 |
|---|---|---|
| `PLAN_CODE_AUDIT.md` | `MATCHES_PLAN`, `PARTIAL_MISMATCH`, `CRITICAL_MISMATCH`, `ERROR` | 决定是否允许进入 GPU / scale-up |
| `DIAGNOSTIC_RUN_AUDIT.md` | `PASS`, `FIX_BEFORE_GPU`, `REDESIGN_EXPERIMENT` | 决定 diagnostic 是否通过 |
| `SCALEUP_DECISION.md` | `PROCEED`, `HOLD`, `REDESIGN`, `HUMAN_DECISION_REQUIRED` | 决定是否 scale-up |
| `HUMAN_DECISION_NOTE.md` | `PROCEED`, `NARROW`, `REDESIGN`, `RE-READ`, `CHANGE BENCHMARK`, `STOP`, `HUMAN_DECISION_REQUIRED` | 高风险转移的人类授权 |
| `result-to-claim` output | `yes`, `partial`, `no` | 决定 claim 是否成立 |

---

## 16. 使用建议

### 想从领域开始

```text
/idea-to-proposal "your broad area"
```

### 已经有 idea 草稿

```text
/idea-to-proposal "path/to/idea.md" — input-mode: idea
```

### 有很多上下文但 idea 还没定

```text
/idea-to-proposal "path/to/context.md" — input-mode: context
```

### 只想打磨方法

```text
/research-refine "problem + rough method"
```

### 已有 proposal，只想生成实验计划

```text
/experiment-plan "refine-logs/FINAL_PROPOSAL.md"
```

### 已有人类批准，准备写代码和跑 sanity

```text
/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
```

### 代码通过 plan-code audit，准备诊断实验到 claim

```text
/diagnostic-to-review "<diagnostic command OR manifest>"
```

### 已有 claim construction 和 red-team，准备写论文

```text
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
```

---

## 17. Review 观察与维护风险

1. **这是多入口系统，不是单入口脚本。**  
   `/research-pipeline` 是总 orchestrator，但实际常用路径会直接调用 `/idea-to-proposal`、`/experiment-bridge`、`/diagnostic-to-review`、`/paper-writing`。文档和维护都应围绕这些入口组织。

2. **镜像 skill 容易漂移。**  
   仓库里有顶层 skill、`skills-codex`、`skills-codex-claude-review`、`skills-codex-gemini-review`。凡是涉及 artifact contract、template、pipeline 行为的改动，应该先改顶层并运行 `tools/sync_codex_mirror.py`，再检查 reviewer overlay 是否需要同步调整。

3. **当前 proposal / experiment plan 已进入渐进式披露格式。**  
   下游应把 `FINAL_PROPOSAL.md` 和 `EXPERIMENT_PLAN.md` 当索引，而不是长文档。实现细节去 `METHOD_SPEC.md`，实验细节去 `EXPERIMENT_PLAN_EXEC.md`。

4. **高风险动作依赖 verdict-line，不依赖“文件存在”。**  
   例如 `PLAN_CODE_AUDIT.md` 存在但 verdict 是 `CRITICAL_MISMATCH` 时必须阻塞，不能只看文件名。

5. **paper-writing 是后置流程，不应该跳过 claim construction。**  
   缺 `CLAIM_CONSTRUCTION.md` 时 `/paper-writing` 应拒绝启动，这是系统里最重要的防 overclaim 机制之一。

6. **research-wiki 是可选增强，不是主线 gate。**  
   它能增强长期记忆和 claim/idea/experiment 图谱，但主 pipeline 不应因为 wiki helper 缺失而硬阻塞。

7. **实验 scale-up 前必须有人类确认。**  
   `experiment-queue` 明确属于 scale-up / Stage 20，不应作为绕过 diagnostic 的捷径。

---

## 18. 最短可执行心智模型

```text
想法阶段：
  /idea-to-proposal
  -> FINAL_PROPOSAL.md(index)
  -> FINAL_PROPOSAL_SHORT.md
  -> METHOD_SPEC.md
  -> EXPERIMENT_PLAN.md(index)
  -> EXPERIMENT_PLAN_EXEC.md
  -> STOP A

实现阶段：
  /experiment-bridge
  -> code
  -> PLAN_CODE_AUDIT.md
  -> sanity / diagnostic ready
  -> STOP B

证据阶段：
  /diagnostic-to-review
  -> DIAGNOSTIC_RUN_AUDIT.md
  -> RESULT_INTERPRETATION.md
  -> CLAIM_CONSTRUCTION.md
  -> RED_TEAM_REVIEW.md
  -> HUMAN_DECISION_NOTE.md
  -> STOP C

论文阶段：
  /paper-writing
  -> PAPER_PLAN.md
  -> figures/
  -> paper/
  -> audits
  -> STOP D
```

这就是当前 skills 组的实际工作流：**先扩大搜索空间，再收窄机制；先证明代码匹配计划，再花 GPU；先把结果约束成 claim，再写论文。**
