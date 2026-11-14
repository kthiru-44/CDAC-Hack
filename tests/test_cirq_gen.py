import pytest
import numpy as np
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.transpile.cirq_gen import generate_cirq_code


def test_cirq_code_generation_and_execution():
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
    res = generate_cirq_code(cir)

    assert res.report.status.lower() == "success"
    assert "cirq.H(q[0])" in res.code
    assert "cirq.CNOT(q[0], q[1])" in res.code
    assert "cirq.measure(q[0], key='c_0')" in res.code

    # Execute generated Cirq code directly if installed
    cirq = pytest.importorskip("cirq")
    namespace = {}
    exec(res.code, namespace)
    assert "build_circuit" in namespace
    circuit = namespace["build_circuit"]()

    assert len(circuit.all_qubits()) == 2
    sim = cirq.Simulator()
    result = sim.run(circuit, repetitions=100)
    assert "c_0" in result.records
    assert "c_1" in result.records
