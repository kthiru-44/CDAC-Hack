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


def test_endianness_conversion():
    from qnvkit.sim import convert_statevector_endianness
    # State |01> (q0=0, q1=1 in Qiskit little-endian) -> index 2 in binary (q1, q0)
    # Cirq represents (q0, q1) where index 1 is |01>
    sv = np.array([0, 1, 0, 0], dtype=complex)  # index 1 (|01> in big-endian)
    converted = convert_statevector_endianness(sv, 2)
    # In little-endian, |01> corresponds to q0=0, q1=1 -> index 2
    assert converted[2] == 1.0
    assert converted[1] == 0.0



# ---------------------------------------------------------------- reference sampler
def test_exact_distribution_static_and_bit_order():
    from qnvkit.qasm.parser3 import parse_qasm3
    from qnvkit.sim import exact_distribution
    ir = parse_qasm3('OPENQASM 3.0; qubit[2] q; bit[2] c; x q[0]; c = measure q;')
    assert exact_distribution(ir) == {"01": 1.0}          # classical bit 0 right-most
    bell = parse_qasm3('OPENQASM 3.0; qubit[2] q; h q[0]; cx q[0], q[1];')   # no measurement: all qubits
    d = exact_distribution(bell)
    assert set(d) == {"00", "11"} and abs(d["00"] - 0.5) < 1e-12


def test_exact_distribution_follows_conditions_and_reset():
    from qnvkit.qasm.parser3 import parse_qasm3
    from qnvkit.sim import exact_distribution, sample_counts
    feed = parse_qasm3('OPENQASM 3.0; qubit[2] q; bit[2] c; h q[0]; c[0] = measure q[0]; '
                       'if (c[0] == 1) x q[1]; c[1] = measure q[1];')
    d = exact_distribution(feed)
    assert set(d) == {"00", "11"} and abs(d["11"] - 0.5) < 1e-12
    reg = parse_qasm3('OPENQASM 3.0; qubit[2] q; bit[2] c; bit[1] d; x q[0]; c[0] = measure q[0]; '
                      'if (c == 2) x q[1]; d[0] = measure q[1];')
    assert exact_distribution(reg) == {"001": 1.0}        # register value is 1, not 2: x is skipped
    rst = parse_qasm3('OPENQASM 3.0; qubit[1] q; bit[1] c; h q[0]; reset q[0]; c[0] = measure q[0];')
    assert exact_distribution(rst) == {"0": 1.0}
    counts = sample_counts(feed, shots=500, seed=3)
    assert sum(counts.values()) == 500 and set(counts) <= {"00", "11"}
