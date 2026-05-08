# 实验计划 — 索引

> **Workflow 1.5 (`/experiment-bridge`) 模板。** 将本文件保存为
> `refine-logs/EXPERIMENT_PLAN.md`。可执行细节放入
> `refine-logs/EXPERIMENT_PLAN_EXEC.md` 和 run card 文件。

**用途**：本文件是**索引**。真正的执行计划拆分为可由 agent 直接行动的
run card 和协议文件。下游 skill 应先读本索引，再跟随交叉引用。

**项目**：[一句话说明项目 / 方法 / 目标会议 / 算力状态]

## 文件

| 阶段 | 文件 | 内容 | 何时读取 |
|---|---|---|---|
| 方法规格 | `FINAL_PROPOSAL.md` | proposal 索引和方法相关引用 | 总是读取 |
| 主执行计划 | `EXPERIMENT_PLAN_EXEC.md` | Claim map、紧凑实验块、运行顺序、关卡、预算、风险 | 总是读取 |
| 当前直接任务 | `[MILESTONE]_RUN_CARD.md` | 只写下一步动作：命令面、成功关卡、停止规则 | 当前任务存在时读取 |
| 失败路由 | `NULL_RESULT_CONTRACT.md` | NEGATIVE / TIE 结果解释和论文 pivot 规则 | 任一实验失败或打平时读取 |
| 可选协议 | `[PROTOCOL].md` | 数据集映射、baseline 协议、图表计划或其他局部细节 | 被引用时读取 |

## 阶段流程

```text
Phase 0 — Sanity / diagnostic gate
  -> [当前里程碑或关卡]
Phase 1 — Baselines and main method
  -> EXPERIMENT_PLAN_EXEC.md Run Order
Phase 2 — Decisive ablations
  -> 每个预注册决策关卡都必须 halt
Phase 3 — Appendix / qualitative / write-up support
  -> 主证据成立后再运行
```

## 关键约束

- [下游 agent 必须执行的 hard stop / 预算 / 数据约束]
- [不能静默放宽阈值；不能启动未注册实验]
- [可选实验不能拖延 must-run 证据]

## 下游 Skill

`/experiment-bridge "refine-logs/EXPERIMENT_PLAN.md"` 读取本索引，跟随交叉引用，
并按 `EXPERIMENT_PLAN_EXEC.md` 中的里程碑顺序实现实验。bridge skill 不能在
hard stop 之后自动启动下一阶段，除非得到明确的人类批准。
