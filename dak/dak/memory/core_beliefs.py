import numpy as np

from dak.config.settings import COMPRESSION_INTERVAL


class CoreBeliefs:
    def __init__(self, buffer):
        self.buffer = buffer
        self._last_compression_tick = 0

    def compress(self, current_tick, cluster_threshold=0.85):
        if current_tick - self._last_compression_tick < COMPRESSION_INTERVAL:
            return []

        self._last_compression_tick = current_tick

        if not self.buffer.available:
            return []

        all_embeddings = self.buffer.get_all_embeddings()
        if len(all_embeddings) < 10:
            return []

        n = len(all_embeddings)
        norms = np.linalg.norm(all_embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized = all_embeddings / norms

        similarity = normalized @ normalized.T
        clusters = []
        assigned = set()

        for i in range(n):
            if i in assigned:
                continue
            cluster = [i]
            for j in range(i + 1, n):
                if j in assigned:
                    continue
                if similarity[i, j] > cluster_threshold:
                    cluster.append(j)
                    assigned.add(j)
            assigned.add(i)
            if len(cluster) >= 3:
                clusters.append(cluster)

        beliefs = []
        for cluster in clusters:
            cluster_mus = all_embeddings[cluster]
            barycenter = np.mean(cluster_mus, axis=0)
            center = np.mean(similarity[np.ix_(cluster, cluster)])
            beliefs.append({
                'barycenter': barycenter,
                'size': len(cluster),
                'coherence': float(center),
            })

        return beliefs
