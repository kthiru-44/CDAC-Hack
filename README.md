# CDAC-Hack

PESU – C-DAC Quantum Hackathon 2026 (14 Nov 2026, 12 h, on C-DAC Qniverse).
We solve one published problem in each class (weights 0.4 / 0.3 / 0.2):

| Class | Problem |
|---|---|
| 1 | **QC-C1-01** Circuit profiling and limited basis-gate decomposition |
| 2 | **QC-C2-03** OpenQASM 3.0 transpiler to Qiskit, Cirq and CUDA-Q |
| 3 | **QC-C3-03** Quantum circuit optimisation using QSDK |

All three share one parser, IR and metrics module. See `docs/01-strategy.md` for the reasoning.

## Layout
```
docs/                 rules, strategy, open questions, technical approach, performance report, plan, AI declaration, team info, Qniverse integration note
Hackathon Problem set.pdf
src/                  (to build)
tests/                (to build)
notebooks/            (to build) Qniverse JupyterLab demo
```

## Required deliverables (rules §6)
1. Team information: `docs/08-team-info.md`
2. Technical approach: `docs/03-technical-approach.md`
3. Performance report: `docs/04-performance-report.md`
4. Working product on Qniverse / QSDK
5. Source, dependencies, AI declaration: this repo, `requirements.txt`, `docs/07-ai-usage.md`

Why this fits Qniverse and how it adapts: `docs/09-qniverse-integration.md`
