import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
FIXTURE = ROOT / "tests" / "fixtures" / "golden_minimal_project"


def run_tool(*args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=check,
    )


def copy_fixture(test_case: unittest.TestCase) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="orbit-golden-"))
    test_case.addCleanup(shutil.rmtree, tmp)
    target = tmp / "project"
    shutil.copytree(FIXTURE, target)
    return target


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class GoldenOrbitWorkflowTest(unittest.TestCase):
    def test_golden_fixture_validates_all_packs(self):
        result = run_tool(str(TOOLS / "validate_orbit_pack.py"), "--repo", str(FIXTURE), "--all")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Summary: 6 ok, 0 warning, 0 error", result.stdout)

    def test_golden_fixture_status_reports_stop_d_and_safe_next(self):
        result = run_tool(str(TOOLS / "orbit_status.py"), "--repo", str(FIXTURE), "--pretty")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Current stop: STOP_D", result.stdout)
        self.assertIn("Status: completed", result.stdout)
        self.assertIn("Current skill: submission-package", result.stdout)
        self.assertIn("Safe next command:\n  none", result.stdout)

    def test_claim_ledger_validator_rejects_ready_unsupported_claim(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"][0]["claim_role"] = "main_claim"
        ledger["claims"][0]["status"] = "unsupported"
        ledger["claims"][0]["paper_use"] = "allowed"
        write_json(ledger_path, ledger)

        result = run_tool(
            str(TOOLS / "validate_orbit_pack.py"),
            "--repo",
            str(project),
            "--pack",
            "claim_ledger",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unsupported claim", result.stdout)
        self.assertIn("paper_use='allowed'", result.stdout)

    def test_claim_ledger_allows_unsupported_original_hypothesis_with_negative_result(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"] = [
            {
                "id": "H0",
                "statement": "The original hypothesis is unsupported in this diagnostic.",
                "claim_role": "original_hypothesis",
                "status": "unsupported",
                "paper_use": "do_not_claim",
                "evidence_refs": ["results/diag_fixture/metrics.json"],
                "controls": ["control_baseline"],
                "scope": "Golden fixture only.",
                "limitations": [
                    "The unsupported original hypothesis may be discussed only as context."
                ],
                "forbidden_overclaims": [
                    "Do not claim the original hypothesis was supported."
                ],
                "allowed_paper_sections": ["limitations"],
            },
            {
                "id": "N1",
                "statement": "The diagnostic supports a bounded negative-result claim.",
                "claim_role": "negative_result_claim",
                "status": "supported",
                "paper_use": "allowed",
                "evidence_refs": ["results/diag_fixture/metrics.json"],
                "controls": ["control_baseline"],
                "scope": "Golden fixture only.",
                "limitations": ["Negative-result fixture only."],
                "forbidden_overclaims": [
                    "Do not generalize beyond the fixture."
                ],
                "allowed_paper_sections": ["results", "limitations"],
            },
        ]
        write_json(ledger_path, ledger)

        result = run_tool(
            str(TOOLS / "validate_orbit_pack.py"),
            "--repo",
            str(project),
            "--pack",
            "claim_ledger",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_figure_manifest_validator_rejects_missing_output_and_status(self):
        project = copy_fixture(self)
        manifest_path = project / "figures" / "figure_manifest.json"
        manifest = load_json(manifest_path)
        manifest["figures"][0].pop("output")
        manifest["figures"][0].pop("status")
        write_json(manifest_path, manifest)

        result = run_tool(
            str(TOOLS / "validate_orbit_pack.py"),
            "--repo",
            str(project),
            "--pack",
            "figure_manifest",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("missing required key output", result.stdout)
        self.assertIn("missing required key status", result.stdout)

    def test_submission_ready_package_rejects_unverified_citation(self):
        project = copy_fixture(self)
        cache_path = project / "references" / "citation_cache.json"
        cache = load_json(cache_path)
        cache["citations"][0]["verified"] = False
        write_json(cache_path, cache)

        result = run_tool(str(TOOLS / "validate_orbit_pack.py"), "--repo", str(project), "--all")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unverified citation", result.stdout)
        self.assertIn("fixture2026", result.stdout)

    def test_ready_paper_package_rejects_unsupported_allowed_claim(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"][0]["claim_role"] = "main_claim"
        ledger["claims"][0]["status"] = "unsupported"
        ledger["claims"][0]["paper_use"] = "allowed"
        write_json(ledger_path, ledger)

        result = run_tool(
            str(TOOLS / "validate_orbit_pack.py"),
            "--repo",
            str(project),
            "--pack",
            "paper_package",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("paper_package", result.stdout)
        self.assertIn("unsupported claim", result.stdout)

    def test_mirror_checker_report_mode_outputs_json(self):
        result = run_tool(str(TOOLS / "check_skill_mirror.py"), "--repo", str(ROOT), "--json")
        self.assertIn(result.returncode, {0, 1}, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("summary", payload)
        self.assertIn("entries", payload)


if __name__ == "__main__":
    unittest.main()
