# ARIS helper resolution

Use this resolver before invoking ARIS helper scripts from a downstream user
project. Do not hard-code `tools/<helper>` unless the command is guaranteed to
run from inside the ARIS repository itself.

## Canonical chain

Resolution order is fixed:

1. `.aris/tools/<helper>` — project install managed by `tools/install_aris.sh`
2. `tools/<helper>` — helper manually copied into the project, or running inside this repo
3. `$ORBIT_REPO/tools/<helper>` then `$ARIS_REPO/tools/<helper>` — explicit repo location

```bash
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)" || exit 1
if [ -z "${ARIS_REPO:-}" ] && [ -f .aris/installed-skills.txt ]; then
  ARIS_REPO=$(awk -F'\t' '$1=="repo_root"{print $2; exit}' .aris/installed-skills.txt 2>/dev/null) || true
fi

resolve_aris_helper() {
  helper_name="$1"
  helper_path=".aris/tools/$helper_name"
  [ -f "$helper_path" ] || helper_path="tools/$helper_name"
  if [ ! -f "$helper_path" ]; then
    if [ -n "${ORBIT_REPO:-}" ] && [ -f "$ORBIT_REPO/tools/$helper_name" ]; then
      helper_path="$ORBIT_REPO/tools/$helper_name"
    elif [ -n "${ARIS_REPO:-}" ] && [ -f "$ARIS_REPO/tools/$helper_name" ]; then
      helper_path="$ARIS_REPO/tools/$helper_name"
    else
      helper_path=""
    fi
  fi
  printf '%s\n' "$helper_path"
}

HELPER_PATH="$(resolve_aris_helper "<helper-name>")"
```

## Missing-helper outcomes

Hard-fail when the helper is the skill's primary mechanism:

```bash
[ -n "$HELPER_PATH" ] || {
  echo "ERROR: <helper-name> not found at .aris/tools/, tools/, \$ORBIT_REPO/tools/, or \$ARIS_REPO/tools/." >&2
  echo "       Fix: rerun 'bash tools/install_aris.sh', export ORBIT_REPO/ARIS_REPO, or copy the helper into tools/." >&2
  exit 1
}
```

Warn and skip when the helper is only a side effect:

```bash
[ -n "$HELPER_PATH" ] || {
  echo "WARN: <helper-name> not found; primary output will still be produced, but the helper side effect is skipped." >&2
  HELPER_PATH=""
}
```

After a warn-skip block, guard every invocation:

```bash
[ -n "$HELPER_PATH" ] && python3 "$HELPER_PATH" ...
```
