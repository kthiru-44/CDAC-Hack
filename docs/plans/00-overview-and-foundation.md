# 00 — Overview and Shared Foundation Plan
**Project:** PESU – C-DAC Quantum Hackathon Tooling (`src/qnvkit/`)  
**Targets:** QC-C1-01 (Class I), QC-C2-03 (Class II), QC-03-03 (Class III)  
**Status:** Stage 0 & Stage 1 Complete | C1-01 Complete | Foundation Ready for Parallel Subagents  

---

## 1. Problem Landscape & Scope

The repository provides a single, high-performance, modular Python package (`qnvkit`) solving three problems from the PESU – C-DAC Quantum Hackathon:
1. **QC-C1-01 (Class I — Checkpoint 1, ~Hour 3):** Circuit Profiling & Limited Basis-Gate Decomposition (`src/qnvkit/decompose/`).
2. **QC-C2-03 (Class II — Checkpoint 2, Mid-event):** OpenQASM 3.0 Transpiler to Qiskit, Cirq, and CUDA-Q (`src/qnvkit/transpile/`).
3. **QC-03-03 (Class III — Final Checkpoint):** Safe Local Rewrite-Rule Quantum Circuit Optimizer (`src/qnvkit/optimize/`).

Individual implementation plans:
- `docs/plans/01-c1-01-profiling-decomposition.md` (Class I)
- `docs/plans/02-c2-03-qasm3-transpiler.md` (Class II)
- `docs/plans/03-c3-03-optimizer.md` (Class III)

---

## 2. Hard Platform Constraints & Design Invariants

- **Qniverse JupyterLab Runtime:** Python 3.9.13, Qiskit 1.1.1, Aer 0.14.2, NumPy 1.26.4, 4 GB RAM.
  - **Rule:** All core modules, IR, profiler, and decomposer must run seamlessly in Python 3.9 using only `numpy` + `qniverse`.
  - Cirq ≥ 1.4 and CUDA-Q require Python ≥ 3.10; therefore, transpilation code generation must emit valid target scripts without requiring those frameworks installed in Qniverse JupyterLab.
- **Documented QSDK Surface:**
  - `QniverseCircuit()`, `QuantumRegister(n, 'q')`, `ClassicalRegister(n, 'c')`
  - `add_register`, `add_gate(gate, *bits)` (last qubit = target for controlled gates)
  - `add_conditional_gate(creg, value, gate, *qubits)`
  - `measure_all()`, `qasm()` (OpenQASM 2.0 export), `list_gates()`, `draw()`
  - `Backend().processor().hpc().simulator()` (strict order required)
  - `run(qc, backend, shots, token=, job_name=)`, `fetch_job_result`, `job_status`, `credit_balance`
  - Global `token = "..."` declared prior to `Backend()`.
- **The 40 Documented QSDK Gates:**
  `id`, `x`, `y`, `z`, `h`, `s`, `t`, `sdg`, `tdg`, `p`, `rx`, `ry`, `rz`, `u1`, `u2`, `u3`, `cx`, `cy`, `cz`, `ch`, `swap`, `cs`, `ct`, `csdg`, `ctdg`, `cp`, `crx`, `cry`, `crz`, `cu1`, `cu2`, `cu3`, `ccx`, `cswap`, `c3x`, `c4x`, `c5x`, `reset`, `measure`, `barrier`.
- **No Documented QASM Importer:** Because QSDK lacks a circuit reader, `qsdk_adapter.py` reads a circuit via `qc.qasm()` + our internal OpenQASM 2.0 parser, and writes back via `add_register` / `add_gate`. Input circuits are guaranteed **100% immutable**.
- **Credit Frugality:** CPU simulation = 5 credits; GPU simulation = 10–15 credits. 100% of testing runs locally using our NumPy simulator (0 credits).

---

## 3. Package Architecture (`src/qnvkit/`)

```
src/qnvkit/
├── __init__.py          # Public API: Op, CircuitIR, ProfileReport, DecomposeResult, profile, decompose
├── ir.py                # Immutable Circuit IR: Op, Register, CircuitIR, fingerprint, copy
├── gates.py             # Complete registry of all 40 QSDK gates: arity, params, matrices, self-inverses
├── metrics.py           # Earliest-available-layer scheduled depth & gate counting (shared by C1 and C3)
├── sim.py               # Pure NumPy unitary and statevector simulator with global phase invariant check
├── report.py            # Standardized dataclasses: ProfileReport, DecomposeResult, UnsupportedReport, OptimizeResult
├── qsdk_adapter.py      # ONLY file that imports Qniverse: from_qniverse(qc) / to_qniverse(ir)
├── runner.py            # Guarded QniverseRunner with job-count quota cap to protect account credits
│
├── qasm/                # OpenQASM Parsing & Code Generation Core
│   ├── expr.py          # Safe parameter expression evaluator (pi, sin, cos, +, -, *, /, **)
│   ├── lexer.py         # Universal QASM 2 / 3 tokenizer with line:col SourceLocation tracking
│   ├── diagnostics.py   # Pretty compiler error formatting with source pointers
│   ├── parser2.py       # OpenQASM 2.0 parser reading qc.qasm()
│   ├── parser3.py       # OpenQASM 3.0 recursive-descent parser (C2-03)
│   └── emit.py          # OpenQASM 2.0 and 3.0 code emitter
│
├── shim/                # Zero-credit local development mock
│   └── Qniverse/        # Drop-in mock package mirroring live Qniverse classes and functions
│
├── decompose/           # QC-C1-01: Profiling & Basis Gate Decomposition
│   ├── euler.py         # Exact Z-Y-Z Euler decomposition & Clifford+T discrete mapping
│   ├── rules.py         # Rule graph: Toffoli (6 CX), Fredkin, SWAP (3 CX), CZ, CY, CH, CRx, CRy, CRz, CU3
│   └── decomposer.py    # Recursive decomposer with cycle guard and explicit unsupported reporting
│
├── transpile/           # QC-C2-03: OpenQASM 3.0 Transpiler
│   ├── qiskit_gen.py    # Target code generator for Qiskit >= 1.0.0
│   ├── cirq_gen.py      # Target code generator for Cirq >= 1.4.0
│   ├── cudaq_gen.py     # Target code generator for CUDA-Q >= 0.8.0
│   ├── api.py           # Unified transpile() interface
│   └── verify.py        # Cross-framework verification against local & Qniverse simulators
│
└── optimize/            # QC-03-03: Safe Quantum Circuit Optimizer
    ├── passes.py        # Rewrite rules: remove_identity, cancel_self_inverse, cancel_cx, merge_rotations
    └── optimizer.py     # Causal wire adjacency engine with strict barrier & measurement guards
```

---

## 4. Execution Roadmap & Stage Status

### Stage 0: Setup and QSDK Probe (COMPLETED)
- [x] Secrets: `.env` and `env` secured and covered by `.gitignore`. Tested with `git check-ignore`.
- [x] Environments: Created `.venv39` (mirrors Qniverse JupyterLab) and `.venv312` (for cross-framework checks).
- [x] Probed live Qniverse REST API (`https://qniverse.in/wp-json/qacc/v1/backends` -> HTTP 200).
- [x] Documented probe results in [`docs/10-qsdk-probe.md`](../10-qsdk-probe.md).
- [x] Defined fixed interface signatures in [`docs/11-contracts.md`](../11-contracts.md).

### Stage 1: Shared Foundation (COMPLETED)
- [x] `src/qnvkit/ir.py`: Immutable `CircuitIR` with SHA-256 fingerprinting.
- [x] `src/qnvkit/gates.py`: Full registry of 40 gates with self-inverse and inverse flags.
- [x] `src/qnvkit/metrics.py`: Earliest-available-layer scheduled depth and gate counts.
- [x] `src/qnvkit/sim.py`: Exact matrix and statevector simulator with trace fidelity $| \text{Tr}(U_a^\dagger U_b) | / 2^n \ge 1 - 10^{-5}$.
- [x] `src/qnvkit/qasm/`: `expr.py`, `lexer.py`, `diagnostics.py`, `parser2.py`, `emit.py`.
- [x] `src/qnvkit/qsdk_adapter.py`: Bidirectional bridge to `QniverseCircuit`.
- [x] `src/qnvkit/shim/Qniverse/`: Zero-credit drop-in mock package for local offline testing.
- [x] `src/qnvkit/runner.py`: Guarded cloud runner with credit cap.
- [x] Comprehensive foundation tests in `tests/test_ir_and_adapter.py`, `tests/test_gates.py`, `tests/test_metrics.py`, `tests/test_sim.py`, `tests/test_lexer.py`.

### Stage 2: Parallel Problem Sprints
- [x] **QC-C1-01 (COMPLETED):**
  - Profiler & basis decomposer into `{rx, ry, rz, cx}`, `{u3, cx}`, `{h, t, tdg, s, cx}`, `{rz, ry, cz}`.
  - Toffoli decomposed with canonical 6 CX gates.
  - Negative tests: entangling circuits without entangling basis gates, continuous rotations in discrete basis.
  - Unit tests and Hypothesis property-based fuzzing passed (`tests/test_c1_decomposer.py`, `tests/test_c1_fuzz.py`).
  - Standalone demo: `examples/c1_demo.py`. User guide: `docs/c1-01-user-guide.md`.
- [x] **QC-C2-03 (COMPLETED):**
  - Robust recursive-descent OpenQASM 3.0 / 2.0 parser with line:column diagnostic reporting in `src/qnvkit/qasm/parser3.py`.
  - Full AST mathematical expression evaluator in `src/qnvkit/qasm/expr.py` supporting `pi`, trigonometric, and user constants.
  - Features supported: register broadcasts (`h q;`), custom gate inlining with parameter/wire substitution, modifiers (`inv@`, `pow@`, `ctrl@`), unrolled `for`-loops over ranges, classical conditional execution, and both measurement styles.
  - Target code generators in `src/qnvkit/transpile/`:
    - `qiskit_gen.py`: Modern Qiskit $\ge 1.0.0$ code with `if_test` blocks and standalone runner.
    - `cirq_gen.py`: Cirq $\ge 1.4.0$ code with `NamedQubit` mapping and `KeyCondition` controls.
    - `cudaq_gen.py`: NVIDIA CUDA-Q $\ge 0.8.0$ `@cudaq.kernel` code with `.ctrl` modifiers.
    - `qniverse_gen.py`: Standalone C-DAC QSDK code runnable locally or on PARAM / QACC clusters.
  - Cross-framework equivalence verifier in `src/qnvkit/transpile/verify.py` with little-endian vs big-endian normalization.
  - Dedicated problem workspace: `c2-03-qasm3-transpiler/` with `transpiler_cli.py`, `README.md`, sample QASM 3 files (`sample_bell.qasm`, `sample_ghz.qasm`, `sample_qpe.qasm`).
  - Standalone demonstration: `examples/c2_demo.py`.
  - Comprehensive unit and integration test suite passing 100% across all targets.
- [ ] **QC-C3-03 (Next):** Safe rewrite-rule optimizer with causal DAG adjacency and barrier guards.

### Stage 3: Integration, Demonstration & Viva Defense
- [ ] Full end-to-end test run across Python 3.9 and 3.12.
- [ ] Three interactive Jupyter notebooks in `notebooks/` runnable inside Qniverse JupyterLab.
- [ ] Exactly 1 curated live verification run per problem on Qniverse Cloud (using $\le 15$ credits total).
- [ ] Final performance report in `docs/04-performance-report.md` and AI usage declaration in `docs/07-ai-usage.md`.

---

## 5. Verification Command Matrix

```bash
# 1. Run all core foundation and C1-01 tests (Python 3.9)
.venv39/bin/pytest -q --tb=short

# 2. Run property-based fuzzing test suite
.venv39/bin/pytest -q --tb=short tests/test_c1_fuzz.py

# 3. Run QC-C1-01 standalone demonstration
.venv39/bin/python examples/c1_demo.py

# 4. Optional: Run QC-C1-01 demo against live Qniverse cloud
.venv39/bin/python examples/c1_demo.py --live
```
