# skills-codex-claude-review 说明

这是一个**薄覆盖层**，适用于想采用以下组合的用户：

- **Codex** 作为主执行者
- **Claude Code** 作为审稿人
- 直接调用 Claude Code CLI，而不是再启一个 Codex reviewer

它不是新造一套完整技能包，而是叠加在上游已有的 `skills/skills-codex/` 之上。

## 这个包包含什么

- 只包含需要切换 reviewer backend 的 review-heavy skill 覆盖文件
- 不重复打包模板和资源目录
- 不替代基础的 `skills/skills-codex/` 安装

当前覆盖的技能：

- `research-review`
- `novelty-check`
- `research-refine`
- `auto-review-loop`
- `paper-plan`
- `paper-figure`
- `paper-write`
- `auto-paper-improvement-loop`

## 安装方式

1. 先安装上游原生 Codex 技能包：

```bash
mkdir -p ~/.codex/skills
cp -a skills/skills-codex/* ~/.codex/skills/
```

2. 再安装这个 Claude-review 覆盖层：

```bash
cp -a skills/skills-codex-claude-review/* ~/.codex/skills/
```

3. 确认 Claude Code CLI 可用：

```bash
claude --version
```

覆盖层里的 skills 会按项目 `AGENTS.md` 的命令形态调用 Claude review：

```bash
claude -p --dangerously-skip-permissions --output-format json --model opus --effort max "your focused review prompt"
```

## 为什么需要这个包

上游 `skills/skills-codex/` 已经支持 Codex 原生执行，并通过 `spawn_agent` 使用第二个 Codex 做 reviewer。

这个覆盖层新增的是另一种分工：

- 执行者：Codex
- 审稿人：Claude Code CLI
- 传输层：直接 `claude -p` CLI 调用

对于长论文和长 review prompt，先把完整 prompt 写入临时 prompt 文件，
再传给同一个 CLI 命令。见 `shared-references/claude-cli-review.md`。

这样不再依赖本地 Codex MCP bridge 来调用 Claude review。
