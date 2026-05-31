#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

VERSION="${1:-$(grep '^version: ' pubspec.yaml | sed 's/version: //')}"
echo "=== Building Windows v$VERSION ==="

export PATH="${FLUTTER_HOME:-$HOME/flutter}/bin:$PATH"

flutter clean
flutter pub get

echo "--- Building Windows release ---"
flutter build windows --release \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}

OUTPUT_DIR="build/release/v$VERSION"
mkdir -p "$OUTPUT_DIR"

BUILD_DIR="build/windows/x64/runner/Release"
ZIPFILE="$OUTPUT_DIR/SamChat-v$VERSION-win64.zip"

if command -v 7z &>/dev/null; then
  7z a -tzip "$ZIPFILE" "$BUILD_DIR"/*
elif command -v zip &>/dev/null; then
  (cd "$BUILD_DIR" && zip -r "$ZIPFILE" .)
fi

echo "=== Windows build complete ==="
ls -lh "$ZIPFILE"
