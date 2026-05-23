# `skills-codex`

Codex-native full mirror of the base ARIS skill set.

## Scope

This package is generated from the top-level `skills/` tree by
`tools/sync_codex_mirror.py`. It mirrors every top-level skill directory with a
`SKILL.md`, plus `shared-references/`.

Do not maintain Codex-specific behavior directly in this directory. Reviewer
transport differences live in the overlay packages:

- `skills/skills-codex-gemini-review/`
- `skills/skills-codex-claude-review/`

## Install

> 💡 **Recommended: project-local symlink** (since v0.4.2). Project isolation keeps ARIS workflows separate from other community skill packs (Superpowers, etc.). See issue [#118](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/issues/118).

```bash
# 1. Clone ARIS once to a stable location
git clone https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep.git ~/aris_repo

# 2. Attach to a Codex project with a flat manual install:
cd ~/your-paper-project
mkdir -p .agents/skills
cp -a ~/aris_repo/skills/skills-codex/* .agents/skills/
# Optional reviewer overlay, installed after the base mirror:
# cp -a ~/aris_repo/skills/skills-codex-gemini-review/* .agents/skills/
# cp -a ~/aris_repo/skills/skills-codex-claude-review/* .agents/skills/

# Windows (PowerShell copy fallback):
Copy-Item -Recurse C:\path\to\aris_repo\skills\skills-codex\* C:\path\to\your-paper-project\.agents\skills\
```

<details>
<summary><b>Alternative: legacy global install (`~/.codex/skills/`)</b></summary>

```bash
cp -a ~/aris_repo/skills/skills-codex/* ~/.codex/skills/
```

Global install increases the risk of skill name collisions when other community skill packs are also installed globally. Use only if you understand the trade-off and don't mix ARIS with other packs.

</details>

<details>
<summary><b>Deprecated: nested project-local copy</b></summary>

Older docs used `.agents/skills/aris`. That nested layout hides skills from
flat skill discovery in current Codex-style project layouts. Prefer the flat
copy shown above: `cp -a ~/aris_repo/skills/skills-codex/* .agents/skills/`.

</details>

Optional companion dependency for the `deepxiv` skill:

```bash
pip install deepxiv-sdk
```

If you also use reviewer overlay packages, install this base package first, then apply the overlay on top.
