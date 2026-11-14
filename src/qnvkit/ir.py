"""
qnvkit.ir: Core Immutable Quantum Circuit Intermediate Representation.
Provides pure, non-mutating data structures for all quantum transformations.
"""

from dataclasses import dataclass, field
import hashlib
import json
from typing import Tuple, List, Optional, Dict, Any, Union


@dataclass(frozen=True)
class Register:
    """Represents a quantum or classical register."""
    name: str
    size: int
    is_classical: bool = False

    def __post_init__(self):
        if self.size < 0:
            raise ValueError(f"Register size cannot be negative: {self.size}")


@dataclass(frozen=True)
class Op:
    """Represents a single gate or quantum operation."""
    name: str                           # Lowercase gate name (e.g., 'h', 'cx', 'rx', 'barrier')
    qubits: Tuple[int, ...]             # 0-indexed flat qubit indices (last is target for controlled gates)
    params: Tuple[float, ...] = ()      # Angle parameters in radians
    clbits: Tuple[int, ...] = ()        # Classical bit indices for measurement
    condition: Optional[Tuple[str, int]] = None  # (creg_name, expected_val)

    def __post_init__(self):
        # Normalize name to lowercase
        object.__setattr__(self, "name", self.name.lower())


@dataclass(frozen=True)
class CircuitIR:
    """
    Immutable Quantum Circuit IR.
    Guarantees that input circuits can never be mutated by decomposition or optimization passes.
    """
    num_qubits: int
    num_clbits: int
    qregs: Tuple[Register, ...]
    cregs: Tuple[Register, ...]
    ops: Tuple[Op, ...]

    def __post_init__(self):
        if self.num_qubits < 0 or self.num_clbits < 0:
            raise ValueError("Qubit and classical bit counts must be non-negative.")

    def copy(self) -> 'CircuitIR':
        """Frozen dataclass is inherently immutable; copy returns self."""
        return self

    def fingerprint(self) -> str:
        """Computes a SHA-256 fingerprint for immutability verification."""
        data = {
            "num_qubits": self.num_qubits,
            "num_clbits": self.num_clbits,
            "qregs": [(r.name, r.size) for r in self.qregs],
            "cregs": [(r.name, r.size) for r in self.cregs],
            "ops": [
                (op.name, list(op.qubits), [round(p, 10) for p in op.params], list(op.clbits), op.condition)
                for op in self.ops
            ]
        }
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def get_qubit_reg_map(self) -> Dict[int, Tuple[str, int]]:
        """Maps flat qubit index -> (register_name, register_offset)."""
        mapping = {}
        curr = 0
        for reg in self.qregs:
            for i in range(reg.size):
                mapping[curr + i] = (reg.name, i)
            curr += reg.size
        return mapping

    def get_clbit_reg_map(self) -> Dict[int, Tuple[str, int]]:
        """Maps flat classical bit index -> (register_name, register_offset)."""
        mapping = {}
        curr = 0
        for reg in self.cregs:
            for i in range(reg.size):
                mapping[curr + i] = (reg.name, i)
            curr += reg.size
        return mapping

    def to_qasm2(self) -> str:
        """Emits valid OpenQASM 2.0 text for this circuit."""
        lines = [
            'OPENQASM 2.0;',
            'include "qelib1.inc";',
        ]
        for reg in self.qregs:
            lines.append(f"qreg {reg.name}[{reg.size}];")
        for reg in self.cregs:
            lines.append(f"creg {reg.name}[{reg.size}];")

        q_map = self.get_qubit_reg_map()
        c_map = self.get_clbit_reg_map()

        for op in self.ops:
            q_args = []
            for q in op.qubits:
                r_name, r_idx = q_map.get(q, ('q', q))
                q_args.append(f"{r_name}[{r_idx}]")

            prefix = ""
            if op.condition:
                cname, cval = op.condition
                prefix = f"if({cname}=={cval}) "

            if op.name == "barrier":
                lines.append(f"{prefix}barrier {', '.join(q_args)};")
            elif op.name == "reset":
                for qa in q_args:
                    lines.append(f"{prefix}reset {qa};")
            elif op.name == "measure":
                for q_idx, c_idx in zip(op.qubits, op.clbits):
                    qr_name, qr_i = q_map.get(q_idx, ('q', q_idx))
                    cr_name, cr_i = c_map.get(c_idx, ('c', c_idx))
                    lines.append(f"{prefix}measure {qr_name}[{qr_i}] -> {cr_name}[{cr_i}];")
            else:
                # Gate with optional parameters
                param_str = ""
                if op.params:
                    param_str = f"({', '.join(f'{p:.10g}' for p in op.params)})"
                lines.append(f"{prefix}{op.name}{param_str} {', '.join(q_args)};")

        return "\n".join(lines) + "\n"
