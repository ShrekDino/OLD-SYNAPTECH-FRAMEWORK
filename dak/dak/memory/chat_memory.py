class ChatMemory:
    def __init__(self, buffer):
        self.buffer = buffer

    def record_turn(self, user_msg, erebus_reply, dak_state):
        if not self.buffer.available:
            return

        mu = dak_state.get('mu', None)
        if mu is None:
            import numpy as np
            mu = np.zeros(64)

        chat_text = f'User: {user_msg}\nErebus: {erebus_reply}'

        self.buffer.record(
            mu=mu,
            F=dak_state.get('F', 0.0),
            H_env=dak_state.get('H_env', 0.0),
            S_gen=dak_state.get('S_gen', 0.0),
            szilard_ratio=dak_state.get('szilard_ratio', 0.0),
            phase=dak_state.get('phase', 'UNKNOWN'),
            tick=dak_state.get('tick_count', 0),
            delta=dak_state.get('delta', 0.0),
            mutual_info=dak_state.get('mutual_info', 0.0),
            chat_text=chat_text,
        )

    def load_recent_context(self, n_turns=10):
        if not self.buffer.available:
            return []

        recent = self.buffer.get_recent(n_turns * 2)
        turns = []
        for ep in recent:
            meta = ep.get('metadata', {})
            chat = meta.get('chat_text', '')
            if chat:
                turns.append(chat)
                if len(turns) >= n_turns:
                    break
        return list(reversed(turns))
