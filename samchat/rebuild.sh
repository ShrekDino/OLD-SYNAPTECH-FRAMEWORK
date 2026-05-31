#!/bin/bash
set -euo pipefail

echo "=== Purging Corrupted Local Caches ==="
flutter clean
flutter pub get

echo "=== Packaging Resilient Release APK for Pixel 6 ==="
export ANDROID_HOME=~/Android/Sdk
export JAVA_HOME=~/jdk21
export PATH="$HOME/flutter/bin:$PATH"

# Pass GITHUB_PAT via --dart-define for crash reporting
flutter build apk --release --no-tree-shake-icons \
  ${GITHUB_PAT:+--dart-define=GITHUB_PAT=$GITHUB_PAT}

echo "=== Done ==="
echo "APK: build/app/outputs/flutter-apk/app-release.apk"
