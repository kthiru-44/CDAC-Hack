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
- **`{rx, rz}`:** $R_y(\gamma) = R_z(\pi/2) \cdot R_x(\gamma) \cdot R_z(-\pi/2)$ (matrix product; applied right to left).
- **`{rx, ry}`:** $R_z(\theta) = R_x(\pi/2) \cdot R_y(\theta) \cdot R_x(-\pi/2)$ (matrix product; applied right to left).
- **`p` or `u1` instead of `rz`:** used as the Z rotation (equal up to global phase).

### 3.2 Two-Qubit and Multi-Qubit Decompositions
- **Toffoli (`ccx`):** Decomposed into 6 $CX$ gates and 9 Clifford+T gates ($H, T, T^\dagger$).
- **Fredkin (`cswap`):** Decomposed into $CX(t_2, t_1) \to CCX(c, t_1, t_2) \to CX(t_2, t_1)$.
- **$SWAP$:** Decomposed into 3 alternating $CX$ gates ($CX(a, b) \to CX(b, a) \to CX(a, b)$).
- **$CZ$:** Decomposed into $H(t) \to CX(c, t) \to H(t)$.
- **$CY$:** Decomposed into $S^\dagger(t) \to CX(c, t) \to S(t)$.
- **Controlled Rotations ($CR_z, CR_x, CR_y$):** Decomposed into 2 $CX$ gates and single-qubit rotations.
- **$CU_3$, $CU_2$:** ABC construction (Nielsen & Chuang, Cor. 4.2): 2 $CX$ plus rotations.
- **$C^3X$, $C^4X$, $C^5X$:** $H \cdot C^nZ \cdot H$ with an exact ancilla-free multi-controlled phase (Barenco et al. 1995, Lemma 7.5).

---

## 4. Run Instructions

### 4.1 In Qniverse JupyterLab (official QSDK)
1. Upload or `git clone` the repository so that `src/qnvkit/` is present.
2. Open `notebooks/c1_demo.ipynb` and run all cells. The first cell prints which QSDK is in use.
3. For the live run (section 6 of the notebook), paste your Qniverse API key into `token`.

### 4.2 Locally (stand-in for the QSDK, no credits used)
The official `Qniverse` package is not on PyPI, so local runs use a stand-in that implements the same documented calls. The script prints which one is active.
```bash
uv venv --python 3.9 .venv39 && uv pip install --python .venv39/bin/python numpy pytest hypothesis
.venv39/bin/python examples/c1_demo.py          # add --live to also go through the job API
.venv39/bin/python -m pytest -q                 # 452 tests
```

### 4.3 Python API
```python
import qnvkit.qsdk_adapter                      # before importing Qniverse
from qnvkit.metrics import profile
from qnvkit.decompose.decomposer import decompose
from Qniverse.QniverseCircuit import *
from Qniverse.gates import *

qc = QniverseCircuit()
q = QuantumRegister(2, 'q')
qc.add_register(q)
qc.add_gate(h, q[0])
qc.add_gate(cx, q[0], q[1])

print(profile(qc).summary())

result = decompose(qc, basis={"rx", "ry", "rz", "cx"})
if result.circuit is not None:                  # a new QniverseCircuit; qc is untouched
    print(result.verified, result.verification_note, result.after.depth)
else:
    print(result.unsupported.summary())
```

---

## 5. Behaviour, Test Evidence and Known Limitations
- **Output is never unverified.** After decomposition the result is compared with the input (full unitary up to global phase for up to 8 qubits, random-state comparison for 9–16). If the check fails, no circuit is returned. Above 16 qubits the check is skipped and the report says so (`verified=False`, with the reason in `verification_note`).
- **Test matrix:** every one of the 37 unitary QSDK gates is decomposed into 8 rotation bases (`{rx,ry,rz,cx}`, `{u3,cx}`, `{rz,ry,cz}`, `{rx,rz,cx}`, `{rx,ry,cx}`, `{p,ry,cx}`, `{u1,rx,cz}`, `{u1,u2,u3,cx}`) and must verify; in 3 discrete bases each gate must either verify or be reported as unsupported (`tests/test_c1_gate_basis_matrix.py`).
- **Global phase:** rewrites are exact up to a global phase, which is unobservable.
- **Discrete bases** (for example `{h, t, cx}`): only exactly reachable gates are converted (Paulis, `s`, `sdg`, `tdg`, `cz`, `swap`, `ccx`, phases that are multiples of π/4, ...). Arbitrary angles and ancilla-free `c3x`–`c5x` are reported as unsupported; no approximation is attempted.
- **Basis without an entangling gate** and a circuit that needs one: reported as unsupported.
- **Non-unitary operations:** `measure`, `reset`, `barrier` are copied in order. For a classically conditioned gate, each emitted gate keeps the same condition; the equivalence check treats conditioned gates as if applied.
- **Not handled:** `add_module` (QFT/IQFT) and `initialize` are untested; an operation whose QASM name is not one of the 40 documented gates is reported as unsupported.
- **No gate merging after decomposition:** adjacent rotations are not combined, so counts are not minimal.
- **Not yet confirmed on the official QSDK:** see `docs/10-qsdk-probe.md` section 1, item 4.
