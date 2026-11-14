"""
qnvkit.gates: Registry of the 40 Documented C-DAC QSDK Gates.
Provides metadata, matrix representations, arity, parameters, and self-inverse properties.
"""

from dataclasses import dataclass
from typing import Dict, Tuple, Optional, Callable, List
import numpy as np


@dataclass(frozen=True)
class GateInfo:
    name: str
    arity: int                          # Minimum qubit arity (variable for barrier)
    num_params: int
    is_unitary: bool
    is_self_inverse: bool = False
    inverse_name: Optional[str] = None
    matrix_fn: Optional[Callable[[Tuple[float, ...]], np.ndarray]] = None


# 1-Qubit matrices
def _mat_id(params=()):
    return np.eye(2, dtype=complex)

def _mat_x(params=()):
    return np.array([[0, 1], [1, 0]], dtype=complex)

def _mat_y(params=()):
    return np.array([[0, -1j], [1j, 0]], dtype=complex)

def _mat_z(params=()):
    return np.array([[1, 0], [0, -1]], dtype=complex)

def _mat_h(params=()):
    return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)

def _mat_s(params=()):
    return np.array([[1, 0], [0, 1j]], dtype=complex)

def _mat_sdg(params=()):
    return np.array([[1, 0], [0, -1j]], dtype=complex)

def _mat_t(params=()):
    return np.array([[1, 0], [0, np.exp(1j * np.pi / 4)]], dtype=complex)

def _mat_tdg(params=()):
    return np.array([[1, 0], [0, np.exp(-1j * np.pi / 4)]], dtype=complex)

def _mat_p(params):
    lam = params[0] if params else 0.0
    return np.array([[1, 0], [0, np.exp(1j * lam)]], dtype=complex)

def _mat_rx(params):
    theta = params[0] if params else 0.0
    c = np.cos(theta / 2)
    s = -1j * np.sin(theta / 2)
    return np.array([[c, s], [s, c]], dtype=complex)

def _mat_ry(params):
    theta = params[0] if params else 0.0
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)

def _mat_rz(params):
    lam = params[0] if params else 0.0
    return np.array([[np.exp(-1j * lam / 2), 0], [0, np.exp(1j * lam / 2)]], dtype=complex)

def _mat_u1(params):
    lam = params[0] if params else 0.0
    return _mat_p((lam,))

def _mat_u2(params):
    phi = params[0] if len(params) > 0 else 0.0
    lam = params[1] if len(params) > 1 else 0.0
    return np.array([
        [1.0 / np.sqrt(2), -np.exp(1j * lam) / np.sqrt(2)],
        [np.exp(1j * phi) / np.sqrt(2), np.exp(1j * (phi + lam)) / np.sqrt(2)]
    ], dtype=complex)

def _mat_u3(params):
    theta = params[0] if len(params) > 0 else 0.0
    phi = params[1] if len(params) > 1 else 0.0
    lam = params[2] if len(params) > 2 else 0.0
    c = np.cos(theta / 2)
    s = np.sin(theta / 2)
    return np.array([
        [c, -np.exp(1j * lam) * s],
        [np.exp(1j * phi) * s, np.exp(1j * (phi + lam)) * c]
    ], dtype=complex)


# 2-Qubit matrices (standard basis: |00>, |01>, |10>, |11> with wire 0 as control, wire 1 as target)
def _mat_cx(params=()):
    return np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0]
    ], dtype=complex)

def _mat_cz(params=()):
    return np.diag([1, 1, 1, -1]).astype(complex)

def _mat_swap(params=()):
    return np.array([
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1]
    ], dtype=complex)

def _make_controlled(u: np.ndarray, num_controls: int = 1) -> np.ndarray:
    dim_target = u.shape[0]
    dim_total = (2 ** num_controls) * dim_target
    mat = np.eye(dim_total, dtype=complex)
    mat[-dim_target:, -dim_target:] = u
    return mat

def _mat_cy(params=()):
    return _make_controlled(_mat_y())

def _mat_ch(params=()):
    return _make_controlled(_mat_h())

def _mat_cs(params=()):
    return _make_controlled(_mat_s())

def _mat_ct(params=()):
    return _make_controlled(_mat_t())

def _mat_csdg(params=()):
    return _make_controlled(_mat_sdg())

def _mat_ctdg(params=()):
    return _make_controlled(_mat_tdg())

def _mat_cp(params):
    return _make_controlled(_mat_p(params))

def _mat_crx(params):
    return _make_controlled(_mat_rx(params))

def _mat_cry(params):
    return _make_controlled(_mat_ry(params))

def _mat_crz(params):
    return _make_controlled(_mat_rz(params))

def _mat_cu1(params):
    return _make_controlled(_mat_u1(params))

def _mat_cu2(params):
    return _make_controlled(_mat_u2(params))

def _mat_cu3(params):
    return _make_controlled(_mat_u3(params))

def _mat_ccx(params=()):
    return _make_controlled(_mat_x(), 2)

def _mat_cswap(params=()):
    return _make_controlled(_mat_swap(), 1)

def _mat_c3x(params=()):
    return _make_controlled(_mat_x(), 3)

def _mat_c4x(params=()):
    return _make_controlled(_mat_x(), 4)

def _mat_c5x(params=()):
    return _make_controlled(_mat_x(), 5)


# Register all 40 QSDK gates
GATE_REGISTRY: Dict[str, GateInfo] = {
    # 1-Qubit Unitaries
    "id":   GateInfo("id", 1, 0, True, is_self_inverse=True, matrix_fn=_mat_id),
    "x":    GateInfo("x", 1, 0, True, is_self_inverse=True, matrix_fn=_mat_x),
    "y":    GateInfo("y", 1, 0, True, is_self_inverse=True, matrix_fn=_mat_y),
    "z":    GateInfo("z", 1, 0, True, is_self_inverse=True, matrix_fn=_mat_z),
    "h":    GateInfo("h", 1, 0, True, is_self_inverse=True, matrix_fn=_mat_h),
    "s":    GateInfo("s", 1, 0, True, inverse_name="sdg", matrix_fn=_mat_s),
    "t":    GateInfo("t", 1, 0, True, inverse_name="tdg", matrix_fn=_mat_t),
    "sdg":  GateInfo("sdg", 1, 0, True, inverse_name="s", matrix_fn=_mat_sdg),
    "tdg":  GateInfo("tdg", 1, 0, True, inverse_name="t", matrix_fn=_mat_tdg),
    "p":    GateInfo("p", 1, 1, True, matrix_fn=_mat_p),
    "rx":   GateInfo("rx", 1, 1, True, matrix_fn=_mat_rx),
    "ry":   GateInfo("ry", 1, 1, True, matrix_fn=_mat_ry),
    "rz":   GateInfo("rz", 1, 1, True, matrix_fn=_mat_rz),
    "u1":   GateInfo("u1", 1, 1, True, matrix_fn=_mat_u1),
    "u2":   GateInfo("u2", 1, 2, True, matrix_fn=_mat_u2),
    "u3":   GateInfo("u3", 1, 3, True, matrix_fn=_mat_u3),

    # 2-Qubit Unitaries
    "cx":   GateInfo("cx", 2, 0, True, is_self_inverse=True, matrix_fn=_mat_cx),
    "cy":   GateInfo("cy", 2, 0, True, is_self_inverse=True, matrix_fn=_mat_cy),
    "cz":   GateInfo("cz", 2, 0, True, is_self_inverse=True, matrix_fn=_mat_cz),
    "ch":   GateInfo("ch", 2, 0, True, is_self_inverse=True, matrix_fn=_mat_ch),
    "swap": GateInfo("swap", 2, 0, True, is_self_inverse=True, matrix_fn=_mat_swap),
    "cs":   GateInfo("cs", 2, 0, True, inverse_name="csdg", matrix_fn=_mat_cs),
    "ct":   GateInfo("ct", 2, 0, True, inverse_name="ctdg", matrix_fn=_mat_ct),
    "csdg": GateInfo("csdg", 2, 0, True, inverse_name="cs", matrix_fn=_mat_csdg),
    "ctdg": GateInfo("ctdg", 2, 0, True, inverse_name="ct", matrix_fn=_mat_ctdg),
    "cp":   GateInfo("cp", 2, 1, True, matrix_fn=_mat_cp),
    "crx":  GateInfo("crx", 2, 1, True, matrix_fn=_mat_crx),
    "cry":  GateInfo("cry", 2, 1, True, matrix_fn=_mat_cry),
    "crz":  GateInfo("crz", 2, 1, True, matrix_fn=_mat_crz),
    "cu1":  GateInfo("cu1", 2, 1, True, matrix_fn=_mat_cu1),
    "cu2":  GateInfo("cu2", 2, 2, True, matrix_fn=_mat_cu2),
    "cu3":  GateInfo("cu3", 2, 3, True, matrix_fn=_mat_cu3),

    # Multi-Qubit Unitaries (>2)
    "ccx":   GateInfo("ccx", 3, 0, True, is_self_inverse=True, matrix_fn=_mat_ccx),
    "cswap": GateInfo("cswap", 3, 0, True, is_self_inverse=True, matrix_fn=_mat_cswap),
    "c3x":   GateInfo("c3x", 4, 0, True, is_self_inverse=True, matrix_fn=_mat_c3x),
    "c4x":   GateInfo("c4x", 5, 0, True, is_self_inverse=True, matrix_fn=_mat_c4x),
    "c5x":   GateInfo("c5x", 6, 0, True, is_self_inverse=True, matrix_fn=_mat_c5x),

    # Non-Unitary / Meta
    "reset":   GateInfo("reset", 1, 0, False),
    "measure": GateInfo("measure", 1, 0, False),
    "barrier": GateInfo("barrier", 1, 0, False),
}

def _mat_cu(params):
    theta, phi, lam, gamma = (list(params) + [0.0] * 4)[:4]
    return _make_controlled(np.exp(1j * gamma) * _mat_u3((theta, phi, lam)))


# Standard OpenQASM 3 stdgates outside QSDK 40
_SX = 0.5 * np.array([[1 + 1j, 1 - 1j], [1 - 1j, 1 + 1j]], dtype=complex)
_SXDG = np.conjugate(_SX.T)

STDGATES_REGISTRY: Dict[str, GateInfo] = {
    "sx": GateInfo("sx", 1, 0, True, inverse_name="sxdg", matrix_fn=lambda params=(): _SX),
    "sxdg": GateInfo("sxdg", 1, 0, True, inverse_name="sx", matrix_fn=lambda params=(): _SXDG),
    "u": GateInfo("u", 1, 3, True, matrix_fn=_mat_u3),
    "cnot": GateInfo("cnot", 2, 0, True, is_self_inverse=True, matrix_fn=_mat_cx),
    "toffoli": GateInfo("toffoli", 3, 0, True, is_self_inverse=True, matrix_fn=_mat_ccx),
    "cu": GateInfo("cu", 2, 4, True, matrix_fn=_mat_cu),
    "phase": GateInfo("phase", 1, 1, True, matrix_fn=_mat_p),
    "cphase": GateInfo("cphase", 2, 1, True, matrix_fn=_mat_cp),
}

GateDef = GateInfo

def get_gate_def(name: str) -> GateInfo:
    """Lookup gate in either QSDK 40-gate registry or OpenQASM 3 stdgates registry."""
    n = name.lower()
    if n in GATE_REGISTRY:
        return GATE_REGISTRY[n]
    if n in STDGATES_REGISTRY:
        return STDGATES_REGISTRY[n]
    raise ValueError(f"Gate '{name}' is not recognized in QSDK or standard gates.")

DOCUMENTED_GATE_NAMES = set(GATE_REGISTRY.keys())


def is_valid_gate_name(name: str) -> bool:
    """Returns True if the gate name is one of the 40 documented QSDK gates."""
    return name.lower() in DOCUMENTED_GATE_NAMES


def get_gate_info(name: str) -> GateInfo:
    """Retrieves GateInfo for a documented gate name, raising ValueError if not documented."""
    n = name.lower()
    if n in GATE_REGISTRY:
        return GATE_REGISTRY[n]
    if n in STDGATES_REGISTRY:
        return STDGATES_REGISTRY[n]
    raise ValueError(f"Gate '{name}' is not one of the 40 documented QSDK gates.")


def get_gate_matrix(name: str, params: Tuple[float, ...] = ()) -> np.ndarray:
    """Computes exact unitary matrix for standard gates."""
    info = get_gate_info(name)
    if not info.is_unitary or info.matrix_fn is None:
        raise NotImplementedError(f"Direct matrix computation not available for '{name}'.")
    return info.matrix_fn(params)
