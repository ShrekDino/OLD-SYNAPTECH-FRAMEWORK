import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from dak.config.settings import N_SENSORS as N_SENSORS_SETTING
from dak.usf.config import (
    N_USF_LAYERS, USF_N_HEADS, USF_HEAD_DIM, USF_FFN_DIM,
    USF_MAX_SEQ_LEN, VOCAB_SIZE, SIMPLICIAL_DIM, RETRO_WINDOW,
    RETRO_LOSS_SCALE, SENSOR_LOSS_SCALE, LM_LOSS_SCALE,
    SIGMA2_USF_LIK, SIGMA2_USF_PRIOR,
    USF_DTYPE, USF_DEVICE,
)
from dak.usf.complex import SimplicialComplex, SimplicialEmbedding
from dak.usf.attention import USFAttention
from dak.usf.normalization import SimplicialLayerNorm
from dak.usf.lee_wick import LeeWickRegulator

class USFFeedForward(nn.Module):
    def __init__(self, d_model: int, d_ff: int = USF_FFN_DIM, dropout: float = 0.1):
        super().__init__()
        self.gate = nn.Linear(d_model, d_ff, dtype=USF_DTYPE)
        self.up = nn.Linear(d_model, d_ff, dtype=USF_DTYPE)
        self.down = nn.Linear(d_ff, d_model, dtype=USF_DTYPE)
        self.dropout = nn.Dropout(dropout)
        self.regulator = LeeWickRegulator()

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.gate.weight, gain=1.0 / math.sqrt(2))
        nn.init.xavier_uniform_(self.up.weight, gain=1.0 / math.sqrt(2))
        nn.init.xavier_uniform_(self.down.weight, gain=1.0)
        for m in [self.gate, self.up, self.down]:
            if m.bias is not None:
                nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate = F.silu(self.gate(x))
        up = self.up(x)
        hidden = gate * up
        hidden = self.regulator.regulate_activation(hidden)
        hidden = self.dropout(hidden)
        out = self.down(hidden)
        return self.regulator.regulate_activation(out)


class USFTransformerBlock(nn.Module):
    def __init__(self, d_model: int, n_heads: int, head_dim: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = USFAttention(d_model, n_heads, head_dim, dropout)
        self.ffn = USFFeedForward(d_model, d_ff, dropout)
        self.norm1 = SimplicialLayerNorm(d_model)
        self.norm2 = SimplicialLayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        residual = x
        x = self.norm1(x)
        x = self.attention(x, mask)
        x = self.dropout(x)
        x = residual + x

        residual = x
        x = self.norm2(x)
        x = self.ffn(x)
        x = self.dropout(x)
        x = residual + x

        return x


class RetrocausalHandshake(nn.Module):
    def __init__(self, d_model: int, retro_window: int = RETRO_WINDOW):
        super().__init__()
        self.retro_window = retro_window
        self.future_predictor = nn.Linear(d_model * retro_window, d_model, dtype=USF_DTYPE)
        self.cross_attn = USFAttention(d_model, n_heads=4, head_dim=d_model // 4)
        self.norm = SimplicialLayerNorm(d_model)
        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.future_predictor.weight, gain=0.5)
        if self.future_predictor.bias is not None:
            nn.init.zeros_(self.future_predictor.bias)

    def predict_future(self, hidden: torch.Tensor) -> torch.Tensor:
        batch, seq_len, d = hidden.shape
        if seq_len < self.retro_window:
            pad = self.retro_window - seq_len
            ctx = F.pad(hidden, (0, 0, 0, pad))
        else:
            ctx = hidden[:, -self.retro_window:, :]
        ctx_flat = ctx.reshape(batch, -1)
        future_repr = self.future_predictor(ctx_flat).unsqueeze(1)
        return future_repr

    def forward(self, hidden: torch.Tensor, future_target: torch.Tensor = None) -> tuple:
        future_repr = self.predict_future(hidden)
        batch, seq_len, d = hidden.shape
        future_expanded = future_repr.expand(-1, seq_len, -1)
        future_key = future_expanded
        future_value = future_expanded
        h = hidden.unsqueeze(1)
        bias = self.cross_attn(hidden, mask=None)
        bias = self.norm(bias)
        out = hidden + 0.1 * bias

        loss = 0.0
        if future_target is not None:
            loss = F.mse_loss(future_repr.squeeze(1), future_target)

        return out, loss, future_repr


class USFTransformer(nn.Module):
    def __init__(
        self,
        vocab_size: int = VOCAB_SIZE,
        d_model: int = SIMPLICIAL_DIM,
        n_layers: int = N_USF_LAYERS,
        n_heads: int = USF_N_HEADS,
        head_dim: int = USF_HEAD_DIM,
        d_ff: int = USF_FFN_DIM,
        max_seq_len: int = USF_MAX_SEQ_LEN,
        n_sensors: int = N_SENSORS_SETTING,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.max_seq_len = max_seq_len
        self.n_sensors = n_sensors

        complex = SimplicialComplex()
        for i in range(vocab_size):
            complex.add_vertex(i)
        self.embedding = SimplicialEmbedding(complex, d_model, vocab_size)

        self.pos_encoding = nn.Embedding(max_seq_len, d_model, dtype=USF_DTYPE)
        nn.init.normal_(self.pos_encoding.weight, mean=0.0, std=0.02)

        self.blocks = nn.ModuleList([
            USFTransformerBlock(d_model, n_heads, head_dim, d_ff, dropout)
            for _ in range(n_layers)
        ])

        self.lm_head = nn.Linear(d_model, vocab_size, bias=False, dtype=USF_DTYPE)
        self.sensor_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2, dtype=USF_DTYPE),
            nn.GELU(),
            nn.Linear(d_model // 2, n_sensors, dtype=USF_DTYPE),
        )
        self.retro_handshake = RetrocausalHandshake(d_model)

        self.norm_final = SimplicialLayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        self.regulator = LeeWickRegulator()

        self._init_weights()

    def _init_weights(self):
        nn.init.xavier_uniform_(self.lm_head.weight, gain=0.02)
        for layer in self.sensor_head:
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight, gain=0.5)
                if layer.bias is not None:
                    nn.init.zeros_(layer.bias)

    def _create_causal_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        mask = torch.triu(
            torch.full((seq_len, seq_len), float('-inf'), device=device),
            diagonal=1,
        )
        return mask

    def forward(
        self,
        input_ids: torch.Tensor,
        sensor_values: torch.Tensor = None,
        labels: torch.Tensor = None,
        return_loss: bool = False,
        return_hidden: bool = False,
    ) -> dict:
        batch, seq_len = input_ids.shape
        device = input_ids.device

        x = self.embedding(input_ids)
        positions = torch.arange(seq_len, device=device).unsqueeze(0)
        x = x + self.pos_encoding(positions)
        x = self.dropout(x)

        mask = self._create_causal_mask(seq_len, device)

        for block in self.blocks:
            x = block(x, mask)

        x = self.norm_final(x)
        hidden = x

        retro_out, retro_loss, future_repr = self.retro_handshake(hidden)

        logits = self.lm_head(retro_out)

        result = {
            'logits': logits,
            'hidden': hidden,
            'future_repr': future_repr,
        }

        if sensor_values is not None:
            sensor_pred = self.sensor_head(hidden[:, -1, :])
            result['sensor_pred'] = sensor_pred

        if return_loss:
            loss_total = 0.0
            losses = {}

            if labels is not None:
                loss_lm = F.cross_entropy(
                    logits.view(-1, logits.size(-1)),
                    labels.view(-1),
                    ignore_index=-100,
                )
                losses['lm'] = loss_lm * LM_LOSS_SCALE
                loss_total = loss_total + losses['lm']

            if sensor_values is not None and 'sensor_pred' in result:
                loss_sensor = F.mse_loss(result['sensor_pred'], sensor_values)
                losses['sensor'] = loss_sensor * SENSOR_LOSS_SCALE
                loss_total = loss_total + losses['sensor']

            losses['retro'] = retro_loss * RETRO_LOSS_SCALE
            loss_total = loss_total + losses['retro']

            param_norm_sq = sum(p.norm() ** 2 for p in self.parameters())
            loss_complexity = param_norm_sq / (2.0 * SIGMA2_USF_PRIOR * batch)
            losses['complexity'] = loss_complexity
            loss_total = loss_total + loss_complexity

            result['loss'] = loss_total
            result['losses'] = losses

        if return_hidden:
            result['hidden'] = hidden

        return result

    def predict_next_token(self, input_ids: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        self.eval()
        with torch.no_grad():
            out = self.forward(input_ids)
            logits = out['logits'][:, -1, :]
            logits = logits / temperature
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
        return next_token

    def predict_sensors(self, input_ids: torch.Tensor) -> torch.Tensor:
        self.eval()
        with torch.no_grad():
            out = self.forward(input_ids)
            return out.get('sensor_pred')

    def generate(self, input_ids: torch.Tensor, max_new_tokens: int = 64, temperature: float = 1.0) -> torch.Tensor:
        self.eval()
        for _ in range(max_new_tokens):
            if input_ids.size(1) > self.max_seq_len:
                input_ids = input_ids[:, -self.max_seq_len:]
            next_token = self.predict_next_token(input_ids, temperature)
            input_ids = torch.cat([input_ids, next_token], dim=1)
        return input_ids

    def extract_mu(self, hidden: torch.Tensor) -> torch.Tensor:
        mu = hidden.mean(dim=1)
        return mu

    def get_param_norm(self) -> float:
        return sum(p.norm().item() for p in self.parameters())
