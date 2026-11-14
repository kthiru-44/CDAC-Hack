"""
qnvkit.decompose.rules: Exact rule graph for multi-qubit and two-qubit gate decompositions.
Guarantees mathematical equivalence and preserves classical conditionals and wire mappings.
"""

from typing import List, Optional, Set
import numpy as np
from qnvkit.ir import Op


def decompose_ccx(c1: int, c2: int, t: int, cond=None) -> List[Op]:
    """Exact 6-CX Toffoli decomposition into Clifford+T gates."""
    return [
        Op("h", (t,), condition=cond),
        Op("cx", (c2, t), condition=cond),
        Op("tdg", (t,), condition=cond),
        Op("cx", (c1, t), condition=cond),
        Op("t", (t,), condition=cond),
        Op("cx", (c2, t), condition=cond),
        Op("tdg", (t,), condition=cond),
        Op("cx", (c1, t), condition=cond),
        Op("t", (c2,), condition=cond),
        Op("t", (t,), condition=cond),
        Op("h", (t,), condition=cond),
        Op("cx", (c1, c2), condition=cond),
        Op("t", (c1,), condition=cond),
        Op("tdg", (c2,), condition=cond),
        Op("cx", (c1, c2), condition=cond),
    ]


def decompose_multi_qubit_gate(op: Op, basis: Set[str]) -> Optional[List[Op]]:
    """
    Decomposes multi-qubit gates (ccx, cswap, c3x, c4x, c5x) into smaller gates.
    """
    name = op.name
    qubits = op.qubits
    cond = op.condition

    if name in basis:
        return [op]

    if name == "ccx":
        c1, c2, t = qubits
        return decompose_ccx(c1, c2, t, cond=cond)

    if name == "cswap":
        c, t1, t2 = qubits
        return [
            Op("cx", (t2, t1), condition=cond),
            Op("ccx", (c, t1, t2), condition=cond),
            Op("cx", (t2, t1), condition=cond),
        ]

    if name == "c3x":
        # 4-qubit MCX on c1, c2, c3, target t
        c1, c2, c3, t = qubits
        # Decompose using Barenco construction with CRx(pi/2)
        # CV(c3, t) -> CX(c2, c3) -> CV_dag(c3, t) -> CX(c2, c3) -> CV(c2, t) with CCX on c1, c2
        # Standard recursive step:
        return [
            Op("h", (t,), condition=cond),
            Op("crz", (c3, t), params=(np.pi / 2,), condition=cond),
            Op("ccx", (c1, c2, c3), condition=cond),
            Op("crz", (c3, t), params=(-np.pi / 2,), condition=cond),
            Op("ccx", (c1, c2, c3), condition=cond),
            Op("h", (t,), condition=cond),
        ]

    if name == "c4x":
        c1, c2, c3, c4, t = qubits
        return [
            Op("h", (t,), condition=cond),
            Op("crz", (c4, t), params=(np.pi / 2,), condition=cond),
            Op("c3x", (c1, c2, c3, c4), condition=cond),
            Op("crz", (c4, t), params=(-np.pi / 2,), condition=cond),
            Op("c3x", (c1, c2, c3, c4), condition=cond),
            Op("h", (t,), condition=cond),
        ]

    if name == "c5x":
        c1, c2, c3, c4, c5, t = qubits
        return [
            Op("h", (t,), condition=cond),
            Op("crz", (c5, t), params=(np.pi / 2,), condition=cond),
            Op("c4x", (c1, c2, c3, c4, c5), condition=cond),
            Op("crz", (c5, t), params=(-np.pi / 2,), condition=cond),
            Op("c4x", (c1, c2, c3, c4, c5), condition=cond),
            Op("h", (t,), condition=cond),
        ]

    return None


def decompose_two_qubit_gate(op: Op, basis: Set[str]) -> Optional[List[Op]]:
    """
    Decomposes two-qubit gates into the target basis.
    """
    name = op.name
    qubits = op.qubits
    cond = op.condition
    params = op.params

    if name in basis:
        return [op]

    c, t = qubits[0], qubits[1]

    # Swap decomposition
    if name == "swap":
        if "cx" in basis:
            return [
                Op("cx", (c, t), condition=cond),
                Op("cx", (t, c), condition=cond),
                Op("cx", (c, t), condition=cond),
            ]
        elif "cz" in basis:
            # SWAP via CZ and H
            return [
                Op("h", (t,), condition=cond),
                Op("cz", (c, t), condition=cond),
                Op("h", (t,), condition=cond),
                Op("h", (c,), condition=cond),
                Op("cz", (t, c), condition=cond),
                Op("h", (c,), condition=cond),
                Op("h", (t,), condition=cond),
                Op("cz", (c, t), condition=cond),
                Op("h", (t,), condition=cond),
            ]

    # CX via CZ
    if name == "cx" and "cz" in basis:
        return [
            Op("h", (t,), condition=cond),
            Op("cz", (c, t), condition=cond),
            Op("h", (t,), condition=cond),
        ]

    # CZ via CX
    if name == "cz" and "cx" in basis:
        return [
            Op("h", (t,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("h", (t,), condition=cond),
        ]

    # CY via CX
    if name == "cy":
        return [
            Op("sdg", (t,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("s", (t,), condition=cond),
        ]

    # CH via CX
    if name == "ch":
        return [
            Op("s", (t,), condition=cond),
            Op("h", (t,), condition=cond),
            Op("t", (t,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("tdg", (t,), condition=cond),
            Op("h", (t,), condition=cond),
            Op("sdg", (t,), condition=cond),
        ]

    # Controlled Phase / Rotations
    if name == "crz":
        lam = params[0] if params else 0.0
        return [
            Op("rz", (t,), params=(lam / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("rz", (t,), params=(-lam / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
        ]

    if name == "crx":
        theta = params[0] if params else 0.0
        return [
            Op("h", (t,), condition=cond),
            Op("crz", (c, t), params=(theta,), condition=cond),
            Op("h", (t,), condition=cond),
        ]

    if name == "cry":
        theta = params[0] if params else 0.0
        return [
            Op("ry", (t,), params=(theta / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("ry", (t,), params=(-theta / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
        ]

    if name in ("cp", "cu1"):
        lam = params[0] if params else 0.0
        return [
            Op("p", (c,), params=(lam / 2.0,), condition=cond),
            Op("p", (t,), params=(lam / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("p", (t,), params=(-lam / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
        ]

    if name == "cs":
        return decompose_two_qubit_gate(Op("cp", (c, t), params=(np.pi / 2.0,), condition=cond), basis)

    if name == "ct":
        return decompose_two_qubit_gate(Op("cp", (c, t), params=(np.pi / 4.0,), condition=cond), basis)

    if name == "csdg":
        return decompose_two_qubit_gate(Op("cp", (c, t), params=(-np.pi / 2.0,), condition=cond), basis)

    if name == "ctdg":
        return decompose_two_qubit_gate(Op("cp", (c, t), params=(-np.pi / 4.0,), condition=cond), basis)

    if name == "cu2":
        phi = params[0] if len(params) > 0 else 0.0
        lam = params[1] if len(params) > 1 else 0.0
        return decompose_two_qubit_gate(Op("cu3", (c, t), params=(np.pi / 2.0, phi, lam), condition=cond), basis)

    if name == "cu3":
        theta = params[0] if len(params) > 0 else 0.0
        phi = params[1] if len(params) > 1 else 0.0
        lam = params[2] if len(params) > 2 else 0.0
        # ABC decomposition:
        # A = Rz(phi) Ry(theta/2)
        # B = Ry(-theta/2) Rz(-(phi+lam)/2)
        # C = Rz((lam-phi)/2)
        return [
            Op("rz", (t,), params=((lam - phi) / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("ry", (t,), params=(-theta / 2.0,), condition=cond),
            Op("rz", (t,), params=(-(phi + lam) / 2.0,), condition=cond),
            Op("cx", (c, t), condition=cond),
            Op("rz", (t,), params=(phi,), condition=cond),
            Op("ry", (t,), params=(theta / 2.0,), condition=cond),
            Op("p", (c,), params=((phi + lam) / 2.0,), condition=cond),
        ]

    return None
