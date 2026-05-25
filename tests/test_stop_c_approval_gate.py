import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SKILLS = ROOT / "skills"
FIXTURE = ROOT / "tests" / "fixtures" / "golden_minimal_project"
sys.path.insert(0, str(TOOLS))

from check_stop_c_approval import (  # noqa: E402
    HUMAN_VERDICTS,
    RED_TEAM_VERDICTS,
    evaluate_stop_c_approval,
    parse_final_verdict,
)


def run_tool(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


def copy_fixture(test_case: unittest.TestCase) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="orbit-stop-c-"))
    test_case.addCleanup(shutil.rmtree, tmp)
    target = tmp / "project"
    shutil.copytree(FIXTURE, target)
    return target


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def approval(project: Path, **kwargs) -> dict:
    return evaluate_stop_c_approval(project, "claims/claim_ledger.json", **kwargs)


class StopCApprovalGateTest(unittest.TestCase):
    def test_paper_from_claims_mentions_human_decision_note(self):
        text = (SKILLS / "paper-from-claims" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("HUMAN_DECISION_NOTE.md", text)
        self.assertIn("final verdict is `PROCEED`", text)

    def test_paper_from_claims_mentions_ready_for_paper(self):
        text = (SKILLS / "paper-from-claims" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("READY_FOR_PAPER", text)
        self.assertIn("RED_TEAM_REVIEW.md", text)

    def test_submission_ready_package_requires_human_proceed(self):
        project = copy_fixture(self)
        (project / "orbit-research" / "HUMAN_DECISION_NOTE.md").unlink()

        result = run_tool(str(TOOLS / "validate_orbit_pack.py"), "--repo", str(project), "--all")

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("STOP C approval required", result.stdout)
        self.assertIn("HUMAN_DECISION_NOTE.md", result.stdout)

    def test_paper_draft_remains_allowed_without_stop_c_approval(self):
        text = (SKILLS / "paper-draft" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Do not require `claims/claim_ledger.json`, `RED_TEAM_REVIEW.md`, or", text)
        self.assertIn("labeled draft / unaudited", text)
        self.assertNotIn("python tools/check_stop_c_approval.py", text)

    def test_stop_c_helper_blocks_missing_human_decision(self):
        project = copy_fixture(self)
        (project / "orbit-research" / "HUMAN_DECISION_NOTE.md").unlink()

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("missing orbit-research/HUMAN_DECISION_NOTE.md", "\n".join(result["errors"]))

    def test_cli_stop_c_helper_smoke(self):
        project = copy_fixture(self)
        (project / "orbit-research" / "HUMAN_DECISION_NOTE.md").unlink()

        cli = run_tool(
            str(TOOLS / "check_stop_c_approval.py"),
            "--repo",
            str(project),
            "--claim-ledger",
            "claims/claim_ledger.json",
        )

        self.assertEqual(cli.returncode, 1, cli.stdout + cli.stderr)
        self.assertIn("STOP C approval: blocked", cli.stdout)
        self.assertIn("missing orbit-research/HUMAN_DECISION_NOTE.md", cli.stdout)

    def test_stop_c_helper_accepts_golden_fixture(self):
        payload = approval(FIXTURE)
        self.assertEqual(payload["status"], "approved")
        self.assertEqual(payload["red_team_verdict"], "READY_FOR_PAPER")
        self.assertEqual(payload["human_decision_verdict"], "PROCEED")

    def test_stop_c_helper_blocks_draft_claim_ledger(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["status"] = "draft"
        write_json(ledger_path, ledger)

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("claim ledger must be 'ready'", "\n".join(result["errors"]))

    def test_stop_c_helper_blocks_pending_codex_review(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["codex_review"] = "pending"
        write_json(ledger_path, ledger)

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        errors = "\n".join(result["errors"])
        self.assertIn("pending", errors)
        self.assertIn("cannot satisfy STOP C approval", errors)

    def test_stop_c_helper_blocks_degraded_codex_review(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["codex_review"] = "degraded"
        write_json(ledger_path, ledger)

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        errors = "\n".join(result["errors"])
        self.assertIn("degraded", errors)
        self.assertIn("cannot satisfy STOP C approval", errors)

    def test_stop_c_helper_blocks_non_gating_ledger(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["gating"] = False
        write_json(ledger_path, ledger)

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("non-gating claim ledger", "\n".join(result["errors"]))

    def test_stop_c_helper_accepts_markdown_wrapped_verdicts(self):
        project = copy_fixture(self)
        red_team = project / "orbit-research" / "diagnostics" / "diag_fixture" / "RED_TEAM_REVIEW.md"
        human = project / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        red_team.write_text(
            "# Red-Team Review\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Final verdict: **READY_FOR_PAPER**\n",
            encoding="utf-8",
        )
        human.write_text(
            "# Human Decision Note\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Final decision: `PROCEED`\n",
            encoding="utf-8",
        )

        payload = approval(project)
        self.assertEqual(payload["red_team_verdict"], "READY_FOR_PAPER")
        self.assertEqual(payload["human_decision_verdict"], "PROCEED")

    def test_stop_c_helper_rejects_human_decision_template(self):
        project = copy_fixture(self)
        human = project / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# HUMAN_DECISION_NOTE\n\n"
            "Diagnostic ID: diag_fixture\n"
            "Claim ledger hash: ledger_fixture_hash\n\n"
            "Allowed final decision tokens:\n"
            "- PROCEED\n"
            "- FIX_FIRST\n"
            "- REDESIGN_DIAGNOSTIC\n"
            "- REFRAME_CLAIM\n"
            "- ARCHIVE\n"
            "- SCALE_UP\n\n"
            "Final decision: <ONE_TOKEN>\n",
            encoding="utf-8",
        )

        payload = approval(project)

        self.assertEqual(payload["status"], "blocked")
        self.assertNotEqual(payload["human_decision_verdict"], "PROCEED")

    def test_stop_c_helper_rejects_red_team_template(self):
        project = copy_fixture(self)
        red_team = project / "orbit-research" / "diagnostics" / "diag_fixture" / "RED_TEAM_REVIEW.md"
        red_team.write_text(
            "# RED_TEAM_REVIEW\n\n"
            "Diagnostic ID: diag_fixture\n"
            "Claim ledger hash: ledger_fixture_hash\n\n"
            "Allowed final verdict tokens:\n"
            "- READY_FOR_PAPER\n"
            "- REQUIRES_FIXES\n"
            "- REDESIGN_REQUIRED\n"
            "- HUMAN_DECISION_REQUIRED\n\n"
            "Final verdict: <ONE_TOKEN>\n",
            encoding="utf-8",
        )

        payload = approval(project)

        self.assertEqual(payload["status"], "blocked")
        self.assertIsNone(payload["red_team_verdict"])

    def test_verdict_parser_ignores_bullet_list_tokens(self):
        self.assertIsNone(parse_final_verdict("- PROCEED\n", HUMAN_VERDICTS))
        self.assertIsNone(parse_final_verdict("- READY_FOR_PAPER\n", RED_TEAM_VERDICTS))

    def test_stop_c_helper_rejects_red_team_candidate_list(self):
        project = copy_fixture(self)
        red_team = project / "orbit-research" / "diagnostics" / "diag_fixture" / "RED_TEAM_REVIEW.md"
        red_team.write_text(
            "# Red-Team Review\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Final verdict: READY_FOR_PAPER | REQUIRES_FIXES\n",
            encoding="utf-8",
        )

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("RED_TEAM_REVIEW final verdict must be READY_FOR_PAPER", "\n".join(result["errors"]))

    def test_stop_c_helper_rejects_human_decision_candidate_list(self):
        project = copy_fixture(self)
        human = project / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# Human Decision Note\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Decision: PROCEED | STOP\n",
            encoding="utf-8",
        )

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("HUMAN_DECISION_NOTE final verdict must be PROCEED", "\n".join(result["errors"]))

    def test_stop_c_helper_blocks_identity_mismatch_by_default(self):
        project = copy_fixture(self)
        human = project / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# Human Decision Note\n\nDiagnostic ID: other_diag\nClaim ledger hash: other_hash\n\n"
            "Final verdict: PROCEED\n",
            encoding="utf-8",
        )

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        errors = "\n".join(result["errors"])
        self.assertIn("does not reference diagnostic_id diag_fixture", errors)
        self.assertIn("does not reference ledger_hash ledger_fixture_hash", errors)

    def test_regression_per_diagnostic_red_team_requires_fixes_must_not_fallback_to_ready_legacy(self):
        project = copy_fixture(self)
        per_diagnostic_review = (
            project
            / "orbit-research"
            / "diagnostics"
            / "diag_fixture"
            / "RED_TEAM_REVIEW.md"
        )
        legacy_review = project / "orbit-research" / "RED_TEAM_REVIEW.md"
        per_diagnostic_review.write_text(
            "# Red-Team Review\n\n"
            "Diagnostic ID: diag_fixture\n"
            "Claim ledger hash: ledger_fixture_hash\n\n"
            "Final verdict: REQUIRES_FIXES\n",
            encoding="utf-8",
        )
        legacy_review.write_text(
            "# Legacy Red-Team Review\n\n"
            "Diagnostic ID: diag_fixture\n"
            "Claim ledger hash: ledger_fixture_hash\n\n"
            "Final verdict: READY_FOR_PAPER\n",
            encoding="utf-8",
        )

        payload = approval(project)
        self.assertEqual(payload["status"], "blocked")
        self.assertEqual(
            payload["red_team_review"],
            "orbit-research/diagnostics/diag_fixture/RED_TEAM_REVIEW.md",
        )
        self.assertIn("REQUIRES_FIXES", "\n".join(payload["errors"]))

    def test_regression_unsupported_allowed_main_claim_blocks_stop_c_approval(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger["claims"][0]["claim_role"] = "main_claim"
        ledger["claims"][0]["status"] = "unsupported"
        ledger["claims"][0]["paper_use"] = "allowed"
        write_json(ledger_path, ledger)

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        errors = "\n".join(result["errors"])
        self.assertIn("unsupported claim", errors)
        self.assertIn("paper_use", errors)

    def test_stop_c_helper_blocks_ready_ledger_without_identity(self):
        project = copy_fixture(self)
        ledger_path = project / "claims" / "claim_ledger.json"
        ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
        ledger.pop("diagnostic_id", None)
        ledger.pop("ledger_hash", None)
        write_json(ledger_path, ledger)

        result = approval(project)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("diagnostic_id or ledger_hash", "\n".join(result["errors"]))

    def test_stop_c_helper_can_allow_unmatched_legacy_approval(self):
        project = copy_fixture(self)
        human = project / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# Human Decision Note\n\nLegacy approval note.\n\nFinal verdict: PROCEED\n",
            encoding="utf-8",
        )

        payload = approval(project, allow_unmatched_legacy_approval=True)
        self.assertEqual(payload["status"], "approved")
        self.assertTrue(payload["warnings"])


if __name__ == "__main__":
    unittest.main()
