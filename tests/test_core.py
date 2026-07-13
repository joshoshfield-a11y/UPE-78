"""Tests for UPE-78 core engine"""

import unittest
import numpy as np
from upe78.core import UPE78Engine, TensorAccelerator, TopologyEngine
from upe78.neural import DynamicNeuralNet, LayerConfig
from upe78.quantum import QuantumLayer
from upe78.stochastic import StochasticEngine, ProcessParams
from upe78.ai_control import AgentSwarm, ControlTheory
from upe78.symbolic import SymbolicRegistry


class TestCoreEngine(unittest.TestCase):
    def test_engine_initialization(self):
        engine = UPE78Engine(dimensions=100, topology="lens")
        self.assertEqual(engine.dimensions, 100)
        self.assertIsNotNone(engine._transform)

    def test_acceleration(self):
        engine = UPE78Engine(dimensions=100, topology="lens")
        tensor = np.random.randn(100)
        result = engine.accelerate(tensor, "transform")
        self.assertEqual(len(result), 100)

    def test_efficiency(self):
        engine = UPE78Engine(dimensions=100)
        eff = engine.compute_efficiency(100.0, 80.0)
        self.assertTrue(0 <= eff <= 1)

    def test_metrics(self):
        engine = UPE78Engine(dimensions=100)
        metrics = engine.get_metrics()
        self.assertIn("operations", metrics)
        self.assertIn("uptime", metrics)


class TestNeural(unittest.TestCase):
    def test_forward_pass(self):
        layers = [
            LayerConfig(10, 20, "relu"),
            LayerConfig(20, 5, "tanh")
        ]
        net = DynamicNeuralNet(layers)
        x = np.random.randn(10)
        out = net.forward(x)
        self.assertEqual(len(out), 5)

    def test_architecture_search(self):
        search = ArchitectureSearch(10, 2, population_size=10)
        best = search.evolve(generations=2)
        self.assertTrue(len(best) > 0)


class TestQuantum(unittest.TestCase):
    def test_qubit_state(self):
        from upe78.quantum import QubitState
        q = QubitState(1/np.sqrt(2), 1/np.sqrt(2))
        p0, p1 = q.probability()
        self.assertAlmostEqual(p0, 0.5, places=5)
        self.assertAlmostEqual(p1, 0.5, places=5)

    def test_hadamard(self):
        ql = QuantumLayer(2)
        ql.apply_gate("H", 0)
        self.assertAlmostEqual(abs(ql.state[0]), 1/np.sqrt(2), places=5)


class TestStochastic(unittest.TestCase):
    def test_brownian(self):
        engine = StochasticEngine(seed=42)
        path = engine.brownian_motion(100)
        self.assertEqual(len(path), 100)

    def test_ornstein_uhlenbeck(self):
        engine = StochasticEngine(seed=42)
        params = ProcessParams(mean_reversion=0.1, long_term_mean=5.0, volatility=0.5)
        path = engine.ornstein_uhlenbeck(0.0, params, 100)
        self.assertEqual(len(path), 100)


class TestAIControl(unittest.TestCase):
    def test_swarm_initialization(self):
        swarm = AgentSwarm(n_agents=50, spatial_hashing=True)
        self.assertEqual(len(swarm.agents), 50)

    def test_swarm_update(self):
        swarm = AgentSwarm(n_agents=20)
        swarm.update(dt=0.1)
        metrics = swarm.get_metrics()
        self.assertIn("dispersion", metrics)

    def test_pid(self):
        output = ControlTheory.pid_controller(1.0, 0.5, 0.1)
        self.assertIsInstance(output, float)


class TestSymbolic(unittest.TestCase):
    def test_registry_initialization(self):
        reg = SymbolicRegistry(dimensions=100)
        self.assertEqual(len(reg.operators), 162)

    def test_operator_retrieval(self):
        reg = SymbolicRegistry()
        op = reg.get_operator("ADD")
        self.assertIsNotNone(op)
        self.assertEqual(op.name, "ADD")

    def test_execute(self):
        reg = SymbolicRegistry()
        result = reg.execute("ADD", 5, 3)
        self.assertEqual(result, 8)

    def test_lens_projection(self):
        reg = SymbolicRegistry(dimensions=100)
        vec = np.random.randn(100)
        proj = reg.lens_projection(vec)
        self.assertEqual(len(proj), 100)


if __name__ == "__main__":
    unittest.main()
