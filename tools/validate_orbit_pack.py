#!/usr/bin/env python3
"""Validate ORBIT machine-readable packs with a small stdlib schema checker."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

try:
    from orbit_pack import PACK_SPECS, get_pack_spec, pack_names, pack_path, schema_path
except ImportError:  # pragma: no cover - used when imported as tools.validate_orbit_pack
    from tools.orbit_pack import PACK_SPECS, get_pack_spec, pack_names, pack_path, schema_path


TOOL_REPO_ROOT = Path(__file__).resolve().parents[1]

JSON_TYPE_NAMES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
}


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate ORBIT pack JSON files.")
    parser.add_argument("--repo", default=".", help="Repository root.")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--all", action="store_true", help="Validate every canonical pack path.")
    selection.add_argument("--pack", choices=pack_names(), help="Validate one named pack.")
    selection.add_argument("--path", help="Validate a specific pack file path.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable validation report.")
    return parser.parse_args(argv)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def type_matches(expected: str, instance: Any) -> bool:
    if expected == "null":
        return instance is None
    if expected == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if expected == "number":
        return (isinstance(instance, int) or isinstance(instance, float)) and not isinstance(instance, bool)
    py_type = JSON_TYPE_NAMES.get(expected)
    if py_type is None:
        return True
    return isinstance(instance, py_type)


def validate_schema_subset(schema: Mapping[str, Any], instance: Any, location: str = "$") -> List[str]:
    errors: List[str] = []

    if "const" in schema and instance != schema["const"]:
        errors.append("%s: expected constant %r, got %r" % (location, schema["const"], instance))

    if "enum" in schema and instance not in schema["enum"]:
        errors.append("%s: expected one of %r, got %r" % (location, schema["enum"], instance))

    expected_type = schema.get("type")
    if expected_type is not None:
        expected_types = expected_type if isinstance(expected_type, list) else [expected_type]
        if not any(type_matches(value, instance) for value in expected_types):
            errors.append("%s: expected type %s, got %s" % (location, expected_types, type(instance).__name__))
            return errors

    if isinstance(instance, str) and "minLength" in schema:
        if len(instance) < int(schema["minLength"]):
            errors.append("%s: expected minLength %s" % (location, schema["minLength"]))

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append("%s: missing required key %s" % (location, key))
        properties = schema.get("properties", {})
        if isinstance(properties, dict):
            for key, child_schema in properties.items():
                if key in instance and isinstance(child_schema, dict):
                    errors.extend(validate_schema_subset(child_schema, instance[key], "%s.%s" % (location, key)))

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(validate_schema_subset(item_schema, item, "%s[%d]" % (location, index)))

    return errors


def validate_updated_at(instance: Mapping[str, Any]) -> List[str]:
    updated_at = instance.get("updated_at")
    if not isinstance(updated_at, str):
        return ["$.updated_at: expected ISO-8601 string"]
    value = updated_at.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(value)
    except ValueError:
        return ["$.updated_at: invalid ISO-8601 datetime %r" % updated_at]
    return []


def validate_pack_semantics(name: str, instance: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []

    if name == "claim_ledger" and instance.get("status") == "ready":
        claims = instance.get("claims")
        if isinstance(claims, list):
            for index, claim in enumerate(claims):
                if not isinstance(claim, dict):
                    continue
                if claim.get("status") != "unsupported":
                    continue
                claim_id = claim.get("id") or index
                errors.append(
                    "$.claims[%d].status: unsupported claim %r cannot appear in a ready claim_ledger"
                    % (index, claim_id)
                )

    return errors


def append_cross_pack_errors(repo: Path, report: Dict[str, Any]) -> None:
    paper_path = pack_path(repo, "paper_package")
    citation_path = pack_path(repo, "citation_cache")
    if not paper_path.exists() or not citation_path.exists():
        return

    paper_package = parse_json_or_none(paper_path)
    citation_cache = parse_json_or_none(citation_path)
    if not isinstance(paper_package, dict) or not isinstance(citation_cache, dict):
        return
    if paper_package.get("status") != "ready":
        return
    if not paper_package.get("citation_cache_ref"):
        return

    citations = citation_cache.get("citations")
    if not isinstance(citations, list):
        return

    errors: List[str] = []
    for index, citation in enumerate(citations):
        if not isinstance(citation, dict):
            continue
        if citation.get("verified") is True:
            continue
        key = citation.get("key") or index
        errors.append(
            "$.citations[%d].verified: unverified citation %r cannot be used when paper_package status is ready"
            % (index, key)
        )
    if not errors:
        return

    for result in report["results"]:
        if result.get("name") == "citation_cache":
            result["status"] = "error"
            result.setdefault("errors", []).extend(errors)
            return


def parse_json_or_none(path: Path) -> Optional[Any]:
    try:
        return load_json(path)
    except (OSError, json.JSONDecodeError):
        return None


def infer_pack_name(path: Path) -> Optional[str]:
    rel = path.as_posix()
    for name, spec in PACK_SPECS.items():
        if rel.endswith(spec.rel_path):
            return name
    basename = path.name
    for name, spec in PACK_SPECS.items():
        if basename == Path(spec.rel_path).name:
            return name
    return None


def relative_to_or_none(path: Path, root: Path) -> Optional[Path]:
    try:
        return path.relative_to(root)
    except ValueError:
        return None


def validate_pack_file(repo: Path, name: str, path: Path) -> Dict[str, Any]:
    spec = get_pack_spec(name)
    result = {
        "name": name,
        "path": spec.rel_path if path == repo / spec.rel_path else path.as_posix(),
        "schema": spec.schema_path,
        "status": "ok",
        "warnings": [],
        "errors": [],
    }

    project_schema_path = schema_path(repo, name)
    fallback_schema_path = schema_path(TOOL_REPO_ROOT, name)
    effective_schema_path = project_schema_path if project_schema_path.exists() else fallback_schema_path

    try:
        schema = load_json(effective_schema_path)
    except (OSError, json.JSONDecodeError) as exc:
        result["status"] = "error"
        result["errors"].append("could not load schema: %s" % exc)
        return result

    try:
        instance = load_json(path)
    except (OSError, json.JSONDecodeError) as exc:
        result["status"] = "error"
        result["errors"].append("could not load pack JSON: %s" % exc)
        return result

    errors = validate_schema_subset(schema, instance)
    if isinstance(instance, dict):
        errors.extend(validate_updated_at(instance))
        errors.extend(validate_pack_semantics(name, instance))
    else:
        errors.append("$: pack root must be a JSON object")

    if errors:
        result["status"] = "error"
        result["errors"].extend(errors)
    return result


def warning_for_missing(repo: Path, name: str) -> Dict[str, Any]:
    spec = get_pack_spec(name)
    return {
        "name": name,
        "path": spec.rel_path,
        "schema": spec.schema_path,
        "status": "warning",
        "warnings": ["missing pack; allowed during incremental migration"],
        "errors": [],
    }


def validate_selection(repo: Path, args: argparse.Namespace) -> Dict[str, Any]:
    selected: List[str]
    path_override: Optional[Path] = None

    if args.path:
        path_override = Path(args.path)
        if not path_override.is_absolute():
            path_override = repo / path_override
        inferred = infer_pack_name(relative_to_or_none(path_override, repo) or path_override)
        if not inferred:
            return {
                "results": [
                    {
                        "name": None,
                        "path": path_override.as_posix(),
                        "schema": None,
                        "status": "error",
                        "warnings": [],
                        "errors": ["could not infer pack type from path; use a canonical pack filename"],
                    }
                ]
            }
        selected = [inferred]
    elif args.pack:
        selected = [args.pack]
    else:
        selected = pack_names()

    results = []
    for name in selected:
        path = path_override if path_override is not None else pack_path(repo, name)
        if not path.exists():
            results.append(warning_for_missing(repo, name))
        else:
            results.append(validate_pack_file(repo, name, path))
    report = {"results": results}
    append_cross_pack_errors(repo, report)
    return report


def print_pretty(report: Mapping[str, Any]) -> None:
    print("ORBIT pack validation")
    for result in report["results"]:
        status = result["status"]
        prefix = {"ok": "[ok]", "warning": "[warn]", "error": "[error]"}.get(status, "[?]")
        print("%s %s: %s" % (prefix, result.get("name") or "unknown", result["path"]))
        for warning in result.get("warnings", []):
            print("  warning: %s" % warning)
        for error in result.get("errors", []):
            print("  error: %s" % error)

    ok_count = sum(1 for result in report["results"] if result["status"] == "ok")
    warning_count = sum(1 for result in report["results"] if result["status"] == "warning")
    error_count = sum(1 for result in report["results"] if result["status"] == "error")
    print("Summary: %d ok, %d warning, %d error" % (ok_count, warning_count, error_count))


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    repo = Path(args.repo).resolve()
    report = validate_selection(repo, args)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=True))
    else:
        print_pretty(report)
    return 1 if any(result["status"] == "error" for result in report["results"]) else 0


if __name__ == "__main__":
    raise SystemExit(main())
