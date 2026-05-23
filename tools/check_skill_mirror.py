#!/usr/bin/env python3
"""Check ORBIT skill mirrors for drift against canonical skills/.

Full mirrors must match canonical SKILL.md files exactly. Review overlays may
intentionally differ only when the catalog marks the overlay root and skill.
"""

from __future__ import annotations

import argparse
import filecmp
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


EXCLUDED_CANONICAL_DIRS = {
    "shared-references",
    "skills-codex",
    "skills-codex-claude-review",
    "skills-codex-gemini-review",
}

UNEXPECTED_STATUSES = {
    "different",
    "missing",
    "extra",
    "overlay_missing",
    "overlay_unlisted",
    "overlay_catalog_unknown",
}


@dataclass(frozen=True)
class MirrorPolicy:
    full_mirrors: list[str]
    overlays: dict[str, set[str]]


@dataclass(frozen=True)
class MirrorEntry:
    mirror: str
    kind: str
    skill: str
    status: str
    canonical: str | None
    mirrored: str | None
    message: str

    @property
    def unexpected(self) -> bool:
        return self.status in UNEXPECTED_STATUSES


def parse_catalog_policy(path: Path) -> MirrorPolicy:
    full_mirrors: list[str] = []
    overlays: dict[str, set[str]] = {}
    section: str | None = None
    overlay_path: str | None = None
    in_overlay_skills = False

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not raw_line.startswith(" "):
            section = stripped.rstrip(":")
            overlay_path = None
            in_overlay_skills = False
            continue

        if section != "mirror_policy":
            continue

        if raw_line.startswith("  full_mirrors:"):
            in_overlay_skills = False
            overlay_path = None
            continue
        if raw_line.startswith("  overlays:"):
            in_overlay_skills = False
            overlay_path = None
            continue
        if raw_line.startswith("    - ") and overlay_path is None and ":" not in stripped[2:]:
            full_mirrors.append(stripped[2:].strip())
            continue
        if raw_line.startswith("    - path:"):
            overlay_path = stripped.split(":", 1)[1].strip()
            overlays.setdefault(overlay_path, set())
            in_overlay_skills = False
            continue
        if raw_line.startswith("      skills:"):
            in_overlay_skills = True
            continue
        if raw_line.startswith("        - ") and overlay_path and in_overlay_skills:
            overlays[overlay_path].add(stripped[2:].strip())

    if not full_mirrors:
        full_mirrors = [".agents/skills", "skills/skills-codex"]
    return MirrorPolicy(full_mirrors=full_mirrors, overlays=overlays)


def canonical_skills(repo: Path) -> dict[str, Path]:
    skills_dir = repo / "skills"
    skills: dict[str, Path] = {}
    for path in skills_dir.glob("*/SKILL.md"):
        name = path.parent.name
        if name in EXCLUDED_CANONICAL_DIRS:
            continue
        skills[name] = path
    return dict(sorted(skills.items()))


def mirror_skills(repo: Path, mirror: str) -> dict[str, Path]:
    mirror_dir = repo / mirror
    if not mirror_dir.exists():
        return {}
    return dict(sorted((path.parent.name, path) for path in mirror_dir.glob("*/SKILL.md")))


def compare_full_mirror(repo: Path, mirror: str, canonical: dict[str, Path]) -> list[MirrorEntry]:
    entries: list[MirrorEntry] = []
    mirrored = mirror_skills(repo, mirror)
    mirror_dir = repo / mirror

    for name, canonical_path in canonical.items():
        mirrored_path = mirrored.get(name)
        if mirrored_path is None:
            entries.append(
                MirrorEntry(
                    mirror=mirror,
                    kind="full",
                    skill=name,
                    status="missing",
                    canonical=str(canonical_path),
                    mirrored=str(mirror_dir / name / "SKILL.md"),
                    message="canonical skill is missing from full mirror",
                )
            )
        elif filecmp.cmp(canonical_path, mirrored_path, shallow=False):
            entries.append(
                MirrorEntry(
                    mirror=mirror,
                    kind="full",
                    skill=name,
                    status="identical",
                    canonical=str(canonical_path),
                    mirrored=str(mirrored_path),
                    message="matches canonical",
                )
            )
        else:
            entries.append(
                MirrorEntry(
                    mirror=mirror,
                    kind="full",
                    skill=name,
                    status="different",
                    canonical=str(canonical_path),
                    mirrored=str(mirrored_path),
                    message="full mirror differs from canonical",
                )
            )

    for name, mirrored_path in mirrored.items():
        if name not in canonical:
            entries.append(
                MirrorEntry(
                    mirror=mirror,
                    kind="full",
                    skill=name,
                    status="extra",
                    canonical=None,
                    mirrored=str(mirrored_path),
                    message="mirror contains a noncanonical skill",
                )
            )
    return sorted(entries, key=lambda item: (item.mirror, item.status, item.skill))


def compare_overlay(
    repo: Path,
    mirror: str,
    allowed: set[str],
    canonical: dict[str, Path],
) -> list[MirrorEntry]:
    entries: list[MirrorEntry] = []
    mirrored = mirror_skills(repo, mirror)

    for name in sorted(allowed - set(mirrored)):
        entries.append(
            MirrorEntry(
                mirror=mirror,
                kind="overlay",
                skill=name,
                status="overlay_missing",
                canonical=str(canonical.get(name)) if name in canonical else None,
                mirrored=str(repo / mirror / name / "SKILL.md"),
                message="catalog marks overlay skill but mirror file is missing",
            )
        )

    for name, mirrored_path in mirrored.items():
        canonical_path = canonical.get(name)
        if canonical_path is None:
            entries.append(
                MirrorEntry(
                    mirror=mirror,
                    kind="overlay",
                    skill=name,
                    status="extra",
                    canonical=None,
                    mirrored=str(mirrored_path),
                    message="overlay contains a noncanonical skill",
                )
            )
            continue
        if name not in allowed:
            entries.append(
                MirrorEntry(
                    mirror=mirror,
                    kind="overlay",
                    skill=name,
                    status="overlay_unlisted",
                    canonical=str(canonical_path),
                    mirrored=str(mirrored_path),
                    message="overlay skill is not listed in catalog mirror_policy",
                )
            )
            continue
        if filecmp.cmp(canonical_path, mirrored_path, shallow=False):
            status = "identical"
            message = "overlay entry currently matches canonical"
        else:
            status = "overlay_intentionally_different"
            message = "catalog-marked review overlay differs from canonical"
        entries.append(
            MirrorEntry(
                mirror=mirror,
                kind="overlay",
                skill=name,
                status=status,
                canonical=str(canonical_path),
                mirrored=str(mirrored_path),
                message=message,
            )
        )
    return sorted(entries, key=lambda item: (item.mirror, item.status, item.skill))


def check_mirrors(repo: Path, catalog: Path) -> list[MirrorEntry]:
    policy = parse_catalog_policy(catalog)
    canonical = canonical_skills(repo)
    entries: list[MirrorEntry] = []
    for mirror in policy.full_mirrors:
        entries.extend(compare_full_mirror(repo, mirror, canonical))
    for mirror, allowed in sorted(policy.overlays.items()):
        entries.extend(compare_overlay(repo, mirror, allowed, canonical))
    return entries


def summarize(entries: list[MirrorEntry]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for entry in entries:
        counts = summary.setdefault(entry.mirror, {})
        counts[entry.status] = counts.get(entry.status, 0) + 1
    return {mirror: dict(sorted(counts.items())) for mirror, counts in sorted(summary.items())}


def render_pretty(entries: list[MirrorEntry]) -> str:
    summary = summarize(entries)
    unexpected = [entry for entry in entries if entry.unexpected]
    lines = [
        "Skill mirror drift report",
        f"Mirrors checked: {len(summary)}",
        f"Unexpected drift: {len(unexpected)}",
        "",
    ]
    for mirror, counts in summary.items():
        lines.append(f"{mirror}")
        for status, count in counts.items():
            lines.append(f"  {status}: {count}")
        details = [
            entry
            for entry in entries
            if entry.mirror == mirror and entry.status != "identical"
        ]
        if details:
            lines.append("  details:")
            for entry in details:
                marker = "!" if entry.unexpected else "-"
                lines.append(f"    {marker} {entry.skill}: {entry.status} ({entry.message})")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="repository root")
    parser.add_argument("--catalog", default=None, help="skill catalog path")
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    catalog = Path(args.catalog).resolve() if args.catalog else repo / "skills" / "skill_catalog.yaml"
    entries = check_mirrors(repo, catalog)
    unexpected = [entry for entry in entries if entry.unexpected]

    if args.json:
        payload: dict[str, Any] = {
            "repo": str(repo),
            "catalog": str(catalog),
            "summary": summarize(entries),
            "unexpected_drift": len(unexpected),
            "entries": [asdict(entry) | {"unexpected": entry.unexpected} for entry in entries],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(render_pretty(entries), end="")
    return 1 if unexpected else 0


if __name__ == "__main__":
    raise SystemExit(main())
