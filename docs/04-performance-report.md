# 04 — Performance Evaluation Report (Deliverable #3)

> Template. Fill in the numbers from `benchmarks/` runs. Rules §6.3 asks for time and memory needs,
> computational complexity, and circuit depth and gate count at scale.

## 1. Setup
- Machine: (CPU, RAM) / Qniverse JupyterLab
- Qniverse backends used: e.g. `aer_Simulator_density_matrix`, `FPGA_dm_simulator`, `qniverse_statevector_simulator`
- Noise parameters: p₁ = __, p₂ = __, T1 = __ µs, T2 = __ µs, Tg = __ µs, p_SPAM = __
- Shots: 1024 (Qniverse default)

## 2. Circuit metrics: before and after
| Circuit | n | Depth before → after | Total gates before → after | CX before → after | ESP before → after | Verified |
|---|---|---|---|---|---|---|
| Grover | 4 | | | | | ✓ |
| QFT | 8 | | | | | ✓ |
| Ripple-carry adder | 6 | | | | | ✓ |
| QAOA (MaxCut) | 6 | | | | | ✓ |
| QASMBench … | | | | | | |

## 3. Comparison with established compilers (CX count / depth)
| Circuit | Original | Qiskit O3 | pytket FullPeephole | PyZX full_reduce | **QOpt** |
|---|---|---|---|---|---|
| | | | | | |

Summary line: "QOpt beats Qiskit O3 on __ of __ circuits, average CX reduction __%."

## 4. Measured on Qniverse (noisy simulation)
| Circuit | Success prob. original | Success prob. optimised | Gain |
|---|---|---|---|
| | | | |

Include histogram plots: `benchmarks/results/*.png`.

## 5. Scaling (n = 3 … 14)
- Plot: optimisation time against n, and memory against n.
- Plot: CX count against n, original vs QOpt.
- Fitted complexity: time ≈ O(__), R² = __.

## 6. Computational complexity
| Component | Time | Memory |
|---|---|---|
| Profiling (DAG depth, counts) | O(g) | O(g) |
| Peephole / merge passes | O(g) per sweep, ≤ s sweeps → O(s·g) | O(g) |
| Commutation cancellation | O(g·k) | O(g) |
| ZX simplification | polynomial, roughly O(V³) worst case | O(V+E) |
| ESP cost evaluation | O(g + n·d) | O(n) |
| Verification: full unitary | O(g·4ⁿ) | O(4ⁿ), feasible to n ≈ 12 |
| Verification: random states (k states) | O(k·g·2ⁿ) | O(2ⁿ) |
| Verification: stabilizer (Clifford) | O(g·n) | O(n²) |

*g = gate count, n = qubits, d = depth, k = random states or window size, V/E = ZX graph size.*

## 7. Limitations
- Full-unitary verification limited to about 12 qubits. Beyond that the check is probabilistic.
- The ESP model is an approximation (no crosstalk, no correlated noise).
- ZX extraction can sometimes *increase* CX count. The pipeline keeps the better candidate.
