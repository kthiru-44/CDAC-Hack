"""
qnvkit.decompose.decomposer: Primary decomposition engine for QC-C1-01.
Implements user-selectable basis-gate decomposition with cycle guards,
strict non-mutation of inputs, full metric profiling, and explicit unsupported reporting.
"""

from typing import Union, List, Set, Optional, Any, Dict
from qnvkit.ir import CircuitIR, Op
from qnvkit.gates import DOCUMENTED_GATE_NAMES, is_valid_gate_name, get_gate_matrix
from qnvkit.metrics import profile
from qnvkit.report import ProfileReport, UnsupportedReport, DecomposeResult
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse, unrepresentable_barriers
from qnvkit.sim import check_unitary_equivalence, check_random_state_equivalence
from qnvkit.decompose.euler import synthesize_1q_unitary, decompose_discrete_1q_gate
from qnvkit.decompose.rules import decompose_multi_qubit_gate, decompose_two_qubit_gate

ENTANGLING_GATES = {
    "cx", "cy", "cz", "ch", "swap", "cs", "ct", "csdg", "ctdg",
    "cp", "crx", "cry", "crz", "cu1", "cu2", "cu3",
    "ccx", "cswap", "c3x", "c4x", "c5x"
}


def _expand_op_recursive(
    op: Op,
    basis_set: Set[str],
    depth: int = 0,
    max_depth: int = 15
) -> Optional[List[Op]]:
    """
    Recursively decomposes an operation until all sub-operations are within basis_set.
    Guarded against infinite cycles with max_depth.
    """
    if op.name in basis_set:
        return [op]

    if depth > max_depth:
        return None

    # Arity check
    arity = len(op.qubits)

    # 1. Multi-qubit (>2)
    if arity > 2:
        expanded = decompose_multi_qubit_gate(op, basis_set)
        if expanded is None:
            return None
        res: List[Op] = []
        for sub_op in expanded:
            sub_res = _expand_op_recursive(sub_op, basis_set, depth + 1, max_depth)
            if sub_res is None:
                return None
            res.extend(sub_res)
        return res

    # 2. Two-qubit
    if arity == 2:
        expanded = decompose_two_qubit_gate(op, basis_set)
        if expanded is None:
            return None
        res: List[Op] = []
        for sub_op in expanded:
            sub_res = _expand_op_recursive(sub_op, basis_set, depth + 1, max_depth)
            if sub_res is None:
                return None
            res.extend(sub_res)
        return res

    # 3. Single-qubit
    if arity == 1:
        def expand_all(ops: List[Op]) -> Optional[List[Op]]:
            out: List[Op] = []
            for sub_op in ops:
                sub_res = _expand_op_recursive(sub_op, basis_set, depth + 1, max_depth)
                if sub_res is None:
                    return None
                out.extend(sub_res)
            return out

        # a) continuous Euler synthesis when the basis offers rotations
        mat = get_gate_matrix(op.name, op.params)
        synth_ops = synthesize_1q_unitary(mat, op.qubits[0], basis_set, condition=op.condition)
        if synth_ops is not None:
            return synth_ops

        # b) exact discrete rewrites (e.g. into {h, t})
        discrete_res = decompose_discrete_1q_gate(op, basis_set)
        if discrete_res is not None:
            return expand_all(discrete_res)
        return None

    return None


# Largest circuit for a full unitary comparison / for a random-state comparison.
MAX_UNITARY_QUBITS = 8
MAX_STATE_QUBITS = 16


def _verify(ir: CircuitIR, decomposed_ir: CircuitIR):
    """Returns (verified, note). verified is None when the circuit is too large to check."""
    n = ir.num_qubits
    if n <= MAX_UNITARY_QUBITS:
        ok = check_unitary_equivalence(ir, decomposed_ir)
        return ok, "full unitary comparison up to global phase (%d qubits)" % n
    if n <= MAX_STATE_QUBITS:
        ok = check_random_state_equivalence(ir, decomposed_ir)
        return ok, "random-state comparison up to global phase (%d qubits, 3 states)" % n
    return None, "not verified: %d qubits exceeds the %d-qubit limit of the built-in check" % (n, MAX_STATE_QUBITS)


def _unsupported_reason(op: Op, basis: Set[str]) -> str:
    names = sorted(basis)
    if len(op.qubits) == 1:
        if not ({"u3"} & basis or len({"rx", "ry", "rz", "p", "u1"} & basis) >= 2):
            return (
                "'%s' cannot be written exactly with the 1-qubit gates in basis %s "
                "(a discrete basis only reaches specific gates; add rotations such as rz+ry or u3)." % (op.name, names)
            )
        return "No exact 1-qubit synthesis for '%s' in basis %s." % (op.name, names)
    return (
        "'%s' needs gates that basis %s cannot express exactly "
        "(its decomposition uses 1-qubit rotations/phases and an entangling gate cx or cz)." % (op.name, names)
    )


def decompose(
    circuit: Union[Any, CircuitIR],
    basis: Union[Set[str], List[str]]
) -> DecomposeResult:
    """
    Decomposes a QniverseCircuit or CircuitIR into a user-selected basis gate set.

    Validations:
      - Rejects None or invalid circuit input.
      - Rejects empty basis set.
      - Rejects basis gate names not in the 40 documented QSDK gates.

    Returns:
      DecomposeResult containing decomposed circuit, before/after metrics,
      unsupported report (if any), and mathematical equivalence verification status.
    """
    # 1. Input Validation
    if circuit is None:
        raise ValueError("Input circuit cannot be None.")
    if isinstance(basis, str):
        raise TypeError("Basis must be a list or set of gate names, e.g. {'rx', 'ry', 'rz', 'cx'}.")

    if not isinstance(circuit, CircuitIR):
        ir = from_qniverse(circuit)
    else:
        ir = circuit

    # Operations the decomposer does not know are reported, never passed through silently.
    unknown = sorted({op.name for op in ir.ops if op.name not in DOCUMENTED_GATE_NAMES})
    if unknown:
        return DecomposeResult(
            circuit=None, ir=None, before=None, after=None,
            unsupported=UnsupportedReport(
                unsupported_gates=tuple(
                    {"gate": g, "qubits": [], "reason": "Operation '%s' is not one of the documented QSDK gates handled by the profiler." % g}
                    for g in unknown
                ),
                is_valid=False,
            ),
            verified=False,
        )

    if not basis:
        raise ValueError("Basis gate set cannot be empty.")

    normalized_basis = {b.strip().lower() for b in basis if b.strip()}
    if not normalized_basis:
        raise ValueError("Basis gate set cannot be empty.")

    # Validate basis names against documented 40 gates
    invalid_gates = [g for g in normalized_basis if g not in DOCUMENTED_GATE_NAMES]
    if invalid_gates:
        raise ValueError(
            f"Invalid basis gate names not in documented QSDK surface: {invalid_gates}. "
            f"Permitted gates are a subset of: {sorted(DOCUMENTED_GATE_NAMES)}"
        )

    # Record initial profile and fingerprint
    profile_before = profile(ir)
    initial_fingerprint = ir.fingerprint()

    # 2. Entanglement feasibility check
    circuit_has_entangling = any(len(op.qubits) >= 2 for op in ir.ops if op.name not in ("barrier", "measure", "reset"))
    basis_has_entangling = any(g in ENTANGLING_GATES for g in normalized_basis)

    if circuit_has_entangling and not basis_has_entangling:
        unsupported = UnsupportedReport(
            unsupported_gates=(
                {
                    "gate": "ENTANGLING_OPERATIONS",
                    "qubits": [],
                    "reason": (
                        f"Circuit contains 2-qubit or multi-qubit entangling gates, "
                        f"but the chosen basis {sorted(normalized_basis)} does not contain any entangling gates."
                    )
                },
            ),
            is_valid=False
        )
        return DecomposeResult(
            circuit=None,
            ir=None,
            before=profile_before,
            after=None,
            unsupported=unsupported,
            verified=False
        )

    # 3. Sequential operation decomposition
    decomposed_ops: List[Op] = []
    unsupported_ops: List[Dict[str, Any]] = []

    for op in ir.ops:
        # Non-unitary operations copied exactly in order
        if op.name in ("barrier", "measure", "reset"):
            decomposed_ops.append(op)
            continue

        expanded = _expand_op_recursive(op, normalized_basis)
        if expanded is None:
            unsupported_ops.append({
                "gate": op.name,
                "qubits": list(op.qubits),
                "params": list(op.params),
                "reason": _unsupported_reason(op, normalized_basis)
            })
        else:
            decomposed_ops.extend(expanded)

    # 4. Handle unsupported operations if any occurred
    if unsupported_ops:
        unsupported = UnsupportedReport(
            unsupported_gates=tuple(unsupported_ops),
            is_valid=False
        )
        return DecomposeResult(
            circuit=None,
            ir=None,
            before=profile_before,
            after=None,
            unsupported=unsupported,
            verified=False
        )

    # 5. Assemble decomposed CircuitIR
    decomposed_ir = CircuitIR(
        num_qubits=ir.num_qubits,
        num_clbits=ir.num_clbits,
        qregs=ir.qregs,
        cregs=ir.cregs,
        ops=tuple(decomposed_ops)
    )

    # Strict immutability assertion
    assert ir.fingerprint() == initial_fingerprint, "Immutability violated: source circuit was modified!"

    # Calculate metrics after decomposition
    profile_after = profile(decomposed_ir)

    # Verify equivalence. A circuit that fails the check is never returned.
    verified, note = _verify(ir, decomposed_ir)
    if verified is False:
        unsupported = UnsupportedReport(
            unsupported_gates=(
                {
                    "gate": "EQUIVALENCE_CHECK",
                    "qubits": [],
                    "reason": "Decomposed circuit failed the equivalence check (%s); no circuit emitted." % note,
                },
            ),
            is_valid=False,
        )
        return DecomposeResult(
            circuit=None, ir=None, before=profile_before, after=None,
            unsupported=unsupported, verified=False, verification_note=note,
        )

    # Build a new QniverseCircuit (the input object is untouched)
    decomposed_qc = to_qniverse(decomposed_ir)
    warnings = []
    n_bar = unrepresentable_barriers(decomposed_ir)
    if n_bar:
        warnings.append(
            "%d one-qubit barrier(s) were left out of the returned QniverseCircuit because the QSDK "
            "needs at least two qubits per barrier; they are kept in result.ir and counted in the profile." % n_bar
        )

    return DecomposeResult(
        circuit=decomposed_qc,
        ir=decomposed_ir,
        before=profile_before,
        after=profile_after,
        unsupported=None,
        verified=bool(verified),
        verification_note=note,
        warnings=tuple(warnings),
    )
