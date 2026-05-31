#!/usr/bin/env python3
"""
Launch every SynapTechBio service with one command.

Usage:
    python tools/run_all.py              # Run all available services
    python tools/run_all.py --idre        # Run only IDRE
    python tools/run_all.py --lsm         # Run only FlyWire LSM
    python tools/run_all.py --realtime    # Run only Realtime Engine
    python tools/run_all.py --csdf        # Run only CSDF
    python tools/run_all.py --cosmos      # Run only Cosmos demo
    python tools/run_all.py --eve         # Run only EVE
"""

import argparse
import logging
import os
import subprocess
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("run_all")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def run_service(name: str, cwd: str, cmd: list, check: bool = False):
    logger.info(f"Starting {name}...")
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        logger.info(f"{name} started (PID {proc.pid})")
        return proc
    except FileNotFoundError as e:
        logger.error(f"Failed to start {name}: {e}")
        if check:
            sys.exit(1)
        return None


def main():
    parser = argparse.ArgumentParser(description="Launch all SynapTechBio services")
    parser.add_argument("--idre", action="store_true", help="Run only IDRE")
    parser.add_argument("--lsm", action="store_true", help="Run only FlyWire LSM")
    parser.add_argument("--realtime", action="store_true", help="Run only Realtime Engine")
    parser.add_argument("--csdf", action="store_true", help="Run only CSDF")
    parser.add_argument("--cosmos", action="store_true", help="Run only Cosmos demo")
    parser.add_argument("--eve", action="store_true", help="Run only EVE")
    parser.add_argument("--identity", action="store_true", help="Run only identity-core (check)")
    parser.add_argument("--sar", action="store_true", help="Run only Substrate-Adaptive Runtime")
    parser.add_argument("--all", action="store_true", help="Run all services (default)")
    args = parser.parse_args()

    run_all = args.all or not any([args.idre, args.lsm, args.realtime, args.csdf, args.cosmos, args.eve, args.identity, args.sar])
    services = []

    if run_all or args.idre:
        idre_dir = os.path.join(ROOT, "packages", "idre")
        if os.path.exists(idre_dir):
            services.append(("IDRE", idre_dir, [sys.executable, "run.py", "all"]))

    if run_all or args.lsm:
        lsm_dir = os.path.join(ROOT, "packages", "flywire-lsm")
        if os.path.exists(lsm_dir):
            services.append(
                ("FlyWire LSM", lsm_dir, [sys.executable, "-m", "flywire_lsm.server"])
            )

    if run_all or args.realtime:
        rt_dir = os.path.join(ROOT, "packages", "flywire-realtime")
        if os.path.exists(rt_dir):
            services.append(
                (
                    "FlyWire Realtime",
                    rt_dir,
                    [
                        sys.executable,
                        "flybrain_activity.py",
                        "--closed-loop",
                        "--realtime",
                    ],
                )
            )

    if run_all or args.csdf:
        csdf_dir = os.path.join(ROOT, "packages", "csdf")
        if os.path.exists(csdf_dir):
            services.append(
                ("CSDF", csdf_dir, [sys.executable, "scripts/run.py", "--single"])
            )

    if run_all or args.cosmos:
        cosmos_dir = os.path.join(ROOT, "packages", "cosmos")
        if os.path.exists(cosmos_dir):
            services.append(
                (
                    "Cosmos Integration",
                    cosmos_dir,
                    [sys.executable, "-m", "src.demo.basic_loop"],
                )
            )

    if run_all or args.eve:
        eve_dir = os.path.join(ROOT, "packages", "eve")
        if os.path.exists(eve_dir):
            services.append(
                ("EVE", eve_dir, [sys.executable, "eve_suite_pyside6.py"])
            )

    if run_all or args.identity:
        id_dir = os.path.join(ROOT, "packages", "identity-core")
        if os.path.exists(id_dir):
            services.append(
                ("Identity-Core", id_dir, [sys.executable, "-c",
                 "from identity_core import IdentityCheckpoint; print('OK')"])
            )

    if run_all or args.sar:
        sar_dir = os.path.join(ROOT, "packages", "substrate-adaptive-runtime")
        if os.path.exists(sar_dir):
            services.append(
                ("SAR", sar_dir, [sys.executable, "-c",
                 "from substrate_adaptive_runtime import SubstrateAdaptiveRuntime; "
                 "r = SubstrateAdaptiveRuntime(); r.initialize(); print('SAR initialized')"])
            )

    if not services:
        logger.warning("No services to run. Check that packages exist.")
        return

    logger.info(f"Starting {len(services)} service(s)...")
    processes = []
    for name, cwd, cmd in services:
        proc = run_service(name, cwd, cmd)
        if proc:
            processes.append((name, proc))

    try:
        while True:
            time.sleep(1)
            for name, proc in processes:
                if proc.poll() is not None:
                    logger.warning(f"{name} exited with code {proc.returncode}")
    except KeyboardInterrupt:
        logger.info("\nShutting down services...")
        for name, proc in processes:
            proc.terminate()
        for name, proc in processes:
            proc.wait(timeout=5)
        logger.info("All services stopped.")


if __name__ == "__main__":
    main()
