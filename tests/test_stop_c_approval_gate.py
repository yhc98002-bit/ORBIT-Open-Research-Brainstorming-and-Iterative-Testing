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

        result = run_tool(
            str(TOOLS / "check_stop_c_approval.py"),
            "--repo",
            str(project),
            "--claim-ledger",
            "claims/claim_ledger.json",
        )

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("STOP C approval: blocked", result.stdout)
        self.assertIn("missing orbit-research/HUMAN_DECISION_NOTE.md", result.stdout)

    def test_stop_c_helper_accepts_golden_fixture(self):
        result = run_tool(
            str(TOOLS / "check_stop_c_approval.py"),
            "--repo",
            str(FIXTURE),
            "--claim-ledger",
            "claims/claim_ledger.json",
            "--json",
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "approved")
        self.assertEqual(payload["red_team_verdict"], "READY_FOR_PAPER")
        self.assertEqual(payload["human_decision_verdict"], "PROCEED")


if __name__ == "__main__":
    unittest.main()
