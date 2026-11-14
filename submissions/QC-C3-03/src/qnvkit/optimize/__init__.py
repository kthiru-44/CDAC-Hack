"""
qnvkit.optimize: Quantum Circuit Optimization Using QSDK (QC-C3-03).

    from qnvkit.optimize import optimize
    result = optimize(qc, passes="all", fixed_point=True)   # qc: QniverseCircuit or CircuitIR
    print(result.summary())
    optimized_qc = result.circuit                            # a new QniverseCircuit

See docs/c3-03-user-guide.md for the rules and their safety conditions.
"""

from qnvkit.optimize.optimizer import optimize
from qnvkit.optimize.passes import (
    PASS_REGISTRY,
    MANDATORY_PASSES,
    ALL_PASSES,
    remove_identity,
    cancel_self_inverse,
    cancel_cx,
    cancel_extended_self_inverse,
    cancel_inverse_pairs,
    merge_rotations,
)

__all__ = [
    "optimize",
    "PASS_REGISTRY",
    "MANDATORY_PASSES",
    "ALL_PASSES",
    "remove_identity",
    "cancel_self_inverse",
    "cancel_cx",
    "cancel_extended_self_inverse",
    "cancel_inverse_pairs",
    "merge_rotations",
]
