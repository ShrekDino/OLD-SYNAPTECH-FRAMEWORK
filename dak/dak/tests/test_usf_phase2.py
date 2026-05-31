import os
import tempfile

import torch
import numpy as np

from dak.usf.tokenizer import USFTokenizer
from dak.usf.checkpoint import USFCheckpoint
from dak.usf.transformer import USFTransformer


def test_tokenizer_build():
    tok = USFTokenizer()
    assert tok.eos_id is not None
    assert tok.pad_id is not None
    assert tok.vocab_size >= 50000


def test_tokenizer_encode_decode():
    tok = USFTokenizer()
    text = "Hello, how are you today?"
    ids = tok.encode(text)
    assert len(ids) > 0
    decoded = tok.decode(ids)
    assert isinstance(decoded, str)
    assert len(decoded) > 0


def test_tokenizer_batch():
    tok = USFTokenizer()
    texts = ["Hello world", "Test message"]
    batch = tok.encode_batch(texts)
    assert len(batch) == 2
    assert all(len(b) > 0 for b in batch)


def test_tokenizer_save_load():
    tok = USFTokenizer()
    path = tempfile.mktemp()
    os.makedirs(path, exist_ok=True)
    tok.save(path)
    assert os.path.isdir(path)
    assert os.listdir(path)
    tok2 = USFTokenizer(model_path=path)
    assert tok2.vocab_size >= 50000


def test_checkpoint_save_load():
    model = USFTransformer(
        vocab_size=500, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    path = tempfile.mktemp(suffix='.pt')

    ckpt = USFCheckpoint(model, path)
    assert not ckpt.exists()

    ckpt.save(metadata={'tick': 42, 'F': 123.4})
    assert ckpt.exists()

    model2 = USFTransformer(
        vocab_size=500, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    ckpt2 = USFCheckpoint(model2, path)
    meta = ckpt2.load()
    assert meta.get('tick') == 42
    assert meta.get('F') == 123.4

    os.unlink(path)


def test_checkpoint_with_optimizer():
    model = USFTransformer(
        vocab_size=500, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    opt = torch.optim.AdamW(model.parameters(), lr=0.01)

    path = tempfile.mktemp(suffix='.pt')

    ckpt = USFCheckpoint(model, path)
    ckpt.save(optimizer_state=opt.state_dict(), metadata={'tick': 1})
    assert ckpt.exists()

    model2 = USFTransformer(
        vocab_size=500, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    opt2 = torch.optim.AdamW(model2.parameters(), lr=0.01)
    ckpt2 = USFCheckpoint(model2, path)
    ckpt2.load(optimizer=opt2)
    os.unlink(path)


def test_checkpoint_versioned_path():
    model = USFTransformer(
        vocab_size=500, d_model=64, n_layers=1,
        n_heads=2, head_dim=32, d_ff=128,
    )
    ckpt = USFCheckpoint(model, '/tmp/usf_test.pt')
    p = ckpt.get_path_for_tick(1000)
    assert p == '/tmp/usf_test_1000.pt'


def test_dak_usf_chat_method():
    from dak import DAK
    import dak.config.settings as settings
    old = settings.USF_ENABLED
    settings.USF_ENABLED = True
    try:
        dak = DAK(fresh=True)
        if dak.usf_transformer is not None:
            reply = dak.usf_chat("Hello")
            assert isinstance(reply, str)
            assert len(reply) > 0
            assert reply != '[USF not enabled]'
        dak.stop()
        dak.state.cleanup()
    finally:
        settings.USF_ENABLED = old


def test_dak_get_state_dict_with_usf():
    from dak import DAK
    import dak.config.settings as settings
    old = settings.USF_ENABLED
    settings.USF_ENABLED = True
    try:
        dak = DAK(fresh=True)
        state = dak.get_state_dict()
        assert 'usf_enabled' in state
        if dak.usf_transformer is not None:
            assert 'usf_avg_vfe' in state or not dak.usf_optimizer
        dak.stop()
        dak.state.cleanup()
    finally:
        settings.USF_ENABLED = old


def test_dak_usf_disabled_fallback():
    from dak import DAK
    import dak.config.settings as settings
    old = settings.USF_ENABLED
    settings.USF_ENABLED = False
    try:
        dak = DAK(fresh=True)
        assert not dak.usf_enabled
        assert dak.usf_transformer is None
        state = dak.get_state_dict()
        assert state['usf_enabled'] == False
        dak.stop()
        dak.state.cleanup()
    finally:
        settings.USF_ENABLED = old


def test_dak_usf_step():
    from dak import DAK
    import dak.config.settings as settings
    import dak.usf.config as usf_config
    old_enabled = settings.USF_ENABLED
    settings.USF_ENABLED = True
    old_train = usf_config.USF_TRAIN_EVERY_N_STEPS
    try:
        usf_config.USF_TRAIN_EVERY_N_STEPS = 0

        dak = DAK(fresh=True)
        if dak.usf_transformer is not None:
            dak._step()
            assert dak.tick_count >= 0
        dak.stop()
        dak.state.cleanup()
    finally:
        settings.USF_ENABLED = old_enabled
        usf_config.USF_TRAIN_EVERY_N_STEPS = old_train


def test_usf_chat_roundtrip():
    from dak import DAK
    import dak.config.settings as settings
    old = settings.USF_ENABLED
    settings.USF_ENABLED = True
    try:
        import dak.usf.config as usf_config
        usf_config.USF_MAX_GEN_TOKENS = 16

        dak = DAK(fresh=True)
        if dak.usf_transformer is not None and dak.usf_tokenizer is not None:
            reply = dak.usf_chat("What is your name?")
            assert reply != '[USF not enabled]'
            assert '[USF generation error' not in reply
            assert len(reply) > 0
        dak.stop()
        dak.state.cleanup()
    finally:
        settings.USF_ENABLED = old
