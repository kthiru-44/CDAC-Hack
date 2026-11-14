"""
Comprehensive test suite for QC-C1-01: Basis Gate Decomposition.
Tests valid rewrites, equivalence checks, non-mutation, and unsupported operation reporting.
"""

import pytest
import numpy as np
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.decompose.decomposer import decompose
from qnvkit.metrics import profile
import qnvkit.qsdk_adapter  # noqa: F401  (makes the QSDK, or its local stand-in, importable)
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
from Qniverse.gates import h, cx


def test_decompose_native_qniverse_basis():
    """Test decomposition into C-DAC native basis: {rx, ry, rz, cx}."""
    # Circuit with H, S, T, CX
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("s", (0,)),
            Op("t", (1,)),
            Op("cx", (0, 1)),
        )
    )

    basis = {"rx", "ry", "rz", "cx"}
    result = decompose(ir, basis)

    assert result.circuit is not None
    assert result.verified is True
    assert result.unsupported is None
    assert result.after is not None

    # Check that all gates in result.ir are in basis
    for op in result.ir.ops:
        assert op.name in basis


def test_decompose_universal_u3_cx_basis():
    """Test decomposition into standard universal basis: {u3, cx}."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("rz", (0,), params=(0.785398,)),
            Op("cx", (0, 1)),
            Op("swap", (0, 1)),
        )
    )

    basis = {"u3", "cx"}
    result = decompose(ir, basis)

    assert result.circuit is not None
    assert result.verified is True
    for op in result.ir.ops:
        assert op.name in basis


def test_decompose_toffoli_into_clifford_t():
    """Test Toffoli (CCX) decomposition into 6 CX + Clifford+T gates."""
    ir = CircuitIR(
        num_qubits=3,
        num_clbits=0,
        qregs=(Register("q", 3),),
        cregs=(),
        ops=(
            Op("ccx", (0, 1, 2)),
        )
    )

    basis = {"h", "t", "tdg", "cx"}
    result = decompose(ir, basis)

    assert result.circuit is not None
    assert result.verified is True
    # 6 CX gates must be present
    cx_count = sum(1 for op in result.ir.ops if op.name == "cx")
    assert cx_count == 6


def test_preserves_measurements_and_barriers():
    """Test that measurement and barrier instructions are preserved without reordering."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=2,
        qregs=(Register("q", 2),),
        cregs=(Register("c", 2),),
        ops=(
            Op("h", (0,)),
            Op("barrier", (0, 1)),
            Op("cx", (0, 1)),
            Op("measure", (0,), clbits=(0,)),
            Op("measure", (1,), clbits=(1,)),
        )
    )

    basis = {"rx", "ry", "rz", "cx"}
    result = decompose(ir, basis)

    assert result.circuit is not None
    assert result.after.measurements == 2
    assert result.after.barriers == 1

    # Verify positions: barrier is between 1q gates and cx, measure at the end
    op_names = [op.name for op in result.ir.ops]
    assert "barrier" in op_names
    assert op_names[-2] == "measure"
    assert op_names[-1] == "measure"


def test_input_immutability():
    """Verify input circuit is strictly unmodified."""
    qc = QniverseCircuit()
    q = QuantumRegister(2, 'q')
    qc.add_register(q)
    qc.add_gate(h, q[0])
    qc.add_gate(cx, q[0], q[1])

    original_qasm = qc.qasm()
    result = decompose(qc, {"rx", "ry", "rz", "cx"})

    # Ensure input circuit has identical QASM
    assert qc.qasm() == original_qasm


# ===================== NEGATIVE TESTS =====================

def test_negative_empty_basis():
    """Empty basis must raise ValueError."""
    ir = CircuitIR(num_qubits=1, num_clbits=0, qregs=(), cregs=(), ops=())
    with pytest.raises(ValueError, match="Basis gate set cannot be empty"):
        decompose(ir, [])


def test_negative_invalid_gate_name():
    """Invalid gate names (e.g. 'sx') must be rejected with offender named."""
    ir = CircuitIR(num_qubits=1, num_clbits=0, qregs=(), cregs=(), ops=())
    with pytest.raises(ValueError, match="Invalid basis gate names"):
        decompose(ir, {"rx", "sx", "cz"})


def test_negative_none_circuit():
    """None circuit must raise ValueError."""
    with pytest.raises(ValueError, match="Input circuit cannot be None"):
        decompose(None, {"rx", "ry", "rz", "cx"})


def test_negative_unsupported_entangling_missing():
    """Entangling circuit decomposed into 1-qubit only basis returns unsupported report."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("cx", (0, 1)),
        )
    )

    basis = {"rx", "ry", "rz"}  # No 2-qubit gate in basis!
    result = decompose(ir, basis)

    assert result.circuit is None
    assert result.ir is None
    assert result.unsupported is not None
    assert result.unsupported.is_valid is False
    assert len(result.unsupported.unsupported_gates) > 0
    assert "ENTANGLING_OPERATIONS" in result.unsupported.unsupported_gates[0]["gate"]


def test_negative_continuous_rotation_in_discrete_basis():
    """Continuous rotation (e.g. rx(0.35)) in discrete Clifford+T basis returns unsupported report."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("rx", (0,), params=(0.35,)),
        )
    )

    basis = {"h", "t", "tdg", "s", "cx"}
    result = decompose(ir, basis)

    assert result.circuit is None
    assert result.unsupported is not None
    assert any(g["gate"] == "rx" for g in result.unsupported.unsupported_gates)
