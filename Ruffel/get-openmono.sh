#!/usr/bin/env bash
set -euo pipefail

# ────────────────────────────────────────────────────────────────────────────────
# OpenMono.ai – bootstrap installer
# ────────────────────────────────────────────────────────────────────────────────

REPO_URL="https://github.com/StartupHakk/OpenMonoAgent.ai.git"
INSTALL_DIR="${OPENMONO_HOME:-$HOME/openmono.ai}"
BRANCH=""

BLUE='\033[38;2;163;255;102m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }
die()  { err "$*"; exit 1; }

# ── OS detection ──────────────────────────────────────────────────────────────
detect_os() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        echo "$ID"
    elif [ "$(uname -s)" = "Darwin" ]; then
        echo "macos"
    else
        echo "linux"
    fi
}

# ── Argument parsing ──────────────────────────────────────────────────────────

PASSTHROUGH_ARGS=()
while [[ $# -gt 0 ]]; do
    case "$1" in
        -b|--branch)
            [[ -n "${2:-}" ]] || die "--branch requires a value"
            BRANCH="$2"; shift 2 ;;
        -*)
            PASSTHROUGH_ARGS+=("$1"); shift ;;
        *)
            # First bare positional arg is treated as an optional branch name
            [[ -z "$BRANCH" ]] && BRANCH="$1" || PASSTHROUGH_ARGS+=("$1")
            shift ;;
    esac
done

# ── Preflight checks ──────────────────────────────────────────────────────────

command -v git  &>/dev/null || die "git is required – install it first: sudo apt install git"
command -v curl &>/dev/null || die "curl is required – install it first: sudo apt install curl"

# ── Clone or update ───────────────────────────────────────────────────────────

BRANCH_LABEL="${BRANCH:-default}"

if [ -d "$INSTALL_DIR/.git" ]; then
    info "Repository already exists at $INSTALL_DIR – fetching latest..."
    git -C "$INSTALL_DIR" fetch --quiet 2>/dev/null || info "Fetch failed; continuing with existing checkout"
    if [[ -n "$BRANCH" ]]; then
        info "Switching to branch '$BRANCH'..."
        git -C "$INSTALL_DIR" checkout "$BRANCH" 2>/dev/null || die "Branch '$BRANCH' not found"
    fi
    git -C "$INSTALL_DIR" pull --ff-only 2>/dev/null \
        || info "Could not fast-forward; continuing with existing checkout"
else
    info "Cloning OpenMono.ai ($BRANCH_LABEL branch) to $INSTALL_DIR..."
    CLONE_ARGS=("$REPO_URL" "$INSTALL_DIR")
    [[ -n "$BRANCH" ]] && CLONE_ARGS=(--branch "$BRANCH" "${CLONE_ARGS[@]}")
    git clone "${CLONE_ARGS[@]}" || die "git clone failed"
fi

ok "Repository ready at $INSTALL_DIR"

# ── Make CLI executable ───────────────────────────────────────────────────────

chmod +x "$INSTALL_DIR/openmono" "$INSTALL_DIR/scripts/"*.sh

# ── OS-specific setup ────────────────────────────────────────────────────────

OS="$(detect_os)"
info "Detected OS: ${OS}"

if [ "$OS" = "arch" ]; then
    info "Arch Linux detected — using Arch-optimized installer"

    # For Ollama provider mode (lightweight fallback), set defaults.
    # User can override with PASSTHROUGH_ARGS if desired.
    if [[ " ${PASSTHROUGH_ARGS[*]} " != *"--full"* ]] && \
       [[ " ${PASSTHROUGH_ARGS[*]} " != *"--inference"* ]] && \
       [[ " ${PASSTHROUGH_ARGS[*]} " != *"--agent"* ]] && \
       [[ " ${PASSTHROUGH_ARGS[*]} " != *"--ollama"* ]]; then
        info "Defaulting to Ollama provider mode (--ollama) on Arch Linux"
        info "  Pass --full to install full llama.cpp inference instead"
        PASSTHROUGH_ARGS+=("--ollama")
    fi

    # Source shared logging and run Arch scripts
    source "$INSTALL_DIR/scripts/lib/log.sh"

    export OPENMONO_LOG_DIR="${OPENMONO_LOG_DIR:-$HOME/.openmono/logs}"
    mkdir -p "$OPENMONO_LOG_DIR"
    export OPENMONO_LOG_FILE="$OPENMONO_LOG_DIR/setup-$(date +%Y%m%d-%H%M%S).log"
    : > "$OPENMONO_LOG_FILE"

    export OPENMONO_ENV_FILE="$HOME/.openmono/.tmp_install_env"
    mkdir -p "$(dirname "$OPENMONO_ENV_FILE")"
    : > "$OPENMONO_ENV_FILE"

    bash "$INSTALL_DIR/scripts/install_prereqs_arch.sh" 2>> "$OPENMONO_LOG_FILE" || {
        show_log_tail 30
        die "Prerequisite install failed. Full log: $OPENMONO_LOG_FILE"
    }

    if [[ -z "${OPENMONO_GPU:-}" && -f "$HOME/.openmono/.tmp_gpu_mode" ]]; then
        _gpu_val=$(grep '^GPU_MODE=' "$HOME/.openmono/.tmp_gpu_mode" | cut -d= -f2 | tr -d '[:space:]')
        [[ "$_gpu_val" == "1" ]] && export OPENMONO_GPU=1 || export OPENMONO_GPU=0
        rm -f "$HOME/.openmono/.tmp_gpu_mode"
    fi

    if command -v docker &>/dev/null && ! docker info &>/dev/null 2>&1; then
        if getent group docker 2>/dev/null | grep -qw "$USER"; then
            if command -v sg &>/dev/null && sg docker -c "docker info" &>/dev/null 2>&1; then
                info "Re-launching with docker group active..."
                exec sg docker -c "$0 setup ${PASSTHROUGH_ARGS[*]}"
            else
                err "User added to docker group but activation failed."
                err "Run: newgrp docker && openmono setup"
                exit 1
            fi
        fi
    fi

    bash "$INSTALL_DIR/scripts/install_arch.sh" 2>> "$OPENMONO_LOG_FILE" || {
        show_log_tail 30
        die "Installation failed. Full log: $OPENMONO_LOG_FILE"
    }

    if [[ -n "${OPENMONO_ENV_FILE:-}" ]] && [[ -f "$OPENMONO_ENV_FILE" ]]; then
        source "$OPENMONO_ENV_FILE"
    fi

    echo ""
    printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
    printf "${BLUE}${BOLD}  Setup Complete (Arch Linux)${NC}\n"
    printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
    echo ""
    echo -e "  ${GREEN}✓${NC} OpenMono.ai is ready!"
    echo ""

    if [[ "${PASSTHROUGH_ARGS[*]}" == *"--ollama"* ]] || [[ "${PASSTHROUGH_ARGS[*]}" != *"--full"* ]]; then
        echo "  Mode: Ollama provider (lightweight fallback)"
        echo "  Ollama endpoint: http://localhost:11434"
        echo "  Model: qwen3.5:9b (configurable via ~/.openmono/settings.json)"
        echo ""
        echo "  Next steps:"
        echo -e "    1. ${BOLD}cd your-project/${NC}"
        echo -e "    2. ${BOLD}openmono agent${NC}"
        echo ""
        echo "  Config: openmono config set llm.endpoint http://localhost:11434"
        echo "  Config: openmono config set llm.model qwen3.5:9b"
    else
        echo "  Mode: full (llama.cpp inference)"
        echo ""
        echo "  Next steps:"
        echo -e "    1. ${BOLD}cd your-project/${NC}"
        echo -e "    2. ${BOLD}openmono agent${NC}"
    fi
    echo ""
    echo "  openmono CLI: $(which openmono 2>/dev/null || echo 'reload shell')"
    echo "  Docker: $(docker info >/dev/null 2>&1 && echo 'OK' || echo 'start daemon')"
    echo ""
    printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
    echo ""

    for rc_file in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.bash_profile"; do
        if [[ -f "$rc_file" ]]; then
            if ! grep -q "# OpenMono.ai" "$rc_file" 2>/dev/null; then
                {
                    echo ""
                    echo "# OpenMono.ai"
                    echo "export PATH=\"$INSTALL_DIR:\$PATH\""
                } >> "$rc_file"
                detail "Updated $(basename "$rc_file")"
            fi
        fi
    done

    export PATH="$INSTALL_DIR:$PATH"
    exec -l "$SHELL"
fi

# ── Hand off to openmono setup (passes all flags through) ────────────────────

# When piped through curl, stdin is the pipe not the terminal — restore it so
# interactive prompts in `openmono setup` can read user input.
if [[ ! -t 0 ]]; then
    exec "$INSTALL_DIR/openmono" setup "${PASSTHROUGH_ARGS[@]+"${PASSTHROUGH_ARGS[@]}"}" </dev/tty
else
    exec "$INSTALL_DIR/openmono" setup "${PASSTHROUGH_ARGS[@]+"${PASSTHROUGH_ARGS[@]}"}"
fi
