#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

CURRENT_VERSION="$(grep '^version: ' pubspec.yaml | sed 's/version: //')"
echo "=== SamChat Release v$CURRENT_VERSION ==="
echo ""

# ---------------------------------------------------------------
# 1. Check for uncommitted changes
# ---------------------------------------------------------------
if [ -n "$(git status --porcelain)" ]; then
  echo "ERROR: You have uncommitted changes. Commit or stash them first."
  git status --short
  exit 1
fi

# ---------------------------------------------------------------
# 2. Prompt for version bump
# ---------------------------------------------------------------
echo "Current version: $CURRENT_VERSION"
read -r -p "New version (or press Enter to keep $CURRENT_VERSION): " NEW_VERSION
NEW_VERSION="${NEW_VERSION:-$CURRENT_VERSION}"

if [ "$NEW_VERSION" != "$CURRENT_VERSION" ]; then
  "$SCRIPT_DIR/update-version.sh" "$NEW_VERSION"
  git add -A
  git commit -m "chore: bump to v$NEW_VERSION"
  echo "Committed version bump."
fi

FINAL_VERSION="$NEW_VERSION"

# ---------------------------------------------------------------
# 3. Update AGENTS.md and PROJECT.md state files
# ---------------------------------------------------------------
echo ""
echo "=== Next: Update AGENTS.md and PROJECT.md with current state ==="
echo "Open these files and update the 'Current State' / 'Working' sections."
read -r -p "Press Enter when done updating documentation, or Ctrl+C to abort: " _

git add -A
git commit --allow-empty -m "docs: update project state for v$FINAL_VERSION" || true

# ---------------------------------------------------------------
# 4. Create signed tag
# ---------------------------------------------------------------
TAG="v$FINAL_VERSION"
if git tag -l "$TAG" | grep -q .; then
  echo "Tag $TAG already exists. Delete and retag? (y/N)"
  read -r response
  if [ "$response" = "y" ]; then
    git tag -d "$TAG"
    git tag -s "$TAG" -m "v$FINAL_VERSION"
  fi
else
  git tag -s "$TAG" -m "v$FINAL_VERSION"
fi

# ---------------------------------------------------------------
# 5. Build all available platforms
# ---------------------------------------------------------------
echo ""
echo "=== Building artifacts for v$FINAL_VERSION ==="

# Detect available platforms
AVAILABLE=""
if [[ "$(uname)" == "Linux" ]]; then
  if flutter devices 2>/dev/null | grep -qi "linux"; then
    AVAILABLE="$AVAILABLE linux"
  fi
  AVAILABLE="$AVAILABLE android"
fi
if [[ "$(uname)" == "Darwin" ]]; then
  AVAILABLE="$AVAILABLE macos ios android"
fi
if [[ "$(uname)" == "MINGW"* ]] || [[ "$(uname)" == "MSYS"* ]]; then
  AVAILABLE="$AVAILABLE windows"
fi

echo "Platforms to build:${AVAILABLE:- none}"

for platform in $AVAILABLE; do
  case "$platform" in
    android) "$SCRIPT_DIR/build-android.sh" "$FINAL_VERSION" ;;
    linux)   "$SCRIPT_DIR/build-linux.sh" "$FINAL_VERSION" ;;
    windows) "$SCRIPT_DIR/build-windows.sh" "$FINAL_VERSION" ;;
    macos)   "$SCRIPT_DIR/build-macos.sh" "$FINAL_VERSION" ;;
  esac
done

# ---------------------------------------------------------------
# 6. Generate checksums
# ---------------------------------------------------------------
OUTPUT_DIR="build/release/v$FINAL_VERSION"
CHECKSUM_FILE="$OUTPUT_DIR/SHA256SUMS.txt"

if [ -d "$OUTPUT_DIR" ]; then
  echo "=== Generating checksums ==="
  (cd "$OUTPUT_DIR" && sha256sum -- * > "$CHECKSUM_FILE")
  cat "$CHECKSUM_FILE"
fi

# ---------------------------------------------------------------
# 7. Push
# ---------------------------------------------------------------
echo ""
echo "=== Ready to push ==="
echo "Commits to push:"
git log --oneline "@{u}..HEAD" 2>/dev/null || echo "(no upstream tracking)"
echo ""
read -r -p "Push commits and tags? (y/N): " PUSH
if [ "$PUSH" = "y" ]; then
  git push
  git push --tags
  echo "Pushed."
fi

# ---------------------------------------------------------------
# 8. Create GitHub Release
# ---------------------------------------------------------------
if command -v gh &>/dev/null; then
  echo ""
  read -r -p "Create GitHub Release? (y/N): " GH
  if [ "$GH" = "y" ]; then
    NOTES=$(sed -n "/^## \[$FINAL_VERSION\]/,/^## \[/p" CHANGELOG.md | head -n -2)
    if [ -d "$OUTPUT_DIR" ]; then
      gh release create "$TAG" \
        --title "v$FINAL_VERSION" \
        --notes "$NOTES" \
        "$OUTPUT_DIR"/*
    else
      gh release create "$TAG" \
        --title "v$FINAL_VERSION" \
        --notes "$NOTES"
    fi
    echo "GitHub Release created."
  fi
else
  echo "gh CLI not found. Create the release manually at:"
  echo "  https://github.com/$(git config --get remote.origin.url | sed 's/.*://;s/\.git$//')/releases/new?tag=$TAG"
fi

echo ""
echo "=== Release v$FINAL_VERSION complete ==="
