"""
Property-based fuzzing tests for QC-C1-01 using Hypothesis.
Generates randomized quantum circuits and verifies:
1. Mathematical unitary equivalence (|Tr(U†V)|/2^n == 1.0 up to phase)
2. Input circuit immutability (byte/fingerprint unchanged)
3. Output circuit contains ONLY gates in the specified basis.
"""

import pytest
from hypothesis import given, strategies as st, settings
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.decompose.decomposer import decompose
from qnvkit.sim import check_unitary_equivalence

GATES_1Q = ["h", "x", "y", "z", "s", "t", "rx", "ry", "rz"]
GATES_2Q = ["cx", "cz", "swap", "crx", "cry", "crz"]


@st.composite
def random_quantum_circuit(draw, num_qubits=2, max_gates=8):
    gate_list = []
    num_gates = draw(st.integers(min_value=1, max_value=max_gates))
    for _ in range(num_gates):
        arity = draw(st.sampled_from([1, 2]))
        if arity == 1:
            gname = draw(st.sampled_from(GATES_1Q))
            q = draw(st.integers(min_value=0, max_value=num_qubits - 1))
            params = ()
            if gname in ("rx", "ry", "rz"):
                params = (draw(st.floats(min_value=-3.14, max_value=3.14)),)
            gate_list.append(Op(gname, (q,), params=params))
        else:
            gname = draw(st.sampled_from(GATES_2Q))
            q0 = draw(st.integers(min_value=0, max_value=num_qubits - 1))
            q1 = draw(st.integers(min_value=0, max_value=num_qubits - 1))
            if q0 == q1:
                q1 = (q0 + 1) % num_qubits
            params = ()
            if gname in ("crx", "cry", "crz"):
                params = (draw(st.floats(min_value=-3.14, max_value=3.14)),)
            gate_list.append(Op(gname, (q0, q1), params=params))

    return CircuitIR(
        num_qubits=num_qubits,
        num_clbits=0,
        qregs=(Register("q", num_qubits),),
        cregs=(),
        ops=tuple(gate_list),
    )


@settings(max_examples=25, deadline=None)
@given(ir=random_quantum_circuit(num_qubits=2, max_gates=6))
def test_fuzz_decomposition_qniverse_basis(ir):
    basis = {"rx", "ry", "rz", "cx"}
    orig_fingerprint = ir.fingerprint()

    result = decompose(ir, basis)

    # Immutability invariant
    assert ir.fingerprint() == orig_fingerprint, "Input circuit was mutated!"

    # Must succeed
    assert result.circuit is not None
    assert result.ir is not None

    # Every gate in output must be in basis
    for op in result.ir.ops:
        assert op.name in basis

    # Equivalence verification
    assert check_unitary_equivalence(ir, result.ir, tol=1e-4) is True


@settings(max_examples=20, deadline=None)
@given(ir=random_quantum_circuit(num_qubits=2, max_gates=6))
def test_fuzz_decomposition_u3_basis(ir):
    basis = {"u3", "cx"}
    orig_fingerprint = ir.fingerprint()

    result = decompose(ir, basis)

    assert ir.fingerprint() == orig_fingerprint
    assert result.circuit is not None
    assert result.ir is not None
    for op in result.ir.ops:
        assert op.name in basis

    assert check_unitary_equivalence(ir, result.ir, tol=1e-4) is True
