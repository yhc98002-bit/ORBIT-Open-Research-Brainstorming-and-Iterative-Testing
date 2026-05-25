import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

from list_skill_profiles import parse_catalog, profile_names  # noqa: E402


class SkillCatalogTest(unittest.TestCase):
    def catalog(self):
        return parse_catalog(ROOT / "skills" / "skill_catalog.yaml")

    def test_skill_catalog_profiles_are_valid(self):
        result = subprocess.run(
            [sys.executable, "tools/list_skill_profiles.py", "--repo", ".", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_orbit_core_installs_codex_recovery_utility(self):
        names = profile_names(self.catalog(), "orbit-core")
        self.assertIn("import-codex-review", names)

    def test_full_idea_to_paper_profile_or_default_install_guidance_exists(self):
        catalog = self.catalog()
        docs = "\n".join(
            [
                (ROOT / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "refactor" / "SKILL_PROFILES.md").read_text(encoding="utf-8"),
            ]
        )
        has_research_paper_profile = "research-paper" in catalog["profiles"]
        has_default_install_guidance = (
            "默认完整安装" in docs
            and "idea-to-paper" in docs
            and "bash tools/install_aris.sh" in docs
        )
        self.assertTrue(
            has_research_paper_profile or has_default_install_guidance,
            "full idea-to-paper use must have a profile or explicit default-install guidance",
        )

    def test_profile_docs_do_not_claim_profile_installs_are_additive(self):
        docs = "\n".join(
            [
                (ROOT / "README.md").read_text(encoding="utf-8"),
                (ROOT / "docs" / "refactor" / "SKILL_PROFILES.md").read_text(encoding="utf-8"),
            ]
        ).lower()
        self.assertNotIn("additive", docs)
        self.assertNotIn("叠加", docs)


if __name__ == "__main__":
    unittest.main()
