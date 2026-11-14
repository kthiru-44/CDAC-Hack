# CDAC-Hack — QOpt: Verified Compiler for Qniverse

PESU – C-DAC Quantum Hackathon 2026 (14 Nov 2026, 12 h, on C-DAC Qniverse).
**Domains:** 2 (circuit optimisation and compilation) + 3 (transpilation and framework interoperability).

> **One-liner:** Qniverse already converts a circuit into 7 frameworks, one way, unchecked. QOpt makes the circuit
> *better* (fewer gates, lower depth, higher fidelity), converts it both ways, and **proves** on many simulators
> that every version gives the same results.

## Why this fits Qniverse
Qniverse's composer turns one circuit (OpenQASM 2.0) into Qiskit / Cirq / CUDA-Q / Qulacs / QuEST code.
QOpt takes OpenQASM 2.0 in and returns optimised OpenQASM 2.0 out. Load the output back into the Qniverse
editor and **every framework Qniverse supports gets the optimised circuit at once**. We plug into what
C-DAC built and don't duplicate it.

## Repository layout
```
CDAC-Hack/
├── README.md                  ← you are here
├── docs/
│   ├── hackathon_rules.pdf    ← official rules sheet
│   ├── 01-strategy.md         ← rules digest, scoring and how we maximise it
│   ├── 02-qniverse-gap-analysis.md ← what Qniverse has and what QOpt adds
│   ├── 03-technical-approach.md    ← architecture, passes, verification, algorithms (deliverable #2)
│   ├── 04-performance-report.md    ← template for benchmarks/complexity (deliverable #3)
│   ├── 05-team-plan.md        ← roles, hour-by-hour timeline, checklist
│   ├── 06-proposal.md         ← one-page open-innovation pitch for the judges
│   ├── 07-ai-usage.md         ← mandatory AI/LLM declaration
│   └── 08-team-info.md        ← deliverable #1 (fill in)
├── src/qopt/                  ← (to build) optimiser package
├── benchmarks/                ← (to build) benchmark circuits and results
└── notebooks/                 ← (to build) Qniverse JupyterLab demo
```

## The five required deliverables (rules §6)
| # | Deliverable | Where |
|---|---|---|
| 1 | Team information | `docs/08-team-info.md` |
| 2 | Technical approach | `docs/03-technical-approach.md` |
| 3 | Performance evaluation report | `docs/04-performance-report.md` |
| 4 | Working product on Qniverse / Qniverse SDK | `src/qopt/` and `notebooks/` |
| 5 | Complete source code, dependencies, AI declaration | this repo, `requirements.txt`, `docs/07-ai-usage.md` |
