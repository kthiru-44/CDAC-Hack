"""
Tests for qnvkit.metrics and scheduled depth calculation.
"""

import pytest
from qnvkit.ir import Register, Op, CircuitIR
from qnvkit.metrics import calculate_scheduled_depth, profile


def test_depth_disjoint_parallel():
    # 2 gates on disjoint qubits should have depth 1
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("h", (1,)),
        )
    )
    assert calculate_scheduled_depth(ir) == 1
    p = profile(ir)
    assert p.depth == 1
    assert p.total_gates == 2
    assert p.single_qubit_gates == 2
    assert p.two_qubit_gates == 0


def test_depth_dependent_sequential():
    # 3 gates on the same qubit should have depth 3
    ir = CircuitIR(
        num_qubits=1,
        num_clbits=0,
        qregs=(Register("q", 1),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("t", (0,)),
            Op("h", (0,)),
        )
    )
    assert calculate_scheduled_depth(ir) == 3


def test_depth_entangling_gate():
    # Gate on q0 (layer 1), gate on q1 (layer 1), CX on q0, q1 (layer 2)
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("h", (1,)),
            Op("cx", (0, 1)),
        )
    )
    assert calculate_scheduled_depth(ir) == 2


def test_depth_barrier_alignment():
    # q0 has 2 gates (layer 2)
    # q1 has 0 gates (layer 0)
    # Barrier on q0, q1 aligns q1 to layer 2 without adding a layer
    # Next gate on q1 should start at layer 3
    ir = CircuitIR(
        num_qubits=2,
        num_clbits=0,
        qregs=(Register("q", 2),),
        cregs=(),
        ops=(
            Op("h", (0,)),
            Op("t", (0,)),
            Op("barrier", (0, 1)),
            Op("h", (1,)),
        )
    )
    # Depth before H(1) is 2. H(1) executes at layer 3.
    assert calculate_scheduled_depth(ir) == 3


def test_qubits_used_vs_declared():
    # 4 declared qubits, only 2 used
    ir = CircuitIR(
        num_qubits=4,
        num_clbits=0,
        qregs=(Register("q", 4),),
        cregs=(),
        ops=(
            Op("h", (1,)),
            Op("cx", (1, 3)),
        )
    )
    p = profile(ir)
    assert p.qubits_declared == 4
    assert p.qubits_used == 2
    assert p.multi_qubit_gates == 0
    assert p.two_qubit_gates == 1
    assert p.single_qubit_gates == 1
