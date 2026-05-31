import numpy as np
from dak.memory.episodic_buffer import EpisodicBuffer
from dak.memory.episodic_retriever import EpisodicRetriever
from dak.memory.chat_memory import ChatMemory
from dak.memory.core_beliefs import CoreBeliefs


def test_episodic_buffer_record_and_count():
    buf = EpisodicBuffer(persist_dir='/tmp/erebus_test_mem')
    mu = np.random.randn(64).astype(np.float64)
    buf.record(mu=mu, F=100.0, H_env=5.0, S_gen=0.5, szilard_ratio=8.0,
               phase='SAMPLING', tick=1)
    assert buf.count() >= 1


def test_episodic_buffer_query_similar():
    buf = EpisodicBuffer(persist_dir='/tmp/erebus_test_mem')
    mu = np.random.randn(64).astype(np.float64)
    buf.record(mu=mu, F=100.0, H_env=5.0, S_gen=0.5, szilard_ratio=8.0,
               phase='SAMPLING', tick=1)
    results = buf.query_similar(mu, n=3)
    assert isinstance(results, list)


def test_episodic_buffer_no_crash_on_no_data():
    buf = EpisodicBuffer(persist_dir='/tmp/erebus_test_mem')
    assert buf.count() >= 0
    results = buf.query_similar(np.random.randn(64).astype(np.float64))
    assert isinstance(results, list)


def test_episodic_retriever_returns_string():
    buf = EpisodicBuffer(persist_dir='/tmp/erebus_test_mem')
    retriever = EpisodicRetriever(buf)
    context = retriever.retrieve_context(np.random.randn(64).astype(np.float64))
    assert isinstance(context, str)


def test_chat_memory_roundtrip():
    buf = EpisodicBuffer(persist_dir='/tmp/erebus_test_mem')
    cm = ChatMemory(buf)
    state = {'mu': np.zeros(64), 'F': 50.0, 'H_env': 3.0, 'S_gen': 0.1,
             'szilard_ratio': 5.0, 'phase': 'SAMPLING', 'tick_count': 1,
             'delta': 0.01, 'mutual_info': 0.5}
    cm.record_turn('hello', 'hello back', state)
    context = cm.load_recent_context(1)
    assert isinstance(context, list)


def test_core_beliefs_no_crash():
    buf = EpisodicBuffer(persist_dir='/tmp/erebus_test_mem')
    cb = CoreBeliefs(buf)
    beliefs = cb.compress(1000)
    assert isinstance(beliefs, list)
