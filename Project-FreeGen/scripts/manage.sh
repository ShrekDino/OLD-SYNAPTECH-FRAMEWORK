#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build"

usage() {
    cat <<EOF
FreeGen Development Manager

Usage: ./manage.sh <command>

Commands:
    build [debug|release|ci]  Build the project (default: debug)
    run                        Run the application
    test                       Run tests
    clean                      Clean build artifacts
    shell                      Enter Docker dev shell
    docs                       Build documentation
    format                     Format code with clang-format
    lint                       Run clang-tidy
    install                    Install system dependencies
EOF
    exit 1
}

ensure_cmake() {
    if ! command -v cmake &>/dev/null; then
        echo "Error: cmake not found. Install it first."
        exit 1
    fi
}

cmd_build() {
    ensure_cmake
    local preset="${1:-debug}"
    echo "Building with preset: ${preset}"
    cmake --preset "${preset}"
    cmake --build "${BUILD_DIR}/${preset}" -j"$(nproc)"
}

cmd_run() {
    local preset="${1:-debug}"
    if [ ! -f "${BUILD_DIR}/${preset}/src/freegen" ]; then
        cmd_build "${preset}"
    fi
    exec "${BUILD_DIR}/${preset}/src/freegen" "$@"
}

cmd_test() {
    ensure_cmake
    cmd_build ci
    cd "${BUILD_DIR}/ci"
    ctest --output-on-failure
}

cmd_clean() {
    rm -rf "${BUILD_DIR}"
    echo "Cleaned build directory"
}

cmd_shell() {
    docker compose -f "${SCRIPT_DIR}/docker-compose.yml" run --rm shell
}

cmd_docs() {
    if command -v doxygen &>/dev/null; then
        doxygen docs/Doxyfile 2>/dev/null || true
    fi
    if command -v mkdocs &>/dev/null; then
        mkdocs build --config-file "${SCRIPT_DIR}/mkdocs.yml" 2>/dev/null || true
    fi
    echo "Documentation built"
}

cmd_format() {
    if command -v clang-format &>/dev/null; then
        find "${SCRIPT_DIR}/src" "${SCRIPT_DIR}/include" -name '*.cpp' -o -name '*.hpp' | \
            xargs clang-format -i -style=file
        echo "Formatted source files"
    else
        echo "clang-format not found"
    fi
}

cmd_lint() {
    if command -v clang-tidy &>/dev/null; then
        ensure_cmake
        cmake --preset debug
        run-clang-tidy -p "${BUILD_DIR}/debug" 2>/dev/null || true
    else
        echo "clang-tidy not found"
    fi
}

cmd_install() {
    if command -v apt-get &>/dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            build-essential cmake pkg-config \
            libvulkan-dev libsdl2-dev \
            libpipewire-0.3-dev libdbus-1-dev \
            glslang-tools clang-format clang-tidy \
            doxygen python3-pip
        pip3 install mkdocs mkdocs-material
    else
        echo "Unsupported package manager"
        exit 1
    fi
}

[ $# -eq 0 ] && usage

case "$1" in
    build) cmd_build "${2:-debug}" ;;
    run) shift; cmd_run "${2:-debug}" "$@" ;;
    test) cmd_test ;;
    clean) cmd_clean ;;
    shell) cmd_shell ;;
    docs) cmd_docs ;;
    format) cmd_format ;;
    lint) cmd_lint ;;
    install) cmd_install ;;
    *) usage ;;
esac
