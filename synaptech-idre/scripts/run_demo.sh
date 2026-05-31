#!/usr/bin/env bash
# =============================================================================
# SynapTech IDRE — Local Demo Launcher
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}→${NC} $1"; }
log_ok()    { echo -e "${GREEN}✓${NC} $1"; }
log_warn()  { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

cleanup() {
    log_info "Shutting down..."
    if [ -n "${BACKEND_PID:-}" ]; then kill "$BACKEND_PID" 2>/dev/null || true; fi
    if [ -n "${FRONTEND_PID:-}" ]; then kill "$FRONTEND_PID" 2>/dev/null || true; fi
    exit 0
}
trap cleanup SIGINT SIGTERM

cd "$PROJECT_DIR"

# ── Python setup ──────────────────────────────────────────────────────
log_info "Setting up Python environment..."

if [ ! -d "$VENV_DIR" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi
source "${VENV_DIR}/bin/activate"

log_info "Installing Python dependencies..."
pip install --quiet --upgrade pip
pip install --quiet fastapi uvicorn[standard] pydantic pydantic-settings \
    numpy pandas scipy httpx cryptography

# Try installing CuPy (may fail — that's OK, we fall back to CPU)
if python3 -c "import cupy" 2>/dev/null; then
    log_ok "CuPy already installed (GPU mode)"
else
    log_info "CuPy not found — trying cupy-cuda12x..."
    pip install --quiet cupy-cuda12x 2>/dev/null && log_ok "CuPy installed (GPU mode)" \
        || log_warn "CuPy not available — will use CPU (SciPy) fallback"
fi

# ── Generate test data ────────────────────────────────────────────────
if [ ! -f "data/flywire/connectome.csv" ] || [ ! -f "data/layout.json" ]; then
    log_info "Generating synthetic connectome data..."
    python3 -c "
import sys; sys.path.insert(0, '.')
from scripts.generate_test_data import main as gen
gen()
"
    log_ok "Test data generated"
else
    log_ok "Existing data found, skipping generation"
fi

# ── Start backend ─────────────────────────────────────────────────────
log_info "Starting backend on http://localhost:8000..."
PYTHONPATH="$PROJECT_DIR" python3 -m uvicorn src.backend.main:app \
    --host 0.0.0.0 --port 8000 --log-level info &
BACKEND_PID=$!
sleep 3

# Health check
if curl -sf http://localhost:8000/health >/dev/null 2>&1; then
    log_ok "Backend is healthy"
else
    log_error "Backend failed to start"
    cleanup
fi

# ── Frontend setup ────────────────────────────────────────────────────
log_info "Setting up frontend..."
cd src/frontend

if [ ! -d "node_modules" ]; then
    log_info "Installing npm packages..."
    npm install --silent 2>&1 | tail -1
fi

log_info "Starting frontend on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

cd "$PROJECT_DIR"

sleep 2

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║       SynapTech IDRE — Demo Running                     ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Frontend:   http://localhost:3000                     ║"
echo "║  Backend:    http://localhost:8000                     ║"
echo "║  API docs:   http://localhost:8000/docs                ║"
echo "║                                                         ║"
echo "║  Click neurons in the 3D view to select them            ║"
echo "║  Press 'Activate Selected' to run the connectome        ║"
echo "║  Press 'Random Stimulus' to see global activation       ║"
echo "║                                                         ║"
echo "║  Press Ctrl+C to stop                                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

wait
