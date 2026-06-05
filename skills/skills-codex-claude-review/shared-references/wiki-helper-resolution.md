# Wiki helper resolution chain

Canonical resolution chain for the research-wiki helper. This is the
wiki-specific form of [`helper-resolution.md`](helper-resolution.md). Used by
every SKILL that touches the wiki — never hard-code
`python3 tools/research_wiki.py`, because that silently fails when
`<project>/tools/` is not on disk (the post-`install_aris.sh` default), exactly
the failure mode that left a real user's `research-wiki/` empty for a week.

## The chain

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1
if [ -z "${ARIS_REPO:-}" ] && [ -f .aris/installed-skills.txt ]; then
  ARIS_REPO=$(awk -F'\t' '$1=="repo_root"{print $2; exit}' .aris/installed-skills.txt 2>/dev/null) || true
fi
WIKI_SCRIPT=".aris/tools/research_wiki.py"
[ -f "$WIKI_SCRIPT" ] || WIKI_SCRIPT="tools/research_wiki.py"
if [ ! -f "$WIKI_SCRIPT" ]; then
  if [ -n "${ORBIT_REPO:-}" ] && [ -f "$ORBIT_REPO/tools/research_wiki.py" ]; then
    WIKI_SCRIPT="$ORBIT_REPO/tools/research_wiki.py"
  elif [ -n "${ARIS_REPO:-}" ] && [ -f "$ARIS_REPO/tools/research_wiki.py" ]; then
    WIKI_SCRIPT="$ARIS_REPO/tools/research_wiki.py"
  fi
fi
```

After the chain runs, exactly one of two outcomes:

- `[ -f "$WIKI_SCRIPT" ]` → helper located, use as `python3 "$WIKI_SCRIPT" <subcommand>`
- `[ ! -f "$WIKI_SCRIPT" ]` → helper missing; pick a variant below

## Variant A — hard-fail (for `/research-wiki` itself)

The skill **is** the wiki tool. If the helper is missing, fail loudly.

```bash
[ -f "$WIKI_SCRIPT" ] || {
  echo "ERROR: research_wiki.py not found at .aris/tools/, tools/, \$ORBIT_REPO/tools/, or \$ARIS_REPO/tools/." >&2
  echo "       Fix one of:" >&2
  echo "         1. rerun 'bash tools/install_aris.sh' from the ARIS repo (creates .aris/tools symlink)" >&2
  echo "         2. export ORBIT_REPO=<path-to-ORBIT-repo> or ARIS_REPO=<path-to-ARIS-repo>" >&2
  echo "         3. cp <ARIS-repo>/tools/research_wiki.py tools/" >&2
  exit 1
}
```

## Variant B — warn + skip (for caller skills)

Used by `/idea-creator`, `/result-to-claim`, `/research-lit`, `/arxiv`,
`/alphaxiv`, `/deepxiv`, `/exa-search`, `/semantic-scholar`. The
skill's primary output (idea ranking, claim verdict, paper summary)
must still be delivered to the user; only the wiki side-effect is
skipped.

```bash
[ -f "$WIKI_SCRIPT" ] || {
  echo "WARN: research_wiki.py not found at .aris/tools/, tools/, \$ORBIT_REPO/tools/, or \$ARIS_REPO/tools/." >&2
  echo "      Primary output will still be produced; wiki update is skipped." >&2
  echo "      Fix: rerun 'bash tools/install_aris.sh', export ORBIT_REPO/ARIS_REPO, or 'cp <ARIS-repo>/tools/research_wiki.py tools/'." >&2
  WIKI_SCRIPT=""
}
```

After Variant B, every helper invocation must be guarded:

```bash
[ -n "$WIKI_SCRIPT" ] && python3 "$WIKI_SCRIPT" ingest_paper research-wiki/ --arxiv-id "$id"
```

## Why three locations and not one

Three locations correspond to three legitimate install / dev paths:

| Location | When applicable |
|---|---|
| `.aris/tools/research_wiki.py` | After running `bash tools/install_aris.sh` in the user project (Phase 0 symlink, added in #174 / #192) |
| `tools/research_wiki.py` | (a) Manual copy of the helper into the user project (a documented temporary workaround); (b) running a SKILL from inside the ARIS repo itself |
| `$ORBIT_REPO/tools/research_wiki.py` or `$ARIS_REPO/tools/research_wiki.py` | Env var explicitly set, or `ARIS_REPO` auto-resolved from `.aris/installed-skills.txt`'s `repo_root` field |

Order matters: the symlinked install is preferred because the symlink
auto-tracks upstream tool fixes; the manual copy is second because it
catches users who haven't run `install_aris.sh`; the env var is last
because it's the most fragile.

## What NOT to add

- ❌ A 4th layer that searches up the directory tree for `tools/` —
  too much path magic, surprising failure modes.
- ❌ A 4th layer at `~/.local/share/aris/...` or `/usr/local/share/...`
  — no installer precedent in ARIS today.
- ❌ Adding `~/.codex/skills/research-wiki/research_wiki.py` — that's
  Codex-side global install, lives in the **Codex** mirror's chain
  (`skills/skills-codex/...`), not the CC chain.

If a fourth layer is genuinely needed in the future, add an explicit
env var (`ARIS_WIKI_SCRIPT=<path>`) rather than another implicit
location.

## ⚠️ Do not wrap the chain in `set -e` / `set -eu`

The `${ARIS_REPO:-$(awk ...)}` substitution propagates the inner
`awk` exit code to `set -e` even when stderr is suppressed with
`2>/dev/null`. `awk` returns non-zero (2 on most macOS systems) when
its input file does not exist — which is the common case (no
`.aris/installed-skills.txt` yet). With `set -e` enabled, the chain
will exit silently with code 2 before reaching the `[ -f ... ]`
checks, masking the real failure mode and breaking the manual-copy
fallback.

The resolver now uses this strict-mode-safe manifest read:

```bash
if [ -z "${ARIS_REPO:-}" ] && [ -f .aris/installed-skills.txt ]; then
    ARIS_REPO=$(awk -F'\t' '$1=="repo_root"{print $2; exit}' .aris/installed-skills.txt 2>/dev/null) || true
fi
```

But the simpler answer is: don't enable strict mode for the resolver
preamble. SKILL bash blocks do not run with `set -e` by default and
the rest of the helper invocations all use explicit `[ -n "$WIKI_SCRIPT" ] && ...`
guards anyway.

## See also

- [`integration-contract.md`](integration-contract.md) §2 — canonical-helper invariant
- `skills/research-wiki/SKILL.md` — the wiki tool itself; uses Variant A
- PR #193 — the parallel fix for `experiment-queue` helpers (same pattern, different helper)
