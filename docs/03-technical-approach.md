# 03 — Technical Approach (Deliverable #2)

> Fill in as we build. Rules §6.2 needs: problem statement, solution, algorithms and mathematics, architecture, references.

## Common foundation
- **IR / QniverseCircuit adapter:** one internal operation list (gate name, qubits, params, classical bits). A thin adapter converts to and from `QniverseCircuit` using only documented QSDK calls.
- **Depth (documented definition):** earliest-available-layer schedule. Each operation occupies one layer on all qubits it uses and must come after earlier operations on those qubits. Operations on disjoint qubits can share a layer. Non-unitary operations (measure, reset, barrier): _to document: which count as a layer, whether barriers add depth._
- **Equivalence checks:** unitary or statevector compare up to global phase; for circuits with measurement, compare distributions.

## Problem 1 — QC-C1-01 Profiling and basis decomposition
- **Profile:** total gates, by type, qubits declared/used, 1q / multi-q / 2q counts, depth, before and after.
- **Decomposition:** rewrite each non-basis gate into the chosen basis (identities to fill in: e.g. H = Rz·Ry·Rz up to phase, Toffoli to H/T/CX, SWAP to 3 CX). Copy measure/reset/barrier in order.
- **Unsupported:** if a gate cannot be decomposed, return an explicit report; never emit an invalid circuit.
- **Limitations:** _to fill in._

## Problem 2 — QC-C2-03 OpenQASM 3.0 transpiler to Qiskit, Cirq, CUDA-Q
- **Parser:** declarations, registers, gate definitions, parameter expressions, supported control flow; source locations for errors.
- **Generators:** one per target, using documented APIs for pinned versions. Preserve qubit mapping, measurement-to-classical-bit mapping, parameters, order.
- **Report:** target, status, warnings, unsupported constructs with locations.
- **Evidence:** run generated code on each framework's simulator; compare statevectors or distributions (watch bit-order conventions across frameworks).

## Problem 3 — QC-C3-03 Circuit optimisation
- **Rules:** remove identities; cancel adjacent self-inverse gates (X, H, Z, ...); cancel adjacent identical CX pairs.
- **Preconditions:** adjacent in operation order on the relevant wires; no barrier, measurement, reset, classical condition or intervening operation blocks it.
- **Non-mutating**, per-rule enable flags, unknown pass names rejected.
- **Report:** counts by type, total, depth before/after, passes applied, warnings. "No improvement" is valid.

## References
_Add books, papers, docs and repos as used (OpenQASM spec, Qiskit/Cirq/CUDA-Q docs, QSDK docs)._
