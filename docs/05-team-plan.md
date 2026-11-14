# 05 — Team Plan (12 hours)

Targets: **C1-01** (checkpoint 1, ~3 h), **C2-03** (checkpoint 2), **C3-03** (final). Weights 0.4 / 0.3 / 0.2.

## Roles (adjust to team size)
| Member | Owns |
|---|---|
| A | **C1-01** end to end: profiler, depth, decomposer, unsupported-operation report, tests |
| B | Shared QASM 2/3 parser and IR, then **C2-03** generators for Qiskit and Cirq |
| C | **C2-03** CUDA-Q generator, equivalence tests across frameworks, then **C3-03** tests |
| D | QSDK integration, **C3-03** rewrite rules, docs, demo, slides |

## Timeline
| Time | Goal |
|---|---|
| 0:00–0:30 | Read problem statements, ask the questions in `02-open-questions.md`, confirm QSDK access, install libraries in JupyterLab |
| 0:30–3:00 | **C1-01 complete** (all mandatory items, tests, sample input and output, metric definitions). Parser and IR started in parallel |
| **~3:00 CP1** | Present C1-01 |
| 3:00–6:00 | **C2-03**: parser validation, gate/measurement/register mapping, three generators, unsupported-construct report |
| **Mid CP2** | Present C2-03 (run generated code on each framework's simulator and show matching distributions) |
| 6:00–9:30 | **C3-03**: mandatory rules (identity removal, self-inverse cancellation, CX-CX), barrier/measurement guards, per-rule tests, before/after report |
| 9:30–10:30 | Stretch: C1-02 (MCX) or C2-04 only if everything above is done and tested |
| 10:30–12:00 | **Freeze code.** Docs, AI declaration, viva prep, submit |

## Rules for ourselves
- Something working beats something ambitious. Finish each problem's mandatory list before any extra.
- Commit every hour. Record AI usage as you go in `07-ai-usage.md`.
- Every member must be able to explain the depth definition, one rewrite rule and one equivalence check (viva is 10%).

## Submission checklist
- [ ] `08-team-info.md`: names, team name, registered Qniverse emails
- [ ] `03-technical-approach.md`: one section per problem, with references
- [ ] `04-performance-report.md`: real numbers
- [ ] Per problem: source, run instructions, sample input and output, tests and results, limitations
- [ ] `requirements.txt`, configs, `07-ai-usage.md`
- [ ] Slides plus a backup demo recording
