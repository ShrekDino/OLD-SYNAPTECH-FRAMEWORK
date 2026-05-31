#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$(dirname "$SCRIPT_DIR")"
source "$SCRIPT_DIR/lib/log.sh"

select_model() {
    case "${1:-0}" in
        24) MODEL_NAME="Qwen3.6-27B-Q4_K_M.gguf"
            MODEL_URL="https://huggingface.co/unsloth/Qwen3.6-27B-GGUF/resolve/main/Qwen3.6-27B-Q4_K_M.gguf"
            MODEL_ACCURACY="full"
            _MODEL_LABEL="Qwen3.6-27B-Q4_K_M (~15GB) [GPU 24GB+ — full accuracy]" ;;
        16) MODEL_NAME="Qwen3.6-27B-UD-IQ3_XXS.gguf"
            MODEL_URL="https://huggingface.co/unsloth/Qwen3.6-27B-GGUF/resolve/main/Qwen3.6-27B-UD-IQ3_XXS.gguf"
            MODEL_ACCURACY="lower"
            _MODEL_LABEL="Qwen3.6-27B-UD-IQ3_XXS (~12GB) [GPU 16GB — lower accuracy]" ;;
        12) MODEL_NAME="Qwen3.5-9B-Q4_K_M.gguf"
            MODEL_URL="https://huggingface.co/unsloth/Qwen3.5-9B-GGUF/resolve/main/Qwen3.5-9B-Q4_K_M.gguf"
            MODEL_ACCURACY="lower"
            _MODEL_LABEL="Qwen3.5-9B-Q4_K_M (~5GB) [GPU 12GB — lower accuracy]" ;;
        *)
            MODEL_NAME="Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf"
            MODEL_URL="https://huggingface.co/unsloth/Qwen3.6-35B-A3B-GGUF/resolve/main/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf"
            MODEL_ACCURACY="standard"
            _MODEL_LABEL="Qwen3.6-35B-A3B (~17.6GB) [CPU]" ;;
    esac
    MODEL_ALIAS="${MODEL_NAME%.gguf}"
}

if command -v docker &>/dev/null && ! docker info &>/dev/null 2>&1; then
    if id -nG 2>/dev/null | grep -qw docker; then
        if command -v sg &>/dev/null && sg docker -c "docker info" &>/dev/null 2>&1; then
            info "Re-launching with docker group active..."
            exec sg docker -- bash "$0" "$@"
        else
            err "Docker group membership exists but sg activation failed."
            err "Run: newgrp docker"
            err "Then resume: $INSTALL_DIR/openmono setup"
            exit 1
        fi
    fi
fi

if [[ -n "${OPENMONO_ENV_FILE:-}" ]] && [[ -f "$OPENMONO_ENV_FILE" ]]; then
    source "$OPENMONO_ENV_FILE"
fi

role_prompt

case "$OPENMONO_ROLE" in
    full|inference|agent|ollama) ;;
    *) echo "ERROR: Invalid OPENMONO_ROLE='$OPENMONO_ROLE' (expected: full, inference, agent, ollama)" >&2; exit 1 ;;
esac

case "$OPENMONO_ROLE" in
    full)      TOTAL_STEPS=8 ;;
    inference) TOTAL_STEPS=7 ;;
    agent)     TOTAL_STEPS=5 ;;
    ollama)    TOTAL_STEPS=4 ;;
esac

banner "OpenMono.ai Installer — Arch Linux (role: $OPENMONO_ROLE)"

CURRENT_STEP=0
next_step() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    step $CURRENT_STEP $TOTAL_STEPS "$1"
}

check_prerequisites() {
    local missing=()
    local warnings=()

    command -v docker &>/dev/null || missing+=("docker")
    command -v git &>/dev/null || missing+=("git")
    command -v curl &>/dev/null || missing+=("curl")

    if ! docker compose version &>/dev/null 2>&1 && ! docker-compose version &>/dev/null 2>&1; then
        missing+=("docker-compose")
    fi

    if command -v docker &>/dev/null; then
        if ! docker info &>/dev/null 2>&1; then
            if id -nG 2>/dev/null | grep -qw docker; then
                warnings+=("Docker group not active. Run: newgrp docker")
            else
                warnings+=("User not in docker group. Run: sudo usermod -aG docker \$USER && newgrp docker")
            fi
        fi
    fi

    if ! command -v dotnet &>/dev/null; then
        warnings+=(".NET SDK not installed")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        err "Missing required prerequisites:"
        for pkg in "${missing[@]}"; do
            printf "  ${RED}✗${NC}  %s\n" "$pkg"
        done
        echo ""
        die "Run install_prereqs_arch.sh first."
    fi

    if [ ${#warnings[@]} -gt 0 ]; then
        warn "Prerequisite warnings:"
        for w in "${warnings[@]}"; do
            printf "  ${YELLOW}⚠${NC}  %s\n" "$w"
        done
        echo ""
    fi

    ok "All prerequisites satisfied"
}

info "Checking prerequisites..."
check_prerequisites

next_step "Resolving install directory"

if [ -f "$SCRIPT_DIR/../OpenMono.sln" ]; then
    INSTALL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
elif [ -n "${OPENMONO_HOME:-}" ]; then
    INSTALL_DIR="$OPENMONO_HOME"
else
    INSTALL_DIR="$HOME/openmono.ai"
fi

ok "Install directory: $INSTALL_DIR"

next_step "Checking system requirements"

_VRAM_MB=0
_GPU_TIER=0
MODEL_NAME=""
MODEL_ACCURACY=""
MODEL_ALIAS=""

if [ "$OPENMONO_ROLE" = "ollama" ]; then
    info "Ollama provider mode — skipping model detection"
    ok "Ollama mode selected"

    if curl -sf http://localhost:11434/api/tags &>/dev/null; then
        ok "Ollama server reachable at http://localhost:11434"
        _ollama_models=$(curl -sf http://localhost:11434/api/tags 2>/dev/null | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    models = [m['name'] for m in d.get('models', [])]
    print('\n'.join(models[:5]))
except: pass
" 2>/dev/null || true)
        if [[ -n "$_ollama_models" ]]; then
            info "Available models:"
            echo "$_ollama_models" | while read -r m; do printf "     ${DIM}• ${m}${NC}\n"; done
        fi
    else
        warn "Ollama server not reachable at http://localhost:11434"
        warn "Make sure Ollama is running: systemctl --user start ollama"
    fi
elif [ "$OPENMONO_ROLE" != "agent" ]; then
    if [ "${GPU_MODE:-0}" = "1" ]; then
        if command -v nvidia-smi &>/dev/null; then
            _VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | awk 'NR==1{print $1}')
            _VRAM_MB=${_VRAM_MB:-0}
            if   [ "$_VRAM_MB" -ge 24000 ]; then _GPU_TIER=24
            elif [ "$_VRAM_MB" -ge 16000 ]; then _GPU_TIER=16
            elif [ "$_VRAM_MB" -ge 12000 ]; then _GPU_TIER=12
            else
                warn "Only $(( (_VRAM_MB + 512) / 1024 ))GB VRAM — falling back to CPU mode"
                GPU_MODE=0
            fi
        else
            warn "GPU mode but nvidia-smi not found. Falling back to CPU."
            GPU_MODE=0
        fi
    fi
    select_model "$_GPU_TIER"
    ok "Model selected: $MODEL_NAME"
fi

detail "docker: $(docker --version 2>/dev/null | head -1)"
detail "git: $(git --version 2>/dev/null)"
detail "curl: $(curl --version 2>/dev/null | head -1)"

ok "System requirements verified"

next_step "Building Docker image"

cd "$INSTALL_DIR/docker"
info "Stopping any running containers..."
run docker compose down || true

if [ "$OPENMONO_ROLE" = "ollama" ]; then
    info "Building agent image (Ollama provider mode)..."
    if ! run docker compose build agent; then
        die "agent build failed"
    fi
    ok "Agent image built"
elif [ "$OPENMONO_ROLE" != "agent" ]; then
    info "Building llama-server image..."
    if ! run docker compose build llama-server; then
        die "llama-server build failed"
    fi
    ok "llama-server image built"
fi

if [ "$OPENMONO_ROLE" != "inference" ] && [ "$OPENMONO_ROLE" != "ollama" ]; then
    info "Building agent image..."
    if ! run docker compose build agent; then
        die "agent build failed"
    fi
    ok "Agent image built"
fi

if [ "$OPENMONO_ROLE" = "ollama" ]; then
    next_step "Configuring Ollama provider"

    mkdir -p "$HOME/.openmono"
    cat > "$HOME/.openmono/settings.json" << 'OLLAMAEOF'
{
  "providers": {
    "ollama": {
      "endpoint": "http://host.docker.internal:11434",
      "model": "qwen3.5:9b",
      "active": true
    }
  },
  "permissions": {
    "tools": {
      "Bash": {
        "allow": ["git *", "dotnet *", "npm *", "python *", "pip *"],
        "deny": ["rm -rf /", "sudo *"],
        "ask": ["sudo *"]
      }
    }
  },
  "auto_detect_code_graph": true,
  "verbose": false
}
OLLAMAEOF
    ok "Ollama provider configured in ~/.openmono/settings.json"

    if ! grep -q "host.docker.internal" /etc/hosts 2>/dev/null; then
        info "Adding host.docker.internal to /etc/hosts..."
        run printf "host.containers.internal\t host.docker.internal\n" | $SUDO tee -a /etc/hosts >/dev/null 2>&1 || true
    fi

    info "Starting Docker daemon..."
    run $SUDO systemctl enable --now docker 2>/dev/null || true
    ok "Ollama provider setup complete"
elif [ "$OPENMONO_ROLE" != "agent" ]; then
    MODEL_DIR="$INSTALL_DIR/models"
    next_step "Downloading $_MODEL_LABEL"

    if [ -n "${OPENMONO_MODEL_MIRROR:-}" ]; then
        MODEL_URL="${OPENMONO_MODEL_MIRROR%/}/models/${MODEL_NAME}"
    fi

    MODEL_FILE="$MODEL_DIR/$MODEL_NAME"
    MODEL_MIN_BYTES=$((1024 * 1024 * 1024))
    mkdir -p "$MODEL_DIR"

    model_size() { stat -c%s "$1" 2>/dev/null || echo 0; }

    if [ -f "$MODEL_FILE" ] && [ "$(model_size "$MODEL_FILE")" -gt "$MODEL_MIN_BYTES" ]; then
        ok "Model already present ($(du -h "$MODEL_FILE" | cut -f1))"
    else
        [ -f "$MODEL_FILE" ] && warn "Incomplete model — removing" && rm -f "$MODEL_FILE"
        info "Downloading from $MODEL_URL..."
        if ! run_live curl -L --fail --progress-bar -o "$MODEL_FILE" "$MODEL_URL"; then
            rm -f "$MODEL_FILE"
            die "Model download failed"
        fi
        SIZE_BYTES=$(model_size "$MODEL_FILE")
        [ "$SIZE_BYTES" -lt "$MODEL_MIN_BYTES" ] && rm -f "$MODEL_FILE" && die "Downloaded file too small."
        ok "Model downloaded ($(du -h "$MODEL_FILE" | cut -f1))"
    fi
fi

if [ "$OPENMONO_ROLE" = "ollama" ] || [ "$OPENMONO_ROLE" = "full" ] || [ "$OPENMONO_ROLE" = "inference" ]; then
    :
fi

DOCKER_ENV_FILE="$INSTALL_DIR/docker/.env"
if [ -f "$DOCKER_ENV_FILE" ]; then
    grep -v -E "^MODEL_NAME=|^MODEL_ALIAS=" "$DOCKER_ENV_FILE" > "${DOCKER_ENV_FILE}.tmp" || true
    mv "${DOCKER_ENV_FILE}.tmp" "$DOCKER_ENV_FILE"
fi
if [ "$OPENMONO_ROLE" != "ollama" ]; then
    printf "MODEL_NAME=%s\nMODEL_ALIAS=%s\n" "$MODEL_NAME" "$MODEL_ALIAS" >> "$DOCKER_ENV_FILE"
    detail "Persisted MODEL_NAME=$MODEL_NAME to $DOCKER_ENV_FILE"
fi

if [ -w /usr/local/bin ] || [ -n "${SUDO:-}" ]; then
    if [ -w /usr/local/bin ]; then
        ln -sf "$INSTALL_DIR/openmono" /usr/local/bin/openmono 2>/dev/null && \
            detail "Symlinked /usr/local/bin/openmono"
    else
        sudo ln -sf "$INSTALL_DIR/openmono" /usr/local/bin/openmono 2>/dev/null && \
            detail "Symlinked /usr/local/bin/openmono"
    fi
fi

clear_setup_prefs

if [[ -n "${OPENMONO_ENV_FILE:-}" ]]; then
    cat > "$OPENMONO_ENV_FILE" <<ENVEOF
export INSTALL_DIR="$INSTALL_DIR"
export LLAMA_PORT="${LLAMA_PORT:-7474}"
export GPU_MODE="${GPU_MODE:-0}"
export OPENMONO_ROLE="$OPENMONO_ROLE"
export MODEL_NAME="${MODEL_NAME:-}"
export MODEL_ACCURACY="${MODEL_ACCURACY:-standard}"
ENVEOF
    _log "Wrote install environment to: $OPENMONO_ENV_FILE"
else
    warn "OPENMONO_ENV_FILE not set"
fi
