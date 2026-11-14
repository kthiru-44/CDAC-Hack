import math
import numpy as np
import pytest
from qnvkit.ir import Condition
from qnvkit.qasm.diagnostics import QASMError
from qnvkit.qasm.parser3 import parse_qasm3
from qnvkit.sim import compute_statevector
from c2_programs import H, PROGRAMS, INVALID


def ops(src):
    return parse_qasm3(H + src).ops


def test_a1_custom_gate_params_on_nonzero_qubits():
    o = ops("gate rot(t) a, b { rx(t) b; cx a, b; }\nqubit[2] x; qubit[3] q; rot(0.5) q[2], x[1];")
    assert [(p.name, p.qubits, p.params) for p in o] == [("rx", (1,), (0.5,)), ("cx", (4, 1), ())]


def test_a2_ctrl_rz_becomes_crz():
    o = ops("qubit[2] q; ctrl @ rz(0.3) q[0], q[1];")
    assert [(p.name, p.qubits, p.params) for p in o] == [("crz", (0, 1), (0.3,))]


def test_a2_ctrl_levels_and_negctrl():
    assert [p.name for p in ops("qubit[3] q; ctrl(2) @ x q[0], q[1], q[2];")] == ["ccx"]
    assert [p.name for p in ops("qubit[2] q; negctrl @ x q[0], q[1];")] == ["x", "cx", "x"]
    with pytest.raises(QASMError):  # no ccz in the gate set: rejected, not corrupted
        ops("qubit[3] q; ctrl @ ctrl @ z q[0], q[1], q[2];")


def test_a2_inv_u3_cancels():
    sv = compute_statevector(parse_qasm3(H + "qubit[1] q; u3(0.3,0.5,0.7) q[0]; inv @ u3(0.3,0.5,0.7) q[0];"))
    assert abs(abs(sv[0]) - 1) < 1e-12


def test_a2_inv_sequence_reverses():
    o = ops("gate g a { s a; h a; t a; }\nqubit[1] q; inv @ g q[0];")
    assert [p.name for p in o] == ["tdg", "h", "sdg"]


def test_a2_pow_integer_and_negative():
    assert [p.name for p in ops("qubit[1] q; pow(3) @ t q[0];")] == ["t", "t", "t"]
    assert [p.name for p in ops("qubit[1] q; pow(-2) @ t q[0];")] == ["tdg", "tdg"]
    assert ops("qubit[1] q; pow(0) @ t q[0];") == ()


def test_a2_pow_fraction_scales_angle_and_keeps_other_modifiers():
    o = ops("qubit[2] q; inv @ pow(0.5) @ rx(0.8) q[0];")
    assert [(p.name, p.params) for p in o] == [("rx", (-0.4,))]
    o = ops("qubit[2] q; ctrl @ pow(2) @ rx(0.1) q[0], q[1];")
    assert [p.name for p in o] == ["crx", "crx"]


def test_a2_ctrl_custom_gate():
    o = ops("gate g(t) a { ry(t) a; h a; }\nqubit[2] q; ctrl @ g(0.7) q[0], q[1];")
    assert [(p.name, p.qubits) for p in o] == [("cry", (0, 1)), ("ch", (0, 1))]


def test_a3_unsized_registers():
    ir = parse_qasm3(H + "qubit q; bit c; h q; c = measure q;")
    assert ir.num_qubits == 1 and ir.num_clbits == 1


def test_a4_gphase_ignored():
    ir = parse_qasm3(H + "qubit[1] q; gphase(0.3); h q[0];")
    assert [o.name for o in ir.ops] == ["h"]


def test_a5_bit_condition_keeps_index():
    o = ops("qubit[2] q; bit[2] c; if (c[1] == 1) x q[0];")[0]
    assert o.condition == Condition("c", 1, 1)
    o = ops("qubit[2] q; bit[1] c; if (c[0] == 1) x q[0];")[0]
    assert o.condition == ("c", 1)


def test_a7_aliases_normalised():
    names = [o.name for o in ops("qubit[3] q; U(0.1,0.2,0.3) q[0]; u(0.1,0.2,0.3) q[0]; phase(0.1) q[0]; "
                                 "cphase(0.1) q[0], q[1]; cnot q[0], q[1]; CX q[0], q[1]; toffoli q[0], q[1], q[2];")]
    assert names == ["u3", "u3", "p", "cp", "cx", "cx", "ccx"]


def test_a8_negative_step():
    o = ops("qubit[4] q; for int i in [3:-1:1] { h q[i]; }")
    assert [p.qubits[0] for p in o] == [3, 2, 1]
    o = ops("qubit[4] q; for int i in [0:2:3] { h q[i]; }")
    assert [p.qubits[0] for p in o] == [0, 2]


@pytest.mark.parametrize("expr", ["(1).__class__", "pi.real", "__import__('os')", "1 .real"])
def test_a9_expression_attack_rejected(expr):
    with pytest.raises(QASMError):
        parse_qasm3(H + "qubit[1] q; rx(%s) q[0];" % expr)


def test_a9_new_constants_and_functions():
    o = ops("qubit[1] q; rx(tau) q[0]; rx(euler) q[0]; rx(floor(2.7)) q[0]; rx(arcsin(1)) q[0]; rx(ln(euler)) q[0];")
    assert [round(p.params[0], 9) for p in o] == [round(2 * math.pi, 9), round(math.e, 9), 2.0, round(math.pi / 2, 9), 1.0]


@pytest.mark.parametrize("name", sorted(INVALID))
def test_a6_invalid_input_raises_qasmerror_with_location(name):
    with pytest.raises(QASMError) as ei:
        parse_qasm3(INVALID[name])
    assert ei.value.line is not None and ei.value.col is not None


@pytest.mark.parametrize("name", sorted(PROGRAMS))
def test_valid_programs_parse(name):
    assert parse_qasm3(PROGRAMS[name]).ops
