# Codex + Gemini 审稿人指南

使用：

- **Codex** 作为主执行者
- **Gemini** 作为审稿人
- 本地 `gemini-review` MCP bridge 作为传输层
- **direct Gemini API** 作为默认 reviewer backend

这份指南是对上游 `skills/skills-codex/` 的**叠加方案**，不是替换。

## 架构

- 基础 skill 集：`skills/skills-codex/`
- 审稿覆盖层：`skills/skills-codex-gemini-review/`
- 审稿 bridge：`mcp-servers/gemini-review/`

安装顺序很重要：

1. 先安装 `skills/skills-codex/*`
2. 再安装 `skills/skills-codex-gemini-review/*`
3. 最后注册 `gemini-review` MCP

## 安装

```bash
git clone https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git
cd Auto-claude-code-research-in-sleep

mkdir -p ~/.codex/skills
cp -a skills/skills-codex/* ~/.codex/skills/
cp -a skills/skills-codex-gemini-review/* ~/.codex/skills/

mkdir -p ~/.codex/mcp-servers/gemini-review
cp mcp-servers/gemini-review/server.py ~/.codex/mcp-servers/gemini-review/server.py
cp mcp-servers/gemini-review/README.md ~/.codex/mcp-servers/gemini-review/README.md
codex mcp add gemini-review --env GEMINI_REVIEW_BACKEND=api -- python3 ~/.codex/mcp-servers/gemini-review/server.py
```

推荐凭证文件：

```bash
mkdir -p ~/.gemini
cat > ~/.gemini/.env <<'EOF'
GEMINI_API_KEY="your-key"
EOF
chmod 600 ~/.gemini/.env
```

如果存在，bridge 会自动加载 `~/.gemini/.env`。

## 为什么默认走 direct API

- 这条路径的目标是：**最大化复用原始 ARIS 的 review-heavy skills，同时最少改 skill**。
- `gemini-review` bridge 保留了与 Claude-review overlay 相同的 `review` / `review_reply` / `review_start` / `review_reply_start` / `review_status` 契约。
- 直接走 Gemini API 可以去掉本地 CLI 这一跳，让 reviewer 路径更接近 ARIS 里已有的 API 型集成方式。

## 接入边界说明

- Google AI Studio / Gemini API 在支持地区提供免费层；这**不要求**你先订阅 Gemini Advanced / Google One AI Premium。
- 免费层可用模型、速率限制和配额会变化，不应把某个固定额度写成长期承诺。
- 免费层下的 prompt / response 处理条款与付费层不同；如果涉及敏感数据，必须先核对官方当前条款。
- 官方入口与定价说明：
  - API key / AI Studio：<https://aistudio.google.com/apikey>
  - Gemini API 定价与免费层：<https://ai.google.dev/gemini-api/docs/pricing>

## 可选 CLI fallback

这份指南的预期路径是 direct API。  
如果你明确想切到 Gemini CLI，可改成：

```bash
codex mcp remove gemini-review
codex mcp add gemini-review --env GEMINI_REVIEW_BACKEND=cli -- python3 ~/.codex/mcp-servers/gemini-review/server.py
```

但这不是本指南的主路径。

## 验证

1. 检查 MCP 是否注册成功：

```bash
codex mcp list
```

2. 检查本地 Gemini 凭证文件是否存在：

```bash
test -f ~/.gemini/.env && echo "Gemini env file found"
```

3. 在你的项目里启动 Codex：

```bash
codex -C /path/to/your/project
```

## 会覆盖哪些 skill

这个 overlay 只替换 review-heavy skills：

- `research-review`
- `novelty-check`
- `research-refine`
- `auto-review-loop`
- `paper-plan`
- `paper-figure`
- `paper-write`
- `auto-paper-improvement-loop`

其它能力仍然来自上游 `skills/skills-codex/`。

## 异步 reviewer 流程

对于长论文 / 长项目审稿，使用：

- `review_start`
- `review_reply_start`
- `review_status`

原因：即便走 direct API，超长同步 reviewer 调用仍然可能撞上宿主侧的 MCP timeout。保留异步 `review*` 流程，才能在**不改原有 review-heavy skill 行为**的前提下继续复用它们。

## 项目配置

这条路径不需要额外的项目配置文件。

- 继续使用你现有的 `CLAUDE.md`
- 保持现有项目布局
- 只切换安装的 Codex skill 文件和 MCP 注册

## 维护原则

让这条路径保持足够窄：

- 基础能力继续复用 `skills/skills-codex/*`
- 只在 `skills/skills-codex-gemini-review/*` 里覆盖 review-heavy skills
- 让 `mcp-servers/gemini-review/server.py` 只聚焦 `review*` 兼容契约
