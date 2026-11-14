"""
Tests for qnvkit.sim: Exact Numerical Simulation & Equivalence Checking.
"""

import pytest
import numpy as np
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.sim import (
    compute_unitary,
    compute_statevector,
    check_unitary_equivalence,
    check_statevector_fidelity,
    total_variation_distance
)


def test_bell_statevector():
    # H(0) -> CX(0, 1) produces (|00> + |11>)/sqrt(2)
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("cx", (0, 1)),
        )
    )
    sv = compute_statevector(ir)
    expected = np.zeros(4, dtype=complex)
    expected[0] = 1.0 / np.sqrt(2)
    expected[3] = 1.0 / np.sqrt(2)
    assert np.allclose(sv, expected, atol=1e-7)


def test_ghz_statevector():
    # 3-qubit GHZ state (|000> + |111>)/sqrt(2)
    ir = CircuitIR(
        num_qubits=3,
        num_clbits=0,
        qregs=(Register("q", 3),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("cx", (0, 1)),
            Op("cx", (1, 2)),
        )
    )
    sv = compute_statevector(ir)
    expected = np.zeros(8, dtype=complex)
    expected[0] = 1.0 / np.sqrt(2)
    expected[7] = 1.0 / np.sqrt(2)
    assert np.allclose(sv, expected, atol=1e-7)


def test_global_phase_invariance():
    # Circuit A: H
    ir_a = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(Op("h", (0,)),)
    )
    # Circuit B: Rz(pi/2) Rx(pi/2) Rz(pi/2) which equals H up to global phase e^(i*pi/4)
    ir_b = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("rz", (0,), params=(np.pi / 2,)),
            Op("rx", (0,), params=(np.pi / 2,)),
            Op("rz", (0,), params=(np.pi / 2,)),
        )
    )
    assert check_unitary_equivalence(ir_a, ir_b) is True


def test_total_variation_distance():
    dist1 = {"00": 0.5, "11": 0.5}
    dist2 = {"00": 0.5, "11": 0.5}
    dist3 = {"00": 1.0, "11": 0.0}

    assert total_variation_distance(dist1, dist2) == 0.0
    assert total_variation_distance(dist1, dist3) == 0.5
