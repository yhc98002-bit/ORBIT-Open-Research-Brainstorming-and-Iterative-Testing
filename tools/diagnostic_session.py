#!/usr/bin/env python3
"""Manage ORBIT STOP C diagnostic session identity and resume state.

This helper intentionally does not execute experiments. It creates and updates
the per-diagnostic context that `/diagnostic-to-review` and `/run-experiment`
can share so resume decisions are based on diagnostic_id/input_hash, not legacy
fixed-path artifacts.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional
from hashlib import sha256


SCHEMA_VERSION = "0.1"
DIAGNOSTICS_REL = Path("orbit-research") / "diagnostics"
CONTEXT_NAME = "DIAGNOSTIC_CONTEXT.json"

DIAGNOSTIC_KINDS = {
    "implementation_smoke",
    "headroom_probe",
    "local_mechanism_probe",
    "paper_bearing_main",
    "paper_bearing_ablation",
    "scaleup_candidate",
    "unknown",
}
CLAIM_RELEVANCE = {
    "none",
    "local",
    "paper_scope_affecting",
    "primary_evidence",
    "unknown",
}
STATUSES = {
    "initialized",
    "blocked",
    "running",
    "run_complete",
    "interpreted",
    "claim_routed",
    "reviewed",
    "stop_c_ready",
    "completed",
    "archived",
}
AUDIT_VERDICTS = {"PASS", "FIX_BEFORE_GPU", "REDESIGN_EXPERIMENT", "ERROR"}
REGIME_VALUES = {"true", "false", "unknown"}
ACTIVE_STATUSES = {
    "initialized",
    "blocked",
    "running",
    "run_complete",
    "interpreted",
    "claim_routed",
}
TERMINAL_STATUSES = {"reviewed", "stop_c_ready", "completed", "archived"}
DIAGNOSTIC_ID_RE = re.compile(r"^diag_[A-Za-z0-9_.-]+$")


class DiagnosticSessionError(ValueError):
    """Raised when a diagnostic session context is malformed or missing."""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_input(value: str) -> str:
    return " ".join(value.strip().split())


def stable_input_hash(value: str) -> str:
    return sha256(normalize_input(value).encode("utf-8")).hexdigest()


def diagnostics_dir(repo: Path) -> Path:
    return repo / DIAGNOSTICS_REL


def context_path(repo: Path, diagnostic_id: str) -> Path:
    validate_diagnostic_id(diagnostic_id)
    return diagnostics_dir(repo) / diagnostic_id / CONTEXT_NAME


def rel_to_repo(repo: Path, path: Path) -> str:
    try:
        return path.relative_to(repo).as_posix()
    except ValueError:
        return path.as_posix()


def validate_diagnostic_id(value: str) -> None:
    if not DIAGNOSTIC_ID_RE.match(value):
        raise DiagnosticSessionError("invalid diagnostic_id: %r" % value)


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def now_diagnostic_id(input_hash: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return "diag_%s_%s" % (stamp, input_hash[:10])


def classify_kind(value: str) -> str:
    lowered = value.lower()
    if "headroom" in lowered:
        return "headroom_probe"
    if "smoke" in lowered or "--smoke" in lowered or "sanity" in lowered:
        return "implementation_smoke"
    if "local" in lowered or "mechanism_probe" in lowered:
        return "local_mechanism_probe"
    if "ablation" in lowered:
        return "paper_bearing_ablation"
    if "scaleup" in lowered or "scale-up" in lowered:
        return "scaleup_candidate"
    if "claim" in lowered or "paper" in lowered or "main" in lowered:
        return "paper_bearing_main"
    return "unknown"


def classify_claim_relevance(value: str, diagnostic_kind: str) -> str:
    lowered = value.lower()
    if diagnostic_kind in {"implementation_smoke", "headroom_probe"}:
        return "none"
    if diagnostic_kind == "local_mechanism_probe":
        return "local"
    if diagnostic_kind in {"paper_bearing_main", "paper_bearing_ablation"}:
        return "primary_evidence"
    if diagnostic_kind == "scaleup_candidate":
        return "paper_scope_affecting"
    if "claim" in lowered or "paper" in lowered:
        return "primary_evidence"
    return "unknown"


def load_context(path: Path) -> Dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise DiagnosticSessionError("missing diagnostic context: %s" % path) from exc
    except json.JSONDecodeError as exc:
        raise DiagnosticSessionError("invalid diagnostic context JSON: %s" % path) from exc
    if not isinstance(data, dict):
        raise DiagnosticSessionError("diagnostic context must be a JSON object: %s" % path)
    validate_context(data)
    return data


def write_context(path: Path, context: Mapping[str, Any]) -> None:
    validate_context(context)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(dict(context), handle, indent=2, sort_keys=True, ensure_ascii=True)
        handle.write("\n")


def validate_context(context: Mapping[str, Any]) -> None:
    required = {
        "diagnostic_id",
        "input",
        "input_hash",
        "diagnostic_kind",
        "claim_relevance",
        "status",
        "run_id",
        "result_paths",
        "audit",
        "artifact_inventory",
    }
    missing = sorted(required - set(context))
    if missing:
        raise DiagnosticSessionError("diagnostic context missing keys: %s" % ", ".join(missing))

    validate_diagnostic_id(str(context.get("diagnostic_id")))
    if not isinstance(context.get("input"), str) or not context["input"].strip():
        raise DiagnosticSessionError("context.input must be a non-empty string")
    input_hash = context.get("input_hash")
    if not isinstance(input_hash, str) or not re.match(r"^[a-f0-9]{64}$", input_hash):
        raise DiagnosticSessionError("context.input_hash must be a sha256 hex string")
    if context.get("diagnostic_kind") not in DIAGNOSTIC_KINDS:
        raise DiagnosticSessionError("invalid diagnostic_kind: %r" % context.get("diagnostic_kind"))
    if context.get("claim_relevance") not in CLAIM_RELEVANCE:
        raise DiagnosticSessionError("invalid claim_relevance: %r" % context.get("claim_relevance"))
    if context.get("status") not in STATUSES:
        raise DiagnosticSessionError("invalid status: %r" % context.get("status"))
    if context.get("run_id") is not None and not isinstance(context.get("run_id"), str):
        raise DiagnosticSessionError("run_id must be string or null")
    if not isinstance(context.get("result_paths"), list) or not all(
        isinstance(item, str) for item in context["result_paths"]
    ):
        raise DiagnosticSessionError("result_paths must be a list of strings")
    if not isinstance(context.get("artifact_inventory"), list) or not all(
        isinstance(item, str) for item in context["artifact_inventory"]
    ):
        raise DiagnosticSessionError("artifact_inventory must be a list of strings")
    audit = context.get("audit")
    if not isinstance(audit, dict):
        raise DiagnosticSessionError("audit must be an object")
    if audit.get("verdict") is not None and audit.get("verdict") not in AUDIT_VERDICTS:
        raise DiagnosticSessionError("invalid audit.verdict: %r" % audit.get("verdict"))
    if audit.get("regime_preserved") not in {"true", "false", "unknown"}:
        raise DiagnosticSessionError("invalid audit.regime_preserved: %r" % audit.get("regime_preserved"))
    if not isinstance(audit.get("mechanism_rejected"), bool):
        raise DiagnosticSessionError("audit.mechanism_rejected must be boolean")
    if audit.get("regime_preserved") == "false" and audit.get("mechanism_rejected") is True:
        raise DiagnosticSessionError(
            "invalid G12 audit: regime_preserved=false cannot reject the mechanism"
        )


def iter_context_paths(repo: Path) -> Iterable[Path]:
    root = diagnostics_dir(repo)
    if not root.exists():
        return []
    return sorted(root.glob("*/%s" % CONTEXT_NAME))


def load_all_contexts(repo: Path) -> List[Dict[str, Any]]:
    contexts: List[Dict[str, Any]] = []
    for path in iter_context_paths(repo):
        try:
            context = load_context(path)
        except DiagnosticSessionError:
            continue
        context["_context_path"] = rel_to_repo(repo, path)
        contexts.append(context)
    return sorted(contexts, key=lambda item: (item.get("created_at", ""), item["diagnostic_id"]))


def find_matching_contexts(repo: Path, input_hash: str) -> List[Dict[str, Any]]:
    return [context for context in load_all_contexts(repo) if context.get("input_hash") == input_hash]


def active_contexts(repo: Path) -> List[Dict[str, Any]]:
    return [context for context in load_all_contexts(repo) if context.get("status") in ACTIVE_STATUSES]


def is_active_status(status: Any) -> bool:
    return status in ACTIVE_STATUSES


def is_terminal_status(status: Any) -> bool:
    return status in TERMINAL_STATUSES


def latest_context(contexts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    return contexts[-1] if contexts else None


def make_context(
    repo: Path,
    input_value: str,
    diagnostic_kind: Optional[str] = None,
    claim_relevance: Optional[str] = None,
) -> Dict[str, Any]:
    input_hash = stable_input_hash(input_value)
    kind = diagnostic_kind or classify_kind(input_value)
    relevance = claim_relevance or classify_claim_relevance(input_value, kind)
    if kind not in DIAGNOSTIC_KINDS:
        raise DiagnosticSessionError("invalid diagnostic_kind: %s" % kind)
    if relevance not in CLAIM_RELEVANCE:
        raise DiagnosticSessionError("invalid claim_relevance: %s" % relevance)

    diagnostic_id = now_diagnostic_id(input_hash)
    path = context_path(repo, diagnostic_id)
    counter = 2
    while path.exists():
        diagnostic_id = "%s_%d" % (now_diagnostic_id(input_hash), counter)
        path = context_path(repo, diagnostic_id)
        counter += 1

    return {
        "schema_version": SCHEMA_VERSION,
        "diagnostic_id": diagnostic_id,
        "input": input_value,
        "input_hash": input_hash,
        "diagnostic_kind": kind,
        "claim_relevance": relevance,
        "status": "initialized",
        "run_id": None,
        "result_paths": [],
        "audit": {
            "verdict": None,
            "regime_preserved": "unknown",
            "mechanism_rejected": False,
        },
        "artifact_inventory": [],
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }


def create_session(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    input_hash = stable_input_hash(args.input)
    matches = find_matching_contexts(repo, input_hash)
    latest = latest_context(matches)
    if latest and not args.fresh:
        if is_active_status(latest.get("status")):
            context = latest
            return {
                "ok": True,
                "created": False,
                "status": "existing_active",
                "diagnostic_id": context["diagnostic_id"],
                "input_hash": input_hash,
                "context_path": context["_context_path"],
                "context": without_private_keys(context),
                "message": "reusing active diagnostic session with matching input_hash",
            }
        return {
            "ok": False,
            "created": False,
            "status": "terminal_session_exists",
            "diagnostic_id": latest["diagnostic_id"],
            "input_hash": input_hash,
            "context_path": latest["_context_path"],
            "context_status": latest.get("status"),
            "context": without_private_keys(latest),
            "message": "matching diagnostic session is terminal; use resume to inspect/recover it or create --fresh to rerun",
        }

    context = make_context(repo, args.input, args.diagnostic_kind, args.claim_relevance)
    path = context_path(repo, context["diagnostic_id"])
    write_context(path, context)
    return {
        "ok": True,
        "created": True,
        "status": "created",
        "diagnostic_id": context["diagnostic_id"],
        "input_hash": context["input_hash"],
        "context_path": rel_to_repo(repo, path),
        "context": context,
    }


def resume_session(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    input_hash = stable_input_hash(args.input)
    matches = find_matching_contexts(repo, input_hash)
    context = latest_context(matches)
    if context:
        return {
            "ok": True,
            "status": "resume_ok",
            "diagnostic_id": context["diagnostic_id"],
            "input_hash": input_hash,
            "context_path": context["_context_path"],
            "context_status": context.get("status"),
            "context": without_private_keys(context),
            "message": "resume approved by explicit matching input_hash",
        }

    active = active_contexts(repo)
    if active:
        return {
            "ok": False,
            "status": "blocked_mismatched_active",
            "input_hash": input_hash,
            "active_diagnostics": [
                {
                    "diagnostic_id": context["diagnostic_id"],
                    "input_hash": context["input_hash"],
                    "status": context["status"],
                    "context_path": context["_context_path"],
                }
                for context in active
            ],
            "message": "no matching input_hash; refusing to resume a different active diagnostic session",
        }

    return {
        "ok": False,
        "status": "missing_matching_session",
        "input_hash": input_hash,
        "message": "no matching diagnostic context; create a new session or check the input command",
    }


def status_session(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    path = context_path(repo, args.diagnostic_id)
    context = load_context(path)
    return {
        "ok": True,
        "status": context["status"],
        "diagnostic_id": context["diagnostic_id"],
        "context_path": rel_to_repo(repo, path),
        "context": context,
    }


def validate_resume(args: argparse.Namespace) -> Dict[str, Any]:
    return resume_session(args)


def update_run(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    path = context_path(repo, args.diagnostic_id)
    context = load_context(path)
    context["run_id"] = args.run_id
    merged_paths = sorted(set(context.get("result_paths", [])) | set(args.result_path or []))
    context["result_paths"] = merged_paths
    context["status"] = "run_complete"
    context["updated_at"] = utc_now_iso()
    inventory = set(context.get("artifact_inventory", []))
    inventory.add(rel_to_repo(repo, path))
    inventory.update(merged_paths)
    context["artifact_inventory"] = sorted(inventory)
    write_context(path, context)
    return {
        "ok": True,
        "status": "updated",
        "diagnostic_id": context["diagnostic_id"],
        "context_path": rel_to_repo(repo, path),
        "context": context,
    }


def update_audit(args: argparse.Namespace) -> Dict[str, Any]:
    repo = Path(args.repo).resolve()
    path = context_path(repo, args.diagnostic_id)
    context = load_context(path)
    if args.regime_preserved == "false" and args.mechanism_rejected is True:
        raise DiagnosticSessionError(
            "invalid G12 audit: regime_preserved=false requires mechanism_rejected=false"
        )
    context["audit"] = {
        "verdict": args.verdict,
        "regime_preserved": args.regime_preserved,
        "mechanism_rejected": args.mechanism_rejected,
    }
    context["status"] = "run_complete" if args.verdict == "PASS" else "blocked"
    context["updated_at"] = utc_now_iso()
    inventory = set(context.get("artifact_inventory", []))
    inventory.add(rel_to_repo(repo, path))
    context["artifact_inventory"] = sorted(inventory)
    write_context(path, context)
    return {
        "ok": True,
        "status": "updated",
        "diagnostic_id": context["diagnostic_id"],
        "context_path": rel_to_repo(repo, path),
        "context": context,
    }


def without_private_keys(context: Mapping[str, Any]) -> Dict[str, Any]:
    return {key: value for key, value in context.items() if not key.startswith("_")}


def render_text(payload: Mapping[str, Any]) -> str:
    lines = [
        "status: %s" % payload.get("status", "unknown"),
        "ok: %s" % payload.get("ok"),
    ]
    if payload.get("diagnostic_id"):
        lines.append("diagnostic_id: %s" % payload["diagnostic_id"])
    if payload.get("input_hash"):
        lines.append("input_hash: %s" % payload["input_hash"])
    if payload.get("context_path"):
        lines.append("context_path: %s" % payload["context_path"])
    if payload.get("message"):
        lines.append("message: %s" % payload["message"])
    if payload.get("context_status"):
        lines.append("context_status: %s" % payload["context_status"])
    if payload.get("active_diagnostics"):
        lines.append("active_diagnostics:")
        for item in payload["active_diagnostics"]:
            lines.append("  - %s (%s)" % (item["diagnostic_id"], item["status"]))
    return "\n".join(lines) + "\n"


def emit(payload: Mapping[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(dict(payload), indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print(render_text(payload), end="")


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--repo", default=".", help="Repository root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON payload.")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    create = subparsers.add_parser("create", help="Create a diagnostic context, or reuse only an active matching one.")
    add_common(create)
    create.add_argument("--input", required=True, help="Diagnostic command, manifest, grid spec, or pack path.")
    create.add_argument("--diagnostic-kind", choices=sorted(DIAGNOSTIC_KINDS))
    create.add_argument("--claim-relevance", choices=sorted(CLAIM_RELEVANCE))
    create.add_argument("--fresh", action="store_true", help="Force a new context even if input_hash matches a terminal prior session.")
    create.set_defaults(func=create_session)

    resume_explicit = subparsers.add_parser("resume", help="Explicitly resume an existing diagnostic context by matching input_hash.")
    add_common(resume_explicit)
    resume_explicit.add_argument("--input", required=True, help="Diagnostic command, manifest, grid spec, or pack path.")
    resume_explicit.set_defaults(func=resume_session)

    status = subparsers.add_parser("status", help="Read a diagnostic context by id.")
    add_common(status)
    status.add_argument("--diagnostic-id", required=True)
    status.set_defaults(func=status_session)

    resume = subparsers.add_parser("validate-resume", help="Compatibility alias for resume; approve only when input_hash matches.")
    add_common(resume)
    resume.add_argument("--input", required=True, help="Diagnostic command, manifest, grid spec, or pack path.")
    resume.set_defaults(func=validate_resume)

    run = subparsers.add_parser("update-run", help="Record run id and exact result paths.")
    add_common(run)
    run.add_argument("--diagnostic-id", required=True)
    run.add_argument("--run-id", required=True)
    run.add_argument("--result-path", action="append", default=[], help="Result file or directory; repeatable.")
    run.set_defaults(func=update_run)

    audit = subparsers.add_parser("update-audit", help="Record structured G12 audit interpretation.")
    add_common(audit)
    audit.add_argument("--diagnostic-id", required=True)
    audit.add_argument("--verdict", required=True, choices=sorted(AUDIT_VERDICTS))
    audit.add_argument("--regime-preserved", required=True, choices=sorted(REGIME_VALUES))
    audit.add_argument("--mechanism-rejected", required=True, type=parse_bool)
    audit.set_defaults(func=update_audit)

    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    try:
        payload = args.func(args)
    except (DiagnosticSessionError, OSError) as exc:
        payload = {"ok": False, "status": "error", "message": str(exc)}
        emit(payload, getattr(args, "json", False))
        return 1
    emit(payload, args.json)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
