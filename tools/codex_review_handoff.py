#!/usr/bin/env python3
"""Standalone Codex review handoff helpers.

This tool does not run Codex. It creates a prompt for a user-run standalone
Codex session, records import metadata, validates the saved response, and can
copy a validated response into the expected review artifact.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


DEFAULT_REQUIRED_SECTIONS = ("VERDICT",)
NEGATIVE_PATTERNS = (
    "i cannot complete",
    "i can't complete",
    "cannot access",
    "unable to access",
    "i do not have access",
)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def repo_path(repo: Path, rel: str) -> Path:
    path = Path(rel)
    return path if path.is_absolute() else repo / path


def safe_phase_id(value: str) -> str:
    normalized = value.strip().replace("/", "_").replace("\\", "_")
    if not normalized or not re.match(r"^[A-Za-z0-9_.-]+$", normalized):
        raise ValueError("phase-id must contain only letters, numbers, dot, underscore, or hyphen")
    return normalized


def phase_id_from_response(path: Path) -> str:
    name = path.name
    suffix = ".response.md"
    if not name.endswith(suffix):
        raise ValueError("response filename must end with %s" % suffix)
    return safe_phase_id(name[: -len(suffix)])


def prompt_path(repo: Path, phase_id: str) -> Path:
    return repo / "orbit-research" / "codex-prompts" / ("%s.md" % phase_id)


def metadata_path(repo: Path, phase_id: str) -> Path:
    return repo / "orbit-research" / "codex-prompts" / ("%s.json" % phase_id)


def import_path(repo: Path, phase_id: str) -> Path:
    return repo / "orbit-research" / "codex-imports" / ("%s.response.md" % phase_id)


def read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("%s must contain a JSON object" % path)
    return data


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(dict(data), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def render_prompt(
    phase_id: str,
    role: str,
    files: Sequence[str],
    objective: str,
    output_format: str,
    required_sections: Sequence[str],
    response_path: str,
    output_artifact: Optional[str],
) -> str:
    files_block = "\n".join("- `%s`" % item for item in files) if files else "- No files listed. Ask the user for missing files rather than guessing."
    sections_block = "\n".join("- `%s`" % item for item in required_sections) if required_sections else "- Non-empty review response"
    artifact_line = output_artifact or "None. Import should validate only unless caller supplies an artifact path."
    return "\n".join(
        [
            "# Standalone Codex Review Prompt",
            "",
            "Phase ID: `%s`" % phase_id,
            "",
            "## Role",
            "",
            role.strip(),
            "",
            "## Files To Read",
            "",
            files_block,
            "",
            "## Review Objective",
            "",
            objective.strip(),
            "",
            "## Required Output Format",
            "",
            output_format.strip(),
            "",
            "The response must include these required sections or tokens:",
            "",
            sections_block,
            "",
            "## Import Instructions",
            "",
            "Save the complete standalone Codex response at:",
            "",
            "```text",
            response_path,
            "```",
            "",
            "Then import it with:",
            "",
            "```text",
            "/import-codex-review %s" % response_path,
            "```",
            "",
            "Expected review artifact or pack field:",
            "",
            "```text",
            artifact_line,
            "```",
            "",
            "Do not summarize or rewrite the response before saving it. The import path is a required Codex review artifact, not an optional note.",
            "",
        ]
    )


def generate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    phase_id = safe_phase_id(args.phase_id)
    required_sections = tuple(args.required_section or DEFAULT_REQUIRED_SECTIONS)
    prompt_rel = "orbit-research/codex-prompts/%s.md" % phase_id
    response_rel = "orbit-research/codex-imports/%s.response.md" % phase_id

    prompt = render_prompt(
        phase_id=phase_id,
        role=args.role,
        files=args.file or [],
        objective=args.objective,
        output_format=args.output_format,
        required_sections=required_sections,
        response_path=response_rel,
        output_artifact=args.output_artifact,
    )

    p_path = prompt_path(repo, phase_id)
    p_path.parent.mkdir(parents=True, exist_ok=True)
    p_path.write_text(prompt, encoding="utf-8")

    metadata = {
        "schema_version": "0.1",
        "phase_id": phase_id,
        "prompt_path": prompt_rel,
        "response_path": response_rel,
        "output_artifact": args.output_artifact,
        "role": args.role,
        "files": list(args.file or []),
        "objective": args.objective,
        "output_format": args.output_format,
        "required_sections": list(required_sections),
        "generated_at": utc_now_iso(),
    }
    write_json(metadata_path(repo, phase_id), metadata)

    if args.write_orbit_state:
        write_handoff_state(repo, phase_id, response_rel)

    print("Wrote %s" % prompt_rel)
    print("Expected response %s" % response_rel)
    print("Import command: /import-codex-review %s" % response_rel)
    return 0


def section_present(text: str, section: str) -> bool:
    needle = section.strip()
    if not needle:
        return True
    if re.search(r"^\s{0,3}#{1,6}\s*%s\b" % re.escape(needle), text, flags=re.IGNORECASE | re.MULTILINE):
        return True
    return needle.lower() in text.lower()


def validate_response_text(text: str, required_sections: Iterable[str]) -> Dict[str, Any]:
    errors: List[str] = []
    warnings: List[str] = []
    stripped = text.strip()
    if len(stripped) < 80:
        errors.append("response is too short to be a substantive Codex review")
    lowered = stripped.lower()
    for pattern in NEGATIVE_PATTERNS:
        if pattern in lowered:
            errors.append("response appears to report inability to complete review: %s" % pattern)
            break
    missing = [section for section in required_sections if not section_present(stripped, section)]
    if missing:
        errors.append("missing required sections/tokens: %s" % ", ".join(missing))
    if "verdict" not in lowered:
        warnings.append("response does not contain the word verdict")
    return {"valid": not errors, "errors": errors, "warnings": warnings}


def required_sections_for(repo: Path, response: Path, explicit: Optional[Sequence[str]]) -> List[str]:
    if explicit:
        return list(explicit)
    phase_id = phase_id_from_response(response)
    m_path = metadata_path(repo, phase_id)
    if m_path.exists():
        metadata = read_json(m_path)
        sections = metadata.get("required_sections")
        if isinstance(sections, list) and all(isinstance(item, str) for item in sections):
            return list(sections)
    return list(DEFAULT_REQUIRED_SECTIONS)


def validate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    response = repo_path(repo, args.response)
    sections = required_sections_for(repo, response, args.required_section)
    try:
        text = response.read_text(encoding="utf-8", errors="replace")
        result = validate_response_text(text, sections)
    except OSError as exc:
        result = {"valid": False, "errors": ["could not read response: %s" % exc], "warnings": []}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print("valid: %s" % result["valid"])
        for warning in result["warnings"]:
            print("warning: %s" % warning)
        for error in result["errors"]:
            print("error: %s" % error)
    return 0 if result["valid"] else 1


def import_review(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    response = repo_path(repo, args.response)
    sections = required_sections_for(repo, response, args.required_section)
    text = response.read_text(encoding="utf-8", errors="replace")
    result = validate_response_text(text, sections)
    if not result["valid"]:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) if args.json else "invalid response")
        for error in result["errors"]:
            if not args.json:
                print("error: %s" % error)
        return 1

    output_artifact = args.output_artifact
    if output_artifact is None:
        phase_id = phase_id_from_response(response)
        m_path = metadata_path(repo, phase_id)
        if m_path.exists():
            metadata = read_json(m_path)
            value = metadata.get("output_artifact")
            if isinstance(value, str) and value:
                output_artifact = value

    copied_to: Optional[str] = None
    if output_artifact:
        target = repo_path(repo, output_artifact)
        target.parent.mkdir(parents=True, exist_ok=True)
        if args.mode == "append":
            existing = target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""
            target.write_text((existing.rstrip() + "\n\n" if existing.strip() else "") + text.rstrip() + "\n", encoding="utf-8")
        else:
            shutil.copyfile(response, target)
        copied_to = output_artifact

    report = {"valid": True, "copied_to": copied_to, "warnings": result["warnings"], "errors": []}
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print("Imported Codex review response")
        if copied_to:
            print("Wrote %s" % copied_to)
    return 0


def write_handoff_state(repo: Path, phase_id: str, response_rel: str) -> None:
    try:
        from orbit_state import make_blocker, make_state, write_state
    except ImportError:  # pragma: no cover
        from tools.orbit_state import make_blocker, make_state, write_state

    command = "/import-codex-review %s" % response_rel
    state = make_state(
        current_stop="NONE",
        current_skill="codex-review-handoff",
        current_phase=phase_id,
        status="blocked",
        pause_reason="codex_review_needed",
        blockers=[
            make_blocker(
                "CODEX_REVIEW",
                "codex_unavailable",
                "orbit-research/codex-prompts/%s.md" % phase_id,
                "Codex MCP failed; standalone Codex review import is required",
                command,
            )
        ],
        safe_next_command=command,
    )
    write_state(repo, state)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate, validate, and import standalone Codex review handoffs.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen = subparsers.add_parser("generate", help="Generate a standalone Codex review prompt and metadata.")
    gen.add_argument("--repo", default=".", help="Repository root.")
    gen.add_argument("--phase-id", required=True, help="Stable phase id, e.g. stop-c.phase-4-review.")
    gen.add_argument("--role", required=True, help="Reviewer role to include in the prompt.")
    gen.add_argument("--file", action="append", help="File path the standalone reviewer must read. Repeatable.")
    gen.add_argument("--objective", required=True, help="Review objective.")
    gen.add_argument("--output-format", required=True, help="Required response schema or format.")
    gen.add_argument("--required-section", action="append", help="Required response section/token. Repeatable.")
    gen.add_argument("--output-artifact", help="Artifact path to copy imported response into.")
    gen.add_argument("--write-orbit-state", action="store_true", help="Write ORBIT_STATE blocked with codex_review_needed.")
    gen.set_defaults(func=generate)

    val = subparsers.add_parser("validate", help="Validate a standalone Codex response.")
    val.add_argument("response", help="Path to orbit-research/codex-imports/<phase-id>.response.md.")
    val.add_argument("--repo", default=".", help="Repository root.")
    val.add_argument("--required-section", action="append", help="Required section/token override. Repeatable.")
    val.add_argument("--json", action="store_true", help="Emit JSON report.")
    val.set_defaults(func=validate)

    imp = subparsers.add_parser("import", help="Validate and copy a standalone response to its review artifact.")
    imp.add_argument("response", help="Path to orbit-research/codex-imports/<phase-id>.response.md.")
    imp.add_argument("--repo", default=".", help="Repository root.")
    imp.add_argument("--required-section", action="append", help="Required section/token override. Repeatable.")
    imp.add_argument("--output-artifact", help="Override target review artifact.")
    imp.add_argument("--mode", choices=("copy", "append"), default="copy", help="How to write the target artifact.")
    imp.add_argument("--json", action="store_true", help="Emit JSON report.")
    imp.set_defaults(func=import_review)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
