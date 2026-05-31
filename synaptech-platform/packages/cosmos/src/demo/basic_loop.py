"""
MVP integration demo — runs one full SynapTechBio+Cosmos cycle.

Demonstrates:
1. Cosmos-Tokenizer encode/decode (local on 6GB)
2. CosmosEnvironment (replaces CSDF synthetic embeddings)
3. CosmosFlyWorld (generates world context from motor commands)
4. SpatialReasoner (physical reasoning about agent state)

Usage:
    python -m src.demo.basic_loop
    python -m src.demo.basic_loop --use-reasoner  # try loading Reason2 if available
"""

import argparse
import logging
import sys
import time

import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("cosmos.demo")


def simulate_motor_commands() -> np.ndarray:
    return np.random.randn(12).astype(np.float32) * 0.1


def simulate_neuropil_state() -> np.ndarray:
    return np.random.randn(78).astype(np.float32) * 0.05


def main():
    parser = argparse.ArgumentParser(description="Cosmos integration MVP demo")
    parser.add_argument(
        "--use-reasoner", action="store_true", help="Attempt to load Cosmos-Reason2"
    )
    parser.add_argument(
        "--steps", type=int, default=10, help="Number of integration cycles to run"
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("SynapTechBio + Cosmos Integration MVP")
    logger.info("=" * 60)

    from ..tokens.encoder import CosmosEncoder
    from ..tokens.decoder import CosmosDecoder
    from ..reason.csdf_adapter import CosmosEnvironment
    from ..reason.spatial_reasoner import SpatialReasoner

    model_name = "Cosmos-Tokenize1-CV8x8x8-720p"
    device = "cuda" if __import__("torch").cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    encoder = CosmosEncoder(model_name=model_name, device=device)
    decoder = CosmosDecoder(model_name=model_name, device=device)
    reasoner = SpatialReasoner()

    if args.use_reasoner:
        logger.info("Attempting to load Cosmos-Reason2...")
        reasoner.load(device=device, quantize=(device == "cuda"))
    else:
        logger.info("Cosmos-Reason2 disabled (use --use-reasoner to enable)")

    env = CosmosEnvironment(reasoner=reasoner, encoder=encoder if encoder.is_loaded else None)

    logger.info("\nStarting integration loop...\n")
    for step in range(args.steps):
        logger.info(f"--- Step {step + 1}/{args.steps} ---")

        motor = simulate_motor_commands()
        neuropil = simulate_neuropil_state()

        logger.info(f"  Motor commands: mean={np.mean(np.abs(motor)):.4f}, "
                     f"peak={np.max(np.abs(motor)):.4f}")
        logger.info(f"  Neuropil activity: mean={np.mean(np.abs(neuropil)):.4f}, "
                     f"peak={np.max(np.abs(neuropil)):.4f}")

        world_state = None
        if encoder.is_loaded:
            dummy_frames = np.random.randint(
                0, 256, (1, 3, 64, 64), dtype=np.uint8
            ).astype(np.float32) / 255.0
            indices, codes = encoder.encode(dummy_frames)
            logger.info(f"  Tokenizer: indices shape={indices.shape}, "
                         f"codes shape={codes.shape}")
            reconstructed = decoder.decode(codes)
            psnr = -10 * np.log10(np.mean((dummy_frames - reconstructed) ** 2))
            logger.info(f"  Tokenizer reconstruction: PSNR={psnr:.2f} dB")
            world_state = codes
        else:
            logger.info("  Tokenizer not loaded (checkpoints not found)")
            world_state = np.random.randn(1, 6, 3, 64, 64).astype(np.float32)

        agent_state = np.random.randn(10, 64).astype(np.float32)
        mu, entropy = env.step(agent_state)
        logger.info(f"  CosmosEnvironment: mu norm={np.linalg.norm(mu):.4f}, "
                     f"entropy={entropy:.4f}")

        if reasoner.is_loaded:
            analysis = reasoner.analyze_agent_trajectory(agent_state)
            logger.info(f"  Spatial analysis: coherence={analysis['spatial_coherence']:.4f}, "
                         f"variance={analysis['state_variance']:.4f}")
        else:
            logger.info("  Spatial analysis: skipped (Reason2 not loaded)")

        time.sleep(0.1)

    logger.info("\n" + "=" * 60)
    logger.info("Integration MVP complete.")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
