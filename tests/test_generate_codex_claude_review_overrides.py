import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

import generate_codex_claude_review_overrides as generator  # noqa: E402


class GenerateCodexClaudeReviewOverridesTest(unittest.TestCase):
    def test_discovers_all_subagent_using_skills(self):
        skills = generator.discover_target_skills()

        self.assertIn("idea-to-proposal", skills)
        self.assertIn("diagnostic-to-review", skills)
        self.assertIn("research-refine", skills)
        self.assertIn("research-review", skills)
        self.assertGreaterEqual(len(skills), 40)

    def test_spawn_and_send_blocks_rewrite_to_direct_claude_cli(self):
        source = """Call reviewer:

```text
spawn_agent:
  model: gpt-5.5
  reasoning_effort: xhigh
  message: |
    Review files.
```

Continue:

```text
send_input:
  target: 123
  message: |
    Re-check after edits.
```
"""

        transformed = generator.transform_body(source)

        self.assertNotIn("spawn_agent:", transformed)
        self.assertNotIn("send_input:", transformed)
        self.assertIn(
            "claude -p --dangerously-skip-permissions --output-format json --model opus --effort max",
            transformed,
        )
        self.assertIn("previous raw Claude JSON/review artifact", transformed)
        self.assertIn("tee \"$RAW_REVIEW_JSON\"", transformed)

    def test_skill_frontmatter_removes_subagent_tools_and_adds_bash(self):
        source = """---
name: sample-skill
description: "Review via Codex-native sub-agent"
allowed-tools: Read, spawn_agent, send_input
---

# Sample

```text
spawn_agent:
  message: |
    Review this.
```
"""

        rendered = generator.render_skill_override("sample-skill", source)

        self.assertIn('name: "sample-skill"', rendered)
        self.assertIn("allowed-tools: Bash(*), Read", rendered)
        self.assertNotIn("allowed-tools: Read, spawn_agent", rendered)
        self.assertIn("Claude Code CLI", rendered)
        self.assertIn("claude -p --dangerously-skip-permissions", rendered)


if __name__ == "__main__":
    unittest.main()
