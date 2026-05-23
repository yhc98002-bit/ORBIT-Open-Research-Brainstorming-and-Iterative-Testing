#!/usr/bin/env python3
"""Check STOP C approval before evidence-bound paper or submission work."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


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
    "REVISE",
    "STOP",
    "HOLD",
    "BLOCKED",
}


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Project or repository root.")
    parser.add_argument(
        "--claim-ledger",
        default="claims/claim_ledger.json",
        help="Claim ledger path relative to --repo.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
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


def parse_final_verdict(text: str, allowed: Iterable[str]) -> Optional[str]:
    allowed_set = {item.upper() for item in allowed}
    verdict_re = re.compile(
        r"(?:final\s+)?(?:verdict|decision)\s*[:=\-]\s*([A-Z][A-Z0-9_]+)",
        re.IGNORECASE,
    )

    for raw_line in reversed(text.splitlines()):
        line = raw_line.strip().strip("*_` ")
        if not line:
            continue
        match = verdict_re.search(line)
        if match:
            value = match.group(1).upper()
            return value if value in allowed_set else value

        normalized = re.sub(r"^[#>\-\s]+", "", line).strip().upper()
        normalized = normalized.rstrip(".")
        if normalized in allowed_set:
            return normalized
    return None


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


def file_mentions_expected_metadata(
    path: Path,
    diagnostic_id: Optional[str],
    ledger_hash: Optional[str],
) -> List[str]:
    warnings: List[str] = []
    text = path.read_text(encoding="utf-8", errors="replace")
    if diagnostic_id and diagnostic_id not in text and diagnostic_id not in path.as_posix():
        warnings.append(
            "%s does not mention diagnostic_id %s" % (path.as_posix(), diagnostic_id)
        )
    if ledger_hash and ledger_hash not in text:
        warnings.append("%s does not mention ledger_hash %s" % (path.as_posix(), ledger_hash))
    return warnings


def evaluate_stop_c_approval(
    repo: Path,
    claim_ledger: str = "claims/claim_ledger.json",
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

    red_team_paths = candidate_red_team_paths(repo, diagnostic_id)
    existing_red_team_paths = [path for path in red_team_paths if path.exists()]
    if not existing_red_team_paths:
        report["errors"].append(
            "missing RED_TEAM_REVIEW.md with final verdict %s" % RED_TEAM_READY
        )
    else:
        found_verdicts = []
        for path in existing_red_team_paths:
            text = path.read_text(encoding="utf-8", errors="replace")
            verdict = parse_final_verdict(text, RED_TEAM_VERDICTS)
            found_verdicts.append("%s=%s" % (relpath(path, repo), verdict or "UNKNOWN"))
            if verdict == RED_TEAM_READY:
                report["red_team_review"] = relpath(path, repo)
                report["red_team_verdict"] = verdict
                report["warnings"].extend(
                    file_mentions_expected_metadata(path, diagnostic_id, ledger_hash)
                )
                break
        if report["red_team_verdict"] != RED_TEAM_READY:
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
            report["warnings"].extend(
                file_mentions_expected_metadata(human_path, diagnostic_id, ledger_hash)
            )

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
    report = evaluate_stop_c_approval(repo, args.claim_ledger)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_pretty(report)
    return 0 if report["status"] == "approved" else 1


if __name__ == "__main__":
    raise SystemExit(main())
