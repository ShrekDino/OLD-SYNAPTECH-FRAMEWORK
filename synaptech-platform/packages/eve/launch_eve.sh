#!/bin/bash
# EVE Developer Suite Launcher
# Usage: ./launch_eve.sh

cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || echo "No venv found, using system Python"

echo "🚀 Launching E.V.E. Developer Suite..."
python3 eve_suite_pyside6.py
