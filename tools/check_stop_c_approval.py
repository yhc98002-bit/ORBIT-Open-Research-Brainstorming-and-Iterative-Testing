#!/usr/bin/env python3
"""Check STOP C approval before evidence-bound paper or submission work."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple


RED_TEAM_READY = "READY_FOR_PAPER"
HUMAN_PROCEED = "PROCEED"

RED_TEAM_VERDICTS = {
    "READY_FOR_PAPER",
    "REQUIRES_FIXES",
    "REDESIGN_REQUIRED",
    "HUMAN_DECISION_REQUIRED",
}

HUMAN_VERDICTS = {
    "PROCEED",
    "NARROW",
    "REDESIGN",
    "REVISE",
    "STOP",
    "HOLD",
    "BLOCKED",
}

READY_CODEX_REVIEWS = {"passed", "imported"}


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Project or repository root.")
    parser.add_argument(
        "--claim-ledger",
        default="claims/claim_ledger.json",
        help="Claim ledger path relative to --repo.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument(
        "--allow-legacy-missing-codex-review",
        action="store_true",
        help="Compatibility mode: allow a ready ledger with no codex_review field.",
    )
    parser.add_argument(
        "--allow-unmatched-legacy-approval",
        action="store_true",
        help="Compatibility mode: warn instead of blocking when legacy approval notes omit ledger identity.",
    )
    return parser.parse_args(argv)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def relpath(path: Path, repo: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def extract_metadata(ledger: Mapping[str, Any]) -> Dict[str, Optional[str]]:
    diagnostic_id = ledger.get("diagnostic_id")
    if not isinstance(diagnostic_id, str):
        diagnostic = ledger.get("diagnostic")
        if isinstance(diagnostic, Mapping):
            value = diagnostic.get("id")
            diagnostic_id = value if isinstance(value, str) else None

    ledger_hash = ledger.get("ledger_hash")
    if not isinstance(ledger_hash, str):
        value = ledger.get("hash")
        ledger_hash = value if isinstance(value, str) else None

    return {
        "diagnostic_id": diagnostic_id,
        "ledger_hash": ledger_hash,
    }


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


def parse_final_verdict(text: str, allowed: Iterable[str]) -> Optional[str]:
    allowed_set = {item.upper() for item in allowed}
    verdict_re = re.compile(
        r"^(?:final\s+)?(?:verdict|decision)\s*[:=\-]\s*(.+)$",
        re.IGNORECASE,
    )

    for raw_line in reversed(text.splitlines()):
        line = raw_line.strip()
        if not line:
            continue

        # Candidate lists/templates are not final approvals.
        if "|" in line:
            continue
        if len(allowed_tokens_in_line(line, allowed_set)) > 1:
            continue

        line = re.sub(r"^[#>\-\s]+", "", line).strip()
        match = verdict_re.search(line)
        if match:
            value = strip_markdown_token(match.group(1))
            if value in allowed_set:
                return value
            continue

        normalized = strip_markdown_token(line)
        if normalized in allowed_set:
            return normalized
    return None


def claim_ledger_readiness_errors(
    ledger: Mapping[str, Any],
    location: str = "$",
    allow_legacy_missing_codex_review: bool = False,
) -> List[str]:
    errors: List[str] = []

    status = ledger.get("status")
    if status != "ready":
        errors.append("%s.status: claim ledger must be 'ready', got %r" % (location, status))

    if ledger.get("gating") is False:
        errors.append("%s.gating: non-gating claim ledger cannot satisfy STOP C approval" % location)

    codex_review = ledger.get("codex_review")
    if codex_review in READY_CODEX_REVIEWS:
        return errors
    if codex_review is None and allow_legacy_missing_codex_review:
        return errors

    if codex_review is None:
        errors.append(
            "%s.codex_review: ready claim ledger must record Codex review as 'passed' or 'imported'"
            % location
        )
    else:
        errors.append(
            "%s.codex_review: %r cannot satisfy STOP C approval; expected 'passed' or 'imported'"
            % (location, codex_review)
        )
    return errors


def candidate_red_team_paths(repo: Path, diagnostic_id: Optional[str]) -> List[Path]:
    paths: List[Path] = []
    if diagnostic_id:
        paths.append(
            repo
            / "orbit-research"
            / "diagnostics"
            / diagnostic_id
            / "RED_TEAM_REVIEW.md"
        )
    else:
        diagnostics_root = repo / "orbit-research" / "diagnostics"
        if diagnostics_root.is_dir():
            paths.extend(sorted(diagnostics_root.glob("*/RED_TEAM_REVIEW.md")))
    paths.append(repo / "orbit-research" / "RED_TEAM_REVIEW.md")

    unique: List[Path] = []
    seen = set()
    for path in paths:
        key = path.as_posix()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def file_metadata_reference_messages(
    path: Path,
    repo: Path,
    diagnostic_id: Optional[str],
    ledger_hash: Optional[str],
) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    display_path = relpath(path, repo)
    if diagnostic_id and diagnostic_id not in text and diagnostic_id not in display_path:
        errors.append(
            "%s does not reference diagnostic_id %s" % (display_path, diagnostic_id)
        )
    if ledger_hash and ledger_hash not in text:
        errors.append("%s does not reference ledger_hash %s" % (display_path, ledger_hash))
    return errors, warnings


def evaluate_stop_c_approval(
    repo: Path,
    claim_ledger: str = "claims/claim_ledger.json",
    allow_legacy_missing_codex_review: bool = False,
    allow_unmatched_legacy_approval: bool = False,
) -> Dict[str, Any]:
    repo = repo.resolve()
    ledger_path = repo / claim_ledger
    report: Dict[str, Any] = {
        "status": "approved",
        "claim_ledger": claim_ledger,
        "diagnostic_id": None,
        "ledger_hash": None,
        "red_team_review": None,
        "red_team_verdict": None,
        "human_decision_note": "orbit-research/HUMAN_DECISION_NOTE.md",
        "human_decision_verdict": None,
        "errors": [],
        "warnings": [],
    }

    if not ledger_path.exists():
        report["errors"].append("missing %s" % claim_ledger)
        report["status"] = "blocked"
        return report

    try:
        ledger = load_json(ledger_path)
    except (OSError, json.JSONDecodeError) as exc:
        report["errors"].append("could not parse %s: %s" % (claim_ledger, exc))
        report["status"] = "blocked"
        return report

    if not isinstance(ledger, Mapping):
        report["errors"].append("%s must be a JSON object" % claim_ledger)
        report["status"] = "blocked"
        return report

    metadata = extract_metadata(ledger)
    diagnostic_id = metadata["diagnostic_id"]
    ledger_hash = metadata["ledger_hash"]
    report["diagnostic_id"] = diagnostic_id
    report["ledger_hash"] = ledger_hash
    report["claim_ledger_status"] = ledger.get("status")
    report["claim_ledger_gating"] = ledger.get("gating")
    report["claim_ledger_codex_review"] = ledger.get("codex_review")

    report["errors"].extend(
        claim_ledger_readiness_errors(
            ledger,
            "$",
            allow_legacy_missing_codex_review=allow_legacy_missing_codex_review,
        )
    )
    if ledger.get("codex_review") is None and allow_legacy_missing_codex_review:
        report["warnings"].append(
            "claim ledger has no codex_review field; accepted only because "
            "--allow-legacy-missing-codex-review was set"
        )

    red_team_paths = candidate_red_team_paths(repo, diagnostic_id)
    existing_red_team_paths = [path for path in red_team_paths if path.exists()]
    if not existing_red_team_paths:
        report["errors"].append(
            "missing RED_TEAM_REVIEW.md with final verdict %s" % RED_TEAM_READY
        )
    else:
        found_verdicts = []
        ready_identity_errors: List[str] = []
        for path in existing_red_team_paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            verdict = parse_final_verdict(text, RED_TEAM_VERDICTS)
            found_verdicts.append("%s=%s" % (relpath(path, repo), verdict or "UNKNOWN"))
            if verdict == RED_TEAM_READY:
                identity_errors, identity_warnings = file_metadata_reference_messages(
                    path,
                    repo,
                    diagnostic_id,
                    ledger_hash,
                )
                if identity_errors and not allow_unmatched_legacy_approval:
                    ready_identity_errors.extend(identity_errors)
                    continue
                report["red_team_review"] = relpath(path, repo)
                report["red_team_verdict"] = verdict
                if identity_errors and allow_unmatched_legacy_approval:
                    report["warnings"].extend(
                        "legacy unmatched approval accepted: %s" % error
                        for error in identity_errors
                    )
                report["warnings"].extend(identity_warnings)
                break
        if report["red_team_verdict"] != RED_TEAM_READY:
            if ready_identity_errors:
                report["errors"].extend(ready_identity_errors)
            else:
                report["errors"].append(
                    "RED_TEAM_REVIEW final verdict must be %s; found %s"
                    % (RED_TEAM_READY, ", ".join(found_verdicts))
                )

    human_path = repo / "orbit-research" / "HUMAN_DECISION_NOTE.md"
    if not human_path.exists():
        report["errors"].append(
            "missing orbit-research/HUMAN_DECISION_NOTE.md ending %s" % HUMAN_PROCEED
        )
    else:
        text = human_path.read_text(encoding="utf-8", errors="replace")
        verdict = parse_final_verdict(text, HUMAN_VERDICTS)
        report["human_decision_verdict"] = verdict
        if verdict != HUMAN_PROCEED:
            report["errors"].append(
                "HUMAN_DECISION_NOTE final verdict must be %s; found %s"
                % (HUMAN_PROCEED, verdict or "UNKNOWN")
            )
        else:
            identity_errors, identity_warnings = file_metadata_reference_messages(
                human_path,
                repo,
                diagnostic_id,
                ledger_hash,
            )
            if identity_errors and allow_unmatched_legacy_approval:
                report["warnings"].extend(
                    "legacy unmatched approval accepted: %s" % error
                    for error in identity_errors
                )
            else:
                report["errors"].extend(identity_errors)
            report["warnings"].extend(identity_warnings)

    if report["errors"]:
        report["status"] = "blocked"
    return report


def print_pretty(report: Mapping[str, Any]) -> None:
    print("STOP C approval: %s" % report["status"])
    print("Claim ledger: %s" % report["claim_ledger"])
    print(
        "Red-team review: %s (%s)"
        % (report.get("red_team_review") or "missing", report.get("red_team_verdict") or "UNKNOWN")
    )
    print(
        "Human decision: %s (%s)"
        % (report.get("human_decision_note") or "missing", report.get("human_decision_verdict") or "UNKNOWN")
    )
    if report.get("errors"):
        print("Blocked by:")
        for error in report["errors"]:
            print("  - %s" % error)
    if report.get("warnings"):
        print("Warnings:")
        for warning in report["warnings"]:
            print("  - %s" % warning)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    repo = Path(args.repo)
    report = evaluate_stop_c_approval(
        repo,
        args.claim_ledger,
        allow_legacy_missing_codex_review=args.allow_legacy_missing_codex_review,
        allow_unmatched_legacy_approval=args.allow_unmatched_legacy_approval,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_pretty(report)
    return 0 if report["status"] == "approved" else 1


if __name__ == "__main__":
    raise SystemExit(main())
