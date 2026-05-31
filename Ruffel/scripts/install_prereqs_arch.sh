#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/log.sh"

if [[ -z "${REPO_DIR:-}" ]]; then
    REPO_DIR="$(dirname "$SCRIPT_DIR")"
fi

export PATH="$REPO_DIR:$PATH"

GPU_MODE="${OPENMONO_GPU:-}"
if [[ -n "${OPENMONO_CPU:-}" ]]; then
    GPU_MODE=0
fi
if [[ -z "$GPU_MODE" && -f "$HOME/.openmono/.setup_prefs" ]]; then
    _saved_gpu=$(grep '^GPU_MODE=' "$HOME/.openmono/.setup_prefs" 2>/dev/null | cut -d= -f2 | tr -d '[:space:]' || true)
    [[ -n "$_saved_gpu" ]] && GPU_MODE="$_saved_gpu"
fi
export GPU_MODE

TOTAL_STEPS=8
banner "OpenMono.ai Prerequisites — Arch Linux"

step 1 $TOTAL_STEPS "Detecting operating system"

if [ ! -f /etc/os-release ]; then
    die "Cannot detect OS."
fi

. /etc/os-release

if [ "$ID" != "arch" ]; then
    warn "Detected $PRETTY_NAME — this script targets Arch Linux."
    warn "Continuing, but some steps may need manual adjustment."
else
    ok "$PRETTY_NAME"
fi

step 2 $TOTAL_STEPS "Checking privileges"

if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
    ok "Running as root"
else
    if ! command -v sudo &>/dev/null; then
        die "sudo is required. Run as root or install sudo first."
    fi
    SUDO="sudo"
    ok "sudo available"
fi

step 3 $TOTAL_STEPS "Updating package database"

if ! run $SUDO pacman -Sy --noconfirm; then
    die "Failed to update package database"
fi
ok "Package database updated"

step 4 $TOTAL_STEPS "Installing core tools"

install_pkg() {
    local pkg="$1"
    local check_cmd="${2:-$pkg}"
    if command -v "$check_cmd" &>/dev/null; then
        ok "$pkg already installed"
        detail "$(command -v "$check_cmd")"
    else
        info "Installing $pkg..."
        if ! run $SUDO pacman -S --noconfirm "$pkg"; then
            die "Failed to install $pkg"
        fi
        ok "$pkg installed"
    fi
}

install_pkg git git
install_pkg curl curl
install_pkg jq jq
install_pkg cmake cmake
install_pkg pciutils lspci
install_pkg ripgrep rg
install_pkg base-devel make

if command -v python &>/dev/null; then
    ok "python already installed"
else
    install_pkg python python
fi

if command -v pip &>/dev/null; then
    ok "pip already installed"
else
    install_pkg python-pip pip
fi

step 5 $TOTAL_STEPS "Checking for NVIDIA GPU"

if [[ "${OPENMONO_ROLE:-}" == "agent" ]]; then
    info "Agent-only role — skipping GPU detection"
    GPU_MODE=0
    HAS_NVIDIA_HW=false
else
    HAS_NVIDIA_HW=false
    if command -v lspci &>/dev/null && lspci 2>/dev/null | grep -qi 'nvidia'; then
        HAS_NVIDIA_HW=true
        detail "$(lspci | grep -i nvidia | head -3)"
    elif grep -qi "0x10de" /sys/bus/pci/devices/*/vendor 2>/dev/null; then
        HAS_NVIDIA_HW=true
        detail "NVIDIA GPU detected via PCI vendor ID (0x10de)"
    fi

    if [[ -n "$GPU_MODE" ]]; then
        :
    elif [ "$HAS_NVIDIA_HW" = true ] || command -v nvidia-smi &>/dev/null; then
        if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null 2>&1; then
            GPU_MODE=1
            ok "NVIDIA GPU detected and driver active — GPU mode enabled"
        else
            echo ""
            printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
            printf "${BLUE}${BOLD}  NVIDIA GPU Detected${NC}\n"
            printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
            echo ""
            _gpu_invalid=0
            while true; do
                [ "$_gpu_invalid" -eq 1 ] && printf "  ${RED}Please press Y or N.${NC}\n\n"
                printf "  Would you like to install on GPU? ${BOLD}(Y/n)${NC}: "
                read -r -n 1 _gpu_choice
                echo ""
                case "${_gpu_choice:-Y}" in
                    [Yy]) GPU_MODE=1; break ;;
                    [Nn]) GPU_MODE=0; break ;;
                    *)    _gpu_invalid=1 ;;
                esac
            done
            _save_setup_pref "GPU_MODE" "$GPU_MODE"
            if [ "$GPU_MODE" = "1" ]; then
                echo ""
                info "NVIDIA drivers will be installed."
            fi
            echo ""
        fi
    else
        GPU_MODE=0
    fi

    if [ "$GPU_MODE" = 0 ]; then
        info "GPU mode disabled — skipping NVIDIA stack"
    else
        ok "GPU mode enabled — installing NVIDIA stack"

        if command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null; then
            ok "NVIDIA drivers already installed"
            detail "$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -1)"
        else
            info "Installing NVIDIA drivers..."
            if pacman -Qi nvidia-open &>/dev/null 2>&1; then
                ok "nvidia-open already installed"
            else
                run $SUDO pacman -S --noconfirm nvidia-open nvidia-utils || warn "NVIDIA driver install had warnings"
                NVIDIA_REBOOT_PENDING=true
            fi
        fi

        if pacman -Qi nvidia-container-toolkit &>/dev/null 2>&1; then
            ok "nvidia-container-toolkit already installed"
        else
            info "Installing nvidia-container-toolkit..."
            run $SUDO pacman -S --noconfirm nvidia-container-toolkit || warn "nvidia-container-toolkit install had warnings"
        fi
    fi
fi

mkdir -p "$HOME/.openmono"
echo "GPU_MODE=$GPU_MODE" > "$HOME/.openmono/.tmp_gpu_mode"

step 6 $TOTAL_STEPS "Installing Docker"

if command -v docker &>/dev/null; then
    ok "Docker already installed"
    detail "$(docker --version)"
else
    info "Installing Docker from official repository..."
    run $SUDO pacman -S --noconfirm docker docker-compose containerd
    run $SUDO systemctl enable docker
    run $SUDO groupadd docker 2>/dev/null || true
    run $SUDO usermod -aG docker "$USER" || true
    ok "Docker installed"
fi

if ! id -nG 2>/dev/null | grep -qw docker; then
    run $SUDO groupadd docker 2>/dev/null || true
    run $SUDO usermod -aG docker "$USER" || true
    ok "Added '$USER' to the docker group"
fi

if docker compose version &>/dev/null 2>&1; then
    ok "Docker Compose available"
    detail "$(docker compose version --short 2>/dev/null || echo 'plugin')"
fi

if [ "$HAS_NVIDIA_HW" = true ] && command -v nvidia-ctk &>/dev/null; then
    if docker info 2>/dev/null | grep -q nvidia; then
        ok "Docker already configured with nvidia runtime"
    else
        info "Configuring Docker with nvidia runtime..."
        run $SUDO nvidia-ctk runtime configure --runtime=docker
        ok "Docker nvidia runtime configured"
    fi
fi

step 7 $TOTAL_STEPS "Installing .NET 10 SDK"

if command -v dotnet &>/dev/null && dotnet --list-sdks 2>/dev/null | grep -q "^10\."; then
    ok ".NET 10 SDK already installed"
    detail "$(dotnet --version)"
else
    info "Downloading Microsoft dotnet-install script..."
    run curl -fsSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh
    chmod +x /tmp/dotnet-install.sh
    info "Installing .NET 10 to \$HOME/.dotnet ..."
    run /tmp/dotnet-install.sh --channel 10.0 --install-dir "$HOME/.dotnet" || die ".NET install failed"
    rm -f /tmp/dotnet-install.sh

    export DOTNET_ROOT="$HOME/.dotnet"
    export PATH="$DOTNET_ROOT:$PATH"

    for rc in "$HOME/.bashrc" "$HOME/.zshrc" "$HOME/.profile"; do
        if [ -f "$rc" ] && ! grep -q "DOTNET_ROOT" "$rc" 2>/dev/null; then
            {
                echo ""
                echo "# .NET SDK"
                echo 'export DOTNET_ROOT="$HOME/.dotnet"'
                echo 'export PATH="$DOTNET_ROOT:$PATH"'
            } >> "$rc"
            detail "Added .NET to PATH in $(basename "$rc")"
        fi
    done
    ok ".NET 10 SDK installed ($(dotnet --version 2>/dev/null || echo 'reload shell'))"
fi

step 8 $TOTAL_STEPS "Verifying install"

check_installed() {
    local cmd="$1"
    if command -v "$cmd" &>/dev/null; then
        printf "  ${GREEN}✓${NC} %s\n" "$cmd"
    else
        printf "  ${YELLOW}…${NC} %s (may need shell reload)\n" "$cmd"
    fi
}

check_installed docker
check_installed git
check_installed jq
check_installed cmake
check_installed curl
check_installed rg
check_installed dotnet
if [ "$HAS_NVIDIA_HW" = true ]; then
    check_installed nvidia-ctk
    check_installed nvidia-smi
fi

echo ""
ok "Prerequisites ready"
echo ""
show_log_location

if [ "${NVIDIA_REBOOT_PENDING:-false}" = "true" ]; then
    _reboot_done_file="$HOME/.openmono/.nvidia_reboot_done"
    if [ -f "$_reboot_done_file" ] || (command -v nvidia-smi &>/dev/null && nvidia-smi &>/dev/null 2>&1); then
        ok "NVIDIA drivers are active — no reboot needed"
    else
        echo ""
        printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
        printf "${BLUE}${BOLD}  Reboot Required${NC}\n"
        printf "${BLUE}%s${NC}\n" "$(printf '─%.0s' $(seq 1 60))"
        echo ""
        info "NVIDIA drivers installed. Reboot to activate."
        echo ""
        _reboot_invalid=0
        while true; do
            [ "$_reboot_invalid" -eq 1 ] && printf "  ${RED}Please press Y or N.${NC}\n\n"
            printf "  Would you like to reboot now? ${BOLD}(Y/n)${NC}: "
            read -r -n 1 _reboot_choice
            echo ""
            case "${_reboot_choice:-Y}" in
                [Yy]) _reboot_choice=Y; break ;;
                [Nn]) _reboot_choice=N; break ;;
                *)    _reboot_invalid=1 ;;
            esac
        done

        if [[ "$_reboot_choice" == "Y" ]]; then
            touch "$_reboot_done_file"
            echo ""
            info "After reboot, run: ${BOLD}$REPO_DIR/openmono setup${NC}"
            echo ""
            info "Rebooting in 10 seconds (press Ctrl+C to cancel)..."
            sleep 10
            $SUDO reboot
        else
            warn "Reboot skipped. NVIDIA drivers will not be active until you reboot."
            warn "Run: sudo reboot"
        fi
    fi
fi

if [[ -n "${OPENMONO_ENV_FILE:-}" ]]; then
    echo "export GPU_MODE=\"${GPU_MODE:-0}\"" >> "$OPENMONO_ENV_FILE"
    _log "GPU_MODE=${GPU_MODE:-0} written to env file"
fi
