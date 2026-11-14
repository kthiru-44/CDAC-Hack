# 03 — Technical Approach (Deliverable #2)

> Fill in or adjust once the problem statement is released. Keep the section headings, since they map to rules §6.2.

## 1. Problem statement
Quantum circuits written in Qniverse (or imported as OpenQASM 2.0) are executed without user-controlled
optimisation. On noisy simulators and hardware, every extra gate, especially two-qubit gates, and every
idle layer lowers the success probability. We need an optimiser that:
1. reduces depth and gate count,
2. maximises the **estimated fidelity** under Qniverse's noise model,
3. **proves** the optimised circuit is equivalent to the original, and
4. works directly with Qniverse's QASM-based workflow, and
5. converts circuits between frameworks (Qiskit, Cirq, CUDA-Q) and **verifies on many simulators** that every
   version gives the same results (domain 3).

## 2. Solution overview: QOpt
A pass-based optimisation pipeline with a profiler in front and a verifier at the end.

```
          ┌──────────┐   ┌──────────────────────────────────────┐   ┌──────────┐   ┌────────────┐
QASM 2.0 ─► Profiler ├──►  Optimisation pipeline                ├──► Verifier ├──► Benchmark  │
          │ (before) │   │  1. Peephole: cancel/merge            │   │  (equiv. │   │ + Qniverse │
          └──────────┘   │  2. Commutation-based cancellation    │   │  certif.)│   │  before/   │
                         │  3. 1-qubit rotation resynthesis      │   └────┬─────┘   │  after run │
                         │  4. ZX-calculus simplification (PyZX) │        │         └────────────┘
                         │  5. 2-qubit block resynthesis (KAK)   │        ▼
                         │  6. Target basis + routing            │   optimised QASM 2.0
                         │  Cost = noise-aware fidelity estimate │   + report (JSON / HTML)
                         └──────────────────────────────────────┘
```

## 3. Algorithms and mathematical concepts
### 3.1 Circuit representation
- A DAG (directed acyclic graph) of gates, using Qiskit `DAGCircuit`. Nodes are gates and edges are qubit wires.
- **Depth** is the longest path in the DAG, O(V+E).

### 3.2 Optimisation passes
| Pass | Idea | Complexity |
|---|---|---|
| Inverse cancellation | Adjacent G·G⁻¹ = I (CX·CX, H·H, …) | O(g) |
| Rotation merging | Rz(a)·Rz(b) = Rz(a+b). Drop when the angle ≈ 0 mod 2π | O(g) |
| Commutation analysis | Move gates through commuting neighbours to expose cancellations | O(g·k), k = window size |
| 1-qubit resynthesis | Fold any run of 1-qubit gates into one U3 via ZYZ Euler decomposition | O(g) |
| 2-qubit block resynthesis | KAK / Cartan decomposition: any 2-qubit unitary needs ≤ 3 CX | O(blocks) |
| ZX-calculus (PyZX `full_reduce`) | Rewrite as a ZX diagram, simplify with spider fusion, local complementation and pivoting, then extract the circuit | Polynomial, roughly O(n³) worst case |
| Basis translation and routing | Map to the target's native gates and coupling map, minimising SWAPs | Heuristic (SABRE) |

### 3.3 Noise-aware cost function
Estimated success probability (ESP):

  ESP = ∏_gates (1 − p_g) × ∏_qubits exp(−t_idle,q / T1) · exp(−t_idle,q / T2) × (1 − p_SPAM)^n

- p_g = depolarizing error for each gate (two-qubit gates weighted higher).
- t_idle,q = idle time on qubit q, computed from the gate duration Tg × idle layers.
- The parameters match Qniverse's noise model (p, T1, T2, Tg, ε), so our estimate lines up with what Qniverse simulates.
- The pipeline **keeps a candidate only if its ESP improves**. It can pick a *deeper* circuit when that circuit has fewer CX gates.

### 3.4 Equivalence verification
| Circuit size | Method | Guarantee |
|---|---|---|
| n ≤ ~12 qubits | Full unitary comparison, U₁ ≈ e^{iφ}U₂, via `qiskit.quantum_info.Operator.equiv` | Exact (up to numerical tolerance) |
| Larger n | Random-state fidelity: \|⟨ψ\|U₁†U₂\|ψ⟩\|² over k random states | Probabilistic, with error falling as k grows |
| Clifford circuits | Stabilizer tableau comparison | Exact, polynomial time |
| ZX path | PyZX `compare_tensors` / `verify_equality` | Exact for small n |

### 3.5 Conversion and multi-simulator verification
- **Common format:** OpenQASM 2.0. Converters in both directions: `qiskit.qasm2`, `cirq.circuit_to_qasm` / `cirq.contrib.qasm_import`, CUDA-Q translate.
- **Differential testing:** run original, converted and optimised circuits on N simulators and compare.

| Case | Comparison | Notes |
|---|---|---|
| Deterministic, small n | Statevector / unitary up to global phase | Fidelity > 1 - 1e-9 |
| Sampled output | TVD and chi-square test against the exact distribution | Shots chosen from a target false-alarm rate |
| Clifford circuits | Stabilizer simulators and tableau comparison | Polynomial time |
| Symbolic | PyZX equivalence | Small n |

- **Discrepancy report:** each mismatch is classified (endianness / bit-order, global phase, gate-definition difference, sampling noise) with the failing circuit minimised.
- **Conversion matrix:** framework pair x simulator, pass/fail, in the performance report.

## 4. Architecture and implementation
```
src/qopt/
├── io.py          # QASM 2.0 load/dump, Qiskit ↔ PyZX ↔ pytket adapters
├── convert.py     # QASM ↔ Qiskit / Cirq / CUDA-Q round-trip converters
├── simulators.py  # uniform runner over Qniverse (or local) simulators
├── discrepancy.py # cross-simulator comparison, mismatch classification
├── profile.py     # depth, gate counts, 2q count, critical path, idle time, ESP
├── passes/        # peephole.py, commute.py, resynth.py, zx.py, route.py
├── pipeline.py    # pass manager, noise-aware selection, levels O0–O3
├── verify.py      # unitary / statevector / stabilizer / ZX equivalence
├── noise.py       # Qniverse-style noise params → ESP + Aer noise model
├── qniverse.py    # submit before/after jobs to Qniverse backends (SDK)
└── report.py      # JSON and HTML report: tables, plots, certificate
benchmarks/        # QASMBench subset + Grover, QFT, adders, QAOA (n = 3…14)
notebooks/demo.ipynb  # Qniverse JupyterLab demo
```
**Stack:** Python 3.10+, qiskit, qiskit-aer, pyzx, pytket (optional), numpy, matplotlib, Qniverse SDK.

## 5. Implementation method
1. Profile the original circuit.
2. Run the pass pipeline. Score each candidate with ESP and keep the best.
3. Verify the best candidate against the original. Reject it if verification fails.
4. Emit optimised QASM 2.0 and a report.
5. Run original and optimised circuits on a Qniverse noisy simulator and compare success probability.

## 6. References
- Qniverse documentation: https://qniverse.in/docs/
- Qiskit transpiler: https://docs.quantum.ibm.com/api/qiskit/transpiler
- Kissinger and van de Wetering, *PyZX: Large Scale Automated Diagrammatic Reasoning* (2019); PyZX repo: https://github.com/zxcalc/pyzx
- Duncan, Kissinger, Perdrix and van de Wetering, *Graph-theoretic Simplification of Quantum Circuits with the ZX-calculus*, Quantum 4, 279 (2020)
- Li, Ding and Xie, *Tackling the Qubit Mapping Problem for NISQ-Era Quantum Devices* (SABRE), ASPLOS 2019
- Vatan and Williams, *Optimal quantum circuits for general two-qubit gates*, PRA 69, 032315 (2004)
- Sivarajah et al., *t|ket⟩: a retargetable compiler for NISQ devices* (2020)
- Li et al., *QASMBench: A Low-level QASM Benchmark Suite for NISQ Evaluation and Simulation* (2022)
- Nielsen and Chuang, *Quantum Computation and Quantum Information*
