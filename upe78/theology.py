"""
UPE-78 Theological Coherence Layer
Formal logic of theological propositions with falsification framework
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import itertools


class AxiomStatus(Enum):
    """Status of theological axiom in framework"""
    AXIOM = "axiom"           # Self-evident, no proof needed
    DERIVED = "derived"       # Proven from other axioms
    HYPOTHESIS = "hypothesis" # Awaiting falsification
    FALSIFIED = "falsified"   # Contradicted by evidence
    UNCERTAIN = "uncertain"   # Insufficient information


@dataclass
class TheologicalProposition:
    """Single theological proposition with formal structure"""
    id: str
    statement: str
    domain: str                    # e.g., "ontology", "cosmology", "eschatology"
    status: AxiomStatus
    dependencies: List[str] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)
    evidence_score: float = 0.5    # 0.0 = falsified, 1.0 = confirmed
    formalization: str = ""        # Logical formalization
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.id)


class TheologicalCoherence:
    """
    Formal framework for evaluating theological coherence.

    Models theological systems as directed graphs of propositions
    with consistency checking and falsification procedures.
    """

    def __init__(self):
        self.propositions: Dict[str, TheologicalProposition] = {}
        self._adjacency: Dict[str, Set[str]] = {}
        self._contradiction_map: Dict[str, Set[str]] = {}
        self._coherence_matrix: Optional[np.ndarray] = None

    def add_proposition(self, prop: TheologicalProposition):
        """Add proposition to framework"""
        self.propositions[prop.id] = prop
        self._adjacency[prop.id] = set(prop.dependencies)
        self._contradiction_map[prop.id] = set(prop.contradictions)
        self._coherence_matrix = None  # Invalidate cache

    def add_axiom(self, statement: str, domain: str, 
                  formalization: str = "") -> str:
        """Add new axiom to system"""
        axiom_id = f"AX{len(self.propositions):03d}"
        prop = TheologicalProposition(
            id=axiom_id,
            statement=statement,
            domain=domain,
            status=AxiomStatus.AXIOM,
            formalization=formalization,
            evidence_score=1.0
        )
        self.add_proposition(prop)
        return axiom_id

    def derive(self, statement: str, domain: str, 
               from_axioms: List[str], formalization: str = "") -> str:
        """Derive proposition from existing axioms"""
        # Check if all dependencies exist
        for ax in from_axioms:
            if ax not in self.propositions:
                raise ValueError(f"Unknown axiom: {ax}")

        prop_id = f"DR{len(self.propositions):03d}"
        prop = TheologicalProposition(
            id=prop_id,
            statement=statement,
            domain=domain,
            status=AxiomStatus.DERIVED,
            dependencies=from_axioms,
            formalization=formalization,
            evidence_score=1.0
        )
        self.add_proposition(prop)
        return prop_id

    def hypothesize(self, statement: str, domain: str,
                    formalization: str = "") -> str:
        """Add falsifiable hypothesis"""
        hyp_id = f"HY{len(self.propositions):03d}"
        prop = TheologicalProposition(
            id=hyp_id,
            statement=statement,
            domain=domain,
            status=AxiomStatus.HYPOTHESIS,
            formalization=formalization,
            evidence_score=0.5
        )
        self.add_proposition(prop)
        return hyp_id

    def check_consistency(self) -> Tuple[bool, List[Tuple[str, str]]]:
        """
        Check global consistency of proposition set.

        Returns:
            (is_consistent, list_of_contradictions)
        """
        contradictions = []

        for prop_id, prop in self.propositions.items():
            for contrad_id in prop.contradictions:
                if contrad_id in self.propositions:
                    contradictions.append((prop_id, contrad_id))

        # Check transitive contradictions
        for a, b in itertools.combinations(self.propositions.keys(), 2):
            if self._implies_contradiction(a, b):
                contradictions.append((a, b))

        return len(contradictions) == 0, contradictions

    def _implies_contradiction(self, a: str, b: str) -> bool:
        """Check if a and b are in contradiction via dependency chains"""
        # If a depends on something that contradicts b
        for dep in self._get_all_dependencies(a):
            if b in self._contradiction_map.get(dep, set()):
                return True

        for dep in self._get_all_dependencies(b):
            if a in self._contradiction_map.get(dep, set()):
                return True

        return False

    def _get_all_dependencies(self, prop_id: str, visited: Set[str] = None) -> Set[str]:
        """Get transitive closure of dependencies"""
        if visited is None:
            visited = set()

        if prop_id in visited:
            return visited

        visited.add(prop_id)
        for dep in self._adjacency.get(prop_id, set()):
            self._get_all_dependencies(dep, visited)

        return visited

    def compute_coherence_matrix(self) -> np.ndarray:
        """
        Compute pairwise coherence matrix.

        C[i,j] = 1 if propositions i and j are coherent
        C[i,j] = -1 if they contradict
        C[i,j] = 0 if unrelated
        """
        n = len(self.propositions)
        ids = list(self.propositions.keys())
        id_to_idx = {id_: i for i, id_ in enumerate(ids)}

        matrix = np.zeros((n, n))

        for i, id_i in enumerate(ids):
            for j, id_j in enumerate(ids):
                if i == j:
                    matrix[i, j] = 1.0
                    continue

                prop_i = self.propositions[id_i]
                prop_j = self.propositions[id_j]

                # Direct contradiction
                if id_j in prop_i.contradictions or id_i in prop_j.contradictions:
                    matrix[i, j] = -1.0
                # Shared dependency = positive coherence
                elif self._adjacency[id_i] & self._adjacency[id_j]:
                    matrix[i, j] = 0.5
                # No relation
                else:
                    matrix[i, j] = 0.0

        self._coherence_matrix = matrix
        return matrix

    def falsify(self, prop_id: str, evidence: str):
        """
        Falsify a hypothesis with evidence.

        Updates status and propagates falsification to derived propositions.
        """
        if prop_id not in self.propositions:
            raise ValueError(f"Unknown proposition: {prop_id}")

        prop = self.propositions[prop_id]
        prop.status = AxiomStatus.FALSIFIED
        prop.evidence_score = 0.0
        prop.metadata["falsification_evidence"] = evidence

        # Propagate to derived propositions
        for other_id, other_prop in self.propositions.items():
            if prop_id in other_prop.dependencies:
                other_prop.status = AxiomStatus.UNCERTAIN
                other_prop.evidence_score *= 0.5

    def confirm(self, prop_id: str, evidence: str):
        """Confirm hypothesis with evidence"""
        if prop_id not in self.propositions:
            raise ValueError(f"Unknown proposition: {prop_id}")

        prop = self.propositions[prop_id]
        if prop.status == AxiomStatus.HYPOTHESIS:
            prop.status = AxiomStatus.DERIVED
        prop.evidence_score = min(1.0, prop.evidence_score + 0.1)
        prop.metadata["confirmation_evidence"] = evidence

    def get_system_coherence(self) -> float:
        """Compute overall system coherence score"""
        if not self.propositions:
            return 0.0

        matrix = self.compute_coherence_matrix()
        # Average of upper triangle (excluding diagonal)
        triu = np.triu(matrix, k=1)
        n_pairs = len(self.propositions) * (len(self.propositions) - 1) / 2

        if n_pairs == 0:
            return 1.0

        return np.sum(triu) / n_pairs

    def get_domain_summary(self, domain: str) -> dict:
        """Get summary of propositions in domain"""
        domain_props = [p for p in self.propositions.values() if p.domain == domain]

        return {
            "total": len(domain_props),
            "axioms": sum(1 for p in domain_props if p.status == AxiomStatus.AXIOM),
            "derived": sum(1 for p in domain_props if p.status == AxiomStatus.DERIVED),
            "hypotheses": sum(1 for p in domain_props if p.status == AxiomStatus.HYPOTHESIS),
            "falsified": sum(1 for p in domain_props if p.status == AxiomStatus.FALSIFIED),
            "mean_evidence": np.mean([p.evidence_score for p in domain_props]) if domain_props else 0.0
        }

    def export_formal_system(self) -> dict:
        """Export as formal logical system"""
        return {
            "axioms": [
                {"id": p.id, "statement": p.statement, "formalization": p.formalization}
                for p in self.propositions.values()
                if p.status == AxiomStatus.AXIOM
            ],
            "theorems": [
                {"id": p.id, "statement": p.statement, "proof": p.dependencies}
                for p in self.propositions.values()
                if p.status == AxiomStatus.DERIVED
            ],
            "hypotheses": [
                {"id": p.id, "statement": p.statement, "falsifiability": p.formalization}
                for p in self.propositions.values()
                if p.status == AxiomStatus.HYPOTHESIS
            ],
            "coherence_score": self.get_system_coherence()
        }


class OntologicalArgument:
    """Formal ontological argument framework"""

    @staticmethod
    def modal_argument(possible_worlds: List[Dict]) -> Tuple[bool, float]:
        """
        Modal ontological argument evaluation.

        In a world where existence is a great-making property,
        if a maximally great being exists in some possible world,
        it exists in all possible worlds.

        Args:
            possible_worlds: List of world descriptions with 'greatness' metrics

        Returns:
            (conclusion, confidence)
        """
        if not possible_worlds:
            return False, 0.0

        # Check if any world has maximally great being
        has_maximal = any(w.get("has_maximal_being", False) for w in possible_worlds)

        if has_maximal:
            # If existence is necessary for maximal greatness,
            # and maximal greatness is possible,
            # then it exists in all worlds
            confidence = len([w for w in possible_worlds if w.get("has_maximal_being", False)]) / len(possible_worlds)
            return True, confidence

        return False, 0.0

    @staticmethod
    def cosmological_argument(causal_chain: List[Dict]) -> Tuple[bool, float]:
        """
        Cosmological argument: every contingent thing has a cause.
        Infinite regress is impossible. Therefore, necessary first cause.

        Returns:
            (conclusion, confidence)
        """
        if not causal_chain:
            return False, 0.0

        # Check for infinite regress
        has_infinite_regress = any(c.get("is_infinite", False) for c in causal_chain)

        if has_infinite_regress:
            return False, 0.3  # Infinite regress undermines argument

        # Check for termination
        has_termination = any(c.get("is_necessary", False) for c in causal_chain)

        if has_termination:
            return True, 0.7

        return False, 0.5

    @staticmethod
    def teleological_argument(complexity_score: float, 
                              randomness_score: float) -> Tuple[bool, float]:
        """
        Teleological argument from design.

        High complexity + low randomness implies design.

        Returns:
            (conclusion, confidence)
        """
        if complexity_score > 0.8 and randomness_score < 0.2:
            confidence = complexity_score * (1 - randomness_score)
            return True, confidence

        return False, complexity_score * randomness_score
