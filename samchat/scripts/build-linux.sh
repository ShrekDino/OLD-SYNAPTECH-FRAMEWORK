#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

VERSION="${1:-$(grep '^version: ' pubspec.yaml | sed 's/version: //')}"
echo "=== Building Linux v$VERSION ==="

export PATH="${FLUTTER_HOME:-$HOME/flutter}/bin:$PATH"

flutter clean
flutter pub get

echo "--- Building Linux release ---"
flutter build linux --release \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}

OUTPUT_DIR="build/release/v$VERSION"
mkdir -p "$OUTPUT_DIR"

BUNDLE_DIR="build/linux/x86_64/release/bundle"
TARBALL="$OUTPUT_DIR/SamChat-v$VERSION-linux-x86_64.tar.gz"

tar czf "$TARBALL" -C "$(dirname "$BUNDLE_DIR")" "$(basename "$BUNDLE_DIR")"

echo "=== Linux build complete ==="
ls -lh "$TARBALL"
