# 01 — Strategy: one problem per class

Sources: `hackathon_rules.pdf`, `Hackathon Problem set.pdf`. If announcements on the day differ, they win.
The earlier "verified compiler" open-innovation plan is **dropped**. We solve published problems only.

## Hard rules
- Working proof of concept required. Must be quantum and **use Qniverse / QSDK** (documented interfaces only: do not assume undocumented constructors or gate names).
- Only the registered Qniverse email. Open-source libraries allowed, but show them working with the QSDK.
- AI use must be declared (`07-ai-usage.md`). Submit all code and docs. C-DAC holds the rights to the documentation.

## Evaluation Weights & Criteria
**Criteria Breakdown:**
| Criterion | Weight | What it covers |
|---|---|---|
| **Product / Application Delivery** | **0.4 (40%)** | The actual working project, code quality, test suite, and QSDK integration |
| **Judges' Evaluations** | **0.3 (30%)** | Technical rigor, novelty, equivalence checks, and meeting all problem specifications |
| **Presentation & Viva-Voce** | **0.2 (20%)** | Visual before/after demo, defense of complexity, and answering judges' questions |

**Checkpoints & Problem Classes (from Rules §3):**
- **Class 1 (Checkpoint 1, ~3 h in):** 20% of class evaluation — *QC-C1-01*
- **Class 2 (Checkpoint 2, mid-event):** 30% of class evaluation — *QC-C2-03*
- **Class 3 (Final Checkpoint):** 50% of class evaluation — *QC-C3-03*

Product delivery (0.4) is the largest single scoring component: **every problem must have a working, non-crashing proof of concept**.

## Target Framework Versions
All generated code and transpilation targets must use the **latest stable versions**:
- **Qiskit:** `>= 1.0.0` (modern `qiskit.circuit` and `qiskit.transpiler` APIs, avoiding legacy `qiskit.execute`)
- **Cirq:** `>= 1.4.0` (standard `cirq.Circuit`, `cirq.Simulator`)
- **NVIDIA CUDA-Q:** `>= 0.8.0` / `>= 0.9.0` (standard `@cudaq.kernel` syntax)

## Our picks
| Class | Problem | Why |
|---|---|---|
| 1 | **QC-C1-01** Circuit profiling and limited basis-gate decomposition | Metric and depth code is reused by C3-03. Decomposition logic is reused by nothing risky. Well specified, so full marks are reachable. |
| 2 | **QC-C2-03** OpenQASM 3.0 transpiler to Qiskit, Cirq, CUDA-Q | The QASM parser is shared with the other problems, and cross-framework equivalence testing makes a strong demo. |
| 3 | **QC-C3-03** Circuit optimisation using QSDK | Builds on the C1-01 profiler and IR. The mandatory scope is small, so we spend the effort on rigorous per-rule tests. |

**Rejected, and why**
- C1-02 (MCX): good fallback if C1-01 is finished early, since it is self-contained. Do it as a stretch.
- C2-01 (S-AES): large (key expansion, MixColumns over GF(2^4), 3 input configurations, ancilla cleanup). High risk for the time.
- C2-02 (unitary synthesis): doable, but it adds a numerical-methods surface with no code reuse.
- C2-04 (QASM to QniverseCircuit): cheap by-product once the C2-03 parser exists. Do it as a stretch.
- C3-01 (JS simulator with noise): big (new language, full noise stack). C3-02 (noise library): large config and channel surface. Both are bigger than C3-03 for a 0.2 weight.
- QC-NI1 (new idea): not pursued.

## Shared architecture (one codebase, three problems)
```
OpenQASM 2/3 ──► parser ──► internal IR / QniverseCircuit ──┬─► profiler + basis decomposer   (C1-01)
                                                             ├─► code generators + verifier    (C2-03)
                                                             └─► rewrite-rule optimiser        (C3-03)
```
The metric definitions (depth by earliest-layer schedule, gate counts) live in **one module** and are imported by C1-01 and C3-03, so before/after numbers are consistent.

## Rules for ourselves
- Non-mutating everywhere: every function returns a new circuit and leaves the input unchanged. Test it.
- Never silently emit an invalid circuit: report unsupported operations explicitly.
- Document metric definitions and limitations in each problem's write-up. The problem sets ask for them.
- Equivalence evidence for each problem: matrix or statevector up to global phase, or distribution comparison.

## How we stand out (many teams will pick the same problems)
Everyone will meet the mandatory lists. We win on rigour and evidence beyond them.

**Shared evidence engine (all three problems):** every decompose, transpile or optimise step is auto-checked against the original (unitary or statevector up to global phase; distributions when measurements exist); property-based fuzzing on random circuits; an immutability test (hash of input before and after); a one-command demo that regenerates all results; real use of documented QSDK calls.

**C1-01:** auto-verified decomposition rule table for several bases ({Rx,Ry,Rz,CX}, {H,T,CX}, {U3,CX}, {SX,Rz,CX}); cheapest Euler choice per basis plus rotation merging after decomposition; known-good counts (Toffoli in 6 CX, SWAP in 3 CX); extra metrics (critical path, T-count, T-depth, parallelism) with every definition documented; unsupported reports that give the reason.

**C2-03:** real OpenQASM 3 parser (official grammar or the `openqasm3` package), not regexes; `stdgates.inc`, custom gates, parameter expressions, unrolled loops, simple `if`, `ctrl@`/`inv@` where supported; line:column diagnostics; automatic cross-framework conversion matrix (Qiskit, Cirq, CUDA-Q, pass/fail with distribution difference) with bit-order handled and documented; also emit a `QniverseCircuit` (C2-04 as a free bonus).

**C3-03:** mandatory rules exact and independently toggleable, with negative tests (barrier, measurement or intervening gate must block a rewrite); cheap extras (S·S† and T·T† cancellation, Rz merging, commutation-aware cancellation, run to fixed point); 1,000-circuit fuzz equivalence test; honest comparison against Qiskit's own passes, stating where we don't win.

**Ordering:** mandatory list and tests first, extras second. No ZX-calculus or other risky features. Be early at every checkpoint. Rehearse the viva (depth definition, one rewrite, one equivalence check).
