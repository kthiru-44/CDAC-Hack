# 02 — Qniverse: what exists and what QOpt adds

Based on the public docs at https://qniverse.in/docs/ (read 14 Nov 2026). The **QSDK page was empty**
(a redirect stub), so confirm SDK details with the C-DAC representatives on the day.

## What Qniverse already has
**Building circuits**
- Drag-and-drop **Circuit Composer** (custom gates up to 3-letter names, undo/redo, registers).
- **Code Editor:** real-time code generation for **QASM, Cirq, Qiskit, CudaQ, Qulacs, QuEST and editable Qiskit**.
  OpenQASM 2.0 is editable and syncs back to the composer. The Qiskit, Cirq and CudaQ views are read-only.
- "Launch Notebook" → JupyterLab environment.

**Simulators**
- **CPU (QACC-Cluster):** qasm_Simulator, aer_Simulator_{statevector, density_matrix}, aer_simulator_{stabilizer, matrix_product_state},
  cirq_Simulator, cirq_clifford_simulator, nvidia_cudaq_stabilizer_simulator, quest_simulator, qsimcirq_simulator,
  qulacs_multicpu_simulator, cdac_photonics_simulator, qniverse_statevector_simulator.
- **CPU (Param Utkarsh):** a subset of the above.
- **GPU:** Aer_StateVector_simulator_GPU, Nvidia_cudaq_statevector_simulator, qsimcirq cuQuantum, Aer tensor network GPU,
  nvidia_cudaq_tensor_network_simulator, nvidia_cudaq_mps_simulator.
- **FPGA:** FPGA simulator and FPGA_dm_simulator (noisy, up to 12 qubits).
- **Vector card:** up to 27 qubits. csim_vector_simulator up to 32.

**Noise modelling**
- Circuits are **auto-transpiled by the Qiskit transpiler into {Rx, Ry, Rz, CX}**.
- Noise parameters: SPAM bit-flip *p*, depolarizing *p*, thermal relaxation T1/T2/Tg (µs), coherent over/under-rotation ε (degrees).

**Hardware**
- IBM (user's own API key), Rigetti, SuperStaq, QI.

## Gaps QOpt fills
| Gap in Qniverse | What QOpt adds |
|---|---|
| No user-facing optimisation control (only a fixed Qiskit transpile for noise) | An optimiser with selectable passes and levels, plus before/after metrics |
| No check that a transformed circuit is still correct | An **equivalence certificate** for every optimisation |
| Optimisation (if any) targets depth/gate count, not noise | A **noise-aware cost** using Qniverse's own noise parameters (p, T1, T2, Tg, ε) |
| No resource or profiling report | Depth, gate counts, 2-qubit count, critical path, estimated success probability |
| No comparison against established compilers | Benchmark table vs Qiskit O3, pytket and PyZX |
| Code views for Qiskit/Cirq/CudaQ are one-way and read-only | **Round-trip converters** (framework code to QASM and back) |
| No check that frameworks or simulators agree on a circuit's result | **Multi-simulator differential testing** with a discrepancy report |
| Fixed {Rx, Ry, Rz, CX} basis | **Target-aware** rewriting for each backend's native gate set |

## Integration point
```
Qniverse composer ──► OpenQASM 2.0 ──► QOpt ──► optimised OpenQASM 2.0 ──► Qniverse editor
                                                                             └─► Qiskit / Cirq / CudaQ / Qulacs / QuEST
```

## Questions for the C-DAC representatives (first hour)
1. Is there a Python SDK (package name?) for submitting circuits and choosing backends from JupyterLab?
2. Can we pip-install PyZX, pytket and qiskit inside the Qniverse JupyterLab?
3. Can we set noise-model parameters (p, T1, T2, ε) from code, or only from the UI?
4. Which basis gates and connectivity does each hardware backend expose (IBM, Rigetti, QI)?
5. Is there an API for getting circuits in and out (QASM upload/download)?
