#!/usr/bin/env python3
"""Baseline inventory and guardrail report for the ORBIT/ARIS skills repo."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import posixpath
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence


MIRROR_ROOTS = (
    ".agents/skills",
    "skills/skills-codex",
    "skills/skills-codex-gemini-review",
    "skills/skills-codex-claude-review",
)

SKILLS_MIRROR_DIR_NAMES = frozenset(
    root.split("/", 1)[1] for root in MIRROR_ROOTS if root.startswith("skills/")
)

SKIP_DIRS = frozenset((".git", "__pycache__"))

MD_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_./$*~-])"
    r"((?:[A-Za-z0-9_.$~{}()*-]+/)*[A-Za-z0-9_.$~{}()*-]+\.md)"
    r"(?![A-Za-z0-9_./$*~-])",
    re.IGNORECASE,
)

RUNTIME_PREFIXES = (
    "orbit-research/",
    "refine-logs/",
    "figures/",
    "results/",
    "runs/",
    "outputs/",
    "logs/",
    "reports/",
    "paper-output/",
    "poster-output/",
    "slides-output/",
)

DOC_PREFIXES = (
    "docs/",
    "templates/",
    "skills/shared-references/",
)

DOC_BASENAMES = frozenset(
    (
        "readme.md",
        "readme_cn.md",
        "contributing.md",
        "contributing_cn.md",
        "agent_guide.md",
        "claude.md",
        "agents.md",
        "skill.md",
    )
)

KNOWN_PUBLIC_ENTRY_NAMES = frozenset(
    (
        "alphaxiv",
        "arxiv",
        "comm-lit-review",
        "deepxiv",
        "diagnostic-to-review",
        "dse-loop",
        "exa-search",
        "experiment-bridge",
        "formula-derivation",
        "grant-proposal",
        "idea-discovery",
        "idea-discovery-robot",
        "idea-to-proposal",
        "mermaid-diagram",
        "overleaf-sync",
        "paper-illustration",
        "paper-illustration-image2",
        "paper-poster",
        "paper-slides",
        "paper-writing",
        "patent-pipeline",
        "pixel-art",
        "proof-checker",
        "proof-writer",
        "qzcli",
        "rebuttal",
        "research-pipeline",
        "research-refine",
        "research-refine-pipeline",
        "research-wiki",
        "run-experiment",
        "semantic-scholar",
        "serverless-modal",
        "system-profile",
        "training-check",
        "vast-gpu",
        "writing-systems-papers",
    )
)

KNOWN_INTERNAL_SUBSKILL_NAMES = frozenset(
    (
        "ablation-planner",
        "analyze-results",
        "auto-paper-improvement-loop",
        "auto-review-loop",
        "auto-review-loop-llm",
        "auto-review-loop-minimax",
        "citation-audit",
        "claims-drafting",
        "embodiment-description",
        "experiment-audit",
        "experiment-plan",
        "experiment-queue",
        "feishu-notify",
        "figure-description",
        "figure-spec",
        "idea-creator",
        "invention-structuring",
        "jurisdiction-format",
        "monitor-experiment",
        "novelty-check",
        "paper-claim-audit",
        "paper-compile",
        "paper-figure",
        "paper-plan",
        "paper-write",
        "patent-novelty-check",
        "patent-review",
        "prior-art-search",
        "proposal-revise",
        "research-doc-hygiene",
        "research-lit",
        "research-review",
        "result-to-claim",
        "specification-writing",
    )
)

INTERNAL_DESCRIPTION_PHRASES = (
    "internal utility",
    "used by other skills",
    "normally called by",
    "called by",
    "core skill of",
    "conditional-required",
    "child audit",
)

PUBLIC_DESCRIPTION_PHRASES = (
    "use when user says",
    "trigger with",
    "full ",
    "workflow",
    "pipeline",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit ORBIT/ARIS skill inventory, mirrors, and markdown artifacts."
    )
    parser.add_argument("--repo", default=".", help="Repository root to scan.")
    parser.add_argument(
        "--out",
        default="docs/refactor",
        help="Output directory for BASELINE_AUDIT.md and baseline_audit.json.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def relpath(path: Path, repo: Path) -> str:
    return path.relative_to(repo).as_posix()


def iter_named_files(repo: Path, filename: str) -> Iterable[Path]:
    for path in repo.rglob(filename):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(repo).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        yield path


def find_all_skill_files(repo: Path) -> List[Path]:
    return sorted(iter_named_files(repo, "SKILL.md"), key=lambda path: relpath(path, repo))


def find_canonical_skill_files(repo: Path) -> List[Path]:
    skills_root = repo / "skills"
    if not skills_root.is_dir():
        return []

    skill_files: List[Path] = []
    for child in sorted(skills_root.iterdir(), key=lambda path: path.name):
        if not child.is_dir() or child.name in SKILLS_MIRROR_DIR_NAMES:
            continue
        skill_file = child / "SKILL.md"
        if skill_file.is_file():
            skill_files.append(skill_file)
    return skill_files


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stats(path: Path, repo: Path) -> Dict[str, Any]:
    text = read_text(path)
    return {
        "path": relpath(path, repo),
        "skill": path.parent.name,
        "lines": len(text.splitlines()),
        "words": len(re.findall(r"\S+", text)),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def unquote_yaml_scalar(value: str) -> str:
    value = value.strip()
    if not value:
        return value
    if value[0] in ("'", '"') and value[-1:] == value[0]:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            parsed = value[1:-1]
        return str(parsed)
    return value


def parse_frontmatter(text: str) -> Dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}

    frontmatter: Dict[str, str] = {}
    for line in lines[1:end_index]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in line:
            continue
        if line[:1].isspace():
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = unquote_yaml_scalar(value)
    return frontmatter


def build_canonical_skill_map(canonical_skill_files: Sequence[Path]) -> Dict[str, Path]:
    return {path.parent.name: path for path in canonical_skill_files}


def mirror_skill_map(repo: Path, mirror_root: str) -> Dict[str, Path]:
    root = repo / mirror_root
    if not root.is_dir():
        return {}
    paths = sorted(root.glob("*/SKILL.md"), key=lambda path: path.parent.name)
    return {path.parent.name: path for path in paths if path.is_file()}


def mirror_drift(
    repo: Path, canonical_map: Mapping[str, Path], mirror_root: str
) -> Dict[str, Any]:
    mirror_map = mirror_skill_map(repo, mirror_root)
    canonical_names = set(canonical_map)
    mirror_names = set(mirror_map)
    common_names = sorted(canonical_names & mirror_names)

    identical: List[str] = []
    drifted: List[Dict[str, str]] = []
    for name in common_names:
        canonical_sha = sha256_file(canonical_map[name])
        mirror_sha = sha256_file(mirror_map[name])
        if canonical_sha == mirror_sha:
            identical.append(name)
        else:
            drifted.append(
                {
                    "skill": name,
                    "canonical_path": relpath(canonical_map[name], repo),
                    "mirror_path": relpath(mirror_map[name], repo),
                    "canonical_sha256": canonical_sha,
                    "mirror_sha256": mirror_sha,
                }
            )

    return {
        "mirror_root": mirror_root,
        "exists": (repo / mirror_root).is_dir(),
        "canonical_count": len(canonical_map),
        "mirror_count": len(mirror_map),
        "common_count": len(common_names),
        "identical_count": len(identical),
        "drifted_count": len(drifted),
        "missing_count": len(canonical_names - mirror_names),
        "extra_count": len(mirror_names - canonical_names),
        "identical": identical,
        "drifted": drifted,
        "missing": sorted(canonical_names - mirror_names),
        "extra": sorted(mirror_names - canonical_names),
    }


def clean_md_ref(raw: str) -> str:
    return raw.strip().strip("`'\"[]()<>.,:;")


def normalize_md_ref(raw: str, skill_rel_path: str) -> str:
    raw = clean_md_ref(raw).replace("\\", "/")
    raw = re.sub(r"/+", "/", raw)
    if not raw:
        return raw
    if raw.startswith("/"):
        return raw.lstrip("/")
    if raw.startswith("../") or raw.startswith("./"):
        base = PurePosixPath(skill_rel_path).parent
        normalized = posixpath.normpath(str(base / raw))
        return normalized.lstrip("./")
    return raw.lstrip("./")


def uppercase_artifact_name(path: str) -> bool:
    basename = PurePosixPath(path).name.lower()
    if basename in DOC_BASENAMES:
        return False
    stem = PurePosixPath(path).name[:-3]
    letters = [char for char in stem if char.isalpha()]
    if not letters:
        return False
    return all(char.upper() == char for char in letters) and (
        "_" in stem or "-" in stem or stem.isupper()
    )


def classify_md_artifact(path: str) -> str:
    lower = path.lower()
    basename = PurePosixPath(lower).name
    parts = set(PurePosixPath(lower).parts)

    if lower.startswith(DOC_PREFIXES) or "shared-references" in parts:
        return "docs_shared_references_templates"
    if "/templates/" in lower or lower.startswith("skills/") and "/templates/" in lower:
        return "docs_shared_references_templates"
    if basename in DOC_BASENAMES:
        return "docs_shared_references_templates"
    if basename == "skill.md" and "skills" in parts:
        return "docs_shared_references_templates"
    if lower.startswith(RUNTIME_PREFIXES):
        return "likely_generated_runtime"
    if uppercase_artifact_name(path):
        return "likely_generated_runtime"
    return "other"


def extract_md_artifacts(
    repo: Path, canonical_skill_files: Sequence[Path]
) -> Dict[str, Any]:
    artifacts: MutableMapping[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "path": "",
            "category": "",
            "mention_count": 0,
            "skills": set(),
            "raw_mentions": set(),
            "exists": False,
        }
    )

    for skill_file in canonical_skill_files:
        skill_name = skill_file.parent.name
        skill_rel = relpath(skill_file, repo)
        text = read_text(skill_file)
        for match in MD_REF_RE.finditer(text):
            raw = clean_md_ref(match.group(1))
            normalized = normalize_md_ref(raw, skill_rel)
            if not normalized:
                continue
            artifact = artifacts[normalized]
            artifact["path"] = normalized
            artifact["category"] = classify_md_artifact(normalized)
            artifact["mention_count"] += 1
            artifact["skills"].add(skill_name)
            artifact["raw_mentions"].add(raw)

    entries: List[Dict[str, Any]] = []
    for artifact in artifacts.values():
        path = artifact["path"]
        repo_path = repo / path
        entries.append(
            {
                "path": path,
                "category": artifact["category"],
                "mention_count": artifact["mention_count"],
                "skills": sorted(artifact["skills"]),
                "skill_count": len(artifact["skills"]),
                "raw_mentions": sorted(artifact["raw_mentions"]),
                "exists": repo_path.exists(),
            }
        )

    entries.sort(key=lambda item: (item["category"], item["path"]))
    summary = {
        "distinct_paths": len(entries),
        "likely_generated_runtime": sum(
            1 for item in entries if item["category"] == "likely_generated_runtime"
        ),
        "docs_shared_references_templates": sum(
            1 for item in entries if item["category"] == "docs_shared_references_templates"
        ),
        "other": sum(1 for item in entries if item["category"] == "other"),
    }

    return {
        "summary": summary,
        "entries": entries,
        "by_category": {
            category: [item for item in entries if item["category"] == category]
            for category in (
                "likely_generated_runtime",
                "docs_shared_references_templates",
                "other",
            )
        },
    }


def classify_entry_candidate(name: str, description: str) -> Dict[str, Any]:
    lowered = description.lower()
    public_score = 0
    internal_score = 0
    signals: List[str] = []

    if name in KNOWN_PUBLIC_ENTRY_NAMES:
        public_score += 3
        signals.append("known public-entry name")
    if name in KNOWN_INTERNAL_SUBSKILL_NAMES:
        internal_score += 3
        signals.append("known internal/subskill name")

    for phrase in PUBLIC_DESCRIPTION_PHRASES:
        if phrase in lowered:
            public_score += 1
            signals.append("description contains %r" % phrase)

    for phrase in INTERNAL_DESCRIPTION_PHRASES:
        if phrase in lowered:
            internal_score += 2
            signals.append("description contains %r" % phrase)

    if not description:
        signals.append("missing frontmatter description")

    if internal_score > public_score:
        category = "internal_subskill_candidate"
    elif public_score > internal_score:
        category = "public_entry_candidate"
    else:
        category = "ambiguous_candidate"

    return {
        "skill": name,
        "category": category,
        "public_score": public_score,
        "internal_score": internal_score,
        "signals": sorted(set(signals)),
    }


def entry_candidates(
    repo: Path, canonical_skill_files: Sequence[Path]
) -> Dict[str, List[Dict[str, Any]]]:
    buckets: Dict[str, List[Dict[str, Any]]] = {
        "public_entry_candidate": [],
        "internal_subskill_candidate": [],
        "ambiguous_candidate": [],
    }
    for skill_file in canonical_skill_files:
        text = read_text(skill_file)
        frontmatter = parse_frontmatter(text)
        name = frontmatter.get("name") or skill_file.parent.name
        description = frontmatter.get("description", "")
        item = classify_entry_candidate(name, description)
        item["path"] = relpath(skill_file, repo)
        buckets[item["category"]].append(item)

    for items in buckets.values():
        items.sort(key=lambda item: item["skill"])
    return buckets


def build_report(repo: Path) -> Dict[str, Any]:
    all_skill_files = find_all_skill_files(repo)
    canonical_skill_files = find_canonical_skill_files(repo)
    canonical_map = build_canonical_skill_map(canonical_skill_files)
    canonical_stats = [file_stats(path, repo) for path in canonical_skill_files]
    canonical_stats.sort(key=lambda item: item["path"])
    longest = sorted(
        canonical_stats,
        key=lambda item: (-item["lines"], -item["bytes"], item["path"]),
    )[:20]

    return {
        "schema_version": 1,
        "counts": {
            "canonical_skill_md": len(canonical_skill_files),
            "all_skill_md": len(all_skill_files),
            "mirror_roots_checked": len(MIRROR_ROOTS),
        },
        "canonical_skills": canonical_stats,
        "all_skill_md_paths": [relpath(path, repo) for path in all_skill_files],
        "mirror_drift": [
            mirror_drift(repo, canonical_map, mirror_root)
            for mirror_root in MIRROR_ROOTS
        ],
        "longest_canonical_skill_md": longest,
        "md_artifacts": extract_md_artifacts(repo, canonical_skill_files),
        "entry_candidates": entry_candidates(repo, canonical_skill_files),
    }


def ascii_safe(value: Any) -> str:
    text = str(value)
    return text.encode("ascii", "backslashreplace").decode("ascii")


def markdown_escape(value: Any) -> str:
    text = ascii_safe(value).replace("\n", " ")
    return text.replace("|", "\\|")


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> str:
    rendered = []
    rendered.append("| " + " | ".join(markdown_escape(header) for header in headers) + " |")
    rendered.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        rendered.append("| " + " | ".join(markdown_escape(cell) for cell in row) + " |")
    return "\n".join(rendered)


def join_names(names: Sequence[str], limit: Optional[int] = None) -> str:
    values = list(names)
    if limit is not None and len(values) > limit:
        shown = values[:limit]
        return ", ".join(shown) + ", ... (%d total)" % len(values)
    return ", ".join(values) if values else "none"


def render_artifact_table(entries: Sequence[Mapping[str, Any]]) -> str:
    rows = []
    for item in entries:
        rows.append(
            (
                item["path"],
                item["mention_count"],
                item["skill_count"],
                "yes" if item["exists"] else "no",
                join_names(item["skills"], limit=6),
            )
        )
    if not rows:
        return "_None._"
    return markdown_table(
        ("Path", "Mentions", "Skills", "Exists now", "Mentioned by"), rows
    )


def render_candidate_table(entries: Sequence[Mapping[str, Any]]) -> str:
    rows = []
    for item in entries:
        rows.append(
            (
                item["skill"],
                item["path"],
                item["public_score"],
                item["internal_score"],
                join_names(item["signals"], limit=4),
            )
        )
    if not rows:
        return "_None._"
    return markdown_table(
        ("Skill", "Path", "Public score", "Internal score", "Signals"), rows
    )


def render_markdown(report: Mapping[str, Any]) -> str:
    lines: List[str] = []
    counts = report["counts"]
    artifacts = report["md_artifacts"]
    candidates = report["entry_candidates"]

    lines.append("# ORBIT/ARIS Baseline Audit")
    lines.append("")
    lines.append("Generated by `python tools/orbit_repo_audit.py --repo . --out docs/refactor`.")
    lines.append("This report is intended as a pre-refactor guardrail inventory.")
    lines.append("")

    lines.append("## Counts")
    lines.append("")
    lines.append(
        markdown_table(
            ("Metric", "Value"),
            (
                ("Canonical `skills/*/SKILL.md` files", counts["canonical_skill_md"]),
                ("All `SKILL.md` files", counts["all_skill_md"]),
                ("Mirror roots checked", counts["mirror_roots_checked"]),
            ),
        )
    )
    lines.append("")

    lines.append("## Mirror Drift")
    lines.append("")
    mirror_rows = []
    for item in report["mirror_drift"]:
        mirror_rows.append(
            (
                item["mirror_root"],
                "yes" if item["exists"] else "no",
                item["mirror_count"],
                item["identical_count"],
                item["drifted_count"],
                item["missing_count"],
                item["extra_count"],
            )
        )
    lines.append(
        markdown_table(
            (
                "Mirror root",
                "Exists",
                "Mirror skills",
                "Identical",
                "Content drift",
                "Missing",
                "Extra",
            ),
            mirror_rows,
        )
    )
    lines.append("")

    for item in report["mirror_drift"]:
        lines.append("### `%s`" % ascii_safe(item["mirror_root"]))
        lines.append("")
        lines.append("- Missing: %s" % ascii_safe(join_names(item["missing"])))
        lines.append("- Extra: %s" % ascii_safe(join_names(item["extra"])))
        drifted_names = [entry["skill"] for entry in item["drifted"]]
        lines.append("- Content drift: %s" % ascii_safe(join_names(drifted_names)))
        lines.append("")

    lines.append("## Top 20 Longest Canonical `SKILL.md`")
    lines.append("")
    longest_rows = []
    for index, item in enumerate(report["longest_canonical_skill_md"], start=1):
        longest_rows.append(
            (index, item["skill"], item["path"], item["lines"], item["words"], item["bytes"])
        )
    lines.append(
        markdown_table(
            ("Rank", "Skill", "Path", "Lines", "Words", "Bytes"), longest_rows
        )
    )
    lines.append("")

    lines.append("## Markdown Artifact Mentions")
    lines.append("")
    artifact_summary = artifacts["summary"]
    lines.append(
        markdown_table(
            ("Category", "Distinct paths"),
            (
                ("Likely generated runtime artifacts", artifact_summary["likely_generated_runtime"]),
                (
                    "Docs/shared references/templates",
                    artifact_summary["docs_shared_references_templates"],
                ),
                ("Other", artifact_summary["other"]),
                ("All distinct `.md` paths", artifact_summary["distinct_paths"]),
            ),
        )
    )
    lines.append("")

    lines.append("### Likely Generated Runtime Artifacts")
    lines.append("")
    lines.append(render_artifact_table(artifacts["by_category"]["likely_generated_runtime"]))
    lines.append("")

    lines.append("### Docs, Shared References, Templates")
    lines.append("")
    lines.append(
        render_artifact_table(artifacts["by_category"]["docs_shared_references_templates"])
    )
    lines.append("")

    lines.append("### Other Markdown Mentions")
    lines.append("")
    lines.append(render_artifact_table(artifacts["by_category"]["other"]))
    lines.append("")

    lines.append("## Entry Candidate Heuristics")
    lines.append("")
    lines.append(
        markdown_table(
            ("Candidate group", "Count"),
            (
                ("Public entry candidates", len(candidates["public_entry_candidate"])),
                ("Internal subskill candidates", len(candidates["internal_subskill_candidate"])),
                ("Ambiguous candidates", len(candidates["ambiguous_candidate"])),
            ),
        )
    )
    lines.append("")

    lines.append("### Public Entry Candidates")
    lines.append("")
    lines.append(render_candidate_table(candidates["public_entry_candidate"]))
    lines.append("")

    lines.append("### Internal Subskill Candidates")
    lines.append("")
    lines.append(render_candidate_table(candidates["internal_subskill_candidate"]))
    lines.append("")

    lines.append("### Ambiguous Candidates")
    lines.append("")
    lines.append(render_candidate_table(candidates["ambiguous_candidate"]))
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: Mapping[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = out_dir / "BASELINE_AUDIT.md"
    json_path = out_dir / "baseline_audit.json"
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    args = parse_args()
    repo = Path(args.repo).resolve()
    out_dir = Path(args.out)
    if not out_dir.is_absolute():
        out_dir = repo / out_dir

    report = build_report(repo)
    write_outputs(report, out_dir)

    markdown_path = out_dir / "BASELINE_AUDIT.md"
    json_path = out_dir / "baseline_audit.json"
    print("Wrote %s" % os.path.relpath(markdown_path, repo))
    print("Wrote %s" % os.path.relpath(json_path, repo))
    print("Canonical skills: %d" % report["counts"]["canonical_skill_md"])
    print("All SKILL.md files: %d" % report["counts"]["all_skill_md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
