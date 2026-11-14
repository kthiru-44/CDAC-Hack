# 09 — Why this fits Qniverse: integration and adaptability

Aim: show that our three modules are the best fit to drop into Qniverse, with clear documentation and easy adaptation.

## Fit with what Qniverse does today
| Qniverse today | Our module | Benefit |
|---|---|---|
| Composer and editor generate code for 7 frameworks, one way, read-only for Qiskit/Cirq/CudaQ | **C2-03** OpenQASM 3 transpiler with cross-framework equivalence matrix | Users can trust generated code, and QASM 3 becomes a first-class input |
| Circuits auto-transpiled to a fixed {Rx, Ry, Rz, CX} basis with no profile | **C1-01** profiler and user-selectable basis decomposition | Users see gate and depth metrics and choose the basis |
| Circuits run as written | **C3-03** safe, documented rewrite rules with before/after report | Fewer gates and lower depth, with evidence of equivalence |

## Design principles for adaptability
1. **Thin QSDK adapter.** All `QniverseCircuit` access lives in one module. The rest of the code uses a small internal IR. If the SDK changes, only the adapter changes.
2. **Documented APIs only.** No undocumented constructors, gate names or registration calls (a rule in the problem sets).
3. **Non-mutating, pure functions.** Input in, new circuit and structured report out. Safe to call from the composer, a notebook or a service.
4. **Plugin-style registries.** Basis-decomposition rules, rewrite rules and target generators are registered entries. Adding a gate, a rule or a framework target is one new entry plus its test.
5. **Structured JSON reports.** Same schema across modules (status, metrics, warnings, unsupported items), ready for a UI to render.
6. **Version-pinned targets.** Generated code states the framework version it targets.
7. **Pip-installable package** with tests and a README, so C-DAC could merge it.

## Evidence we will show
- Each module runs inside the Qniverse JupyterLab using the QSDK.
- Automated equivalence checks for every transformation (see the evidence engine in `01-strategy.md`).
- A walkthrough of adding one new gate, one new rewrite rule and one new target framework, to prove the registries work.
- Documentation per module: supported constructs, metric definitions, limitations.

## Documentation we will ship
Per problem: run instructions, sample input and output, tests and results, supported-construct list, known limitations. Plus the architecture note in `03-technical-approach.md` and the performance report in `04-performance-report.md`.
