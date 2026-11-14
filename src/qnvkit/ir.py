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
class QubitRef:
    """Reference to a specific qubit in a quantum register."""
    register: str
    index: int

    def __repr__(self) -> str:
        return f"{self.register}[{self.index}]"


@dataclass(frozen=True)
class ClbitRef:
    """Reference to a specific classical bit in a classical register."""
    register: str
    index: int

    def __repr__(self) -> str:
        return f"{self.register}[{self.index}]"


@dataclass(frozen=True)
class Condition:
    """Classical control condition (e.g. c == 1 or c[0] == 1)."""
    register: str
    value: int
    index: Optional[int] = None
    op: str = "=="

    def __repr__(self) -> str:
        target = f"{self.register}[{self.index}]" if self.index is not None else self.register
        return f"{target} {self.op} {self.value}"

    def to_tuple(self) -> Tuple[str, int]:
        return (self.register, self.value)


@dataclass(frozen=True)
class Op:
    """Represents a single gate or quantum operation."""
    name: str                           # Lowercase gate name (e.g., 'h', 'cx', 'rx', 'barrier')
    qubits: Tuple[int, ...]             # 0-indexed flat qubit indices (last is target for controlled gates)
    params: Tuple[float, ...] = ()      # Angle parameters in radians
    clbits: Tuple[int, ...] = ()        # Classical bit indices for measurement
    condition: Optional[Tuple[str, int]] = None  # (creg_name, expected_val)
    line: Optional[int] = None
    col: Optional[int] = None

    def __post_init__(self):
        # Normalize name to lowercase
        object.__setattr__(self, "name", self.name.lower())

    def is_gate(self) -> bool:
        return self.name not in ("barrier", "reset", "measure")

    def is_measurement(self) -> bool:
        return self.name == "measure"

    def is_barrier(self) -> bool:
        return self.name == "barrier"

    def is_reset(self) -> bool:
        return self.name == "reset"


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
    name: str = "circuit"

    def __post_init__(self):
        if self.num_qubits < 0 or self.num_clbits < 0:
            raise ValueError("Qubit and classical bit counts must be non-negative.")

    def copy(self) -> 'CircuitIR':
        """Frozen dataclass is inherently immutable; copy returns self."""
        return self

    def __len__(self) -> int:
        return len(self.ops)

    def __iter__(self):
        return iter(self.ops)

    @property
    def qreg_dict(self) -> Dict[str, int]:
        return {r.name: r.size for r in self.qregs}

    @property
    def creg_dict(self) -> Dict[str, int]:
        return {r.name: r.size for r in self.cregs}

    def qubit_to_flat_index(self, q: Union[Tuple[str, int], QubitRef, str], idx: Optional[int] = None) -> int:
        if isinstance(q, QubitRef):
            r_name, r_idx = q.register, q.index
        elif isinstance(q, tuple):
            r_name, r_idx = q[0], q[1]
        elif isinstance(q, str) and idx is not None:
            r_name, r_idx = q, idx
        else:
            raise ValueError(f"Invalid qubit argument: {q}")

        offset = 0
        for reg in self.qregs:
            if reg.name == r_name:
                if 0 <= r_idx < reg.size:
                    return offset + r_idx
                raise IndexError(f"Index {r_idx} out of bounds for register '{r_name}' of size {reg.size}")
            offset += reg.size
        raise KeyError(f"Quantum register '{r_name}' not found")

    def flat_index_to_qubit(self, flat_idx: int) -> Tuple[str, int]:
        q_map = self.get_qubit_reg_map()
        if flat_idx not in q_map:
            raise IndexError(f"Flat qubit index {flat_idx} out of range (0..{self.num_qubits-1})")
        return q_map[flat_idx]

    def clbit_to_flat_index(self, c: Union[Tuple[str, int], ClbitRef, str], idx: Optional[int] = None) -> int:
        if isinstance(c, ClbitRef):
            r_name, r_idx = c.register, c.index
        elif isinstance(c, tuple):
            r_name, r_idx = c[0], c[1]
        elif isinstance(c, str) and idx is not None:
            r_name, r_idx = c, idx
        else:
            raise ValueError(f"Invalid classical bit argument: {c}")

        offset = 0
        for reg in self.cregs:
            if reg.name == r_name:
                if 0 <= r_idx < reg.size:
                    return offset + r_idx
                raise IndexError(f"Index {r_idx} out of bounds for classical register '{r_name}' of size {reg.size}")
            offset += reg.size
        raise KeyError(f"Classical register '{r_name}' not found")

    def flat_index_to_clbit(self, flat_idx: int) -> Tuple[str, int]:
        c_map = self.get_clbit_reg_map()
        if flat_idx not in c_map:
            raise IndexError(f"Flat clbit index {flat_idx} out of range (0..{self.num_clbits-1})")
        return c_map[flat_idx]


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
