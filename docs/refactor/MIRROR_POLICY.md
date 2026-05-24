# Mirror Policy

Canonical skill sources live under `skills/<name>/SKILL.md`. Edit canonical skills
first; generated mirrors must be updated from canonical, not hand-edited.

Mirrors are generated or synchronized views. They should not be hand-edited:

- `.agents/skills`
- `skills/skills-codex`

These are full mirrors. Every canonical `skills/<name>/SKILL.md` must have an
identical mirror `SKILL.md` in both roots.

Review overlays are intentionally partial and may differ from canonical only when
`skills/skill_catalog.yaml` marks the overlay root and skill under `mirror_policy`:

- `skills/skills-codex-gemini-review`
- `skills/skills-codex-claude-review`

## Drift Check

Use the CI-friendly checker:

```bash
python3 tools/check_skill_mirror.py --repo .
```

Exit codes:

- `0`: no unexpected drift
- `1`: at least one full mirror drift, missing skill, extra skill, or unlisted overlay entry

The checker reports deterministic status buckets:

- `identical`
- `different`
- `missing`
- `extra`
- `overlay_intentionally_different`
- `overlay_missing`
- `overlay_unlisted`

CI should run this checker and fail on any non-zero exit code. Full mirror statuses
`different`, `missing`, and `extra` are unexpected drift. Overlay differences are allowed
only as `overlay_intentionally_different`; an unlisted overlay skill is still drift.

## Sync

Use the sync tool in dry-run mode first:

```bash
python3 tools/sync_skill_mirror.py --repo .
```

Apply only after reviewing the plan:

```bash
python3 tools/sync_skill_mirror.py --repo . --mirror .agents/skills --apply
python3 tools/sync_skill_mirror.py --repo . --mirror skills/skills-codex --apply
```

The sync tool only targets catalog full mirrors. It refuses review overlay paths and does
not delete extra files or directories. Existing `SKILL.md` files may be overwritten only
when `--apply` is explicit.

For a single drifted mirror, prefer a targeted sync:

```bash
python3 tools/sync_skill_mirror.py --repo . --mirror .agents/skills --apply
```

## Existing Helper

`tools/sync_codex_mirror.py` remains the exact full-directory synchronizer for
`skills/skills-codex`. It can delete stale entries in that mirror. Prefer
`tools/check_skill_mirror.py` for CI drift checks and `tools/sync_skill_mirror.py` when a
non-destructive sync is enough.
