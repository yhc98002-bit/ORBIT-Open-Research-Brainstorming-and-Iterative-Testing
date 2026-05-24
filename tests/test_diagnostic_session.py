import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "diagnostic_session.py"
SKILLS = ROOT / "skills"


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


class DiagnosticSessionTest(unittest.TestCase):
    def test_create_context(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            payload = run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")

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
            first = run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")
            second = run_json("create", "--repo", str(repo), "--input", "  python   train.py   --smoke ")

            self.assertEqual(first["input_hash"], second["input_hash"])
            self.assertFalse(second["created"])

    def test_different_input_has_different_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            first = run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")
            second = run_json("create", "--repo", str(repo), "--input", "python train.py --ablation")

            self.assertNotEqual(first["input_hash"], second["input_hash"])

    def test_validate_resume_refuses_mismatched_active_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")

            result = run_tool(
                "validate-resume",
                "--repo",
                str(repo),
                "--input",
                "python train.py --different",
                "--json",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "blocked_mismatched_active")
            self.assertIn("active_diagnostics", payload)

    def test_update_run_records_run_id_and_result_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")

            updated = run_json(
                "update-run",
                "--repo",
                str(repo),
                "--diagnostic-id",
                created["diagnostic_id"],
                "--run-id",
                "run_001",
                "--result-path",
                "results/diag_main",
            )

            context = updated["context"]
            self.assertEqual(context["run_id"], "run_001")
            self.assertEqual(context["result_paths"], ["results/diag_main"])
            self.assertEqual(context["status"], "run_complete")

    def test_update_audit_records_structured_g12_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")

            updated = run_json(
                "update-audit",
                "--repo",
                str(repo),
                "--diagnostic-id",
                created["diagnostic_id"],
                "--verdict",
                "REDESIGN_EXPERIMENT",
                "--regime-preserved",
                "false",
                "--mechanism-rejected",
                "false",
            )

            audit = updated["context"]["audit"]
            self.assertEqual(audit["verdict"], "REDESIGN_EXPERIMENT")
            self.assertEqual(audit["regime_preserved"], "false")
            self.assertFalse(audit["mechanism_rejected"])
            self.assertEqual(updated["context"]["status"], "blocked")

    def test_update_audit_rejects_mechanism_rejection_when_regime_not_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            created = run_json("create", "--repo", str(repo), "--input", "python train.py --smoke")

            result = run_tool(
                "update-audit",
                "--repo",
                str(repo),
                "--diagnostic-id",
                created["diagnostic_id"],
                "--verdict",
                "REDESIGN_EXPERIMENT",
                "--regime-preserved",
                "false",
                "--mechanism-rejected",
                "true",
                "--json",
            )

            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "error")
            self.assertIn("regime_preserved=false", payload["message"])

    def test_diagnostic_to_review_references_session_helper(self):
        text = (SKILLS / "diagnostic-to-review" / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("tools/diagnostic_session.py", text)
        self.assertIn("validate-resume", text)


if __name__ == "__main__":
    unittest.main()
