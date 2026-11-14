"""
Property-based fuzzing tests for QC-C3-03 using Hypothesis.
Generates randomized quantum circuits with inserted redundancies and asserts:
1. Exact mathematical unitary equivalence after optimization
2. Gate count never increases (reduction_percentage >= 0)
3. Input circuit immutability
"""

import pytest
from hypothesis import given, strategies as st, settings
import numpy as np
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.optimize.optimizer import optimize
from qnvkit.sim import check_unitary_equivalence

GATES_1Q = ["h", "x", "y", "z", "s", "t", "rx", "ry", "rz"]


@st.composite
def random_redundant_circuit(draw, num_qubits=2, num_ops=6):
    ops = []
    for _ in range(num_ops):
        choice = draw(st.sampled_from(["normal_1q", "self_inv_pair", "cx_pair", "identity", "rot_pair"]))
        q = draw(st.integers(min_value=0, max_value=num_qubits - 1))
        other_q = (q + 1) % num_qubits

        if choice == "normal_1q":
            g = draw(st.sampled_from(GATES_1Q))
            p = (draw(st.floats(min_value=-3.14, max_value=3.14)),) if g in ("rx", "ry", "rz") else ()
            ops.append(Op(g, (q,), params=p))
        elif choice == "self_inv_pair":
            # X-X or H-H
            g = draw(st.sampled_from(["x", "h", "z", "y"]))
            ops.append(Op(g, (q,)))
            ops.append(Op(g, (q,)))
        elif choice == "cx_pair":
            # CX-CX
            ops.append(Op("cx", (q, other_q)))
            ops.append(Op("cx", (q, other_q)))
        elif choice == "identity":
            ops.append(Op("id", (q,)))
        elif choice == "rot_pair":
            angle = draw(st.floats(min_value=-2.0, max_value=2.0))
            ops.append(Op("rz", (q,), params=(angle,)))
            ops.append(Op("rz", (q,), params=(-angle,)))

    return CircuitIR(
        num_qubits=num_qubits,
        num_clbits=0,
        qregs=(Register("q", num_qubits),),
        cregs=(),
        ops=tuple(ops),
    )


@settings(max_examples=30, deadline=None)
@given(ir=random_redundant_circuit(num_qubits=2, num_ops=5))
def test_fuzz_optimizer_equivalence(ir):
    orig_fingerprint = ir.fingerprint()
    all_passes = [
        "remove_identity",
        "cancel_self_inverse",
        "cancel_cx",
        "cancel_extended_self_inverse",
        "cancel_inverse_pairs",
        "merge_rotations",
    ]

    res = optimize(ir, passes=all_passes, fixed_point=True)

    # Immutability
    assert ir.fingerprint() == orig_fingerprint

    # Gate count must not increase
    assert res.after.total_gates <= res.before.total_gates
    assert res.reduction_percentage >= 0.0

    # Mathematical equivalence
    assert check_unitary_equivalence(ir, res.ir, tol=1e-4) is True
