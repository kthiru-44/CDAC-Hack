"""
qnvkit.optimize.optimizer: Master optimization engine for QC-03-03.
Applies safe, documented local rewrite passes, verifies non-mutation,
and calculates before/after metrics using the shared profiler.
"""

from typing import Union, List, Optional, Any, Dict
from qnvkit.ir import CircuitIR
from qnvkit.metrics import profile
from qnvkit.report import OptimizeResult
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from qnvkit.sim import check_unitary_equivalence, check_statevector_fidelity
from qnvkit.optimize.passes import PASS_REGISTRY, MANDATORY_PASSES


def optimize(
    circuit: Union[Any, CircuitIR],
    passes: Optional[List[str]] = None,
    fixed_point: bool = False
) -> OptimizeResult:
    """
    Optimizes a QniverseCircuit or CircuitIR using a documented set of safe local rewrite rules.

    Parameters:
      circuit: Input quantum circuit. Remains strictly unmodified.
      passes: Optional list of pass names. Default: ["remove_identity", "cancel_self_inverse", "cancel_cx"].
      fixed_point: If True, iteratively applies passes until no further reduction (max 10 iterations).

    Returns:
      OptimizeResult dataclass with new optimized circuit, before/after ProfileReports,
      applied passes, and reduction percentage.
    """
    if circuit is None:
        raise ValueError("Input circuit cannot be None.")

    # Convert to CircuitIR if QniverseCircuit
    if not isinstance(circuit, CircuitIR):
        ir = from_qniverse(circuit)
    else:
        ir = circuit

    # Validate passes
    if passes is None:
        selected_passes = list(MANDATORY_PASSES)
    else:
        selected_passes = list(passes)
        if not selected_passes:
            raise ValueError("Pass list cannot be empty. Specify at least one pass or None for default.")

    # Check unknown pass names
    invalid_passes = [p for p in selected_passes if p not in PASS_REGISTRY]
    if invalid_passes:
        raise ValueError(
            f"Unknown pass name(s): {invalid_passes}. "
            f"Available passes are: {list(PASS_REGISTRY.keys())}"
        )

    # Immutability snapshot & before profile
    initial_fingerprint = ir.fingerprint()
    profile_before = profile(ir)

    current_ir = ir
    total_eliminated = 0
    warnings: List[str] = []

    # Execution loop
    max_iters = 10 if fixed_point else 1
    for iteration in range(max_iters):
        iter_eliminated = 0
        for pass_name in selected_passes:
            pass_fn = PASS_REGISTRY[pass_name]
            current_ir, count = pass_fn(current_ir)
            iter_eliminated += count

        total_eliminated += iter_eliminated
        if iter_eliminated == 0 and fixed_point:
            # Fixed point reached
            break

    # Immutability check
    assert ir.fingerprint() == initial_fingerprint, "Immutability violated: source circuit was modified!"

    profile_after = profile(current_ir)

    # Reduction calculation
    if profile_before.total_gates > 0:
        reduction_pct = round(
            ((profile_before.total_gates - profile_after.total_gates) / profile_before.total_gates) * 100.0,
            2
        )
    else:
        reduction_pct = 0.0

    if reduction_pct < 0:
        # Safety invariant: optimizer must never increase gate count
        warnings.append("Warning: Optimized circuit has more gates than original circuit.")

    # Verify mathematical equivalence
    try:
        if ir.num_qubits <= 8:
            eq = check_unitary_equivalence(ir, current_ir)
        else:
            eq = check_statevector_fidelity(ir, current_ir)
        if not eq:
            warnings.append("Mathematical equivalence check failed after optimization.")
    except Exception as e:
        warnings.append(f"Equivalence check could not be run: {e}")

    # Convert back to fresh QniverseCircuit
    optimized_qc = to_qniverse(current_ir)

    return OptimizeResult(
        circuit=optimized_qc,
        ir=current_ir,
        before=profile_before,
        after=profile_after,
        passes_applied=tuple(selected_passes),
        reduction_percentage=reduction_pct,
        warnings=tuple(warnings),
    )
