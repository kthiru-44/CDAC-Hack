"""
Tests for qnvkit.ir, qnvkit.qasm, and qnvkit.qsdk_adapter.
"""

import pytest
from qnvkit.ir import Register, Op, CircuitIR
from qnvkit.qasm.parser2 import parse_qasm2
from qnvkit.qsdk_adapter import from_qniverse, to_qniverse
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
from Qniverse.gates import h, cx, rx


def test_register_and_op_immutability():
    qr = Register("q", 3)
    assert qr.size == 3
    assert not qr.is_classical
    
    op = Op("H", (0,))
    assert op.name == "h"  # Auto lowercased
    assert op.qubits == (0,)


def test_qasm2_roundtrip():
    qasm_src = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0], q[1];
barrier q[0], q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""
    ir = parse_qasm2(qasm_src)
    assert ir.num_qubits == 2
    assert ir.num_clbits == 2
    assert len(ir.ops) == 5
    assert ir.ops[0].name == "h"
    assert ir.ops[1].name == "cx"
    assert ir.ops[2].name == "barrier"

    # Re-emit QASM
    emitted = ir.to_qasm2()
    assert "h q[0];" in emitted
    assert "cx q[0], q[1];" in emitted
    assert "barrier q[0], q[1];" in emitted

    # Re-parse
    ir2 = parse_qasm2(emitted)
    assert ir.fingerprint() == ir2.fingerprint()


def test_qsdk_adapter_roundtrip():
    qc = QniverseCircuit()
    q = QuantumRegister(2, 'q')
    qc.add_register(q)
    qc.add_register(ClassicalRegister(2, 'c'))
    qc.add_gate(h, q[0])
    qc.add_gate(cx, q[0], q[1])
    qc.add_gate(rx(1.570796), q[1])
    qc.measure_all()

    # Convert to IR
    ir = from_qniverse(qc)
    assert ir.num_qubits == 2
    assert len(ir.ops) == 5

    # Convert back to QniverseCircuit
    qc_back = to_qniverse(ir)
    assert qc_back is not None
    qasm_back = qc_back.qasm()
    assert "h q[0];" in qasm_back
    assert "cx q[0], q[1];" in qasm_back


def test_conditional_gates():
    qasm_src = """OPENQASM 2.0;
include "qelib1.inc";
qreg q[1];
creg c[1];
if(c==1) x q[0];
"""
    ir = parse_qasm2(qasm_src)
    assert len(ir.ops) == 1
    assert ir.ops[0].condition == ("c", 1)
    assert ir.ops[0].name == "x"


def test_circuit_ir_flat_index_helpers():
    ir = CircuitIR(
        num_qubits=5,
        num_clbits=3,
        qregs=(Register("q", 3), Register("anc", 2)),
        cregs=(Register("c", 3, is_classical=True),),
        ops=(Op("h", (0,)),)
    )
    assert ir.num_qubits == 5
    assert ir.num_clbits == 3

    assert ir.qubit_to_flat_index(("q", 0)) == 0
    assert ir.qubit_to_flat_index(("q", 2)) == 2
    assert ir.qubit_to_flat_index(("anc", 0)) == 3
    assert ir.qubit_to_flat_index(("anc", 1)) == 4

    assert ir.flat_index_to_qubit(3) == ("anc", 0)
    assert ir.flat_index_to_qubit(0) == ("q", 0)

