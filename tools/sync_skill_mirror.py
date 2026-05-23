#!/usr/bin/env python3
"""Synchronize canonical skill SKILL.md files into full mirrors.

Default mode is dry-run. This tool never syncs review overlay roots and never
deletes extra files or directories.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

from check_skill_mirror import canonical_skills, parse_catalog_policy


def copy_skill_dir_missing(src_dir: Path, dst_dir: Path, apply: bool) -> str:
    if apply:
        shutil.copytree(src_dir, dst_dir, symlinks=True)
    return f"copy missing directory {src_dir} -> {dst_dir}"


def copy_skill_md(src: Path, dst: Path, apply: bool) -> str:
    if apply:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return f"copy {src} -> {dst}"


def sync_mirror(repo: Path, mirror: str, selected: set[str] | None, apply: bool) -> list[str]:
    canonical = canonical_skills(repo)
    actions: list[str] = []
    mirror_dir = repo / mirror
    if apply:
        mirror_dir.mkdir(parents=True, exist_ok=True)

    for name, canonical_skill_md in canonical.items():
        if selected and name not in selected:
            continue
        target_skill_dir = mirror_dir / name
        target_skill_md = target_skill_dir / "SKILL.md"
        if not target_skill_dir.exists():
            actions.append(copy_skill_dir_missing(canonical_skill_md.parent, target_skill_dir, apply))
        elif not target_skill_md.exists() or not filecmp.cmp(canonical_skill_md, target_skill_md, shallow=False):
            actions.append(copy_skill_md(canonical_skill_md, target_skill_md, apply))

    if mirror_dir.exists():
        extras = sorted(
            path.name
            for path in mirror_dir.iterdir()
            if path.is_dir() and (path / "SKILL.md").is_file() and path.name not in canonical
        )
        for name in extras:
            actions.append(f"leave extra mirror skill untouched {mirror_dir / name}")
    return actions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--catalog", default=None, help="skill catalog path")
    parser.add_argument("--mirror", action="append", help="full mirror path to sync; repeatable")
    parser.add_argument("--skill", action="append", help="single skill to sync; repeatable")
    parser.add_argument("--apply", action="store_true", help="write changes; default is dry-run")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    catalog = Path(args.catalog).resolve() if args.catalog else repo / "skills" / "skill_catalog.yaml"
    policy = parse_catalog_policy(catalog)
    mirrors = args.mirror or policy.full_mirrors
    selected = set(args.skill) if args.skill else None

    unknown = sorted(set(mirrors) - set(policy.full_mirrors))
    if unknown:
        parser.error(
            "refusing to sync non-full mirror paths: "
            + ", ".join(unknown)
            + " (only catalog full_mirrors are allowed)"
        )

    total = 0
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"{mode} skill mirror sync")
    for mirror in mirrors:
        actions = sync_mirror(repo, mirror, selected, args.apply)
        total += len(actions)
        print(f"{mirror}: {len(actions)} action(s)")
        for action in actions:
            print(f"  - {action}")
    if total == 0:
        print("No sync actions needed.")
    elif not args.apply:
        print("Dry-run only. Re-run with --apply to copy canonical files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
