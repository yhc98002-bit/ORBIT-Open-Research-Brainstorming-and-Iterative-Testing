#!/usr/bin/env python3
"""Synchronize skills/skills-codex with the top-level skill set.

The Codex base package mirrors the top-level skill set, then applies a small
transport conversion so reviewer calls are usable from Codex-native sessions.
Reviewer-specific differences still belong in skills-codex-claude-review/ and
skills-codex-gemini-review/, not here.
"""

from __future__ import annotations

import argparse
import filecmp
import re
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
MIRROR_DIR = SKILLS_DIR / "skills-codex"
SHARED_REFS = "shared-references"
EXCLUDED_TOP_LEVEL = {
    SHARED_REFS,
    "skills-codex",
    "skills-codex-claude-review",
    "skills-codex-gemini-review",
}
IGNORED_NAMES = {"__pycache__", ".DS_Store"}

FENCED_BLOCK_RE = re.compile(r"```(?P<info>[^\n]*)\n(?P<body>[\s\S]*?)```")
MODEL_LINE_RE = re.compile(r"^\s*model:\s*.*$", re.MULTILINE)
CONFIG_LINE_RE = re.compile(r"^\s*config:\s*\{[^}]*model_reasoning_effort[^}]*\}\s*$", re.MULTILINE)
THREAD_ID_LINE_RE = re.compile(r"^(\s*)threadId:\s*(.*)$", re.MULTILINE)
PROMPT_PARAM_RE = re.compile(r"^(\s*)prompt:\s*\|", re.MULTILINE)

CODEX_PRECONDITION_MD = """# Codex-Native Reviewer Precondition + Loud-Stop Contract

> Single source of truth for Codex-native ORBIT skills that require an
> independent reviewer. In Codex CLI, the reviewer transport is a secondary
> Codex sub-agent through `spawn_agent`; follow-up reviewer turns use
> `send_input`.

## Entry-Time Precondition

Do not run a shell helper and do not reference Claude Code plugin-root
variables. Codex-native skills do not use a plugin-root probe.

At skill entry, confirm from the current session that the Codex-native
multi-agent tools are available:

- `spawn_agent` for fresh independent reviewer calls;
- `send_input` for reviewer follow-up turns when the skill explicitly requires
  same-thread continuity.

If those tools are not available and the skill marks reviewer participation as
load-bearing, write STATE with:

```jsonc
{
  "phase": "phase-0-precondition",
  "status": "awaiting_user_action",
  "next_action": "fix-codex-native-reviewer-then-reinvoke",
  "reviewer_unavailable_reason": {
    "ready": false,
    "transport": "codex-native-subagent",
    "detail": "<spawn_agent/send_input unavailable or failed>"
  }
}
```

Then stop before writing proposal, plan, diagnostic, claim, or paper artifacts.

## Reviewer Call Protocol

For a fresh independent review, call:

```text
spawn_agent:
  message: |
    [Full review prompt and required output schema]
```

For a continuation in the same reviewer conversation, call:

```text
send_input:
  target: <agent id returned by spawn_agent>
  message: |
    [Follow-up prompt]
```

Save the returned agent id when continuity is required. If a skill requires
fresh-context independence, start a new `spawn_agent` call instead of using
`send_input`.

## Mid-Run Failure

If a required reviewer call fails, preserve upstream artifacts already written,
write STATE with `status: "awaiting_user_action"` and a
`reviewer_call_failure` block, and stop. Do not produce a single-model
substitute artifact for a reviewer-required gate unless the user explicitly
passes `-- reviewer-required: false` or the skill documents an equivalent
degraded-mode override.
"""


def top_level_skill_dirs() -> list[Path]:
    return sorted(
        path
        for path in SKILLS_DIR.iterdir()
        if path.is_dir()
        and path.name not in EXCLUDED_TOP_LEVEL
        and (path / "SKILL.md").is_file()
    )


def _ignore(_dir: str, names: list[str]) -> set[str]:
    return {name for name in names if name in IGNORED_NAMES}


def sync_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True, ignore=_ignore)


def _dedupe_allowed_tools(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix = match.group(1)
        tools = [part.strip() for part in match.group(2).split(",")]
        out: list[str] = []
        seen: set[str] = set()
        for tool in tools:
            if not tool or tool in seen:
                continue
            seen.add(tool)
            out.append(tool)
        return prefix + ", ".join(out)

    return re.sub(r"^(allowed-tools:\s*)(.+)$", repl, text, flags=re.MULTILINE)


def _convert_reviewer_block(match: re.Match[str]) -> str:
    body = match.group("body")
    if "spawn_agent:" not in body and "send_input:" not in body:
        return match.group(0)

    body = CONFIG_LINE_RE.sub("", body)
    body = MODEL_LINE_RE.sub("", body)
    body = THREAD_ID_LINE_RE.sub(r"\1target: \2", body)
    body = PROMPT_PARAM_RE.sub(r"\1message: |", body)
    body = re.sub(r"^\s*# Codex MCP per-call config.*\n?", "", body, flags=re.MULTILINE)
    body = re.sub(r"^\s*# Sandbox is set globally.*\n?", "", body, flags=re.MULTILINE)
    body = re.sub(r"(spawn_agent:|send_input:)\n\s*\n", r"\1\n", body)
    body = re.sub(r"\n{3,}", "\n\n", body)
    return f"```{match.group('info')}\n{body}```"


def _convert_skill_text(text: str, rel: Path) -> str:
    if rel == Path("shared-references/codex-precondition.md"):
        return CODEX_PRECONDITION_MD

    replacements = [
        ("mcp__codex__codex-reply", "send_input"),
        ("mcp__codex__codex", "spawn_agent"),
        ("Codex MCP", "Codex-native sub-agent"),
        ("Codex MCP/auth/sandbox", "Codex-native reviewer transport"),
        ("MCP/auth/sandbox", "reviewer transport"),
        ("codex-reply", "send_input"),
        ("`threadId`", "`agent id`"),
        ("threadId", "agent id"),
        ("CLAUDE_PLUGIN_ROOT", "CODEX_NATIVE_SESSION"),
        ("codex-companion.mjs", "spawn_agent availability"),
        ("claude mcp add -s user codex -- codex mcp-server", "use Codex CLI with multi-agent tools enabled"),
        ("claude mcp add codex -s user -- codex mcp-server", "use Codex CLI with multi-agent tools enabled"),
        ("Claude Code access to `spawn_agent` and `send_input` tools", "Codex access to `spawn_agent` and `send_input` tools"),
        ("codex_unavailable_reason", "reviewer_unavailable_reason"),
        ("fix-codex-then-reinvoke", "fix-codex-native-reviewer-then-reinvoke"),
        ("fix-codex-then-resume", "fix-codex-native-reviewer-then-resume"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)

    text = text.replace(
        'node "${CODEX_NATIVE_SESSION}/scripts/spawn_agent availability" setup --json',
        '# Codex-native: no shell helper is run. Confirm spawn_agent/send_input are available in this session.',
    )
    text = text.replace(
        'node "${CODEX_NATIVE_SESSION}/scripts/spawn_agent availability" setup --json',
        '# Codex-native: no shell helper is run. Confirm spawn_agent/send_input are available in this session.',
    )
    text = text.replace(
        "Parse the JSON. If `.ready && .codex.available && .auth.loggedIn` are not all\ntrue (or the helper script itself is missing / errors), apply the LOUD STOP\nprotocol (§4 of that contract):",
        "If the Codex-native reviewer transport is unavailable, apply the LOUD STOP\nprotocol (§4 of that contract):",
    )
    text = text.replace(
        "If the user passed `— codex-required: false`, the precondition still runs\n(for STATE logging) but a failure becomes a single warning + a degraded-mode\nheader on every Phase 3/Phase 4 artifact (§6 of the contract).",
        "If the user passed `— codex-required: false`, reviewer transport failure becomes\na single warning + a degraded-mode header on every Phase 3/Phase 4 artifact.",
    )
    text = text.replace(
        "Codex CLI is installed but the MCP server isn't registered",
        "Codex-native multi-agent tools are unavailable",
    )
    text = text.replace(
        "Run `/codex:setup` to install/login Codex CLI.",
        "Use a Codex CLI session with multi-agent tools enabled.",
    )
    text = text.replace(
        "If Codex CLI is installed but the MCP server is not registered:",
        "If multi-agent tools are unavailable in the current session:",
    )
    text = text.replace(
        "If Codex CLI is installed but the MCP server isn't registered:",
        "If multi-agent tools are unavailable in the current session:",
    )

    text = FENCED_BLOCK_RE.sub(_convert_reviewer_block, text)
    text = _dedupe_allowed_tools(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def convert_codex_mirror_tree(root: Path) -> None:
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        original = path.read_text(encoding="utf-8")
        converted = _convert_skill_text(original, rel)
        if converted != original:
            path.write_text(converted, encoding="utf-8")


def sync() -> None:
    MIRROR_DIR.mkdir(parents=True, exist_ok=True)
    source_dirs = top_level_skill_dirs()
    source_names = {path.name for path in source_dirs}

    for child in MIRROR_DIR.iterdir():
        if child.is_dir() and child.name != SHARED_REFS and child.name not in source_names:
            shutil.rmtree(child)

    for src in source_dirs:
        sync_tree(src, MIRROR_DIR / src.name)

    sync_tree(SKILLS_DIR / SHARED_REFS, MIRROR_DIR / SHARED_REFS)
    convert_codex_mirror_tree(MIRROR_DIR)


def _relative_files(root: Path) -> set[Path]:
    files: set[Path] = set()
    for path in root.rglob("*"):
        if any(part in IGNORED_NAMES for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.add(path.relative_to(root))
    return files


def compare_tree(src: Path, dst: Path, base_rel: Path) -> list[str]:
    failures: list[str] = []
    if not dst.exists():
        return [f"missing mirror directory: {dst.relative_to(ROOT)}"]

    src_files = _relative_files(src)
    dst_files = _relative_files(dst)
    for rel in sorted(src_files - dst_files):
        failures.append(f"missing: {dst.relative_to(ROOT) / rel}")
    for rel in sorted(dst_files - src_files):
        failures.append(f"extra: {dst.relative_to(ROOT) / rel}")
    for rel in sorted(src_files & dst_files):
        if rel.suffix == ".md":
            src_text = (src / rel).read_text(encoding="utf-8")
            expected = _convert_skill_text(src_text, base_rel / rel)
            actual = (dst / rel).read_text(encoding="utf-8")
            if expected != actual:
                failures.append(f"differs: {dst.relative_to(ROOT) / rel}")
        elif not filecmp.cmp(src / rel, dst / rel, shallow=False):
            failures.append(f"differs: {dst.relative_to(ROOT) / rel}")
    return failures


def check() -> list[str]:
    failures: list[str] = []
    source_dirs = top_level_skill_dirs()
    source_names = {path.name for path in source_dirs}
    mirror_names = {
        path.name
        for path in MIRROR_DIR.iterdir()
        if path.is_dir() and path.name != SHARED_REFS and (path / "SKILL.md").is_file()
    }
    if mirror_names != source_names:
        failures.append(
            "skill set mismatch: "
            f"missing={sorted(source_names - mirror_names)} "
            f"extra={sorted(mirror_names - source_names)}"
    )

    for src in source_dirs:
        failures.extend(compare_tree(src, MIRROR_DIR / src.name, Path(src.name)))
    failures.extend(compare_tree(SKILLS_DIR / SHARED_REFS, MIRROR_DIR / SHARED_REFS, Path(SHARED_REFS)))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that skills-codex is already in sync without modifying files",
    )
    args = parser.parse_args(argv)

    if args.check:
        failures = check()
        if failures:
            print("skills-codex mirror is out of sync:", file=sys.stderr)
            for failure in failures:
                print(f"  - {failure}", file=sys.stderr)
            return 1
        return 0

    sync()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
