import re
import shutil
import subprocess
import tempfile
import urllib.parse
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / "skills"
CODEX_MIRROR_DIR = SKILLS_DIR / "skills-codex"
MIRROR_EXCLUDES = {
    "shared-references",
    "skills-codex",
    "skills-codex-claude-review",
    "skills-codex-gemini-review",
}
IGNORED_TREE_NAMES = {"__pycache__", ".DS_Store"}


def _frontmatter_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end == -1:
        return None
    for line in text[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("\"'")
    return None


def _shared_ref_candidates(path: Path):
    text = path.read_text(encoding="utf-8")
    patterns = [
        r"`((?:\.\./|\.\./\.\./)?shared-references/[A-Za-z0-9_.-]+\.md)`",
        r"`(skills/shared-references/[A-Za-z0-9_.-]+\.md)`",
        r"\]\(((?:\.\./|\.\./\.\./)?shared-references/[A-Za-z0-9_.-]+\.md)(?:#[^)]+)?\)",
        r"\]\((skills/shared-references/[A-Za-z0-9_.-]+\.md)(?:#[^)]+)?\)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            yield match.group(1), text[: match.start()].count("\n") + 1


def _resolve_shared_ref(skill_path: Path, ref: str) -> Path:
    if ref.startswith("skills/shared-references/"):
        return ROOT / ref

    local = (skill_path.parent / ref).resolve()
    if local.exists():
        return local

    # Reviewer overlay packages are installed on top of skills-codex, so their
    # ../shared-references links resolve against the base mirror after install.
    parts = skill_path.parts
    if (
        "skills-codex-claude-review" in parts
        or "skills-codex-gemini-review" in parts
    ):
        return (
            SKILLS_DIR
            / "skills-codex"
            / "shared-references"
            / Path(ref).name
        )

    return local


def _top_level_skill_names() -> set[str]:
    return {
        path.name
        for path in SKILLS_DIR.iterdir()
        if path.is_dir()
        and path.name not in MIRROR_EXCLUDES
        and (path / "SKILL.md").is_file()
    }


def _relative_files(root: Path) -> set[Path]:
    files = set()
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in IGNORED_TREE_NAMES for part in rel.parts):
            continue
        if path.is_file():
            files.add(rel)
    return files


def _tree_mismatches(src: Path, dst: Path) -> list[str]:
    if not dst.exists():
        return [f"missing dir: {dst.relative_to(ROOT)}"]
    failures = []
    src_files = _relative_files(src)
    dst_files = _relative_files(dst)
    for rel in sorted(src_files - dst_files):
        failures.append(f"missing: {(dst / rel).relative_to(ROOT)}")
    for rel in sorted(dst_files - src_files):
        failures.append(f"extra: {(dst / rel).relative_to(ROOT)}")
    for rel in sorted(src_files & dst_files):
        if (src / rel).read_bytes() != (dst / rel).read_bytes():
            failures.append(f"differs: {(dst / rel).relative_to(ROOT)}")
    return failures


class SkillIntegrityTest(unittest.TestCase):
    def test_skill_frontmatter_name_matches_directory(self):
        failures = []
        for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
            name = _frontmatter_name(skill_md)
            if name != skill_md.parent.name:
                failures.append(f"{skill_md.relative_to(ROOT)}: {name!r}")

        self.assertEqual(failures, [])

    def test_shared_reference_links_resolve(self):
        failures = []
        for skill_md in sorted(SKILLS_DIR.rglob("SKILL.md")):
            for ref, line in _shared_ref_candidates(skill_md):
                target = _resolve_shared_ref(skill_md, ref)
                if not target.exists():
                    failures.append(
                        f"{skill_md.relative_to(ROOT)}:{line}: {ref} -> {target}"
                    )

        self.assertEqual(failures, [])

    def test_top_level_skills_do_not_use_bare_shared_reference_paths(self):
        failures = []
        pattern = re.compile(r"`shared-references/[A-Za-z0-9_.-]+\.md`")
        for skill_md in sorted(SKILLS_DIR.glob("*/SKILL.md")):
            text = skill_md.read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                failures.append(
                    f"{skill_md.relative_to(ROOT)}:{text[:match.start()].count(chr(10)) + 1}"
                )

        self.assertEqual(failures, [])

    def test_codex_mirror_skill_set_matches_top_level(self):
        source_names = _top_level_skill_names()
        mirror_names = {
            path.name
            for path in CODEX_MIRROR_DIR.iterdir()
            if path.is_dir()
            and path.name != "shared-references"
            and (path / "SKILL.md").is_file()
        }

        self.assertEqual(
            mirror_names,
            source_names,
            msg=f"missing={sorted(source_names - mirror_names)} extra={sorted(mirror_names - source_names)}",
        )

    def test_codex_mirror_files_match_top_level(self):
        failures = []
        for name in sorted(_top_level_skill_names()):
            failures.extend(
                _tree_mismatches(SKILLS_DIR / name, CODEX_MIRROR_DIR / name)
            )

        self.assertEqual(failures, [])

    def test_codex_mirror_shared_references_match_top_level(self):
        failures = _tree_mismatches(
            SKILLS_DIR / "shared-references",
            CODEX_MIRROR_DIR / "shared-references",
        )

        self.assertEqual(failures, [])

    def test_helper_resolution_reference_defines_standard_chain(self):
        text = (SKILLS_DIR / "shared-references" / "helper-resolution.md").read_text(
            encoding="utf-8"
        )
        required = [
            ".aris/tools/<helper>",
            "tools/<helper>",
            "$ORBIT_REPO/tools/<helper>",
            "$ARIS_REPO/tools/<helper>",
        ]
        missing = [item for item in required if item not in text]

        self.assertEqual(missing, [])

    def test_markdown_relative_links_resolve(self):
        docs = [
            *sorted(SKILLS_DIR.rglob("SKILL.md")),
            *sorted((SKILLS_DIR / "shared-references").glob("*.md")),
        ]
        runtime_prefixes = (
            "orbit-research/",
            "refine-logs/",
            "review-stage/",
            "paper/",
            "results/",
            "research-wiki/",
            "figures/",
        )
        ignored_examples = {"filename.svg"}
        failures = []
        pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
        for path in docs:
            text = path.read_text(encoding="utf-8")
            for match in pattern.finditer(text):
                target = match.group(1).split("#", 1)[0].strip().strip("<>")
                if not target or target in ignored_examples:
                    continue
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                    continue
                if target.startswith(("/", "$", *runtime_prefixes)):
                    continue
                resolved = (path.parent / urllib.parse.unquote(target)).resolve()
                if not resolved.exists():
                    failures.append(
                        f"{path.relative_to(ROOT)}:{text[:match.start()].count(chr(10)) + 1}: {target}"
                    )

        self.assertEqual(failures, [])

    def test_state_contract_includes_user_action_status(self):
        text = (SKILLS_DIR / "shared-references" / "continuation-contract.md").read_text(
            encoding="utf-8"
        )
        required = [
            "awaiting_user_action",
            "in_progress | awaiting_human_continue | awaiting_user_action | completed",
            "Downstream skills must not treat this as approval",
        ]
        missing = [item for item in required if item not in text]

        self.assertEqual(missing, [])

    def test_codex_unavailable_is_not_advisory_audit_error(self):
        forbidden = [
            re.compile(r"codex_mcp_unavailable"),
            re.compile(r"ERROR.*advisory", re.IGNORECASE),
            re.compile(r"advisory at the diagnostic", re.IGNORECASE),
            re.compile(r"Codex unavailable, audit could not complete", re.IGNORECASE),
        ]
        failures = []
        for path in [
            *sorted(SKILLS_DIR.rglob("SKILL.md")),
            *sorted((SKILLS_DIR / "shared-references").glob("*.md")),
        ]:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                for match in pattern.finditer(text):
                    failures.append(
                        f"{path.relative_to(ROOT)}:{text[:match.start()].count(chr(10)) + 1}: {match.group(0)}"
                    )

        self.assertEqual(failures, [])

    def test_result_to_claim_uses_standalone_codex_handoff(self):
        text = (SKILLS_DIR / "result-to-claim" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        required = [
            "tools/codex_review_handoff.py",
            "/import-codex-review orbit-research/codex-imports/result-to-claim.claim-evaluation.response.md",
            'pause_reason: "codex_review_needed"',
            'codex_review: "pending"',
            "gating: false",
            "A draft `claims/claim_ledger.json` is allowed only when it is",
            "Do not let a non-gating or degraded draft ledger satisfy paper gates",
        ]
        missing = [item for item in required if item not in text]

        self.assertEqual(missing, [])

    def test_human_gate_requires_proceed_verdict(self):
        files = [
            SKILLS_DIR / "paper-writing" / "SKILL.md",
            SKILLS_DIR / "research-pipeline" / "SKILL.md",
            SKILLS_DIR / "shared-references" / "research-agent-pipeline.md",
            SKILLS_DIR / "shared-references" / "research-harness-prompts.md",
        ]
        required = [
            "HUMAN_DECISION_NOTE.md` ending `PROCEED`",
            "AGENT_DECISION_RECOMMENDATION.md",
        ]
        failures = []
        for item in required:
            if not any(item in path.read_text(encoding="utf-8") for path in files):
                failures.append(item)

        self.assertEqual(failures, [])

    def test_red_team_review_has_verdict_contract(self):
        files = [
            SKILLS_DIR / "auto-review-loop" / "SKILL.md",
            SKILLS_DIR / "paper-writing" / "SKILL.md",
            SKILLS_DIR / "shared-references" / "research-agent-pipeline.md",
            SKILLS_DIR / "shared-references" / "research-harness-prompts.md",
        ]
        required = [
            "READY_FOR_PAPER | REQUIRES_FIXES | REDESIGN_REQUIRED | HUMAN_DECISION_REQUIRED",
            "RED_TEAM_REVIEW.md`  *(must end `READY_FOR_PAPER`)",
            "— orbit-red-team: true",
        ]
        failures = []
        for item in required:
            if not any(item in path.read_text(encoding="utf-8") for path in files):
                failures.append(item)

        self.assertEqual(failures, [])

    def test_auto_review_loop_separates_orbit_red_team_mode(self):
        text = (SKILLS_DIR / "auto-review-loop" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        required = [
            "Use **generic improvement mode**",
            "## ORBIT red-team Mode",
            "GENERIC_POSITIVE_THRESHOLD",
            "never a STOP C paper-readiness rule",
            "Do not use score >= 4, score >= 6, or any numeric threshold as STOP C readiness.",
            "ORBIT RED-TEAM STOP CONDITION",
            "STOP C readiness is determined only by the final verdict token",
            "Do not implement fixes directly.",
            "Prompt Template for Round 2+ (Generic Improvement Mode Only)",
            "READY_FOR_PAPER | REQUIRES_FIXES | REDESIGN_REQUIRED | HUMAN_DECISION_REQUIRED",
        ]
        missing = [item for item in required if item not in text]

        self.assertEqual(missing, [])

    def test_run_experiment_supports_diagnostic_session_output_root(self):
        run_text = (SKILLS_DIR / "run-experiment" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        diagnostic_text = (
            SKILLS_DIR / "diagnostic-to-review" / "SKILL.md"
        ).read_text(encoding="utf-8")

        run_required = [
            "— diagnostic-id: <id>",
            "— output-root: orbit-research/diagnostics/<diagnostic_id>/",
            "ORBIT_DIAGNOSTIC_ID=<diagnostic_id>",
            "ORBIT_DIAGNOSTIC_OUTPUT_ROOT=orbit-research/diagnostics/<diagnostic_id>/",
            "Per-diagnostic formal output paths are canonical",
            "orbit-research/diagnostics/<diagnostic_id>/RUN_REPORT.md",
            "orbit-research/diagnostics/<diagnostic_id>/RUN_AUDIT.md",
            "Do not write only the legacy fixed paths for formal diagnostics",
            "Compatibility latest copies may still be written to:",
            "python3 tools/diagnostic_session.py update-run",
        ]
        diagnostic_required = [
            "Call\n`/run-experiment` with that diagnostic_id and output_root",
            "— diagnostic-id: \"<diagnostic_id>\"",
            "— output-root: \"orbit-research/diagnostics/<diagnostic_id>/\"",
            "ORBIT_DIAGNOSTIC_ID=\"<diagnostic_id>\"",
            "ORBIT_DIAGNOSTIC_OUTPUT_ROOT=\"orbit-research/diagnostics/<diagnostic_id>\"",
            "directly into:",
            "Compatibility latest copies may be written to:",
        ]

        missing = [item for item in run_required if item not in run_text]
        missing.extend(item for item in diagnostic_required if item not in diagnostic_text)

        self.assertEqual(missing, [])

    def test_install_docs_do_not_recommend_dangerous_copy_patterns(self):
        docs = [
            ROOT / "README.md",
            ROOT / "README_CN.md",
            *sorted((ROOT / "docs").glob("*.md")),
            CODEX_MIRROR_DIR / "README.md",
            CODEX_MIRROR_DIR / "README_CN.md",
            ROOT / "tools" / "smart_update.sh",
            ROOT / "tools" / "smart_update.ps1",
        ]
        forbidden = [
            re.compile(r"cp\s+-[A-Za-z]*r[A-Za-z]*\s+skills/\*"),
            re.compile(r"--target-subdir\s+\.agents/skills/aris"),
            re.compile(r"-TargetSubdir\s+['\"]?\.agents/skills/aris"),
        ]
        failures = []
        for path in docs:
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                for match in pattern.finditer(text):
                    line = text[: match.start()].count("\n") + 1
                    failures.append(
                        f"{path.relative_to(ROOT)}:{line}: {match.group(0)}"
                    )

        self.assertEqual(failures, [])


@unittest.skipUnless(shutil.which("bash"), "bash is required for installer tests")
class InstallerRegressionTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="orbit-install-"))
        self.project = self.tmp / "project"
        self.project.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_replace_link_dry_run_rewrites_named_symlink_conflict(self):
        target_dir = self.project / ".claude" / "skills"
        target_dir.mkdir(parents=True)
        (target_dir / "arxiv").symlink_to(SKILLS_DIR / "deepxiv")

        result = subprocess.run(
            [
                "bash",
                str(ROOT / "tools" / "install_aris.sh"),
                str(self.project),
                "--aris-repo",
                str(ROOT),
                "--dry-run",
                "--replace-link",
                "arxiv",
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)

    def test_install_creates_aris_tools_symlink(self):
        result = subprocess.run(
            [
                "bash",
                str(ROOT / "tools" / "install_aris.sh"),
                str(self.project),
                "--aris-repo",
                str(ROOT),
                "--quiet",
                "--no-doc",
            ],
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        tools_link = self.project / ".aris" / "tools"
        self.assertTrue(tools_link.is_symlink())
        self.assertEqual(tools_link.resolve(), ROOT / "tools")


if __name__ == "__main__":
    unittest.main()
