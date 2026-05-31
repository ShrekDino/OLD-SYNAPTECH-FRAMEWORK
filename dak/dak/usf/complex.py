import math
from typing import List, Tuple, Set, Optional

import torch
import torch.nn as nn
import torch.nn.functional as F

from dak.usf.config import SIMPLICIAL_DIM, VOCAB_SIZE, USF_DTYPE, USF_DEVICE


class Simplex:
    __slots__ = ('vertices', 'dimension', 'orientation')

    def __init__(self, vertices: Tuple[int, ...], orientation: int = 1):
        self.vertices = tuple(sorted(set(vertices)))
        self.dimension = len(self.vertices) - 1
        self.orientation = orientation

    def __hash__(self):
        return hash(self.vertices)

    def __eq__(self, other):
        return self.vertices == other.vertices

    def __repr__(self):
        return f'Simplex(dim={self.dimension}, verts={self.vertices})'

    def faces(self) -> List['Simplex']:
        f = []
        for i in range(len(self.vertices)):
            v = self.vertices[:i] + self.vertices[i + 1:]
            f.append(Simplex(v))
        return f

    def boundary(self) -> List[Tuple['Simplex', int]]:
        b = []
        for i in range(len(self.vertices)):
            v = self.vertices[:i] + self.vertices[i + 1:]
            sign = (-1) ** i * self.orientation
            b.append((Simplex(v), sign))
        return b


class SimplicialComplex:
    def __init__(self, fundamental_length: float = 1.0):
        self.simplices: Set[Simplex] = set()
        self.vertex_set: Set[int] = set()
        self.fundamental_length = fundamental_length
        self._adjacency: dict[int, Set[int]] = {}

    def add_simplex(self, simplex: Simplex) -> bool:
        if any(simplex in self.simplices for s in [simplex]):
            return False
        self.simplices.add(simplex)
        for v in simplex.vertices:
            self.vertex_set.add(v)
        self._rebuild_adjacency()
        return True

    def add_vertex(self, vertex: int) -> bool:
        if vertex in self.vertex_set:
            return False
        s = Simplex((vertex,))
        self.simplices.add(s)
        self.vertex_set.add(vertex)
        self._adjacency[vertex] = set()
        return True

    def _rebuild_adjacency(self):
        self._adjacency = {}
        for v in self.vertex_set:
            self._adjacency[v] = set()
        for s in self.simplices:
            verts = list(s.vertices)
            for i in range(len(verts)):
                for j in range(i + 1, len(verts)):
                    self._adjacency[verts[i]].add(verts[j])
                    self._adjacency[verts[j]].add(verts[i])

    def neighbors(self, vertex: int) -> Set[int]:
        return self._adjacency.get(vertex, set())

    def boundary_matrix(self, dim: int) -> torch.Tensor:
        d_simplices = [s for s in self.simplices if s.dimension == dim]
        dm1_simplices = [s for s in self.simplices if s.dimension == dim - 1]
        d_idx = {s: i for i, s in enumerate(d_simplices)}
        dm1_idx = {s: j for j, s in enumerate(dm1_simplices)}

        mat = torch.zeros(len(dm1_simplices), len(d_simplices), dtype=torch.int8)
        for s in d_simplices:
            for face, sign in s.boundary():
                if face in dm1_idx:
                    mat[dm1_idx[face], d_idx[s]] = sign
        return mat

    def total_vertices(self) -> int:
        return len(self.vertex_set)


class SimplicialEmbedding(nn.Module):
    def __init__(
        self,
        complex: SimplicialComplex,
        embedding_dim: int = SIMPLICIAL_DIM,
        vocab_size: int = VOCAB_SIZE,
    ):
        super().__init__()
        self.complex = complex
        self.embedding_dim = embedding_dim

        n_vertices = max(complex.vertex_set) + 1 if complex.vertex_set else vocab_size
        n_vertices = max(n_vertices, vocab_size)

        self.vertex_embeddings = nn.Embedding(
            n_vertices, embedding_dim, dtype=USF_DTYPE,
        )
        self.simplicial_proj = nn.Linear(
            embedding_dim, embedding_dim, dtype=USF_DTYPE,
        )

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.vertex_embeddings.weight, gain=1.0 / math.sqrt(2))
        nn.init.orthogonal_(self.simplicial_proj.weight)
        nn.init.zeros_(self.simplicial_proj.bias)

        with torch.no_grad():
            self._enforce_fundamental_length()

    def _enforce_fundamental_length(self):
        fl = self.complex.fundamental_length
        w = self.vertex_embeddings.weight
        for v in self.complex.vertex_set:
            for nv in self.complex.neighbors(v):
                if nv < len(w):
                    diff = w[v] - w[nv]
                    dist = diff.norm()
                    if dist < fl and dist > 1e-8:
                        scale = fl / dist
                        w[v] = w[v] + (scale - 1.0) * diff * 0.5
                        w[nv] = w[nv] - (scale - 1.0) * diff * 0.5

    def forward(self, token_ids: torch.Tensor) -> torch.Tensor:
        emb = self.vertex_embeddings(token_ids)
        emb = self.simplicial_proj(emb)
        return emb

    def co_boundary_regularization(self, token_ids: torch.Tensor) -> torch.Tensor:
        emb = self.vertex_embeddings(token_ids)
        batch, seq, d = emb.shape
        loss = 0.0
        count = 0
        for b in range(batch):
            for i in range(seq - 1):
                for j in range(i + 1, seq):
                    diff = emb[b, i] - emb[b, j]
                    dist = diff.norm()
                    if dist < self.complex.fundamental_length and dist > 1e-8:
                        loss = loss + (self.complex.fundamental_length - dist) ** 2
                        count += 1
        return loss / (count + 1)
