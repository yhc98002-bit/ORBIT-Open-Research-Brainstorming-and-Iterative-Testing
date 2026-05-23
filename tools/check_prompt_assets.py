#!/usr/bin/env python3
"""Validate SKILL.md prompt asset references.

The checker is intentionally small and stdlib-only. It verifies local prompt assets
referenced from canonical SKILL.md files and validates frontmatter on every canonical
prompt asset.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable


EXCLUDED_SKILL_ROOTS = {
    "skills-codex",
    "skills-codex-claude-review",
    "skills-codex-gemini-review",
}

REQUIRED_FRONTMATTER_KEYS = {"id", "used_by", "purpose"}
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
BARE_PROMPT_RE = re.compile(r"(?<![A-Za-z0-9_./-])((?:\./)?prompts/[A-Za-z0-9_.@/-]+\.md)")


def canonical_skill_dirs(repo: Path) -> list[Path]:
    skills_dir = repo / "skills"
    dirs = []
    for skill_md in skills_dir.glob("*/SKILL.md"):
        name = skill_md.parent.name
        if name in EXCLUDED_SKILL_ROOTS or name == "shared-references":
            continue
        dirs.append(skill_md.parent)
    return sorted(dirs)


def canonical_prompt_assets(repo: Path) -> list[Path]:
    assets: list[Path] = []
    for skill_dir in canonical_skill_dirs(repo):
        prompt_dir = skill_dir / "prompts"
        if prompt_dir.exists():
            assets.extend(sorted(prompt_dir.glob("*.md")))
    shared_prompt_dir = repo / "skills" / "shared-references" / "prompt-library"
    if shared_prompt_dir.exists():
        assets.extend(sorted(shared_prompt_dir.glob("*.md")))
    return sorted(assets)


def iter_prompt_refs(skill_md: Path) -> Iterable[tuple[str, int]]:
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    for line_no, line in enumerate(text.splitlines(), start=1):
        linked_spans: list[tuple[int, int]] = []
        for match in MARKDOWN_LINK_RE.finditer(line):
            linked_spans.append(match.span(1))
            target = match.group(1).strip()
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            if "prompts/" in target and target.endswith(".md") and "codex-prompts/" not in target:
                yield target, line_no
        for match in BARE_PROMPT_RE.finditer(line):
            if any(start <= match.start(1) < end for start, end in linked_spans):
                continue
            yield match.group(1), line_no


def resolve_ref(skill_dir: Path, target: str) -> Path:
    target = target.split("#", 1)[0]
    return (skill_dir / target).resolve()


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            data: dict[str, str] = {}
            for raw in lines[1:index]:
                if ":" not in raw or raw.startswith(" "):
                    continue
                key, value = raw.split(":", 1)
                data[key.strip()] = value.strip()
            body = "\n".join(lines[index + 1 :]).strip()
            return data, body
    return {}, text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--verbose", action="store_true", help="print every validated reference")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    errors: list[str] = []
    refs_checked = 0

    for skill_dir in canonical_skill_dirs(repo):
        skill_md = skill_dir / "SKILL.md"
        for target, line_no in iter_prompt_refs(skill_md):
            refs_checked += 1
            resolved = resolve_ref(skill_dir, target)
            if not resolved.exists():
                errors.append(
                    f"{skill_md.relative_to(repo)}:{line_no}: missing prompt asset {target}"
                )
            elif args.verbose:
                print(f"ref ok: {skill_md.relative_to(repo)}:{line_no} -> {resolved.relative_to(repo)}")

    assets = canonical_prompt_assets(repo)
    for asset in assets:
        frontmatter, body = parse_frontmatter(asset)
        missing = sorted(REQUIRED_FRONTMATTER_KEYS - set(frontmatter))
        if missing:
            errors.append(f"{asset.relative_to(repo)}: missing frontmatter key(s): {', '.join(missing)}")
        for key in REQUIRED_FRONTMATTER_KEYS:
            if key in frontmatter and not frontmatter[key]:
                errors.append(f"{asset.relative_to(repo)}: empty frontmatter key: {key}")
        if not body:
            errors.append(f"{asset.relative_to(repo)}: prompt body is empty")

    if errors:
        print("Prompt asset check failed:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(f"Prompt asset check OK: {refs_checked} references, {len(assets)} assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
