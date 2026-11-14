# QC-C3-03 — Quantum Circuit Optimization Using QSDK
**PESU – C-DAC Quantum Hackathon User Guide & Specification**

---

## 1. Problem Overview
- **Problem ID:** QC-03-03
- **Class:** Class III (Final Checkpoint — 50% of class evaluation)
- **Objective:** Implement a safe, local rewrite-rule quantum circuit optimizer that accepts a `QniverseCircuit`, applies a documented set of rule passes, and produces a new optimized `QniverseCircuit` with lower gate count and scheduled depth.
- **Safety Invariant:** Must preserve exact circuit semantics ($|\text{Tr}(U_{\text{orig}}^\dagger U_{\text{opt}})| / 2^n \equiv 1.0$), respect timing barriers and measurements, never mutate inputs, and avoid introducing unnecessary gates.

---

## 2. Theoretical Mechanics & The Causal Wire Model

### 2.1 Why Simple Pattern Matching Fails
A naive string- or list-replacement approach searches for adjacent gates $G_1$ and $G_2$. However, in a quantum circuit:
- If a gate executes on another wire, the two gates might still be adjacent.
- If a gate, barrier, measurement, or reset occurs on the **same wire**, the two gates are **not** adjacent, and cancelling them corrupts the quantum computation!

### 2.2 The Causal Wire Adjacency Graph
In `qnvkit.optimize`, we maintain an ordered sequence of operations for every qubit wire:
$$\text{wire\_ops}[q] = [op_1, op_2, \dots, op_m]$$
Two operations $A$ and $B$ are **strictly causally adjacent** if and only if:
$$\forall q \in \text{wires}(A), \quad \text{next\_op}(q, A) = B$$

### 2.3 Preconditions & Safety Guards
Cancellation is **strictly prevented** if:
1. **Barrier Guard:** A `barrier` lies between $A$ and $B$ on any shared wire. Barriers act as immutable synchronization boundaries.
2. **Measurement & Reset Guards:** Non-unitary operations freeze or collapse state; rewrites across them are strictly disallowed.
3. **Intervening Gates:** Any non-commuting gate on any of the operand wires invalidates the rewrite.
4. **Classical Conditionals:** Conditioned gates (`if(c==k)`) are never rewritten.

---

## 3. Supported Rewrite Passes

### 3.1 Mandatory Passes
| Pass Name | Rule | Transformation |
|---|---|---|
| `remove_identity` | Eliminate explicit identity and zero rotations | $I \to \emptyset$, $R_x(0) \to \emptyset$, $R_z(2\pi) \to \emptyset$, $U_3(0,0,0) \to \emptyset$ |
| `cancel_self_inverse` | Eliminate adjacent 1Q self-inverse pairs | $X \cdot X \to \emptyset$, $Y \cdot Y \to \emptyset$, $Z \cdot Z \to \emptyset$, $H \cdot H \to \emptyset$ |
| `cancel_cx` | Eliminate adjacent identical CNOT pairs | $CX(c, t) \cdot CX(c, t) \to \emptyset$ (same control & target) |

### 3.2 Opt-in Extra Passes
| Pass Name | Rule | Transformation |
|---|---|---|
| `cancel_extended_self_inverse` | Multi-qubit self-inverse gates | $CZ \cdot CZ \to \emptyset$, $SWAP \cdot SWAP \to \emptyset$, $CCX \cdot CCX \to \emptyset$ |
| `cancel_inverse_pairs` | Adjoint gate cancellation | $S \cdot S^\dagger \to \emptyset$, $T \cdot T^\dagger \to \emptyset$, $CS \cdot CS^\dagger \to \emptyset$ |
| `merge_rotations` | Continuous rotation combination | $R_z(\alpha) \cdot R_z(\beta) \to R_z(\alpha+\beta)$; if $\alpha+\beta \equiv 0$, gate is removed |

---

## 4. Run Instructions

### 4.1 Running the Standalone Demo Script
```bash
# Execute standalone verification demo (Python 3.9)
.venv39/bin/python examples/c3_demo.py
```

### 4.2 Running the Full Test Suite
```bash
# Run C3 tests
.venv39/bin/pytest -q --tb=short tests/test_c3_optimizer.py tests/test_c3_fuzz.py

# Run all hackathon tests across C1, C2, C3
.venv39/bin/pytest -q --tb=short
```

### 4.3 Python API Usage
```python
from qnvkit.optimize import optimize
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister
from Qniverse.gates import h, x, cx

qc = QniverseCircuit()
q = QuantumRegister(2, "q")
qc.add_register(q)

# Redundant sequence
qc.add_gate(h, q[0])
qc.add_gate(h, q[0])
qc.add_gate(cx, q[0], q[1])
qc.add_gate(cx, q[0], q[1])

# Optimize
result = optimize(qc, fixed_point=True)
print(f"Reduction: {result.reduction_percentage}%")
print(f"Gates before: {result.before.total_gates} -> after: {result.after.total_gates}")
```

---

## 5. Known Limitations
1. **Peephole Commutation Limits:** The optimizer prioritizes **absolute provable safety**. Non-commuting gates on separate axes (e.g. $X$ followed by $Z$) do not commute and are strictly preserved.
2. **Dynamic / Classical Circuits:** Circuits containing dynamic measurements conditioning subsequent gates are safely bypassed without modification to prevent altering real-time classical feed-forward behavior.
