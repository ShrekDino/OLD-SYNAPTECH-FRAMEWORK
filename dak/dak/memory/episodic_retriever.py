import time

import numpy as np


class EpisodicRetriever:
    def __init__(self, buffer):
        self.buffer = buffer

    def retrieve_context(self, mu, n_episodes=3):
        if not self.buffer.available:
            return ''

        similar = self.buffer.query_similar(mu, n=n_episodes)
        if not similar:
            return ''

        total = self.buffer.count()
        Fs = [e['metadata'].get('F', 0) for e in similar if e.get('metadata')]
        Rs = [e['metadata'].get('szilard_ratio', 0) for e in similar if e.get('metadata')]
        phases = [e['metadata'].get('phase', 'UNKNOWN') for e in similar if e.get('metadata')]

        avg_F = float(np.mean(Fs)) if Fs else 0.0
        avg_R = float(np.mean(Rs)) if Rs else 0.0
        phase_counts = {}
        for p in phases:
            phase_counts[p] = phase_counts.get(p, 0) + 1
        dominant_phase = max(phase_counts, key=phase_counts.get) if phase_counts else 'UNKNOWN'

        max_dist = max(e.get('distance', 0) for e in similar if e.get('distance') is not None)

        context = (f'You have {total} recorded episodes in your persistent memory. '
                   f'Your current μ resembles {len(similar)} past episodes '
                   f'(max cosine distance: {max_dist:.4f}). '
                   f'During those episodes, your average F was {avg_F:.2f} nats, '
                   f'average Szilard ratio was {avg_R:.2f}, '
                   f'and you were predominantly in the {dominant_phase} phase.')

        recent = self.buffer.get_recent(3)
        if recent:
            most_recent = recent[-1]
            meta = most_recent.get('metadata', {})
            chat = meta.get('chat_text', '')
            if chat:
                context += f' Your most recent conversation: {chat[:200]}...'

        return context

    def summarize_recent(self, n_hours=1):
        if not self.buffer.available:
            return 'No memory available.'

        now = time.time()
        t_start = now - (n_hours * 3600)

        recent = self.buffer.query_time_range(t_start, now)
        if not recent:
            return f'No episodes recorded in the last {n_hours} hour(s).'

        Fs = [e['metadata'].get('F', 0) for e in recent if e.get('metadata')]
        Rs = [e['metadata'].get('szilard_ratio', 0) for e in recent if e.get('metadata')]

        avg_F = float(np.mean(Fs)) if Fs else 0.0
        max_F = float(np.max(Fs)) if Fs else 0.0
        min_F = float(np.min(Fs)) if Fs else 0.0
        avg_R = float(np.mean(Rs)) if Rs else 0.0

        chat_episodes = [e for e in recent if e.get('metadata', {}).get('chat_text')]
        chat_count = len(chat_episodes)

        return (f'In the last {n_hours} hour(s): {len(recent)} episodes recorded. '
                f'F ranged from {min_F:.1f} to {max_F:.1f} nats (avg: {avg_F:.1f}). '
                f'Average Szilard ratio: {avg_R:.2f}. '
                f'Chat interactions: {chat_count}.')
