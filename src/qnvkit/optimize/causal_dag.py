"""
qnvkit.optimize.causal_dag: Causal wire adjacency engine and barrier collision tracker.
Guarantees that two gates are considered adjacent if and only if no intervening operation
(barrier, measurement, reset, conditional, or non-commuting gate) touches their wires.
"""

from typing import List, Dict, Set, Tuple, Optional, Callable
from qnvkit.ir import CircuitIR, Op


class CausalWireTracker:
    """
    Maintains an ordered timeline of operations per qubit wire to perform
    provably safe adjacency checks in O(N) time.
    """
    def __init__(self, ir: CircuitIR):
        self.ir = ir
        self.num_qubits = ir.num_qubits
        self.ops = list(ir.ops)
        
        # Build wire trace: wire index -> list of op indices
        self.wire_trace: Dict[int, List[int]] = {q: [] for q in range(self.num_qubits)}
        # Lookup table: (wire, op_index) -> position in wire_trace[wire]
        self.pos_in_wire: Dict[Tuple[int, int], int] = {}
        
        for idx, op in enumerate(self.ops):
            for q in op.qubits:
                if q < self.num_qubits:
                    pos = len(self.wire_trace[q])
                    self.wire_trace[q].append(idx)
                    self.pos_in_wire[(q, idx)] = pos

    def are_strictly_adjacent(self, idx_a: int, idx_b: int) -> bool:
        """
        Returns True if op at idx_a and op at idx_b are strictly adjacent on all shared wires,
        with NO intervening operations (barriers, measurements, resets, or gates) between them.
        """
        if idx_a >= idx_b or idx_a < 0 or idx_b >= len(self.ops):
            return False

        op_a = self.ops[idx_a]
        op_b = self.ops[idx_b]

        # Must touch the exact same set of qubits
        if set(op_a.qubits) != set(op_b.qubits):
            return False

        # If either operation is classically conditioned, do not rewrite
        if op_a.condition is not None or op_b.condition is not None:
            return False

        # Non-unitary operations are never cancellation candidates
        if op_a.name in ("barrier", "measure", "reset") or op_b.name in ("barrier", "measure", "reset"):
            return False

        # Verify no intervening operation on ANY of the shared wires
        for q in op_a.qubits:
            pos_a = self.pos_in_wire.get((q, idx_a))
            pos_b = self.pos_in_wire.get((q, idx_b))
            if pos_a is None or pos_b is None:
                return False
            # If pos_b is not immediately after pos_a, there is an intervening op on wire q!
            if pos_a + 1 != pos_b:
                return False

        return True

    def find_all_adjacent_pairs(
        self,
        match_fn: Callable[[Op, Op], bool]
    ) -> List[Tuple[int, int]]:
        """
        Finds disjoint pairs of operation indices (i, j) that are strictly adjacent
        and satisfy match_fn(op_i, op_j).
        """
        matched_indices: Set[int] = set()
        pairs: List[Tuple[int, int]] = []

        for i, op_a in enumerate(self.ops):
            if i in matched_indices:
                continue
            if not op_a.qubits or op_a.name in ("barrier", "measure", "reset") or op_a.condition:
                continue

            # Look at the next operation on the primary wire
            primary_wire = op_a.qubits[0]
            pos = self.pos_in_wire.get((primary_wire, i))
            if pos is None or pos + 1 >= len(self.wire_trace[primary_wire]):
                continue

            j = self.wire_trace[primary_wire][pos + 1]
            if j in matched_indices:
                continue

            op_b = self.ops[j]
            if self.are_strictly_adjacent(i, j) and match_fn(op_a, op_b):
                pairs.append((i, j))
                matched_indices.add(i)
                matched_indices.add(j)

        return pairs
