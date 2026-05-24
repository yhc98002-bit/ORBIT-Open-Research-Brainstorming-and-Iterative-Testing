import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillCatalogTest(unittest.TestCase):
    def test_skill_catalog_profiles_are_valid(self):
        result = subprocess.run(
            [sys.executable, "tools/list_skill_profiles.py", "--repo", ".", "--check"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
