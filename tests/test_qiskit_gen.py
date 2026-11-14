import pytest
import numpy as np
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.transpile.qiskit_gen import generate_qiskit_code


def test_qiskit_code_generation_and_execution():
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
    res = generate_qiskit_code(cir)

    assert res.report.status.lower() == "success"
    assert "qc.h(q[0])" in res.code
    assert "qc.cx(q[0], q[1])" in res.code
    assert "qc.measure(q[0], c[0])" in res.code

    # Execute generated code directly
    namespace = {}
    exec(res.code, namespace)
    assert "build_circuit" in namespace
    qc = namespace["build_circuit"]()

    assert qc.num_qubits == 2
    assert qc.num_clbits == 2
    assert len(qc.data) == 4


def test_qiskit_conditional_execution():
    qasm = """
    OPENQASM 3.0;
    qubit[1] q;
    bit[1] c;

    if (c[0] == 1) {
        x q[0];
    }
    """
    cir = parse_qasm3(qasm)
    res = generate_qiskit_code(cir)

    assert "with qc.if_test((c" in res.code
    namespace = {}
    exec(res.code, namespace)
    qc = namespace["build_circuit"]()
    assert qc.num_qubits == 1
