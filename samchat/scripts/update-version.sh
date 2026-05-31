#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

CURRENT_VERSION="$(grep '^version: ' pubspec.yaml | sed 's/version: //')"

if [ $# -ne 1 ]; then
  echo "Current version: $CURRENT_VERSION"
  echo "Usage: $0 <new_version>"
  echo "  e.g. $0 0.6.1"
  exit 1
fi

NEW_VERSION="$1"

# Validate semver
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
  echo "Error: version must be semver (e.g. 0.6.1)"
  exit 1
fi

echo "Bumping version: $CURRENT_VERSION → $NEW_VERSION"

# Update pubspec.yaml
sed -i "s/^version: $CURRENT_VERSION/version: $NEW_VERSION/" pubspec.yaml

# Update device_identity.dart default
sed -i "s/appVersion = '[0-9.]*'/appVersion = '$NEW_VERSION'/" \
  lib/core/models/device_identity.dart

# Update settings_screen.dart license page version
sed -i "s/applicationVersion: '[0-9.]*'/applicationVersion: '$NEW_VERSION'/" \
  lib/features/settings/widgets/settings_screen.dart

echo "Version bumped to $NEW_VERSION"
echo ""
echo "Files updated:"
grep -n "version:" pubspec.yaml
grep -n "appVersion" lib/core/models/device_identity.dart
grep -n "applicationVersion" lib/features/settings/widgets/settings_screen.dart
