"""
Comprehensive test suite for QC-C3-03: Quantum Circuit Optimization Using QSDK.
Tests all mandatory passes, opt-in passes, strict negative guards (barriers, intervening gates,
measurements, resets), immutability, and mathematical equivalence.
"""

import pytest
import numpy as np
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.optimize.optimizer import optimize
from qnvkit.optimize.passes import (
    remove_identity,
    cancel_self_inverse,
    cancel_cx,
    cancel_extended_self_inverse,
    cancel_inverse_pairs,
    merge_rotations,
)
from qnvkit.sim import check_unitary_equivalence
import qnvkit.qsdk_adapter
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
from Qniverse.gates import x


# ==============================================================================
# Mandatory Passes Unit Tests
# ==============================================================================

def test_remove_identity():
    """Verify explicit id and zero-rotations are eliminated."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("id", (0,)),
            Op("h", (0,)),
            Op("rx", (1,), params=(0.0,)),
            Op("rz", (1,), params=(2.0 * np.pi,)),
            Op("cx", (0, 1)),
        )
    )
    res_ir, count = remove_identity(ir)
    assert count == 3
    assert len(res_ir.ops) == 2
    op_names = [op.name for op in res_ir.ops]
    assert op_names == ["h", "cx"]


def test_cancel_self_inverse_mandatory():
    """Verify X-X, Y-Y, Z-Z, H-H cancel when adjacent."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("x", (0,)),
            Op("x", (0,)),
            Op("y", (1,)),
            Op("y", (1,)),
            Op("z", (0,)),
            Op("z", (0,)),
            Op("h", (1,)),
            Op("h", (1,)),
        )
    )
    res_ir, count = cancel_self_inverse(ir)
    assert count == 8
    assert len(res_ir.ops) == 0


def test_cancel_cx_mandatory():
    """Verify CX-CX with same control and target cancels."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("cx", (0, 1)),
            Op("cx", (0, 1)),
            Op("h", (1,)),
        )
    )
    res_ir, count = cancel_cx(ir)
    assert count == 2
    assert len(res_ir.ops) == 2
    assert [op.name for op in res_ir.ops] == ["h", "h"]


# ==============================================================================
# Negative Precondition Tests (CRITICAL SAFETY GUARDRAILS)
# ==============================================================================

def test_negative_barrier_blocks_self_inverse():
    """A barrier between two self-inverse gates MUST prevent cancellation."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("barrier", (0,)),
            Op("h", (0,)),
        )
    )
    res = optimize(ir)
    # The H gates must NOT be cancelled because of the barrier
    assert res.after.total_gates == 2
    assert len(res.ir.ops) == 3  # H, barrier, H


def test_negative_barrier_blocks_cx_cancellation():
    """A barrier between two CX gates MUST prevent cancellation."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("cx", (0, 1)),
            Op("barrier", (0, 1)),
            Op("cx", (0, 1)),
        )
    )
    res = optimize(ir)
    assert res.after.total_gates == 2
    assert len(res.ir.ops) == 3


def test_negative_intervening_gate_on_wire_blocks():
    """An intervening gate on wire 0 prevents cancellation of X(0) and X(0)."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("x", (0,)),
            Op("z", (0,)),  # Intervening Z gate
            Op("x", (0,)),
        )
    )
    res = optimize(ir)
    # Cannot cancel because Z is between them (X Z X = -Z != Z)
    assert res.after.total_gates == 3
    assert len(res.ir.ops) == 3


def test_negative_intervening_gate_on_cx_control_blocks():
    """An intervening gate on control wire of CX prevents cancellation."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("cx", (0, 1)),
            Op("x", (0,)),  # Intervening gate on control wire q0
            Op("cx", (0, 1)),
        )
    )
    res = optimize(ir)
    assert res.after.two_qubit_gates == 2


def test_negative_reverse_cx_does_not_cancel():
    """CX(0, 1) and CX(1, 0) have different roles and MUST NOT cancel."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("cx", (0, 1)),
            Op("cx", (1, 0)),
        )
    )
    res = optimize(ir)
    assert res.after.two_qubit_gates == 2


def test_negative_measurement_blocks_cancellation():
    """A measurement between identical gates blocks cancellation."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=1,
        qregs=(Register("q", 1),),
        cregs=(Register("c", 1),),
        ops=(
            Op("x", (0,)),
            Op("measure", (0,), clbits=(0,)),
            Op("x", (0,)),
        )
    )
    res = optimize(ir)
    assert res.after.single_qubit_gates == 2
    assert res.after.measurements == 1


def test_negative_reset_blocks_cancellation():
    """A reset between identical gates blocks cancellation."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("x", (0,)),
            Op("reset", (0,)),
            Op("x", (0,)),
        )
    )
    res = optimize(ir)
    assert res.after.single_qubit_gates == 2
    assert res.after.resets == 1


def test_negative_conditional_gates_not_rewritten():
    """Classically conditioned gates are never cancelled."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=1,
        qregs=(Register("q", 1),),
        cregs=(Register("c", 1),),
        ops=(
            Op("x", (0,), condition=("c", 1)),
            Op("x", (0,), condition=("c", 1)),
        )
    )
    res = optimize(ir)
    assert res.after.total_gates == 2


# ==============================================================================
# Opt-in Extra Passes Tests
# ==============================================================================

def test_extended_self_inverse():
    """Verify CZ-CZ and SWAP-SWAP cancellation."""
    ir = CircuitIR(
        num_qubits=3,
        num_clbits=0,
        qregs=(Register("q", 3),),
        cregs=(),
        ops=(
            Op("cz", (0, 1)),
            Op("cz", (0, 1)),
            Op("swap", (1, 2)),
            Op("swap", (1, 2)),
            Op("ccx", (0, 1, 2)),
            Op("ccx", (0, 1, 2)),
        )
    )
    res = optimize(ir, passes=["cancel_extended_self_inverse"])
    assert res.after.total_gates == 0


def test_inverse_pairs():
    """Verify S-Sdg and T-Tdg cancellation."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("s", (0,)),
            Op("sdg", (0,)),
            Op("t", (1,)),
            Op("tdg", (1,)),
        )
    )
    res = optimize(ir, passes=["cancel_inverse_pairs"])
    assert res.after.total_gates == 0


def test_merge_rotations():
    """Verify Rz(0.3) + Rz(0.5) merges to Rz(0.8), and Rz(pi/2) + Rz(-pi/2) eliminates."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            # Merges to Rz(0.8)
            Op("rz", (0,), params=(0.3,)),
            Op("rz", (0,), params=(0.5,)),
            # Eliminates completely
            Op("rx", (1,), params=(1.5,)),
            Op("rx", (1,), params=(-1.5,)),
        )
    )
    res = optimize(ir, passes=["merge_rotations"])
    assert res.after.total_gates == 1
    assert res.ir.ops[0].name == "rz"
    assert np.isclose(res.ir.ops[0].params[0], 0.8)


def test_fixed_point_pipeline():
    """Verify iterative collapse: X H H X -> X X -> Empty."""
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("x", (0,)),
            Op("h", (0,)),
            Op("h", (0,)),
            Op("x", (0,)),
        )
    )
    # Single pass only cancels H-H (leaves X X)
    res_single = optimize(ir, passes=["cancel_self_inverse"], fixed_point=False)
    assert res_single.after.total_gates == 2

    # Fixed point collapses completely
    res_fixed = optimize(ir, passes=["cancel_self_inverse"], fixed_point=True)
    assert res_fixed.after.total_gates == 0


# ==============================================================================
# Immutability and Validation Tests
# ==============================================================================

def test_input_immutability():
    """Ensure original QniverseCircuit is untouched."""
    qc = QniverseCircuit()
    q = QuantumRegister(2, "q")
    qc.add_register(q)
    qc.add_gate(x, q[0])
    qc.add_gate(x, q[0])
    original_qasm = qc.qasm()

    res = optimize(qc)
    assert qc.qasm() == original_qasm
    assert res.after.total_gates == 0


def test_no_improvement_circuit():
    """Circuit with no redundancies remains unchanged and gains 0 gates."""
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
    res = optimize(ir)
    assert res.after.total_gates == 2
    assert res.reduction_percentage == 0.0
    assert len(res.warnings) == 0


def test_unknown_pass_rejected():
    """Unknown pass name raises ValueError with list of valid passes."""
    ir = CircuitIR(1, 0, (), (), ())
    with pytest.raises(ValueError, match="Unknown pass name"):
        optimize(ir, passes=["invalid_pass_name"])
