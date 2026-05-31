#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

VERSION="${1:-$(grep '^version: ' pubspec.yaml | sed 's/version: //')}"
echo "=== Building Android v$VERSION ==="

export ANDROID_HOME="${ANDROID_HOME:-$HOME/Android/Sdk}"
export JAVA_HOME="${JAVA_HOME:-$HOME/jdk21}"
export PATH="${FLUTTER_HOME:-$HOME/flutter}/bin:$PATH"

flutter clean
flutter pub get

OUTPUT_DIR="build/release/v$VERSION"
mkdir -p "$OUTPUT_DIR"

echo "--- Building universal APK ---"
flutter build apk --release --no-tree-shake-icons \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}
cp build/app/outputs/flutter-apk/app-release.apk \
  "$OUTPUT_DIR/SamChat-v$VERSION-universal.apk"

echo "--- Building split-per-abi APKs ---"
flutter build apk --release --split-per-abi --no-tree-shake-icons \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}
for abi in arm64-v8a armeabi-v7a x86_64; do
  src="build/app/outputs/flutter-apk/app-$abi-release.apk"
  if [ -f "$src" ]; then
    cp "$src" "$OUTPUT_DIR/SamChat-v$VERSION-$abi.apk"
  fi
done

echo "--- Building App Bundle ---"
flutter build appbundle --release \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}
cp build/app/outputs/bundle/release/app-release.aab \
  "$OUTPUT_DIR/SamChat-v$VERSION.aab"

echo "=== Android builds complete ==="
ls -lh "$OUTPUT_DIR/"*.apk "$OUTPUT_DIR/"*.aab
