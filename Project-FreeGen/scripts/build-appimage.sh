#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build/appimage"
APP_DIR="${BUILD_DIR}/AppDir"

echo "Building FreeGen AppImage..."

cmake -S "${SCRIPT_DIR}" -B "${BUILD_DIR}" \
    -DCMAKE_BUILD_TYPE=Release \
    -DFREEGEN_ENABLE_TESTS=OFF

cmake --build "${BUILD_DIR}" -j"$(nproc)"

mkdir -p "${APP_DIR}/usr/bin"
cp "${BUILD_DIR}/src/freegen" "${APP_DIR}/usr/bin/"

mkdir -p "${APP_DIR}/usr/share/applications"
cat > "${APP_DIR}/usr/share/applications/freegen.desktop" <<EOF
[Desktop Entry]
Name=FreeGen
Comment=Open-source screen capture upscaling and frame generation
Exec=freegen
Icon=freegen
Terminal=false
Type=Application
Categories=Game;Graphics;Utility;
EOF

mkdir -p "${APP_DIR}/usr/share/icons/hicolor/256x256/apps"
# Placeholder icon - replace with actual icon in production
convert -size 256x256 xc:blue "${APP_DIR}/usr/share/icons/hicolor/256x256/apps/freegen.png" 2>/dev/null || true

if command -v appimagetool &>/dev/null; then
    appimagetool "${APP_DIR}" "freegen-x86_64.AppImage"
    echo "AppImage build complete: freegen-x86_64.AppImage"
else
    echo "appimagetool not found. Install it from https://github.com/AppImage/AppImageKit"
    echo "AppDir prepared at: ${APP_DIR}"
fi
