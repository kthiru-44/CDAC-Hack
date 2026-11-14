"""
qnvkit.qasm.gate_ops: exact rewrites of gate lists for the OpenQASM 3 modifiers
``inv @``, ``pow(k) @``, ``ctrl(n) @`` and ``negctrl(n) @``.

Every function works on a list of ``Op`` and raises ``QASMError`` (without location; the
parser attaches line and column) when no exact rewrite exists in the supported gate set.
"""

from __future__ import annotations
import dataclasses
import math
from typing import List

from qnvkit.ir import Op
from qnvkit.gates import get_gate_def
from qnvkit.qasm.diagnostics import QASMError

# Gates whose single angle is negated by inversion and scaled by a real power.
ANGLE_GATES = {"p", "rx", "ry", "rz", "u1", "cp", "crx", "cry", "crz", "cu1"}

# gate -> same gate with one more control
CONTROLLED = {
    "x": "cx", "cx": "ccx", "ccx": "c3x", "c3x": "c4x", "c4x": "c5x",
    "y": "cy", "z": "cz", "h": "ch", "s": "cs", "t": "ct", "sdg": "csdg", "tdg": "ctdg",
    "p": "cp", "u1": "cu1", "rx": "crx", "ry": "cry", "rz": "crz",
    "u2": "cu2", "u3": "cu3", "swap": "cswap",
}


def inverse_op(op: Op) -> Op:
    n, p = op.name, op.params
    if n == "barrier":
        return op
    if n in ANGLE_GATES:
        return dataclasses.replace(op, params=tuple(-x for x in p))
    if n in ("u3", "cu3"):
        return dataclasses.replace(op, params=(-p[0], -p[2], -p[1]))
    if n == "u2":
        return dataclasses.replace(op, name="u3", params=(-math.pi / 2, -p[1], -p[0]))
    if n == "cu2":
        return dataclasses.replace(op, name="cu3", params=(-math.pi / 2, -p[1], -p[0]))
    if n == "cu":
        return dataclasses.replace(op, params=(-p[0], -p[2], -p[1], -p[3]))
    info = get_gate_def(n)
    if info.is_self_inverse:
        return op
    if info.inverse_name:
        return dataclasses.replace(op, name=info.inverse_name)
    raise QASMError("inv modifier is not supported for gate '%s'" % n)


def inverse_ops(ops: List[Op]) -> List[Op]:
    return [inverse_op(o) for o in reversed(ops)]


def controlled_ops(ops: List[Op], controls: List[int]) -> List[Op]:
    """Adds the given control qubits (prepended to the operands) to every gate."""
    out: List[Op] = []
    for op in ops:
        if op.name == "barrier":
            out.append(op)
            continue
        if op.name == "id":
            continue  # controlled identity is the identity
        cur = op
        for c in reversed(controls):
            nxt = CONTROLLED.get(cur.name)
            if nxt is None:
                raise QASMError("ctrl modifier is not supported for gate '%s' (no controlled form in the gate set)" % op.name)
            cur = dataclasses.replace(cur, name=nxt, qubits=(c,) + tuple(cur.qubits))
        out.append(cur)
    return out


def power_ops(ops: List[Op], k: float) -> List[Op]:
    if abs(k - round(k)) < 1e-12:
        n = int(round(k))
        if n >= 0:
            return list(ops) * n
        return inverse_ops(ops) * (-n)
    # non-integer power: only exact for a single op
    if len(ops) == 1:
        op = ops[0]
        if op.name in ANGLE_GATES:
            return [dataclasses.replace(op, params=(op.params[0] * k,) + tuple(op.params[1:]))]
        special = {("z", 0.5): "s", ("z", 0.25): "t", ("s", 0.5): "t", ("sdg", 0.5): "tdg",
                   ("x", 0.5): "sx", ("x", -0.5): "sxdg", ("z", -0.5): "sdg", ("z", -0.25): "tdg"}
        for (g, e), tgt in special.items():
            if op.name == g and abs(k - e) < 1e-12:
                return [dataclasses.replace(op, name=tgt)]
    raise QASMError("pow(%g) modifier is not supported for this gate (only integer powers, or a "
                    "single rotation/phase gate, can be rewritten exactly)" % k)
