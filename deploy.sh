#!/usr/bin/env bash
# Build and copy this site to the same destination as the old website.
set -euo pipefail

usage() {
  echo "Usage: $0 [--dry-run | --build-only | --help]"
  echo "  --dry-run     Build, then preview rsync changes (SSH required; no remote writes)."
  echo "  --build-only  Build for Berkeley without connecting to the server."
  echo "  No option     Build and upload, overwriting matching files but deleting none."
}

mode=deploy
if [[ $# -gt 1 ]]; then usage >&2; exit 2; fi
case "${1:-}" in
  '') ;;
  --dry-run) mode=dry-run ;;
  --build-only) mode=build-only ;;
  --help|-h) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_dir"
build_dir="$repo_dir/_site_berkeley"
destination='watson.millennium.berkeley.edu:~/public_html/'

# Prefer the Ruby/Bundler installation used to refresh this site on this Mac.
# On other machines, use the bundle command from the configured Ruby environment.
bundle_command=(bundle)
if [[ -x /opt/homebrew/opt/ruby@3.2/bin/ruby && -f vendor/tooling/gems/bundler-2.6.2/exe/bundle ]]; then
  export GEM_HOME="$repo_dir/vendor/tooling"
  export GEM_PATH="$repo_dir/vendor/tooling"
  export PATH="/opt/homebrew/opt/ruby@3.2/bin:$PATH"
  bundle_command=(/opt/homebrew/opt/ruby@3.2/bin/ruby vendor/tooling/gems/bundler-2.6.2/exe/bundle)
elif ! command -v bundle >/dev/null 2>&1; then
  echo "Bundler is required. Install Ruby 3.2 and run bundle install (see README.md)." >&2
  exit 1
fi

if [[ "$mode" != build-only ]]; then
  command -v rsync >/dev/null 2>&1 || { echo "rsync is required." >&2; exit 1; }
  command -v ssh >/dev/null 2>&1 || { echo "ssh is required." >&2; exit 1; }
fi

# Keep production canonical metadata, but make local navigation work beneath
# /~jegonzal/. A separate output directory leaves the local preview untouched.
JEKYLL_ENV=production BUNDLE_FROZEN=true "${bundle_command[@]}" exec jekyll build \
  --baseurl /~jegonzal --destination "$build_dir"
[[ -s "$build_dir/index.html" ]] || { echo "Build has no index.html; refusing upload." >&2; exit 1; }

if [[ "$mode" == build-only ]]; then
  echo "Berkeley build ready: $build_dir"
  exit 0
fi

# Preserve file modes and timestamps without trying to copy local ownership or
# group membership, which can fail on the Berkeley server (including backups).
backup_dir="/home/eecs/jegonzal/website-backups/$(date -u +%Y%m%dT%H%M%SZ)-$$"
rsync_options=(-rlptDvh --itemize-changes --exclude=CNAME
  --backup "--backup-dir=$backup_dir")
if [[ "$mode" == dry-run ]]; then rsync_options+=(--dry-run); fi
echo "Destination: $destination"
# Deliberately no --delete: preserve older papers, course pages, and other files.
rsync "${rsync_options[@]}" "$build_dir/" "$destination"
if [[ "$mode" == dry-run ]]; then
  echo "Preview complete; no remote files changed. Run ./deploy.sh to upload."
else
  echo "Uploaded to https://people.eecs.berkeley.edu/~jegonzal/"
  echo "Replaced files backed up on the server in: $backup_dir"
fi
