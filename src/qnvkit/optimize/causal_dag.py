"""
qnvkit.optimize.causal_dag: wire-adjacency engine behind every pair rewrite.

A circuit is a list of operations, but list order is not what matters physically: ``X q0``,
``H q1``, ``X q0`` has the two X gates next to each other on wire q0 even though H sits
between them in the list. The tracker therefore keeps, for every qubit wire, the ordered list
of operations touching it. Two operations are *strictly adjacent* when, on every wire they
act on, the second is the very next operation after the first.

Anything on a shared wire in between (another gate, a barrier, a measurement, a reset)
breaks adjacency, and classically conditioned operations are never paired. That is what
makes the rewrites in ``passes.py`` safe.
"""

from typing import Callable, Dict, List, Set, Tuple
from qnvkit.ir import CircuitIR, Op

NON_UNITARY = ("barrier", "measure", "reset")


class CausalWireTracker:
    """Per-wire timeline of a circuit, built once in O(number of operations)."""

    def __init__(self, ir: CircuitIR):
        self.ir = ir
        self.num_qubits = ir.num_qubits
        self.ops = list(ir.ops)

        # wire -> indices (into self.ops) of the operations on that wire, in circuit order
        self.wire_trace: Dict[int, List[int]] = {q: [] for q in range(self.num_qubits)}
        # (wire, op index) -> position of that operation within wire_trace[wire]
        self.pos_in_wire: Dict[Tuple[int, int], int] = {}

        for idx, op in enumerate(self.ops):
            for q in op.qubits:
                if q < self.num_qubits:
                    self.pos_in_wire[(q, idx)] = len(self.wire_trace[q])
                    self.wire_trace[q].append(idx)

    def are_strictly_adjacent(self, idx_a: int, idx_b: int) -> bool:
        """
        True when ops ``idx_a`` and ``idx_b`` (a before b) are unconditioned unitary gates on
        the same set of qubits with nothing between them on any of those wires.
        """
        if idx_a >= idx_b or idx_a < 0 or idx_b >= len(self.ops):
            return False
        op_a, op_b = self.ops[idx_a], self.ops[idx_b]

        if set(op_a.qubits) != set(op_b.qubits):
            return False
        if op_a.condition is not None or op_b.condition is not None:
            return False
        if op_a.name in NON_UNITARY or op_b.name in NON_UNITARY:
            return False

        for q in op_a.qubits:
            pos_a = self.pos_in_wire.get((q, idx_a))
            pos_b = self.pos_in_wire.get((q, idx_b))
            if pos_a is None or pos_b is None or pos_a + 1 != pos_b:
                return False  # something else touches wire q in between
        return True

    def find_all_adjacent_pairs(self, match_fn: Callable[[Op, Op], bool]) -> List[Tuple[int, int]]:
        """
        Disjoint pairs ``(i, j)`` of strictly adjacent operations with ``match_fn(op_i, op_j)``.
        Each operation appears in at most one pair, so ``G G G`` yields one pair and keeps one G.
        """
        matched: Set[int] = set()
        pairs: List[Tuple[int, int]] = []

        for i, op_a in enumerate(self.ops):
            if i in matched or not op_a.qubits or op_a.name in NON_UNITARY or op_a.condition:
                continue

            # The only candidate partner is the next operation on any one of op_a's wires.
            wire = op_a.qubits[0]
            pos = self.pos_in_wire.get((wire, i))
            if pos is None or pos + 1 >= len(self.wire_trace[wire]):
                continue
            j = self.wire_trace[wire][pos + 1]
            if j in matched:
                continue

            if self.are_strictly_adjacent(i, j) and match_fn(op_a, self.ops[j]):
                pairs.append((i, j))
                matched.update((i, j))

        return pairs
