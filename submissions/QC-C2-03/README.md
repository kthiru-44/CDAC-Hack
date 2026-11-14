# QC-C2-03: OpenQASM 3.0 Transpiler across Qiskit, Cirq, CUDA-Q & QSDK
**PESU – C-DAC Quantum Hackathon 2026**

## Quick Start for Evaluators & Judges

To reproduce full multi-target code generation across all 4 frameworks, cross-framework TVD tables, and compiler diagnostics in **under 3 seconds**:

```bash
# 1. (Optional) Create clean virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run automated judge reproduction script
python reproduce_c2.py
```

---

## Submission Package Contents

- **`reproduce_c2.py`**: Standalone CLI evaluation script testing all 3 OpenQASM 3 circuits across Qiskit, Cirq, CUDA-Q, and QSDK, with TVD verification and compiler diagnostics.
- **`notebooks/c2_demo.ipynb`**: Standard modular Jupyter demonstration notebook with selectable `CIRCUIT_CHOICE = 1, 2, or 3`.
- **`notebooks/c2_demo_standalone.ipynb`**: Single-file uploadable standalone notebook for Qniverse JupyterLab (embeds pure-Python `qnvkit`).
- **`evidence/c2_demo_standalone.pdf`**: Official Firefox PDF printout from live execution on Qniverse JupyterLab showing cloud execution (`Job ID: 38069`) and matching counts.
- **`figures/`**: High-resolution 150 DPI vector-extracted PNG images of notebook cell outputs, circuit diagrams, and cross-framework tables.
- **`src/qnvkit/`**: Full source code of the `qnvkit` engine (`transpile/`, `qasm/`, `sim.py`, `qsdk_adapter.py`).
- **`DOCUMENTATION_AND_ANALYSIS.md`**: Complete technical documentation, theoretical TVD analysis, target code generation mappings, empirical tables, and proofs.
- **`requirements.txt` / `pyproject.toml`**: Environment dependency specifications.

---

## Summary of Results

### Cross-Framework Verification Table (1024 Shots)

```
outcome    exact p  original    qiskit      cirq    qniverse
----------------------------------------------------------------
000         0.5000       552       502       515         514
111         0.5000       472       522       509         510
----------------------------------------------------------------
TVD                   0.0391    0.0098    0.0029      0.0020
match                    yes       yes       yes         yes
```

- **All 4 Targets Transpiled:** Qiskit (dynamic with `if_test`), Cirq (`controlled_by`), CUDA-Q (valid C++20 QPU kernels), and QSDK (`QniverseCircuit` builder).
- **Static Fidelity:** Unitary fidelity $= 0.9999999999999993$ on QSDK static circuits.
- **Live Cloud Run:** Completed on Qniverse HPC cluster with `Job ID: 38069`.
- **Diagnostics:** Exact `line:col` diagnostic errors on bad syntax; graceful isolation of unsupported constructs.
- **Detailed Report:** See [DOCUMENTATION_AND_ANALYSIS.md](DOCUMENTATION_AND_ANALYSIS.md).
