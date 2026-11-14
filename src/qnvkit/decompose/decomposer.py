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
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from qnvkit.sim import check_unitary_equivalence, check_statevector_fidelity
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
        # Check discrete lookup first
        discrete_res = decompose_discrete_1q_gate(op, basis_set)
        if discrete_res is not None:
            res: List[Op] = []
            for sub_op in discrete_res:
                sub_res = _expand_op_recursive(sub_op, basis_set, depth + 1, max_depth)
                if sub_res is None:
                    return None
                res.extend(sub_res)
            return res

        # Fall back to continuous Euler matrix synthesis
        try:
            mat = get_gate_matrix(op.name, op.params)
            synth_ops = synthesize_1q_unitary(mat, op.qubits[0], basis_set, condition=op.condition)
            if synth_ops is None:
                return None
            res: List[Op] = []
            for sub_op in synth_ops:
                sub_res = _expand_op_recursive(sub_op, basis_set, depth + 1, max_depth)
                if sub_res is None:
                    return None
                res.extend(sub_res)
            return res
        except Exception:
            return None

    return None


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

    if not isinstance(circuit, CircuitIR):
        ir = from_qniverse(circuit)
    else:
        ir = circuit

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
                "reason": f"No decomposition rule available to convert '{op.name}' into basis {sorted(normalized_basis)}"
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

    # Verify mathematical equivalence
    verified = False
    try:
        if ir.num_qubits <= 8:
            verified = check_unitary_equivalence(ir, decomposed_ir)
        else:
            verified = check_statevector_fidelity(ir, decomposed_ir)
    except Exception:
        verified = False

    # Convert back to QniverseCircuit
    decomposed_qc = to_qniverse(decomposed_ir)

    return DecomposeResult(
        circuit=decomposed_qc,
        ir=decomposed_ir,
        before=profile_before,
        after=profile_after,
        unsupported=None,
        verified=verified
    )
