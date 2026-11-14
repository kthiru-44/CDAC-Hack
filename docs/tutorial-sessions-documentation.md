# C-DAC & PESU Quantum Hackathon 2026: Tutorial Sessions Documentation

> Comprehensive reference documentation compiled from the three official C-DAC training sessions leading up to the PESU – C-DAC Quantum Hackathon (14 November 2026).
> 
> **Source Recordings:**
> - **Session 1 (28-10-2026, 2h 08m):** Quantum Foundations, Indigenous Initiatives & Qniverse Web Composer (*Vikas Ramaswamy & Naresh Raghavan, C-DAC Bengaluru*)
> - **Session 2 (07-11-2026, 1h 34m):** QSDK (Qniverse Software Development Kit) Architecture & JupyterLab Demo (*Harishankar Mishra, C-DAC Bengaluru*)
> - **Session 3 (12-11-2026, 1h 11m):** Grover's Algorithm Deep Dive & Official Hackathon Rules Briefing (*Vikas Ramaswamy, C-DAC Bengaluru & PESU Coordinators*)

---

## Table of Contents
1. [Session 1: Quantum Foundations & Qniverse Web Platform](#1-session-1-quantum-foundations--qniverse-web-platform)
   - [1.1 Indigenous Quantum Initiatives at C-DAC](#11-indigenous-quantum-initiatives-at-c-dac)
   - [1.2 Fundamental Quantum Concepts & Hardware Modalities](#12-fundamental-quantum-concepts--hardware-modalities)
   - [1.3 Quantum Gates, Superposition, and Entanglement](#13-quantum-gates-superposition-and-entanglement)
   - [1.4 Qniverse Web Composer & Real-Time OpenQASM 2.0](#14-qniverse-web-composer--real-time-openqasm-20)
   - [1.5 Execution, Detailed Job Reporting, and Metrics](#15-execution-detailed-job-reporting-and-metrics)
2. [Session 2: QSDK Architecture & Programming Model](#2-session-2-qsdk-architecture--programming-model)
   - [2.1 The 4-Step Execution Workflow](#21-the-4-step-execution-workflow)
   - [2.2 QSDK Dependencies & Environment Requirements](#22-qsdk-dependencies--environment-requirements)
   - [2.3 Circuit Construction (`QniverseCircuit`, Registers, Gate Application)](#23-circuit-construction-qniversecircuit-registers-gate-application)
   - [2.4 Supported Gate Library (40 Documented Gates)](#24-supported-gate-library-40-documented-gates)
   - [2.5 Advanced Primitives (Measurement, Conditionals, Modules, Initialization)](#25-advanced-primitives-measurement-conditionals-modules-initialization)
   - [2.6 Visualization & Export APIs](#26-visualization--export-apis)
   - [2.7 Backend Binding Architecture & Hierarchy](#27-backend-binding-architecture--hierarchy)
   - [2.8 Complete Simulator Taxonomy: CPU vs GPU on QACC and Param Utkarsh](#28-complete-simulator-taxonomy-cpu-vs-gpu-on-qacc-and-param-utkarsh)
   - [2.9 End-to-End Implementation Example (Bell State)](#29-end-to-end-implementation-example-bell-state)
   - [2.10 QSDK Job Management API](#210-qsdk-job-management-api)
   - [2.11 Troubleshooting & Common Runtime Errors](#211-troubleshooting--common-runtime-errors)
3. [Session 3: Grover's Algorithm & Hackathon Rules Briefing](#3-session-3-grovers-algorithm--hackathon-rules-briefing)
   - [3.1 Unsorted Search Problem Formulation](#31-unsorted-search-problem-formulation)
   - [3.2 Geometric Interpretation in 2D Subspace](#32-geometric-interpretation-in-2d-subspace)
   - [3.3 The Grover Operator: Phase Oracle & Diffusion Operator](#33-the-grover-operator-phase-oracle--diffusion-operator)
   - [3.4 Time Complexity & Iteration Optimization](#34-time-complexity--iteration-optimization)
   - [3.5 Hands-On Qniverse Implementation (`preloadedAlgorithm`)](#35-hands-on-qniverse-implementation-preloadedalgorithm)
   - [3.6 Official Hackathon Rules & Submission Guidelines](#36-official-hackathon-rules--submission-guidelines)
4. [Synthesis: How Tutorial Insights Empower Our Project (QOpt)](#4-synthesis-how-tutorial-insights-empower-our-project-qopt)

---

## 1. Session 1: Quantum Foundations & Qniverse Web Platform
*Presented by Vikas Ramaswamy and Naresh Raghavan (C-DAC Bengaluru) on 28 October 2026.*

### 1.1 Indigenous Quantum Initiatives at C-DAC
- **Historical Background:** C-DAC developed India's first indigenous quantum simulator, **Qsim**, launched in 2021 (serving over 7,000+ researchers and students).
- **The Qniverse Vision:** Qniverse (`https://qniverse.in/`) is C-DAC's unified quantum cloud platform. Its objective is to allow users to compose quantum circuits, simulate them at high scale across heterogeneous classical supercomputing infrastructure (Vector processors, HPC clusters, NVIDIA GPU acceleration), and eventually dispatch circuits to actual physical quantum processors (QPUs).

### 1.2 Fundamental Quantum Concepts & Hardware Modalities
- **Classical vs Quantum Information:**
  - Classical bit: Deterministic state $b \in \{0, 1\}$, represented physically by discrete voltage levels (e.g., $0\text{ V}$ and $5\text{ V}$).
  - Qubit (Quantum Bit): State $|\psi\rangle = \alpha|0\rangle + \beta|1\rangle$ in a 2D complex Hilbert space $\mathbb{C}^2$, with normalization $|\alpha|^2 + |\beta|^2 = 1$.
- **Major Physical Qubit Modalities:**
  1. **Superconducting Qubits:** Non-linear LC oscillators formed by Josephson junctions operating at millikelvin dilution refrigerator temperatures. Uses Cooper pairs with discrete anharmonic energy levels (e.g., IBM, Google, Rigetti).
  2. **Photonic Qubits:** Quantum states encoded in individual photons (polarization degrees of freedom $|\text{H}\rangle, |\text{V}\rangle$ or spatial waveguide modes/time-bin encodings). Operational at room temperature.
  3. **Trapped Ion Qubits:** Electrically charged atomic ions trapped in ultra-high vacuum by oscillating RF electromagnetic fields (Paul traps), manipulated via laser pulses (e.g., IonQ, Quantinuum).
  4. **Neutral Atom Qubits:** Neutral atoms held in arrays of focused optical laser tweezers, interacting via excitation into high-lying Rydberg states (e.g., QuEra).

### 1.3 Quantum Gates, Superposition, and Entanglement
- **Single-Qubit Unitary Operators:**
  - **Pauli-X (Bit-flip / NOT):** $X = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$; maps $|0\rangle \to |1\rangle$ and $|1\rangle \to |0\rangle$.
  - **Pauli-Y (Bit & Phase-flip):** $Y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}$; maps $|0\rangle \to i|1\rangle$ and $|1\rangle \to -i|0\rangle$.
  - **Pauli-Z (Phase-flip):** $Z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}$; maps $|0\rangle \to |0\rangle$ and $|1\rangle \to -|1\rangle$.
  - **Hadamard Gate ($H$):** Creates equal superposition:
    $$H = \frac{1}{\sqrt{2}}\begin{pmatrix} 1 & 1 \\ 1 & -1 \end{pmatrix}$$
    $$H|0\rangle = |+\rangle = \frac{|0\rangle + |1\rangle}{\sqrt{2}}, \quad H|1\rangle = |-\rangle = \frac{|0\rangle - |1\rangle}{\sqrt{2}}, \quad H|+\rangle = |0\rangle$$
- **Two-Qubit Controlled Gates & Entanglement:**
  - **Controlled-NOT ($CX$ / CNOT):** Acts as a quantum XOR operator. Control qubit $q_c$ leaves target qubit $q_t$ unchanged if $q_c=0$, and applies $X$ to $q_t$ if $q_c=1$.
    $$CX = \begin{pmatrix} 1 & 0 & 0 & 0 \\ 0 & 1 & 0 & 0 \\ 0 & 0 & 0 & 1 \\ 0 & 0 & 1 & 0 \end{pmatrix}$$
  - **Separable vs Entangled States:**
    - A state is separable if $|\psi_{\text{sep}}\rangle = |\psi_A\rangle \otimes |\psi_B\rangle$.
    - An entangled state cannot be factored into a single tensor product: $|\psi_{\text{ent}}\rangle \ne |\psi_A\rangle \otimes |\psi_B\rangle$.
    - **Canonical Bell State ($|\Phi^+\rangle$):** Built by $H(q_0)$ followed by $CX(q_0, q_1)$:
      $$|00\rangle \xrightarrow{H \otimes I} \frac{|00\rangle + |10\rangle}{\sqrt{2}} \xrightarrow{CX} \frac{|00\rangle + |11\rangle}{\sqrt{2}}$$

### 1.4 Qniverse Web Composer & Real-Time OpenQASM 2.0
- **URL & Interface:** `https://qniverse.in/QACC/`
- **Gate Palette:**
  - Single-qubit: $H, X, Y, Z, S, S^\dagger, T, T^\dagger, P, Rx, Ry, Rz, U$ (Euler rotation $U3$).
  - Two-qubit: $CX, CY, CZ, CP, SWAP$.
  - Measurement and Barrier operators.
  - Multi-qubit composite blocks: `QFT`, `IQFT`, `EPR`, `BSM`, `ORA` (Oracle), `DIF` (Diffusion).
- **Bi-directional Code Synchronization:**
  - Dragging gates visually generates OpenQASM 2.0 code in real time (`include "qelib1.inc";`).
  - Editing OpenQASM 2.0 text directly updates the graphical schematic on blur/compile.
  - Multi-framework exporter converts OpenQASM into Qiskit, Cirq, CUDA-Q, Qulacs, and QuEST (read-only code generation).
- **Inspection Tools:**
  - Unitary matrix inspector showing transition matrices in $\{0, 1\}$, $\{+, -\}$, and $\{+i, -i\}$ bases.
  - Bloch sphere vector display for single-qubit states.
  - Probability distribution bar charts displaying state probabilities across computational basis states.

### 1.5 Execution, Detailed Job Reporting, and Metrics
- Circuits can be executed by selecting the **Run** button.
- **Detailed Report Page (`detailedreport.php?jobid=...`):**
  - Displays execution backend (e.g. `qasm_simulator`), execution duration, and noise model flags.
  - Histogram plot of sampled shot counts (default 1024 shots).
  - JSON output payload (e.g., `{"probability": {"11": 503, "00": 521}, "shots": 1024}`).
  - Three inspection tabs: `Circuit` (schematic), `QASM` (OpenQASM source), and `Transpiled Code` (the backend-synthesized instructions).

---

## 2. Session 2: QSDK Architecture & Programming Model
*Presented by Harishankar Mishra (Project Engineer, C-DAC Bengaluru) on 7 November 2026.*

### 2.1 The 4-Step Execution Workflow
1. **Build:** Instantiate `QniverseCircuit`, register quantum/classical registers, apply gates and measurements.
2. **Configure:** Instantiate `Backend()`, configure processor (`CPU`/`GPU`), select HPC environment, and choose simulation engine.
3. **Submit:** Dispatch circuit to backend using `run()`, supplying your Qniverse user API token.
4. **Retrieve:** Poll job status, retrieve results using `fetch_job_result()`, and plot output histograms.

### 2.2 QSDK Dependencies & Environment Requirements
QSDK requires Python 3.8+ and 5 fundamental dependencies:
| Package | Min Version | Purpose |
|---|---|---|
| `numpy` | 1.21+ | State-vector mathematics, rotation angles, matrix transformations |
| `requests` | 2.25+ | REST API communication with Qniverse backend gateway |
| `svgwrite` | 1.4+ | Rendering circuit diagrams as vector graphics (`.svg`) |
| `IPython` | 7.0+ | Interactive notebook display and visualization |
| `tabulate` | 0.10.0+ | Formatted tabular summaries in terminal / stdout |

### 2.3 Circuit Construction (`QniverseCircuit`, Registers, Gate Application)
```python
from Qniverse.QniverseCircuit import *
from Qniverse.gates import *

# 1. Initialize Circuit
qc = QniverseCircuit()

# 2. Add Registers
# Rules: Alphabetic names only, unique in circuit, positive integer size
q = QuantumRegister(5, 'q')
c = ClassicalRegister(3, 'c')
qc.add_register(q)
qc.add_register(c)
```

#### Four Ways to Apply Gates:
1. **Single-Qubit Gates:**
   ```python
   qc.add_gate(h, q[0])
   qc.add_gate(y, q[1])
   ```
2. **Controlled Two-Qubit Gates (Last qubit is ALWAYS the target):**
   ```python
   qc.add_gate(ch, q[3], q[2])    # Control: q[3], Target: q[2]
   qc.add_gate(cx, q[1], q[4])    # Control: q[1], Target: q[4]
   ```
3. **Multi-Controlled Gates (Controls precede target):**
   ```python
   qc.add_gate(ccx, q[1], q[2], q[4])         # Controls: q[1], q[2]; Target: q[4]
   qc.add_gate(c3x, q[1], q[2], q[3], q[4])   # Controls: q[1], q[2], q[3]; Target: q[4]
   ```
4. **Parameterized Gates (Angles in radians via NumPy):**
   ```python
   import numpy as np
   qc.add_gate(rx(np.pi / 2), q[1])
   qc.add_gate(u3(np.pi / 2, 0, np.pi), q[2])
   ```

### 2.4 Supported Gate Library (40 Documented Gates)
QSDK provides 40 documented gate primitives:
- **Single-Qubit (15):** `id`, `x`, `y`, `z`, `h`, `s`, `t`, `sdg` ($S^\dagger$), `tdg` ($T^\dagger$), `p` (Phase), `rx`, `ry`, `rz`, `u1`, `u2`, `u3`
- **Controlled & Two-Qubit (16):** `cx`, `cy`, `cz`, `ch`, `swap`, `cs`, `ct`, `csdg`, `ctdg`, `cp`, `crx`, `cry`, `crz`, `cu1`, `cu2`, `cu3`
- **Multi-Qubit (5):** `ccx` (Toffoli), `cswap` (Fredkin), `c3x`, `c4x`, `c5x`
- **Utility & Non-Unitary (4):** `reset`, `measure`, `barrier`
- **Inspection Helper:** `qc.list_gates()` returns all registered gate keywords.

### 2.5 Advanced Primitives (Measurement, Conditionals, Modules, Initialization)
- **Measurement:**
  ```python
  qc.add_gate(measure, q[1], c[2])  # Maps single qubit to classical bit
  qc.measure_all()                  # Measures all qubits into dedicated 'meas' register
  ```
- **Classical Conditioning:**
  ```python
  qc.add_conditional_gate(c, 1, h, q[1])  # Executes H on q[1] if classical register c == 1
  # NOTE: cirq_simulator does not support conditional gates!
  ```
- **Predefined Composite Modules:**
  ```python
  qc.add_module(qft, q[0], q[1], q[2])
  qc.add_module(iqft, q[0], q[1], q[2])
  ```
- **Arbitrary State Initialization:**
  ```python
  # Amplitudes must be complex numbers
  qc.initialize(q[0], complex(np.sqrt(0.5), 0), complex(0, np.sqrt(0.5)))
  qc.initialize_all(complex(np.sqrt(0.5), 0), complex(np.sqrt(0.5), 0))
  ```

### 2.6 Visualization & Export APIs
- `qc.qasm()`: Returns string containing standard OpenQASM 2.0 representation.
- `qc.draw("circuit.svg")`: Renders the circuit as an SVG vector image.
- `qc.download_circuit()`: Downloads the rendered SVG to disk.
- `plot_histogram(result, probability=True)`: Displays bar chart of measurement results.

### 2.7 Backend Binding Architecture & Hierarchy
The backend requires binding three decisions in **strict order**:
1. `backend.processor("CPU" | "GPU")`
2. `backend.hpc("QACC_Cluster" | "Param_Utkarsh")`
3. `backend.simulator("<simulator_name>")`

> [!WARNING]
> Calling these out of order raises a `ValueError`. Omitting the API token at global scope raises a `RuntimeError`.

#### Dynamic Discovery Functions:
Rather than hardcoding simulator names, QSDK exposes introspection methods:
- `Backend.get_processor()`: Returns available target processors (`['CPU', 'GPU']`).
- `Backend.get_hpc(processor)`: Returns valid clusters for selected processor.
- `Backend.get_simulator(processor, hpc)`: Returns available simulator engines for given target.

### 2.8 Complete Simulator Taxonomy: CPU vs GPU on QACC and Param Utkarsh
| Processor | HPC Environment | Supported Simulators | Count |
|---|---|---|---|
| **CPU** | `QACC_Cluster` | `aer_simulator_density_matrix`, `aer_simulator_statevector`, `cirq_simulator`, `qasm_simulator`, `qsimcirq_simulator`, `quest_simulator`, `qulacs_multicpu_simulator` | 7 |
| **GPU** | `QACC_Cluster` | `aer_simulator_statevector_gpu`, `nvidia_cudaq_statevector_simulator`, `qsimcirq_cuquantum_gpu_simulator` | 3 |
| **CPU** | `Param_Utkarsh` | `aer_simulator_density_matrix`, `aer_simulator_statevector`, `cirq_simulator`, `qasm_simulator` | 4 |
| **GPU** | `Param_Utkarsh` | `aer_simulator_statevector_gpu` | 1 |

*Note: GPU backends build on NVIDIA cuStateVec, CUDA-Q, and cuQuantum acceleration libraries.*

### 2.9 End-to-End Implementation Example (Bell State)
```python
import numpy as np

# Define token at global scope
token = "YOUR_QNIVERSE_API_TOKEN"

from Qniverse.QniverseCircuit import *
from Qniverse.gates import *
from Qniverse.backend import Backend
from Qniverse.api import run, fetch_job_result, plot_histogram

# 1. Build circuit
qc = QniverseCircuit()
q = QuantumRegister(2, 'q')
c = ClassicalRegister(2, 'c')
qc.add_register(q)
qc.add_register(c)

qc.add_gate(h, q[0])
qc.add_gate(cx, q[0], q[1])
qc.measure_all()

# 2. Configure backend
backend = Backend()
backend.processor("CPU")
backend.hpc("QACC_Cluster")
backend.simulator("qasm_simulator")

# 3. Submit
job = run(qc, backend, shots=1024, token=token, job_name="bell_demo")

# 4. Fetch results
result = fetch_job_result(token, job)
print("Execution Result:", result)
# plot_histogram(result, probability=True)
```

### 2.10 QSDK Job Management API
All job interactions can be invoked as functions or backend/job methods:
| Call | Description |
|---|---|
| `run(qc, backend, shots, token=, job_name=)` | Validates circuit and submits job to queue |
| `job_status(token, job)` | Returns status (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`) |
| `job_details(token, job)` | Returns job metadata, configuration, timestamps |
| `fetch_job_result(token, job)` | Returns dictionary of counts / probabilities |
| `transpiled_code(token, job)` | Retrieves backend-transpiled circuit (Cirq or Qiskit representation) |
| `get_backend(token)` | Lists all backend simulators accessible to user |
| `list_jobs(token)` | Lists user execution history |
| `cancel_job(token, job)` | Cancels queued or running job |
| `delete_job(token, job)` | Removes job from user records |
| `credit_balance(token)` | Queries remaining account credits |

### 2.11 Troubleshooting & Common Runtime Errors
| Exception / Error | Cause | Solution |
|---|---|---|
| `RuntimeError: Token not found` | Token defined inside function or class scope | Define `token = "..."` at **global scope** at top of script |
| `HTTP 401 Unauthorized` | Invalid or expired token | Regenerate API key on Qniverse profile dashboard |
| `HTTP 403 Forbidden` | Account lacks access permissions | Request hackathon credits pool access from C-DAC reps |
| `ValueError: Backend set out of order` | Methods called in wrong sequence | Call `processor()`, then `hpc()`, then `simulator()` |
| `RuntimeError: No measurements` | `run()` called without measure gates | Add measurement gate(s) or `qc.measure_all()` before submission |
| `RuntimeError: No conditional logic` | Conditional gate submitted to Cirq | `cirq_simulator` lacks conditional gate support; switch to Aer/QASM |
| `ConnectionError: Unreachable / stuck` | Job PENDING > 30 minutes | Verify network/VPN; email `qniverse@cdac.in` with job ID |

---

## 3. Session 3: Grover's Algorithm & Hackathon Rules Briefing
*Presented by Vikas Ramaswamy (C-DAC Bengaluru) on 12 November 2026.*

### 3.1 Unsorted Search Problem Formulation
- **Objective:** Find target input $x^*$ in an unsorted search space of $N = 2^n$ items, defined by a boolean oracle:
  $$f(x) = \begin{cases} 1 & \text{if } x = x^* \\ 0 & \text{if } x \ne x^* \end{cases}$$
- **Classical Search:** Exhaustive search requires $O(N)$ query evaluations (average $N/2$).
- **Quantum Advantage:** Grover's algorithm evaluates the search in $O(\sqrt{N})$ queries—a proven quadratic speedup.
- **Initial State:** Uniform superposition across all $N$ states:
  $$|s\rangle = \frac{1}{\sqrt{N}} \sum_{x=0}^{N-1} |x\rangle = \cos\theta |\psi_{\text{non-target}}\rangle + \sin\theta |\psi_{\text{target}}\rangle$$
  where $\sin\theta = \sqrt{\frac{M}{N}}$ ($M$ is the number of target solutions; $M=1$ for unique target).

### 3.2 Geometric Interpretation in 2D Subspace
The algorithm operates strictly within the 2D plane spanned by two orthonormal basis states:
1. $|\psi_{\text{target}}\rangle$: The superposition of all solution states.
2. $|\psi_{\text{non-target}}\rangle$: The superposition of all non-solution states.

In this 2D plane:
- The initial state $|s\rangle$ forms an angle $\theta = \sin^{-1}\left(\sqrt{\frac{M}{N}}\right)$ with $|\psi_{\text{non-target}}\rangle$.
- When $N \gg M$, $\theta \approx \sqrt{\frac{M}{N}} \ll 1$.

### 3.3 The Grover Operator: Phase Oracle & Diffusion Operator
The full Grover iteration operator is defined as:
$$G = D_s \cdot S_f$$

#### 1. Phase Oracle ($S_f$):
- Marks target state(s) by inverting their phase by $\pi$:
  $$S_f |x\rangle = (-1)^{f(x)} |x\rangle$$
- **Geometric action:** Reflection across the horizontal $|\psi_{\text{non-target}}\rangle$ axis.
- State vector $|s\rangle$ at angle $+\theta$ is reflected to $-\theta$.

#### 2. Diffusion Operator ($D_s$ - Inversion About the Mean):
- Mathematical formulation:
  $$D_s = 2|s\rangle\langle s| - I = H^{\otimes n} (2|0\rangle\langle 0| - I) H^{\otimes n}$$
- Circuit implementation:
  1. $H^{\otimes n}$ layer
  2. $X^{\otimes n}$ layer
  3. Multi-controlled phase / $Z$ gate (conjugated by $H$ on target)
  4. $X^{\otimes n}$ layer
  5. $H^{\otimes n}$ layer
- **Geometric action:** Reflection of the state across the original uniform superposition vector $|s\rangle$.
- Because the state prior to diffusion was at $-\theta$ and $|s\rangle$ is at $+\theta$, the reflection rotates the state to:
  $$\theta + (\theta - (-\theta)) = 3\theta$$
- **Net Effect per Iteration:** The state vector advances toward $|\psi_{\text{target}}\rangle$ by exactly $2\theta$.

### 3.4 Time Complexity & Iteration Optimization
After $k$ iterations of $G$, the state becomes:
$$|\psi_k\rangle = \sin((2k+1)\theta)|\psi_{\text{target}}\rangle + \cos((2k+1)\theta)|\psi_{\text{non-target}}\rangle$$

The probability of measuring a target solution is:
$$P_{\text{success}} = \sin^2((2k+1)\theta)$$

To maximize $P_{\text{success}} \approx 1$:
$$(2k + 1)\theta = \frac{\pi}{2} \implies k = \frac{\pi}{4\theta} - \frac{1}{2}$$

Substituting $\theta \approx \sqrt{\frac{M}{N}}$:
$$k_{\text{opt}} \approx \left\lfloor \frac{\pi}{4}\sqrt{\frac{N}{M}} \right\rfloor$$

> [!CAUTION]
> **Over-rotation:** Applying more than $k_{\text{opt}}$ iterations causes the state vector to rotate past $|\psi_{\text{target}}\rangle$, causing $P_{\text{success}}$ to decrease. The iteration count must be precisely tuned.

### 3.5 Hands-On Qniverse Implementation (`preloadedAlgorithm`)
- **Portal Path:** `qniverse.in/QACC/preloadedAlgorithm`
- Selecting **Grover's Algorithm - Search**:
  - Configure number of qubits (e.g., $n=3$, $N=8$).
  - Configure target bitstring (e.g., `111`).
  - Click **Load Circuit**.
- **Circuit Decomposition in Qniverse Composer:**
  - $n=3, N=8, M=1 \implies k_{\text{opt}} \approx \frac{\pi}{4}\sqrt{8} \approx 2$ iterations.
  - Phase Oracle for $|111\rangle$: Controlled-Phase ($CP(\pi)$) or Toffoli ($CCX$) targeting an ancilla initialized in $|-\rangle$, or $H \cdot CCX \cdot H$ on the last qubit.
  - Diffusion block (`DF`): Standard $H \to X \to \text{multi-}CZ \to X \to H$ sequence.
  - Measurement registers and histogram displaying $>95\%$ peak amplitude on target $|111\rangle$.

### 3.6 Official Hackathon Rules & Submission Guidelines
*(Reviewed from `hackathon_rules.pdf` presented by Vikas Ramaswamy and coordinators)*

#### Participation Rules:
1. **Working Implementation Mandatory:** A theoretical or slides-only concept is automatically rejected. A functional proof-of-concept (POC) must be demonstrated.
2. **Quantum Relevance:** Project must directly solve a problem in quantum computing, quantum compilation, or related quantum technologies.
3. **Qniverse Integration:** Solution must run on the Qniverse platform or integrate with the Qniverse SDK.
4. **Permitted External Libraries:** Open-source packages (e.g. Qiskit, PyZX, PyTket, Cirq, CuQuantum) may be installed locally or inside the Qniverse JupyterLab instance, provided they are demonstrated interoperating with the Qniverse pipeline.
5. **Mandatory AI Declaration:** AI and LLM tools (e.g. Claude Code, Gemini) are permitted for development, debugging, and documentation, but their specific usage and models must be formally disclosed in `docs/07-ai-usage.md`.

#### Evaluation Checkpoints & Weightage:
| Class | Evaluation Timing | Weight |
|---|---|---|
| **Class 1** | Checkpoint 1 (~3 hours after start) | 20% |
| **Class 2** | Checkpoint 2 (Mid-event, ~6 hours in) | 30% |
| **Class 3** | Final Submission Checkpoint (~11 hours in) | 50% |

#### Scoring Breakdown:
- **40%:** Product & Application Delivery (Working code, measured benchmarks, clean integration)
- **35%:** Scheduled Judges' Evaluations (Technical rigor, novelty, equivalence proofs)
- **15%:** Presentation & Reviewers' Assessment (Clarity, before/after metrics, visual plots)
- **10%:** Final Viva-Voce (Technical Q&A defending algorithm complexity and design choices)

#### Open Innovation Track:
- Teams may propose their own challenge under Domain 9 ("Open Innovation").
- Can earn an **additional weightage bonus of up to +20%** under product delivery.
- Must be pitched to judges at the start or Checkpoint 1 to be classified into Class 1, 2, or 3.

---

## 4. Synthesis: How Tutorial Insights Empower Our Project (QOpt)

The tutorial sessions provide direct solutions and architectural validation for our **QOpt** compiler project (`CDAC-Hack`):

1. **Resolution of QSDK Ambiguity (from `docs/02-qniverse-gap-analysis.md`):**
   - The team's earlier question: *"Is there a Python SDK and what is its syntax?"* is now completely answered.
   - We have the exact imports (`from Qniverse.QniverseCircuit import *`, `from Qniverse.gates import *`, `from Qniverse.backend import Backend`, `from Qniverse.api import run, fetch_job_result, transpiled_code, get_backend`).
   - We know the exact dynamic discovery methods (`Backend.get_processor()`, `Backend.get_hpc()`, `Backend.get_simulator()`), which allows QOpt's `src/qopt/simulators.py` to auto-discover all available backends cleanly!

2. **Backend Transpiler Hook Discovered:**
   - Slide 12 revealed the call `transpiled_code(token, job)`: Qniverse already transpile circuits to Cirq or Qiskit representations before running!
   - This provides the ideal benchmark baseline: QOpt can compare its own optimized circuits against Qniverse's internal transpiler output!

3. **Multi-Simulator Verification Strategy (Domain 3):**
   - Slide 10 gave the exact simulator roster across CPU and GPU on `QACC_Cluster` and `Param_Utkarsh` (15 total simulator configurations).
   - QOpt's differential testing harness can target `aer_simulator_statevector`, `cirq_simulator`, `quest_simulator`, `qulacs_multicpu_simulator`, and `qasm_simulator` to prove that our optimized circuits yield identical unitaries and distributions across all engines.

4. **Benchmarking with Grover's Algorithm:**
   - Session 3 presented Grover's algorithm in detail as the gold-standard algorithm for Qniverse.
   - We can include Grover circuits ($n=3$ to $n=8$) as core benchmark targets in `benchmarks/`, demonstrating how QOpt optimizes the oracle and diffusion layers to reduce 2-qubit CX counts and boost Estimated Success Probability (ESP) on Qniverse noisy simulators!
