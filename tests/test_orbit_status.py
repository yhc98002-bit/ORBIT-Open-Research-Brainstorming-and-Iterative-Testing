import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from orbit_state import make_state, write_state  # noqa: E402
from orbit_status import format_pretty, get_status  # noqa: E402


class OrbitStatusTest(unittest.TestCase):
    def test_empty_project_reports_none_and_json_cli_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state = get_status(repo)

            self.assertEqual(state["current_stop"], "NONE")
            self.assertEqual(state["status"], "paused")
            self.assertEqual(state["pause_reason"], "ambiguous_resume")
            self.assertEqual(state["blockers"], [])
            self.assertEqual(state["safe_next_command"], '/idea-to-proposal "<research direction>"')

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


if __name__ == "__main__":
    unittest.main()
