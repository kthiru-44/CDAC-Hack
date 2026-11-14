"""
qnvkit.optimize.passes: the rewrite passes of the QC-C3-03 optimizer.

Every pass is a pure function ``CircuitIR -> (new CircuitIR, gates_removed)``. A pass never
changes its input and never adds a gate. ``gates_removed`` is the drop in gate count, so a
merge of two rotations into one counts as 1 and a cancelled pair counts as 2.

All pair rules share one safety rule, enforced by ``CausalWireTracker``: two gates may only be
rewritten when they act on the same qubits and nothing at all (gate, barrier, measurement,
reset) sits between them on any of those wires, and neither is classically conditioned.

To add a pass: write a function with the signature above and register it in ``PASS_REGISTRY``.
"""

from typing import Callable, Dict, List, Tuple
import numpy as np
from qnvkit.ir import CircuitIR, Op
from qnvkit.optimize.causal_dag import CausalWireTracker

PassFn = Callable[[CircuitIR], Tuple[CircuitIR, int]]
MatchFn = Callable[[Op, Op], bool]

TWO_PI = 2.0 * np.pi

# Angle period after which a rotation is the identity (up to a global phase).
# rx/ry/rz(2*pi) = -I, which is only a global phase. Once controlled, that -1 becomes a
# relative phase on the control qubit, so crx/cry/crz are the identity only every 4*pi.
ROTATION_PERIOD: Dict[str, float] = {
    "rx": TWO_PI, "ry": TWO_PI, "rz": TWO_PI, "p": TWO_PI, "u1": TWO_PI,
    "cp": TWO_PI, "cu1": TWO_PI,
    "crx": 2 * TWO_PI, "cry": 2 * TWO_PI, "crz": 2 * TWO_PI,
}

SELF_INVERSE_1Q = {"x", "y", "z", "h"}
INVERSE_PAIRS = {
    ("s", "sdg"), ("sdg", "s"),
    ("t", "tdg"), ("tdg", "t"),
    ("cs", "csdg"), ("csdg", "cs"),
    ("ct", "ctdg"), ("ctdg", "ct"),
}


def _is_multiple_of(angle: float, period: float = TWO_PI, atol: float = 1e-7) -> bool:
    """True when ``angle`` is congruent to 0 modulo ``period``."""
    rem = abs(angle) % period
    return rem < atol or abs(rem - period) < atol


def _with_ops(ir: CircuitIR, ops: List[Op]) -> CircuitIR:
    """A copy of ``ir`` with a new operation list (registers unchanged)."""
    return CircuitIR(ir.num_qubits, ir.num_clbits, ir.qregs, ir.cregs, tuple(ops), ir.name)


def _cancel_adjacent_pairs(ir: CircuitIR, match: MatchFn) -> Tuple[CircuitIR, int]:
    """Removes every strictly adjacent pair of gates for which ``match(first, second)`` holds."""
    pairs = CausalWireTracker(ir).find_all_adjacent_pairs(match)
    if not pairs:
        return ir, 0
    dropped = {index for pair in pairs for index in pair}
    kept = [op for index, op in enumerate(ir.ops) if index not in dropped]
    return _with_ops(ir, kept), len(dropped)


# ==============================================================================
# Mandatory passes
# ==============================================================================

def remove_identity(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Removes gates that do nothing: ``id``, a rotation whose angle is a multiple of its
    period (see ``ROTATION_PERIOD``), and ``u3`` with all three angles multiples of 2*pi.
    """
    def is_identity(op: Op) -> bool:
        if op.name in ("id", "i"):
            return True
        if op.name in ROTATION_PERIOD and len(op.params) == 1:
            return _is_multiple_of(op.params[0], ROTATION_PERIOD[op.name])
        if op.name == "u3" and len(op.params) == 3:
            return all(_is_multiple_of(p) for p in op.params)
        return False

    kept = [op for op in ir.ops if not is_identity(op)]
    return _with_ops(ir, kept), len(ir.ops) - len(kept)


def cancel_self_inverse(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """Cancels adjacent identical one-qubit self-inverse gates: X-X, Y-Y, Z-Z, H-H."""
    def match(a: Op, b: Op) -> bool:
        return a.name in SELF_INVERSE_1Q and a.name == b.name and a.qubits == b.qubits

    return _cancel_adjacent_pairs(ir, match)


def cancel_cx(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """Cancels adjacent CX pairs with the same control and the same target."""
    def match(a: Op, b: Op) -> bool:
        return a.name == "cx" and b.name == "cx" and a.qubits == b.qubits

    return _cancel_adjacent_pairs(ir, match)


# ==============================================================================
# Opt-in extra passes
# ==============================================================================

def cancel_extended_self_inverse(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Cancels adjacent multi-qubit self-inverse pairs: CZ-CZ, SWAP-SWAP, CH-CH, CCX-CCX,
    CSWAP-CSWAP. Operand order is ignored only where the gate is symmetric.
    """
    def match(a: Op, b: Op) -> bool:
        if a.name != b.name:
            return False
        if a.name in ("cz", "swap"):          # symmetric in both qubits
            return set(a.qubits) == set(b.qubits)
        if a.name == "ccx":                   # symmetric in the two controls
            return a.qubits[2] == b.qubits[2] and set(a.qubits[:2]) == set(b.qubits[:2])
        if a.name == "ch":
            return a.qubits == b.qubits
        if a.name == "cswap":                 # symmetric in the two swapped qubits
            return a.qubits[0] == b.qubits[0] and set(a.qubits[1:]) == set(b.qubits[1:])
        return False

    return _cancel_adjacent_pairs(ir, match)


def cancel_inverse_pairs(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """Cancels a gate next to its adjoint: S-Sdg, T-Tdg, CS-CSdg, CT-CTdg (either order)."""
    def match(a: Op, b: Op) -> bool:
        return (a.name, b.name) in INVERSE_PAIRS and a.qubits == b.qubits

    return _cancel_adjacent_pairs(ir, match)


def merge_rotations(ir: CircuitIR) -> Tuple[CircuitIR, int]:
    """
    Merges adjacent rotations about the same axis on the same qubits into one gate:
    ``rz(a) rz(b) -> rz(a+b)``, likewise rx, ry, p, u1 and the controlled crx, cry, crz, cp, cu1.
    When the summed angle is a multiple of the gate's period the pair disappears entirely.
    """
    def match(a: Op, b: Op) -> bool:
        return (a.name in ROTATION_PERIOD and a.name == b.name and a.qubits == b.qubits
                and len(a.params) == 1 and len(b.params) == 1)

    pairs = CausalWireTracker(ir).find_all_adjacent_pairs(match)
    if not pairs:
        return ir, 0

    second_of = dict(pairs)                    # index of the first gate -> index of the second
    absorbed = set(second_of.values())
    new_ops: List[Op] = []
    for index, op in enumerate(ir.ops):
        if index in absorbed:
            continue
        if index in second_of:
            angle = op.params[0] + ir.ops[second_of[index]].params[0]
            if not _is_multiple_of(angle, ROTATION_PERIOD[op.name]):
                new_ops.append(Op(op.name, op.qubits, params=(angle,)))
        else:
            new_ops.append(op)
    return _with_ops(ir, new_ops), len(ir.ops) - len(new_ops)


# Pass name -> function. The order here is the order used by ``optimize(passes="all")``.
PASS_REGISTRY: Dict[str, PassFn] = {
    "remove_identity": remove_identity,
    "cancel_self_inverse": cancel_self_inverse,
    "cancel_cx": cancel_cx,
    "cancel_extended_self_inverse": cancel_extended_self_inverse,
    "cancel_inverse_pairs": cancel_inverse_pairs,
    "merge_rotations": merge_rotations,
}

MANDATORY_PASSES = ["remove_identity", "cancel_self_inverse", "cancel_cx"]
ALL_PASSES = list(PASS_REGISTRY)
