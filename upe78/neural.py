"""
UPE-78 Neural Layer
Dynamic neural architecture with topology-aware routing
"""

import numpy as np
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
import random


@dataclass
class LayerConfig:
    """Configuration for neural layer"""
    input_dim: int
    output_dim: int
    activation: str = "relu"
    dropout_rate: float = 0.0
    use_topology: bool = True


class DynamicNeuralNet:
    """
    Dynamic neural network with architecture search capabilities.

    Supports topology-aware routing through UPE-78 engine integration.
    """

    ACTIVATIONS = {
        "relu": lambda x: np.maximum(0, x),
        "sigmoid": lambda x: 1 / (1 + np.exp(-x)),
        "tanh": np.tanh,
        "swish": lambda x: x / (1 + np.exp(-x)),
        "gelu": lambda x: x * 0.5 * (1 + np.tanh(np.sqrt(2/np.pi) * (x + 0.044715 * x**3)))
    }

    def __init__(self, layer_configs: List[LayerConfig], topology_engine=None):
        self.layers = layer_configs
        self.topology_engine = topology_engine
        self.weights = []
        self.biases = []
        self._initialize_weights()
        self._history = []

    def _initialize_weights(self):
        """Initialize weights with Xavier/He initialization"""
        for config in self.layers:
            # He initialization for ReLU, Xavier for others
            if config.activation == "relu":
                scale = np.sqrt(2.0 / config.input_dim)
            else:
                scale = np.sqrt(1.0 / config.input_dim)

            w = np.random.randn(config.output_dim, config.input_dim) * scale
            b = np.zeros(config.output_dim)

            self.weights.append(w)
            self.biases.append(b)

    def forward(self, x: np.ndarray) -> np.ndarray:
        """Forward pass through network"""
        current = x

        for i, config in enumerate(self.layers):
            # Linear transformation
            z = np.dot(self.weights[i], current) + self.biases[i]

            # Activation
            if config.activation in self.ACTIVATIONS:
                z = self.ACTIVATIONS[config.activation](z)

            # Dropout
            if config.dropout_rate > 0 and self.training:
                mask = np.random.binomial(1, 1 - config.dropout_rate, size=z.shape) / (1 - config.dropout_rate)
                z = z * mask

            # Topology routing if enabled
            if config.use_topology and self.topology_engine is not None:
                z = self.topology_engine.accelerate(z, "project")

            current = z

        return current

    @property
    def training(self) -> bool:
        """Check if network is in training mode"""
        return getattr(self, '_training', False)

    def train_mode(self):
        self._training = True

    def eval_mode(self):
        self._training = False

    def backward(self, x: np.ndarray, target: np.ndarray, lr: float = 0.01) -> float:
        """Simple backpropagation with SGD"""
        self.train_mode()

        # Forward pass to cache activations
        activations = [x]
        current = x
        for i, config in enumerate(self.layers):
            z = np.dot(self.weights[i], current) + self.biases[i]
            a = self.ACTIVATIONS.get(config.activation, lambda x: x)(z)
            activations.append(a)
            current = a

        # Backward pass
        output = activations[-1]
        loss = np.mean((output - target) ** 2)

        delta = 2 * (output - target) / target.size

        for i in reversed(range(len(self.layers))):
            # Gradient w.r.t weights
            grad_w = np.outer(delta, activations[i])
            grad_b = delta

            # Update
            self.weights[i] -= lr * grad_w
            self.biases[i] -= lr * grad_b

            # Propagate delta
            if i > 0:
                delta = np.dot(self.weights[i].T, delta)
                # Apply derivative of activation
                if self.layers[i-1].activation == "relu":
                    delta *= (activations[i] > 0).astype(float)

        self._history.append(loss)
        return loss

    def get_architecture_summary(self) -> dict:
        """Return architecture summary"""
        total_params = sum(w.size + b.size for w, b in zip(self.weights, self.biases))
        return {
            "n_layers": len(self.layers),
            "total_params": total_params,
            "layer_dims": [(l.input_dim, l.output_dim) for l in self.layers],
            "activations": [l.activation for l in self.layers]
        }


class ArchitectureSearch:
    """Neural Architecture Search using evolutionary strategies"""

    def __init__(self, input_dim: int, output_dim: int, population_size: int = 50):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.population_size = population_size
        self.population = []

    def _random_architecture(self) -> List[LayerConfig]:
        """Generate random architecture"""
        n_layers = random.randint(2, 8)
        dims = [self.input_dim]

        for _ in range(n_layers - 1):
            dims.append(random.choice([64, 128, 256, 512, 936]))
        dims.append(self.output_dim)

        layers = []
        for i in range(n_layers):
            act = random.choice(["relu", "swish", "gelu", "tanh"])
            layers.append(LayerConfig(dims[i], dims[i+1], activation=act))

        return layers

    def initialize_population(self):
        """Create initial population"""
        self.population = [self._random_architecture() for _ in range(self.population_size)]

    def evaluate_fitness(self, architecture: List[LayerConfig], 
                         eval_fn: Callable) -> float:
        """Evaluate architecture fitness"""
        try:
            net = DynamicNeuralNet(architecture)
            return eval_fn(net)
        except Exception:
            return float('-inf')

    def evolve(self, generations: int = 10, eval_fn: Callable = None) -> List[LayerConfig]:
        """Evolve population over generations"""
        if eval_fn is None:
            eval_fn = lambda net: -net.get_architecture_summary()["total_params"]

        self.initialize_population()

        for gen in range(generations):
            # Evaluate fitness
            fitness = [self.evaluate_fitness(arch, eval_fn) for arch in self.population]

            # Sort by fitness
            sorted_indices = np.argsort(fitness)[::-1]
            self.population = [self.population[i] for i in sorted_indices]

            # Elitism: keep top 20%
            elite_size = self.population_size // 5
            new_population = self.population[:elite_size]

            # Crossover and mutation
            while len(new_population) < self.population_size:
                parent = random.choice(self.population[:elite_size])
                child = self._mutate(parent)
                new_population.append(child)

            self.population = new_population

        # Return best
        fitness = [self.evaluate_fitness(arch, eval_fn) for arch in self.population]
        best_idx = np.argmax(fitness)
        return self.population[best_idx]

    def _mutate(self, architecture: List[LayerConfig]) -> List[LayerConfig]:
        """Mutate architecture"""
        new_arch = [LayerConfig(l.input_dim, l.output_dim, l.activation) 
                    for l in architecture]

        if random.random() < 0.3 and len(new_arch) > 2:
            # Remove random layer
            idx = random.randint(1, len(new_arch) - 2)
            new_arch.pop(idx)
            # Fix dimensions
            for i in range(idx, len(new_arch)):
                if i > 0:
                    new_arch[i].input_dim = new_arch[i-1].output_dim

        if random.random() < 0.3:
            # Change activation
            idx = random.randint(0, len(new_arch) - 1)
            new_arch[idx].activation = random.choice(["relu", "swish", "gelu", "tanh"])

        return new_arch


class NeuralController:
    """Neural network controller for agent systems"""

    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.policy = DynamicNeuralNet([
            LayerConfig(state_dim, hidden_dim, "relu"),
            LayerConfig(hidden_dim, hidden_dim, "relu"),
            LayerConfig(hidden_dim, action_dim, "tanh")
        ])

        self.value = DynamicNeuralNet([
            LayerConfig(state_dim, hidden_dim, "relu"),
            LayerConfig(hidden_dim, hidden_dim, "relu"),
            LayerConfig(hidden_dim, 1, "linear")
        ])

    def select_action(self, state: np.ndarray) -> np.ndarray:
        """Select action given state"""
        self.policy.eval_mode()
        return self.policy.forward(state)

    def evaluate(self, state: np.ndarray) -> float:
        """Evaluate state value"""
        self.value.eval_mode()
        return float(self.value.forward(state)[0])
