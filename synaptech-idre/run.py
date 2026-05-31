#!/usr/bin/env python3
"""SynapTech IDRE — root entry point for local demo.

Usage:
    python run.py              # Start backend server
    python run.py --gen-data   # Generate test data only
    python run.py --help       # Show options
"""

import sys
import os
import subprocess
import argparse

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def gen_data():
    print("Generating synthetic connectome data...")
    from scripts.generate_test_data import main as gen
    gen()
    print("Data generation complete.")


def run_backend():
    os.chdir(PROJECT_ROOT)
    os.environ["PYTHONPATH"] = PROJECT_ROOT

    import uvicorn
    print("Starting SynapTech IDRE backend on http://localhost:8000")
    uvicorn.run(
        "src.backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )


def run_frontend():
    frontend_dir = os.path.join(PROJECT_ROOT, "src", "frontend")
    os.chdir(frontend_dir)

    print("Installing frontend dependencies...")
    subprocess.run(["npm", "install"], check=True, cwd=frontend_dir)

    print("Starting frontend dev server on http://localhost:3000")
    subprocess.run(["npm", "run", "dev"], check=True, cwd=frontend_dir)


def main():
    parser = argparse.ArgumentParser(description="SynapTech IDRE Launcher")
    parser.add_argument("command", nargs="?", default="backend",
                        choices=["backend", "frontend", "gen-data", "all"],
                        help="What to run (default: backend)")
    args = parser.parse_args()

    if args.command == "gen-data":
        gen_data()
    elif args.command == "backend":
        if not os.path.exists(os.path.join(PROJECT_ROOT, "data", "layout.json")):
            print("No data found. Generating test data first...")
            gen_data()
        run_backend()
    elif args.command == "frontend":
        run_frontend()
    elif args.command == "all":
        if not os.path.exists(os.path.join(PROJECT_ROOT, "data", "layout.json")):
            gen_data()
        import threading
        t = threading.Thread(target=run_backend, daemon=True)
        t.start()
        run_frontend()


if __name__ == "__main__":
    main()
