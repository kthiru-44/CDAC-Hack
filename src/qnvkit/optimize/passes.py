"""
qnvkit.optimize.passes: Modular, pure rewrite passes for quantum circuit optimization.
Every pass returns a new CircuitIR and an integer count of eliminated/reduced gates.
"""

from typing import Tuple, List, Dict, Callable, Optional, Set
import numpy as np
from qnvkit.ir import CircuitIR, Op
from qnvkit.optimize.causal_dag import CausalWireTracker


def _is_zero_mod_2pi(angle: float, atol: float = 1e-7) -> bool:
    """Returns True if angle is congruent to 0 mod 2*pi."""
    rem = abs(angle) % (2.0 * np.pi)
    return rem < atol or abs(rem - 2.0 * np.pi) < atol


# ==============================================================================
# Mandatory Passes
# ==============================================================================

def remove_identity(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Pass 1: Eliminates explicit identity gates ('id', 'i') and trivial rotations
    with parameter theta congruent to 0 mod 2*pi.
    """
    new_ops: List[Op] = []
    removed_count = 0

    for op in ir.ops:
        # Check explicit identity
        if op.name in ("id", "i"):
            removed_count += 1
            continue

        # Check trivial rotation gates
        if op.name in ("rx", "ry", "rz", "p", "u1") and op.params:
            if _is_zero_mod_2pi(op.params[0]):
                removed_count += 1
                continue

        # Check trivial U3(0, 0, 0)
        if op.name == "u3" and len(op.params) == 3:
            if _is_zero_mod_2pi(op.params[0]) and _is_zero_mod_2pi(op.params[1]) and _is_zero_mod_2pi(op.params[2]):
                removed_count += 1
                continue

        new_ops.append(op)

    new_ir = CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(new_ops))
    return new_ir, removed_count


def cancel_self_inverse(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Pass 2: Cancels adjacent identical 1-qubit self-inverse gates (X-X, Y-Y, Z-Z, H-H).
    """
    SELF_INVERSE_1Q = {"x", "y", "z", "h"}

    def _match(op_a: Op, op_b: Op) -> bool:
        return (
            op_a.name in SELF_INVERSE_1Q
            and op_a.name == op_b.name
            and op_a.qubits == op_b.qubits
        )

    tracker = CausalWireTracker(ir)
    pairs = tracker.find_all_adjacent_pairs(_match)

    if not pairs:
        return ir, 0

    indices_to_drop = set()
    for i, j in pairs:
        indices_to_drop.add(i)
        indices_to_drop.add(j)

    new_ops = [op for idx, op in enumerate(ir.ops) if idx not in indices_to_drop]
    new_ir = CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(new_ops))
    return new_ir, len(indices_to_drop)


def cancel_cx(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Pass 3: Cancels adjacent identical CX operations with the exact same control and target.
    """
    def _match(op_a: Op, op_b: Op) -> bool:
        return op_a.name == "cx" and op_b.name == "cx" and op_a.qubits == op_b.qubits

    tracker = CausalWireTracker(ir)
    pairs = tracker.find_all_adjacent_pairs(_match)

    if not pairs:
        return ir, 0

    indices_to_drop = set()
    for i, j in pairs:
        indices_to_drop.add(i)
        indices_to_drop.add(j)

    new_ops = [op for idx, op in enumerate(ir.ops) if idx not in indices_to_drop]
    new_ir = CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(new_ops))
    return new_ir, len(indices_to_drop)


# ==============================================================================
# Opt-in Extra Passes
# ==============================================================================

def cancel_extended_self_inverse(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Cancels adjacent multi-qubit self-inverse gates:
    CZ-CZ, SWAP-SWAP, CH-CH, CCX-CCX, CSWAP-CSWAP.
    """
    def _match(op_a: Op, op_b: Op) -> bool:
        if op_a.name != op_b.name:
            return False
        if op_a.name in ("cz", "swap"):
            # Symmetric gates on 2 qubits
            return set(op_a.qubits) == set(op_b.qubits)
        if op_a.name in ("ch", "ccx"):
            return op_a.qubits == op_b.qubits
        if op_a.name == "cswap":
            # Control must match, targets can be in either order
            return op_a.qubits[0] == op_b.qubits[0] and set(op_a.qubits[1:]) == set(op_b.qubits[1:])
        return False

    tracker = CausalWireTracker(ir)
    pairs = tracker.find_all_adjacent_pairs(_match)

    if not pairs:
        return ir, 0

    indices_to_drop = set()
    for i, j in pairs:
        indices_to_drop.add(i)
        indices_to_drop.add(j)

    new_ops = [op for idx, op in enumerate(ir.ops) if idx not in indices_to_drop]
    new_ir = CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(new_ops))
    return new_ir, len(indices_to_drop)


def cancel_inverse_pairs(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Cancels adjacent adjoint pairs:
    S·S† = I, S†·S = I, T·T† = I, T†·T = I, CS·CS† = I, CT·CT† = I.
    """
    INVERSE_PAIRS = {
        ("s", "sdg"), ("sdg", "s"),
        ("t", "tdg"), ("tdg", "t"),
        ("cs", "csdg"), ("csdg", "cs"),
        ("ct", "ctdg"), ("ctdg", "ct"),
    }

    def _match(op_a: Op, op_b: Op) -> bool:
        return (op_a.name, op_b.name) in INVERSE_PAIRS and op_a.qubits == op_b.qubits

    tracker = CausalWireTracker(ir)
    pairs = tracker.find_all_adjacent_pairs(_match)

    if not pairs:
        return ir, 0

    indices_to_drop = set()
    for i, j in pairs:
        indices_to_drop.add(i)
        indices_to_drop.add(j)

    new_ops = [op for idx, op in enumerate(ir.ops) if idx not in indices_to_drop]
    new_ir = CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(new_ops))
    return new_ir, len(indices_to_drop)


def merge_rotations(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Merges adjacent rotations along the same axis on the same wire:
    Rz(a)·Rz(b) -> Rz(a+b), Rx(a)·Rx(b) -> Rx(a+b), Ry(a)·Ry(b) -> Ry(a+b), P(a)·P(b) -> P(a+b).
    If a+b == 0 mod 2pi, removes the gate completely.
    Also merges controlled rotations CRz, CRx, CRy on the same control and target.
    """
    ROTATION_GATES = {"rx", "ry", "rz", "p", "u1", "crx", "cry", "crz", "cp", "cu1"}

    def _match(op_a: Op, op_b: Op) -> bool:
        return (
            op_a.name in ROTATION_GATES
            and op_a.name == op_b.name
            and op_a.qubits == op_b.qubits
            and len(op_a.params) == 1
            and len(op_b.params) == 1
        )

    tracker = CausalWireTracker(ir)
    pairs = tracker.find_all_adjacent_pairs(_match)

    if not pairs:
        return ir, 0

    pair_map = dict(pairs)  # i -> j
    second_indices = set(pair_map.values())
    new_ops: List[Op] = []
    reduced_count = 0

    for idx, op in enumerate(ir.ops):
        if idx in second_indices:
            continue
        if idx in pair_map:
            # Merge with op at pair_map[idx]
            other_op = ir.ops[pair_map[idx]]
            sum_angle = op.params[0] + other_op.params[0]
            if _is_zero_mod_2pi(sum_angle):
                # Completely eliminated! 2 gates become 0
                reduced_count += 2
            else:
                # 2 gates become 1 merged gate
                merged_op = Op(op.name, op.qubits, params=(sum_angle,), condition=op.condition)
                new_ops.append(merged_op)
                reduced_count += 1
        else:
            new_ops.append(op)

    new_ir = CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(new_ops))
    return new_ir, reduced_count


# Master Registry
PASS_REGISTRY: Dict[str, Callable[[CircuitIR], Tuple[CircuitIR, int]]] = {
    "remove_identity": remove_identity,
    "cancel_self_inverse": cancel_self_inverse,
    "cancel_cx": cancel_cx,
    "cancel_extended_self_inverse": cancel_extended_self_inverse,
    "cancel_inverse_pairs": cancel_inverse_pairs,
    "merge_rotations": merge_rotations,
}

MANDATORY_PASSES = ["remove_identity", "cancel_self_inverse", "cancel_cx"]
