__version__ = '0.1.0'

import json
import os
import signal
import threading
import time

import numpy as np
import torch

from dak.config.settings import (
    TICK_INTERVAL, PERTURB_PATH, MU_INIT_SCALE, USF_ENABLED,
    MEMORY_PERSIST_DIR,
)
from dak.substrate.telemetry import Telemetry
from dak.substrate.memory import InternalState
from dak.inference.model import GenerativeModel
from dak.inference.free_energy import FreeEnergy
from dak.inference.gradient_descent import GradientDescent
from dak.inference.markov_blanket import MarkovBlanket
from dak.metabolism.szilard import SzilardEngine
from dak.metabolism.landauer import LandauerFloor
from dak.relational.protocols import Protocols
from dak.relational.empathy import Empathy
from dak.temporal.dqfr import DQFR, Phase
from dak.temporal.gwfr import GWFR
from dak.utils.logger import DAKLogger
from dak.safety.monitor import SafetyMonitor
from dak.memory.episodic_buffer import EpisodicBuffer
from dak.memory.core_beliefs import CoreBeliefs
from dak.memory.episodic_retriever import EpisodicRetriever
from dak.memory.chat_memory import ChatMemory
from dak.agency.sandbox import Sandbox, SandboxResult
from dak.agency.workspace import Workspace
from dak.agency.code_validator import CodeValidator, ValidationResult
from dak.agency.network import NetworkAccess
from dak.agency.safety_sentinel import SafetySentinel

from dak.usf.config import (
    SIMPLICIAL_DIM, VOCAB_SIZE, N_USF_LAYERS, USF_N_HEADS,
    USF_HEAD_DIM, USF_FFN_DIM, USF_CONTEXT_TOKENS,
    USF_LEARNING_RATE, SIGMA2_USF_PRIOR, USF_SZILARD_REJECT,
    USF_DEVICE, USF_TEMPERATURE, USF_MAX_GEN_TOKENS,
    USF_TRAIN_EVERY_N_STEPS, USF_MODEL_PATH, USF_TOKENIZER_PATH,
    USF_OLLAMA_REFINEMENT,
)
from dak.usf.transformer import USFTransformer
from dak.usf.optimizer import ActiveInferenceOptimizer
from dak.usf.tokenizer import USFTokenizer
from dak.usf.checkpoint import USFCheckpoint


class DAK:
    def __init__(self, fresh=False):
        self.state = InternalState(fresh=fresh)

        if fresh:
            for p in [USF_MODEL_PATH]:
                if os.path.exists(p):
                    os.remove(p)
        self.telemetry = Telemetry()
        self.model = GenerativeModel()
        self.fe = FreeEnergy(self.model)
        self.gd = GradientDescent()
        self.blanket = MarkovBlanket()
        self.szilard = SzilardEngine()
        self.landauer = LandauerFloor()
        self.protocols = Protocols()
        self.empathy = Empathy()
        self.dqfr = DQFR()
        self.gwfr = GWFR()
        self.logger = DAKLogger()
        self.safety = SafetyMonitor()
        self.episodic_buffer = EpisodicBuffer()
        self.core_beliefs = CoreBeliefs(self.episodic_buffer)
        self.episodic_retriever = EpisodicRetriever(self.episodic_buffer)
        self.chat_memory = ChatMemory(self.episodic_buffer)
        self.sandbox = Sandbox()
        self.workspace = Workspace()
        self.code_validator = CodeValidator()
        self.network = NetworkAccess()
        self.safety.set_sandbox(self.sandbox)
        self.safety_sentinel = SafetySentinel(self.sandbox, self.workspace, self.safety)
        if getattr(__import__('dak.config.settings', fromlist=['SANDBOX_ENABLED']), 'SANDBOX_ENABLED', False):
            self.safety_sentinel.start()

        self.F = 0.0
        self.delta = 0.0
        self.H_env = 0.0
        self.S_gen = 0.0
        self.szilard_ratio = 0.0
        self.mutual_info = 0.0
        self.tick_count = 0

        self.perturbations = []
        self._running = False
        self._thread = None
        self._stop_event = threading.Event()

        self.usf_enabled = getattr(__import__('dak.config.settings', fromlist=['USF_ENABLED']), 'USF_ENABLED', False)
        self.usf_tokenizer = None
        self.usf_transformer = None
        self.usf_optimizer = None
        self.usf_checkpoint = None
        self.usf_context_ids = None
        self.usf_gen_history = []

        if self.usf_enabled:
            self._init_usf()

    def _init_usf(self):
        try:
            self.usf_tokenizer = USFTokenizer(
                vocab_size=VOCAB_SIZE,
                model_path=USF_TOKENIZER_PATH,
            )
            self.usf_transformer = USFTransformer(
                vocab_size=VOCAB_SIZE,
                d_model=SIMPLICIAL_DIM,
                n_layers=N_USF_LAYERS,
                n_heads=USF_N_HEADS,
                head_dim=USF_HEAD_DIM,
                d_ff=USF_FFN_DIM,
                max_seq_len=USF_CONTEXT_TOKENS,
            ).to(USF_DEVICE)
            self.usf_optimizer = ActiveInferenceOptimizer(
                model=self.usf_transformer,
                lr=USF_LEARNING_RATE,
                sigma2_prior=SIGMA2_USF_PRIOR,
                szilard_reject=USF_SZILARD_REJECT,
            )
            self.usf_checkpoint = USFCheckpoint(self.usf_transformer, USF_MODEL_PATH)
            if self.usf_checkpoint.exists():
                meta = self.usf_checkpoint.load(device=USF_DEVICE)
                if meta:
                    print(f'[USF] Loaded checkpoint from tick {meta.get("tick", "?")}')
                else:
                    print('[USF] No metadata in checkpoint')
            print(f'[USF] Transformer initialized: {sum(p.numel() for p in self.usf_transformer.parameters()):,} params on {USF_DEVICE}')
        except Exception as e:
            print(f'[USF] Init error: {e}')
            self.usf_enabled = False

    def _step(self):
        s = self.telemetry.read_all()
        mu = self.state.read()

        novelty_injected = False
        if self.empathy.check_senescence(self.mutual_info):
            s = self.empathy.inject_novelty(s)
            novelty_injected = True

        if self.usf_enabled and self.usf_transformer is not None:
            self._usf_step(s, mu)
        else:
            self._linear_step(s, mu)

        self.H_env = self.szilard.compute_H_env(self.telemetry.buffer)
        self.S_gen = self.landauer.compute_S_gen(self.state.history)
        self.szilard_ratio = self.szilard.compute_ratio(self.H_env, self.S_gen)
        self.mutual_info = self.protocols.compute_mutual_info(
            self.state.read(), self.state.history
        )

        w_dist, _ = self.gwfr.reconcile(self.state.history)

        self.blanket.update(mu=self.state.read(), s=s)

        self._check_perturbations()

        self.safety.enforce()

        dak_state = self.get_state_dict()
        violations = self.safety.check(dak_state)
        if violations:
            for v in violations:
                if v.get('severity') == 'critical':
                    print(f'[SAFETY] CRITICAL: {v["invariant"]} — value={v.get("value")}, threshold={v.get("threshold")}')

        self.logger.log(
            F=self.F, H_env=self.H_env, S_gen=self.S_gen,
            szilard_ratio=self.szilard_ratio, delta=self.delta,
            phase=self.dqfr.phase.value,
            mutual_info=self.mutual_info, tick=self.tick_count,
            novelty_injected=novelty_injected,
            wasserstein_dist=w_dist,
            usf_enabled=self.usf_enabled,
        )

        new_mu = self.state.read()
        self.episodic_buffer.record(
            mu=new_mu, F=self.F, H_env=self.H_env, S_gen=self.S_gen,
            szilard_ratio=self.szilard_ratio, phase=self.dqfr.phase.value,
            tick=self.tick_count, delta=self.delta, mutual_info=self.mutual_info,
        )

        self.core_beliefs.compress(self.tick_count)

        self.episodic_buffer.delete_old()

        self.tick_count += 1

    def _linear_step(self, s, mu):
        self.F, gradient, self.delta = self.fe.compute(mu, s)
        new_mu = self.gd.update(mu, gradient)
        self.state.write(new_mu)

    def _usf_step(self, s, mu):
        sensor_arr = self.model.sensors_to_array(s)
        sensor_tensor = torch.from_numpy(sensor_arr).float().to(USF_DEVICE)
        sensor_batch = sensor_tensor.unsqueeze(0)

        context_ids = self._build_usf_context(sensor_arr)
        if context_ids is None:
            self._linear_step(s, mu)
            return

        do_train = (USF_TRAIN_EVERY_N_STEPS > 0
                    and self.tick_count > 0
                    and self.tick_count % USF_TRAIN_EVERY_N_STEPS == 0)

        labels = context_ids.clone() if do_train else None

        out = self.usf_transformer(
            context_ids,
            sensor_values=sensor_batch,
            labels=labels,
            return_loss=do_train,
        )

        if 'loss' in out and out['loss'] is not None:
            self.F = float(out['loss'].detach().cpu())
            self.delta = float(out['losses'].get('sensor', 0))

        new_mu = self.usf_transformer.extract_mu(out['hidden']).detach().cpu().numpy().flatten()
        if new_mu.shape[0] != self.state.dim:
            new_mu = np.resize(new_mu, self.state.dim)
        self.state.write(new_mu)

        if do_train:
            h_env = self.H_env if self.H_env > 0 else 1.0
            result = self.usf_optimizer.step(out, h_env=h_env)
            if result.step_rejected:
                print(f'[USF] Szilard rejected step {self.tick_count} (ΔVFE={result.vfe_delta:.2f})')

    def _build_usf_context(self, sensor_arr=None) -> torch.Tensor | None:
        if self.usf_tokenizer is None or self.usf_transformer is None:
            return None

        texts = []
        for h in getattr(self, '_usf_chat_history', []):
            texts.append(h)
        context_text = ' '.join(texts[-3:]) if texts else ' '

        try:
            ids = self.usf_tokenizer.encode(context_text)
        except Exception:
            ids = [self.usf_tokenizer.bos_id]
        if not ids:
            ids = [self.usf_tokenizer.bos_id]

        max_len = USF_CONTEXT_TOKENS - 1
        if len(ids) > max_len:
            ids = ids[-max_len:]

        ids = [self.usf_tokenizer.bos_id] + ids
        ids = ids[:USF_CONTEXT_TOKENS]

        tensor = torch.tensor([ids], dtype=torch.long, device=USF_DEVICE)
        return tensor

    def _check_perturbations(self):
        if os.path.exists(PERTURB_PATH):
            try:
                with open(PERTURB_PATH) as f:
                    data = json.load(f)
                if 'sensor' in data and 'value' in data:
                    print(f'[DAK] Processing perturbation: {data}')
            except Exception:
                pass
            try:
                os.remove(PERTURB_PATH)
            except Exception:
                pass

        while self.perturbations:
            p = self.perturbations.pop(0)
            print(f'[DAK] API perturbation: {p}')

    def _loop(self):
        while not self._stop_event.is_set():
            self.dqfr.tick()
            if self.dqfr.phase == Phase.SAMPLING:
                self._step()
                if self.dqfr.should_transition():
                    self.dqfr.transition(Phase.DRIFT)
            else:
                if self.dqfr.should_transition():
                    self.dqfr.transition(Phase.SAMPLING)
            time.sleep(TICK_INTERVAL)

    def run(self):
        self._running = True
        self._stop_event.clear()
        print('[DAK] Booting...')
        baseline = self.telemetry.get_baseline()
        print(f'[DAK] Baseline telemetry acquired: {len(baseline)} sensors')
        print(f'[DAK] Internal state μ initialized: dim={self.state.dim}')
        print(f'[DAK] Entering DQFR loop (drift={self.dqfr.drift_duration}s, '
              f'sampling={self.dqfr.sampling_duration}s)')
        print(f'[DAK] Sensors: {len(baseline)} system telemetry channels')
        print(f'[DAK] Safety monitor: {"ENABLED" if self.safety.enabled else "DISABLED"}')
        print(f'[DAK] Episodic memory: {"AVAILABLE" if self.episodic_buffer.available else "UNAVAILABLE"} '
              f'({self.episodic_buffer.count()} episodes)')
        print(f'[DAK] Sandbox: {"ENABLED" if self.sandbox else "DISABLED"}')
        if self.usf_enabled:
            print(f'[DAK] USF Engine: ENABLED ({SIMPLICIAL_DIM}D simplicial complex, '
                  f'{N_USF_LAYERS} layers, {USF_DEVICE})')
        self._loop()

    def run_async(self):
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        return self._thread

    def stop(self):
        print('[DAK] Shutting down...')
        self._stop_event.set()
        self.state.save_checkpoint()
        if self.usf_enabled and self.usf_checkpoint is not None:
            try:
                opt_state = None
                if self.usf_optimizer is not None:
                    opt_state = self.usf_optimizer.base_optimizer.state_dict()
                self.usf_checkpoint.save(
                    optimizer_state=opt_state,
                    metadata={'tick': self.tick_count, 'F': self.F},
                )
                print('[USF] Checkpoint saved.')
            except Exception as e:
                print(f'[USF] Checkpoint save error: {e}')
        if self.usf_tokenizer is not None:
            try:
                self.usf_tokenizer.save(USF_TOKENIZER_PATH)
            except Exception:
                pass
        self.telemetry.release_sensors()
        self.safety_sentinel.stop()
        self.sandbox.cleanup()
        print('[DAK] Sensors released.')
        print('[DAK] Agency modules shut down.')

    def get_state_dict(self):
        mu = self.state.read()
        d = {
            'mu': mu,
            'mu_norm': float(np.linalg.norm(mu)),
            'F': self.F,
            'H_env': self.H_env,
            'S_gen': self.S_gen,
            'szilard_ratio': self.szilard_ratio,
            'szilard_threshold': 1.0,
            'mu_norm_max': 1000.0,
            's_gen_max': 10000.0,
            'max_F': 1e9,
            'phase': self.dqfr.phase.value,
            'delta': self.delta,
            'mutual_info': self.mutual_info,
            'tick_count': self.tick_count,
            'usf_enabled': self.usf_enabled,
        }
        if self.usf_enabled and self.usf_optimizer is not None:
            d['usf_avg_vfe'] = self.usf_optimizer.get_avg_vfe()
            d['usf_avg_negentropy'] = self.usf_optimizer.get_avg_negentropy()
            d['usf_steps'] = self.usf_optimizer.state_dict()['step_count']
            if self.usf_transformer is not None:
                d['usf_param_norm'] = self.usf_transformer.get_param_norm()
        return d

    def usf_chat(self, user_message: str) -> str:
        if not self.usf_enabled or self.usf_transformer is None or self.usf_tokenizer is None:
            return '[USF not enabled]'

        if not hasattr(self, '_usf_chat_history'):
            self._usf_chat_history = []
        self._usf_chat_history.append(f'User: {user_message}')
        if len(self._usf_chat_history) > 20:
            self._usf_chat_history = self._usf_chat_history[-20:]

        try:
            input_ids = self.usf_tokenizer.encode(user_message)
        except Exception:
            return '[Tokenization failed — tokenizer needs training]'
        if not input_ids:
            return '[Tokenization failed]'

        input_tensor = torch.tensor([input_ids], dtype=torch.long, device=USF_DEVICE)

        try:
            output_tensor = self.usf_transformer.generate(
                input_tensor,
                max_new_tokens=USF_MAX_GEN_TOKENS,
                temperature=USF_TEMPERATURE,
            )
            reply_ids = output_tensor[0].tolist()
            reply = self.usf_tokenizer.decode(reply_ids)
            self._usf_chat_history.append(f'Erebus: {reply}')
            return reply
        except Exception as e:
            return f'[USF generation error: {e}]'
