# 05 — Team Plan (12 hours)

## Roles (adjust to team size)
| Member | Main role | Owns |
|---|---|---|
| A | Class 1 and 2 problems, then benchmarks | Checkpoint 1 and 2 scores, `benchmarks/`, `04-performance-report.md` |
| B | Optimisation passes | `passes/`, `pipeline.py` |
| C | Converter and multi-simulator verifier | `convert.py`, `verify.py`, `simulators.py`, `discrepancy.py` |
| D | Qniverse integration, profiling, demo and docs | `qniverse.py`, `profile.py`, `noise.py`, `notebooks/demo.ipynb`, `report.py`, slides |

## Timeline
| Time | A | B | C | D |
|---|---|---|---|---|
| 0:00–0:30 | Read problem statements | Read problem statements | Set up env (qiskit, pyzx) | Log into Qniverse, ask C-DAC reps the questions in `02` |
| 0:30 | **Pitch QOpt, the verified compiler (open innovation), to the judges** | | | |
| 0:30–3:00 | Solve Class 1 | Peephole, merge, commutation passes | QASM <-> Qiskit/Cirq/CUDA-Q converters + unitary verifier | Qniverse SDK: submit a circuit to named backends, read results; profiler |
| **~3:00 CP1** | Present Class 1 | Show QOpt v0 to judges for feedback | | |
| 3:00–6:00 | Solve Class 2 | Resynthesis + PyZX pass | Differential testing harness over 5-6 simulators (statevector, then statistical), discrepancy report | ESP noise-aware cost; before/after runs on Qniverse noisy simulator |
| **Mid CP2** | Present Class 2 | Show QOpt v1 | | |
| 6:00–9:00 | Benchmark suite vs Qiskit O3, pytket, PyZX | Pipeline levels O0–O3, noise-aware selection, verify after every pass | Stabilizer verifier, conversion matrix (framework pair x simulator), scaling runs | Demo notebook, HTML report with certificate |
| 9:00–10:30 | Performance report | Bug fixes, edge cases | Complexity table | Slides, demo rehearsal |
| 10:30–12:00 | **Freeze code.** Docs, AI declaration, viva prep, submit | | | |

## Scope guard
- First cut: **3-4 frameworks and 5-6 simulators**, not all 7 and all 25.
- If the Qniverse SDK cannot submit to named backends, run the open-source engines (Aer, Cirq, Qulacs, QuEST, CUDA-Q)
  inside the Qniverse JupyterLab, and use Qniverse backends for the headline demo only if the API works.
- Fallback: if a published Class 3 problem lands in domain 2 or 3, map onto it.

## Rules for ourselves
- **Something working beats something ambitious.** Have an end-to-end pipeline (even a basic one) by hour 3.
- Commit to git every hour.
- Note AI usage as you go in `07-ai-usage.md`, not at the end.
- Every member must be able to explain the ESP formula, one pass, and how verification works (viva is 10%).

## Submission checklist
- [ ] `08-team-info.md`: names, team name, registered Qniverse email IDs
- [ ] `03-technical-approach.md` finalised, with references
- [ ] `04-performance-report.md` filled with real numbers and plots
- [ ] Working demo runs on Qniverse / SDK
- [ ] All source, `requirements.txt`, configs
- [ ] `07-ai-usage.md` complete
- [ ] Slides, plus a backup demo recording in case the network fails
