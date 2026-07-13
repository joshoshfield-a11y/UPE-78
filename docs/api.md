# UPE-78 API Reference

## Core Engine (`upe78.core`)

### UPE78Engine
Main acceleration engine.

```python
engine = UPE78Engine(dimensions=936, topology="lens", precision="float64")
```

**Methods:**
- `accelerate(tensor, operation="transform")` - Apply topology-aware transformation
- `compute_efficiency(E_in, E_out)` - Thermodynamic efficiency
- `get_metrics()` - Performance metrics

### TensorAccelerator
Static tensor operations.

**Methods:**
- `fast_matmul(a, b)` - Optimized matrix multiplication
- `spectral_decompose(tensor)` - SVD decomposition
- `entropy(tensor)` - Von Neumann entropy

### TopologyEngine
Graph topology management.

**Methods:**
- `shortest_path(source, target)` - Dijkstra path
- `betweenness_centrality()` - Node centrality

## Neural Layer (`upe78.neural`)

### DynamicNeuralNet
Dynamic neural network with architecture search.

```python
layers = [LayerConfig(784, 256, "relu"), LayerConfig(256, 10, "tanh")]
net = DynamicNeuralNet(layers)
output = net.forward(input)
```

### ArchitectureSearch
Evolutionary neural architecture search.

```python
search = ArchitectureSearch(input_dim=784, output_dim=10)
best_arch = search.evolve(generations=20)
```

## Quantum Layer (`upe78.quantum`)

### QuantumLayer
Quantum circuit simulator.

```python
ql = QuantumLayer(n_qubits=8)
ql.apply_gate("H", 0)
ql.apply_cnot(0, 1)
result = ql.measure(0)
```

### HybridCompute
Quantum-classical hybrid engine.

```python
hybrid = HybridCompute(n_qubits=8, classical_dim=936)
hybrid.encode(classical_data)
hybrid.variational_circuit(params)
```

## Stochastic Engine (`upe78.stochastic`)

### StochasticEngine
Process simulator.

**Methods:**
- `brownian_motion(n_steps)` - Standard Brownian motion
- `geometric_brownian(S0, params, n_steps)` - GBM
- `ornstein_uhlenbeck(x0, params, n_steps)` - Mean-reverting
- `jump_diffusion(S0, params, n_steps)` - Jump-diffusion
- `fractional_brownian(n_steps, hurst)` - fBM

### MonteCarlo
Simulation engine.

```python
mc = MonteCarlo(n_paths=10000)
paths = mc.simulate(process_fn, n_steps)
mean, std_err = mc.estimate_expectation(paths, payoff_fn)
```

## AI Control (`upe78.ai_control`)

### AgentSwarm
Multi-agent coordination.

```python
swarm = AgentSwarm(n_agents=200, spatial_hashing=True)
swarm.orchestrate(target="discovery", strategy="distributed")
```

### ControlTheory
Control implementations.

**Methods:**
- `pid_controller(error, integral, derivative, Kp, Ki, Kd)`
- `lqr_gain(A, B, Q, R)`
- `kalman_filter(x, P, z, F, H, Q, R)`

## Symbolic Registry (`upe78.symbolic`)

### SymbolicRegistry
162-operator computation engine.

```python
reg = SymbolicRegistry(dimensions=936)
result = reg.execute("ADD", a, b)
proj = reg.lens_projection(vector)
state = reg.dehydrate()  # Serialize
reg.hydrate(state)         # Restore
```

### OperatorSpace
Algebraic operator manipulation.

**Methods:**
- `commutator(op1, op2, value)` - Compute [A, B]
- `is_commutative(op1, op2, values)` - Test commutativity

### LensTopology
936-Lens topology management.

```python
lens = LensTopology(dimensions=936)
projected = lens.project(vector, n_components=100)
```
