# Plan for QC-C1-01

Shared context, constraints, package layout and setup are in `00-overview-and-foundation.md` (read it first: Python 3.9 target, documented QSDK surface only, `src/qnvkit/` layout, interfaces).

## Problem 1 — QC-C1-01 (do first; checkpoint 1)
- **API:** `profile(qc) -> ProfileReport`; `decompose(qc, basis) -> DecomposeResult(circuit: QniverseCircuit | None, before, after, unsupported, verified)`.
- **Validation:** reject `None`/non-circuit, empty basis, basis names not in the gate list (message names the offenders).
- **Metrics:** total gates, by type, qubits declared and used, 1-qubit / multi-qubit / 2-qubit counts, depth; measure/reset/barrier counted separately. **Depth:** earliest-available layer; an op takes one layer on every qubit (and classical bit) it touches; measure and reset take a layer; barrier takes no layer but aligns its qubits (documented).
- **Decomposition:** rule graph, expanded recursively with a cycle guard until every gate is in the basis:
  - multi-qubit → smaller: `c5x/c4x/c3x → ccx`, `ccx → h,t,tdg,cx` (6 CX), `cswap → cx,ccx`, `swap → 3 cx`, `cz/cy/ch`, `crx/cry/crz/cp/cu1/cu2/cu3/cs/ct/csdg/ctdg → 1-qubit rotations + cx`; `cx ↔ cz` via `h`.
  - 1-qubit: compute the 2×2 matrix and Euler-synthesise into whatever the basis offers (`u3`; `rz+ry`; `rz+rx`; `rx+ry`; `p/u1` for diagonal). Discrete bases (`h,s,t,...`): exact word lookup; if no exact word exists → unsupported.
  - no entangling gate in basis but one is needed → unsupported.
- Measure, reset, barrier copied in order. Conditional gates keep their condition on every emitted gate (flagged in report). Anything not representable → **explicit unsupported report, `circuit=None`**, never an invalid circuit.
- **Evidence:** every rule × several bases (`{rx,ry,rz,cx}`, `{u3,cx}`, `{h,t,tdg,s,cx}`, `{rz,ry,cz}`) auto-checked by unitary comparison up to global phase; random-circuit fuzz; input QASM identical before/after; one unsupported example.

