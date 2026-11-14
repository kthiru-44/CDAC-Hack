"""
qnvkit.shim.Qniverse: High-fidelity drop-in mock of the C-DAC QSDK for local development.
Mirrors the exact documented classes and methods of Qniverse.
"""

from typing import List, Tuple, Dict, Any, Optional
import math


class QuantumRegister:
    def __init__(self, size: int, name: str = 'q'):
        self.size = size
        self.name = name

    def __repr__(self):
        return f"QuantumRegister({self.size}, '{self.name}')"


class ClassicalRegister:
    def __init__(self, size: int, name: str = 'c'):
        self.size = size
        self.name = name

    def __repr__(self):
        return f"ClassicalRegister({self.size}, '{self.name}')"


class QniverseCircuit:
    def __init__(self):
        self._qregs: List[QuantumRegister] = []
        self._cregs: List[ClassicalRegister] = []
        self._ops: List[Dict[str, Any]] = []

    def add_register(self, reg: Any):
        if isinstance(reg, QuantumRegister):
            self._qregs.append(reg)
        elif isinstance(reg, ClassicalRegister):
            self._cregs.append(reg)
        else:
            raise TypeError(f"Unknown register type: {type(reg)}")

    def add_gate(self, gate: str, *qubits, params=None):
        self._ops.append({
            "type": "gate",
            "name": gate.lower(),
            "qubits": list(qubits),
            "params": list(params) if params else [],
            "condition": None,
        })

    def add_conditional_gate(self, creg: Any, value: int, gate: str, *qubits):
        cname = creg.name if hasattr(creg, 'name') else str(creg)
        self._ops.append({
            "type": "gate",
            "name": gate.lower(),
            "qubits": list(qubits),
            "params": [],
            "condition": (cname, value),
        })

    def measure_all(self):
        # Create classical register if needed
        total_q = sum(r.size for r in self._qregs)
        if not self._cregs:
            self._cregs.append(ClassicalRegister(total_q, 'c'))
        for q in range(total_q):
            self._ops.append({
                "type": "measure",
                "name": "measure",
                "qubit": q,
                "clbit": q,
                "condition": None,
            })

    def list_gates(self) -> List[str]:
        return [op["name"] for op in self._ops]

    def get_registers(self) -> Tuple[List[QuantumRegister], List[ClassicalRegister]]:
        return list(self._qregs), list(self._cregs)

    def draw(self) -> str:
        s = f"QniverseCircuit: {sum(r.size for r in self._qregs)} qubits, {len(self._ops)} gates\n"
        for op in self._ops:
            s += f"  {op['name']} {op.get('qubits', [])}\n"
        return s

    def qasm(self) -> str:
        """Exports to OpenQASM 2.0 text."""
        lines = [
            'OPENQASM 2.0;',
            'include "qelib1.inc";',
        ]
        for qr in self._qregs:
            lines.append(f"qreg {qr.name}[{qr.size}];")
        for cr in self._cregs:
            lines.append(f"creg {cr.name}[{cr.size}];")

        # Wire mapping
        q_map = {}
        curr = 0
        for qr in self._qregs:
            for i in range(qr.size):
                q_map[curr + i] = (qr.name, i)
            curr += qr.size

        c_map = {}
        curr = 0
        for cr in self._cregs:
            for i in range(cr.size):
                c_map[curr + i] = (cr.name, i)
            curr += cr.size

        for op in self._ops:
            prefix = ""
            if op.get("condition"):
                cname, cval = op["condition"]
                prefix = f"if({cname}=={cval}) "

            if op["type"] == "measure":
                q_idx = op["qubit"]
                c_idx = op["clbit"]
                qr_name, qr_i = q_map.get(q_idx, ('q', q_idx))
                cr_name, cr_i = c_map.get(c_idx, ('c', c_idx))
                lines.append(f"{prefix}measure {qr_name}[{qr_i}] -> {cr_name}[{cr_i}];")
            elif op["name"] == "barrier":
                args = [f"{q_map.get(q, ('q', q))[0]}[{q_map.get(q, ('q', q))[1]}]" for q in op["qubits"]]
                lines.append(f"{prefix}barrier {', '.join(args)};")
            elif op["name"] == "reset":
                for q in op["qubits"]:
                    qr_name, qr_i = q_map.get(q, ('q', q))
                    lines.append(f"{prefix}reset {qr_name}[{qr_i}];")
            else:
                args = [f"{q_map.get(q, ('q', q))[0]}[{q_map.get(q, ('q', q))[1]}]" for q in op["qubits"]]
                params_str = ""
                if op.get("params"):
                    params_str = f"({', '.join(f'{p:.10g}' for p in op['params'])})"
                lines.append(f"{prefix}{op['name']}{params_str} {', '.join(args)};")

        return "\n".join(lines) + "\n"
