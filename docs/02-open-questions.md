# 02 — Questions for the C-DAC representatives (first hour)

The QSDK documentation web page was a redirect stub, but **Tutorial Session 2 (07-11-2026)** provided a full walkthrough of the QSDK architecture. See [`docs/tutorial-sessions-documentation.md`](tutorial-sessions-documentation.md) for full code examples and API details.

### Already Answered from Tutorial Session 2:
1. **Python package name & construction:**
   - Package: `Qniverse` (or `qniverse`).
   - Imports: `from Qniverse.QniverseCircuit import *`, `from Qniverse.gates import *`, `from Qniverse.backend import Backend`, `from Qniverse.api import run, fetch_job_result, transpiled_code, get_backend`.
   - Construction: `qc = QniverseCircuit()`, `q = QuantumRegister(2, 'q')`, `c = ClassicalRegister(2, 'c')`, `qc.add_register(q)`, `qc.add_register(c)`.
   - Gates: `qc.add_gate(h, q[0])`, `qc.add_gate(cx, q[0], q[1])`, `qc.measure_all()` or `qc.add_gate(measure, q[0], c[0])`.
2. **Supported gate names and conventions:**
   - 40 documented gates! Single: `id, x, y, z, h, s, t, sdg, tdg, p, rx, ry, rz, u1, u2, u3`. Controlled: `cx, cy, cz, ch, swap, cs, ct, csdg, ctdg, cp, crx, cry, crz, cu1, cu2, cu3`. Multi: `ccx, cswap, c3x, c4x, c5x`. Utility: `reset, measure, barrier`.
   - In controlled gates, **the last qubit argument is always the target** (e.g. `qc.add_gate(cx, q_control, q_target)`).
   - Rotation angles are passed in radians using NumPy (`rx(np.pi / 2)`).
   - Introspection: `qc.list_gates()`.
3. **Reading operations from `QniverseCircuit`:**
   - `qc.qasm()` exports the full circuit as an OpenQASM 2.0 string.
   - `qc.get_registers()` returns `[('quantum', 'q', n), ('classical', 'c', m)]`.
   - In Python, `qc` has internal operation attributes, but parsing `qc.qasm()` or wrapping `add_gate` in an adapter is 100% deterministic and safe.
5. **QASM import/export in QSDK:**
   - `qc.qasm()` exports QASM 2.0.
   - QSDK does NOT have a built-in QASM importer (which is why problem QC-C2-04 was proposed). We must parse QASM ourselves.

---

### Clarified Requirements:
1. **Target Framework Versions (C2-03):** Must target the **latest stable versions** (Qiskit 1.0+, Cirq 1.4+, CUDA-Q 0.8+/0.9+).
2. **Evaluation Weights:** 
   - **0.4 (40%):** Actual working project / product delivery.
   - **0.3 (30%):** Judges' evaluations.
   - **0.2 (20%):** Presentation + viva voce.

---

### Questions to Clarify with C-DAC Reps on the Floor:
1. Can we pip-install external packages (`qiskit`, `cirq`, `openqasm3`) inside the Qniverse JupyterLab environment without proxy or network restrictions?
2. If CUDA-Q cannot run natively inside CPU-only JupyterLab instances, will the judges evaluate CUDA-Q code generation statically or via GPU backend access?
