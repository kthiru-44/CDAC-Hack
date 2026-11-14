# QC-C2-03: OpenQASM 3.0 Transpiler to Qiskit, Cirq, CUDA-Q & QSDK

> **Problem ID:** QC-C2-03 (Class II, Checkpoint 2)  
> **Package:** `src/qnvkit/` | **CLI Tool:** `c2-03-qasm3-transpiler/transpiler_cli.py` | **Demo:** `examples/c2_demo.py`  
> **Target Framework Versions:** Qiskit $\ge 1.0.0$, Cirq $\ge 1.4.0$, NVIDIA CUDA-Q $\ge 0.8.0$, C-DAC QSDK ($1.6+$)

---

## 1. Executive Summary

This module implements a production-grade, dependency-free **OpenQASM 3.0 and OpenQASM 2.0 transpiler** that translates quantum circuit programs into standalone, executable Python source code for:
1. **IBM Qiskit ($\ge 1.0.0$):** Using modern `QuantumCircuit`, `QuantumRegister`, `ClassicalRegister`, and `with qc.if_test():` classical branching.
2. **Google Cirq ($\ge 1.4.0$):** Using `cirq.Circuit`, `cirq.NamedQubit`, measurement keys, and `cirq.ClassicallyControlledOperation`.
3. **NVIDIA CUDA-Q ($\ge 0.8.0$):** Using `@cudaq.kernel`, `cudaq.qvector`, and `.ctrl` controlled gates ready for GPU simulation on Qniverse and PARAM supercomputing nodes.
4. **C-DAC Qniverse QSDK (Bonus / QC-C2-04):** Using documented `QniverseCircuit`, `add_gate`, `add_conditional_gate`, and remote job submission interfaces.

Every transpilation is verified by an automated **Mathematical Equivalence Engine** that executes the circuits on local simulation backends, normalizes framework bit-ordering conventions, and proves fidelity $|\langle \psi_{\text{target}} | \psi_{\text{ref}} \rangle| \approx 1.0$.

---

## 2. Architecture & Pipeline

```
OpenQASM 3.0 / 2.0 Source (.qasm or string)
                      │
                      ▼
             ┌──────────────────┐
             │    QASMLexer     │  Token stream with exact line:col locations
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │   QASM3Parser    │  Recursive-descent AST parser
             │  ExprEvaluator   │  Gate parameter math (pi, functions, consts)
             └────────┬─────────┘
                      │
                      ▼
             ┌──────────────────┐
             │    CircuitIR     │  Framework-agnostic immutable circuit model
             └────────┬─────────┘
                      │
         ┌────────────┼─────────────┬─────────────┐
         ▼            ▼             ▼             ▼
   ┌───────────┐ ┌──────────┐ ┌───────────┐ ┌───────────┐
   │  Qiskit   │ │   Cirq   │ │  CUDA-Q   │ │   QSDK    │
   │ Generator │ │ Generator│ │ Generator │ │ Generator │
   └─────┬─────┘ └────┬─────┘ └─────┬─────┘ └─────┬─────┘
         │            │             │             │
         └────────────┼─────────────┴─────────────┘
                      │
                      ▼
        ┌───────────────────────────┐
        │    Equivalence Engine     │  NumPy Statevector Reference
        │  (Bit-order Normalizer)   │  Fidelity & TVD Verification
        └─────────────┬─────────────┘
                      │
                      ▼
       Structured Transpile Report (JSON) + Executable Target Files
```

---

## 3. Supported Language Constructs & Gate Matrix

### Language Syntax
- **Version Headers:** `OPENQASM 3.0;`, `OPENQASM 3;`, `OPENQASM 2.0;`.
- **Includes:** `include "stdgates.inc";`, `include "qelib1.inc";`.
- **Declarations:** `qubit[n] q;`, `bit[n] c;`, `qreg q[n];`, `creg c[n];`.
- **Constants & Math:** `const float[64] theta = pi / 4;`, expressions with `+`, `-`, `*`, `/`, `**`, `sin`, `cos`, `tan`, `sqrt`, `exp`, `ln`, `abs`.
- **Custom Gate Definitions:** `gate my_u(theta) q { ... }` with automated AST inlining.
- **Register Broadcast:** `h q;` applies to all qubits in register `q`.
- **Modifiers:** `inv @ gate`, `pow(k) @ gate`, `ctrl @ gate`.
- **Control Flow:** `for i in [start:end] { ... }` (statically unrolled), `if (c == 1) { ... }`, `if (c[i] == 1) { ... }`.
- **Measurements:** `c = measure q;`, `c[0] = measure q[0];`, `measure q -> c;`.
- **Diagnostics:** Explicit line:column errors for unsupported dynamic constructs (`while`, `extern`, `def`, `delay`, `cal`).

### Gate Mapping Table

| OpenQASM Gate | Arity & Parameters | Qiskit ($\ge 1.0$) | Cirq ($\ge 1.4$) | NVIDIA CUDA-Q ($\ge 0.8$) | Qniverse QSDK |
|---|:---:|---|---|---|---|
| `id` | 1q, 0p | `qc.id(q)` | `cirq.I(q)` | `# Identity` | `qc.add_gate(id, q)` |
| `x` / `y` / `z` | 1q, 0p | `qc.x(q)`, `qc.y(q)`, `qc.z(q)` | `cirq.X(q)`, `cirq.Y(q)`, `cirq.Z(q)` | `cudaq.x(q)`, `cudaq.y(q)`, `cudaq.z(q)` | `qc.add_gate(x, q)` |
| `h` | 1q, 0p | `qc.h(q)` | `cirq.H(q)` | `cudaq.h(q)` | `qc.add_gate(h, q)` |
| `s` / `sdg` | 1q, 0p | `qc.s(q)`, `qc.sdg(q)` | `cirq.S(q)`, `cirq.S(q)**-1` | `cudaq.s(q)`, `cudaq.rz(-pi/2, q)` | `qc.add_gate(s, q)` |
| `t` / `tdg` | 1q, 0p | `qc.t(q)`, `qc.tdg(q)` | `cirq.T(q)`, `cirq.T(q)**-1` | `cudaq.t(q)`, `cudaq.rz(-pi/4, q)` | `qc.add_gate(t, q)` |
| `sx` / `sxdg` | 1q, 0p | `qc.sx(q)`, `qc.sxdg(q)` | `cirq.X(q)**0.5`, `cirq.X(q)**-0.5` | Decomposed | `qc.add_gate(sx, q)` |
| `p` / `rz` | 1q, 1p | `qc.p(lam, q)`, `qc.rz(phi, q)` | `cirq.ZPowGate(lam/pi)(q)`, `cirq.rz(phi)(q)` | `cudaq.rz(lam, q)` | `qc.add_gate(p(lam), q)` |
| `rx` / `ry` | 1q, 1p | `qc.rx(theta, q)`, `qc.ry(theta, q)` | `cirq.rx(theta)(q)`, `cirq.ry(theta)(q)` | `cudaq.rx(theta, q)`, `cudaq.ry(theta, q)` | `qc.add_gate(rx(theta), q)` |
| `u` / `u3` | 1q, 3p | `qc.u(th, ph, lam, q)` | Euler rotation sequence | Sequence of `rz, ry, rz` | `qc.add_gate(u3(th, ph, lam), q)` |
| `cx` / `cnot` | 2q, 0p | `qc.cx(c, t)` | `cirq.CNOT(c, t)` | `cudaq.x.ctrl(c, t)` | `qc.add_gate(cx, c, t)` |
| `cy` / `cz` / `ch`| 2q, 0p | `qc.cy(c, t)`, `qc.cz(c, t)`, `qc.ch(c, t)` | `cirq.Y(t).controlled_by(c)`, etc. | `cudaq.y.ctrl(c, t)`, `cudaq.z.ctrl(c, t)` | `qc.add_gate(cy, c, t)` |
| `swap` | 2q, 0p | `qc.swap(q0, q1)` | `cirq.SWAP(q0, q1)` | `cudaq.swap(q0, q1)` | `qc.add_gate(swap, q0, q1)` |
| `cp` / `crz` | 2q, 1p | `qc.cp(lam, c, t)`, `qc.crz(phi, c, t)` | `cirq.CZPowGate(lam/pi)(c, t)` | `cudaq.rz.ctrl(lam, c, t)` | `qc.add_gate(cp(lam), c, t)` |
| `crx` / `cry` | 2q, 1p | `qc.crx(th, c, t)`, `qc.cry(th, c, t)` | `cirq.rx(th)(t).controlled_by(c)` | `cudaq.rx.ctrl(th, c, t)` | `qc.add_gate(crx(th), c, t)` |
| `ccx` / `cswap` | 3q, 0p | `qc.ccx(c1, c2, t)`, `qc.cswap(c, t1, t2)` | `cirq.CCNOT(c1, c2, t)`, `cirq.CSWAP(...)` | `cudaq.x.ctrl([c1, c2], t)` | `qc.add_gate(ccx, c1, c2, t)` |
| `c3x`..`c5x` | 4-6q, 0p | `qc.mcx(controls, t)` | `cirq.X(t).controlled_by(*ctrls)` | `cudaq.x.ctrl(controls, t)` | `qc.add_gate(c3x, ...)` |
| `measure` | 1q->1c | `qc.measure(q, c)` | `cirq.measure(q, key='...')` | `var = cudaq.mz(q)` | `qc.add_gate('measure', q, c)` |
| `barrier` | nq, 0p | `qc.barrier(*qubits)` | `# Barrier` | `# Barrier` | `qc.add_gate('barrier', ...)` |
| `reset` | 1q, 0p | `qc.reset(q)` | `cirq.reset(q)` | `cudaq.reset(q)` | `qc.add_gate('reset', q)` |

---

## 4. How to Run

### Command-Line Interface (CLI)

```bash
# Transpile a file and verify equivalence against Qiskit, Cirq, CUDA-Q, and QSDK
python c2-03-qasm3-transpiler/transpiler_cli.py c2-03-qasm3-transpiler/sample_bell.qasm --targets qiskit cirq cudaq qniverse --verify

# Save generated code to an output directory
python c2-03-qasm3-transpiler/transpiler_cli.py c2-03-qasm3-transpiler/sample_qpe.qasm --targets qiskit cirq --out-dir ./generated_output
```

### Python API

```python
from qnvkit.transpile.api import transpile

qasm_code = """
OPENQASM 3.0;
qubit[2] q;
h q[0];
cx q[0], q[1];
"""

# Transpile across targets
results = transpile(qasm_code, targets=["qiskit", "cirq", "cudaq", "qniverse"], options={"verify": True})

# Inspect generated code and reports
for target, res in results.items():
    print(f"=== {target.upper()} Code ===")
    print(res.code)
    print(f"Report: {res.report.to_json()}")
```

### Running Test Suite

```bash
PYTHONPATH=src pytest tests/
```

---

## 5. Mathematical Equivalence Evidence

When `--verify` is passed, the transpiler verifies circuit equivalence:
1. **Reference Simulation:** Simulates the original circuit in pure NumPy without approximations.
2. **Execution on Target Engines:** Instantiates the generated Qiskit circuit in `qiskit.quantum_info.Statevector` and Cirq circuit in `cirq.Simulator`.
3. **Endianness Normalization:** Qiskit represents qubit 0 as least-significant bit (little-endian), whereas Cirq represents qubit 0 as most-significant bit (big-endian). The engine maps tensor indices to ensure mathematical comparison is invariant to bit-ordering:
   $$|\langle \psi_{\text{target, normalized}} | \psi_{\text{reference}} \rangle| \ge 1.0 - 10^{-6}$$
4. **Distribution Checks:** For circuits with final measurements, computes Total Variation Distance (TVD) over probability distributions.

---

## 6. Known Limitations & Framework Assumptions

1. **Dynamic Runtime Loops:** OpenQASM 3 `while` loops depend on real-time classical feedback during execution. Since target hardware and cloud simulators in Qniverse execute static compiled graphs, dynamic `while` loops are rejected with an explicit line:column diagnostic.
2. **Pulse Calibration (`defcal`):** Pulse-level timing controls (`delay`, `cal`) are flagged as unsupported, as the transpiler targets gate-level intermediate representations.
3. **Local CUDA-Q Execution:** When running on CPU-only workstations without CUDA-Q installed, the transpiler generates syntactically valid `@cudaq.kernel` code and marks local execution as skipped, ready for dispatch to Qniverse GPU nodes (`Param_Utkarsh` / `QACC_Cluster`).

---

## 7. Qniverse Platform Backend Compatibility Matrix

All frameworks transpiled by QC-C2-03 correspond directly to verified C-DAC Qniverse backend simulators available on **Param Utkarsh** and **QACC Cluster** (verified against `/wp-json/qacc/v1/backends`):

| Transpiler Target | Target Version | Supported Qniverse HPC Simulator | Processor | Cluster Target |
|---|---|---|---|---|
| **Qiskit** | `qiskit>=1.0.0` | `qasm_simulator`, `aer_simulator_statevector`, `aer_simulator_density_matrix` | CPU | `Param_Utkarsh`, `QACC_Cluster` |
| **Qiskit GPU** | `qiskit>=1.0.0` | `aer_simulator_statevector_gpu` (NVIDIA cuStateVec) | GPU | `Param_Utkarsh`, `QACC_Cluster` |
| **Cirq** | `cirq>=1.4.0` | `cirq_simulator`, `qsimcirq_simulator` (Google qsim) | CPU | `Param_Utkarsh`, `QACC_Cluster` |
| **Cirq GPU** | `cirq>=1.4.0` | `qsimcirq_cuquantum_gpu_simulator` (NVIDIA cuQuantum) | GPU | `QACC_Cluster` |
| **NVIDIA CUDA-Q** | `cudaq>=0.8.0` | `nvidia_cudaq_statevector_simulator` | GPU | `QACC_Cluster` |
| **C-DAC QSDK** | `QSDK (1.6+)` | Native `QniverseCircuit` via `to_qniverse()` / `run()` | CPU / GPU | `Param_Utkarsh`, `QACC_Cluster` |

