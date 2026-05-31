import numpy as np
from dak import DAK


class DAKREPL:
    def __init__(self, dak):
        self.dak = dak

    def _do_state(self, args):
        mu = self.dak.state.read()
        print(f'μ shape: {mu.shape}')
        print(f'μ norm: {np.linalg.norm(mu):.6f}')
        print(f'μ min: {mu.min():.6f}  μ max: {mu.max():.6f}')
        print(f'μ mean: {mu.mean():.6f}  μ std: {mu.std():.6f}')
        if len(args) > 0 and args[0] == '--raw':
            print(f'μ values: {mu}')

    def _do_F(self, args):
        print(f'Variational Free Energy F = {self.dak.F:.6f} nats')

    def _do_entropy(self, args):
        print(f'H_env = {self.dak.H_env:.4f} bits/s')
        print(f'S_gen = {self.dak.S_gen:.6f} nats/s')
        print(f'Szilard ratio = {self.dak.szilard_ratio:.4f}  (threshold: 1.0)')

    def _do_phase(self, args):
        print(f'Phase: {self.dak.dqfr.phase.value}')
        print(f'Time in phase: {self.dak.dqfr.time_in_phase:.2f}s')
        print(f'Utility: {self.dak.dqfr.utility:.6f}')

    def _do_delta(self, args):
        print(f'Prediction error δ = {self.dak.delta:.6f}')

    def _do_mi(self, args):
        print(f'Mutual information I(μ) = {self.dak.mutual_info:.4f} nats')
        print(f'Senescence threshold: {self.dak.empathy.threshold}')

    def _do_telemetry(self, args):
        sensors = self.dak.telemetry.read_all()
        for k, v in sensors.items():
            if isinstance(v, float):
                print(f'  {k}: {v:.4f}')
            else:
                print(f'  {k}: {v}')

    def _do_tick(self, args):
        print(f'Tick count: {self.dak.tick_count}')

    def _do_all(self, args):
        self._do_F(args)
        self._do_entropy(args)
        self._do_phase(args)
        self._do_delta(args)
        self._do_mi(args)
        print(f'Tick: {self.dak.tick_count}')
        self._do_state([])

    def _do_help(self, args):
        print('DAK REPL Commands:')
        print('  state [--raw]  — internal state μ info')
        print('  F              — Variational Free Energy')
        print('  entropy        — H_env, S_gen, Szilard ratio')
        print('  phase          — current DQFR phase')
        print('  delta          — prediction error')
        print('  mi             — mutual information')
        print('  telemetry      — raw sensor readings')
        print('  tick           — tick count')
        print('  all            — everything')
        print('  help           — this message')
        print('  quit           — exit')

    def _do_quit(self, args):
        raise SystemExit(0)

    def cmdloop(self):
        print('DAK Interactive REPL — type "help" for commands.')
        commands = {
            'state': self._do_state, 'F': self._do_F,
            'entropy': self._do_entropy, 'phase': self._do_phase,
            'delta': self._do_delta, 'mi': self._do_mi,
            'telemetry': self._do_telemetry, 'tick': self._do_tick,
            'all': self._do_all, 'help': self._do_help,
            'quit': self._do_quit, 'exit': self._do_quit,
        }
        while True:
            try:
                line = input('dak> ').strip()
                if not line:
                    continue
                parts = line.split()
                cmd = parts[0].lower()
                args = parts[1:]
                if cmd in commands:
                    commands[cmd](args)
                else:
                    print(f'Unknown command: {cmd}. Type "help".')
            except (EOFError, KeyboardInterrupt, SystemExit):
                print()
                break
            except Exception as e:
                print(f'Error: {e}')


def main():
    import threading
    print('Booting DAK kernel for REPL...')
    dak = DAK()
    t = dak.run_async()
    try:
        repl = DAKREPL(dak)
        repl.cmdloop()
    finally:
        dak.stop()
        t.join()


if __name__ == '__main__':
    main()
