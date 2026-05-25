import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "diagnostic_session.py"
SKILLS = ROOT / "skills"
sys.path.insert(0, str(ROOT / "tools"))

from diagnostic_session import (  # noqa: E402
    DiagnosticSessionError,
    create_session,
    resume_session,
    update_audit,
    update_run,
    validate_resume,
)


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def run_json(*args: str) -> dict:
    result = run_tool(*args, "--json")
    if result.returncode != 0:
        raise AssertionError(result.stdout + result.stderr)
    return json.loads(result.stdout)


def args(**kwargs):
    return SimpleNamespace(**kwargs)


def create(repo: Path, input_value: str, fresh: bool = False) -> dict:
    return create_session(
        args(
            repo=str(repo),
            input=input_value,
            diagnostic_kind=None,
            claim_relevance=None,
            fresh=fresh,
        )
    )


def resume(repo: Path, input_value: str) -> dict:
    return resume_session(args(repo=str(repo), input=input_value))


def validate_resume_for(repo: Path, input_value: str) -> dict:
    return validate_resume(args(repo=str(repo), input=input_value))


def update_run_for(repo: Path, diagnostic_id: str, run_id: str, result_paths: list[str]) -> dict:
    return update_run(
        args(
            repo=str(repo),
            diagnostic_id=diagnostic_id,
            run_id=run_id,
            result_path=result_paths,
        )
    )


def update_audit_for(
    repo: Path,
    diagnostic_id: str,
    verdict: str,
    regime_preserved: str,
    mechanism_rejected: bool,
) -> dict:
    return update_audit(
        args(
            repo=str(repo),
            diagnostic_id=diagnostic_id,
            verdict=verdict,
            regime_preserved=regime_preserved,
            mechanism_rejected=mechanism_rejected,
        )
    )


def set_context_status(repo: Path, payload: dict, status: str) -> None:
    path = repo / payload["context_path"]
    context = json.loads(path.read_text(encoding="utf-8"))
    context["status"] = status
    path.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class DiagnosticSessionTest(unittest.TestCase):
    def test_create_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            payload = create(repo, "python train.py --smoke")

            self.assertTrue(payload["created"])
            context_path = repo / payload["context_path"]
            self.assertTrue(context_path.exists())
            context = json.loads(context_path.read_text(encoding="utf-8"))
            self.assertEqual(context["diagnostic_id"], payload["diagnostic_id"])
            self.assertEqual(context["diagnostic_kind"], "implementation_smoke")
            self.assertEqual(context["claim_relevance"], "none")
            self.assertEqual(context["status"], "initialized")
            self.assertEqual(context["audit"]["regime_preserved"], "unknown")

    def test_same_input_has_same_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = create(repo, "python train.py --smoke")
            second = create(repo, "  python   train.py   --smoke ")

            self.assertEqual(first["input_hash"], second["input_hash"])
            self.assertFalse(second["created"])
            self.assertEqual(second["status"], "existing_active")
            self.assertEqual(first["diagnostic_id"], second["diagnostic_id"])

    def test_same_input_after_stop_c_ready_is_not_silently_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = create(repo, "python train.py --main")
            set_context_status(repo, created, "stop_c_ready")

            payload = create(repo, "python train.py --main")
            self.assertFalse(payload["ok"])
            self.assertFalse(payload["created"])
            self.assertEqual(payload["status"], "terminal_session_exists")
            self.assertEqual(payload["diagnostic_id"], created["diagnostic_id"])
            self.assertEqual(payload["context_status"], "stop_c_ready")
            self.assertIn("--fresh", payload["message"])

    def test_fresh_creates_new_session_after_terminal_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = create(repo, "python train.py --main")
            set_context_status(repo, first, "stop_c_ready")

            fresh = create(repo, "python train.py --main", fresh=True)

            self.assertTrue(fresh["created"])
            self.assertEqual(first["input_hash"], fresh["input_hash"])
            self.assertNotEqual(first["diagnostic_id"], fresh["diagnostic_id"])

    def test_different_input_has_different_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = create(repo, "python train.py --smoke")
            second = create(repo, "python train.py --ablation")

            self.assertNotEqual(first["input_hash"], second["input_hash"])

    def test_validate_resume_refuses_mismatched_active_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            create(repo, "python train.py --smoke")

            payload = validate_resume_for(repo, "python train.py --different")
            self.assertEqual(payload["status"], "blocked_mismatched_active")
            self.assertIn("active_diagnostics", payload)

    def test_resume_requires_matching_input_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = create(repo, "python train.py --main")
            resumed = resume(repo, "python train.py --main")

            self.assertEqual(resumed["status"], "resume_ok")
            self.assertEqual(resumed["diagnostic_id"], created["diagnostic_id"])

            payload = resume(repo, "python train.py --different")
            self.assertEqual(payload["status"], "blocked_mismatched_active")

    def test_update_run_records_run_id_and_result_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = create(repo, "python train.py --smoke")

            updated = update_run_for(repo, created["diagnostic_id"], "run_001", ["results/diag_main"])

            context = updated["context"]
            self.assertEqual(context["run_id"], "run_001")
            self.assertEqual(context["result_paths"], ["results/diag_main"])
            self.assertEqual(context["status"], "run_complete")

    def test_update_audit_records_structured_g12_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = create(repo, "python train.py --smoke")

            updated = update_audit_for(
                repo,
                created["diagnostic_id"],
                "REDESIGN_EXPERIMENT",
                "false",
                False,
            )

            audit = updated["context"]["audit"]
            self.assertEqual(audit["verdict"], "REDESIGN_EXPERIMENT")
            self.assertEqual(audit["regime_preserved"], "false")
            self.assertFalse(audit["mechanism_rejected"])
            self.assertEqual(updated["context"]["status"], "blocked")

    def test_update_audit_rejects_mechanism_rejection_when_regime_not_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = create(repo, "python train.py --smoke")

            with self.assertRaises(DiagnosticSessionError) as caught:
                update_audit_for(
                    repo,
                    created["diagnostic_id"],
                    "REDESIGN_EXPERIMENT",
                    "false",
                    True,
                )
            self.assertIn("regime_preserved=false", str(caught.exception))

    def test_cli_create_json_smoke(self):
        with tempfile.TemporaryDirectory() as tmp:
            payload = run_json("create", "--repo", tmp, "--input", "python train.py --smoke")

            self.assertTrue(payload["created"])
            self.assertEqual(payload["status"], "created")

    def test_diagnostic_to_review_references_session_helper(self):
        text = (SKILLS / "diagnostic-to-review" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("tools/diagnostic_session.py", text)
        self.assertIn("validate-resume", text)


if __name__ == "__main__":
    unittest.main()
