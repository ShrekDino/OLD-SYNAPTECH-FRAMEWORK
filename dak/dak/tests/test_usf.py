import torch
import numpy as np
from dak.usf import (
    Simplex, SimplicialComplex, SimplicialEmbedding,
    LeeWickRegulator, SimplicialLayerNorm, USFAttention,
    USFTransformerBlock, RetrocausalHandshake, USFTransformer,
    ScaleInvariantMarkovBlanket, ActiveInferenceOptimizer,
    LAMBDA_CUTOFF, SIMPLICIAL_DIM,
)


def test_simplex_creation():
    s = Simplex((0, 1, 2))
    assert s.dimension == 2
    assert s.vertices == (0, 1, 2)
    assert len(s.faces()) == 3


def test_simplex_boundary():
    s = Simplex((0, 1, 2))
    boundary = s.boundary()
    assert len(boundary) == 3
    signs = [b[1] for b in boundary]
    assert sum(signs) == 1  # (-1)^0 + (-1)^1 + (-1)^2 = 1 - 1 + 1 = 1


def test_simplicial_complex():
    sc = SimplicialComplex()
    sc.add_vertex(0)
    sc.add_vertex(1)
    sc.add_vertex(2)
    sc.add_simplex(Simplex((0, 1, 2)))
    assert sc.total_vertices() == 3
    assert sc.neighbors(0) == {1, 2}
    assert sc.neighbors(1) == {0, 2}


def test_simplicial_embedding():
    sc = SimplicialComplex()
    for i in range(10):
        sc.add_vertex(i)
    emb = SimplicialEmbedding(sc, embedding_dim=16, vocab_size=10)
    ids = torch.randint(0, 10, (2, 8))
    out = emb(ids)
    assert out.shape == (2, 8, 16)
    assert torch.isfinite(out).all()


def test_lee_wick_regulator_small():
    reg = LeeWickRegulator(cutoff=10.0, mass=1.0)
    x = torch.tensor([0.1, 0.5, 1.0, 2.0])
    y = reg(x)
    assert torch.isfinite(y).all()
    assert (y > 0).all()


def test_lee_wick_regulator_bounded():
    reg = LeeWickRegulator(cutoff=10.0, mass=1.0)
    x = torch.tensor([100.0, 1000.0, 1e6, 1e10])
    y = reg(x)
    assert torch.isfinite(y).all()
    assert float(y.max()) < 1.0


def test_lee_wick_regulator_gradient_finite():
    reg = LeeWickRegulator(cutoff=10.0, mass=1.0)
    x = torch.tensor([1e6, 1e10, -1e6, -1e10], requires_grad=True)
    y = reg(x).sum()
    y.backward()
    assert torch.isfinite(x.grad).all()


def test_lee_wick_stability_check():
    reg = LeeWickRegulator()
    x_safe = torch.tensor([0.1, 0.5, 1.0])
    x_wild = torch.tensor([1e10, 1e20, 1e30])
    safe = reg.check_stability(x_safe)
    wild = reg.check_stability(x_wild)
    assert safe['all_finite']
    assert wild['all_finite']


def test_simplicial_layer_norm():
    ln = SimplicialLayerNorm(64)
    x = torch.randn(4, 16, 64)
    y = ln(x)
    assert y.shape == x.shape
    assert torch.isfinite(y).all()
    assert not torch.isnan(y).any()


def test_simplicial_layer_norm_degenerate():
    ln = SimplicialLayerNorm(4)
    x = torch.ones(2, 8, 4) * 1e10
    y = ln(x)
    assert torch.isfinite(y).all(), 'LayerNorm should handle large values'


def test_usf_attention():
    attn = USFAttention(d_model=256, n_heads=4, head_dim=64)
    x = torch.randn(2, 8, 256)
    y = attn(x)
    assert y.shape == (2, 8, 256)
    assert torch.isfinite(y).all()


def test_usf_attention_with_mask():
    attn = USFAttention(d_model=64, n_heads=2, head_dim=32)
    x = torch.randn(1, 16, 64)
    mask = torch.triu(torch.full((16, 16), float('-inf')), diagonal=1)
    y = attn(x, mask=mask)
    assert y.shape == (1, 16, 64)
    assert torch.isfinite(y).all()


def test_usf_attention_extreme_input():
    attn = USFAttention(d_model=64, n_heads=2, head_dim=32)
    x = torch.randn(1, 8, 64) * 1e10
    y = attn(x)
    assert torch.isfinite(y).all(), 'Attention should handle extreme inputs'


def test_transformer_block():
    block = USFTransformerBlock(d_model=128, n_heads=4, head_dim=32, d_ff=512)
    x = torch.randn(2, 8, 128)
    y = block(x)
    assert y.shape == x.shape
    assert torch.isfinite(y).all()


def test_retrocausal_handshake():
    retro = RetrocausalHandshake(d_model=128, retro_window=4)
    x = torch.randn(2, 16, 128)
    out, loss, future = retro(x)
    assert out.shape == x.shape
    assert future.shape == (2, 1, 128)
    assert loss == 0.0


def test_retrocausal_with_target():
    retro = RetrocausalHandshake(d_model=128, retro_window=4)
    x = torch.randn(2, 16, 128)
    target = torch.randn(2, 128)
    out, loss, future = retro(x, future_target=target)
    assert loss > 0


def test_usf_transformer_forward():
    model = USFTransformer(
        vocab_size=500, d_model=128, n_layers=2,
        n_heads=4, head_dim=32, d_ff=256, max_seq_len=32,
        n_sensors=15,
    )
    input_ids = torch.randint(0, 500, (2, 16))
    sensor_vals = torch.randn(2, 15)
    labels = torch.randint(0, 500, (2, 16))
    out = model(input_ids, sensor_values=sensor_vals, labels=labels, return_loss=True)
    assert 'logits' in out
    assert 'hidden' in out
    assert 'sensor_pred' in out
    assert 'loss' in out
    assert out['logits'].shape == (2, 16, 500)
    assert out['hidden'].shape == (2, 16, 128)
    assert out['sensor_pred'].shape == (2, 15)
    assert float(out['loss']) > 0


def test_usf_transformer_generate():
    model = USFTransformer(
        vocab_size=500, d_model=128, n_layers=2,
        n_heads=4, head_dim=32, d_ff=256, max_seq_len=32,
    )
    input_ids = torch.randint(0, 500, (1, 8))
    generated = model.generate(input_ids, max_new_tokens=16, temperature=1.0)
    assert generated.shape == (1, 24)
    assert torch.isfinite(generated).all()


def test_usf_transformer_mu_extraction():
    model = USFTransformer(
        vocab_size=500, d_model=128, n_layers=2,
        n_heads=4, head_dim=32, d_ff=256,
    )
    input_ids = torch.randint(0, 500, (2, 16))
    sensor_vals = torch.randn(2, 15)
    out = model(input_ids, sensor_values=sensor_vals, return_loss=False)
    mu = model.extract_mu(out['hidden'])
    assert mu.shape == (2, 128)
    assert torch.isfinite(mu).all()


def test_usf_transformer_no_nan():
    model = USFTransformer(
        vocab_size=500, d_model=128, n_layers=3,
        n_heads=4, head_dim=32, d_ff=256, max_seq_len=64,
    )
    x = torch.randint(0, 500, (1, 32))
    out = model(x)
    for key, val in out.items():
        if isinstance(val, torch.Tensor):
            assert not torch.isnan(val).any(), f'NaN in {key}'
            assert not torch.isinf(val).any(), f'Inf in {key}'


def test_markov_blanket_basic():
    mb = ScaleInvariantMarkovBlanket()
    assert not mb.is_sealed()
    mb.seal()
    assert mb.is_sealed()
    mb.unseal()
    assert not mb.is_sealed()


def test_markov_blanket_entropy_guard():
    mb = ScaleInvariantMarkovBlanket()
    hidden = torch.randn(2, 8, 64)
    filtered = mb.entropy_guard(hidden)
    assert filtered.shape == hidden.shape
    assert torch.isfinite(filtered).all()


def test_markov_blanket_state_dict():
    mb = ScaleInvariantMarkovBlanket()
    mb.update(mu=torch.randn(64))
    mb.update(s={'cpu': 50})
    state = mb.get_state_dict()
    assert state['internal_count'] == 1
    assert state['sensory_count'] == 1


def test_active_inference_optimizer_steps():
    model = USFTransformer(
        vocab_size=100, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    opt = ActiveInferenceOptimizer(model, lr=0.01)
    input_ids = torch.randint(0, 100, (2, 8))
    labels = torch.randint(0, 100, (2, 8))

    vfes = []
    for _ in range(3):
        out = model(input_ids, labels=labels, return_loss=True)
        result = opt.step(out, h_env=10.0)
        vfes.append(float(out['loss']))
    assert vfes[-1] <= vfes[0] * 1.1


def test_szilard_step_rejection():
    model = USFTransformer(
        vocab_size=100, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    opt = ActiveInferenceOptimizer(model, lr=0.01, szilard_reject=True)
    input_ids = torch.randint(0, 100, (2, 8))

    out = model(input_ids, return_loss=True)
    result = opt.step(out, h_env=0.0)
    assert isinstance(result.step_rejected, bool)


def test_usf_transformer_cuda():
    if not torch.cuda.is_available():
        return
    device = torch.device('cuda')
    model = USFTransformer(
        vocab_size=500, d_model=128, n_layers=2,
        n_heads=4, head_dim=32, d_ff=256,
    ).to(device)
    input_ids = torch.randint(0, 500, (2, 16), device=device)
    out = model(input_ids)
    assert torch.isfinite(out['logits']).all()
    mu = model.extract_mu(out['hidden']).detach().cpu().numpy()
    assert mu.shape == (2, 128)
