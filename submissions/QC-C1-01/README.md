# QC-C1-01: Circuit Profiling and Limited Basis-Gate Decomposition
**PESU – C-DAC Quantum Hackathon 2026**

## Quick Start for Evaluators & Judges

To reproduce all profiling metrics, basis decompositions, fidelity checks, and immutability guarantees in **under 3 seconds**:

```bash
# 1. (Optional) Create clean virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run automated judge reproduction script
python reproduce_c1.py
```

---

## Submission Package Contents

- **`reproduce_c1.py`**: Standalone CLI evaluation script verifying profiling, 4 basis decompositions, mathematical fidelities ($1.00000000$), and negative test guardrails.
- **`notebooks/c1_demo.ipynb`**: Standard modular Jupyter demonstration notebook.
- **`notebooks/c1_demo_standalone.ipynb`**: Single-file uploadable standalone notebook for Qniverse JupyterLab (embeds pure-Python `qnvkit`).
- **`src/qnvkit/`**: Full source code of the `qnvkit` engine (`metrics/profiler.py`, `decompose/decomposer.py`, `sim.py`, `qsdk_adapter.py`).
- **`DOCUMENTATION_AND_ANALYSIS.md`**: Complete technical documentation, theoretical DAG scheduling analysis, decomposition rules, empirical tables, and proofs.
- **`requirements.txt` / `pyproject.toml`**: Environment dependency specifications.

---

## Summary of Results

| Target Basis Set | Gate Reduction / Expansion | Depth | Unitary Fidelity | Result |
| :--- | :---: | :---: | :---: | :---: |
| **`{rx, ry, rz, cx}`** | $9 \to 37$ | $8 \to 26$ | **1.00000000** | **PASSED** |
| **`{u3, cx}`** | $9 \to 30$ | $8 \to 22$ | **1.00000000** | **PASSED** |
| **`{rz, ry, cz}`** | $9 \to 81$ | $8 \to 55$ | **1.00000000** | **PASSED** |
| **`{rx, rz, cx}`** | $9 \to 49$ | $8 \to 33$ | **1.00000000** | **PASSED** |

- **Functional Immutability:** Input `QniverseCircuit` is completely untouched.
- **Guardrails:** Missing entangler basis safely flagged; invalid basis sets rejected.
- **Detailed Report:** See [DOCUMENTATION_AND_ANALYSIS.md](DOCUMENTATION_AND_ANALYSIS.md).
