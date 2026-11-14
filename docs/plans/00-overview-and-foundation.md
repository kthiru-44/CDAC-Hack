# Overview and shared foundation — implement QC-C1-01, QC-C2-03, QC-C3-03 around the Qniverse QSDK


Three problem plans: `01-c1-01-profiling-decomposition.md`, `02-c2-03-qasm3-transpiler.md`, `03-c3-03-optimizer.md`. Each can be executed on a different computer after Stage 0 and the foundation (Stage 1) are in place.

## What the documentation fixes (design constraints)
- **Qniverse JupyterLab: Python 3.9.13, Qiskit 1.1.1, Aer 0.14.2, NumPy 1.26.4, 4 GB RAM.** So: all core code is **Python 3.9-compatible** and depends only on **numpy + qniverse**. Cirq ≥ 1.4 and current CUDA-Q need Python ≥ 3.10, so they cannot be assumed there; code *generation* must not need the target framework installed.
- **Documented QSDK surface (use only this):** `QniverseCircuit()`, `QuantumRegister(n,'q')`, `ClassicalRegister(n,'c')`, `add_register`, `add_gate(gate, *bits)` (last qubit = target), `add_conditional_gate(creg, value, gate, *qubits)`, `measure_all()`, `add_module(qft|iqft, ...)`, `initialize`, `qasm()` (OpenQASM 2.0 export), `list_gates()`, `draw`; `Backend().processor().hpc().simulator()` in that order, `Backend.get_processor/get_hpc/get_simulator`; `run(qc, backend, shots, token=, job_name=)`, `fetch_job_result`, `job_status`, `transpiled_code`, `credit_balance`. `token` must be a global variable before `Backend()`.
- **40 gates:** `id x y z h s t sdg tdg p rx ry rz u1 u2 u3 | cx cy cz ch swap cs ct csdg ctdg cp crx cry crz cu1 cu2 cu3 | ccx cswap c3x c4x c5x | reset measure barrier`. A "basis gate set" (C1-01) is a subset of these names (so no `sx`).
- **No documented way to read operations back** except `qc.qasm()`. There is no QASM importer. So the adapter reads a circuit via `qc.qasm()` + our own QASM 2 parser and writes via `add_register/add_gate`. This also means inputs are never mutated.
- Simulators reachable through the QSDK include `qasm_simulator`, `aer_simulator_statevector`, `cirq_simulator` (no conditionals), `quest_simulator`, `qulacs_multicpu_simulator`, `nvidia_cudaq_statevector_simulator` (GPU). CPU job = 5 credits, GPU = 10. Circuits need ≥ 1 measurement to run.

## Stage 0 — setup and QSDK probe (main session, before any agent)
1. **Secrets:** the keys file is named `env`, which `.gitignore` does **not** cover (it ignores `.env`). Rename `env` → `.env` so the four keys can never be committed. Keys are read from the environment only, never printed or written to docs/tests.
2. `uv` venvs: `.venv39` (Python 3.9, numpy, qniverse, pytest, hypothesis, qiskit 1.1.1 + aer — mirrors JupyterLab) and `.venv312` (qiskit ≥ 1.0, cirq ≥ 1.4, cudaq, for cross-framework checks). Add `requirements.txt` / `requirements-dev.txt`.
3. `pip install qniverse` and **probe** (write results to `docs/10-qsdk-probe.md`): import name casing (`Qniverse` vs `qniverse`), whether `qc.qasm()` returns or prints, exact QASM text for every gate (e.g. `cp` vs `cu1`, `id`, barrier, conditional `if(c==k)`, `measure_all`, `qft` module, `initialize`), `list_gates()` output, how `token` is looked up, and (2–3 live jobs) the result format and **bit order** (`x q[0]` on 2 qubits).
4. If `qniverse` is not installable locally: build against a tiny shim that implements only the documented interface (tests only), and run the real thing in Qniverse JupyterLab. I will tell you if this happens.
5. Write `docs/11-contracts.md`: the interfaces below, so parallel agents code against fixed signatures.

## Architecture (one package, `src/qnvkit/`)
```
ir.py            Circuit IR: registers, Op(name, qubits, params, clbits, condition); immutable copies
gates.py         Registry of the 40 QSDK gates: arity, params, numpy matrix, inverse, self-inverse flag
qsdk_adapter.py  ONLY file that imports Qniverse: from_qniverse(qc) via qc.qasm(); to_qniverse(ir) via add_gate
qasm/            lexer.py, expr.py (pi, + - * / **, sin/cos/...), parser2.py, parser3.py, emit.py, diagnostics.py (line:col)
sim.py           numpy statevector/unitary simulator; equivalence up to global phase; counts/TVD comparison
metrics.py       profile(): counts + depth (single definition shared by C1 and C3)
report.py        shared JSON-able report types (status, metrics, warnings, unsupported)
decompose/       C1-01: rules.py (registry), euler.py, decomposer.py
transpile/       C2-03: qiskit_gen.py, cirq_gen.py, cudaq_gen.py, api.py, verify.py
optimize/        C3-03: passes.py (registry), optimizer.py
runner.py        Backend/run/fetch_job_result wrapper with a job-count cap
tests/  examples/  notebooks/ (one demo notebook per problem, runnable in Qniverse JupyterLab)
```
Adaptability: if the QSDK changes, only `qsdk_adapter.py` changes; gates, decomposition rules, rewrite passes and code-gen targets are registry entries (one entry + one test to add).

## Execution with subagents
1. **Stage 0** (me): setup, probe, contracts, commit.
2. **Stage 1 — foundation agent (1):** `ir`, `gates`, `sim`, `metrics`, `qasm` (lexer, expr, QASM 2 parser, emitter), `qsdk_adapter`, `report`, `runner`, tests.
3. **Stage 2 — three agents in parallel**, disjoint directories: `decompose/` (C1), `qasm/parser3.py` + `transpile/` (C2), `optimize/` (C3). Each writes its tests, example, and a problem README (run instructions, definitions, supported list, limitations). C1 gets priority if anything contends, because its checkpoint is first.
4. **Stage 3 — integration** (me): review all code, full test run on 3.9 and 3.12, live Qniverse smoke jobs, three demo notebooks, fill `docs/03-technical-approach.md`, `04-performance-report.md`, `07-ai-usage.md` (models: Sonnet 5.5 and Fable 5.2).
- **Credits:** live jobs use the primary key only, hard cap ~30 jobs total (≈150 credits), balance checked first.
- **Git:** commit at the end of each stage; push when you ask.

## Verification
- `.venv39/bin/pytest` (core, mirrors Qniverse JupyterLab) and `.venv312/bin/pytest -m frameworks` (generated Qiskit/Cirq/CUDA-Q code actually executed).
- `python examples/c1_demo.py`, `c2_demo.py`, `c3_demo.py`: print reports, before/after metrics and equivalence results.
- Live: each demo's `--live` flag submits a small circuit through the QSDK and compares results to the local simulator.
- Final manual check: open the three notebooks in Qniverse JupyterLab (Python 3.9) and run all cells.

## Risks
- `qniverse` not installable locally, or `qc.qasm()` behaves differently than documented → shim + JupyterLab run (Stage 0 decides).
- CUDA-Q wheel unavailable on this machine → CUDA-Q code checked via the Qniverse `nvidia_cudaq_statevector_simulator` route and reported as "generated, not executed locally".
- Time: C1 must be demo-ready by checkpoint 1; extras in every problem are cut before mandatory items.
