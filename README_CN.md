<p align="center">
  <img src="assets/ORBIT.png" alt="ORBIT — Open Research Brainstorming and Iterative Testing" width="640">
</p>

# ORBIT — Open Research Brainstorming and Iterative Testing（中文入口）

**v1.3 — 科研方法论路由 harness（research-methodology routing harness）**。
ORBIT 不是僵硬的 0A–15 实验流水线，而是一个根据用户输入形态、模式（探索/创新/承诺）和风险等级
路由的科研方法论 harness。它在探索期跑得快，在高风险承诺前慢下来，鼓励发散式机制创造，
仅在不可逆的高风险转折点强制硬门禁。ORBIT 复用 ARIS 成熟执行链路，**不重写**它们。

> 完整契约见英文 [README.md](./README.md) 与 `skills/shared-references/` 下的合约文件——
> README.md 与 shared-references 是 canonical 合约源。本文件是**简明中文入口**，
> 不替代英文契约。

## v1.3 是什么

v1.0 是僵硬的诊断 harness：16 个强制阶段（0A–15）通过强制数据审计、baseline ceiling、
tiny run 来防止坏实验。它对常规验证有效，但 (a) 把方法创新挡在前置审计后面，
(b) 即使 tiny run 无法证伪核心 claim 也强制 tiny run，(c) 在数据还不存在时就要求数据审计。

v1.3 在承诺时保留诊断纪律，并增加：

- **模式与风险路由** — EXPLORATION / INNOVATION / COMMITMENT 三种模式 + 1–5 风险评分
- **假设台账（ASSUMPTION_LEDGER.md）** 作为一等公民
- **artifact 触发审计**（数据审计仅在数据存在后触发，不再前置强制）
- **创新循环**——发散机制创造、跨域类比、算法草稿锦标赛、失败转创新
- **最便宜的有效诊断（cheapest valid diagnostic）** 取代"总是 tiny run"
- **组件 / 最小机制保留 bundle 阶梯** 取代"总是单组件"
- **plan-code 一致性循环** 与 **reviewer red-team 循环**——明确的 audit → fix → re-audit
- **Codex 创新协作模式**（创新时不否决、只增补；承诺时切换回对抗模式）
- 显式复用 ARIS 成熟执行链路（`/auto-review-loop`、`/paper-writing`、
  `/auto-paper-improvement-loop`、`/paper-claim-audit`、`/citation-audit`、
  `/experiment-audit`、`/experiment-bridge`）

## 四脉络框架（Four Spines）

ORBIT 把 26 个阶段组织成四条脉络。这**不是严格线性**——orchestrator 按模式和风险路由；
许多阶段是循环；某些阶段在 EXPLORATION 模式下被跳过，仅在 COMMITMENT 前触发。

| 脉络 | 阶段 | 用途 |
|---|---|---|
| **Discovery（发现）** | 0, 1, 2, 2.5, 3 | 框定问题、选择目标。模式路由、seed framing、文献映射、问题重构、问题选择。 |
| **Grounding（地基）** | 4, 5, 6, 7 | **是 Innovation 的诊断支撑，不是创新本身**。假设台账、抽象任务/机制框定、artifact 触发审计（仅在数据/环境/benchmark 存在后）、baseline ceiling。 |
| **Innovation（创新）** | 8, 9, 10, 18.5 | 发散机制创造、类比/跨域迁移、算法草稿锦标赛、失败转创新。**Codex 在这里切换为协作模式**——见 `skills/shared-references/innovation-loops.md`。 |
| **Validation（验证）** | 11–25 | 假设-机制-基准-控制矩阵、null-result 契约、组件 bundle、形式化、plan-code 审计、最便宜诊断、诊断审计、结果解释、scale-up、claim 构造、tie/negative 策略、reviewer red-team、论文写作、人类决策。 |

Grounding（4–7）是让 Innovation 真正可诊断的校准层——它**不是**创造新方法的地方，
而是把假设、抽象任务框定、可用 artifact、baseline 余量钉住，让 Innovation 产出候选、
让 Validation 能判断候选是否有效。

## 模式与风险路由

orchestrator 的第一步是分类用户输入并写入 `MODE_ROUTING.md`。

**模式：**
- `EXPLORATION` — 宽泛领域，问题不明，无 committed artifact。跑得快、门禁低、各处允许候选、
  尚不写论文 claim。
- `INNOVATION` — 具体问题，无 committed 方法。创新循环触发（阶段 8/9/10）；Grounding（4–7）
  提供校准但不阻断创意。
- `COMMITMENT` — committed 方法、官方实验、scale-up、论文写作。Validation Spine 全部生效，
  全部硬门禁激活。

**风险评分（1–5）：** 本地/可逆（1–2）→ 非平凡 GPU 消耗（3）→ 官方运行/论文 claim（4）
→ 公开发布/投稿（5）。

不是每次都跑所有阶段。orchestrator 只跑满足你当前风险等级所需要的最少阶段集合。
完整路由规则见 `skills/shared-references/research-agent-pipeline.md`。

## 核心原则

1. **大胆想，谨慎跑** — 探索时移动得快，承诺前停下来。
2. **假设是一等公民** — 任何 "is/will/always" 类 claim 必须能追溯到 ASSUMPTION_LEDGER 的某行（G2）。
3. **最便宜的有效诊断** — 不是最小的 run，而是能证伪核心 claim 的最便宜 run。
4. **artifact 触发审计** — 数据/benchmark/simulator 不存在时不要做审计；存在了再审计（G4）。
5. **Codex 创新协作 + 承诺对抗** — 创造时 Codex 只增补不否决；承诺时切换为独立语义审计员。
6. **复用 ARIS 成熟链路** — `/auto-review-loop`、`/paper-writing`、`/experiment-bridge` 等
   不要重写，ORBIT 调用它们。
7. **claim → evidence → control → scope → limitation** — 论文 claim 永远证据绑定，
   部分证据降级 claim 措辞（G14、G17）。
8. **高风险转折保留人类判断** — scale-up、论文写作、公开发布前必须有
   `HUMAN_DECISION_NOTE.md`（G15、G19）。
9. **组件渐进验证** — 单组件优先；机制不可分时允许"最小机制保留 bundle"，但 artifact 必须
   写明为何不可分（G9）。
10. **失败也是输出** — tie/failure 不强写成功故事；事后重构必须明确标注为
    "exploratory finding, not pre-planned hypothesis"（G14、G17）。

## Quick Start

在 Claude Code 里：

**宽泛方向（EXPLORATION 模式）：**
```text
/research-pipeline "Discrete Diffusion VLA post-training"
```

ORBIT 走 Discovery 路由：seed framing → literature map → problem reframing → problem selection。
不承诺方法、不跑实验。

**已有 idea 想验证（INNOVATION 模式）：**
```text
/research-pipeline "problem | rough method idea"
```

ORBIT 走 Grounding（assumption ledger、abstract task、baseline ceiling）+ Innovation Spine
（mechanism invention、analogy transfer、algorithm sketch tournament）。

**已有结果想写论文（COMMITMENT 模式）：**
```text
/result-to-claim "main result on benchmark X with method Y"
/paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
```

参数分隔符是 em-dash `—`，不是单个 `-`。

## 流水线一眼看完

```text
Discovery   → 0  Mode & Risk Routing
              1  Seed Framing
              2  Question-driven Literature Map         (loop)
              2.5 Problem Reframing Loop
              3  Problem Selection

Grounding   → 4  Assumption Ledger
              5  Abstract Task / Mechanism Framing
              6  Artifact-triggered Audit               (artifact 存在后才触发)
              7  Baseline Ceiling

Innovation  → 8  Mechanism Invention                    (Codex 协作)
              9  Analogy / Cross-pollination             (Codex 协作)
              10 Algorithm Sketch Tournament            (Codex 协作 / 仲裁时对抗)
              18.5 Failure-to-Innovation                (失败时触发，Codex 协作)

Validation  → 11 Hypothesis-Mechanism-Benchmark-Control
              12 Null-result Contract
              13 Component / Mechanism Bundle Ladder
              14 Algorithmic Formalization
              15 Plan-Code Consistency Loop             (audit → fix → re-audit)
              16 Cheapest Valid Diagnostic
              17 Diagnostic Run Audit
              18 Result Interpretation Loop
              19 Re-read Literature Loop
              20 Scale-up Decision
              21 Result-to-Claim Construction
              22 Tie / Negative / Reframing Strategy
              23 Reviewer Red-team Loop                  (review → fix → re-review)
              24 Paper Writing / Improvement Loop        (调用 ARIS 链)
              25 Human Decision / Next Loop
```

完整 canonical 阶段映射、每阶段职责、必需 artifact、verdict ending：见
`skills/shared-references/research-agent-pipeline.md`。

## 关键硬门禁（精简版）

v1.3 共 19 条硬门禁（G0–G19），全部基于 verdict line 解析（不是文件存在性）。重点：

- **G6** — 方法承诺前必须有至少一个创新 artifact（MECHANISM_IDEATION / ANALOGY_TRANSFER /
  ALGORITHM_TOURNAMENT 三选一）
- **G8** — 诊断/确认实验前必须有 `NULL_RESULT_CONTRACT.md`
- **G11** — `PLAN_CODE_AUDIT.md` verdict = `CRITICAL_MISMATCH` 无条件阻止 scale-up
- **G12** — 诊断 run 在违反机制必要前置条件的 regime 下失败时，**不杀机制**——重新设计诊断
  到机制能 manifest 的 regime（取代 v1.0 "tiny-run failure → kill idea"）
- **G14** — `NULL_RESULT_CONTRACT` 触发的 tie/failure 不能在结果解释/claim 中写正向叙事
- **G15 + G19** — scale-up、论文写作、公开发布前必须有 `HUMAN_DECISION_NOTE.md`
- **G17** — 事后重构的发现必须显式标注 "exploratory finding, not pre-planned hypothesis"

完整 19 条 IF-THEN-UNLESS 规则：`skills/shared-references/research-agent-pipeline.md` §6。

v1.0 中的 "tiny run 总是必须" 与 "数据审计必须前置" 在 v1.3 中**故意去除**——分别由
G11/G12（regime 感知）和 G4（artifact 触发）取代。

## 标准 HITL 流程 — 4 个停顿点

ORBIT v1.3 不追求全自动，也不每步问。设计 **4 个 human-in-the-loop 停顿点**：段内
agent 连贯跑，段与段之间 `awaiting_human_continue`（见
[continuation-contract.md](skills/shared-references/continuation-contract.md)）让人审 +
决定是否继续。

```
1. /idea-to-proposal "<keyword OR draft-idea.md>"
   Discovery → Grounding → Innovation → final refinement → experiment plan
   ⏸ STOP A: 一起审 FINAL_PROPOSAL.md + EXPERIMENT_PLAN.md + claim map
              （合并的"值得花 GPU 吗"决策点）

2. /experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"
   实施 + plan-code 一致性循环 (Stage 15)
   ⏸ STOP B: 审 PLAN_CODE_AUDIT.md verdict — GPU 花钱前最后一关

3. /diagnostic-to-review "<diagnostic command OR manifest>"
   /run-experiment（自动 solo vs queue 路由）→ /analyze-results →
   /result-to-claim → /auto-review-loop
   遇到任何 verdict 瓶颈（FIX_BEFORE_GPU、claim_supported=no、不可救的 review 分、
   G14/G17 违反）就 awaiting_human_continue + 清晰 next_action 报告，从不 silent fail
   ⏸ STOP C: 一起审 CLAIM_CONSTRUCTION + RED_TEAM_REVIEW + HUMAN_DECISION_NOTE

4. /paper-writing "NARRATIVE_REPORT.md" — venue: ICLR, assurance: submission
   论文写作链（G16+G18 强制 — 必须有 STOP C 产生的 CLAIM_CONSTRUCTION.md）
   ⏸ STOP D（隐式）: 投稿/上 arXiv 前最后人工审
```

**段内行为：** AUTO_PROCEED = true 默认。任何 skill 加 `— human checkpoint: true` 让它
每个内部 phase 都停。加 `— no-checkpoint: true` 跳过 designed `awaiting_human_continue`
出口（dev / demo 才用）。

**断点恢复：** 流程里所有 skill 都遵守
[continuation contract](skills/shared-references/continuation-contract.md)。中途崩了直接
重调，STATE.json 自动决定 resume vs fresh（按 phase 进度 + artifact 在场 + 24h 失效）。

## 创新循环（Innovation Loops）

5 个命名循环 + Codex 协作模式规范，全部定义在 `skills/shared-references/innovation-loops.md`：

- **Loop A** — Mechanism Invention（5–10 候选机制；循环内**禁止收敛**）
- **Loop B** — Analogy / Cross-pollination（每个候选 ≥1 个跨域已解决问题）
- **Loop C** — Algorithm Sketch Tournament（round-robin 两两比较；保留落选方案）
- **Loop D** — Failure-to-Innovation（失败后复活落选方案 / 提出新机制）
- **Loop E** — Re-read Literature（按问题驱动的定向 query）

加上 **Collaborative Claude-Codex Innovation Mode** 规范：创新阶段 Codex 切换为
"不否决、只增补" 模式（扩展候选空间而非裁剪）；承诺阶段切回对抗模式。

## 安装

项目级安装（推荐，避免污染全局 skills）：

```bash
bash tools/install_aris.sh
```

手动复制：

```bash
mkdir -p .claude/skills
cp -r skills/* .claude/skills/
```

Codex reviewer 需要 Codex CLI / MCP：

```bash
npm install -g @openai/codex
codex setup
claude mcp add codex -s user -- codex mcp-server
```

ORBIT 默认 Codex reviewer 配置：

```toml
model = "gpt-5.5"
model_reasoning_effort = "xhigh"
sandbox_mode = "danger-full-access"
```

## 从 v1.0 迁移

现有用户项目的 v1.0 artifact 名继续可用——consumer 接受任一名字（v1.3 优先），
兼容窗口为一个主版本：

| v1.0 名 | v1.3 canonical |
|---|---|
| `COMPONENT_LADDER.md` | `COMPONENT_BUNDLE_LADDER.md` |
| `TINY_RUN_PLAN.md` | `DIAGNOSTIC_EXPERIMENT_PLAN.md` |
| `TINY_RUN_REPORT.md` | `DIAGNOSTIC_RUN_REPORT.md` |
| `TINY_RUN_AUDIT.md` | `DIAGNOSTIC_RUN_AUDIT.md` |

`TASK_ONTOLOGY.md`（v1.0）**无别名**——它的内容在 v1.3 拆分为四个 artifact，需手动迁移：

- 模式标记 → `MODE_ROUTING.md`
- 框定文本 → `SEED_FRAMING.md`
- 输入/假设块 → `ASSUMPTION_LEDGER.md`
- 任务/机制块 → `ABSTRACT_TASK_MECHANISM.md`

完整迁移附录：`skills/shared-references/research-agent-pipeline.md` 末尾。

v1.0 别名将在 v2.0 中移除。

## Codex 不可用 — 显式降级，非 silent skip

Codex（gpt-5.5 xhigh）是 ORBIT 的跨模型 reviewer。不可用时**分三档显式报告**，从不 silent skip：

| 档 | 行为 | 报告位置 |
|---|---|---|
| **Advisory（继续）** | Innovation 协作 additions / Stage 15 PLAN_CODE_AUDIT 在 diagnostic 阶段 / `/idea-to-proposal` Phase 4 final review | 相关 artifact 的 footer：`Codex collaborative additions: NOT_AVAILABLE` 或 `Phase X review: SKIPPED` |
| **Block 等人确认** | Stage 15 PLAN_CODE_AUDIT 在 scale-up 阶段（G11 ERROR 规则）；Stage 17 G12 regime check 不可答 | DIAGNOSTIC_RUN_AUDIT.verdict = ERROR + reason；orchestrator 升级 HUMAN_DECISION_REQUIRED |
| **Load-bearing 降级** | `/auto-review-loop` (Stage 23) → 单模型 review；`/paper-writing` Phase 5.5/5.8 audits → BLOCKED | RED_TEAM_REVIEW.md 头部 `⚠️ degraded: codex_mcp_unreachable, single-model review only`；PAPER_CLAIM_AUDIT / CITATION_AUDIT verdict = BLOCKED |

每个 skill 的"ARIS / Sub-skill Unavailability"段有完整降级契约。

## 重要文件（canonical 合约源）

- `skills/research-pipeline/SKILL.md` — v1.3 路由 orchestrator
- `skills/idea-to-proposal/SKILL.md` — STOP A：从领域/想法到 proposal + experiment plan（无 GPU）
- `skills/diagnostic-to-review/SKILL.md` — STOP C：串 run → analyze → claim → review
- `skills/shared-references/research-agent-pipeline.md` — canonical 0–25 阶段映射 + 19 硬门禁
- `skills/shared-references/research-harness-prompts.md` — 各阶段 canonical 提示词
- `skills/shared-references/innovation-loops.md` — Stages 8/9/10/18.5 流程 + Codex 协作模式
- `skills/shared-references/semantic-code-audit.md` — Stage 15 plan-code 审计 + Stage 17 诊断 run 审计
- `skills/shared-references/continuation-contract.md` — STATE.json schema、三态 enum、跨 skill resume
- `skills/shared-references/reviewer-routing.md` — Codex / Oracle reviewer 默认路由
- `AGENT_GUIDE.md` — 面向 agent 的路由索引
- `README.md` — 完整英文文档（canonical）

## 设计哲学

```text
大胆想，谨慎跑。
先诊断，再放大。
先 baseline，再 method（但 baseline 是参照，不是否决）。
先控制变量，再 claim。
先小实验，再 full run（但"小实验"必须是能证伪的最便宜诊断，不是无用的微 run）。
代码能跑不是成功，代码忠实实现 v1.3 契约才是成功。
创新循环产出候选；承诺门禁挑选实跑方案。
复用 ARIS 执行链路，不要重写。
高风险不可逆转折点保留人类判断。
```

## 从 BRIS（本项目旧名）迁移

本项目原名 **BRIS — Better Research in Sleep**，已 rebrand 为 **ORBIT — Open Research
Brainstorming and Iterative Testing**。已经在使用 `bris-research/` 目录的项目应该改名：

```bash
# 在你的项目根目录
git mv bris-research orbit-research
```

（不用 git 的话改成 `mv bris-research orbit-research`。）`install_aris.sh` 在一个主版本
内仍接受旧的 `BRIS_REPO` 环境变量和 `<!-- BRIS:BEGIN -->` / `<!-- BRIS:END -->`
CLAUDE.md 标记，所以已安装的项目无需修改也能继续用；下次运行 install 时这些标记会被
自动升级为 `<!-- ORBIT:BEGIN -->` / `<!-- ORBIT:END -->`。

→ 完整英文文档与 canonical 合约：[README.md](./README.md)
