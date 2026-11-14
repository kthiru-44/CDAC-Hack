import pytest
import numpy as np
from qnvkit.ir import CircuitIR, Register, Op
from qnvkit.metrics import profile
from qnvkit.sim import compute_unitary, compute_statevector
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.qasm.parser2 import parse_qasm2
import qnvkit.qsdk_adapter as adapter
from qnvkit.transpile.api import transpile
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister
from Qniverse.gates import h, cx, barrier


def test_barrier_scheduled_depth():
    """Barriers align spanned wires without adding an extra layer."""
    # Wire 0: layer 2 (H then X)
    # Wire 1: layer 0
    # Barrier on 0, 1 -> both align to layer 2
    # Next op on wire 1 -> layer 3
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register('q', 2),),
        cregs=(),
        ops=(
            Op('h', (0,)),
            Op('x', (0,)),
            Op('barrier', (0, 1)),
            Op('h', (1,)),
        )
    )
    prof = profile(ir)
    assert prof.depth == 3
    assert prof.barriers == 1


def test_barrier_simulation_invariance():
    """Barriers have zero effect on unitary and statevector."""
    ir_no_barrier = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register('q', 2),),
        cregs=(),
        ops=(
            Op('h', (0,)),
            Op('cx', (0, 1)),
        )
    )
    ir_with_barrier = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register('q', 2),),
        cregs=(),
        ops=(
            Op('h', (0,)),
            Op('barrier', (0, 1)),
            Op('cx', (0, 1)),
        )
    )
    u1 = compute_unitary(ir_no_barrier)
    u2 = compute_unitary(ir_with_barrier)
    assert np.allclose(u1, u2)

    sv1 = compute_statevector(ir_no_barrier)
    sv2 = compute_statevector(ir_with_barrier)
    assert np.allclose(sv1, sv2)


def test_bare_barrier_openqasm3():
    """OpenQASM 3 'barrier;' expands to all qubits."""
    qasm = """
    OPENQASM 3.0;
    qubit[3] q;
    h q[0];
    barrier;
    h q[1];
    """
    ir = parse_qasm3(qasm)
    barrier_op = [op for op in ir.ops if op.name == "barrier"][0]
    assert barrier_op.qubits == (0, 1, 2)


def test_qsdk_multi_register_barrier_safety():
    """Multi-register barriers are safely partitioned by register in QSDK."""
    ir = CircuitIR(
        num_qubits=5,
        num_clbits=0,
        qregs=(Register('qa', 1), Register('qb', 4)),
        cregs=(),
        ops=(
            Op('barrier', (0, 1, 2, 3, 4)),
        )
    )
    qc = adapter.to_qniverse(ir)
    text = adapter.read_qasm(qc)
    assert "barrier qb[0], qb[1], qb[2], qb[3];" in text
    assert "barrier qa" not in text  # qa has 1 qubit so omitted in QSDK (no out-of-bounds wires)

    # Roundtrip back
    ir2 = adapter.from_qniverse(qc)
    assert len(ir2.ops) == 1
    assert ir2.ops[0].name == "barrier"


def test_qsdk_single_qubit_barrier_handling():
    """Single-qubit barriers are omitted with unrepresentable_barriers tracking."""
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register('q', 2),),
        cregs=(),
        ops=(
            Op('barrier', (0,)),
        )
    )
    assert adapter.unrepresentable_barriers(ir) == 1
    qc = adapter.to_qniverse(ir)
    text = adapter.read_qasm(qc)
    assert "barrier" not in text


def test_transpile_barrier_all_targets():
    """Transpiler emits correct framework syntax for barriers."""
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;
    bit[2] c;
    h q[0];
    barrier q[0], q[1];
    cx q[0], q[1];
    c[0] = measure q[0];
    """
    res = transpile(qasm, targets=["qiskit", "cirq", "cudaq", "qniverse"])
    assert "qc.barrier(q[0], q[1])" in res["qiskit"].code
    for t in ("cirq", "cudaq"):
        compile(res[t].code, t, "exec")  # barrier must never become broken code
        assert "Barrier" not in res[t].code
        assert any("barrier omitted" in n for n in res[t].report.notes)
    assert "qc.add_gate(barrier, q[0], q[1])" in res["qniverse"].code
