import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PromptAssetsTest(unittest.TestCase):
    def test_prompt_asset_references_are_valid(self):
        result = subprocess.run(
            [sys.executable, "tools/check_prompt_assets.py", "--repo", "."],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
