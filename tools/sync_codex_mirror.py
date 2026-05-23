#!/usr/bin/env python3
"""Synchronize skills/skills-codex with the top-level skill set.

The Codex base package is a full mirror. Reviewer-specific differences belong
in skills-codex-claude-review/ and skills-codex-gemini-review/, not here.
"""

from __future__ import annotations

import argparse
import filecmp
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


def _relative_files(root: Path) -> set[Path]:
    files: set[Path] = set()
    for path in root.rglob("*"):
        if any(part in IGNORED_NAMES for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.add(path.relative_to(root))
    return files


def compare_tree(src: Path, dst: Path) -> list[str]:
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
        if not filecmp.cmp(src / rel, dst / rel, shallow=False):
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
        failures.extend(compare_tree(src, MIRROR_DIR / src.name))
    failures.extend(compare_tree(SKILLS_DIR / SHARED_REFS, MIRROR_DIR / SHARED_REFS))
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
