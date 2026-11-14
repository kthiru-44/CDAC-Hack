"""
qnvkit.decompose.euler: Exact Euler synthesis for 1-qubit unitaries into target basis sets.
Supports {rx, ry, rz}, {u3}, {u1, u2, u3}, and exact discrete words for Clifford+T bases.
"""

from typing import Tuple, List, Optional, Set
import numpy as np
from qnvkit.ir import Op
from qnvkit.gates import get_gate_info


def euler_zyz_decompose(U: np.ndarray) -> Tuple[float, float, float]:
    """
    Decomposes an arbitrary 2x2 unitary matrix U into Z-Y-Z Euler angles:
    U = e^(i*alpha) * Rz(beta) * Ry(gamma) * Rz(delta)
    Returns (beta, gamma, delta).
    """
    det = complex(np.linalg.det(U))
    phase = np.sqrt(det)
    U_norm = U / phase

    u00 = U_norm[0, 0]
    u11 = U_norm[1, 1]
    u10 = U_norm[1, 0]
    u01 = U_norm[0, 1]

    cos_half = np.clip(np.abs(u00), 0.0, 1.0)
    gamma = 2.0 * float(np.arccos(cos_half))

    if np.isclose(cos_half, 1.0, atol=1e-7):
        gamma = 0.0
        beta = 0.0
        delta = 2.0 * float(np.angle(u11))
    elif np.isclose(cos_half, 0.0, atol=1e-7):
        gamma = float(np.pi)
        beta = 2.0 * float(np.angle(u10))
        delta = 0.0
    else:
        phi_sum = 2.0 * float(np.angle(u11))
        phi_diff = 2.0 * float(np.angle(u10))
        beta = float((phi_sum + phi_diff) / 2.0)
        delta = float((phi_sum - phi_diff) / 2.0)

    # Normalize angles to [-pi, pi]
    def _norm(angle):
        return (angle + np.pi) % (2.0 * np.pi) - np.pi

    return _norm(beta), _norm(gamma), _norm(delta)


def synthesize_1q_unitary(
    matrix: np.ndarray,
    qubit: int,
    basis: Set[str],
    condition: Optional[Tuple[str, int]] = None
) -> Optional[List[Op]]:
    """
    Synthesizes a 1-qubit unitary matrix into operations using only the gates in basis.
    Returns None if the basis lacks suitable 1-qubit generators.
    """
    beta, gamma, delta = euler_zyz_decompose(matrix)
    ops: List[Op] = []

    # Priority 1: U3 gate directly
    if "u3" in basis:
        ops.append(Op("u3", (qubit,), params=(gamma, beta, delta), condition=condition))
        return ops

    # Priority 2: {rz, ry}
    if "rz" in basis and "ry" in basis:
        if abs(delta) > 1e-7:
            ops.append(Op("rz", (qubit,), params=(delta,), condition=condition))
        if abs(gamma) > 1e-7:
            ops.append(Op("ry", (qubit,), params=(gamma,), condition=condition))
        if abs(beta) > 1e-7:
            ops.append(Op("rz", (qubit,), params=(beta,), condition=condition))
        if not ops:
            # Identity
            if "id" in basis:
                ops.append(Op("id", (qubit,), condition=condition))
            elif "rz" in basis:
                ops.append(Op("rz", (qubit,), params=(0.0,), condition=condition))
        return ops

    # Priority 3: {rx, rz} -> Ry(gamma) = Rz(pi/2) Rx(gamma) Rz(-pi/2)
    if "rx" in basis and "rz" in basis:
        if abs(delta) > 1e-7:
            ops.append(Op("rz", (qubit,), params=(delta,), condition=condition))
        if abs(gamma) > 1e-7:
            ops.append(Op("rz", (qubit,), params=(np.pi / 2,), condition=condition))
            ops.append(Op("rx", (qubit,), params=(gamma,), condition=condition))
            ops.append(Op("rz", (qubit,), params=(-np.pi / 2,), condition=condition))
        if abs(beta) > 1e-7:
            ops.append(Op("rz", (qubit,), params=(beta,), condition=condition))
        if not ops:
            ops.append(Op("rz", (qubit,), params=(0.0,), condition=condition))
        return ops

    # Priority 4: {rx, ry} -> Rz(theta) = Rx(pi/2) Ry(theta) Rx(-pi/2)
    if "rx" in basis and "ry" in basis:
        def _add_rz(angle):
            if abs(angle) > 1e-7:
                ops.append(Op("rx", (qubit,), params=(np.pi / 2,), condition=condition))
                ops.append(Op("ry", (qubit,), params=(angle,), condition=condition))
                ops.append(Op("rx", (qubit,), params=(-np.pi / 2,), condition=condition))

        _add_rz(delta)
        if abs(gamma) > 1e-7:
            ops.append(Op("ry", (qubit,), params=(gamma,), condition=condition))
        _add_rz(beta)
        if not ops:
            ops.append(Op("rx", (qubit,), params=(0.0,), condition=condition))
        return ops

    return None


def decompose_discrete_1q_gate(
    op: Op,
    basis: Set[str]
) -> Optional[List[Op]]:
    """
    Decomposes standard discrete Clifford+T gates into a discrete basis (e.g. {h, t, tdg, s, cx}).
    Returns None if gate cannot be exactly represented in the discrete basis.
    """
    name = op.name
    q = op.qubits[0]
    cond = op.condition

    if name in basis:
        return [op]

    if name == "x":
        if "h" in basis and "z" in basis:
            return [Op("h", (q,), condition=cond), Op("z", (q,), condition=cond), Op("h", (q,), condition=cond)]
    elif name == "y":
        if "s" in basis and "sdg" in basis and "x" in basis:
            return [Op("s", (q,), condition=cond), Op("x", (q,), condition=cond), Op("sdg", (q,), condition=cond)]
    elif name == "z":
        if "s" in basis:
            return [Op("s", (q,), condition=cond), Op("s", (q,), condition=cond)]
    elif name == "s":
        if "t" in basis:
            return [Op("t", (q,), condition=cond), Op("t", (q,), condition=cond)]
    elif name == "sdg":
        if "tdg" in basis:
            return [Op("tdg", (q,), condition=cond), Op("tdg", (q,), condition=cond)]

    return None
