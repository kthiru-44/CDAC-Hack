import math
import pytest
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.qasm.diagnostics import QASMError


def test_parse_basic_bell_state():
    qasm = """
    OPENQASM 3.0;
    include "stdgates.inc";
    qubit[2] q;
    bit[2] c;

    h q[0];
    cx q[0], q[1];
    c[0] = measure q[0];
    c[1] = measure q[1];
    """
    cir = parse_qasm3(qasm)
    assert cir.num_qubits == 2
    assert cir.num_clbits == 2
    assert len(cir) == 4
    assert cir.ops[0].name == "h"
    assert cir.ops[1].name == "cx"
    assert cir.ops[2].name == "measure"
    assert cir.ops[3].name == "measure"


def test_parse_qasm2_compatibility():
    qasm = """
    OPENQASM 2.0;
    include "qelib1.inc";
    qreg q[2];
    creg c[2];

    h q[0];
    cx q[0], q[1];
    measure q -> c;
    """
    cir = parse_qasm3(qasm)
    assert cir.num_qubits == 2
    assert cir.num_clbits == 2
    assert len(cir) == 4  # h, cx, measure q[0]->c[0], measure q[1]->c[1]


def test_parse_register_broadcast():
    qasm = """
    OPENQASM 3.0;
    qubit[3] q;
    h q;
    """
    cir = parse_qasm3(qasm)
    assert cir.num_qubits == 3
    assert len(cir) == 3
    assert all(op.name == "h" for op in cir.ops)
    assert [op.qubits[0] for op in cir.ops] == [0, 1, 2]


def test_parse_custom_gate_inlining():
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;

    gate bell a, b {
        h a;
        cx a, b;
    }

    bell q[0], q[1];
    """
    cir = parse_qasm3(qasm)
    assert len(cir) == 2
    assert cir.ops[0].name == "h"
    assert cir.ops[1].name == "cx"


def test_parse_modifiers():
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;

    inv @ s q[0];
    pow(2) @ x q[1];
    ctrl @ x q[0], q[1];
    """
    cir = parse_qasm3(qasm)
    assert len(cir) == 4  # s->sdg, x, x, cx
    assert cir.ops[0].name == "sdg"
    assert cir.ops[1].name == "x"
    assert cir.ops[2].name == "x"
    assert cir.ops[3].name == "cx"



def test_parse_for_loop():
    qasm = """
    OPENQASM 3.0;
    qubit[4] q;

    for i in [0:3] {
        h q[i];
    }
    """
    cir = parse_qasm3(qasm)
    assert len(cir) == 4
    for i in range(4):
        assert cir.ops[i].name == "h"
        assert cir.ops[i].qubits[0] == i


def test_parse_conditionals():
    qasm = """
    OPENQASM 3.0;
    qubit[1] q;
    bit[1] c;

    if (c[0] == 1) {
        x q[0];
    }
    """
    cir = parse_qasm3(qasm)
    assert len(cir) == 1
    assert cir.ops[0].name == "x"
    assert cir.ops[0].condition is not None
    assert cir.ops[0].condition == ("c", 1)


def test_parse_unsupported_diagnostics():
    qasm = """
    OPENQASM 3.0;
    qubit[1] q;
    bit[1] c;

    while (c[0] == 0) {
        h q[0];
    }
    """
    with pytest.raises(QASMError) as excinfo:
        parse_qasm3(qasm)
    assert "Unsupported OpenQASM 3 construct 'while'" in str(excinfo.value)
