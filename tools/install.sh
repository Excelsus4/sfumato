#!/usr/bin/env bash
# Sfumato installer (macOS / Linux).
#
# Local checkout:   bash tools/install.sh [--target claude|agy|codex|all|auto] [--dry-run]
# Recommended:      git clone the repo, inspect skill/sfumato and this script,
#                   then run it from the checkout (no piping remote code into a shell).
#
# Targets:
#   claude -> ~/.claude/skills/sfumato  (+ ~/.claude/commands/*.md)
#   agy    -> ~/.gemini/config/skills/sfumato
#   codex  -> ~/.codex/skills/sfumato
#   all    -> all of the above
#   auto   -> every agent whose config dir exists (default; falls back to claude)
#
# Options:
#   --dry-run        print actions without writing anything
#   --home DIR       install under DIR instead of $HOME (testing)
#   --source DIR     use DIR as the repo root instead of auto-detecting
set -euo pipefail

REPO_TARBALL="https://github.com/Excelsus4/sfumato/archive/refs/heads/main.tar.gz"
TARGET="auto"
DRY_RUN=0
HOME_DIR="${HOME:-}"
SOURCE=""

usage() { sed -n '2,20p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --target) TARGET="${2:-}"; shift 2 ;;
    --target=*) TARGET="${1#*=}"; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --home) HOME_DIR="${2:-}"; shift 2 ;;
    --home=*) HOME_DIR="${1#*=}"; shift ;;
    --source) SOURCE="${2:-}"; shift 2 ;;
    --source=*) SOURCE="${1#*=}"; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown argument: $1" >&2; exit 2 ;;
  esac
done

case "$TARGET" in
  claude|agy|codex|all|auto) ;;
  *) echo "error: --target must be claude|agy|codex|all|auto (got '$TARGET')" >&2; exit 2 ;;
esac
[ -n "$HOME_DIR" ] || { echo "error: HOME is not set; use --home DIR" >&2; exit 2; }

log() { printf '%s\n' "$*"; }
run() {
  if [ "$DRY_RUN" -eq 1 ]; then log "[dry-run] $*"; else "$@"; fi
}

# --- locate source -----------------------------------------------------------
TMP_DIR=""
cleanup() { if [ -n "$TMP_DIR" ]; then rm -rf "$TMP_DIR"; fi; }
trap cleanup EXIT

if [ -z "$SOURCE" ]; then
  SCRIPT_PATH="${BASH_SOURCE[0]:-}"
  if [ -n "$SCRIPT_PATH" ] && [ -f "$SCRIPT_PATH" ]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
    for cand in "$SCRIPT_DIR" "$SCRIPT_DIR/.."; do
      if [ -f "$cand/skill/sfumato/SKILL.md" ]; then SOURCE="$(cd "$cand" && pwd)"; break; fi
    done
  fi
fi

if [ -z "$SOURCE" ]; then
  log "Local checkout not found; downloading $REPO_TARBALL"
  if [ "$DRY_RUN" -eq 1 ]; then
    log "[dry-run] would download and extract $REPO_TARBALL"
    SOURCE="<downloaded-archive>"
  else
    command -v tar >/dev/null 2>&1 || { echo "error: tar is required" >&2; exit 1; }
    TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t sfumato)"
    # Bounded network waits: a stalled peer or proxy must fail within minutes
    # (so the EXIT trap cleans up), never hang silently.
    if command -v curl >/dev/null 2>&1; then
      curl -fsSL --connect-timeout 30 --speed-limit 1 --speed-time 60 --max-time 600 \
        "$REPO_TARBALL" -o "$TMP_DIR/src.tar.gz"
    elif command -v wget >/dev/null 2>&1; then
      # -T is understood by GNU wget and BusyBox; GNU also retries 20x by default.
      wget_opts="-q -T 60"
      # (grep without -q reads all input, so pipefail never sees a SIGPIPE'd wget)
      if wget --help 2>&1 | grep -- '--tries' >/dev/null; then wget_opts="$wget_opts --tries=2"; fi
      # shellcheck disable=SC2086
      wget $wget_opts -O "$TMP_DIR/src.tar.gz" "$REPO_TARBALL"
    else
      echo "error: curl or wget is required to download" >&2; exit 1
    fi
    tar -xzf "$TMP_DIR/src.tar.gz" -C "$TMP_DIR"
    for d in "$TMP_DIR"/*/; do
      if [ -f "${d}skill/sfumato/SKILL.md" ]; then SOURCE="${d%/}"; break; fi
    done
    [ -n "$SOURCE" ] || { echo "error: skill/sfumato not found in downloaded archive" >&2; exit 1; }
  fi
elif [ ! -f "$SOURCE/skill/sfumato/SKILL.md" ]; then
  echo "error: $SOURCE/skill/sfumato/SKILL.md not found" >&2; exit 1
fi
log "Source: $SOURCE"

# --- resolve targets ---------------------------------------------------------
TARGETS=""
case "$TARGET" in
  all) TARGETS="claude agy codex" ;;
  auto)
    [ -d "$HOME_DIR/.claude" ] && TARGETS="$TARGETS claude"
    [ -d "$HOME_DIR/.gemini" ] && TARGETS="$TARGETS agy"
    [ -d "$HOME_DIR/.codex" ] && TARGETS="$TARGETS codex"
    if [ -z "$TARGETS" ]; then log "No agent config dirs detected; defaulting to claude"; TARGETS="claude"; fi ;;
  *) TARGETS="$TARGET" ;;
esac

skill_dest() {
  case "$1" in
    claude) printf '%s' "$HOME_DIR/.claude/skills/sfumato" ;;
    agy)    printf '%s' "$HOME_DIR/.gemini/config/skills/sfumato" ;;
    codex)  printf '%s' "$HOME_DIR/.codex/skills/sfumato" ;;
  esac
}

for t in $TARGETS; do
  dest="$(skill_dest "$t")"
  log "[$t] skill -> $dest"
  # cp copies source permission bits, so a read-only source (Nix store,
  # chmod -R a-w checkout) yields read-only copies. Restore owner write
  # before removing an old install and after copying a new one.
  if [ -L "$dest" ]; then
    run rm -f "$dest"
  elif [ -e "$dest" ]; then
    run chmod -R u+w "$dest"
    run rm -rf "$dest"
  fi
  run mkdir -p "$dest"
  run cp -R "$SOURCE/skill/sfumato/." "$dest/"
  run chmod -R u+w "$dest"
  if [ "$t" = "claude" ]; then
    cmd_dir="$HOME_DIR/.claude/commands"
    if [ "$SOURCE" = "<downloaded-archive>" ]; then
      log "[claude] commands -> $cmd_dir"
      run mkdir -p "$cmd_dir"
      run cp "$SOURCE/commands/*.md" "$cmd_dir/"
    else
      found_cmd=0
      for cmd_src in "$SOURCE"/commands/*.md; do
        [ -f "$cmd_src" ] || continue
        if [ "$found_cmd" -eq 0 ]; then run mkdir -p "$cmd_dir"; found_cmd=1; fi
        cmd_dest="$cmd_dir/$(basename "$cmd_src")"
        log "[claude] command -> $cmd_dest"
        # Replace (not overwrite in place): an earlier copy may be read-only.
        run rm -f "$cmd_dest"
        run cp "$cmd_src" "$cmd_dest"
        run chmod u+w "$cmd_dest"
      done
      if [ "$found_cmd" -eq 0 ]; then
        log "[claude] warning: no $SOURCE/commands/*.md found; skipping slash commands"
      fi
    fi
  fi
done

if [ "$DRY_RUN" -eq 1 ]; then log "Dry run complete. No files were changed."; else log "Sfumato installed for:$TARGETS"; fi
