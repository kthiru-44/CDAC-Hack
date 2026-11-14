"""
Tests for qnvkit.gates: 40 Documented QSDK Gates and Unitary Properties.
"""

import pytest
import numpy as np
from qnvkit.gates import GATE_REGISTRY, is_valid_gate_name, get_gate_info, get_gate_matrix


def test_all_40_gates_registered():
    """Verify that all 40 documented QSDK gates are present in registry."""
    assert len(GATE_REGISTRY) == 40
    for name in ["id", "x", "y", "z", "h", "s", "t", "sdg", "tdg", "rx", "ry", "rz", "cx", "cz", "ccx", "swap"]:
        assert is_valid_gate_name(name)


def test_self_inverse_gates():
    """Verify that self-inverse gates square to identity."""
    self_inv_1q = ["id", "x", "y", "z", "h"]
    for name in self_inv_1q:
        mat = get_gate_matrix(name)
        sq = mat @ mat
        assert np.allclose(sq, np.eye(2), atol=1e-7), f"{name} failed self-inverse property"

    # 2Q self-inverse
    for name in ["cx", "cz", "swap"]:
        mat = get_gate_matrix(name)
        sq = mat @ mat
        assert np.allclose(sq, np.eye(4), atol=1e-7), f"{name} failed self-inverse property"


def test_inverse_pairs():
    """Verify that (s, sdg) and (t, tdg) are true inverses."""
    s = get_gate_matrix("s")
    sdg = get_gate_matrix("sdg")
    assert np.allclose(s @ sdg, np.eye(2), atol=1e-7)

    t = get_gate_matrix("t")
    tdg = get_gate_matrix("tdg")
    assert np.allclose(t @ tdg, np.eye(2), atol=1e-7)


def test_rotations_at_zero():
    """Verify that Rx(0), Ry(0), Rz(0) equal identity up to phase."""
    for name in ["rx", "ry", "rz"]:
        mat = get_gate_matrix(name, (0.0,))
        assert np.allclose(np.abs(mat), np.eye(2), atol=1e-7)


def test_unitarity_of_gates():
    """Verify unitarity U @ U.dag = I across all unitary gates."""
    for name, gdef in GATE_REGISTRY.items():
        if not gdef.is_unitary or gdef.matrix_fn is None or gdef.arity > 3:
            continue
        params = tuple([0.456, 1.234, 2.345, 0.789][:gdef.num_params])
        mat = gdef.matrix_fn(params)
        ident = np.eye(mat.shape[0], dtype=complex)
        prod = mat @ np.conjugate(mat.T)
        np.testing.assert_allclose(prod, ident, atol=1e-10, err_msg=f"Gate {name} is not unitary")


def test_extra_rotations():
    rx_2pi = get_gate_matrix("rx", (2 * np.pi,))
    np.testing.assert_allclose(rx_2pi, -np.eye(2), atol=1e-10)

    rz_2pi = get_gate_matrix("rz", (2 * np.pi,))
    np.testing.assert_allclose(rz_2pi, -np.eye(2), atol=1e-10)

    h = get_gate_matrix("h")
    x = get_gate_matrix("x")
    z = get_gate_matrix("z")
    np.testing.assert_allclose(h, (x + z) / np.sqrt(2), atol=1e-10)

