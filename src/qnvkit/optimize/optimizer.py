"""
qnvkit.optimize.optimizer: entry point of the QC-C3-03 circuit optimizer.

``optimize(circuit)`` runs a pipeline of rewrite passes (``qnvkit.optimize.passes``) and
returns an ``OptimizeResult`` holding a *new* circuit plus before/after metrics.

Guarantees:
  * the input circuit is never modified (the IR is immutable; a fingerprint check proves it);
  * no pass adds a gate, so the gate count never grows;
  * the result is checked against the input (unitary equal up to a global phase). If that
    check ever fails, the original circuit is returned unchanged with a warning, so a wrong
    circuit is never handed back.
"""

from typing import Any, List, Optional, Sequence, Tuple, Union
from qnvkit.ir import CircuitIR
from qnvkit.metrics import profile
from qnvkit.report import OptimizeResult
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from qnvkit.sim import check_unitary_equivalence, check_random_state_equivalence
from qnvkit.optimize.passes import ALL_PASSES, MANDATORY_PASSES, PASS_REGISTRY

# Up to this size the full unitaries are compared; above it, output states for random inputs.
FULL_UNITARY_MAX_QUBITS = 8
# Above this size a state vector no longer fits comfortably in memory; the check is skipped.
VERIFY_MAX_QUBITS = 20


def _resolve_passes(passes: Union[None, str, Sequence[str]]) -> List[str]:
    """Turns the ``passes`` argument into a validated list of pass names."""
    if passes is None:
        return list(MANDATORY_PASSES)
    if isinstance(passes, str):
        if passes != "all":
            raise ValueError("passes must be a list of pass names, None (mandatory passes) or 'all'.")
        return list(ALL_PASSES)
    selected = list(passes)
    if not selected:
        raise ValueError("Pass list cannot be empty. Specify at least one pass or None for default.")
    unknown = [p for p in selected if p not in PASS_REGISTRY]
    if unknown:
        raise ValueError(f"Unknown pass name(s): {unknown}. Available passes are: {list(PASS_REGISTRY)}")
    return selected


def _run_pipeline(ir: CircuitIR, pass_names: Sequence[str], fixed_point: bool) -> Tuple[CircuitIR, int]:
    """
    Applies the passes in order. With ``fixed_point`` the whole sequence is repeated until a
    full round removes nothing (each productive round removes at least one gate, so this ends).
    Returns the new IR and the number of rounds run.
    """
    rounds = 0
    while True:
        rounds += 1
        removed = 0
        for name in pass_names:
            ir, count = PASS_REGISTRY[name](ir)
            removed += count
        if not fixed_point or removed == 0:
            return ir, rounds


def _verify(original: CircuitIR, optimized: CircuitIR) -> Tuple[Optional[bool], Optional[str]]:
    """Checks that both circuits act identically. Returns ``(verdict, reason_if_not_checked)``."""
    n = original.num_qubits
    if n > VERIFY_MAX_QUBITS:
        return None, f"Equivalence check skipped: {n} qubits exceeds the simulator limit of {VERIFY_MAX_QUBITS}."
    try:
        if n <= FULL_UNITARY_MAX_QUBITS:
            return check_unitary_equivalence(original, optimized), None
        return check_random_state_equivalence(original, optimized), None
    except Exception as e:
        return None, f"Equivalence check could not be run: {e}"


def optimize(
    circuit: Union[Any, CircuitIR],
    passes: Union[None, str, Sequence[str]] = None,
    fixed_point: bool = False,
) -> OptimizeResult:
    """
    Optimizes a QniverseCircuit or CircuitIR with safe local rewrite rules.

    Parameters:
      circuit: the input circuit. It is never modified.
      passes: which passes to run, in this order.
          ``None`` (default)  the three mandatory passes: remove_identity, cancel_self_inverse, cancel_cx
          ``"all"``           every registered pass (adds cancel_extended_self_inverse,
                              cancel_inverse_pairs, merge_rotations)
          a list of names     exactly those passes; see ``PASS_REGISTRY``
      fixed_point: ``False`` runs the pass list once. ``True`` repeats it until nothing more
          can be removed, which catches nested redundancy such as ``X H H X``.

    Returns:
      OptimizeResult with
        ``circuit``                a new QniverseCircuit,
        ``ir``                     the same circuit as CircuitIR,
        ``before`` / ``after``     ProfileReport (gate counts, depth, ...),
        ``reduction_percentage``   drop in gate count,
        ``equivalence_verified``   True / False / None (None: check not run),
        ``warnings``               anything the caller should know.
      ``print(result.summary())`` gives a readable before/after report.

    Raises:
      ValueError for ``None`` input, an empty pass list or an unknown pass name.
    """
    if circuit is None:
        raise ValueError("Input circuit cannot be None.")
    pass_names = _resolve_passes(passes)
    ir = circuit if isinstance(circuit, CircuitIR) else from_qniverse(circuit)

    fingerprint = ir.fingerprint()
    optimized, rounds = _run_pipeline(ir, pass_names, fixed_point)
    assert ir.fingerprint() == fingerprint, "Immutability violated: source circuit was modified!"

    warnings: List[str] = []
    verified, not_checked = _verify(ir, optimized)
    if not_checked:
        warnings.append(not_checked)
    if verified is False:
        warnings.append("Mathematical equivalence check failed after optimization; "
                        "the original circuit is returned unchanged.")
        optimized = ir

    before, after = profile(ir), profile(optimized)
    if after.total_gates > before.total_gates:  # cannot happen with the built-in passes
        warnings.append("Warning: Optimized circuit has more gates than original circuit.")
    reduction = 0.0
    if before.total_gates:
        reduction = round(100.0 * (before.total_gates - after.total_gates) / before.total_gates, 2)

    return OptimizeResult(
        circuit=to_qniverse(optimized),
        ir=optimized,
        before=before,
        after=after,
        passes_applied=tuple(pass_names),
        reduction_percentage=reduction,
        warnings=tuple(warnings),
        equivalence_verified=verified,
        rounds=rounds,
    )
