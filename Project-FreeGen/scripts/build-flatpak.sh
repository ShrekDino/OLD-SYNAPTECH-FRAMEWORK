#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANIFEST="${SCRIPT_DIR}/flatpak/io.github.freegen.yml"

if ! command -v flatpak-builder &>/dev/null; then
    echo "Error: flatpak-builder not found."
    echo "Install it: sudo apt install flatpak flatpak-builder"
    exit 1
fi

echo "Building FreeGen Flatpak..."
flatpak-builder --force-clean \
    --install-deps-from=flathub \
    --repo=freegen-repo \
    build-dir \
    "${MANIFEST}"

echo "Creating Flatpak bundle..."
flatpak build-bundle freegen-repo freegen.flatpak io.github.freegen

echo "Flatpak build complete: freegen.flatpak"
