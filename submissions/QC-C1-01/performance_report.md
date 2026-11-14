# QC-C1-01 — Performance Evaluation Report (Deliverable #3)

> Mandated by PESU – C-DAC Hackathon Rules §6.3: Execution time and memory requirements, computational complexity, circuit depth and gate count trade-offs, and empirical verification.

---

## 1. Experimental Setup & Environment

All empirical benchmarks were conducted within the standardized Qniverse-compliant runtime environment:
- **Host OS:** Linux x86_64 (Kernel 6.17)
- **Primary Runtime:** Python 3.9.25 (configured to mirror the C-DAC Qniverse JupyterLab environment)
- **Secondary Verification Runtime:** Python 3.12 (modern virtual environment)
- **Target Frameworks & Libraries:**
  - NumPy: `1.26.4`
  - Qiskit: `1.1.2`
  - QSDK: `Qniverse 1.6+` (via `qnvkit.qsdk_adapter` and local stand-in `qnvkit.shim.Qniverse`)
  - Testing & Verification Engine: `pytest 8.3.4`, `hypothesis 6.115.3`
- **Memory Footprint:** Baseline package memory overhead is $\approx 35\text{ MB}$ RSS. Memory scaling during compilation, profiling, and optimization is strictly linear $O(g + q)$ in gate count $g$ and qubit count $q$. Exponential memory $O(2^n)$ is only invoked during local unitary simulation equivalence checks for $n \le 10$ qubits.

---


## 2. Problem QC-C1-01: Circuit Profiling and Basis Decomposition

### 2.1 Empirical Benchmarks across Standard Bases

Decomposition was evaluated across multiple algorithmic circuits and target basis gate sets:
- **Basis A:** Standard Rotation Basis `{rx, ry, rz, cx}`
- **Basis B:** IBM/Qiskit Universal Basis `{u3, cx}`
- **Basis C:** Rigetti / CZ Basis `{cz, ry, rz}`
- **Basis D:** Two-Axis Rotation Basis `{rx, rz, cx}`

| Circuit | Target Basis | Gates Before → After | Depth Before → After | Runtime | Unitary Equivalence |
|---|---|---|---|---|---|
| **Bell State (2Q)** | `{rx, ry, rz, cx}` | 2 → 3 | 2 → 3 | 0.52 ms | **Verified** ($F = 1.0$) |
| **Bell State (2Q)** | `{u3, cx}` | 2 → 2 | 2 → 2 | 0.26 ms | **Verified** ($F = 1.0$) |
| **Bell State (2Q)** | `{cz, ry, rz}` | 2 → 7 | 2 → 5 | 0.46 ms | **Verified** ($F = 1.0$) |
| **Bell State (2Q)** | `{rx, rz, cx}` | 2 → 5 | 2 → 5 | 0.31 ms | **Verified** ($F = 1.0$) |
| **GHZ State (3Q)** | `{rx, ry, rz, cx}` | 3 → 4 | 3 → 4 | 0.48 ms | **Verified** ($F = 1.0$) |
| **GHZ State (3Q)** | `{u3, cx}` | 3 → 3 | 3 → 3 | 0.43 ms | **Verified** ($F = 1.0$) |
| **GHZ State (3Q)** | `{cz, ry, rz}` | 3 → 12 | 3 → 8 | 0.97 ms | **Verified** ($F = 1.0$) |
| **GHZ State (3Q)** | `{rx, rz, cx}` | 3 → 6 | 3 → 6 | 0.55 ms | **Verified** ($F = 1.0$) |
| **QFT (3Q)** | `{rx, ry, rz, cx}` | 7 → 21 | 6 → 18 | 1.55 ms | **Verified** ($F = 1.0$) |
| **QFT (3Q)** | `{u3, cx}` | 7 → 18 | 6 → 16 | 2.07 ms | **Verified** ($F = 1.0$) |
| **QFT (3Q)** | `{cz, ry, rz}` | 7 → 57 | 6 → 44 | 3.61 ms | **Verified** ($F = 1.0$) |
| **QFT (3Q)** | `{rx, rz, cx}` | 7 → 27 | 6 → 23 | 1.78 ms | **Verified** ($F = 1.0$) |
| **Mixed Algorithmic (3Q)**<br>*(CCX, CRZ, SWAP, CZ)* | `{rx, ry, rz, cx}` | 8 → 34 | 6 → 22 | 2.35 ms | **Verified** ($F = 1.0$) |
| **Mixed Algorithmic (3Q)** | `{u3, cx}` | 8 → 29 | 6 → 20 | 2.28 ms | **Verified** ($F = 1.0$) |
| **Mixed Algorithmic (3Q)** | `{cz, ry, rz}` | 8 → 78 | 6 → 53 | 4.79 ms | **Verified** ($F = 1.0$) |
| **Mixed Algorithmic (3Q)** | `{rx, rz, cx}` | 8 → 44 | 6 → 29 | 2.74 ms | **Verified** ($F = 1.0$) |

### 2.2 Complexity Analysis
- **Profiling Complexity:** $\mathcal{O}(g)$ linear pass over the gate sequence. Maintaining wire availability layers via a hash map or array of size $q$ gives an amortized $\mathcal{O}(1)$ step per gate, resulting in strict $\mathcal{O}(g)$ execution time and $\mathcal{O}(q)$ auxiliary memory.
- **Decomposition Complexity:** $\mathcal{O}(g \cdot d_{\max})$, where $d_{\max}$ is the maximum expansion factor of any single gate into the basis (e.g., Toffoli/CCX expands to $15$ gates; SWAP expands to $3$ CX gates). For all finite discrete/continuous bases, $d_{\max} \le 16$, guaranteeing linear $\mathcal{O}(g)$ execution time.

---


## 3. Architectural Trade-offs & Limitations (QC-C1-01)
- **Universal Basis Trade-offs:** Decomposing multi-qubit gates (such as CCX and CRz) into standard bases increases gate counts while strictly maintaining 1.00000000 unitary fidelity.
- **Fail-Closed Gate Validation:** When a requested hardware basis lacks multi-qubit entangling capabilities, decomposition fails gracefully (`is_valid = False`) without emitting corrupted circuits.
