#!/usr/bin/env python3
"""Generate Claude CLI review overrides for upstream Codex-native skills."""

from __future__ import annotations

import ast
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "skills" / "skills-codex"
DEST_ROOT = REPO_ROOT / "skills" / "skills-codex-claude-review"
SRC_SHARED_ROOT = SRC_ROOT / "shared-references"
DEST_SHARED_ROOT = DEST_ROOT / "shared-references"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)
SPAWN_BLOCK_RE = re.compile(r"```(?:yaml|text)?\nspawn_agent:\n([\s\S]*?)```")
SEND_BLOCK_RE = re.compile(r"```(?:yaml|text)?\nsend_input:\n([\s\S]*?)```")

OVERRIDE_NOTE = (
    "> Override for Codex users who want **Claude Code CLI**, not a second Codex "
    "agent, to act as the reviewer/helper. Install this package **after** "
    "`skills/skills-codex/*`.\n\n"
    "Whenever the upstream skill asks for an external reviewer/helper, write the "
    "complete focused prompt to `$PROMPT_FILE` and run:\n\n"
    "```bash\n"
    "claude -p --dangerously-skip-permissions --output-format json --model opus "
    "--effort max < \"$PROMPT_FILE\" | tee \"$RAW_REVIEW_JSON\"\n"
    "```"
)

REVIEWER_LINE = (
    "- **REVIEWER_MODEL = `claude-cli`** — Claude reviewer invoked through direct "
    "`claude -p` CLI calls following `../shared-references/claude-cli-review.md`."
)

PREREQ_BLOCK = """## Prerequisites

- Install the base Codex-native skills first: copy `skills/skills-codex/*` into `~/.codex/skills/`.
- Then install this overlay package: copy `skills/skills-codex-claude-review/*` into `~/.codex/skills/` and allow it to overwrite the same skill names.
- Ensure the `claude` CLI is available:
  ```bash
  claude --version
  ```
- Reviews and helper critiques use direct `claude -p` calls; see `../shared-references/claude-cli-review.md`.
""".strip()


def extract_field(frontmatter: str, field: str) -> str:
    pattern = re.compile(rf"^{re.escape(field)}:\s*(.+)$", re.MULTILINE)
    match = pattern.search(frontmatter)
    if not match:
        return ""
    value = match.group(1).strip()
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        try:
            value = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            value = value[1:-1]
    return value


def normalize_allowed_tools(frontmatter: str) -> str:
    raw = extract_field(frontmatter, "allowed-tools")
    if raw:
        tools = [item.strip() for item in raw.split(",") if item.strip()]
    else:
        tools = ["Bash(*)", "Read", "Write", "Edit", "Grep", "Glob", "WebSearch", "WebFetch"]

    normalized = []
    seen = set()
    for tool in ["Bash(*)", *tools]:
        if tool in {"spawn_agent", "send_input"}:
            continue
        if tool not in seen:
            normalized.append(tool)
            seen.add(tool)
    return ", ".join(normalized)


def build_frontmatter(name: str, description: str, allowed_tools: str) -> str:
    safe_desc = description.replace('"', '\\"')
    return (
        "---\n"
        f'name: "{name}"\n'
        f'description: "{safe_desc}"\n'
        f"allowed-tools: {allowed_tools}\n"
        "---\n\n"
    )


def normalize_description(text: str) -> str:
    text = text or "Claude CLI review override for a Codex-native ARIS skill."
    replacements = {
        "via Codex-native sub-agent": "via Claude Code CLI",
        "via a secondary Codex agent": "via Claude Code CLI",
        "via GPT-5.5": "via Claude Code CLI",
        "via GPT-5.4 xhigh review": "via Claude Code CLI review",
        "from GPT": "from Claude Code CLI",
        "using a secondary Codex agent": "using Claude Code CLI",
        "using Claude Code via claude-review MCP": "using Claude Code CLI",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def strip_call_backend_fields(block: str, *, followup: bool) -> str:
    out = []
    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            out.append(line)
            continue
        if stripped.startswith(("model:", "reasoning_effort:", "sandbox:", "approval-policy:")):
            continue
        if followup and stripped.startswith(("target:", "id:", "threadId:", "thread_id:")):
            continue
        if stripped.startswith("message:"):
            out.append(line.replace("message:", "prompt:", 1))
            continue
        out.append(line)
    return "\n".join(out).strip()


def claude_cli_rewrite(original_call: str, *, followup: bool) -> str:
    cleaned = strip_call_backend_fields(original_call, followup=followup)
    kind = "follow-up" if followup else "fresh"
    continuity = (
        "\nFor follow-up rounds, include the previous raw Claude JSON/review artifact, "
        "implemented changes, any pushback, and the current files in the prompt. "
        "Claude CLI has no persistent `threadId`."
        if followup
        else ""
    )
    return "\n".join(
        [
            "```text",
            f"Write the complete {kind} Claude review/help prompt to `$PROMPT_FILE`.",
            "Preserve the role, files-to-read, objective, and required output schema from this original call shape.",
            continuity,
            "",
            cleaned or "[focused review/help prompt]",
            "```",
            "",
            "```bash",
            'PROMPT_FILE="${PROMPT_FILE:-.aris/review-prompts/claude-review-round-N.md}"',
            'RAW_REVIEW_JSON="${RAW_REVIEW_JSON:-.aris/review-outputs/claude-review-round-N.json}"',
            'mkdir -p "$(dirname "$PROMPT_FILE")" "$(dirname "$RAW_REVIEW_JSON")"',
            'claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < "$PROMPT_FILE" | tee "$RAW_REVIEW_JSON"',
            "```",
            "",
            "Save the raw Claude CLI JSON before summarizing it. Treat the response text inside the JSON as the reviewer/helper output.",
        ]
    )


def rewrite_spawn_block(match: re.Match[str]) -> str:
    return claude_cli_rewrite(match.group(1), followup=False)


def rewrite_send_block(match: re.Match[str]) -> str:
    return claude_cli_rewrite(match.group(1), followup=True)


def transform_body(text: str) -> str:
    replacements = {
        "CODEX_": "CLAUDE_",
        "Codex precondition": "Claude CLI precondition",
        "Codex effort level": "Claude CLI effort level",
        "Codex falls back": "the skill must record a Claude CLI availability/configuration issue",
        "Codex-native sub-agent/auth/sandbox": "Claude CLI reviewer",
        "Codex-native sub-agent": "Claude CLI reviewer",
        "Codex-native reviewer": "Claude CLI reviewer",
        "Codex-native": "Claude CLI",
        "Codex Precondition + Loud-Stop Contract": "Claude CLI Review Transport + Loud-Stop Contract",
        "Codex availability": "Claude CLI availability",
        "Codex unavailability": "Claude CLI reviewer unavailability",
        "Codex call": "Claude CLI review call",
        "Codex review": "Claude CLI review",
        "Codex reviewer": "Claude CLI reviewer",
        "secondary Codex agent": "Claude CLI reviewer",
        "second Codex agent": "Claude CLI reviewer",
        "GPT-5.5 xhigh": "Claude CLI max-effort",
        "GPT-5.4 xhigh": "Claude CLI max-effort",
        "gpt-5.5": "claude-cli",
        "gpt-5.4": "claude-cli",
        "`gpt-5.5`": "`claude-cli`",
        "`gpt-5.4`": "`claude-cli`",
        "reasoning_effort: xhigh": "Claude CLI `--effort max`",
        "model_reasoning_effort": "Claude CLI `--effort max`",
        "spawn_agent/send_input": "direct Claude CLI review calls",
        "`spawn_agent`/`send_input`": "direct Claude CLI review calls",
        "`spawn_agent` / `send_input`": "direct Claude CLI review calls",
        "`spawn_agent`": "`claude -p`",
        "`send_input`": "a new `claude -p` invocation",
        "spawn_agent invocation": "Claude CLI invocation",
        "send_input invocation": "Claude CLI follow-up invocation",
        "Confirm direct Claude CLI review calls are available in this session.": "Run `claude --version` to confirm Claude CLI is available.",
        "Codex-native: no shell helper is run. Confirm direct Claude CLI review calls are available in this session.": "Claude CLI: run `claude --version`, then use direct `claude -p` calls.",
        "Verify `.ready && .codex.available && .auth.loggedIn`.": "Verify `claude --version` exits successfully.",
        "`agent_id`": "`claude_review_json_path`",
        "`agent id`": "`claude_review_json_path`",
        '"agent_id"': '"claude_review_json_path"',
        '"agent id"': '"claude_review_json_path"',
        "`threadId`": "`claude_review_json_path`",
        "`thread_id`": "`claude_review_json_path`",
        "codex-precondition.md": "claude-cli-review.md",
        "`codex_precondition`": "`claude_cli_precondition`",
        '"codex_precondition"': '"claude_cli_precondition"',
        "`codex_required`": "`claude_required`",
        '"codex_required"': '"claude_required"',
        "`— codex-required: false`": "`— claude-required: false`",
        "codex-required": "claude-required",
        "`-- reviewer-required: false`": "`-- reviewer-required: false`",
        "fix-codex-native-reviewer-then-reinvoke": "fix-claude-cli-reviewer-then-reinvoke",
        "codex_call_failure": "claude_cli_call_failure",
        "codex_review_needed": "claude_review_needed",
        "orbit-research/codex-prompts/": ".aris/review-prompts/",
        "orbit-research/codex-imports/": ".aris/review-outputs/",
        "/import-codex-review": "rerun the blocked skill after fixing Claude CLI access",
        "tools/codex_review_handoff.py": "direct Claude CLI prompt/raw-JSON files",
        "`/codex:setup`": "`claude --version` / Claude CLI authentication",
        "use Codex CLI with multi-agent tools enabled": "make the `claude` CLI available and authenticated",
        "Codex required": "Claude CLI reviewer required",
        "Codex is load-bearing": "Claude CLI reviewer is load-bearing",
        "Codex contribution": "Claude CLI reviewer contribution",
        "Codex collaborative": "Claude CLI collaborative",
        "Codex switches": "Claude CLI reviewer switches",
        "Codex appends": "Claude CLI reviewer appends",
        "Codex returns": "Claude CLI reviewer returns",
        "Codex on sketch quality": "Claude CLI reviewer on sketch quality",
        "Codex flags": "Claude CLI reviewer flags",
        "Codex objected": "Claude CLI reviewer objected",
        "Codex in": "Claude CLI reviewer in",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"^-\s+\*{0,2}REVIEWER_MODEL.*$",
        REVIEWER_LINE,
        text,
        flags=re.MULTILINE,
    )
    text = re.sub(
        r"## Prerequisites\n\n(?:- .*\n)+",
        PREREQ_BLOCK + "\n\n",
        text,
        count=1,
    )
    text = SPAWN_BLOCK_RE.sub(rewrite_spawn_block, text)
    text = SEND_BLOCK_RE.sub(rewrite_send_block, text)
    text = re.sub(
        r"(?m)^.*import-claude-review.*$",
        "After fixing Claude CLI access, rerun the blocked skill with its documented resume flag.",
        text,
    )
    text = re.sub(
        r"(?m)^.*rerun the blocked skill after fixing Claude CLI access.*$",
        "After fixing Claude CLI access, rerun the blocked skill with its documented resume flag.",
        text,
    )
    text = text.replace(
        "```\nClaude CLI `--effort max`\n```",
        claude_cli_rewrite("[Full review/help briefing + specific questions]", followup=False),
    )
    return text


def render_skill_override(skill_name: str, content: str) -> str:
    match = FRONTMATTER_RE.match(content)
    if not match:
        raise ValueError(f"Missing frontmatter for {skill_name}")

    frontmatter = match.group(1)
    body = content[match.end() :].lstrip("\n")
    name = extract_field(frontmatter, "name") or skill_name
    description = normalize_description(extract_field(frontmatter, "description"))
    allowed_tools = normalize_allowed_tools(frontmatter)

    output = build_frontmatter(name, description, allowed_tools)
    output += OVERRIDE_NOTE + "\n\n"
    output += transform_body(body).rstrip() + "\n"
    return output


def skill_uses_subagent(skill_dir: Path) -> bool:
    for path in skill_dir.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        if "spawn_agent" in text or "send_input" in text:
            return True
    return False


def discover_target_skills(src_root: Path = SRC_ROOT) -> list[str]:
    skills = []
    for skill_dir in sorted(path for path in src_root.iterdir() if path.is_dir()):
        if (skill_dir / "SKILL.md").exists() and skill_uses_subagent(skill_dir):
            skills.append(skill_dir.name)
    return skills


def copy_and_transform_skill(skill_name: str) -> None:
    source_dir = SRC_ROOT / skill_name
    target_dir = DEST_ROOT / skill_name
    if target_dir.exists():
        shutil.rmtree(target_dir)
    shutil.copytree(source_dir, target_dir)

    for path in target_dir.rglob("*.md"):
        rel = path.relative_to(target_dir)
        text = path.read_text(encoding="utf-8")
        if rel == Path("SKILL.md"):
            path.write_text(render_skill_override(skill_name, text), encoding="utf-8")
        else:
            path.write_text(transform_body(text), encoding="utf-8")


def copy_and_transform_shared_references() -> None:
    DEST_SHARED_ROOT.mkdir(parents=True, exist_ok=True)
    for source in SRC_SHARED_ROOT.glob("*.md"):
        target = DEST_SHARED_ROOT / source.name
        target.write_text(transform_body(source.read_text(encoding="utf-8")), encoding="utf-8")

    cli_review = DEST_SHARED_ROOT / "claude-cli-review.md"
    if not cli_review.exists():
        cli_review.write_text(
            "# Claude CLI Review Transport\n\n"
            "Use direct `claude -p --dangerously-skip-permissions --output-format json "
            "--model opus --effort max` calls for independent reviews.\n",
            encoding="utf-8",
        )
    (DEST_SHARED_ROOT / "codex-precondition.md").write_text(
        "# Claude CLI Reviewer Precondition + Loud-Stop Contract\n\n"
        "This compatibility file intentionally replaces the upstream sub-agent "
        "precondition when `skills-codex-claude-review` is installed over "
        "`skills/skills-codex`.\n\n"
        "## Entry-Time Precondition\n\n"
        "Before any load-bearing review/helper call, verify the Claude CLI is available:\n\n"
        "```bash\n"
        "claude --version\n"
        "```\n\n"
        "If this fails, write the skill STATE as `awaiting_user_action` with "
        "`next_action: \"fix-claude-cli-reviewer-then-reinvoke\"` and stop before "
        "emitting downstream proposal, plan, diagnostic, claim, or paper artifacts.\n\n"
        "## Reviewer Call Protocol\n\n"
        "For every fresh review/helper call, write the complete focused prompt to "
        "`$PROMPT_FILE`, then run:\n\n"
        "```bash\n"
        "claude -p --dangerously-skip-permissions --output-format json --model opus --effort max < \"$PROMPT_FILE\" | tee \"$RAW_REVIEW_JSON\"\n"
        "```\n\n"
        "Save the raw JSON before summarizing it. Treat the response text inside the "
        "JSON as the reviewer/helper output.\n\n"
        "For follow-up rounds, start a new `claude -p` invocation and include the "
        "previous raw Claude JSON/review, implemented changes, any pushback, and the "
        "current artifact in the prompt. Claude CLI has no persistent `threadId`.\n\n"
        "## Mid-Run Failure\n\n"
        "If a required Claude CLI call fails, preserve upstream artifacts already "
        "written, write STATE with `status: \"awaiting_user_action\"` and a "
        "`reviewer_call_failure` block, and stop. Do not produce a single-model "
        "substitute artifact unless the skill documents and the user explicitly "
        "selects a degraded-mode override.\n",
        encoding="utf-8",
    )


def main() -> None:
    DEST_ROOT.mkdir(parents=True, exist_ok=True)
    target_skills = discover_target_skills()
    for skill_name in target_skills:
        copy_and_transform_skill(skill_name)
    copy_and_transform_shared_references()
    print(f"Generated {len(target_skills)} Claude CLI override skills.")


if __name__ == "__main__":
    main()
