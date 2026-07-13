"""
UPE-78 Quantum Layer
Quantum-classical hybrid computation with stochastic elements
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class QubitState:
    """Representation of a qubit state"""
    alpha: complex  # |0> amplitude
    beta: complex   # |1> amplitude

    def __post_init__(self):
        # Normalize
        norm = np.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        self.alpha /= norm
        self.beta /= norm

    def to_vector(self) -> np.ndarray:
        """Convert to state vector"""
        return np.array([self.alpha, self.beta], dtype=complex)

    def probability(self) -> Tuple[float, float]:
        """Return probabilities of |0> and |1>"""
        return abs(self.alpha)**2, abs(self.beta)**2


class QuantumLayer:
    """
    Quantum computation layer for UPE-78.

    Simulates quantum operations using classical matrix math.
    Supports entanglement and superposition modeling.
    """

    # Standard quantum gates
    GATES = {
        "H": np.array([[1, 1], [1, -1]]) / np.sqrt(2),  # Hadamard
        "X": np.array([[0, 1], [1, 0]]),               # Pauli-X
        "Y": np.array([[0, -1j], [1j, 0]]),            # Pauli-Y
        "Z": np.array([[1, 0], [0, -1]]),              # Pauli-Z
        "S": np.array([[1, 0], [0, 1j]]),             # Phase
        "T": np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]]),  # T-gate
    }

    def __init__(self, n_qubits: int = 8):
        self.n_qubits = n_qubits
        self.state_dim = 2 ** n_qubits
        self.state = np.zeros(self.state_dim, dtype=complex)
        self.state[0] = 1.0  # Initialize to |0...0>
        self._operations = []

    def apply_gate(self, gate: str, target: int):
        """Apply single-qubit gate to target qubit"""
        if gate not in self.GATES:
            raise ValueError(f"Unknown gate: {gate}")

        gate_matrix = self.GATES[gate]

        # Build full operator via tensor product
        op = np.eye(1, dtype=complex)
        for i in range(self.n_qubits):
            if i == target:
                op = np.kron(op, gate_matrix)
            else:
                op = np.kron(op, np.eye(2))

        self.state = op @ self.state
        self._operations.append((gate, target))

    def apply_cnot(self, control: int, target: int):
        """Apply CNOT gate"""
        # Build CNOT matrix
        dim = 2 ** self.n_qubits
        cnot = np.eye(dim, dtype=complex)

        for i in range(dim):
            # Check if control bit is set
            if (i >> control) & 1:
                # Flip target bit
                j = i ^ (1 << target)
                cnot[i, i] = 0
                cnot[i, j] = 1

        self.state = cnot @ self.state
        self._operations.append(("CNOT", control, target))

    def measure(self, qubit: int) -> int:
        """Measure a qubit, collapse state"""
        # Calculate probability of |1>
        prob_1 = 0.0
        for i in range(self.state_dim):
            if (i >> qubit) & 1:
                prob_1 += abs(self.state[i])**2

        # Collapse
        result = np.random.random() < prob_1

        # Normalize remaining states
        new_state = np.zeros(self.state_dim, dtype=complex)
        for i in range(self.state_dim):
            if ((i >> qubit) & 1) == int(result):
                new_state[i] = self.state[i]

        norm = np.linalg.norm(new_state)
        if norm > 0:
            self.state = new_state / norm

        return int(result)

    def expectation(self, operator: np.ndarray) -> complex:
        """Compute expectation value of operator"""
        return np.vdot(self.state, operator @ self.state)

    def entropy(self) -> float:
        """Compute von Neumann entropy of state"""
        probs = np.abs(self.state)**2
        probs = probs[probs > 1e-15]
        return -np.sum(probs * np.log2(probs))

    def reset(self):
        """Reset to |0...0>"""
        self.state = np.zeros(self.state_dim, dtype=complex)
        self.state[0] = 1.0
        self._operations = []


class StochasticQuantum:
    """Stochastic quantum process simulator"""

    def __init__(self, n_qubits: int = 8, noise_rate: float = 0.01):
        self.n_qubits = n_qubits
        self.noise_rate = noise_rate
        self.layer = QuantumLayer(n_qubits)

    def apply_with_noise(self, gate: str, target: int):
        """Apply gate with depolarizing noise"""
        self.layer.apply_gate(gate, target)

        # Apply noise
        if np.random.random() < self.noise_rate:
            # Random Pauli error
            error = np.random.choice(["X", "Y", "Z"])
            self.layer.apply_gate(error, target)

    def simulate_circuit(self, operations: List[Tuple], shots: int = 1000) -> dict:
        """Simulate quantum circuit with multiple shots"""
        results = {}

        for _ in range(shots):
            self.layer.reset()

            # Apply operations
            for op in operations:
                if op[0] == "CNOT":
                    self.layer.apply_cnot(op[1], op[2])
                else:
                    self.apply_with_noise(op[0], op[1])

            # Measure all qubits
            outcome = 0
            for q in range(self.n_qubits):
                outcome |= self.layer.measure(q) << q

            results[outcome] = results.get(outcome, 0) + 1

        return results


class HybridCompute:
    """Quantum-classical hybrid computation engine"""

    def __init__(self, n_qubits: int = 8, classical_dim: int = 936):
        self.quantum = QuantumLayer(n_qubits)
        self.classical_dim = classical_dim
        self._cache = {}

    def encode(self, classical_data: np.ndarray) -> None:
        """Encode classical data into quantum state via amplitude encoding"""
        # Normalize and pad/truncate to quantum dimension
        data = classical_data.flatten()
        target_dim = 2 ** self.quantum.n_qubits

        if len(data) > target_dim:
            data = data[:target_dim]
        elif len(data) < target_dim:
            data = np.pad(data, (0, target_dim - len(data)))

        # Normalize to quantum state
        norm = np.linalg.norm(data)
        if norm > 0:
            self.quantum.state = data / norm

    def decode(self) -> np.ndarray:
        """Decode quantum state to classical data"""
        return np.real(self.quantum.state)

    def variational_circuit(self, params: np.ndarray, layers: int = 3):
        """Apply variational quantum circuit"""
        idx = 0
        for l in range(layers):
            # Rotation layer
            for q in range(self.quantum.n_qubits):
                if idx < len(params):
                    # Rx rotation
                    theta = params[idx]
                    rx = np.array([[np.cos(theta/2), -1j*np.sin(theta/2)],
                                   [-1j*np.sin(theta/2), np.cos(theta/2)]])
                    self.quantum.state = self._apply_single(rx, q) @ self.quantum.state
                    idx += 1

            # Entanglement layer
            for q in range(self.quantum.n_qubits - 1):
                self.quantum.apply_cnot(q, q + 1)

    def _apply_single(self, gate: np.ndarray, target: int) -> np.ndarray:
        """Build single-qubit gate matrix"""
        op = np.eye(1, dtype=complex)
        for i in range(self.quantum.n_qubits):
            if i == target:
                op = np.kron(op, gate)
            else:
                op = np.kron(op, np.eye(2))
        return op
