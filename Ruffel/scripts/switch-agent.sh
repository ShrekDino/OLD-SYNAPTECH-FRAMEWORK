#!/usr/bin/env bash
set -euo pipefail

# ──────────────────────────────────────────────────────────────────────────────
# Agent Switcher — toggle between OpenCode and OpenMonoAgent
# Usage: agent [opencode|openmono|status]
#
# If no argument is given, infers from current shell state or opens a picker.
# ──────────────────────────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[38;2;163;255;102m'
BOLD='\033[1m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
err()   { echo -e "${RED}[ERROR]${NC} $*" >&2; }

OPENCODE_BIN="${OPENCODE_BIN:-$HOME/.opencode/bin/opencode}"
OPENMONO_DIR="${OPENMONO_DIR:-$HOME/openmono.ai}"
OPENMONO_CLI="${OPENMONO_CLI:-$OPENMONO_DIR/openmono}"
SWITCH_STATE_FILE="${SWITCH_STATE_FILE:-$HOME/.openmono/.active_agent}"

show_status() {
    local active=""
    if [[ -f "$SWITCH_STATE_FILE" ]]; then
        active=$(cat "$SWITCH_STATE_FILE")
    fi

    echo ""
    echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       Agent Status Overview          ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
    echo ""

    # OpenCode status
    if [[ -x "$OPENCODE_BIN" ]]; then
        OC_VER=$("$OPENCODE_BIN" --version 2>/dev/null || echo "?")
        echo -e "  ${GREEN}✓${NC} OpenCode v${OC_VER}"
        echo -e "     Path: ${OPENCODE_BIN}"
    else
        echo -e "  ${YELLOW}…${NC} OpenCode — not found at ${OPENCODE_BIN}"
    fi

    # OpenMono status
    if [[ -x "$OPENMONO_CLI" ]]; then
        echo -e "  ${GREEN}✓${NC} OpenMonoAgent"
        echo -e "     Path: ${OPENMONO_CLI}"

        if [[ -f "$HOME/.openmono/settings.json" ]] && command -v jq &>/dev/null; then
            local provider
            provider=$(jq -r '.providers.ollama.active' "$HOME/.openmono/settings.json" 2>/dev/null)
            if [[ "$provider" == "true" ]]; then
                local model
                model=$(jq -r '.providers.ollama.model // "unknown"' "$HOME/.openmono/settings.json" 2>/dev/null)
                echo -e "     Provider: Ollama (${model})"
            fi
        fi
    else
        echo -e "  ${YELLOW}…${NC} OpenMonoAgent — not found at ${OPENMONO_CLI}"
    fi

    # Ollama status
    if curl -sf http://localhost:11434/api/tags &>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Ollama — running on http://localhost:11434"
    else
        echo -e "  ${YELLOW}…${NC} Ollama — not detected"
    fi

    # Active agent
    echo ""
    if [[ -n "$active" ]]; then
        echo -e "  ${BOLD}Active agent:${NC} ${GREEN}${active}${NC}"
    else
        echo -e "  ${BOLD}Active agent:${NC} not set (run 'agent opencode' or 'agent openmono')"
    fi
    echo ""
}

switch_to_opencode() {
    if ! [[ -x "$OPENCODE_BIN" ]]; then
        err "OpenCode not found at $OPENCODE_BIN"
        err "Install: opencode install or check OPENCODE_BIN"
        return 1
    fi

    echo "ollama" > "$SWITCH_STATE_FILE"
    ok "Switched to OpenCode"

    # Create convenience alias if not present
    if ! grep -q "alias ai=" "$HOME/.bashrc" 2>/dev/null; then
        echo "" >> "$HOME/.bashrc"
        echo "# AI Coding Agent (switched by agent-switcher)" >> "$HOME/.bashrc"
        echo "alias ai='$OPENCODE_BIN -m ollama/qwen3.5:9b'" >> "$HOME/.bashrc"
        echo "alias ai-mono='$OPENMONO_CLI agent'" >> "$HOME/.bashrc"
        echo "" >> "$HOME/.bashrc"
        ok "Added aliases to ~/.bashrc (ai, ai-mono)"
    fi

    echo ""
    echo "  Run:  ai           # Start OpenCode"
    echo "  Run:  ai-mono      # Start OpenMonoAgent"
    echo "  Run:  agent status # Show status"
    echo ""

    # Execute OpenCode immediately if in a terminal
    if [[ -t 1 ]]; then
        info "Starting OpenCode..."
        exec "$OPENCODE_BIN" -m ollama/qwen3.5:9b
    fi
}

switch_to_openmono() {
    if ! [[ -x "$OPENMONO_CLI" ]]; then
        err "OpenMonoAgent not found at $OPENMONO_CLI"
        err "Setup: $OPENMONO_DIR/get-openmono.sh"
        return 1
    fi

    echo "openmono" > "$SWITCH_STATE_FILE"
    ok "Switched to OpenMonoAgent"

    # Ensure Docker is running
    if ! docker info &>/dev/null 2>&1; then
        warn "Docker daemon not accessible."
        warn "Start it: sudo systemctl start docker"
        warn "Or: newgrp docker"
    fi

    echo ""
    echo "  Run:  cd your-project/ && openmono agent"
    echo "  Run:  ai-mono       # Alias (if configured)"
    echo "  Run:  agent status  # Show status"
    echo ""

    if [[ -t 1 ]]; then
        info "Starting OpenMonoAgent..."
        cd "$(pwd)" && exec "$OPENMONO_CLI" agent
    fi
}

configure_shell() {
    local rcfile="$HOME/.bashrc"
    local added=false

    # Add agent function
    if ! grep -q "agent()" "$rcfile" 2>/dev/null; then
        cat >> "$rcfile" << 'FUNCEOF'

# AI Agent Switcher — unified launcher for OpenCode and OpenMonoAgent
agent() {
    local script="$HOME/openmono.ai/scripts/switch-agent.sh"
    if [[ -x "$script" ]]; then
        bash "$script" "$@"
    else
        echo "Agent switcher not found at $script" >&2
        return 1
    fi
}

# Quick aliases
alias ai='agent opencode'
alias ai-mono='agent openmono'
alias ai-status='agent status'
FUNCEOF
        added=true
    fi

    # Add to PATH
    if ! grep -q "openmono.ai" "$rcfile" 2>/dev/null; then
        echo "" >> "$rcfile"
        echo "# OpenMono.ai" >> "$rcfile"
        echo 'export PATH="$HOME/openmono.ai:$PATH"' >> "$rcfile"
        added=true
    fi

    # Add .NET to PATH if not there
    if ! grep -q "DOTNET_ROOT" "$rcfile" 2>/dev/null; then
        echo "" >> "$rcfile"
        echo "# .NET SDK" >> "$rcfile"
        echo 'export DOTNET_ROOT="$HOME/.dotnet"' >> "$rcfile"
        echo 'export PATH="$DOTNET_ROOT:$PATH"' >> "$rcfile"
        added=true
    fi

    if $added; then
        ok "Shell configuration updated in ~/.bashrc"
        info "Run: source ~/.bashrc  (or open a new terminal)"
    else
        ok "Shell already configured"
    fi
}

case "${1:-}" in
    opencode|oc|opencode)
        shift
        switch_to_opencode "$@"
        ;;
    openmono|om|mono)
        shift
        switch_to_openmono "$@"
        ;;
    status|st)
        show_status
        ;;
    configure|config|setup)
        configure_shell
        ;;
    help|--help|-h|"")
        echo "Usage: agent <command>"
        echo ""
        echo "Commands:"
        echo "  opencode       Switch to OpenCode and launch it"
        echo "  openmono       Switch to OpenMonoAgent and launch it"
        echo "  status         Show agent status overview"
        echo "  configure      Add shell aliases to ~/.bashrc"
        echo "  help           Show this help"
        echo ""
        echo "Aliases (after configure):"
        echo "  ai             Start OpenCode"
        echo "  ai-mono        Start OpenMonoAgent"
        echo "  ai-status      Show agent status"
        echo ""
        show_status
        ;;
    *)
        err "Unknown command: $1"
        echo "Usage: agent [opencode|openmono|status|configure]"
        exit 1
        ;;
esac
