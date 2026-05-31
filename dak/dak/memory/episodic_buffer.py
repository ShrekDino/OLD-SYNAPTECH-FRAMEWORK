import json
import time
import os

import numpy as np

from dak.config.settings import MEMORY_PERSIST_DIR, CHROMA_COLLECTION_NAME


class EpisodicBuffer:
    def __init__(self, persist_dir=MEMORY_PERSIST_DIR, collection_name=CHROMA_COLLECTION_NAME):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self._collection = None
        self._client = None
        self._init_db()

    def _init_db(self):
        try:
            import chromadb
            self._client = chromadb.PersistentClient(path=self.persist_dir)
            try:
                self._collection = self._client.get_collection(self.collection_name)
            except Exception:
                self._collection = self._client.create_collection(
                    self.collection_name,
                    metadata={'hnsw:space': 'cosine'},
                )
        except ImportError:
            pass

    @property
    def available(self):
        return self._collection is not None

    def record(self, mu, F, H_env, S_gen, szilard_ratio, phase, tick,
               delta=None, mutual_info=None, chat_text=None, metadata=None):
        if not self.available:
            return

        episode_id = f'ep_{tick}_{int(time.time() * 1000)}'
        embedding = mu.astype(np.float64).tolist() if isinstance(mu, np.ndarray) else mu
        mu_norm = float(np.linalg.norm(mu)) if isinstance(mu, np.ndarray) else 0.0

        meta = {
            'timestamp': time.time(),
            'tick': tick,
            'F': float(F),
            'H_env': float(H_env),
            'S_gen': float(S_gen),
            'szilard_ratio': float(szilard_ratio),
            'phase': str(phase),
            'mu_norm': mu_norm,
        }
        if delta is not None:
            meta['delta'] = float(delta)
        if mutual_info is not None:
            meta['mutual_info'] = float(mutual_info)
        if chat_text is not None:
            meta['chat_text'] = chat_text
        if metadata:
            meta.update(metadata)

        try:
            self._collection.add(
                ids=[episode_id],
                embeddings=[embedding],
                metadatas=[meta],
            )
        except Exception:
            pass

    def query_similar(self, mu, n=5):
        if not self.available:
            return []

        embedding = mu.astype(np.float64).tolist() if isinstance(mu, np.ndarray) else mu
        try:
            results = self._collection.query(
                query_embeddings=[embedding],
                n_results=min(n, self.count()),
            )
            return self._format_results(results)
        except Exception:
            return []

    def query_time_range(self, t_start, t_end):
        if not self.available:
            return []
        try:
            results = self._collection.get(
                where={'$and': [
                    {'timestamp': {'$gte': t_start}},
                    {'timestamp': {'$lte': t_end}},
                ]},
            )
            return self._format_results(results)
        except Exception:
            return []

    def get_recent(self, n=10):
        if not self.available:
            return []

        total = self.count()
        if total == 0:
            return []
        try:
            results = self._collection.get(limit=min(n, total))
            return self._format_results(results)
        except Exception:
            return []

    def count(self):
        if not self.available:
            return 0
        try:
            return self._collection.count()
        except Exception:
            return 0

    def delete_old(self, max_episodes=10000):
        if not self.available:
            return
        total = self.count()
        if total <= max_episodes:
            return
        try:
            results = self._collection.get(limit=total - max_episodes)
            if results and results['ids']:
                self._collection.delete(ids=results['ids'])
        except Exception:
            pass

    def get_all_embeddings(self):
        if not self.available:
            return np.array([])
        try:
            results = self._collection.get(include=['embeddings'])
            if results and results['embeddings']:
                return np.array(results['embeddings'])
            return np.array([])
        except Exception:
            return np.array([])

    def _format_results(self, results):
        if not results or not results['ids']:
            return []
        formatted = []
        for i, ep_id in enumerate(results['ids']):
            entry = {'id': ep_id}
            if results.get('metadatas') and results['metadatas'][i]:
                entry['metadata'] = results['metadatas'][i]
            if results.get('distances') and results['distances'][i] is not None:
                entry['distance'] = float(results['distances'][i])
            formatted.append(entry)
        return formatted
