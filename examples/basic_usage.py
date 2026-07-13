"""
UPE-78 Basic Usage Examples
"""

import numpy as np
from upe78 import UPE78Engine, AgentSwarm, SymbolicRegistry
from upe78.neural import DynamicNeuralNet, LayerConfig
from upe78.quantum import QuantumLayer
from upe78.stochastic import StochasticEngine, ProcessParams


def example_1_core_engine():
    """Example 1: Core tensor acceleration"""
    print("=== Example 1: Core Engine ===")
    engine = UPE78Engine(dimensions=936, topology="lens")

    tensor = np.random.randn(936)
    result = engine.accelerate(tensor, "transform")

    print(f"Input shape: {tensor.shape}")
    print(f"Output shape: {result.shape}")
    print(f"Efficiency: {engine.compute_efficiency(100.0, 85.0):.4f}")
    print(f"Metrics: {engine.get_metrics()}")
    print()


def example_2_neural_net():
    """Example 2: Dynamic neural network"""
    print("=== Example 2: Neural Network ===")
    layers = [
        LayerConfig(784, 256, "relu"),
        LayerConfig(256, 128, "relu"),
        LayerConfig(128, 10, "tanh")
    ]

    net = DynamicNeuralNet(layers)
    x = np.random.randn(784)
    output = net.forward(x)

    print(f"Architecture: {net.get_architecture_summary()}")
    print(f"Output shape: {output.shape}")
    print()


def example_3_quantum():
    """Example 3: Quantum computation"""
    print("=== Example 3: Quantum Layer ===")
    ql = QuantumLayer(n_qubits=4)

    # Apply Hadamard to create superposition
    ql.apply_gate("H", 0)
    ql.apply_gate("H", 1)

    # Entangle
    ql.apply_cnot(0, 1)

    # Measure
    result = ql.measure(0)
    print(f"Measurement result: {result}")
    print(f"State entropy: {ql.entropy():.4f}")
    print()


def example_4_stochastic():
    """Example 4: Stochastic processes"""
    print("=== Example 4: Stochastic Engine ===")
    engine = StochasticEngine(seed=42)

    # Ornstein-Uhlenbeck (mean-reverting)
    params = ProcessParams(
        mean_reversion=0.1,
        long_term_mean=10.0,
        volatility=0.5
    )
    path = engine.ornstein_uhlenbeck(5.0, params, n_steps=1000)

    print(f"Final value: {path[-1]:.4f}")
    print(f"Mean: {np.mean(path):.4f}")
    print(f"Std: {np.std(path):.4f}")
    print()


def example_5_swarm():
    """Example 5: Multi-agent swarm"""
    print("=== Example 5: Agent Swarm ===")
    swarm = AgentSwarm(n_agents=100, spatial_hashing=True)

    # Run orchestration
    metrics = swarm.orchestrate(target="discovery", strategy="distributed")

    print(f"Swarm metrics: {metrics}")
    print()


def example_6_symbolic():
    """Example 6: Symbolic registry"""
    print("=== Example 6: Symbolic Registry ===")
    reg = SymbolicRegistry(dimensions=936)

    # Execute operator
    result = reg.execute("ADD", 10, 20)
    print(f"ADD(10, 20) = {result}")

    # Lens projection
    vec = np.random.randn(936)
    proj = reg.lens_projection(vec)
    print(f"Lens projection shape: {proj.shape}")

    # Registry stats
    print(f"Registry stats: {reg.get_registry_stats()}")
    print()


def example_7_hydration():
    """Example 7: Cross-instance hydration"""
    print("=== Example 7: Hydration Protocol ===")
    reg1 = SymbolicRegistry(dimensions=100)

    # Serialize
    state = reg1.dehydrate()
    print(f"Serialized {len(state['operators'])} operators")

    # Restore
    reg2 = SymbolicRegistry(dimensions=100)
    reg2.hydrate(state)
    print(f"Restored {len(reg2.operators)} operators")
    print()


if __name__ == "__main__":
    example_1_core_engine()
    example_2_neural_net()
    example_3_quantum()
    example_4_stochastic()
    example_5_swarm()
    example_6_symbolic()
    example_7_hydration()
    print("All examples completed successfully!")
