import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import codex_review_handoff  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class CodexReviewHandoffTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="codex-handoff-"))
        self.addCleanup(shutil.rmtree, self.tmp)

    def run_tool(self, *args: str) -> None:
        code = codex_review_handoff.main(list(args))
        self.assertEqual(code, 0)

    def write_response(self, phase_id: str) -> Path:
        response = self.tmp / "orbit-research" / "codex-imports" / ("%s.response.md" % phase_id)
        response.parent.mkdir(parents=True, exist_ok=True)
        response.write_text(
            "# VERDICT\n\n"
            "PASS\n\n"
            "The standalone Codex review inspected the requested artifacts, preserved the "
            "producer context, and gives a substantive response that is long enough for import.\n",
            encoding="utf-8",
        )
        return response

    def write_response_text(self, phase_id: str, text: str) -> Path:
        response = self.tmp / "orbit-research" / "codex-imports" / ("%s.response.md" % phase_id)
        response.parent.mkdir(parents=True, exist_ok=True)
        response.write_text(text, encoding="utf-8")
        return response

    def generate_red_team_handoff(self, phase_id: str = "diag_123.phase-4-review") -> None:
        self.run_tool(
            "generate",
            "--repo",
            str(self.tmp),
            "--phase-id",
            phase_id,
            "--role",
            "Independent STOP C reviewer",
            "--objective",
            "Review STOP C claims.",
            "--output-format",
            "Include VERDICT and one final ORBIT red-team token.",
            "--output-artifact",
            "orbit-research/diagnostics/diag_123/RED_TEAM_REVIEW.md",
            "--current-stop",
            "STOP_C",
            "--producer-skill",
            "diagnostic-to-review",
            "--producer-phase",
            "phase-4-review",
            "--diagnostic-id",
            "diag_123",
            "--resume-command",
            '/diagnostic-to-review "experiment/experiment_pack.json" -- resume:true',
            "--verdict-required",
            "--expected-verdict-token",
            "READY_FOR_PAPER",
            "--expected-verdict-token",
            "REQUIRES_FIXES",
            "--expected-verdict-token",
            "REDESIGN_REQUIRED",
            "--expected-verdict-token",
            "HUMAN_DECISION_REQUIRED",
            "--write-orbit-state",
        )

    def test_generate_with_producer_context_writes_orbit_state(self):
        self.run_tool(
            "generate",
            "--repo",
            str(self.tmp),
            "--phase-id",
            "diag_123.phase-4-review",
            "--role",
            "Independent STOP C reviewer",
            "--file",
            "claims/claim_ledger.json",
            "--objective",
            "Review STOP C claims.",
            "--output-format",
            "Include VERDICT.",
            "--output-artifact",
            "orbit-research/diagnostics/diag_123/RED_TEAM_REVIEW.md",
            "--current-stop",
            "STOP_C",
            "--producer-skill",
            "diagnostic-to-review",
            "--producer-phase",
            "phase-4-review",
            "--diagnostic-id",
            "diag_123",
            "--resume-command",
            '/diagnostic-to-review "experiment/experiment_pack.json" -- resume:true',
            "--write-orbit-state",
        )

        metadata = read_json(self.tmp / "orbit-research" / "codex-prompts" / "diag_123.phase-4-review.json")
        self.assertEqual(metadata["current_stop"], "STOP_C")
        self.assertEqual(metadata["producer_skill"], "diagnostic-to-review")
        self.assertEqual(metadata["producer_phase"], "phase-4-review")
        self.assertEqual(metadata["diagnostic_id"], "diag_123")
        self.assertEqual(
            metadata["resume_command"],
            '/diagnostic-to-review "experiment/experiment_pack.json" -- resume:true',
        )

        state = read_json(self.tmp / "orbit-research" / "ORBIT_STATE.json")
        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["current_skill"], "diagnostic-to-review")
        self.assertEqual(state["current_phase"], "phase-4-review")
        self.assertEqual(state["status"], "blocked")
        self.assertEqual(state["pause_reason"], "codex_review_needed")
        self.assertEqual(
            state["safe_next_command"],
            "/import-codex-review orbit-research/codex-imports/diag_123.phase-4-review.response.md",
        )

    def test_import_updates_orbit_state_and_metadata_for_resume(self):
        phase_id = "diag_123.phase-4-review"
        resume_command = '/diagnostic-to-review "experiment/experiment_pack.json" -- resume:true'
        self.run_tool(
            "generate",
            "--repo",
            str(self.tmp),
            "--phase-id",
            phase_id,
            "--role",
            "Independent STOP C reviewer",
            "--objective",
            "Review STOP C claims.",
            "--output-format",
            "Include VERDICT.",
            "--output-artifact",
            "orbit-research/diagnostics/diag_123/RED_TEAM_REVIEW.md",
            "--current-stop",
            "STOP_C",
            "--producer-skill",
            "diagnostic-to-review",
            "--producer-phase",
            "phase-4-review",
            "--diagnostic-id",
            "diag_123",
            "--resume-command",
            resume_command,
            "--write-orbit-state",
        )
        self.write_response(phase_id)

        self.run_tool(
            "import",
            "orbit-research/codex-imports/%s.response.md" % phase_id,
            "--repo",
            str(self.tmp),
        )

        state = read_json(self.tmp / "orbit-research" / "ORBIT_STATE.json")
        self.assertEqual(state["current_stop"], "STOP_C")
        self.assertEqual(state["current_skill"], "diagnostic-to-review")
        self.assertEqual(state["current_phase"], "phase-4-review")
        self.assertEqual(state["status"], "paused")
        self.assertEqual(state["pause_reason"], "codex_review_imported")
        self.assertEqual(state["safe_next_command"], resume_command)

        metadata = read_json(self.tmp / "orbit-research" / "codex-prompts" / ("%s.json" % phase_id))
        self.assertEqual(metadata["diagnostic_id"], "diag_123")
        self.assertEqual(metadata["resume_command"], resume_command)
        self.assertEqual(
            metadata["imported_response_path"],
            "orbit-research/codex-imports/%s.response.md" % phase_id,
        )
        self.assertEqual(
            metadata["imported_output_artifact"],
            "orbit-research/diagnostics/diag_123/RED_TEAM_REVIEW.md",
        )
        self.assertIn("imported_at", metadata)
        self.assertTrue((self.tmp / "orbit-research" / "diagnostics" / "diag_123" / "RED_TEAM_REVIEW.md").exists())

    def test_regression_import_rejects_verdict_heading_without_concrete_token(self):
        phase_id = "diag_123.phase-4-review"
        self.generate_red_team_handoff(phase_id)
        self.write_response_text(
            phase_id,
            "# VERDICT\n\n"
            "The response has the expected heading and enough explanatory prose, but it "
            "intentionally omits a concrete review token so import must reject it.\n",
        )

        code = codex_review_handoff.main(
            [
                "import",
                "orbit-research/codex-imports/%s.response.md" % phase_id,
                "--repo",
                str(self.tmp),
            ]
        )

        self.assertNotEqual(code, 0)
        self.assertFalse(
            (self.tmp / "orbit-research" / "diagnostics" / "diag_123" / "RED_TEAM_REVIEW.md").exists()
        )

    def test_import_accepts_markdown_wrapped_phase_specific_verdict(self):
        phase_id = "diag_123.phase-4-review"
        self.generate_red_team_handoff(phase_id)
        self.write_response_text(
            phase_id,
            "# VERDICT\n\n"
            "The standalone Codex review checked the claim ledger, evidence paths, and "
            "STOP C blockers. It found issues that must be fixed before paper handoff.\n\n"
            "Final verdict: **REQUIRES_FIXES**\n",
        )

        self.run_tool(
            "import",
            "orbit-research/codex-imports/%s.response.md" % phase_id,
            "--repo",
            str(self.tmp),
        )

        metadata = read_json(self.tmp / "orbit-research" / "codex-prompts" / ("%s.json" % phase_id))
        self.assertTrue(metadata["verdict_required"])
        self.assertEqual(
            metadata["expected_verdict_tokens"],
            [
                "READY_FOR_PAPER",
                "REQUIRES_FIXES",
                "REDESIGN_REQUIRED",
                "HUMAN_DECISION_REQUIRED",
            ],
        )
        self.assertEqual(metadata["imported_verdict"], "REQUIRES_FIXES")
        artifact = self.tmp / "orbit-research" / "diagnostics" / "diag_123" / "RED_TEAM_REVIEW.md"
        self.assertIn("Final verdict: **REQUIRES_FIXES**", artifact.read_text(encoding="utf-8"))

    def test_import_rejects_phase_specific_verdict_candidate_list(self):
        phase_id = "diag_123.phase-4-review"
        self.generate_red_team_handoff(phase_id)
        self.write_response_text(
            phase_id,
            "# VERDICT\n\n"
            "The standalone Codex review text is long enough and describes several issues, "
            "but it leaves the final decision as a template instead of choosing one.\n\n"
            "Final verdict: READY_FOR_PAPER | REQUIRES_FIXES\n",
        )

        code = codex_review_handoff.main(
            [
                "import",
                "orbit-research/codex-imports/%s.response.md" % phase_id,
                "--repo",
                str(self.tmp),
            ]
        )

        self.assertNotEqual(code, 0)
        self.assertFalse(
            (self.tmp / "orbit-research" / "diagnostics" / "diag_123" / "RED_TEAM_REVIEW.md").exists()
        )

    def test_import_rejects_phase_specific_verdict_template_bullets(self):
        phase_id = "diag_123.phase-4-review"
        self.generate_red_team_handoff(phase_id)
        self.write_response_text(
            phase_id,
            "# VERDICT\n\n"
            "The standalone Codex review text is substantive enough for import validation, "
            "but it leaves the verdict section as an unfinished template.\n\n"
            "Allowed final verdict tokens:\n"
            "- READY_FOR_PAPER\n"
            "- REQUIRES_FIXES\n"
            "- REDESIGN_REQUIRED\n"
            "- HUMAN_DECISION_REQUIRED\n\n"
            "Final verdict: <ONE_TOKEN>\n",
        )

        code = codex_review_handoff.main(
            [
                "import",
                "orbit-research/codex-imports/%s.response.md" % phase_id,
                "--repo",
                str(self.tmp),
            ]
        )

        self.assertNotEqual(code, 0)
        self.assertFalse(
            (self.tmp / "orbit-research" / "diagnostics" / "diag_123" / "RED_TEAM_REVIEW.md").exists()
        )

    def test_validate_response_rejects_single_bullet_token_as_final_verdict(self):
        text = (
            "# VERDICT\n\n"
            "This response is long enough and includes a discussion, but the only token is "
            "presented as a bullet from a template rather than an explicit final verdict.\n\n"
            "- READY_FOR_PAPER\n"
        )

        result = codex_review_handoff.validate_response_text(
            text,
            ["VERDICT"],
            verdict_required=True,
            expected_verdict_tokens=[
                "READY_FOR_PAPER",
                "REQUIRES_FIXES",
                "REDESIGN_REQUIRED",
                "HUMAN_DECISION_REQUIRED",
            ],
        )

        self.assertFalse(result["valid"])
        self.assertIsNone(result["verdict"])

    def test_generic_handoff_without_verdict_required_remains_flexible(self):
        phase_id = "generic.phase"
        self.run_tool(
            "generate",
            "--repo",
            str(self.tmp),
            "--phase-id",
            phase_id,
            "--role",
            "Independent reviewer",
            "--objective",
            "Review an artifact.",
            "--output-format",
            "Include VERDICT.",
            "--output-artifact",
            "orbit-research/GENERIC_REVIEW.md",
        )
        self.write_response_text(
            phase_id,
            "# VERDICT\n\n"
            "This generic standalone Codex response contains a substantive review narrative "
            "without a phase-specific final token, which is acceptable for non-gating handoff.\n",
        )

        self.run_tool(
            "import",
            "orbit-research/codex-imports/%s.response.md" % phase_id,
            "--repo",
            str(self.tmp),
        )

        self.assertTrue((self.tmp / "orbit-research" / "GENERIC_REVIEW.md").exists())

    def test_missing_producer_context_still_writes_unknown_context_state(self):
        self.run_tool(
            "generate",
            "--repo",
            str(self.tmp),
            "--phase-id",
            "unknown.phase",
            "--role",
            "Independent reviewer",
            "--objective",
            "Review an artifact.",
            "--output-format",
            "Include VERDICT.",
            "--write-orbit-state",
        )

        state = read_json(self.tmp / "orbit-research" / "ORBIT_STATE.json")
        self.assertEqual(state["current_stop"], "NONE")
        self.assertEqual(state["current_skill"], "codex-review-handoff")
        self.assertEqual(state["current_phase"], "unknown.phase")
        self.assertEqual(state["pause_reason"], "codex_review_needed")

        prompt = (self.tmp / "orbit-research" / "codex-prompts" / "unknown.phase.md").read_text(encoding="utf-8")
        self.assertIn("Producer context unknown", prompt)


if __name__ == "__main__":
    unittest.main()
