---
name: orbit-status
description: Read-only ORBIT status doctor. Use when the user asks "where am I", "what is blocked", "what next", "resume ORBIT", or needs the current STOP and safe next command.
argument-hint: [--json]
allowed-tools: Bash(python tools/orbit_status.py --repo *), Bash(python3 tools/orbit_status.py --repo *), Read
---

# /orbit-status

Report the current ORBIT STOP, blocker summary, and safe next command.

This skill is read-only. It must not create, repair, rewrite, or delete artifacts.

Run from the repository root:

```bash
python tools/orbit_status.py --repo . --pretty
```

If the user asks for machine-readable output, run:

```bash
python tools/orbit_status.py --repo . --json
```

The tool prefers `orbit-research/ORBIT_STATE.json` when present. If it is missing,
it conservatively infers status from legacy ORBIT artifacts and reports
`ambiguous_resume` rather than claiming success when verdicts are missing or unclear.
