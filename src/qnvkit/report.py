"""
qnvkit.report: Standardized structured report dataclasses for Qniverse hackathon modules.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Tuple


@dataclass(frozen=True)
class ProfileReport:
    """Structured metrics for a quantum circuit."""
    total_gates: int
    gate_counts: Dict[str, int]
    qubits_declared: int
    qubits_used: int
    single_qubit_gates: int
    two_qubit_gates: int
    multi_qubit_gates: int  # >2 qubits (e.g. ccx, cswap, c3x, c4x, c5x)
    depth: int              # Earliest-available-layer scheduled depth
    measurements: int = 0
    resets: int = 0
    barriers: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def summary(self) -> str:
        lines = [
            f"--- Circuit Profile Report ---",
            f"Total Gates: {self.total_gates} | Depth: {self.depth}",
            f"Qubits (Declared / Active): {self.qubits_declared} / {self.qubits_used}",
            f"Gates by Arity: 1Q={self.single_qubit_gates}, 2Q={self.two_qubit_gates}, MultiQ={self.multi_qubit_gates}",
            f"Non-Unitary: Meas={self.measurements}, Reset={self.resets}, Barrier={self.barriers}",
            f"Gate Breakdown: {self.gate_counts}",
        ]
        return "\n".join(lines)


@dataclass(frozen=True)
class UnsupportedReport:
    """Explicit report for operations that cannot be represented or decomposed into the target basis."""
    unsupported_gates: Tuple[Dict[str, Any], ...]
    is_valid: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "unsupported_gates": list(self.unsupported_gates),
        }

    def summary(self) -> str:
        if not self.unsupported_gates:
            return "All operations supported."
        lines = ["--- Unsupported Operations Report ---"]
        for item in self.unsupported_gates:
            lines.append(f"  • Gate '{item.get('gate')}' on qubits {item.get('qubits')}: {item.get('reason')}")
        return "\n".join(lines)


@dataclass(frozen=True)
class DecomposeResult:
    """Result of basis gate decomposition (QC-C1-01)."""
    circuit: Optional[Any]  # QniverseCircuit (or None if unsupported)
    ir: Optional[Any]       # CircuitIR
    before: ProfileReport
    after: Optional[ProfileReport]
    unsupported: Optional[UnsupportedReport]
    verified: bool = False  # True if unitary or statevector equivalence verified

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.circuit is not None,
            "verified": self.verified,
            "before": self.before.to_dict(),
            "after": self.after.to_dict() if self.after else None,
            "unsupported": self.unsupported.to_dict() if self.unsupported else None,
        }

    def summary(self) -> str:
        status = "SUCCESS" if self.circuit is not None else "FAILED (Unsupported Operations)"
        lines = [
            f"==========================================",
            f"Basis Decomposition: {status}",
            f"Equivalence Verified: {self.verified}",
            f"--- Metrics Before Decomposition ---",
            self.before.summary(),
        ]
        if self.after:
            lines.extend([
                f"--- Metrics After Decomposition ---",
                self.after.summary(),
            ])
        if self.unsupported and self.unsupported.unsupported_gates:
            lines.append(self.unsupported.summary())
        lines.append(f"==========================================")
        return "\n".join(lines)


@dataclass(frozen=True)
class OptimizeResult:
    """Result of circuit optimization (QC-C3-03)."""
    circuit: Any
    ir: Any
    before: ProfileReport
    after: ProfileReport
    passes_applied: Tuple[str, ...]
    reduction_percentage: float
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "before": self.before.to_dict(),
            "after": self.after.to_dict(),
            "passes_applied": list(self.passes_applied),
            "reduction_percentage": self.reduction_percentage,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class TranspilerReport:
    """Result of OpenQASM 3.0 transpilation (QC-C2-03)."""
    target: str
    target_version: str
    status: str
    warnings: Tuple[str, ...] = ()
    unsupported_constructs: Tuple[Dict[str, Any], ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "target_version": self.target_version,
            "status": self.status,
            "warnings": list(self.warnings),
            "unsupported_constructs": list(self.unsupported_constructs),
        }
