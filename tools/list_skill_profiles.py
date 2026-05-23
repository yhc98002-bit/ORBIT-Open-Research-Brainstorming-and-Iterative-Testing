#!/usr/bin/env python3
"""List ORBIT skill profiles from skills/skill_catalog.yaml.

The repository intentionally keeps the catalog as a small human-edited YAML file.
This helper parses only the subset used by that file so installs stay standard
library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value in {"[]", ""}:
        return []
    if value == "true":
        return True
    if value == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip('"') for part in inner.split(",")]
    return value


def parse_catalog(path: Path) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    profiles: dict[str, dict[str, list[str]]] = {}
    skills: list[dict[str, Any]] = []
    section: str | None = None
    current_profile: str | None = None
    current_profile_list: str | None = None
    current_skill: dict[str, Any] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if not raw_line.startswith(" "):
            key, _, value = raw_line.partition(":")
            if key not in {"profiles", "skills"}:
                metadata[key] = parse_scalar(value)
            section = key if key in {"profiles", "skills"} else None
            current_profile = None
            current_profile_list = None
            if current_skill is not None:
                skills.append(current_skill)
                current_skill = None
            continue

        if section == "profiles":
            if raw_line.startswith("  ") and not raw_line.startswith("    "):
                current_profile = raw_line.strip().rstrip(":")
                profiles[current_profile] = {"public": [], "internal": []}
                current_profile_list = None
            elif raw_line.startswith("    ") and not raw_line.startswith("      "):
                key, _, value = raw_line.strip().partition(":")
                current_profile_list = key
                parsed = parse_scalar(value)
                if isinstance(parsed, list) and current_profile:
                    profiles[current_profile][key] = parsed
            elif raw_line.startswith("      - ") and current_profile and current_profile_list:
                profiles[current_profile].setdefault(current_profile_list, []).append(
                    raw_line.strip()[2:].strip()
                )
            continue

        if section == "skills":
            stripped = raw_line.strip()
            if stripped.startswith("- name:"):
                if current_skill is not None:
                    skills.append(current_skill)
                current_skill = {"name": parse_scalar(stripped.split(":", 1)[1])}
            elif current_skill is not None and ":" in stripped:
                key, value = stripped.split(":", 1)
                current_skill[key] = parse_scalar(value)

    if current_skill is not None:
        skills.append(current_skill)

    return {**metadata, "profiles": profiles, "skills": skills}


def profile_names(catalog: dict[str, Any], profile: str) -> list[str]:
    profiles = catalog["profiles"]
    if profile not in profiles:
        known = ", ".join(sorted(profiles))
        raise SystemExit(f"unknown profile: {profile} (known: {known})")
    seen: set[str] = set()
    names: list[str] = []
    for bucket in ("public", "internal"):
        for name in profiles[profile].get(bucket, []):
            if name not in seen:
                seen.add(name)
                names.append(name)
    return names


def local_skill_names(repo: Path) -> list[str]:
    skills_dir = repo / "skills"
    names = []
    for path in skills_dir.glob("*/SKILL.md"):
        name = path.parent.name
        if name.startswith("skills-codex") or name == "shared-references":
            continue
        names.append(name)
    return sorted(names)


def check_catalog(catalog: dict[str, Any], repo: Path) -> int:
    catalog_names = sorted(skill["name"] for skill in catalog["skills"])
    disk_names = local_skill_names(repo)
    missing = sorted(set(disk_names) - set(catalog_names))
    extra = sorted(set(catalog_names) - set(disk_names))
    source_missing = sorted(
        skill["name"]
        for skill in catalog["skills"]
        if not (repo / skill.get("canonical_source", "")).is_file()
    )

    profile_refs: set[str] = set()
    for profile in catalog["profiles"].values():
        profile_refs.update(profile.get("public", []))
        profile_refs.update(profile.get("internal", []))
    bad_refs = sorted(profile_refs - set(catalog_names))
    profile_tags: dict[str, set[str]] = {
        skill["name"]: set(skill.get("profiles", [])) for skill in catalog["skills"]
    }
    missing_profile_tags = sorted(
        f"{profile}:{name}"
        for profile, buckets in catalog["profiles"].items()
        for name in buckets.get("public", []) + buckets.get("internal", [])
        if profile not in profile_tags.get(name, set())
    )

    if not missing and not extra and not bad_refs and not source_missing and not missing_profile_tags:
        print(f"Catalog OK: {len(catalog_names)} skills, {len(catalog['profiles'])} profiles")
        return 0

    if missing:
        print("Missing from catalog:", ", ".join(missing), file=sys.stderr)
    if extra:
        print("Catalog entries without local SKILL.md:", ", ".join(extra), file=sys.stderr)
    if source_missing:
        print("Canonical source paths missing:", ", ".join(source_missing), file=sys.stderr)
    if bad_refs:
        print("Profile references missing skills:", ", ".join(bad_refs), file=sys.stderr)
    if missing_profile_tags:
        print("Profile members missing reverse tags:", ", ".join(missing_profile_tags), file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", default="skills/skill_catalog.yaml", help="catalog path")
    parser.add_argument("--profile", help="profile name to print")
    parser.add_argument("--names-only", action="store_true", help="print only skill names")
    parser.add_argument("--all-skill-names", action="store_true", help="print every catalog skill")
    parser.add_argument("--public-only", action="store_true", help="print public catalog skills")
    parser.add_argument("--json", action="store_true", help="emit parsed catalog JSON")
    parser.add_argument("--check", action="store_true", help="verify catalog covers local skills")
    parser.add_argument("--repo", default=".", help="repo root for --check")
    args = parser.parse_args()

    catalog_path = Path(args.catalog)
    catalog = parse_catalog(catalog_path)

    if args.check:
        return check_catalog(catalog, Path(args.repo))
    if args.json:
        print(json.dumps(catalog, indent=2, sort_keys=True))
        return 0
    if args.all_skill_names:
        for name in sorted(skill["name"] for skill in catalog["skills"]):
            print(name)
        return 0
    if args.public_only:
        for skill in sorted(catalog["skills"], key=lambda item: item["name"]):
            if skill.get("public_entry") is True:
                print(skill["name"])
        return 0
    if args.profile:
        names = profile_names(catalog, args.profile)
        if args.names_only:
            for name in names:
                print(name)
        else:
            profile = catalog["profiles"][args.profile]
            print(f"{args.profile}")
            print("  public:")
            for name in profile.get("public", []):
                print(f"    - {name}")
            print("  internal:")
            for name in profile.get("internal", []):
                print(f"    - {name}")
        return 0

    print("Profiles:")
    for name in sorted(catalog["profiles"]):
        members = profile_names(catalog, name)
        print(f"  {name}: {len(members)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
