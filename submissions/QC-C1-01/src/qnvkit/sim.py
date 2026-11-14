"""
qnvkit.sim: Exact Numerical Quantum Simulator and Equivalence Verifier.
Uses pure NumPy for exact statevector and unitary matrix computation (up to 10 qubits).
Provides invariant checking up to global phase: |Tr(U_a^dagger @ U_b)| / 2^n >= 1 - tol.
"""

from typing import Dict, Any, List, Tuple
import numpy as np
from qnvkit.ir import CircuitIR, Condition, Op
from qnvkit.gates import get_gate_info


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


# name -> (number of controls, base 1-qubit gate). Controls come first, the target is last.
_CONTROLLED = {
    "cy": (1, "y"), "ch": (1, "h"), "cs": (1, "s"), "ct": (1, "t"), "csdg": (1, "sdg"), "ctdg": (1, "tdg"),
    "cp": (1, "p"), "cu1": (1, "u1"), "crx": (1, "rx"), "cry": (1, "ry"), "crz": (1, "rz"),
    "cu2": (1, "u2"), "cu3": (1, "u3"),
    "ccx": (2, "x"), "c3x": (3, "x"), "c4x": (4, "x"), "c5x": (5, "x"),
}


def _get_op_matrix(op: Op) -> np.ndarray:
    """Returns the matrix of a gate. The first operand is the most significant index."""
    name = op.name
    info = get_gate_info(name)
    if info.matrix_fn is not None:
        return info.matrix_fn(op.params)

    if name in _CONTROLLED:
        n_ctrl, base = _CONTROLLED[name]
        base_mat = get_gate_info(base).matrix_fn(op.params)
        m = np.eye(2 ** (n_ctrl + 1), dtype=complex)
        m[-2:, -2:] = base_mat
        return m
    if name == "cswap":
        m = np.eye(8, dtype=complex)
        m[5, 5] = 0; m[5, 6] = 1
        m[6, 5] = 1; m[6, 6] = 0
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



# ---------------------------------------------------------------- measurement outcomes
MAX_BRANCHES = 1 << 14


def _condition_holds(ir: CircuitIR, op: Op, bits: int) -> bool:
    """Evaluates an op's classical condition against ``bits`` (flat classical bit i is bit i)."""
    cond = op.condition
    if not cond:
        return True
    name, value = cond[0], cond[1]
    index = cond.index if isinstance(cond, Condition) else None  # a plain tuple tests the whole register
    offset = 0
    for reg in ir.cregs:
        if reg.name == name:
            if index is not None:
                return ((bits >> (offset + index)) & 1) == (value & 1)
            return ((bits >> offset) & ((1 << reg.size) - 1)) == value
        offset += reg.size
    raise KeyError("Classical register '%s' not found" % name)


def _project(state: np.ndarray, qubit: int, n: int, outcome: int) -> Tuple[np.ndarray, float]:
    """Projects ``qubit`` onto ``outcome``. Returns the (unnormalised) state and its probability."""
    index = [slice(None)] * n
    index[n - 1 - qubit] = 1 - outcome
    out = state.copy()
    out[tuple(index)] = 0.0
    return out, float(np.vdot(out, out).real)


def exact_distribution(ir: CircuitIR) -> Dict[str, float]:
    """
    Exact probability of every classical outcome of the circuit, starting from |0...0>.

    Unlike ``compute_statevector`` this models the whole program: mid-circuit measurement,
    reset and classically conditioned operations. Every measurement splits the simulation
    into one branch per outcome; trailing unconditioned measurements are read off the state
    vector directly, so a static circuit costs a single state-vector simulation.

    Keys are bitstrings over all classical bits with classical bit 0 right-most. A circuit
    without any measurement is treated as "measure every qubit" (qubit 0 right-most).
    """
    n = ir.num_qubits
    ops = [op for op in ir.ops if op.name != "barrier"]
    if not any(op.name == "measure" for op in ops):
        ops += [Op("measure", (q,), clbits=(q,)) for q in range(n)]
        width = n
    else:
        width = max(ir.num_clbits, 1 + max(op.clbits[0] for op in ops if op.name == "measure"))

    # Trailing unconditioned measurements need no branching.
    tail = len(ops)
    while tail > 0 and ops[tail - 1].name == "measure" and not ops[tail - 1].condition:
        tail -= 1

    start = np.zeros((2,) * n, dtype=complex)
    start[(0,) * n] = 1.0
    branches: List[Tuple[int, np.ndarray, float]] = [(0, start, 1.0)]  # (classical bits, state, probability)

    for op in ops[:tail]:
        nxt: List[Tuple[int, np.ndarray, float]] = []
        for bits, state, prob in branches:
            if not _condition_holds(ir, op, bits):
                nxt.append((bits, state, prob))
            elif op.name in ("measure", "reset"):
                q = op.qubits[0]
                for outcome in (0, 1):
                    projected, p = _project(state, q, n, outcome)
                    if p < 1e-12:
                        continue
                    projected = projected / np.sqrt(p)
                    if op.name == "measure":
                        c = op.clbits[0]
                        new_bits = (bits & ~(1 << c)) | (outcome << c)
                    else:
                        new_bits = bits
                        if outcome:  # reset: bring the qubit back to |0>
                            projected = _apply_gate_to_state(projected, get_gate_info("x").matrix_fn(()), (q,), n)
                    nxt.append((new_bits, projected, prob * p))
            else:
                nxt.append((bits, _apply_gate_to_state(state, _get_op_matrix(op), op.qubits, n), prob))
        if len(nxt) > MAX_BRANCHES:
            raise RuntimeError("Circuit has too many measurement branches for the reference simulator.")
        branches = nxt

    basis = np.arange(1 << n)
    totals: Dict[int, float] = {}
    for bits, state, prob in branches:
        outcome_bits = np.full(1 << n, bits, dtype=object if width > 62 else np.int64)
        for op in ops[tail:]:
            q, c = op.qubits[0], op.clbits[0]
            outcome_bits = (outcome_bits & ~(1 << c)) | (((basis >> q) & 1) << c)
        weights = prob * np.abs(state.reshape(-1)) ** 2
        for key, w in zip(outcome_bits.tolist(), weights.tolist()):
            if w > 1e-15:
                totals[key] = totals.get(key, 0.0) + w

    norm = sum(totals.values()) or 1.0
    return {format(k, "0%db" % width): v / norm for k, v in sorted(totals.items())}


def sample_counts(ir: CircuitIR, shots: int = 1024, seed: int = 1234) -> Dict[str, int]:
    """
    Reference execution of a circuit: ``shots`` samples drawn from ``exact_distribution``.
    Same key format (all classical bits, classical bit 0 right-most).
    """
    dist = exact_distribution(ir)
    keys = list(dist)
    drawn = np.random.default_rng(seed).multinomial(shots, [dist[k] for k in keys])
    return {k: int(c) for k, c in zip(keys, drawn) if c}


def unitary_fidelity(ir_a: CircuitIR, ir_b: CircuitIR) -> float:
    """
    Process fidelity |Tr(U_a^dagger @ U_b)| / 2^n of two circuits on the same qubits.
    1.0 means the unitaries are equal up to an unobservable global phase.
    """
    if ir_a.num_qubits != ir_b.num_qubits:
        return 0.0
    u_a = compute_unitary(ir_a)
    u_b = compute_unitary(ir_b)
    return float(np.abs(np.trace(u_a.conj().T @ u_b)) / (1 << ir_a.num_qubits))


def check_unitary_equivalence(ir_a: CircuitIR, ir_b: CircuitIR, tol: float = 1e-5) -> bool:
    """
    Verifies that ir_a and ir_b implement the exact same unitary up to an unobservable global phase.
    Criterion: |Tr(U_a^dagger @ U_b)| / 2^n >= 1 - tol
    """
    if ir_a.num_qubits != ir_b.num_qubits:
        return False
    if ir_a.num_qubits > 8:
        # High qubit count: fall back to statevector comparison
        return check_statevector_fidelity(ir_a, ir_b, tol=tol)
    return bool(unitary_fidelity(ir_a, ir_b) >= (1.0 - tol))


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

def check_random_state_equivalence(ir_a: CircuitIR, ir_b: CircuitIR, trials: int = 3, tol: float = 1e-5, seed: int = 7) -> bool:
    """
    Equivalence evidence for circuits too large for a full unitary comparison:
    both circuits are applied to the same random product states and the output states
    must agree up to a global phase.
    """
    if ir_a.num_qubits != ir_b.num_qubits:
        return False
    n = ir_a.num_qubits
    rng = np.random.default_rng(seed)
    for _ in range(trials):
        prep = tuple(
            Op("u3", (q,), params=tuple(float(x) for x in rng.uniform(0, 2 * np.pi, 3))) for q in range(n)
        )
        a = CircuitIR(n, ir_a.num_clbits, ir_a.qregs, ir_a.cregs, prep + tuple(ir_a.ops))
        b = CircuitIR(n, ir_b.num_clbits, ir_b.qregs, ir_b.cregs, prep + tuple(ir_b.ops))
        if not check_statevector_fidelity(a, b, tol=tol):
            return False
    return True
