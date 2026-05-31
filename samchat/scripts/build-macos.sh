#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

VERSION="${1:-$(grep '^version: ' pubspec.yaml | sed 's/version: //')}"
echo "=== Building macOS v$VERSION ==="

export PATH="${FLUTTER_HOME:-$HOME/flutter}/bin:$PATH"

flutter clean
flutter pub get

echo "--- Building macOS release ---"
flutter build macos --release \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}

OUTPUT_DIR="build/release/v$VERSION"
mkdir -p "$OUTPUT_DIR"

APP_BUNDLE="build/macos/Build/Products/Release/SamChat.app"
DMG="$OUTPUT_DIR/SamChat-v$VERSION-macos.dmg"

if command -v create-dmg &>/dev/null; then
  create-dmg \
    --volname "SamChat v$VERSION" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --app-drop-link 450 170 \
    "$DMG" "$APP_BUNDLE"
elif command -v hdiutil &>/dev/null; then
  STAGING="build/release/staging"
  mkdir -p "$STAGING"
  cp -R "$APP_BUNDLE" "$STAGING/"
  hdiutil create -volname "SamChat v$VERSION" \
    -srcfolder "$STAGING" \
    -ov -format UDZO "$DMG"
  rm -rf "$STAGING"
else
  echo "WARNING: No DMG tool found. Zipping .app bundle instead."
  zip -r "$OUTPUT_DIR/SamChat-v$VERSION-macos.zip" "$APP_BUNDLE"
fi

echo "=== macOS build complete ==="
ls -lh "$OUTPUT_DIR/"*.dmg "$OUTPUT_DIR/"*.zip 2>/dev/null || true
