import pytest
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.transpile.cudaq_gen import generate_cudaq_code


def test_cudaq_code_generation():
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
    res = generate_cudaq_code(cir)

    assert res.report.status.lower() == "success"
    assert "@cudaq.kernel" in res.code
    assert "q = cudaq.qvector(2)" in res.code
    assert "h(q[0])" in res.code and "cudaq.h" not in res.code
    assert "x.ctrl(q[0], q[1])" in res.code
    assert "c_0 = mz(q[0])" in res.code
    assert "c_1 = mz(q[1])" in res.code


def test_cudaq_rotations():
    qasm = """
    OPENQASM 3.0;
    qubit[1] q;

    rx(1.57) q[0];
    ry(3.14) q[0];
    rz(0.78) q[0];
    """
    cir = parse_qasm3(qasm)
    res = generate_cudaq_code(cir)

    assert "rx(1.57, q[0])" in res.code
    assert "ry(3.14, q[0])" in res.code
    assert "rz(0.78, q[0])" in res.code
