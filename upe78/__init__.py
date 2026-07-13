"""
UPE-78: Universal Processing Engine 78
Multi-Agent Acceleration Architecture v10.0

Author: Joshoshfield
License: MIT
"""

__version__ = "10.0.0"
__author__ = "Joshoshfield"

from .core import UPE78Engine, TensorAccelerator, TopologyEngine
from .neural import DynamicNeuralNet, ArchitectureSearch, NeuralController
from .quantum import QuantumLayer, StochasticQuantum, HybridCompute
from .stochastic import StochasticEngine, ProcessModel, MonteCarlo
from .ai_control import AgentSwarm, ControlTheory, Orchestrator
from .symbolic import SymbolicRegistry, OperatorSpace, LensTopology

__all__ = [
    "UPE78Engine",
    "TensorAccelerator",
    "TopologyEngine",
    "DynamicNeuralNet",
    "ArchitectureSearch",
    "NeuralController",
    "QuantumLayer",
    "StochasticQuantum",
    "HybridCompute",
    "StochasticEngine",
    "ProcessModel",
    "MonteCarlo",
    "AgentSwarm",
    "ControlTheory",
    "Orchestrator",
    "SymbolicRegistry",
    "OperatorSpace",
    "LensTopology",
]
