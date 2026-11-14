"""
QC-C1-01: every documented QSDK gate x every basis.

Each decomposition must either (a) return a circuit that uses only basis gates and passes the
unitary equivalence check, or (b) return no circuit plus an explicit unsupported report.
Circuits are built and read back through the documented QSDK calls.
"""

import numpy as np
import pytest

import qnvkit.qsdk_adapter as adapter
from qnvkit.decompose.decomposer import decompose
from qnvkit.gates import DOCUMENTED_GATE_NAMES
from qnvkit.sim import check_unitary_equivalence
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister, ClassicalRegister
import Qniverse.gates as G

UNITARY_GATES = sorted(DOCUMENTED_GATE_NAMES - {"measure", "reset", "barrier"})
ARITY = {"ccx": 3, "cswap": 3, "c3x": 4, "c4x": 5, "c5x": 6}
ONE_QUBIT = {"id", "x", "y", "z", "h", "s", "t", "sdg", "tdg", "p", "rx", "ry", "rz", "u1", "u2", "u3"}
N_PARAMS = {"p": 1, "rx": 1, "ry": 1, "rz": 1, "u1": 1, "u2": 2, "u3": 3,
            "cp": 1, "crx": 1, "cry": 1, "crz": 1, "cu1": 1, "cu2": 2, "cu3": 3}

# Bases with continuous rotations: every gate must decompose.
UNIVERSAL_BASES = [
    ("rx", "ry", "rz", "cx"), ("u3", "cx"), ("rz", "ry", "cz"), ("rx", "rz", "cx"),
    ("rx", "ry", "cx"), ("p", "ry", "cx"), ("u1", "rx", "cz"), ("u1", "u2", "u3", "cx"),
]
# Discrete bases: only some gates are exactly reachable; the rest must be reported.
DISCRETE_BASES = [("h", "t", "cx"), ("h", "t", "tdg", "s", "sdg", "cx"), ("h", "s", "cx")]


def _single_gate_circuit(name, angles=(0.37, 0.21, 0.11)):
    n = 1 if name in ONE_QUBIT else ARITY.get(name, 2)
    qc = QniverseCircuit()
    q = QuantumRegister(n, "q")
    qc.add_register(q)
    gate = getattr(G, name)
    if name in N_PARAMS:
        gate = gate(*angles[: N_PARAMS[name]])
    qc.add_gate(gate, *[q[i] for i in range(n)])
    return qc


@pytest.mark.parametrize("basis", UNIVERSAL_BASES, ids=lambda b: "+".join(b))
@pytest.mark.parametrize("gate", UNITARY_GATES)
def test_every_gate_decomposes_and_verifies(gate, basis):
    qc = _single_gate_circuit(gate)
    before = qc.qasm()
    result = decompose(qc, set(basis))
    assert result.circuit is not None, result.unsupported.summary()
    assert result.verified is True
    assert {op.name for op in result.ir.ops} <= set(basis)
    # independent re-check on the circuit that was actually built through the QSDK calls
    assert check_unitary_equivalence(adapter.from_qniverse(qc), adapter.from_qniverse(result.circuit))
    assert qc.qasm() == before  # input untouched
    assert result.circuit is not qc


@pytest.mark.parametrize("basis", DISCRETE_BASES, ids=lambda b: "+".join(b))
@pytest.mark.parametrize("gate", UNITARY_GATES)
def test_discrete_basis_is_exact_or_reported(gate, basis):
    result = decompose(_single_gate_circuit(gate), set(basis))
    if result.circuit is None:
        assert result.unsupported is not None and result.unsupported.unsupported_gates
        assert result.after is None
    else:
        assert result.verified is True
        assert {op.name for op in result.ir.ops} <= set(basis)


@pytest.mark.parametrize("gate,expected_ok", [
    ("ccx", True), ("cz", True), ("swap", True), ("cs", True), ("x", True), ("tdg", True),
    ("ct", False), ("c3x", False), ("u3", False),
])
def test_clifford_t_reachability(gate, expected_ok):
    result = decompose(_single_gate_circuit(gate), {"h", "t", "cx"})
    assert (result.circuit is not None) is expected_ok


def test_special_angles_are_exact_in_clifford_t():
    qc = _single_gate_circuit("cp", angles=(np.pi / 2,))
    result = decompose(qc, {"h", "t", "tdg", "cx"})
    assert result.circuit is not None and result.verified


def test_toffoli_uses_six_cx():
    result = decompose(_single_gate_circuit("ccx"), {"h", "t", "tdg", "cx"})
    assert result.after.gate_counts["cx"] == 6


def test_conditional_gate_keeps_condition_and_parameters():
    qc = QniverseCircuit()
    q, c = QuantumRegister(2, "q"), ClassicalRegister(2, "c")
    qc.add_register(q)
    qc.add_register(c)
    qc.add_gate(G.h, q[0])
    qc.add_gate(G.measure, q[0], c[0])
    qc.add_conditional_gate(c, 1, G.x, q[1])
    result = decompose(qc, {"u3", "cx"})
    assert result.circuit is not None
    cond_ops = [op for op in adapter.from_qniverse(result.circuit).ops if op.condition]
    assert len(cond_ops) == 1
    assert cond_ops[0].name == "u3" and len(cond_ops[0].params) == 3
    assert cond_ops[0].condition == ("c", 1)


def test_measure_reset_barrier_are_copied_in_order():
    qc = QniverseCircuit()
    q, c = QuantumRegister(2, "q"), ClassicalRegister(2, "c")
    qc.add_register(q)
    qc.add_register(c)
    qc.add_gate(G.h, q[0])
    qc.add_gate(G.barrier, q[0], q[1])
    qc.add_gate(G.reset, q[1])
    qc.add_gate(G.swap, q[0], q[1])
    qc.add_gate(G.measure, q[0], c[1])
    assert "measure q[0] -> c[1];" in qc.qasm()
    result = decompose(qc, {"rz", "ry", "cx"})
    names = [op.name for op in result.ir.ops if op.name in ("barrier", "reset", "measure")]
    assert names == ["barrier", "reset", "measure"]
    assert "measure q[0] -> c[1];" in result.circuit.qasm()


def test_string_basis_and_non_circuit_are_rejected():
    qc = _single_gate_circuit("h")
    with pytest.raises(TypeError):
        decompose(qc, "cx")
    with pytest.raises(TypeError):
        decompose(object(), {"cx"})


def test_stand_in_rejects_undocumented_call_style():
    """The local stand-in only accepts the documented call style (gate objects, q[i] operands)."""
    if adapter.IS_LIVE_QNIVERSE:
        pytest.skip("only relevant for the local stand-in")
    qc = QniverseCircuit()
    q = QuantumRegister(1, "q")
    qc.add_register(q)
    with pytest.raises(TypeError):
        qc.add_gate("h", q[0])
    with pytest.raises(TypeError):
        qc.add_gate(G.h, 0)


def test_one_qubit_barrier_is_omitted_with_warning():
    """The official SDK cannot hold a one-qubit barrier (qc.qasm() raises); the IR keeps it."""
    from qnvkit.ir import CircuitIR, Register, Op
    ir = CircuitIR(2, 0, (Register("q", 2),), (), (Op("h", (0,)), Op("barrier", (0,)), Op("cx", (0, 1))))
    result = decompose(ir, {"u3", "cx"})
    assert result.circuit is not None
    assert result.warnings and "barrier" in result.warnings[0]
    assert any(op.name == "barrier" for op in result.ir.ops)
    assert "barrier" not in result.circuit.qasm()
