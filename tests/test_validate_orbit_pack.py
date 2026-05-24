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


def run_validator(project: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOLS / "validate_orbit_pack.py"), "--repo", str(project), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def copy_fixture(test_case: unittest.TestCase) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="orbit-pack-validator-"))
    test_case.addCleanup(shutil.rmtree, tmp)
    target = tmp / "project"
    shutil.copytree(FIXTURE, target)
    return target


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class ValidateOrbitPackTest(unittest.TestCase):
    def test_experiment_pack_missing_formal_diagnostic_command_fails(self):
        project = copy_fixture(self)
        pack_path = project / "experiment" / "experiment_pack.json"
        pack = load_json(pack_path)
        diagnostic = pack["formal_diagnostics"][0]
        diagnostic["command"] = ""
        diagnostic.pop("manifest", None)
        diagnostic.pop("manifest_path", None)
        diagnostic.pop("grid_spec", None)
        write_json(pack_path, pack)

        result = run_validator(project, "--pack", "experiment_pack")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("must include command, manifest, manifest_path, or grid_spec", result.stdout)

    def test_experiment_pack_duplicate_formal_diagnostic_id_fails(self):
        project = copy_fixture(self)
        pack_path = project / "experiment" / "experiment_pack.json"
        pack = load_json(pack_path)
        pack["formal_diagnostics"].append(dict(pack["formal_diagnostics"][0]))
        write_json(pack_path, pack)

        result = run_validator(project, "--pack", "experiment_pack")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate formal diagnostic id", result.stdout)

    def test_experiment_pack_rejects_probe_as_formal_diagnostic(self):
        project = copy_fixture(self)
        pack_path = project / "experiment" / "experiment_pack.json"
        pack = load_json(pack_path)
        diagnostic = pack["formal_diagnostics"][0]
        diagnostic["id"] = pack["probes"][0]["id"]
        diagnostic["command"] = "experiment/PROBE_REPORT.md"
        write_json(pack_path, pack)

        result = run_validator(project, "--pack", "experiment_pack")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("reuses a probe id", result.stdout)
        self.assertIn("STOP B probe artifact", result.stdout)

    def test_duplicate_claim_id_fails(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        duplicate = dict(ledger["claims"][0])
        ledger["claims"].append(duplicate)
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate claim id", result.stdout)

    def test_unsupported_allowed_claim_fails(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"][0]["status"] = "unsupported"
        ledger["claims"][0]["paper_use"] = "allowed"
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("unsupported claim", result.stdout)
        self.assertIn("paper_use='allowed'", result.stdout)

    def test_ready_claim_ledger_missing_codex_review_fails(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger.pop("codex_review", None)
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("ready claim ledger must record Codex review", result.stdout)

    def test_ready_claim_ledger_pending_codex_review_fails(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["codex_review"] = "pending"
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("pending", result.stdout)
        self.assertIn("cannot satisfy STOP C approval", result.stdout)

    def test_ready_claim_ledger_degraded_codex_review_fails(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["codex_review"] = "degraded"
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("degraded", result.stdout)
        self.assertIn("cannot satisfy STOP C approval", result.stdout)

    def test_ready_claim_ledger_non_gating_fails(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["gating"] = False
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("non-gating claim ledger", result.stdout)

    def test_negative_original_hypothesis_do_not_claim_passes(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"] = [
            {
                "id": "H0",
                "statement": "The original hypothesis is unsupported.",
                "claim_role": "original_hypothesis",
                "status": "unsupported",
                "paper_use": "do_not_claim",
                "evidence_refs": ["results/diag_fixture/metrics.json"],
                "controls": ["control_baseline"],
                "scope": "Golden fixture only.",
                "limitations": ["Discuss only as an unsupported hypothesis."],
                "forbidden_overclaims": ["Do not claim support for H0."],
                "allowed_paper_sections": ["limitations"],
            },
            {
                "id": "N1",
                "statement": "The diagnostic supports a bounded negative result.",
                "claim_role": "negative_result_claim",
                "status": "supported",
                "paper_use": "allowed",
                "evidence_refs": ["results/diag_fixture/metrics.json"],
                "controls": ["control_baseline"],
                "scope": "Golden fixture only.",
                "limitations": ["Fixture only."],
                "forbidden_overclaims": ["Do not generalize."],
                "allowed_paper_sections": ["results", "limitations"],
            },
        ]
        write_json(ledger_path, ledger)

        result = run_validator(project, "--pack", "claim_ledger")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_verified_figure_missing_output_warns(self):
        project = copy_fixture(self)
        manifest_path = project / "figures" / "figure_manifest.json"
        manifest = load_json(manifest_path)
        manifest["figures"][0]["output"] = "figures/missing_fixture_metric.pdf"
        write_json(manifest_path, manifest)

        result = run_validator(project, "--pack", "figure_manifest")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("[warn] figure_manifest", result.stdout)
        self.assertIn("output path does not exist", result.stdout)

    def test_duplicate_figure_id_fails(self):
        project = copy_fixture(self)
        manifest_path = project / "figures" / "figure_manifest.json"
        manifest = load_json(manifest_path)
        manifest["figures"].append(dict(manifest["figures"][0]))
        write_json(manifest_path, manifest)

        result = run_validator(project, "--pack", "figure_manifest")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate figure id", result.stdout)

    def test_duplicate_citation_key_fails(self):
        project = copy_fixture(self)
        cache_path = project / "references" / "citation_cache.json"
        cache = load_json(cache_path)
        cache["citations"].append(dict(cache["citations"][0]))
        write_json(cache_path, cache)

        result = run_validator(project, "--pack", "citation_cache")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("duplicate citation key", result.stdout)

    def test_verified_citation_missing_source_fails(self):
        project = copy_fixture(self)
        cache_path = project / "references" / "citation_cache.json"
        cache = load_json(cache_path)
        cache["citations"][0]["source"] = ""
        write_json(cache_path, cache)

        result = run_validator(project, "--pack", "citation_cache")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("verified citation", result.stdout)
        self.assertIn("must include a source", result.stdout)

    def test_ready_paper_package_with_unverified_citation_fails(self):
        project = copy_fixture(self)
        cache_path = project / "references" / "citation_cache.json"
        cache = load_json(cache_path)
        cache["citations"][0]["verified"] = False
        write_json(cache_path, cache)

        result = run_validator(project, "--pack", "paper_package")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("referenced citation key 'fixture2026' is not verified", result.stdout)

    def test_ready_paper_package_with_missing_figure_id_fails(self):
        project = copy_fixture(self)
        package_path = project / "paper" / "paper_package.json"
        package = load_json(package_path)
        package["figure_refs"] = ["fig:missing"]
        write_json(package_path, package)

        result = run_validator(project, "--pack", "paper_package")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("referenced figure id 'fig:missing' is missing", result.stdout)


if __name__ == "__main__":
    unittest.main()
