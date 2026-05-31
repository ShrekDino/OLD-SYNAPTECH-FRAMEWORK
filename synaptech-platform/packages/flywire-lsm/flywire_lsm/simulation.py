
import numpy as np

from flywire_lsm.config import (
    CHAR_TO_IDX,
    DEFAULT_SEED,
    IDX_TO_CHAR,
    N_A,
    N_B,
    N_NEURONS,
    STEPS_PER_TOKEN,
    TEMPERATURE,
    VOCAB_SIZE,
    WASHOUT_STEPS,
)
from flywire_lsm.core import HierarchicalReservoir
from flywire_lsm.logging import FlyWireLogger, get_logger
from flywire_lsm.readout import LinearReadout
from flywire_lsm.text_encoder import TextEncoder

_LOG = get_logger()


class ReservoirSimulation:
    def __init__(self, temperature: float = TEMPERATURE) -> None:
        _LOG.info("=" * 70)
        _LOG.info("[INIT] FlyWire LSM Text Processor -- Initialising")
        _LOG.info("=" * 70)

        self.temperature = temperature
        self.rng = np.random.default_rng(DEFAULT_SEED)
        FlyWireLogger.log_memory(_LOG, "pre-init")
        self.hlayer = HierarchicalReservoir()
        FlyWireLogger.log_memory(_LOG, "post-reservoir")
        self.encoder = TextEncoder(N_NEURONS)
        self.readout = LinearReadout(N_A + N_B, VOCAB_SIZE)
        self.latest_accuracy = 0.0
        self._training_buffer_X: list[np.ndarray] = []
        self._training_buffer_Y: list[np.ndarray] = []
        FlyWireLogger.log_memory(_LOG, "post-readout")

        _LOG.info("=" * 70)
        _LOG.info("[INIT] Initialisation complete")
        _LOG.info("=" * 70)

    def train_readout(self, train_text: str, warm_start: bool = False,
                      cumulative: bool = True, num_passes: int = 2) -> float:
        _LOG.info("=" * 70)
        _LOG.info("[TRAIN] Readout training on \"%s\"", train_text)
        _LOG.info("[TRAIN] Washout=%d steps/token=%d  warm_start=%s  cumulative=%s  passes=%d",
                  WASHOUT_STEPS, STEPS_PER_TOKEN, warm_start, cumulative, num_passes)

        if not warm_start:
            self.hlayer.reset()

        if not cumulative:
            self._training_buffer_X = []
            self._training_buffer_Y = []

        valid_chars = [c for c in train_text if c in CHAR_TO_IDX]
        n_valid = len(valid_chars)
        _LOG.info("[TRAIN] Next-token prediction: %d valid chars, wrapping final token  passes=%d",
                  n_valid, num_passes)

        collected_in_pass = 0
        for p in range(num_passes):
            if p > 0:
                _LOG.info("[TRAIN] Pass %d/%d (warm, reservoir carries over)", p + 1, num_passes)
            for i, char in enumerate(valid_chars):
                next_char = valid_chars[(i + 1) % n_valid]
                next_idx = CHAR_TO_IDX[next_char]
                target = np.zeros(VOCAB_SIZE, dtype=np.float64)
                target[next_idx] = 1.0
                I_inj = self.encoder.encode(char)

                for step_in_token in range(STEPS_PER_TOKEN):
                    self.hlayer.step(I_inj, log=False)
                    if step_in_token + 1 > WASHOUT_STEPS:
                        self._training_buffer_X.append(self.hlayer.get_state().copy())
                        self._training_buffer_Y.append(target.copy())
                        collected_in_pass += 1

        X_arr = np.array(self._training_buffer_X)
        Y_arr = np.array(self._training_buffer_Y)
        _LOG.info("[TRAIN] Collected %d samples (%d this call)  X=%s Y=%s",
                  X_arr.shape[0], collected_in_pass, X_arr.shape, Y_arr.shape)
        acc = self.readout.train_ridge(X_arr, Y_arr)
        self.latest_accuracy = float(acc)
        return acc

    def run_inference(self, text: str) -> tuple[list[str], list[np.ndarray]]:
        _LOG.info("=" * 70)
        _LOG.info("[RUN] Inference on \"%s\"", text)
        _LOG.info("=" * 70)

        self.hlayer.reset()
        predictions: list[str] = []
        all_logits: list[np.ndarray] = []

        for pos, char in enumerate(text):
            if char not in CHAR_TO_IDX:
                predictions.append(char)
                _LOG.warning("[RUN] Skipping unknown char  pos=%d '%s'", pos, char)
                continue

            _LOG.info("[RUN] Token %d: '%s' -> %d steps", pos, char, STEPS_PER_TOKEN)
            I_inj = self.encoder.encode(char)

            for _ in range(STEPS_PER_TOKEN):
                self.hlayer.step(I_inj)

            state = self.hlayer.get_state()
            _LOG.info("[OUTPUT] state: mu=%.4f sigma=%.4f [%.4f, %.4f]",
                      float(np.mean(state)), float(np.std(state)),
                      float(np.min(state)), float(np.max(state)))

            logits = self.readout.predict(state)
            all_logits.append(logits)

            pred_char, pred_idx = self.readout.decode(logits)
            predictions.append(pred_char)

            top5 = np.argsort(logits)[-5:][::-1]
            top5_str = ", ".join(
                f"'{IDX_TO_CHAR[i]}'={logits[i]:+.4f}" for i in top5
            )
            _LOG.info("[OUTPUT] Logits top-5: [%s]", top5_str)
            _LOG.info("[OUTPUT] Pred='%s' expect='%s' %s", pred_char, char,
                      "\u2713" if pred_char == char else "\u2717")

            FlyWireLogger.log_memory(_LOG, f"after '{char}'")

        valid_chars = [c for c in text if c in CHAR_TO_IDX]
        correct = sum(1 for p, t in zip(predictions, valid_chars) if p == t)
        num_valid = len(valid_chars)
        accuracy = correct / num_valid if num_valid else 0.0

        _LOG.info("=" * 70)
        _LOG.info("[SUMMARY] Input:       \"%s\"", text)
        _LOG.info("[SUMMARY] Predicted:   \"%s\"", "".join(predictions))
        _LOG.info("[SUMMARY] Accuracy:    %.4f (%d/%d)", accuracy, correct, num_valid)
        _LOG.info("[SUMMARY] Total steps: %d", self.hlayer.step_count)
        _LOG.info("=" * 70)

        return predictions, all_logits

    def compare_priming_effect(self, char: str) -> None:
        _LOG.info("=" * 70)
        _LOG.info("[PRIMING] Priming effect comparison -- first char '%s'", char)
        _LOG.info("=" * 70)

        self.hlayer.reset()
        I_inj = self.encoder.encode(char)
        for _ in range(STEPS_PER_TOKEN):
            self.hlayer.step(I_inj)
        state = self.hlayer.get_state()
        logits_cold = self.readout.predict(state)

        top5 = np.argsort(logits_cold)[-5:][::-1]
        top5_str_cold = ", ".join(
            f"'{IDX_TO_CHAR[i]}'={logits_cold[i]:+.4f}" for i in top5
        )
        pred_cold, _ = self.readout.decode(logits_cold)
        _LOG.info("[PRIMING] Unprimed (cold) top-5: [%s]", top5_str_cold)
        _LOG.info("[PRIMING] Unprimed prediction:  '%s'", pred_cold)

        self.hlayer.reset()
        _LOG.info("[PRIMING] Warm-up: %d steps background noise amp=0.05", 30)
        for _ in range(30):
            noise = 0.05 * self.rng.normal(0.0, 1.0, size=N_NEURONS)
            self.hlayer.step(noise, log=False)
        _LOG.info("[PRIMING] Post-warmup: V_A mu=%.4f sigma=%.4f  V_B mu=%.4f sigma=%.4f",
                  float(np.mean(self.hlayer.v_A)), float(np.std(self.hlayer.v_A)),
                  float(np.mean(self.hlayer.v_B)), float(np.std(self.hlayer.v_B)))

        I_inj = self.encoder.encode(char)
        for _ in range(STEPS_PER_TOKEN):
            self.hlayer.step(I_inj)
        state = self.hlayer.get_state()
        logits_primed = self.readout.predict(state)

        top5 = np.argsort(logits_primed)[-5:][::-1]
        top5_str_primed = ", ".join(
            f"'{IDX_TO_CHAR[i]}'={logits_primed[i]:+.4f}" for i in top5
        )
        pred_primed, _ = self.readout.decode(logits_primed)
        _LOG.info("[PRIMING] Primed     top-5: [%s]", top5_str_primed)
        _LOG.info("[PRIMING] Primed prediction:  '%s'", pred_primed)

        correct = "\u2713" if pred_primed == char else "\u2717"
        _LOG.info("[PRIMING] Primed '%s' -> '%s' %s", char, pred_primed, correct)

    def generate(
        self, seed_text: str = "fly", max_gen_len: int = 5,
    ) -> str:
        _LOG.info("=" * 70)
        _LOG.info("[GENERATION] Seed=\"%s\" max_gen_len=%d", seed_text, max_gen_len)
        _LOG.info("=" * 70)

        generated: list[str] = []

        for pos, char in enumerate(seed_text):
            if char not in CHAR_TO_IDX:
                _LOG.warning("[GENERATION] Skipping unknown char pos=%d '%s'", pos, char)
                generated.append(char)
                continue

            _LOG.info("[GENERATION] Seed token %d: '%s' -> %d steps", pos, char, STEPS_PER_TOKEN)
            I_inj = self.encoder.encode(char)
            for _ in range(STEPS_PER_TOKEN):
                self.hlayer.step(I_inj)
            state = self.hlayer.get_state()
            logits = self.readout.predict(state)
            pred_char, _ = self.readout.decode(logits)
            generated.append(pred_char)

            top5 = np.argsort(logits)[-5:][::-1]
            top5_str = ", ".join(
                f"'{IDX_TO_CHAR[i]}'={logits[i]:+.4f}" for i in top5
            )
            _LOG.info("[GENERATION]   -> predicted '%s'  top-5: [%s]  (expected '%s' %s)",
                      pred_char, top5_str, char,
                      "\u2713" if pred_char == char else "\u2717")

        for gen_i in range(max_gen_len):
            last_pred = generated[-1]
            if last_pred not in CHAR_TO_IDX:
                _LOG.warning("[GENERATION] Unknown prediction '%s', stopping", last_pred)
                break

            _LOG.info("[GENERATION] Gen step %d: input '%s' -> %d steps  T=%.1f",
                      gen_i, last_pred, STEPS_PER_TOKEN, self.temperature)
            I_inj = self.encoder.encode(last_pred)
            for _ in range(STEPS_PER_TOKEN):
                self.hlayer.step(I_inj)
            state = self.hlayer.get_state()
            logits = self.readout.predict(state)

            scaled = logits / self.temperature
            scaled -= scaled.max()
            probs = np.exp(scaled)
            probs /= probs.sum()
            next_idx = int(self.rng.choice(VOCAB_SIZE, p=probs))
            next_char = IDX_TO_CHAR[next_idx]
            generated.append(next_char)

            top5 = np.argsort(logits)[-5:][::-1]
            top5_str = ", ".join(
                f"'{IDX_TO_CHAR[i]}'={logits[i]:+.4f}" for i in top5
            )
            _LOG.info("[GENERATION]   -> sampled '%s'  argmax='%s'  top-5: [%s]",
                      next_char, IDX_TO_CHAR[int(np.argmax(logits))], top5_str)

        result = "".join(generated)
        _LOG.info("[GENERATION] Result: \"%s\"", result)
        return result

    def save_readout(self, path: str = "readout_weights.npz") -> None:
        self.readout.save_weights(path)

    def load_readout(self, path: str = "readout_weights.npz") -> None:
        self.readout.load_weights(path)
