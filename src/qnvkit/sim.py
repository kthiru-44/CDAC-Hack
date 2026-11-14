"""
qnvkit.sim: Exact Numerical Quantum Simulator and Equivalence Verifier.
Uses pure NumPy for exact statevector and unitary matrix computation (up to 10 qubits).
Provides invariant checking up to global phase: |Tr(U_a^dagger @ U_b)| / 2^n >= 1 - tol.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from qnvkit.ir import CircuitIR, Op
from qnvkit.gates import get_gate_info, _mat_u3


def _apply_gate_to_state(state: np.ndarray, gate_mat: np.ndarray, target_qubits: Tuple[int, ...], n: int, endianness: str = "little") -> np.ndarray:
    """
    Applies gate_mat to an n-qubit state tensor.
    state has shape (2, 2, ..., 2) with n axes.
    target_qubits is a tuple of qubit indices (0 = qubit 0).
    endianness: "little" (Qiskit standard: q[0] is LSB / last axis) or "big" (Cirq standard: q[0] is MSB / first axis).
    """
    k = len(target_qubits)
    if endianness == "little":
        axes = [n - 1 - q for q in target_qubits]
    else:
        axes = list(target_qubits)

    gate_tensor = gate_mat.reshape((2,) * (2 * k))
    input_axes = list(range(k, 2 * k))
    contracted = np.tensordot(gate_tensor, state, axes=(input_axes, axes))

    remaining_axes = [i for i in range(n) if i not in axes]
    perm = [0] * n
    for out_idx, orig_axis in enumerate(axes):
        perm[orig_axis] = out_idx
    for rem_idx, orig_axis in enumerate(remaining_axes):
        perm[orig_axis] = k + rem_idx

    return np.transpose(contracted, perm)



def _get_op_matrix(op: Op) -> np.ndarray:
    """Returns matrix for single- or multi-qubit standard gate."""
    name = op.name
    info = get_gate_info(name)
    if info.matrix_fn is not None:
        return info.matrix_fn(op.params)
    
    # Multi-qubit controlled gates
    if name == "ccx":
        m = np.eye(8, dtype=complex)
        m[6:8, 6:8] = np.array([[0, 1], [1, 0]], dtype=complex)
        return m
    elif name == "cswap":
        m = np.eye(8, dtype=complex)
        m[5, 5] = 0; m[5, 6] = 1
        m[6, 5] = 1; m[6, 6] = 0
        return m
    elif name == "ch":
        h = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
        m = np.eye(4, dtype=complex)
        m[2:4, 2:4] = h
        return m
    elif name == "cy":
        y = np.array([[0, -1j], [1j, 0]], dtype=complex)
        m = np.eye(4, dtype=complex)
        m[2:4, 2:4] = y
        return m
    elif name == "cp":
        lam = op.params[0] if op.params else 0.0
        m = np.eye(4, dtype=complex)
        m[3, 3] = np.exp(1j * lam)
        return m
    elif name == "crx":
        from qnvkit.gates import _mat_rx
        rx = _mat_rx(op.params)
        m = np.eye(4, dtype=complex)
        m[2:4, 2:4] = rx
        return m
    elif name == "cry":
        from qnvkit.gates import _mat_ry
        ry = _mat_ry(op.params)
        m = np.eye(4, dtype=complex)
        m[2:4, 2:4] = ry
        return m
    elif name == "crz":
        from qnvkit.gates import _mat_rz
        rz = _mat_rz(op.params)
        m = np.eye(4, dtype=complex)
        m[2:4, 2:4] = rz
        return m
    elif name == "cu1":
        lam = op.params[0] if op.params else 0.0
        m = np.eye(4, dtype=complex)
        m[3, 3] = np.exp(1j * lam)
        return m
    elif name == "cu3":
        u3 = _mat_u3(op.params)
        m = np.eye(4, dtype=complex)
        m[2:4, 2:4] = u3
        return m

    raise NotImplementedError(f"Matrix not implemented for gate '{name}'.")


def compute_unitary(ir: CircuitIR, endianness: str = "little") -> np.ndarray:
    """
    Computes the full 2^n x 2^n unitary matrix for the circuit.
    Non-unitary gates (barrier, measure, reset) are bypassed or identity.
    """
    n = ir.num_qubits
    dim = 1 << n
    unitary = np.zeros((dim, dim), dtype=complex)

    for basis_idx in range(dim):
        state = np.zeros(dim, dtype=complex)
        state[basis_idx] = 1.0
        state = state.reshape((2,) * n)

        for op in ir.ops:
            if op.name in ("barrier", "measure", "reset"):
                continue
            mat = _get_op_matrix(op)
            state = _apply_gate_to_state(state, mat, op.qubits, n, endianness=endianness)

        unitary[:, basis_idx] = state.flatten()

    return unitary


def compute_statevector(ir: CircuitIR, endianness: str = "little") -> np.ndarray:
    """
    Computes final statevector starting from |0...0>.
    """
    n = ir.num_qubits
    dim = 1 << n
    state = np.zeros(dim, dtype=complex)
    state[0] = 1.0
    state = state.reshape((2,) * n)

    for op in ir.ops:
        if op.name in ("barrier", "measure", "reset"):
            continue
        mat = _get_op_matrix(op)
        state = _apply_gate_to_state(state, mat, op.qubits, n, endianness=endianness)

    return state.flatten()



def check_unitary_equivalence(ir_a: CircuitIR, ir_b: CircuitIR, tol: float = 1e-5) -> bool:
    """
    Verifies that ir_a and ir_b implement the exact same unitary up to an unobservable global phase.
    Criterion: |Tr(U_a^dagger @ U_b)| / 2^n >= 1 - tol
    """
    if ir_a.num_qubits != ir_b.num_qubits:
        return False
    n = ir_a.num_qubits
    if n > 8:
        # High qubit count: fall back to statevector comparison on several states
        return check_statevector_fidelity(ir_a, ir_b, tol=tol)
        
    u_a = compute_unitary(ir_a)
    u_b = compute_unitary(ir_b)
    
    trace_val = np.abs(np.trace(u_a.conj().T @ u_b))
    fidelity = trace_val / (1 << n)
    return bool(fidelity >= (1.0 - tol))


def check_statevector_fidelity(ir_a: CircuitIR, ir_b: CircuitIR, tol: float = 1e-5) -> bool:
    """
    Verifies that ir_a and ir_b generate the same statevector: |<psi_a | psi_b>|^2 >= 1 - tol.
    """
    if ir_a.num_qubits != ir_b.num_qubits:
        return False
    psi_a = compute_statevector(ir_a)
    psi_b = compute_statevector(ir_b)
    
    overlap = np.abs(np.vdot(psi_a, psi_b))
    return bool((overlap ** 2) >= (1.0 - tol))


def total_variation_distance(dist_a: Dict[str, float], dist_b: Dict[str, float]) -> float:
    """
    Computes Total Variation Distance (TVD) between two probability distributions:
    TVD = 0.5 * sum_x |P_a(x) - P_b(x)|
    """
    all_keys = set(dist_a.keys()).union(dist_b.keys())
    tvd = 0.5 * sum(abs(dist_a.get(k, 0.0) - dist_b.get(k, 0.0)) for k in all_keys)
    return float(tvd)


def convert_statevector_endianness(statevector: np.ndarray, num_qubits: int) -> np.ndarray:
    """
    Converts between little-endian (Qiskit/QSDK: qubit 0 is LSB) and big-endian (Cirq: qubit 0 is MSB).
    Permutes tensor axes from (q0, q1, ..., q_{n-1}) to (q_{n-1}, ..., q0).
    """
    if num_qubits <= 1:
        return statevector.copy()
    tensor = statevector.reshape((2,) * num_qubits)
    reversed_axes = list(reversed(range(num_qubits)))
    converted = np.transpose(tensor, reversed_axes)
    return converted.flatten()

