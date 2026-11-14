# QC-C3-03: Quantum Circuit Optimization Using QSDK
**PESU – C-DAC Quantum Hackathon 2026**

## Quick Start for Evaluators & Judges

To reproduce full circuit optimization, discrete pass verifications (Tests A-F), barrier guardrails, and 1024-shot distributions in **under 3 seconds**:

```bash
# 1. (Optional) Create clean virtual environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Run automated judge reproduction script
python reproduce_c3.py
```

---

## Submission Package Contents

- **`reproduce_c3.py`**: Standalone CLI evaluation script testing all 3 benchmark circuits, discrete rewrite rules A-F, 4-qubit benchmark, barrier negative test assertion, and unitary fidelity proofs ($1.00000000$).
- **`notebooks/c3_demo.ipynb`**: Standard modular Jupyter demonstration notebook with selectable `CIRCUIT_CHOICE = 1, 2, or 3`.
- **`notebooks/c3_demo_standalone.ipynb`**: Single-file uploadable standalone notebook for Qniverse JupyterLab (embeds pure-Python `qnvkit`).
- **`evidence/c3_demo_standalone.pdf`**: Official Firefox PDF printout from live execution on Qniverse JupyterLab showing cloud execution (`Job ID: 38070`, `Job ID: 38071`) and matching distributions.
- **`figures/`**: High-resolution 150 DPI vector-extracted PNG images of notebook cell outputs, circuit diagrams, and before/after comparison tables.
- **`src/qnvkit/`**: Full source code of the `qnvkit` engine (`optimize/`, `metrics/`, `sim.py`, `qsdk_adapter.py`).
- **`DOCUMENTATION_AND_ANALYSIS.md`**: Complete technical documentation, theoretical causal wire graph proofs, rewrite rules, empirical tables, and proofs.
- **`requirements.txt` / `pyproject.toml`**: Environment dependency specifications.

---

## Summary of Results

### Live Qniverse Cloud Execution Results (QACC_Cluster)

```
================================================================================
             1024-SHOT MEASUREMENT & PERFORMANCE COMPARISON
================================================================================
Metric                       | Unoptimized Circuit    | Optimized Circuit     
--------------------------------------------------------------------------------
Unitary Gate Count           | 15                     | 6                     
Circuit Scheduled Depth      | 11                     | 6                     
Gate Count Reduction         | -                      | 60.0%                 
Depth Reduction              | -                      | 45.45%                
--------------------------------------------------------------------------------
  * Unoptimized  ran on: official Qniverse QSDK (imported as 'qniverse') job Job(job_id='38070')
                 counts: {'000': 507, '111': 517}
  * Optimized    ran on: official Qniverse QSDK (imported as 'qniverse') job Job(job_id='38071')
                 counts: {'000': 492, '111': 532}
--------------------------------------------------------------------------------
Total variation distance between the two distributions: 0.0146 (sampling noise only if < 0.05)
================================================================================
VERDICT: matching measurement distributions with 60.0% fewer gates.
```

- **Gate Reduction:** 60.0% on Circuit 1, 53.85% on Circuit 2, 56.25% on Circuit 3, 68.0% on 4-qubit benchmark.
- **Barrier Guardrail:** Strictly preserved both $Z$ gates across the barrier (`Remaining Z gates: 2`).
- **Mathematical Equivalence:** Unitary process fidelity $= 1.00000000$.
- **Functional Immutability:** Input `QniverseCircuit` is completely untouched.
- **Detailed Report:** See [DOCUMENTATION_AND_ANALYSIS.md](DOCUMENTATION_AND_ANALYSIS.md).
