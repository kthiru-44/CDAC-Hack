# Plan for QC-C2-03

Shared context, constraints, package layout and setup are in `00-overview-and-foundation.md` (read it first: Python 3.9 target, documented QSDK surface only, `src/qnvkit/` layout, interfaces).

## Problem 2 — QC-C2-03 (checkpoint 2)
- **API:** `transpile(source: str | path, targets=("qiskit","cirq","cudaq"), options=None) -> {target: {code, report}}`; report = target, status, warnings, unsupported constructs with line:col, targeted framework version.
- **Parser (own recursive-descent, no dependency):** `OPENQASM 3;`, `include "stdgates.inc"`, `qubit[n]`/`bit[n]` (and `qreg/creg`), all stdgates + `U`, parameter expressions and `const`, register broadcast, `gate` definitions (inlined), modifiers `inv @`, `pow(int) @`, `ctrl @` where a controlled form exists, `barrier`, `reset`, both measurement forms, `if (c == k)` / `if (c[i] == 1)`, `for` over ranges (unrolled). Everything else (`while`, `def`, `extern`, `delay`, `cal`, arrays, `input`) → explicit unsupported diagnostic with location. Invalid QASM → rejected with line:col.
- **Generators** emit standalone runnable source (a `build_circuit()` plus a `__main__` that simulates and prints counts): Qiskit ≥ 1.0 (`if_test`, no `execute`), Cirq ≥ 1.4 (`LineQubit`, measurement keys, classical controls), CUDA-Q ≥ 0.9 (`@cudaq.kernel`, `qvector`, `mz`, `.ctrl`). When a target lacks a gate natively, fall back to the C1 decomposer and add a warning. Qubit/register mapping and measurement→bit mapping preserved; bit-order convention documented.
- **Evidence (`transpile/verify.py`):** run each generated program in `.venv312`, compare statevector/counts with our reference simulator (bit order normalised); frameworks not installed are reported as "not run", never faked. **Qniverse route:** the same IR → `QniverseCircuit` → `run()` on `qasm_simulator`, `cirq_simulator`, `nvidia_cudaq_statevector_simulator`, compare distributions. This also gives `qasm_to_qniverse()` (problem C2-04) as a by-product.

