import pytest
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.transpile.qniverse_gen import generate_qniverse_code
from qnvkit.qsdk_adapter import to_qniverse


def test_qniverse_code_generation():
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;
    bit[2] c;

    h q[0];
    cx q[0], q[1];
    barrier q[0], q[1];
    c[0] = measure q[0];
    c[1] = measure q[1];
    """
    cir = parse_qasm3(qasm)
    res = generate_qniverse_code(cir)

    assert res.report.status.lower() == "success"
    assert "qc = QniverseCircuit" in res.code
    assert "qc.add_gate(h, q[0])" in res.code
    assert "qc.add_gate(cx, q[0], q[1])" in res.code
    assert "qc.add_gate(barrier, q[0], q[1])" in res.code
    assert "qc.add_gate(measure, q[0], c[0])" in res.code


def test_qsdk_adapter_direct_conversion():
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;
    bit[2] c;

    h q[0];
    cx q[0], q[1];
    c[0] = measure q[0];
    c[1] = measure q[1];
    """
    cir = parse_qasm3(qasm)
    qc = to_qniverse(cir)
    qasm_exported = qc.qasm()

    assert "OPENQASM 2.0;" in qasm_exported
    assert "h q[0];" in qasm_exported
    assert "cx q[0], q[1];" in qasm_exported
    assert "measure q[0] -> c[0];" in qasm_exported
