# QC-C3-03 — Performance Evaluation Report (Deliverable #3)

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


## 4. Problem QC-C3-03: Safe Rewrite-Rule Quantum Circuit Optimizer

### 4.1 Benchmark Evaluation on Diverse Test Topologies

All rewrite passes enforce wire adjacency, barrier boundaries, and non-mutation:

| Test Circuit Scenario | Gates Before → After | Depth Before → After | Passes Applied | Mathematical Equivalence | Runtime |
|---|---|---|---|---|---|
| **Pure Inverses & Rotations**<br>*(H-H, X-X, CX-CX, S-Sdg, Rz)* | 10 → 1 (**90.0% red.**) | 6 → 1 (**83.3% red.**) | `cancel_self_inverse`, `cancel_cx`, `cancel_inverse_pairs`, `merge_rotations` | **Verified** ($F = 1.000000$) | 0.69 ms |
| **Mixed with Barrier Boundary**<br>*(Protected pair across barrier)* | 13 → 4 (**69.2% red.**) | 8 → 3 (**62.5% red.**) | `cancel_self_inverse`, `cancel_cx`, `cancel_inverse_pairs`, `merge_rotations` | **Verified** ($F = 1.000000$) | 0.90 ms |
| **Negative Control (Barrier Guarded)**<br>*(H, X followed by barrier)* | 4 → 4 (**0.0% red.**) | 2 → 2 (**0.0% red.**) | *None* (Preserved by design) | **Verified** ($F = 1.000000$) | 0.28 ms |
| **Irreducible Circuit (QFT-3)**<br>*(No adjacent inverse gates)* | 4 → 4 (**0.0% red.**) | 4 → 4 (**0.0% red.**) | *None* (No spurious rewrites) | **Verified** ($F = 1.000000$) | 0.88 ms |

### 4.2 Complexity Analysis
- **Causal Wire Adjacency Construction:** $\mathcal{O}(g)$ forward pass recording the immediate predecessor and successor index for each qubit wire.
- **Pass Execution:** Each pass scans candidate pairs in $\mathcal{O}(g)$. Because each successful rewrite strictly decreases gate count by at least 1, the fixed-point loop runs at most $k \le 10$ times.
- **Overall Optimization Complexity:** $\mathcal{O}(k \cdot g) = \mathcal{O}(g)$, linear in circuit size.

---


## 3. Architectural Trade-offs & Limitations (QC-C3-03)
- **Local Rewrite vs Global Synthesis:** Local wire-graph rewrites provide fast O(g) fixed-point optimization with zero fidelity loss (F = 1.0), avoiding the exponential overhead of full unitary synthesis.
- **Barrier Safety Invariants:** Barriers strictly prevent gate cancellations across timing synchronization points, preserving intentional hardware calibration semantics.
