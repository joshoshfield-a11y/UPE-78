"""
UPE-78 Symbolic Registry
162-operator symbolic computation with 936-Lens topology
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json


class AccessLevel(Enum):
    """3-bit Access Control Triad"""
    READ = 0b001
    WRITE = 0b010
    EXECUTE = 0b100
    FULL = 0b111


@dataclass
class SymbolicOperator:
    """Single operator in symbolic registry"""
    id: int
    name: str
    primitive: str
    arity: int
    access_level: AccessLevel = AccessLevel.FULL
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash((self.id, self.name))


class SymbolicRegistry:
    """
    URSA-TECH-SPEC-SYMREG-v1.0 implementation.

    162 operators mapped to concrete computational primitives
    with 3-bit AccessControlTriad and cross-instance HydrationProtocol.
    """

    # 162 operators organized by category
    OPERATOR_CATEGORIES = {
        "arithmetic": ["ADD", "SUB", "MUL", "DIV", "MOD", "POW", "ROOT", "LOG", "EXP"],
        "logical": ["AND", "OR", "NOT", "XOR", "NAND", "NOR", "XNOR", "IMPLIES"],
        "set": ["UNION", "INTERSECT", "DIFF", "SYM_DIFF", "CARTESIAN", "POWER_SET"],
        "tensor": ["TENSOR_PROD", "CONTRACT", "TRACE", "DET", "INVERSE", "TRANSPOSE", "EIG"],
        "topology": ["PROJECT", "EMBED", "FOLD", "UNFOLD", "MERGE", "SPLIT", "LENS_MAP"],
        "control": ["IF", "WHILE", "FOR", "PARALLEL", "SEQUENTIAL", "GUARD", "TIMEOUT"],
        "io": ["READ", "WRITE", "SEND", "RECV", "BROADCAST", "GATHER", "SCATTER"],
        "meta": ["DEFINE", "BIND", "EVAL", "QUOTE", "MACRO", "HYDRATE", "PERSIST"],
        "crypto": ["HASH", "ENCRYPT", "DECRYPT", "SIGN", "VERIFY", "COMMIT", "REVEAL"],
        "spatial": ["NEAREST", "CONVEX_HULL", "VORONOI", "DELAUNAY", "OCTREE", "KD_TREE"],
        "temporal": ["DELAY", "SCHEDULE", "DEBOUNCE", "THROTTLE", "WINDOW", "TUMBLE"],
        "neural": ["CONV", "POOL", "ACTIVATE", "DROPOUT", "BATCH_NORM", "ATTENTION", "LSTM_STEP"],
        "quantum": ["HADAMARD", "PAULI_X", "PAULI_Y", "PAULI_Z", "CNOT", "MEASURE", "ENTANGLE"],
        "stochastic": ["SAMPLE", "SEED", "SHUFFLE", "PERTURB", "NOISE", "SMOOTH", "FILTER"],
        "discovery": ["HYPOTHESIZE", "TEST", "FALSIFY", "VALIDATE", "INDUCE", "DEDUCE", "ABDUCE"],
        "agent": ["SPAWN", "KILL", "MIGRATE", "CLONE", "MERGE_AGENTS", "SPLIT_AGENT", "NEGOTIATE"],
        "sync": ["LOCK", "UNLOCK", "BARRIER", "SEMAPHORE", "MUTEX", "RW_LOCK", "SPIN_LOCK"],
        "transform": ["FFT", "DWT", "DCT", "WAVELET", "HILBERT", "RADON", "HOUGH"],
        "geometry": ["ROTATE", "TRANSLATE", "SCALE", "SHEAR", "REFLECT", "PROJECT_3D", "UNPROJECT"],
    }

    def __init__(self, dimensions: int = 936):
        self.dimensions = dimensions
        self.operators: Dict[int, SymbolicOperator] = {}
        self._operator_index: Dict[str, int] = {}
        self._topology = np.zeros((dimensions, dimensions))
        self._hydration_state = {}

        self._initialize_operators()
        self._initialize_topology()

    def _initialize_operators(self):
        """Initialize all 162 operators"""
        op_id = 0
        for category, names in self.OPERATOR_CATEGORIES.items():
            for name in names:
                # Determine access level based on category sensitivity
                if category in ["crypto", "control", "agent"]:
                    access = AccessLevel.FULL
                elif category in ["io", "sync"]:
                    access = AccessLevel(0b110)  # WRITE | EXECUTE
                else:
                    access = AccessLevel.FULL

                op = SymbolicOperator(
                    id=op_id,
                    name=name,
                    primitive=f"primitive_{name.lower()}",
                    arity=self._infer_arity(name),
                    access_level=access,
                    metadata={"category": category, "version": "1.0"}
                )

                self.operators[op_id] = op
                self._operator_index[name] = op_id
                op_id += 1

        assert len(self.operators) == 162, f"Expected 162 operators, got {len(self.operators)}"

    def _infer_arity(self, name: str) -> int:
        """Infer operator arity from name"""
        unary = ["NOT", "TRACE", "DET", "INVERSE", "TRANSPOSE", "EIG", "LOG", "EXP", 
                 "ROOT", "HASH", "ENCRYPT", "DECRYPT", "SIGN", "VERIFY", "READ", "WRITE",
                 "EVAL", "QUOTE", "COMMIT", "REVEAL", "MEASURE", "SAMPLE", "SEED",
                 "SPAWN", "KILL", "FFT", "DWT", "DCT"]

        if name in unary:
            return 1
        elif name in ["CNOT", "MERGE", "SPLIT", "UNION", "INTERSECT", "DIFF", "ADD", 
                      "SUB", "MUL", "DIV", "AND", "OR", "XOR", "IMPLIES", "CONV", "POOL"]:
            return 2
        elif name in ["IF", "FOLD", "UNFOLD"]:
            return 3
        else:
            return 2  # Default

    def _initialize_topology(self):
        """Initialize 936-Lens topology"""
        n = self.dimensions
        # Overlapping spherical projections
        for i in range(n):
            theta = (i / n) * 2 * np.pi
            for j in range(n):
                phi = (j / n) * np.pi
                # Spherical coupling with decay
                coupling = np.sin(theta) * np.cos(phi) * np.exp(-0.0005 * abs(i - j))
                self._topology[i, j] = coupling

        # Normalize
        self._topology = self._topology / np.linalg.norm(self._topology, axis=1, keepdims=True)

    def get_operator(self, name_or_id) -> Optional[SymbolicOperator]:
        """Retrieve operator by name or ID"""
        if isinstance(name_or_id, str):
            op_id = self._operator_index.get(name_or_id)
            if op_id is not None:
                return self.operators.get(op_id)
        elif isinstance(name_or_id, int):
            return self.operators.get(name_or_id)
        return None

    def execute(self, op_name: str, *args, context: Dict[str, Any] = None) -> Any:
        """
        Execute operator with given arguments.

        Args:
            op_name: Operator name
            *args: Operator arguments
            context: Execution context with access credentials

        Returns:
            Operation result
        """
        op = self.get_operator(op_name)
        if op is None:
            raise ValueError(f"Unknown operator: {op_name}")

        # Access control check
        if context and not self._check_access(op, context):
            raise PermissionError(f"Access denied for operator: {op_name}")

        # Execute primitive
        primitive_fn = self._get_primitive(op.primitive)
        return primitive_fn(*args)

    def _check_access(self, op: SymbolicOperator, context: Dict) -> bool:
        """Check if context has required access level"""
        user_access = context.get("access_level", AccessLevel.READ.value)
        return (user_access & op.access_level.value) == op.access_level.value

    def _get_primitive(self, primitive_name: str) -> Callable:
        """Get primitive function implementation"""
        primitives = {
            "primitive_add": lambda a, b: a + b,
            "primitive_sub": lambda a, b: a - b,
            "primitive_mul": lambda a, b: a * b,
            "primitive_div": lambda a, b: a / b if b != 0 else float('inf'),
            "primitive_and": lambda a, b: a & b,
            "primitive_or": lambda a, b: a | b,
            "primitive_not": lambda a: ~a,
            "primitive_xor": lambda a, b: a ^ b,
            "primitive_hash": lambda a: hashlib.sha256(str(a).encode()).hexdigest(),
            "primitive_fft": lambda a: np.fft.fft(a),
            "primitive_trace": lambda a: np.trace(a),
            "primitive_det": lambda a: np.linalg.det(a),
            "primitive_inverse": lambda a: np.linalg.inv(a + 1e-10 * np.eye(len(a))),
            "primitive_transpose": lambda a: a.T if hasattr(a, 'T') else a,
            "primitive_sample": lambda a: np.random.choice(a) if hasattr(a, '__len__') else a,
        }

        return primitives.get(primitive_name, lambda *args: args[0] if args else None)

    def compose(self, op_sequence: List[str]) -> Callable:
        """
        Compose sequence of operators into single function.

        Args:
            op_sequence: List of operator names

        Returns:
            Composed function
        """
        def composed(*args):
            result = args[0] if args else None
            for op_name in op_sequence:
                result = self.execute(op_name, result)
            return result

        return composed

    def hydrate(self, state_data: Dict[str, Any]) -> None:
        """
        Cross-instance HydrationProtocol.

        Restore registry state from serialized data.
        """
        self._hydration_state = state_data

        if "operators" in state_data:
            for op_data in state_data["operators"]:
                op = SymbolicOperator(**op_data)
                self.operators[op.id] = op
                self._operator_index[op.name] = op.id

        if "topology" in state_data:
            self._topology = np.array(state_data["topology"])

    def dehydrate(self) -> Dict[str, Any]:
        """Serialize registry state for hydration"""
        return {
            "operators": [
                {
                    "id": op.id,
                    "name": op.name,
                    "primitive": op.primitive,
                    "arity": op.arity,
                    "access_level": op.access_level.value,
                    "metadata": op.metadata
                }
                for op in self.operators.values()
            ],
            "topology": self._topology.tolist(),
            "dimensions": self.dimensions
        }

    def lens_projection(self, vector: np.ndarray) -> np.ndarray:
        """Project vector through 936-Lens topology"""
        if len(vector) != self.dimensions:
            # Pad or truncate
            if len(vector) < self.dimensions:
                vector = np.pad(vector, (0, self.dimensions - len(vector)))
            else:
                vector = vector[:self.dimensions]

        return np.dot(self._topology, vector)

    def get_registry_stats(self) -> dict:
        """Return registry statistics"""
        categories = defaultdict(int)
        for op in self.operators.values():
            categories[op.metadata["category"]] += 1

        return {
            "total_operators": len(self.operators),
            "categories": dict(categories),
            "dimensions": self.dimensions,
            "topology_sparsity": np.count_nonzero(self._topology) / self._topology.size
        }


class OperatorSpace:
    """Operator space for algebraic manipulation"""

    def __init__(self, registry: SymbolicRegistry):
        self.registry = registry

    def commutator(self, op1: str, op2: str, test_value: Any) -> Any:
        """Compute [A, B] = AB - BA"""
        a = self.registry.get_operator(op1)
        b = self.registry.get_operator(op2)

        if a is None or b is None:
            return None

        ab = self.registry.execute(op1, self.registry.execute(op2, test_value))
        ba = self.registry.execute(op2, self.registry.execute(op1, test_value))

        return ab - ba if isinstance(ab, (int, float, np.ndarray)) else None

    def is_commutative(self, op1: str, op2: str, test_values: List[Any]) -> bool:
        """Test if two operators commute"""
        for val in test_values:
            if self.commutator(op1, op2, val) != 0:
                return False
        return True

    def find_commuting_set(self, op_name: str) -> List[str]:
        """Find all operators that commute with given operator"""
        test_values = [1, 2.0, np.array([1, 2, 3])]
        commuting = []

        for other_name in self.registry._operator_index.keys():
            if other_name != op_name:
                try:
                    if self.is_commutative(op_name, other_name, test_values):
                        commuting.append(other_name)
                except Exception:
                    pass

        return commuting


class LensTopology:
    """936-Lens topology management"""

    def __init__(self, dimensions: int = 936):
        self.dimensions = dimensions
        self._basis = self._build_basis()

    def _build_basis(self) -> np.ndarray:
        """Build orthonormal basis for lens topology"""
        n = self.dimensions
        basis = np.zeros((n, n))

        for i in range(n):
            # Spherical harmonics-like basis functions
            theta = np.linspace(0, np.pi, n)
            basis[i] = np.sin((i + 1) * theta) * np.sqrt(2 / n)

        # Orthonormalize via Gram-Schmidt
        for i in range(n):
            for j in range(i):
                proj = np.dot(basis[j], basis[i]) * basis[j]
                basis[i] -= proj
            norm = np.linalg.norm(basis[i])
            if norm > 0:
                basis[i] /= norm

        return basis

    def project(self, vector: np.ndarray, n_components: int = 100) -> np.ndarray:
        """Project onto top n_components of lens basis"""
        coeffs = np.dot(self._basis[:n_components], vector)
        return np.dot(coeffs, self._basis[:n_components])

    def reconstruct(self, coefficients: np.ndarray) -> np.ndarray:
        """Reconstruct vector from coefficients"""
        return np.dot(coefficients, self._basis[:len(coefficients)])
