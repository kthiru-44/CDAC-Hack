# QC-C1-01 — Technical Approach (Deliverable #2)

> Comprehensive technical description mandated by PESU – C-DAC Hackathon Rules §6.2: Problem statements, mathematical algorithms, architectural design, verification methodologies, and formal references.

---

## 1. Executive Summary & Unified Architecture

Our solution, **`qnvkit`**, is an integrated quantum compiler toolkit built on top of the C-DAC Qniverse ecosystem. Rather than treating the three problem statements as isolated assignments, `qnvkit` unites them around a shared, immutable quantum intermediate representation (`CircuitIR`), an earliest-available-layer depth scheduler, and a rigorous mathematical equivalence verification engine.

```mermaid
flowchart TD
    subgraph Inputs ["Input Interfaces"]
        QASM["OpenQASM 2.0 / 3.0 Source"]
        QC["QniverseCircuit (QSDK)"]
    end

    subgraph Core ["qnvkit Core Foundation"]
        Parser["qnvkit.qasm.parser3 / parser2"]
        Adapter["qnvkit.qsdk_adapter"]
        IR["Immutable CircuitIR\n(SHA-256 Fingerprinted)"]
        Metrics["qnvkit.metrics\n(Earliest-Layer Depth & Profiling)"]
        Sim["qnvkit.sim\n(Unitary & Statevector Verifier)"]
    end

    subgraph Solvers ["Problem Solvers"]
        C1["QC-C1-01: Profiling &\nBasis Decomposer"]
        C2["QC-C2-03: OpenQASM 3.0 Transpiler\n(Qiskit, Cirq, CUDA-Q, QSDK)"]
        C3["QC-C3-03: Safe Local Rewrite-Rule\nCircuit Optimizer"]
    end

    Inputs --> Parser
    Inputs --> Adapter
    Parser --> IR
    Adapter --> IR
    IR --> Metrics
    IR --> Sim
    IR --> C1
    IR --> C2
    IR --> C3
    C1 --> Sim
    C2 --> Sim
    C3 --> Sim
```

### 1.1 Guiding Engineering Principles
1. **Strict Immutability:** All functions (`profile`, `decompose`, `transpile`, `optimize`) are purely functional. Inputs are never mutated in place; every transformation constructs and returns a new circuit.
2. **Documented Interface Adherence:** Integrates strictly with documented C-DAC QSDK interfaces (`QniverseCircuit`, `QuantumRegister`, `ClassicalRegister`, `add_gate`, `add_conditional_gate`, `qasm`, `run`, `fetch_job_result`).
3. **Fail-Closed Unsupported Handling:** Never emits malformed or partially compiled circuits. If an operation cannot be mapped or decomposed, an explicit, structured `UnsupportedReport` is emitted.
4. **Zero-Credit Local Development:** 100% of unit tests, equivalence checks, and benchmarks run locally using NumPy matrix arithmetic at zero credit cost, conserving the team's 200 cloud credits.

---


## 2. Problem Statement 1: QC-C1-01 Profiling & Basis Decomposition

### 2.1 Problem Formulation
Given an arbitrary quantum circuit constructed via `QniverseCircuit` or OpenQASM:
1. Extract a granular structural profile: total unitary gates, operation counts by type, single-qubit vs two-qubit vs multi-qubit gate counts, declared vs actively used qubits, and scheduled circuit depth.
2. Decompose all non-basis gates into a user-selected basis gate set (e.g., `{rx, ry, rz, cx}`, `{cz, ry, rz}`, `{u3, cx}`, `{rx, rz, cx}`).
3. Retain measurements, barriers, and resets in proper relative sequence.
4. Verify mathematical equivalence against the original circuit up to global phase.

### 2.2 Earliest-Available-Layer Scheduled Depth Algorithm
A naive count of gates ignores physical parallel execution on disjoint qubits. `qnvkit` defines depth as the scheduled layer count under earliest-available execution:
- Let $L[q]$ represent the next available execution layer on qubit wire $q \in \{0, \dots, n-1\}$, initialized to $0$.
- For each unitary gate $G$ acting on qubit subset $Q_G \subseteq \{0, \dots, n-1\}$:
  $$\text{layer}(G) = \max_{q \in Q_G} L[q]$$
  $$L[q] \leftarrow \text{layer}(G) + 1, \quad \forall q \in Q_G$$
- **Barriers:** A barrier across qubit set $Q_B$ does not add computational depth, but synchronizes wire timing:
  $$\text{sync} = \max_{q \in Q_B} L[q], \quad L[q] \leftarrow \text{sync}, \quad \forall q \in Q_B$$
- **Measurements:** A measurement on qubit $q$ advancing classical bit $c$ increments wire layers on both domains.
- Total scheduled depth is $\max_{q} L[q]$.

### 2.3 Mathematical Algorithms for Basis Decomposition

#### Single-Qubit Euler Angle Synthesis
Any single-qubit unitary $U \in \text{SU}(2)$ can be parameterized by Euler angles $\theta, \phi, \lambda$:
$$U(\theta, \phi, \lambda) = \begin{pmatrix} \cos(\theta/2) & -e^{i\lambda}\sin(\theta/2) \\ e^{i\phi}\sin(\theta/2) & e^{i(\phi+\lambda)}\cos(\theta/2) \end{pmatrix}$$

1. **$ZYZ$ Canonical Form (for `{rx, ry, rz, cx}` and `{u3, cx}`):**
   $$U = R_z(\phi) R_y(\theta) R_z(\lambda)$$
   Where angles are extracted directly from matrix entries:
   $$\theta = 2 \arccos\left(\min(1, \max(0, |U_{00}|))\right)$$
   $$\phi + \lambda = \arg(U_{11}) - \arg(U_{00}), \quad \phi - \lambda = \arg(U_{10}) - \arg(U_{01})$$

2. **$ZXZ$ Canonical Form (for `{rx, rz, cx}`):**
   $$U = R_z(\alpha) R_x(\beta) R_z(\gamma)$$
   Converted from $ZYZ$ via basis rotation $R_y(\theta) = R_z(-\pi/2) R_x(\theta) R_z(\pi/2)$.

#### Entangling Gate Decompositions
- **CZ Decomposition into CX:**
  $$\text{CZ}(q_0, q_1) = \left(I \otimes H\right) \cdot \text{CX}(q_0, q_1) \cdot \left(I \otimes H\right)$$
- **SWAP Decomposition into CX:**
  $$\text{SWAP}(q_0, q_1) = \text{CX}(q_0, q_1) \cdot \text{CX}(q_1, q_0) \cdot \text{CX}(q_0, q_1)$$
- **Toffoli (CCX) Decomposition into Clifford+T:**
  Synthesized using $6$ CX gates and single-qubit rotations ($H, T, T^\dagger$), maintaining minimal two-qubit depth.

---


## 5. Mathematical Equivalence Verification Engine

To guarantee circuit correctness across decomposition, transpilation, and optimization, `qnvkit.sim` implements full unitary matrix reconstruction and statevector simulation:

### 5.1 Unitary Equivalence Up to Global Phase
For an $n$-qubit circuit without measurements ($n \le 10$):
1. Compute the full unitary $U_{\text{orig}} \in \mathbb{C}^{2^n \times 2^n}$ and $U_{\text{mod}} \in \mathbb{C}^{2^n \times 2^n}$ via Kronecker tensor products and tensordot permutations.
2. The normalized Hilbert-Schmidt inner product evaluates global phase invariance:
   $$F_{\text{unitary}}(U_A, U_B) = \frac{1}{2^n} \left| \operatorname{Tr}\left( U_A^\dagger U_B \right) \right|$$
3. Circuits are declared mathematically equivalent if and only if:
   $$\left| 1 - F_{\text{unitary}}(U_A, U_B) \right| < 10^{-7}$$

### 5.2 Statevector Fidelity
For arbitrary pure input states $|\psi_0\rangle = |0\rangle^{\otimes n}$:
$$F_{\text{state}}(|\psi_A\rangle, |\psi_B\rangle) = \left| \langle \psi_A \mid \psi_B \rangle \right|^2$$
Equivalence is verified when $1 - F < 10^{-7}$.

---


## 6. Formal References & Literature

1. **C-DAC Qniverse Platform Manuals:**
   - *C-DAC Quantum Software Development Kit (QSDK) User Guide*, 2024.
   - *Qniverse Cloud Execution & Backend API Reference*, 2024.
2. **Quantum Circuit Compilation & Equivalence:**
   - Nielsen, M. A., & Chuang, I. L. *Quantum Computation and Quantum Information*, Cambridge University Press, 2010.
   - Shende, V. V., Bullock, S. S., & Markov, I. L. *Synthesis of Quantum-Logic Circuits*, IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems, 2006.
   - Cross, A. W., et al. *Open Quantum Assembly Language (OpenQASM 3.0)*, ACM Transactions on Quantum Computing, 2022.
3. **Framework Documentation:**
   - Qiskit Development Team, *Qiskit: An Open-source Framework for Quantum Computing*, 2024.
   - Google Quantum AI, *Cirq: A Python Framework for Creating, Editing, and Invoking Quantum Circuits*, 2024.
   - NVIDIA Corporation, *CUDA-Q: High-Performance Quantum-Classical Computing*, 2024.

