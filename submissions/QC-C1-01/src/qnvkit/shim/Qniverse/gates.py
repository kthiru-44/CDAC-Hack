"""
Local stand-in for ``Qniverse.gates`` (used only when the real QSDK is not installed).

Mirrors the documented usage:
    qc.add_gate(h, q[0])
    qc.add_gate(rx(np.pi / 2), q[1])
    qc.add_gate(measure, q[0], c[0])
"""

_GATE_PARAMS = {
    "id": 0, "x": 0, "y": 0, "z": 0, "h": 0, "s": 0, "t": 0, "sdg": 0, "tdg": 0,
    "p": 1, "rx": 1, "ry": 1, "rz": 1, "u1": 1, "u2": 2, "u3": 3,
    "cx": 0, "cy": 0, "cz": 0, "ch": 0, "swap": 0, "cs": 0, "ct": 0, "csdg": 0, "ctdg": 0,
    "cp": 1, "crx": 1, "cry": 1, "crz": 1, "cu1": 1, "cu2": 2, "cu3": 3,
    "ccx": 0, "cswap": 0, "c3x": 0, "c4x": 0, "c5x": 0,
    "reset": 0, "measure": 0, "barrier": 0,
}

_GATE_QUBITS = {
    "cx": 2, "cy": 2, "cz": 2, "ch": 2, "swap": 2, "cs": 2, "ct": 2, "csdg": 2, "ctdg": 2,
    "cp": 2, "crx": 2, "cry": 2, "crz": 2, "cu1": 2, "cu2": 2, "cu3": 2,
    "ccx": 3, "cswap": 3, "c3x": 4, "c4x": 5, "c5x": 6,
}


class Gate:
    """A gate object. Parameterised gates are called with their angles: ``rx(theta)``."""

    def __init__(self, name, params=()):
        self.name = name
        self.params = tuple(float(p) for p in params)
        self.num_params = _GATE_PARAMS[name]
        self.num_qubits = _GATE_QUBITS.get(name, 1)

    def __call__(self, *params):
        if self.num_params == 0:
            raise TypeError("Gate '%s' takes no parameters." % self.name)
        if len(params) != self.num_params:
            raise TypeError(
                "Gate '%s' expects %d parameter(s), got %d." % (self.name, self.num_params, len(params))
            )
        return Gate(self.name, params)

    def __repr__(self):
        if self.params:
            return "%s(%s)" % (self.name, ", ".join("%g" % p for p in self.params))
        return self.name


for _name in _GATE_PARAMS:
    globals()[_name] = Gate(_name)
cnot = globals()["cx"]

__all__ = list(_GATE_PARAMS) + ["cnot", "Gate"]
