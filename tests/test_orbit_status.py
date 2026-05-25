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
sys.path.insert(0, str(TOOLS))

from orbit_state import make_state, write_state  # noqa: E402
from orbit_status import format_pretty, get_status  # noqa: E402


def copy_fixture(test_case: unittest.TestCase) -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="orbit-status-"))
    test_case.addCleanup(shutil.rmtree, tmp)
    target = tmp / "project"
    shutil.copytree(FIXTURE, target)
    state_path = target / "orbit-research" / "ORBIT_STATE.json"
    if state_path.exists():
        state_path.unlink()
    return target


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


class OrbitStatusTest(unittest.TestCase):
    def test_empty_project_reports_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state = get_status(repo)

            self.assertEqual(state["current_stop"], "NONE")
            self.assertEqual(state["status"], "paused")
            self.assertEqual(state["pause_reason"], "ambiguous_resume")
            self.assertEqual(state["blockers"], [])
            self.assertEqual(state["safe_next_command"], '/idea-to-proposal "<research direction>"')

    def test_cli_empty_project_json_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    str(TOOLS / "orbit_status.py"),
                    "--repo",
                    str(repo),
                    "--json",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            parsed = json.loads(result.stdout)
            self.assertEqual(parsed["current_stop"], "NONE")

    def test_bad_plan_code_verdict_blocks_stop_b(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            audit = repo / "orbit-research" / "PLAN_CODE_AUDIT.md"
            audit.parent.mkdir(parents=True)
            audit.write_text("# Audit\n\nFinal verdict: CRITICAL_MISMATCH\n", encoding="utf-8")

            state = get_status(repo)
            self.assertEqual(state["current_stop"], "STOP_B")
            self.assertEqual(state["status"], "blocked")
            self.assertEqual(state["pause_reason"], "gate_failed")
            self.assertEqual(state["blockers"][0]["id"], "G11")
            self.assertIn("PLAN_CODE_AUDIT verdict CRITICAL_MISMATCH", state["blockers"][0]["message"])

            pretty = format_pretty(state)
            self.assertIn("Current stop: STOP_B", pretty)
            self.assertIn("- G11: PLAN_CODE_AUDIT verdict CRITICAL_MISMATCH", pretty)

    def test_good_plan_code_verdict_without_pack_does_not_suggest_plan_audit_as_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            audit = repo / "orbit-research" / "PLAN_CODE_AUDIT.md"
            audit.parent.mkdir(parents=True)
            audit.write_text("Verdict: MATCHES_PLAN\n", encoding="utf-8")
            legacy_exec = repo / "refine-logs" / "EXPERIMENT_PLAN_EXEC.md"
            legacy_exec.parent.mkdir(parents=True)
            legacy_exec.write_text("# Legacy exec plan\n", encoding="utf-8")

            state = get_status(repo)
            self.assertEqual(state["current_stop"], "STOP_B")
            self.assertEqual(state["current_skill"], "experiment-bridge")
            self.assertEqual(state["status"], "blocked")
            self.assertEqual(state["pause_reason"], "missing_prereq")
            self.assertEqual(state["blockers"][0]["kind"], "missing_artifact")
            self.assertEqual(state["blockers"][0]["artifact"], "experiment/experiment_pack.json")
            self.assertIn("experiment_pack.json", state["blockers"][0]["message"])
            bad_command = '/diagnostic-to-review "' + 'orbit-research/PLAN_CODE_AUDIT.md"'
            self.assertNotIn(bad_command, state["safe_next_command"])
            self.assertEqual(
                state["safe_next_command"],
                '/experiment-bridge "refine-logs/EXPERIMENT_PLAN_EXEC.md" — mode: plan-only',
            )

    def test_experiment_pack_formal_diagnostics_route_to_stop_c_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            pack_path = repo / "experiment" / "experiment_pack.json"
            pack_path.parent.mkdir(parents=True)
            pack_path.write_text(
                json.dumps(
                    {
                        "schema_version": "0.1",
                        "status": "ready",
                        "updated_at": "2026-05-23T00:00:00Z",
                        "source_markdown": [],
                        "generated_views": [],
                        "proposal_ref": "proposal/proposal_pack.json",
                        "decision_tree": [],
                        "controls": [],
                        "null_result_contract": {},
                        "component_ladder": [],
                        "algorithmic_formalization": {},
                        "plan_code_audit": {"verdict": "MATCHES_PLAN"},
                        "probes": [],
                        "formal_diagnostics": [
                            {
                                "id": "diag_main",
                                "kind": "paper_bearing_main",
                                "claim_relevance": "primary_evidence",
                                "command": "python train.py --diag main",
                                "expected_result_paths": ["results/diag_main/"],
                                "success_signal": "main diagnostic improves the primary metric",
                                "null_result_interpretation": "record unsupported hypothesis",
                                "status": "planned",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            state = get_status(repo)
            self.assertEqual(state["current_stop"], "STOP_B")
            self.assertEqual(state["status"], "paused")
            self.assertEqual(
                state["safe_next_command"],
                '/diagnostic-to-review "python train.py --diag main"',
            )
            self.assertNotIn("PLAN_CODE_AUDIT.md", state["safe_next_command"])

    def test_experiment_pack_without_formal_diagnostics_blocks(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            pack_path = repo / "experiment" / "experiment_pack.json"
            pack_path.parent.mkdir(parents=True)
            pack_path.write_text(
                json.dumps(
                    {
                        "schema_version": "0.1",
                        "status": "ready",
                        "updated_at": "2026-05-23T00:00:00Z",
                        "source_markdown": [],
                        "generated_views": [],
                        "proposal_ref": "proposal/proposal_pack.json",
                        "decision_tree": [],
                        "controls": [],
                        "null_result_contract": {},
                        "component_ladder": [],
                        "algorithmic_formalization": {},
                        "plan_code_audit": {"verdict": "MATCHES_PLAN"},
                        "probes": [],
                        "formal_diagnostics": [],
                    }
                ),
                encoding="utf-8",
            )

            state = get_status(repo)
            self.assertEqual(state["current_stop"], "STOP_B")
            self.assertEqual(state["status"], "blocked")
            self.assertEqual(state["pause_reason"], "missing_prereq")
            self.assertEqual(state["blockers"][0]["artifact"], "experiment_pack.formal_diagnostics")
            self.assertEqual(
                state["safe_next_command"],
                '/experiment-bridge "experiment/experiment_pack.json" — mode: plan-only',
            )

    def test_existing_orbit_state_is_preferred(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state = make_state(
                current_stop="STOP_A",
                current_skill="idea-to-proposal",
                current_phase="user_review",
                status="paused",
                pause_reason="stop_review",
                safe_next_command='/idea-to-proposal "topic"',
            )
            write_state(repo, state)

            loaded = get_status(repo)
            self.assertEqual(loaded["current_stop"], "STOP_A")
            self.assertEqual(loaded["current_phase"], "user_review")
            self.assertEqual(loaded["safe_next_command"], '/idea-to-proposal "topic"')

    def test_regression_stale_orbit_state_submission_safe_next_is_blocked_by_invalid_claim_ledger(self):
        repo = copy_fixture(self)
        package_path = repo / "paper" / "paper_package.json"
        if package_path.exists():
            package_path.unlink()
        ledger_path = repo / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"][0]["claim_role"] = "main_claim"
        ledger["claims"][0]["status"] = "unsupported"
        ledger["claims"][0]["paper_use"] = "allowed"
        write_json(ledger_path, ledger)
        stale_state = make_state(
            current_stop="STOP_D",
            current_skill="submission-package",
            current_phase="paper_package_ready",
            status="paused",
            pause_reason="stop_review",
            safe_next_command='/submission-package "paper/"',
        )
        write_state(repo, stale_state)

        state = get_status(repo)

        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["status"], "blocked")
        self.assertNotIn("/submission-package", state.get("safe_next_command") or "")
        self.assertTrue(
            any("unsupported claim" in blocker.get("message", "") for blocker in state.get("blockers", [])),
            state,
        )

    def test_invalid_claim_ledger_routes_to_claim_repair_not_red_team(self):
        repo = copy_fixture(self)
        package_path = repo / "paper" / "paper_package.json"
        if package_path.exists():
            package_path.unlink()
        ledger_path = repo / "claims" / "claim_ledger.json"
        ledger = load_json(ledger_path)
        ledger["claims"][0]["claim_role"] = "main_claim"
        ledger["claims"][0]["status"] = "unsupported"
        ledger["claims"][0]["paper_use"] = "allowed"
        write_json(ledger_path, ledger)

        state = get_status(repo)

        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["status"], "blocked")
        self.assertNotIn("/auto-review-loop", state.get("safe_next_command") or "")
        self.assertIn("/result-to-claim", state.get("safe_next_command") or "")

    def test_stale_orbit_state_paper_writing_safe_next_revalidates_human_stop(self):
        repo = copy_fixture(self)
        package_path = repo / "paper" / "paper_package.json"
        if package_path.exists():
            package_path.unlink()
        human = repo / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# Human Decision Note\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Final verdict: STOP\n",
            encoding="utf-8",
        )
        stale_state = make_state(
            current_stop="STOP_D",
            current_skill="paper-writing",
            current_phase="legacy_ready_for_paper",
            status="paused",
            pause_reason="stop_review",
            safe_next_command='/paper-writing "claims/claim_ledger.json"',
        )
        write_state(repo, stale_state)

        state = get_status(repo)

        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["current_skill"], "diagnostic-to-review")
        self.assertEqual(state["status"], "blocked")
        self.assertNotIn("/paper-writing", state.get("safe_next_command") or "")
        self.assertNotIn("/paper-from-claims", state.get("safe_next_command") or "")

    def test_stale_completed_state_with_draft_paper_package_is_not_completed(self):
        repo = copy_fixture(self)
        package_path = repo / "paper" / "paper_package.json"
        package = load_json(package_path)
        package["status"] = "draft"
        write_json(package_path, package)
        stale_state = make_state(
            current_stop="COMPLETED",
            current_skill="paper-writing",
            current_phase="legacy_completed",
            status="completed",
            pause_reason=None,
            safe_next_command=None,
        )
        write_state(repo, stale_state)

        state = get_status(repo)

        self.assertEqual(state["current_stop"], "STOP_D")
        self.assertEqual(state["current_skill"], "submission-package")
        self.assertEqual(state["status"], "paused")
        self.assertEqual(state["stop_d"]["paper_package_status"], "draft")

    def test_blocked_paper_package_is_not_completed(self):
        repo = copy_fixture(self)
        package_path = repo / "paper" / "paper_package.json"
        package = load_json(package_path)
        package["status"] = "blocked"
        package["blockers"] = [
            {
                "id": "PAPER_AUDIT",
                "kind": "bad_verdict",
                "artifact": "paper/PAPER_CLAIM_AUDIT.md",
                "message": "claim audit failed",
            }
        ]
        write_json(package_path, package)

        state = get_status(repo)
        self.assertEqual(state["current_stop"], "STOP_D")
        self.assertEqual(state["current_skill"], "submission-package")
        self.assertEqual(state["status"], "blocked")
        self.assertNotEqual(state["status"], "completed")
        self.assertIn("claim audit failed", state["blockers"][0]["message"])

    def test_human_stop_does_not_suggest_paper_from_claims(self):
        repo = copy_fixture(self)
        (repo / "paper" / "paper_package.json").unlink()
        human = repo / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# Human Decision Note\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Final verdict: STOP\n",
            encoding="utf-8",
        )

        state = get_status(repo)
        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["current_skill"], "diagnostic-to-review")
        self.assertNotIn("/paper-from-claims", state.get("safe_next_command") or "")
        self.assertNotIn("/submission-package", state.get("safe_next_command") or "")

    def test_human_decision_template_list_is_not_approval(self):
        repo = copy_fixture(self)
        (repo / "paper" / "paper_package.json").unlink()
        human = repo / "orbit-research" / "HUMAN_DECISION_NOTE.md"
        human.write_text(
            "# Human Decision Note\n\nDiagnostic ID: diag_fixture\nClaim ledger hash: ledger_fixture_hash\n\n"
            "Decision: PROCEED | STOP | HOLD\n",
            encoding="utf-8",
        )

        state = get_status(repo)
        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertNotEqual(state["status"], "completed")
        self.assertNotIn("/paper-from-claims", state.get("safe_next_command") or "")

    def test_per_diagnostic_red_team_review_is_recognized(self):
        repo = copy_fixture(self)
        (repo / "paper" / "paper_package.json").unlink()
        legacy_review = repo / "orbit-research" / "RED_TEAM_REVIEW.md"
        if legacy_review.exists():
            legacy_review.unlink()

        state = get_status(repo)
        self.assertEqual(state["current_stop"], "STOP_D")
        self.assertEqual(state["current_skill"], "paper-from-claims")
        self.assertEqual(state["status"], "paused")
        self.assertEqual(state["safe_next_command"], '/paper-from-claims "claims/claim_ledger.json"')
        self.assertEqual(
            state["stop_c"]["approval"]["red_team_review"],
            "orbit-research/diagnostics/diag_fixture/RED_TEAM_REVIEW.md",
        )

    def test_missing_red_team_after_claim_ledger_blocks_stop_c(self):
        repo = copy_fixture(self)
        (repo / "paper" / "paper_package.json").unlink()
        red_team = repo / "orbit-research" / "diagnostics" / "diag_fixture" / "RED_TEAM_REVIEW.md"
        red_team.unlink()
        legacy_review = repo / "orbit-research" / "RED_TEAM_REVIEW.md"
        if legacy_review.exists():
            legacy_review.unlink()

        state = get_status(repo)
        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["status"], "paused")
        self.assertEqual(state["pause_reason"], "missing_prereq")
        self.assertEqual(state["blockers"][0]["artifact"], "orbit-research/diagnostics/diag_fixture/RED_TEAM_REVIEW.md")
        self.assertNotIn("/paper-from-claims", state.get("safe_next_command") or "")

    def test_ready_paper_package_with_valid_approval_is_completed(self):
        repo = copy_fixture(self)

        state = get_status(repo)
        self.assertEqual(state["current_stop"], "STOP_D")
        self.assertEqual(state["current_skill"], "submission-package")
        self.assertEqual(state["status"], "completed")
        self.assertIsNone(state["safe_next_command"])


if __name__ == "__main__":
    unittest.main()
