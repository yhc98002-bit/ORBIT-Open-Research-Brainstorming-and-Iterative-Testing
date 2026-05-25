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


def rel_to_repo(repo: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path)


def clean_optional(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def normalize_verdict_tokens(tokens: Optional[Sequence[str]]) -> List[str]:
    normalized: List[str] = []
    seen = set()
    for token in tokens or []:
        value = token.strip().upper()
        if not value or value in seen:
            continue
        if not re.match(r"^[A-Z0-9_][A-Z0-9_-]*$", value):
            raise ValueError("expected verdict token must be uppercase token-like text: %r" % token)
        seen.add(value)
        normalized.append(value)
    return normalized


def producer_context_from_args(args: argparse.Namespace) -> Dict[str, Optional[str]]:
    current_stop = clean_optional(getattr(args, "current_stop", None)) or "NONE"
    producer_skill = clean_optional(getattr(args, "producer_skill", None))
    producer_phase = clean_optional(getattr(args, "producer_phase", None))
    diagnostic_id = clean_optional(getattr(args, "diagnostic_id", None))
    resume_command = clean_optional(getattr(args, "resume_command", None))
    return {
        "producer_skill": producer_skill,
        "producer_phase": producer_phase,
        "current_stop": current_stop,
        "diagnostic_id": diagnostic_id,
        "resume_command": resume_command,
    }


def render_prompt(
    phase_id: str,
    role: str,
    files: Sequence[str],
    objective: str,
    output_format: str,
    required_sections: Sequence[str],
    response_path: str,
    output_artifact: Optional[str],
    producer_context: Optional[Mapping[str, Optional[str]]] = None,
    verdict_required: bool = False,
    expected_verdict_tokens: Sequence[str] = (),
) -> str:
    files_block = "\n".join("- `%s`" % item for item in files) if files else "- No files listed. Ask the user for missing files rather than guessing."
    sections_block = "\n".join("- `%s`" % item for item in required_sections) if required_sections else "- Non-empty review response"
    artifact_line = output_artifact or "None. Import should validate only unless caller supplies an artifact path."
    verdict_lines: List[str] = []
    if verdict_required:
        token_list = ", ".join(expected_verdict_tokens) if expected_verdict_tokens else "<configured expected verdict tokens>"
        verdict_lines = [
            "",
            "Verdict import validation is enabled for this handoff.",
            "",
            "End the response with exactly one final verdict line using one of:",
            "",
            "```text",
            token_list,
            "```",
            "",
            "Accepted form:",
            "",
            "```text",
            "Final verdict: <ONE_TOKEN>",
            "```",
            "",
            "Do not write a candidate list such as `A | B`; import rejects templates.",
            "",
        ]
    context_lines: List[str] = []
    has_known_context = bool(
        producer_context
        and (
            producer_context.get("current_stop") not in (None, "NONE")
            or producer_context.get("producer_skill")
            or producer_context.get("producer_phase")
            or producer_context.get("diagnostic_id")
            or producer_context.get("resume_command")
        )
    )
    if producer_context and has_known_context:
        labels = (
            ("Current STOP", "current_stop"),
            ("Producer skill", "producer_skill"),
            ("Producer phase", "producer_phase"),
            ("Diagnostic ID", "diagnostic_id"),
            ("Resume command", "resume_command"),
        )
        for label, key in labels:
            value = producer_context.get(key)
            if value:
                context_lines.append("- %s: `%s`" % (label, value))
    context_block = context_lines or ["- Producer context unknown. Preserve this fact in the response metadata."]
    return "\n".join(
        [
            "# Standalone Codex Review Prompt",
            "",
            "Phase ID: `%s`" % phase_id,
            "",
            "## Workflow Context",
            "",
            "\n".join(context_block),
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
            *verdict_lines,
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
    expected_verdict_tokens = normalize_verdict_tokens(args.expected_verdict_token)
    if args.verdict_required and not expected_verdict_tokens:
        raise ValueError("--verdict-required requires at least one --expected-verdict-token")
    prompt_rel = "orbit-research/codex-prompts/%s.md" % phase_id
    response_rel = "orbit-research/codex-imports/%s.response.md" % phase_id
    producer_context = producer_context_from_args(args)

    prompt = render_prompt(
        phase_id=phase_id,
        role=args.role,
        files=args.file or [],
        objective=args.objective,
        output_format=args.output_format,
        required_sections=required_sections,
        response_path=response_rel,
        output_artifact=args.output_artifact,
        producer_context=producer_context,
        verdict_required=args.verdict_required,
        expected_verdict_tokens=expected_verdict_tokens,
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
        "verdict_required": bool(args.verdict_required),
        "expected_verdict_tokens": list(expected_verdict_tokens),
        "generated_at": utc_now_iso(),
        "producer_context": producer_context,
        "producer_skill": producer_context["producer_skill"],
        "producer_phase": producer_context["producer_phase"],
        "current_stop": producer_context["current_stop"],
        "diagnostic_id": producer_context["diagnostic_id"],
        "resume_command": producer_context["resume_command"],
    }
    write_json(metadata_path(repo, phase_id), metadata)

    if args.write_orbit_state:
        write_handoff_state(repo, phase_id, response_rel, metadata)

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


def strip_markdown_token(value: str) -> str:
    value = value.strip().rstrip(".").strip()
    previous = None
    while previous != value:
        previous = value
        value = value.strip().strip("*_`").strip()
    return value.upper()


def allowed_tokens_in_line(line: str, allowed_set: set[str]) -> List[str]:
    upper = line.upper()
    return sorted(
        {
            token
            for token in allowed_set
            if re.search(r"(?<![A-Z0-9_])%s(?![A-Z0-9_])" % re.escape(token), upper)
        }
    )


def extract_final_verdict(text: str, expected_tokens: Sequence[str]) -> Dict[str, Any]:
    allowed_set = set(normalize_verdict_tokens(expected_tokens))
    errors: List[str] = []
    occurrences: List[Dict[str, Any]] = []
    if not allowed_set:
        return {
            "verdict": None,
            "errors": ["verdict_required is true but expected_verdict_tokens is empty"],
        }

    verdict_re = re.compile(
        r"^(?:final\s+)?(?:verdict|decision)\s*[:=\-]\s*(.+)$",
        re.IGNORECASE,
    )
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        token_matches = allowed_tokens_in_line(line, allowed_set)
        if token_matches and "|" in line:
            errors.append("line %d contains a verdict candidate list, not a final verdict" % line_no)
            continue
        if len(token_matches) > 1:
            errors.append(
                "line %d contains multiple expected verdict tokens: %s"
                % (line_no, ", ".join(token_matches))
            )
            continue
        if not token_matches:
            continue

        clean = re.sub(r"^[#>\-\s]+", "", line).strip()
        match = verdict_re.search(clean)
        if match:
            value = strip_markdown_token(match.group(1))
            if value in allowed_set:
                occurrences.append({"line": line_no, "verdict": value})
            else:
                errors.append(
                    "line %d mentions a verdict token but is not exactly one expected final verdict"
                    % line_no
                )
            continue

        value = strip_markdown_token(clean)
        if value in allowed_set:
            occurrences.append({"line": line_no, "verdict": value})

    if len(occurrences) == 0:
        errors.append("missing exactly one final verdict token from expected_verdict_tokens")
    elif len(occurrences) > 1:
        errors.append(
            "expected exactly one final verdict token, found %d at lines %s"
            % (len(occurrences), ", ".join(str(item["line"]) for item in occurrences))
        )

    return {
        "verdict": occurrences[0]["verdict"] if len(occurrences) == 1 and not errors else None,
        "errors": errors,
    }


def validate_response_text(
    text: str,
    required_sections: Iterable[str],
    verdict_required: bool = False,
    expected_verdict_tokens: Sequence[str] = (),
) -> Dict[str, Any]:
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
    verdict: Optional[str] = None
    if verdict_required:
        verdict_result = extract_final_verdict(stripped, expected_verdict_tokens)
        verdict = verdict_result["verdict"]
        errors.extend(verdict_result["errors"])
    return {"valid": not errors, "errors": errors, "warnings": warnings, "verdict": verdict}


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


def metadata_for_response(repo: Path, response: Path) -> Dict[str, Any]:
    phase_id = phase_id_from_response(response)
    m_path = metadata_path(repo, phase_id)
    return read_json(m_path) if m_path.exists() else {}


def verdict_requirements_for(
    metadata: Mapping[str, Any],
    verdict_required_override: bool = False,
    token_override: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    verdict_required = bool(verdict_required_override or metadata.get("verdict_required"))
    if token_override:
        expected_tokens = normalize_verdict_tokens(token_override)
    else:
        metadata_tokens = metadata.get("expected_verdict_tokens")
        expected_tokens = normalize_verdict_tokens(
            metadata_tokens if isinstance(metadata_tokens, list) else []
        )
    return {
        "verdict_required": verdict_required,
        "expected_verdict_tokens": expected_tokens,
    }


def validate(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    response = repo_path(repo, args.response)
    metadata = metadata_for_response(repo, response)
    sections = required_sections_for(repo, response, args.required_section)
    verdict_requirements = verdict_requirements_for(
        metadata,
        verdict_required_override=args.verdict_required,
        token_override=args.expected_verdict_token,
    )
    try:
        text = response.read_text(encoding="utf-8", errors="replace")
        result = validate_response_text(text, sections, **verdict_requirements)
    except OSError as exc:
        result = {"valid": False, "errors": ["could not read response: %s" % exc], "warnings": [], "verdict": None}
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
    phase_id = phase_id_from_response(response)
    m_path = metadata_path(repo, phase_id)
    metadata: Dict[str, Any] = read_json(m_path) if m_path.exists() else {
        "schema_version": "0.1",
        "phase_id": phase_id,
        "response_path": rel_to_repo(repo, response),
        "producer_context": {
            "producer_skill": None,
            "producer_phase": None,
            "current_stop": "NONE",
            "diagnostic_id": None,
            "resume_command": None,
        },
        "producer_skill": None,
        "producer_phase": None,
        "current_stop": "NONE",
        "diagnostic_id": None,
        "resume_command": None,
    }
    metadata.setdefault("producer_skill", None)
    metadata.setdefault("producer_phase", None)
    metadata.setdefault("current_stop", "NONE")
    metadata.setdefault("diagnostic_id", None)
    metadata.setdefault("resume_command", None)
    metadata.setdefault(
        "producer_context",
        {
            "producer_skill": metadata.get("producer_skill"),
            "producer_phase": metadata.get("producer_phase"),
            "current_stop": metadata.get("current_stop"),
            "diagnostic_id": metadata.get("diagnostic_id"),
            "resume_command": metadata.get("resume_command"),
        },
    )
    sections = required_sections_for(repo, response, args.required_section)
    text = response.read_text(encoding="utf-8", errors="replace")
    verdict_requirements = verdict_requirements_for(
        metadata,
        verdict_required_override=args.verdict_required,
        token_override=args.expected_verdict_token,
    )
    result = validate_response_text(text, sections, **verdict_requirements)
    if not result["valid"]:
        print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True) if args.json else "invalid response")
        for error in result["errors"]:
            if not args.json:
                print("error: %s" % error)
        return 1

    output_artifact = args.output_artifact
    if output_artifact is None:
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

    imported_at = utc_now_iso()
    metadata.update(
        {
            "imported_at": imported_at,
            "imported_response_path": rel_to_repo(repo, response),
            "imported_output_artifact": copied_to,
            "import_valid": True,
            "imported_verdict": result.get("verdict"),
        }
    )
    write_json(m_path, metadata)
    write_imported_state(repo, phase_id, metadata)

    report = {
        "valid": True,
        "copied_to": copied_to,
        "warnings": result["warnings"],
        "errors": [],
        "verdict": result.get("verdict"),
        "producer_skill": metadata.get("producer_skill"),
        "producer_phase": metadata.get("producer_phase"),
        "diagnostic_id": metadata.get("diagnostic_id"),
        "resume_command": metadata.get("resume_command"),
    }
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print("Imported Codex review response")
        if copied_to:
            print("Wrote %s" % copied_to)
    return 0


def write_handoff_state(repo: Path, phase_id: str, response_rel: str, metadata: Mapping[str, Any]) -> None:
    try:
        from orbit_state import make_blocker, make_state, write_state
    except ImportError:  # pragma: no cover
        from tools.orbit_state import make_blocker, make_state, write_state

    command = "/import-codex-review %s" % response_rel
    current_stop = metadata.get("current_stop") if isinstance(metadata.get("current_stop"), str) else "NONE"
    current_skill = metadata.get("producer_skill") if isinstance(metadata.get("producer_skill"), str) and metadata.get("producer_skill") else "codex-review-handoff"
    current_phase = metadata.get("producer_phase") if isinstance(metadata.get("producer_phase"), str) and metadata.get("producer_phase") else phase_id
    state = make_state(
        current_stop=current_stop,
        current_skill=current_skill,
        current_phase=current_phase,
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


def write_imported_state(repo: Path, phase_id: str, metadata: Mapping[str, Any]) -> None:
    try:
        from orbit_state import make_state, write_state
    except ImportError:  # pragma: no cover
        from tools.orbit_state import make_state, write_state

    current_stop = metadata.get("current_stop") if isinstance(metadata.get("current_stop"), str) else "NONE"
    current_skill = metadata.get("producer_skill") if isinstance(metadata.get("producer_skill"), str) and metadata.get("producer_skill") else "codex-review-handoff"
    current_phase = metadata.get("producer_phase") if isinstance(metadata.get("producer_phase"), str) and metadata.get("producer_phase") else phase_id
    resume_command = metadata.get("resume_command") if isinstance(metadata.get("resume_command"), str) and metadata.get("resume_command") else "/orbit-status"
    state = make_state(
        current_stop=current_stop,
        current_skill=current_skill,
        current_phase=current_phase,
        status="paused",
        pause_reason="codex_review_imported",
        blockers=[],
        safe_next_command=resume_command,
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
    gen.add_argument("--verdict-required", action="store_true", help="Require exactly one final verdict token during import.")
    gen.add_argument("--expected-verdict-token", action="append", help="Allowed final verdict token. Repeatable.")
    gen.add_argument("--output-artifact", help="Artifact path to copy imported response into.")
    gen.add_argument("--current-stop", choices=("NONE", "STOP_A", "STOP_B", "STOP_C", "STOP_D", "COMPLETED"), default="NONE", help="Original ORBIT stop that requested the Codex review.")
    gen.add_argument("--producer-skill", help="Skill that requested the Codex review, e.g. diagnostic-to-review.")
    gen.add_argument("--producer-phase", help="Producer phase that requested the Codex review.")
    gen.add_argument("--diagnostic-id", help="Diagnostic session id, if applicable.")
    gen.add_argument("--resume-command", help="Command to resume the producer workflow after successful import.")
    gen.add_argument("--write-orbit-state", action="store_true", help="Write ORBIT_STATE blocked with codex_review_needed.")
    gen.set_defaults(func=generate)

    val = subparsers.add_parser("validate", help="Validate a standalone Codex response.")
    val.add_argument("response", help="Path to orbit-research/codex-imports/<phase-id>.response.md.")
    val.add_argument("--repo", default=".", help="Repository root.")
    val.add_argument("--required-section", action="append", help="Required section/token override. Repeatable.")
    val.add_argument("--verdict-required", action="store_true", help="Require exactly one final verdict token.")
    val.add_argument("--expected-verdict-token", action="append", help="Allowed final verdict token override. Repeatable.")
    val.add_argument("--json", action="store_true", help="Emit JSON report.")
    val.set_defaults(func=validate)

    imp = subparsers.add_parser("import", help="Validate and copy a standalone response to its review artifact.")
    imp.add_argument("response", help="Path to orbit-research/codex-imports/<phase-id>.response.md.")
    imp.add_argument("--repo", default=".", help="Repository root.")
    imp.add_argument("--required-section", action="append", help="Required section/token override. Repeatable.")
    imp.add_argument("--verdict-required", action="store_true", help="Require exactly one final verdict token.")
    imp.add_argument("--expected-verdict-token", action="append", help="Allowed final verdict token override. Repeatable.")
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
