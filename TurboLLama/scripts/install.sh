# NOTE: Patch 007 (qwen35moe-mtp) copies a model file from the TurboQuant clone into the Ollama tree before patching.
# Report issues at https://github.com/ShrekDino/TurboLLama/issues

#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
info()  { echo -e "${CYAN}==>${NC} $*"; }
ok()    { echo -e "${GREEN}  ✓${NC} $*"; }
warn()  { echo -e "${YELLOW}  ⚠${NC} $*"; }
err()   { echo -e "${RED}  ✗${NC} $*" >&2; }

TURBO_DIR="${TURBO_DIR:-$HOME/turbo}"
OLLAMA_REPO="https://github.com/ollama/ollama.git"
TURBOQUANT_REPO="https://github.com/TheTom/llama-cpp-turboquant.git"
PATCHES_URL="https://raw.githubusercontent.com/ShrekDino/TurboLLama/main/patches"
CUDA_PATH=""  # auto-detect below

echo -e "${CYAN}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║        TurboLLama Installer              ║"
echo "  ║  Ollama-compatible · TurboQuant-powered  ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ── Parse CLI args ───────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cuda-path) CUDA_PATH="$2"; shift 2 ;;
        *) shift ;;
    esac
done

# ── CUDA auto-detection ─────────────────────────────────────
info "Checking prerequisites..."

if [ -z "$CUDA_PATH" ]; then
    CUDA_CANDIDATES=(
        /opt/cuda /usr/local/cuda /usr/local/cuda-13 /usr/local/cuda-12
        /usr/lib/cuda /usr/lib/x86_64-linux-gnu/cuda
    )
    for candidate in "${CUDA_CANDIDATES[@]}"; do
        if [ -x "$candidate/bin/nvcc" ]; then
            CUDA_PATH="$candidate"
            break
        fi
    done
fi

if [ -n "$CUDA_PATH" ]; then
    export PATH="$CUDA_PATH/bin:$PATH"
    export CUDAToolkit_ROOT="$CUDA_PATH"
    ok "CUDA found at $CUDA_PATH"
elif command -v nvcc >/dev/null 2>&1; then
    CUDA_PATH=$(dirname "$(dirname "$(command -v nvcc)")")
    export CUDAToolkit_ROOT="$CUDA_PATH"
    ok "CUDA found at $CUDA_PATH"
else
    err "CUDA Toolkit not found!"
    err "Install: sudo apt install nvidia-cuda-toolkit (or pacman -S cuda)"
    err "Or pass the path: curl ... | sh -s -- --cuda-path /opt/cuda"
    exit 1
fi

command -v go    >/dev/null 2>&1 || { err "Go is required: apt install golang-go (or pacman -S go)"; exit 1; }
command -v cmake >/dev/null 2>&1 || { err "CMake is required: apt install cmake"; exit 1; }
command -v git   >/dev/null 2>&1 || { err "Git is required: apt install git"; exit 1; }

ok "Go $(go version | grep -oP '\d+\.\d+\.\d+' | head -1)"
ok "CMake $(cmake --version | head -1 | grep -oP '\d+\.\d+\.\d+')"
ok "Git $(git --version | grep -oP '\d+\.\d+\.\d+')"
ok "CUDA $($CUDA_PATH/bin/nvcc --version | grep release | grep -oP '\d+\.\d+')"

# ── Find CUDA-compatible host compiler ─────────────────────
# CUDA 13.x supports GCC up to ~14. Newer GCC causes compilation errors.
CUDA_HOST_COMPILER=""
for candidate in g++-15 g++-14 g++-13 clang++ g++; do
    if command -v "$candidate" >/dev/null 2>&1; then
        # Test if this compiler works with nvcc
        echo 'int main(){}' > /tmp/.cuda_test.cu
        if "$CUDA_PATH/bin/nvcc" -ccbin "$candidate" -c /tmp/.cuda_test.cu -o /tmp/.cuda_test.o 2>/dev/null; then
            CUDA_HOST_COMPILER="$candidate"
            rm -f /tmp/.cuda_test.cu /tmp/.cuda_test.o
            break
        fi
        rm -f /tmp/.cuda_test.cu /tmp/.cuda_test.o
    fi
done
if [ -n "$CUDA_HOST_COMPILER" ]; then
    ok "CUDA host compiler: $CUDA_HOST_COMPILER"
else
    warn "Could not find a CUDA-compatible host compiler. Trying default (may fail)."
fi

# ── Clean workspace ───────────────────────────────────────────
info "Preparing workspace at ${TURBO_DIR}..."
mkdir -p "$TURBO_DIR"

# ── Clone repos ───────────────────────────────────────────────
if [ ! -d "$TURBO_DIR/ollama" ]; then
    info "Cloning Ollama..."
    git clone --depth 1 "$OLLAMA_REPO" "$TURBO_DIR/ollama"
    ok "Ollama cloned"
else
    ok "Ollama already cloned"
fi

if [ ! -d "$TURBO_DIR/turboquant" ]; then
    info "Cloning TurboQuant llama.cpp..."
    git clone --depth 1 --branch feature/turboquant-kv-cache "$TURBOQUANT_REPO" "$TURBO_DIR/turboquant"
    ok "TurboQuant cloned"
else
    ok "TurboQuant already cloned"
fi

# ── Apply patches ─────────────────────────────────────────────
info "Applying patches..."

apply_patch() {
    local num="$1" name="$2" target="$3"
    # Use local patches from the cloned repo first, fall back to CDN
    local SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
    local patch_file="${SCRIPT_DIR}/../patches/${num}-${name}.patch"
    if [ ! -f "$patch_file" ]; then
        patch_file="/tmp/turbo_patch_${num}"
        curl -fsSL "${PATCHES_URL}/${num}-${name}.patch" -o "$patch_file"
    fi
    (cd "$target" && patch -p1 -N < "$patch_file" 2>/dev/null) && ok "Patch ${num} applied" || warn "Patch ${num} already applied (or skipped)"
}

# All patch paths are relative to the Ollama repo root (e.g. ml/backend/ggml/...)
OLLAMA_ROOT="$TURBO_DIR/ollama"
apply_patch "001" "ggml-h-types"          "$OLLAMA_ROOT"
apply_patch "002" "ggml-common-blocks"    "$OLLAMA_ROOT"
apply_patch "003" "ggml-c-type-traits"    "$OLLAMA_ROOT"
apply_patch "004" "llama-context-head-dim" "$OLLAMA_ROOT"
apply_patch "005" "llama-kv-cache"        "$OLLAMA_ROOT"
apply_patch "006" "expert-cache"          "$OLLAMA_ROOT"
# Patch 007 (qwen35moe MTP) requires extensive TurboQuant infrastructure not present in Ollama.
# MTP speculative decoding is disabled by default. Skipping.
warn "Patch 007 (MTP speculative decode) skipped — requires full TurboQuant model support"
apply_patch "008" "ollama-go-fa-bypass"   "$OLLAMA_ROOT"
apply_patch "009" "cmake-duplicate-target" "$OLLAMA_ROOT"

# ── Build ggml-cuda ──────────────────────────────────────────
info "Building TurboQuant ggml-cuda (this will take a while)..."

cd "$TURBO_DIR/ollama"
mkdir -p build
CUDA_HOST_FLAG=""
if [ -n "$CUDA_HOST_COMPILER" ]; then
    CUDA_HOST_FLAG="-DCMAKE_CUDA_HOST_COMPILER=${CUDA_HOST_COMPILER}"
fi
cmake -B build \
    -DGGML_CUDA=ON \
    -DGGML_CUDA_FA=ON \
    -DGGML_CUDA_FA_ALL_QUANTS=ON \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_COMPILER="${CUDA_PATH}/bin/nvcc" \
    ${CUDA_HOST_FLAG} \
    -DCUDAToolkit_ROOT="${CUDA_PATH}" \
    2>&1 | tail -5

cmake --build build --target ggml-cuda -j$(nproc) 2>&1 | tail -5
ok "TurboQuant ggml-cuda built"

# ── Build Ollama Go binary ────────────────────────────────────
info "Building Ollama Go binary..."

export GGML_CUDA=ON
export GGML_CUDA_FA=ON
go build -o "$TURBO_DIR/ollama-turboquant" . 2>&1 | tail -3
ok "TurboLLama binary built: $TURBO_DIR/ollama-turboquant"

# ── Install ───────────────────────────────────────────────────
info "Installing to /usr/local/bin..."

if [ -w /usr/local/bin ]; then
    cp "$TURBO_DIR/ollama-turboquant" /usr/local/bin/ollama
else
    sudo cp "$TURBO_DIR/ollama-turboquant" /usr/local/bin/ollama
fi
ok "Installed /usr/local/bin/ollama"

# ── Systemd service ───────────────────────────────────────────
info "Setting up systemd service..."

SERVICE_FILE="/tmp/turbo_service"
cat > "$SERVICE_FILE" << 'SERVICEEOF'
[Unit]
Description=TurboLLama - Ollama with TurboQuant
After=network.target

[Service]
ExecStart=/usr/local/bin/ollama serve
Environment=OLLAMA_KV_CACHE_TYPE=turbo3
Environment=OLLAMA_FLASH_ATTENTION=0
Environment=OLLAMA_MODELS=%h/.ollama/models
Environment=OLLAMA_KEEP_ALIVE=5m
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICEEOF

sudo cp "$SERVICE_FILE" /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
ok "Systemd service installed"

# ── Done ──────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}  ✅ TurboLLama installed!${NC}"
echo ""
echo "  Start the server:"
echo "    sudo systemctl enable --now ollama"
echo ""
echo "  Use it:"
echo "    export OLLAMA_KV_CACHE_TYPE=turbo3"
echo "    ollama run qwen3.6:35b-a3b"
echo ""
echo "  Or with flash attention:"
echo "    export OLLAMA_KV_CACHE_TYPE=turbo3"
echo "    export OLLAMA_FLASH_ATTENTION=1"
echo "    ollama run qwen3.6:35b-a3b"
echo ""
