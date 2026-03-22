# Codex + Gemini Reviewer Guide

Run ARIS with:

- **Codex** as the main executor
- **Gemini** as the reviewer
- the local `gemini-review` MCP bridge as the transport layer
- the direct **Gemini API** as the default reviewer backend

This guide is **additive** to the upstream Codex-native path. It does not replace `skills/skills-codex/`.

## Architecture

- Base skill set: `skills/skills-codex/`
- Reviewer override layer: `skills/skills-codex-gemini-review/`
- Reviewer bridge: `mcp-servers/gemini-review/`

The install order matters:

1. install `skills/skills-codex/*`
2. install `skills/skills-codex-gemini-review/*`
3. register `gemini-review` MCP

## Install

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

Recommended credential file:

```bash
mkdir -p ~/.gemini
cat > ~/.gemini/.env <<'EOF'
GEMINI_API_KEY="your-key"
EOF
chmod 600 ~/.gemini/.env
```

The bridge auto-loads `~/.gemini/.env` if present.

## Why direct API is the default

- This path is designed to maximize reuse of the original ARIS review-heavy skills while minimizing skill changes.
- The `gemini-review` bridge preserves the same `review` / `review_reply` / `review_start` / `review_reply_start` / `review_status` contract used by the existing Claude-review overlay.
- Using the direct Gemini API removes the extra local CLI hop and keeps the reviewer path closer to the API-backed integrations already used elsewhere in ARIS.

## Access Notes

- Google AI Studio / Gemini API has a free tier in eligible countries; this does **not** require a Gemini Advanced / Google One AI Premium subscription.
- Free-tier model availability and rate limits change over time, so do not treat any single quota number as permanent.
- On the free tier, prompts and responses may be used to improve Google's products; do not position this path as suitable for sensitive data unless the user has reviewed the current official terms.
- Official references:
  - API key / AI Studio entry: <https://aistudio.google.com/apikey>
  - Gemini API pricing and free tier: <https://ai.google.dev/gemini-api/docs/pricing>

## Optional CLI fallback

The intended path is direct API. If you explicitly need Gemini CLI instead:

```bash
codex mcp remove gemini-review
codex mcp add gemini-review --env GEMINI_REVIEW_BACKEND=cli -- python3 ~/.codex/mcp-servers/gemini-review/server.py
```

That fallback is available, but it is not the primary path for this guide.

## Verify

1. Check MCP registration:

```bash
codex mcp list
```

2. Check that your Gemini API key file exists:

```bash
test -f ~/.gemini/.env && echo "Gemini env file found"
```

3. Start Codex in your project:

```bash
codex -C /path/to/your/project
```

## What gets overridden

The overlay only replaces review-heavy skills:

- `research-review`
- `novelty-check`
- `research-refine`
- `auto-review-loop`
- `paper-plan`
- `paper-figure`
- `paper-write`
- `auto-paper-improvement-loop`

Everything else still comes from the upstream `skills/skills-codex/` package.

## Async reviewer flow

For long paper or project reviews, use:

- `review_start`
- `review_reply_start`
- `review_status`

Why: even on the direct API path, long synchronous reviewer calls can still hit host-side MCP tool timeouts. The async `review*` flow keeps the original review-heavy skills usable without changing their behavior.

## Project config

No special project config file is required for this path.

- keep using your existing `CLAUDE.md`
- keep your current project layout
- only switch the installed Codex skill files and MCP registration

## Maintenance

Keep this path intentionally narrow:

- reuse `skills/skills-codex/*` unchanged
- only override review-heavy skills in `skills/skills-codex-gemini-review/*`
- keep `mcp-servers/gemini-review/server.py` focused on the `review*` compatibility contract
