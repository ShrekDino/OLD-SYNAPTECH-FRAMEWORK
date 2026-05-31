#!/usr/bin/env python3
"""
CLI trainer for the FlyWire Connectome Hierarchical LSM.

Usage:
    python scripts/train.py [--temperature 0.4] [--passes 2] [--seed "text"]

If no --seed text is provided, uses the default baseline training corpus.
"""

import argparse

from flywire_lsm.logging import get_logger
from flywire_lsm.simulation import ReservoirSimulation

_LOG = get_logger()

BASELINE_TRAIN_TEXT = (
    "The FlyWire Connectome is a two-region hierarchical liquid state machine. "
    "It has five hundred neurons split into two modules. Module A handles fast "
    "sensory input. Module B provides slow deep memory retention. "
    "Hello there! How are you today? I am doing well thank you for asking. "
    "What is your name? My name is FlyWire. I am a brain simulation. "
    "Can you help me with this task? Yes I can help you with it. "
    "What is the answer to the question? The answer is forty two. "
    "Where is the library located? It is on the left side of the building. "
    "The quick brown fox jumps over the lazy dog near the river. "
    "She sells sea shells by the sea shore. The shells she sells are sea shells. "
    "The rain in Spain falls mainly on the plain. That is a fact. "
    "Machine learning is a fascinating field of study. Neural networks can learn "
    "complex patterns from data. Reservoir computing uses fixed random connections "
    "with trained readout weights. This is a powerful technique for temporal data. "
    "The weather today is sunny and warm. Tomorrow it will rain. Please remember "
    "to bring an umbrella with you. The temperature will be seventy five degrees. "
    "I like to read books about science and technology. My favorite subjects are "
    "physics chemistry and biology. Learning new things is always exciting and fun. "
    "What is the capital of France? The capital of France is Paris. "
    "What color is the sky? The sky is blue during the day and black at night. "
    "Tell me a story about a brave knight. The brave knight fought the dragon "
    "and saved the kingdom from destruction. Everyone was happy and grateful. "
    "Please turn on the lights. The room is too dark for reading and writing. "
    "Good morning! Did you sleep well? Yes I slept very well thank you. "
    "What would you like to eat for dinner? I would like to have pasta and salad. "
    "The cat sat on the mat. The dog ran after the ball. The bird flew in the sky. "
    "One two three four five six seven eight nine ten. These are the first ten "
    "numbers. Eleven twelve thirteen fourteen fifteen. Counting is easy and fun. "
    "Artificial intelligence is transforming the world in amazing ways. "
    "Self driving cars can navigate roads without human help. "
    "Voice assistants can answer questions and play music for you. "
    "Robots can build cars and explore distant planets like Mars. "
    "Hello world welcome to the FlyWire Connectome simulation. "
    "This system learns to predict the next character in a sequence. "
    "It uses a liquid state machine with two specialized brain regions. "
    "The sensory region registers input quickly. The memory region stores "
    "information over time. Together they form a powerful computing system. "
    "Can you teach me something new today? Yes I can teach you about reservoirs. "
    "A reservoir computer has three parts. The input layer the reservoir layer "
    "and the readout layer. Only the readout layer is trained. "
    "The reservoir is fixed and random. This makes training fast and simple. "
    "Why is the sky blue? It is blue because of Rayleigh scattering. "
    "Light from the sun scatters in the atmosphere. Blue light scatters more "
    "than red light. That is why the sky appears blue to our eyes. "
    "What is the meaning of life? That is a deep question. Some say it is "
    "forty two. Others say it is about learning and growing. "
    "Please write a poem about a tree. A tree stands tall and proud and free. "
    "Its branches reach up to the sky. Its roots go deep into the earth. "
    "It gives us shade and fruit and air. The tree is a friend to all. "
    "Where do stars come from? Stars are born in clouds of gas and dust. "
    "Gravity pulls the gas together until it becomes hot and dense. "
    "Then nuclear fusion begins and a star is born. Stars shine for billions "
    "of years before they fade away. That is the life cycle of a star. "
    "Tell me a joke. What do you call a fish with no eyes? A fsh. "
    "That is a silly joke but it makes me smile. "
    "The end of the training text is here. Thank you for reading it. "
    "I hope this helps the LSM learn language patterns better."
)


def main() -> None:
    parser = argparse.ArgumentParser(description="FlyWire Connectome CLI Trainer")
    parser.add_argument("--temperature", type=float, default=0.4, help="Generation temperature")
    parser.add_argument("--passes", type=int, default=2, help="Number of training passes")
    parser.add_argument("--seed", type=str, default=None, help="Seed text for generation")
    parser.add_argument("--text", type=str, default=None, help="Custom training text")
    parser.add_argument("--generate", type=int, default=0, help="Number of tokens to generate after training")
    args = parser.parse_args()

    _LOG.info("=" * 70)
    _LOG.info("Two-Region Hierarchical LSM -- CLI Demo")
    _LOG.info("=" * 70)

    sim = ReservoirSimulation(temperature=args.temperature)

    train_text = args.text if args.text else BASELINE_TRAIN_TEXT
    sim.train_readout(train_text, num_passes=args.passes)

    seed = args.seed if args.seed else "Hello there how are you"
    gen_len = args.generate if args.generate > 0 else 30
    _LOG.info("")
    sim.generate(seed_text=seed, max_gen_len=gen_len)

    _LOG.info("")
    _LOG.info("=" * 70)
    _LOG.info("DEMO COMPLETE")
    _LOG.info("=" * 70)


if __name__ == "__main__":
    main()
