import pytest
from qnvkit.transpile.api import transpile


def test_transpile_multi_target():
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;
    bit[2] c;

    h q[0];
    cx q[0], q[1];
    c[0] = measure q[0];
    c[1] = measure q[1];
    """
    results = transpile(qasm, targets=["qiskit", "cirq", "cudaq", "qniverse"])

    assert "qiskit" in results
    assert "cirq" in results
    assert "cudaq" in results
    assert "qniverse" in results

    assert results["qiskit"].report.status.lower() == "success"
    assert results["cirq"].report.status.lower() == "success"
    assert results["cudaq"].report.status.lower() == "success"
    assert results["qniverse"].report.status.lower() == "success"


def test_transpile_with_verification():
    qasm = """
    OPENQASM 3.0;
    qubit[2] q;

    h q[0];
    cx q[0], q[1];
    """
    results = transpile(qasm, targets=["qiskit", "cirq"], options={"verify": True})

    q_ver = results["qiskit"].report.metrics.get("cross_framework_verification")
    assert q_ver is not None
    if q_ver["frameworks"]["qiskit"].get("executed"):
        assert q_ver["frameworks"]["qiskit"]["equivalent"] is True
        assert q_ver["frameworks"]["qiskit"]["fidelity"] >= 1.0 - 1e-6
    else:
        assert "not installed" in q_ver["frameworks"]["qiskit"].get("note", "")
        assert results["qiskit"].report.equivalence_verified is None

    c_ver = results["cirq"].report.metrics.get("cross_framework_verification")
    assert c_ver is not None
    if c_ver["frameworks"]["cirq"].get("executed"):
        assert c_ver["frameworks"]["cirq"]["equivalent"] is True
        assert c_ver["frameworks"]["cirq"]["fidelity"] >= 1.0 - 1e-6
    else:
        assert "not installed" in c_ver["frameworks"]["cirq"].get("note", "")
