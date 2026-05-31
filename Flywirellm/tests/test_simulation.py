from flywire_lsm.simulation import ReservoirSimulation


class TestReservoirSimulation:
    def test_initialization(self):
        sim = ReservoirSimulation()
        assert sim.hlayer is not None
        assert sim.encoder is not None
        assert sim.readout is not None
        assert sim.latest_accuracy == 0.0

    def test_train_readout_small(self):
        sim = ReservoirSimulation()
        acc = sim.train_readout("Hello there!", num_passes=1)
        assert acc > 0.0

    def test_run_inference(self):
        sim = ReservoirSimulation()
        sim.train_readout("Hello world!", num_passes=1)
        predictions, logits = sim.run_inference("Hello")
        assert len(predictions) == 5
        assert len(logits) == 5
        assert all(isinstance(p, str) for p in predictions)

    def test_generate(self):
        sim = ReservoirSimulation()
        sim.train_readout("Hello world test!", num_passes=1)
        result = sim.generate(seed_text="Hel", max_gen_len=3)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_cumulative_training(self):
        sim = ReservoirSimulation()
        _ = sim.train_readout("First", num_passes=1, cumulative=True)
        acc2 = sim.train_readout("Second", num_passes=1, cumulative=True)
        assert acc2 >= 0

    def test_warm_start_training(self):
        sim = ReservoirSimulation()
        sim.train_readout("First pass", num_passes=1)
        acc2 = sim.train_readout("Second pass with warm start", num_passes=1, warm_start=True)
        assert acc2 >= 0
