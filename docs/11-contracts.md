# 11 — Fixed Interface Contracts (qnvkit)

**Package:** `src/qnvkit`  
**Purpose:** Deterministic API signatures across parallel development modules.  
**Rule:** No agent or subagent may alter these function signatures or return dataclass schemas.  

---

## 1. Core Data Structures (`qnvkit.ir`, `qnvkit.report`)

### 1.1 Operation Representation
```python
from dataclasses import dataclass, field
from typing import Tuple, List, Optional, Dict, Any, Union, Set

@dataclass(frozen=True)
class Register:
    name: str
    size: int
    is_classical: bool = False

@dataclass(frozen=True)
class Op:
    name: str                           # Lowercase gate name from the 40 QSDK gates
    qubits: Tuple[int, ...]             # 0-indexed qubit indices (last is target for multi-q controlled gates)
    params: Tuple[float, ...] = ()      # Angle parameters in radians (e.g., rx(theta))
    clbits: Tuple[int, ...] = ()        # Classical bit indices for measurement
    condition: Optional[Tuple[str, int]] = None  # (creg_name, integer_value) for classical conditionals

@dataclass(frozen=True)
class CircuitIR:
    num_qubits: int
    num_clbits: int
    qregs: Tuple[Register, ...]
    cregs: Tuple[Register, ...]
    ops: Tuple[Op, ...]
    
    def copy(self) -> 'CircuitIR':
        return self  # Immutable frozen dataclass
    
    def to_qasm2(self) -> str:
        """Returns valid OpenQASM 2.0 text."""
        ...
```

### 1.2 Metric & Report Structures (`qnvkit.report`)
```python
@dataclass(frozen=True)
class ProfileReport:
    total_gates: int
    gate_counts: Dict[str, int]
    qubits_declared: int
    qubits_used: int
    single_qubit_gates: int
    two_qubit_gates: int
    multi_qubit_gates: int              # Gates on >2 qubits (ccx, cswap, c3x, etc.)
    depth: int                          # Earliest-available-layer scheduled depth
    measurements: int
    resets: int
    barriers: int

    def to_dict(self) -> Dict[str, Any]:
        ...

@dataclass(frozen=True)
class UnsupportedReport:
    unsupported_gates: List[Dict[str, Any]]  # List of {gate: name, qubits: [...], reason: str}
    is_valid: bool = False

@dataclass(frozen=True)
class DecomposeResult:
    circuit: Optional[Any]              # Decomposed QniverseCircuit (or None if unsupported)
    ir: Optional[CircuitIR]             # Decomposed CircuitIR
    before: ProfileReport
    after: Optional[ProfileReport]
    unsupported: Optional[UnsupportedReport]
    verified: bool                      # Unitary / statevector equivalence confirmed

@dataclass(frozen=True)
class OptimizeResult:
    circuit: Any                        # Optimized QniverseCircuit
    ir: CircuitIR                       # Optimized CircuitIR
    before: ProfileReport
    after: ProfileReport
    passes_applied: List[str]
    reduction_percentage: float
    warnings: List[str]

@dataclass(frozen=True)
class TranspilerReport:
    target: str                         # "qiskit" | "cirq" | "cudaq"
    target_version: str
    status: str                         # "SUCCESS" | "WARNING" | "ERROR"
    warnings: List[str]
    unsupported_constructs: List[Dict[str, Any]]
```

---

## 2. Shared Core Module Functions

### 2.1 Adapter Bridge (`qnvkit.qsdk_adapter`)
```python
def from_qniverse(qc: Any) -> CircuitIR:
    """
    Ingests a QniverseCircuit via qc.qasm() + QASM 2 parser.
    Non-mutating: leaves qc completely unchanged.
    """
    ...

def to_qniverse(ir: CircuitIR) -> Any:
    """
    Constructs and returns a fresh QniverseCircuit from CircuitIR
    using documented add_register, add_gate, add_conditional_gate calls.
    """
    ...
```

### 2.2 Metrics & Depth (`qnvkit.metrics`)
```python
def profile(circuit: Union[Any, CircuitIR]) -> ProfileReport:
    """
    Calculates exact gate counts and scheduled depth.
    Depth rules:
    - Each unitary operation occupies 1 layer on all operand qubits.
    - Measure and reset occupy 1 layer.
    - Barrier occupies 0 layers but aligns the current layer across all spanned wires.
    """
    ...
```

### 2.3 Numerical Simulation & Equivalence (`qnvkit.sim`)
```python
def compute_unitary(ir: CircuitIR) -> np.ndarray:
    """Computes exact 2^n x 2^n unitary matrix using NumPy."""
    ...

def check_unitary_equivalence(ir_a: CircuitIR, ir_b: CircuitIR, tol: float = 1e-6) -> bool:
    """
    Checks if U_a and U_b are equal up to a global phase:
    |Tr(U_a^dagger @ U_b)| / 2^n >= 1 - tol
    """
    ...

def compute_statevector(ir: CircuitIR) -> np.ndarray:
    """Computes final statevector starting from |0...0>."""
    ...

def check_statevector_fidelity(ir_a: CircuitIR, ir_b: CircuitIR, tol: float = 1e-6) -> bool:
    """Checks |<psi_a | psi_b>|^2 >= 1 - tol."""
    ...

def total_variation_distance(dist_a: Dict[str, float], dist_b: Dict[str, float]) -> float:
    """Computes 0.5 * sum(|P_a(x) - P_b(x)|)."""
    ...
```

---

## 3. Problem APIs

### 3.1 Problem 1 — QC-C1-01 (`qnvkit.decompose`)
```python
def decompose(
    circuit: Union[Any, CircuitIR],
    basis: Union[Set[str], List[str]]
) -> DecomposeResult:
    """
    Accepts QniverseCircuit or CircuitIR and a basis gate set.
    Rejects:
    - None or invalid circuit input.
    - Empty basis set.
    - Gate names not in the 40 documented QSDK gates.
    Returns DecomposeResult.
    If circuit contains gates that cannot be decomposed into basis:
    - circuit is None
    - unsupported contains structured details
    - never silently emits an invalid circuit.
    """
    ...
```

### 3.2 Problem 2 — QC-C2-03 (`qnvkit.transpile`)
```python
def transpile(
    source: Union[str, Path],
    targets: Tuple[str, ...] = ("qiskit", "cirq", "cudaq"),
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Dict[str, Any]]:
    """
    Transpiles OpenQASM 3.0 source string or file to target framework scripts.
    Returns: {
        "qiskit": {"code": str, "report": TranspilerReport},
        "cirq":   {"code": str, "report": TranspilerReport},
        "cudaq":  {"code": str, "report": TranspilerReport}
    }
    """
    ...
```

### 3.3 Problem 3 — QC-C3-03 (`qnvkit.optimize`)
```python
def optimize(
    circuit: Union[Any, CircuitIR],
    passes: Optional[List[str]] = None
) -> OptimizeResult:
    """
    Optimizes a QniverseCircuit or CircuitIR using safe local rewrite passes.
    Default passes: ["remove_identity", "cancel_self_inverse", "cancel_cx"]
    Adjacency rule:
    - Two gates cancel ONLY if consecutive on all shared wires.
    - Barriers, measurements, resets, or intervening non-commuting gates strictly block rewrites.
    """
    ...
```
