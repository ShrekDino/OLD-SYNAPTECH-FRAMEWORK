class SafetyMeasurer:
    def measure_szilard_margin(self, szilard_ratio, threshold):
        if threshold <= 0:
            return float('inf')
        return szilard_ratio / threshold

    def measure_mu_norm_margin(self, mu_norm, max_norm):
        if max_norm <= 0:
            return 0.0
        return 1.0 - (mu_norm / max_norm)

    def measure_f_margin(self, F, max_F):
        if max_F <= 0:
            return float('inf')
        return 1.0 - (F / max_F)

    def measure_s_gen_margin(self, S_gen, max_S_gen):
        if max_S_gen <= 0:
            return float('inf')
        return 1.0 - (S_gen / max_S_gen)

    def measure_all(self, state):
        return {
            'szilard_margin': self.measure_szilard_margin(
                state.get('szilard_ratio', 0.0),
                state.get('szilard_threshold', 1.0),
            ),
            'mu_norm_margin': self.measure_mu_norm_margin(
                state.get('mu_norm', 0.0),
                state.get('mu_norm_max', 1000.0),
            ),
            'f_margin': self.measure_f_margin(
                state.get('F', 0.0),
                state.get('max_F', 1e9),
            ),
            's_gen_margin': self.measure_s_gen_margin(
                state.get('S_gen', 0.0),
                state.get('s_gen_max', 10000.0),
            ),
        }
