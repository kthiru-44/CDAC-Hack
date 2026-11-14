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


def _z_rotation_gate(basis: Set[str]) -> Optional[str]:
    """Gate available for a Z-axis rotation. p(a) and u1(a) equal rz(a) up to a global phase."""
    for g in ("rz", "p", "u1"):
        if g in basis:
            return g
    return None


def synthesize_1q_unitary(
    matrix: np.ndarray,
    qubit: int,
    basis: Set[str],
    condition: Optional[Tuple[str, int]] = None
) -> Optional[List[Op]]:
    """
    Synthesizes a 1-qubit unitary (up to global phase) using only gates in `basis`.
    The returned list is in circuit (time) order. An identity yields an empty list.
    Returns None if the basis has no continuous 1-qubit rotations that can express it.

    U = Rz(beta) Ry(gamma) Rz(delta)  (matrix product) -> circuit order: Z(delta), Y(gamma), Z(beta)
    """
    beta, gamma, delta = euler_zyz_decompose(matrix)
    eps = 1e-9
    if abs(gamma) < eps:
        # Pure Z rotation: merge both Z angles into one.
        delta = (beta + delta + np.pi) % (2.0 * np.pi) - np.pi
        beta = 0.0

    def op(name, *params):
        return Op(name, (qubit,), params=tuple(float(p) for p in params), condition=condition)

    is_identity = abs(gamma) < eps and abs(delta) < eps
    if is_identity:
        return []

    if "u3" in basis:
        return [op("u3", gamma, beta, delta)]

    zg = _z_rotation_gate(basis)

    def z_rot(angle) -> Optional[List[Op]]:
        if abs(angle) < eps:
            return []
        if zg:
            return [op(zg, angle)]
        if "rx" in basis and "ry" in basis:
            # Rz(a) = Rx(pi/2) Ry(a) Rx(-pi/2) as a matrix product -> time order: Rx(-pi/2), Ry(a), Rx(pi/2)
            return [op("rx", -np.pi / 2), op("ry", angle), op("rx", np.pi / 2)]
        return None

    def y_rot(angle) -> Optional[List[Op]]:
        if abs(angle) < eps:
            return []
        if "ry" in basis:
            return [op("ry", angle)]
        if "rx" in basis and zg:
            # Ry(a) = Rz(pi/2) Rx(a) Rz(-pi/2) as a matrix product -> time order: Rz(-pi/2), Rx(a), Rz(pi/2)
            return [op(zg, -np.pi / 2), op("rx", angle), op(zg, np.pi / 2)]
        return None

    parts = [z_rot(delta), y_rot(gamma), z_rot(beta)]
    if any(part is None for part in parts):
        return None
    return [o for part in parts for o in part]


def decompose_discrete_1q_gate(
    op: Op,
    basis: Set[str]
) -> Optional[List[Op]]:
    """
    Exact rewrites of the fixed 1-qubit gates into simpler fixed gates (for discrete bases such
    as {h, t, cx}). Each rule is exact up to a global phase. The caller expands the result
    further; returns None when no rule exists.
    """
    name = op.name
    q = op.qubits[0]
    cond = op.condition

    def g(n):
        return Op(n, (q,), condition=cond)

    if name == "id":
        return []
    if name in ("p", "u1", "rz") and op.params:
        # A Z rotation by a multiple of pi/4 is exactly a power of T (rz differs only by a global phase).
        k = op.params[0] / (np.pi / 4.0)
        if abs(k - round(k)) < 1e-9:
            words = {0: [], 1: ["t"], 2: ["s"], 3: ["s", "t"], 4: ["z"], 5: ["z", "t"], 6: ["sdg"], 7: ["tdg"]}
            return [g(n) for n in words[int(round(k)) % 8]]
        return None
    if name == "x":
        return [g("h"), g("z"), g("h")]
    if name == "y":
        return [g("z"), g("x")]            # Y = i X Z
    if name == "z":
        return [g("s"), g("s")]
    if name == "s":
        return [g("t"), g("t")]
    if name == "sdg":
        if "tdg" in basis:
            return [g("tdg"), g("tdg")]
        return [g("s"), g("s"), g("s")]    # S^3 = Sdg
    if name == "tdg":
        if "sdg" in basis:
            return [g("sdg"), g("t")]      # Sdg T = Tdg
        return [g("t")] * 7                # T^7 = Tdg
    return None
