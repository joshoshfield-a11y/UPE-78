"""
UPE-78 Formal Logic Layer
Propositional, predicate, and modal logic with theorem proving
"""

import numpy as np
from typing import List, Dict, Tuple, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import itertools


class Connective(Enum):
    """Logical connectives"""
    AND = "∧"
    OR = "∨"
    NOT = "¬"
    IMPLIES = "→"
    IFF = "↔"
    XOR = "⊕"


class Quantifier(Enum):
    """Logical quantifiers"""
    UNIVERSAL = "∀"
    EXISTENTIAL = "∃"
    UNIQUE = "∃!"


@dataclass
class Formula:
    """Logical formula representation"""
    id: str
    expression: str
    variables: Set[str] = field(default_factory=set)
    is_axiom: bool = False
    is_theorem: bool = False
    proof: List[str] = field(default_factory=list)
    truth_value: Optional[bool] = None

    def __hash__(self):
        return hash(self.id)


class PropositionalLogic:
    """Propositional logic engine with truth table generation"""

    def __init__(self):
        self.formulas: Dict[str, Formula] = {}
        self._truth_cache: Dict[str, np.ndarray] = {}

    def atom(self, name: str) -> str:
        """Create atomic proposition"""
        f = Formula(id=name, expression=name, variables={name})
        self.formulas[name] = f
        return name

    def negate(self, formula_id: str) -> str:
        """¬A"""
        new_id = f"NOT_{formula_id}"
        f = Formula(
            id=new_id,
            expression=f"¬{self.formulas[formula_id].expression}",
            variables=self.formulas[formula_id].variables.copy()
        )
        self.formulas[new_id] = f
        return new_id

    def conjunction(self, a: str, b: str) -> str:
        """A ∧ B"""
        new_id = f"AND_{a}_{b}"
        f = Formula(
            id=new_id,
            expression=f"({self.formulas[a].expression} ∧ {self.formulas[b].expression})",
            variables=self.formulas[a].variables | self.formulas[b].variables
        )
        self.formulas[new_id] = f
        return new_id

    def disjunction(self, a: str, b: str) -> str:
        """A ∨ B"""
        new_id = f"OR_{a}_{b}"
        f = Formula(
            id=new_id,
            expression=f"({self.formulas[a].expression} ∨ {self.formulas[b].expression})",
            variables=self.formulas[a].variables | self.formulas[b].variables
        )
        self.formulas[new_id] = f
        return new_id

    def implication(self, a: str, b: str) -> str:
        """A → B ≡ ¬A ∨ B"""
        new_id = f"IMP_{a}_{b}"
        f = Formula(
            id=new_id,
            expression=f"({self.formulas[a].expression} → {self.formulas[b].expression})",
            variables=self.formulas[a].variables | self.formulas[b].variables
        )
        self.formulas[new_id] = f
        return new_id

    def truth_table(self, formula_id: str) -> Dict[str, np.ndarray]:
        """Generate truth table for formula"""
        if formula_id not in self.formulas:
            raise ValueError(f"Unknown formula: {formula_id}")

        f = self.formulas[formula_id]
        variables = sorted(f.variables)
        n = len(variables)

        if n == 0:
            return {}

        # Generate all assignments
        table = {}
        for i, var in enumerate(variables):
            # Column i of truth table
            col = np.array([(j >> (n - 1 - i)) & 1 for j in range(2**n)])
            table[var] = col

        # Evaluate formula (simplified - assumes formula is built from our operations)
        result = self._evaluate(formula_id, table)
        table[formula_id] = result

        return table

    def _evaluate(self, formula_id: str, assignments: Dict[str, np.ndarray]) -> np.ndarray:
        """Evaluate formula given variable assignments"""
        f = self.formulas[formula_id]

        # Base case: atomic
        if f.id in assignments:
            return assignments[f.id]

        # Handle compound formulas
        if formula_id.startswith("NOT_"):
            inner = formula_id[4:]
            return 1 - self._evaluate(inner, assignments)

        if formula_id.startswith("AND_"):
            parts = formula_id[4:].split("_", 1)
            a, b = parts[0], parts[1]
            return self._evaluate(a, assignments) & self._evaluate(b, assignments)

        if formula_id.startswith("OR_"):
            parts = formula_id[3:].split("_", 1)
            a, b = parts[0], parts[1]
            return self._evaluate(a, assignments) | self._evaluate(b, assignments)

        if formula_id.startswith("IMP_"):
            parts = formula_id[4:].split("_", 1)
            a, b = parts[0], parts[1]
            # A → B = ¬A ∨ B
            return (1 - self._evaluate(a, assignments)) | self._evaluate(b, assignments)

        return np.zeros(2**len(assignments), dtype=int)

    def is_tautology(self, formula_id: str) -> bool:
        """Check if formula is tautology (true in all models)"""
        table = self.truth_table(formula_id)
        if formula_id not in table:
            return False
        return np.all(table[formula_id] == 1)

    def is_contradiction(self, formula_id: str) -> bool:
        """Check if formula is contradiction (false in all models)"""
        table = self.truth_table(formula_id)
        if formula_id not in table:
            return False
        return np.all(table[formula_id] == 0)

    def is_contingent(self, formula_id: str) -> bool:
        """Check if formula is contingent (true in some, false in others)"""
        return not self.is_tautology(formula_id) and not self.is_contradiction(formula_id)

    def entails(self, premises: List[str], conclusion: str) -> bool:
        """Check if premises entail conclusion (semantic entailment)"""
        # Γ ⊨ φ iff Γ ∧ ¬φ is unsatisfiable
        all_vars = set()
        for p in premises + [conclusion]:
            all_vars |= self.formulas[p].variables

        n = len(all_vars)
        var_list = sorted(all_vars)

        # Check all models
        for assignment in itertools.product([0, 1], repeat=n):
            assign_dict = {var: val for var, val in zip(var_list, assignment)}

            # Check if all premises true
            premises_true = all(
                self._evaluate_single(p, assign_dict) for p in premises
            )

            if premises_true:
                # Conclusion must also be true
                if not self._evaluate_single(conclusion, assign_dict):
                    return False

        return True

    def _evaluate_single(self, formula_id: str, assignment: Dict[str, int]) -> bool:
        """Evaluate formula on single assignment"""
        f = self.formulas[formula_id]

        if f.id in assignment:
            return bool(assignment[f.id])

        # Handle compound
        if formula_id.startswith("NOT_"):
            inner = formula_id[4:]
            return not self._evaluate_single(inner, assignment)

        if formula_id.startswith("AND_"):
            parts = formula_id[4:].split("_", 1)
            return self._evaluate_single(parts[0], assignment) and self._evaluate_single(parts[1], assignment)

        if formula_id.startswith("OR_"):
            parts = formula_id[3:].split("_", 1)
            return self._evaluate_single(parts[0], assignment) or self._evaluate_single(parts[1], assignment)

        if formula_id.startswith("IMP_"):
            parts = formula_id[4:].split("_", 1)
            return (not self._evaluate_single(parts[0], assignment)) or self._evaluate_single(parts[1], assignment)

        return False

    def prove(self, premises: List[str], conclusion: str) -> List[str]:
        """
        Attempt natural deduction proof.

        Returns proof steps or empty list if no proof found.
        """
        # Simplified: check if conclusion is syntactically derivable
        proof = []

        # Direct entailment
        if self.entails(premises, conclusion):
            proof = premises + [f"Therefore, {conclusion} (by entailment)"]

        return proof


class ModalLogic:
    """Modal logic with Kripke semantics"""

    def __init__(self, n_worlds: int = 5):
        self.n_worlds = n_worlds
        # Accessibility relation: R[i,j] = 1 if world i can access world j
        self.accessibility = np.random.randint(0, 2, (n_worlds, n_worlds))
        # Ensure reflexivity
        np.fill_diagonal(self.accessibility, 1)

        # Proposition valuations: val[prop][world] = truth value
        self.valuations: Dict[str, np.ndarray] = {}

    def set_valuation(self, proposition: str, values: List[bool]):
        """Set truth values for proposition across worlds"""
        self.valuations[proposition] = np.array(values[:self.n_worlds], dtype=int)

    def necessity(self, proposition: str) -> np.ndarray:
        """
        □φ is true at world w iff φ is true at all worlds accessible from w.
        """
        if proposition not in self.valuations:
            raise ValueError(f"Unknown proposition: {proposition}")

        result = np.zeros(self.n_worlds, dtype=int)

        for w in range(self.n_worlds):
            # Check all accessible worlds
            accessible = self.accessibility[w] == 1
            if np.all(self.valuations[proposition][accessible] == 1):
                result[w] = 1

        return result

    def possibility(self, proposition: str) -> np.ndarray:
        """
        ◇φ is true at world w iff φ is true at some world accessible from w.
        """
        if proposition not in self.valuations:
            raise ValueError(f"Unknown proposition: {proposition}")

        result = np.zeros(self.n_worlds, dtype=int)

        for w in range(self.n_worlds):
            accessible = self.accessibility[w] == 1
            if np.any(self.valuations[proposition][accessible] == 1):
                result[w] = 1

        return result

    def is_valid(self, proposition: str) -> bool:
        """Check if proposition is valid (true in all worlds)"""
        if proposition not in self.valuations:
            return False
        return np.all(self.valuations[proposition] == 1)

    def is_satisfiable(self, proposition: str) -> bool:
        """Check if proposition is satisfiable (true in some world)"""
        if proposition not in self.valuations:
            return False
        return np.any(self.valuations[proposition] == 1)


class FuzzyLogic:
    """Fuzzy logic with continuous truth values in [0, 1]"""

    @staticmethod
    def t_norm(a: float, b: float, method: str = "product") -> float:
        """T-norm (fuzzy AND)"""
        if method == "min":
            return min(a, b)
        elif method == "product":
            return a * b
        elif method == "lukasiewicz":
            return max(0, a + b - 1)
        else:
            return a * b

    @staticmethod
    def t_conorm(a: float, b: float, method: str = "probabilistic") -> float:
        """T-conorm (fuzzy OR)"""
        if method == "max":
            return max(a, b)
        elif method == "probabilistic":
            return a + b - a * b
        elif method == "lukasiewicz":
            return min(1, a + b)
        else:
            return a + b - a * b

    @staticmethod
    def negate(a: float, method: str = "standard") -> float:
        """Fuzzy negation"""
        if method == "standard":
            return 1 - a
        elif method == "godel":
            return 1 if a == 0 else 0
        else:
            return 1 - a

    @staticmethod
    def implication(a: float, b: float, method: str = "lukasiewicz") -> float:
        """Fuzzy implication"""
        if method == "lukasiewicz":
            return min(1, 1 - a + b)
        elif method == "godel":
            return 1 if a <= b else b
        elif method == "product":
            return 1 if a <= b else b / a
        else:
            return min(1, 1 - a + b)


class TheoremProver:
    """Automated theorem prover using resolution"""

    def __init__(self):
        self.clauses: List[Set[str]] = []
        self.literals: Set[str] = set()

    def add_clause(self, literals: List[str]):
        """
        Add clause as set of literals.
        Positive literal: "P"
        Negative literal: "¬P" or "NOT_P"
        """
        clause = set(literals)
        self.clauses.append(clause)
        for lit in clause:
            self.literals.add(lit.replace("¬", "").replace("NOT_", ""))

    def resolve(self, c1: Set[str], c2: Set[str]) -> Optional[Set[str]]:
        """Resolve two clauses"""
        for lit in c1:
            neg = f"¬{lit}" if not lit.startswith("¬") else lit[1:]
            if neg in c2:
                # Found complementary pair
                new_clause = (c1 - {lit}) | (c2 - {neg})
                return new_clause
        return None

    def prove_unsatisfiable(self) -> Tuple[bool, List[Set[str]]]:
        """
        Resolution refutation: prove clause set is unsatisfiable.

        Returns:
            (is_unsatisfiable, proof_steps)
        """
        clauses = [set(c) for c in self.clauses]
        proof = []

        added = True
        while added:
            added = False
            new_clauses = []

            for i in range(len(clauses)):
                for j in range(i + 1, len(clauses)):
                    resolvent = self.resolve(clauses[i], clauses[j])

                    if resolvent is not None:
                        if len(resolvent) == 0:
                            # Empty clause found - contradiction!
                            proof.append(clauses[i])
                            proof.append(clauses[j])
                            proof.append(set())
                            return True, proof

                        if resolvent not in clauses and resolvent not in new_clauses:
                            new_clauses.append(resolvent)
                            proof.append(clauses[i])
                            proof.append(clauses[j])
                            proof.append(resolvent)
                            added = True

            clauses.extend(new_clauses)

        return False, proof

    def prove_by_refutation(self, premises: List[List[str]], 
                           conclusion: List[str]) -> bool:
        """
        Prove conclusion from premises by refutation.

        Add premises and negated conclusion, then check unsatisfiability.
        """
        self.clauses = []

        for p in premises:
            self.add_clause(p)

        # Negate conclusion (De Morgan)
        negated = []
        for lit in conclusion:
            if lit.startswith("¬"):
                negated.append(lit[1:])
            else:
                negated.append(f"¬{lit}")

        self.add_clause(negated)

        is_unsat, _ = self.prove_unsatisfiable()
        return is_unsat
