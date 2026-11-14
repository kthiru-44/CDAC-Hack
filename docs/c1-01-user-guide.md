# QC-C1-01 — Circuit Profiling and Limited Basis-Gate Decomposition
**PESU – C-DAC Quantum Hackathon User Guide & Specification**

---

## 1. Problem Overview
- **Problem ID:** QC-C1-01
- **Class:** Class I (Checkpoint 1, ~Hour 3)
- **Objective:** Implement a QSDK-compatible circuit analyzer and basis decomposer that generates a structured profile report and produces a decomposed `QniverseCircuit` where all non-basis gates are converted into a user-selected basis gate set, with strict non-mutation of inputs, provable mathematical equivalence, and explicit error reporting for unsupported gates.

---

## 2. Metric Definitions & Earliest-Available-Layer Schedule

### 2.1 Scheduled Depth ($D$)
Depth is calculated using an **earliest-available-layer schedule**:
1. For an $n$-qubit quantum circuit, maintain an array of layer availability: $L[q]$ for $q \in \{0, \dots, n-1\}$, initialized to 0.
2. Maintain classical bit layers: $L_{cl}[c]$ for $c \in \{0, \dots, m-1\}$, initialized to 0.
3. For each unitary gate $op$ acting on qubits $Q_{op}$:
   $$\text{Layer}_{\text{start}} = \max_{q \in Q_{op}}(L[q])$$
   $$\forall q \in Q_{op}, \quad L[q] \leftarrow \text{Layer}_{\text{start}} + 1$$
4. **Operations on disjoint qubits execute in parallel**: If gate $A$ acts on $q_0$ and gate $B$ acts on $q_1$, both occupy Layer 1 simultaneously.
5. **Barriers (Synchronization boundaries):**
   A barrier on qubits $Q_{bar}$ aligns all spanned wires to the latest current layer without incrementing depth:
   $$L_{\text{sync}} = \max_{q \in Q_{bar}}(L[q])$$
   $$\forall q \in Q_{bar}, \quad L[q] \leftarrow L_{\text{sync}}$$
6. **Measurements:**
   A measurement touching qubit $q$ and classical bit $c$ takes 1 layer:
   $$L_{\text{start}} = \max(L[q], L_{cl}[c])$$
   $$L[q] \leftarrow L_{\text{start}} + 1, \quad L_{cl}[c] \leftarrow L_{\text{start}} + 1$$
7. **Total Depth:**
   $$D = \max_{q \in \{0, \dots, n-1\}} L[q]$$

### 2.2 Gate Counting
- **Total Gates:** Sum of all unitary operations (1-qubit, 2-qubit, multi-qubit).
- **Gate Counts by Type:** Dictionary mapping each gate name to its frequency.
- **Active Qubits Used:** Unique set of qubits that participate in at least one operation.
- **Non-Unitary Counts:** Explicit counts for `measure`, `reset`, and `barrier`.

---

## 3. Basis Gate Decomposition Mechanics

### 3.1 1-Qubit Euler Z-Y-Z Synthesis
Any single-qubit unitary $U \in U(2)$ can be expressed as:
$$U = e^{i\alpha} R_z(\beta) R_y(\gamma) R_z(\delta)$$
Where:
- $\gamma = 2 \arccos(|u_{00}|)$
- For diagonal unitaries ($\gamma \approx 0$): $\beta = 0, \delta = 2 \arg(u_{11})$
- For anti-diagonal unitaries ($\gamma \approx \pi$): $\beta = 2 \arg(u_{10}), \delta = 0$
- In general:
  $$\beta + \delta = 2 \arg(u_{11}), \quad \beta - \delta = 2 \arg(u_{10})$$

Depending on the chosen basis:
- **`{u3}`:** Emits a single $U_3(\gamma, \beta, \delta)$ gate.
- **`{rx, ry, rz}`:** Emits $R_z(\delta) \cdot R_y(\gamma) \cdot R_z(\beta)$.
- **`{rx, rz}`:** Decomposes $R_y(\gamma) = R_z(\pi/2) \cdot R_x(\gamma) \cdot R_z(-\pi/2)$.
- **`{rx, ry}`:** Decomposes $R_z(\theta) = R_x(\pi/2) \cdot R_y(\theta) \cdot R_x(-\pi/2)$.

### 3.2 Two-Qubit and Multi-Qubit Decompositions
- **Toffoli (`ccx`):** Decomposed into 6 $CX$ gates and 9 Clifford+T gates ($H, T, T^\dagger$).
- **Fredkin (`cswap`):** Decomposed into $CX(t_2, t_1) \to CCX(c, t_1, t_2) \to CX(t_2, t_1)$.
- **$SWAP$:** Decomposed into 3 alternating $CX$ gates ($CX(a, b) \to CX(b, a) \to CX(a, b)$).
- **$CZ$:** Decomposed into $H(t) \to CX(c, t) \to H(t)$.
- **$CY$:** Decomposed into $S^\dagger(t) \to CX(c, t) \to S(t)$.
- **Controlled Rotations ($CR_z, CR_x, CR_y$):** Decomposed into 2 $CX$ gates and single-qubit rotations.

---

## 4. Run Instructions

### 4.1 Running the Demo Script
```bash
# Run with Python 3.9 in the virtual environment
.venv39/bin/python examples/c1_demo.py
```

### 4.2 Running the Unit and Fuzzing Tests
```bash
# Run all tests with short failure tracebacks
.venv39/bin/pytest -q --tb=short tests/
```

### 4.3 Python API Usage
```python
from qnvkit.metrics import profile
from qnvkit.decompose.decomposer import decompose
from Qniverse.QniverseCircuit import QniverseCircuit, QuantumRegister

# 1. Build circuit
qc = QniverseCircuit()
qc.add_register(QuantumRegister(2, 'q'))
qc.add_gate("h", 0)
qc.add_gate("cx", 0, 1)

# 2. Profile circuit
report = profile(qc)
print(report.summary())

# 3. Decompose into basis
result = decompose(qc, basis={"rx", "ry", "rz", "cx"})
if result.circuit:
    print("Decomposed successfully! Verified:", result.verified)
    print("New Depth:", result.after.depth)
else:
    print("Unsupported operations:", result.unsupported.summary())
```

---

## 5. Known Limitations
1. **Discrete Basis Approximation:** When decomposing into discrete Clifford+T bases (e.g. `{h, t, cx}`), arbitrary continuous rotation angles (like $R_x(0.35)$) cannot be expressed exactly without approximate Solovay-Kitaev algorithms. In accordance with requirement D.6, such operations are safely flagged in an `UnsupportedReport`, returning `circuit = None` rather than emitting an invalid circuit.
2. **Entangling Gate Requirement:** If a circuit contains entangling gates (2-qubit or multi-qubit operations) and the user selects a basis set containing only 1-qubit gates (e.g., `{rx, ry, rz}`), decomposition is mathematically impossible. The engine safely detects this and returns an explicit `UnsupportedReport`.
