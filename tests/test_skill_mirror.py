import shutil
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_skill_mirror import check_mirrors  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class SkillMirrorPolicyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="orbit-mirror-test-"))
        self.repo = self.tmp / "repo"
        self.repo.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _write_catalog(self, extra: str = "") -> Path:
        catalog = self.repo / "skills" / "skill_catalog.yaml"
        _write(
            catalog,
            """mirror_policy:
  canonical_root: skills
  full_mirrors:
    - .agents/skills
  overlays:
"""
            + extra,
        )
        return catalog

    def test_full_mirror_drift_is_unexpected(self):
        _write(self.repo / "skills" / "demo" / "SKILL.md", "canonical\n")
        _write(self.repo / ".agents" / "skills" / "demo" / "SKILL.md", "drift\n")

        entries = check_mirrors(self.repo, self._write_catalog())

        drift = [
            entry
            for entry in entries
            if entry.mirror == ".agents/skills" and entry.skill == "demo"
        ]
        self.assertEqual(len(drift), 1)
        self.assertEqual(drift[0].status, "different")
        self.assertTrue(drift[0].unexpected)

    def test_catalog_marked_overlay_drift_is_allowed(self):
        _write(self.repo / "skills" / "demo" / "SKILL.md", "canonical\n")
        _write(self.repo / ".agents" / "skills" / "demo" / "SKILL.md", "canonical\n")
        _write(
            self.repo
            / "skills"
            / "skills-codex-gemini-review"
            / "demo"
            / "SKILL.md",
            "overlay variant\n",
        )
        catalog = self._write_catalog(
            """    - path: skills/skills-codex-gemini-review
      kind: review-overlay
      skills:
        - demo
"""
        )

        entries = check_mirrors(self.repo, catalog)

        unexpected = [entry for entry in entries if entry.unexpected]
        overlay = [
            entry
            for entry in entries
            if entry.mirror == "skills/skills-codex-gemini-review"
            and entry.skill == "demo"
        ]
        self.assertEqual(unexpected, [])
        self.assertEqual(len(overlay), 1)
        self.assertEqual(overlay[0].status, "overlay_intentionally_different")
        self.assertFalse(overlay[0].unexpected)


if __name__ == "__main__":
    unittest.main()
