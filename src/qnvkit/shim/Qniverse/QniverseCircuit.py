"""
Local stand-in for ``Qniverse.QniverseCircuit`` (used only when the real QSDK is not installed).

It implements the *documented* QSDK calls so that code written against it runs unchanged
on the real SDK:
    qc = QniverseCircuit()
    q = QuantumRegister(3, 'q'); c = ClassicalRegister(3, 'c')
    qc.add_register(q); qc.add_register(c)
    qc.add_gate(h, q[0]); qc.add_gate(cx, q[0], q[1]); qc.add_gate(rx(0.5), q[2])
    qc.add_gate(measure, q[0], c[0])
    qc.add_conditional_gate(c, 1, x, q[1])
    qc.qasm()
"""

from .gates import Gate, _GATE_PARAMS


class Qubit:
    def __init__(self, register, index):
        self.register = register
        self.index = index

    def __repr__(self):
        return "%s[%d]" % (self.register.prefix, self.index)


class Clbit(Qubit):
    pass


class _Register:
    _bit_cls = Qubit

    def __init__(self, size, prefix):
        if not isinstance(size, int) or size <= 0:
            raise ValueError("Register size must be a positive integer.")
        if not isinstance(prefix, str) or not prefix.isalpha():
            raise ValueError("Register name must contain alphabetic characters only.")
        if prefix in _GATE_PARAMS:
            raise ValueError("Register name '%s' conflicts with a gate name." % prefix)
        self.size = size
        self.prefix = prefix
        self.name = prefix
        self._bits = [self._bit_cls(self, i) for i in range(size)]

    def __getitem__(self, i):
        return self._bits[i]

    def __len__(self):
        return self.size

    def __repr__(self):
        return "%s(%d, '%s')" % (type(self).__name__, self.size, self.prefix)


class QuantumRegister(_Register):
    _bit_cls = Qubit


class ClassicalRegister(_Register):
    _bit_cls = Clbit


class QniverseCircuit:
    def __init__(self):
        self._qregs = []
        self._cregs = []
        self._ops = []  # (gate, bits, condition)

    # ---- registers -------------------------------------------------------
    def add_register(self, reg):
        if not isinstance(reg, (QuantumRegister, ClassicalRegister)):
            raise TypeError("Unknown register type: %r" % type(reg))
        if any(r.prefix == reg.prefix for r in self._qregs + self._cregs):
            raise ValueError("Register name '%s' is already used in this circuit." % reg.prefix)
        (self._qregs if isinstance(reg, QuantumRegister) else self._cregs).append(reg)

    def _owns(self, bit):
        regs = self._cregs if isinstance(bit, Clbit) else self._qregs
        return any(bit.register is r for r in regs)

    # ---- gates -----------------------------------------------------------
    def _check(self, gate, bits):
        if not isinstance(gate, Gate):
            raise TypeError("add_gate expects a gate object from Qniverse.gates, got %r." % (gate,))
        if gate.num_params and len(gate.params) != gate.num_params:
            raise TypeError("Gate '%s' needs %d parameter(s)." % (gate.name, gate.num_params))
        for b in bits:
            if not isinstance(b, Qubit):
                raise TypeError("Gate operands must be Qubit/Clbit objects such as q[0], got %r." % (b,))
            if not self._owns(b):
                raise ValueError("Wire %r does not belong to this circuit." % (b,))
        if len(set(id(b) for b in bits)) != len(bits):
            raise ValueError("Duplicate wires are not allowed.")
        if gate.name == "measure":
            if len(bits) != 2 or isinstance(bits[0], Clbit) or not isinstance(bits[1], Clbit):
                raise ValueError("measure requires exactly a Qubit followed by a Clbit.")
        else:
            if any(isinstance(b, Clbit) for b in bits):
                raise ValueError("Gate '%s' acts on qubits only." % gate.name)
            if gate.name == "barrier" and len(bits) not in (1, 2):
                raise ValueError("Gate 'BARRIER' requires 1 or 2 qubits, but got %d" % len(bits))
            if gate.name != "barrier" and len(bits) != gate.num_qubits:
                raise ValueError(
                    "Gate '%s' acts on %d qubit(s), got %d." % (gate.name, gate.num_qubits, len(bits))
                )

    def add_gate(self, gate, *indices):
        self._check(gate, indices)
        self._ops.append((gate, tuple(indices), None))

    def add_conditional_gate(self, classical_reg, condition, gate, *qubits):
        if not isinstance(classical_reg, ClassicalRegister) or classical_reg not in self._cregs:
            raise ValueError("Condition register must be a ClassicalRegister of this circuit.")
        if isinstance(gate, Gate) and gate.name in ("measure", "barrier", "reset"):
            raise ValueError("Conditional gate cannot be measure, barrier or reset.")
        if isinstance(condition, str):
            condition = int(condition, 2)
        if not isinstance(condition, int) or condition < 0:
            raise ValueError("Condition must be a non-negative integer or a binary string.")
        self._check(gate, qubits)
        self._ops.append((gate, tuple(qubits), (classical_reg, condition)))

    def measure_all(self):
        from .gates import measure
        qubits = [b for r in self._qregs for b in r._bits]
        clbits = [b for r in self._cregs for b in r._bits]
        missing = len(qubits) - len(clbits)
        if missing > 0:
            meas = ClassicalRegister(missing, "meas")
            self.add_register(meas)
            clbits.extend(meas._bits)
        for qb, cb in zip(qubits, clbits):
            self._ops.append((measure, (qb, cb), None))

    def list_gates(self):
        return [n for n in _GATE_PARAMS]

    def draw(self, output="text", filename=None):
        try:
            from qiskit import QuantumCircuit as QC
            drawn = QC.from_qasm_str(self.qasm()).draw(output=output or "text")
            print(drawn)
            return drawn
        except Exception:
            return self.qasm()

    # ---- export ----------------------------------------------------------
    def qasm(self, shots=None):
        """Returns the circuit as OpenQASM 2.0 text."""
        lines = ["OPENQASM 2.0;", 'include "qelib1.inc";']
        for r in self._qregs:
            lines.append("qreg %s[%d];" % (r.prefix, r.size))
        for r in self._cregs:
            lines.append("creg %s[%d];" % (r.prefix, r.size))
        for gate, bits, cond in self._ops:
            prefix = "if(%s==%d) " % (cond[0].prefix, cond[1]) if cond else ""
            if gate.name == "measure":
                lines.append("%smeasure %r -> %r;" % (prefix, bits[0], bits[1]))
                continue
            if gate.name == "barrier" and len(bits) < 2:
                # Observed on the official SDK (qniverse 1.0.6): qc.qasm() raises this error.
                raise ValueError("Barrier requires at least two qubits")
            if gate.name == "barrier":
                # two qubits = start and end of a span (if same register)
                if len(bits) == 2 and bits[0].register is bits[1].register:
                    reg = bits[0].register
                    lo, hi = sorted((bits[0].index, bits[1].index))
                    lines.append("barrier %s;" % ", ".join("%s[%d]" % (reg.prefix, i) for i in range(lo, hi + 1)))
                else:
                    lines.append("barrier %s;" % ", ".join(repr(b) for b in bits))
                continue
            params = "(%s)" % ", ".join(repr(p) for p in gate.params) if gate.params else ""
            lines.append("%s%s%s %s;" % (prefix, gate.name, params, ", ".join(repr(b) for b in bits)))
        return "\n".join(lines) + "\n"
