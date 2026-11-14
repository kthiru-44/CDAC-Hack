# Fix plan for QC-C2-03 (OpenQASM 3 transpiler)

Review date: 14 Nov 2026. The code is in `src/qnvkit/qasm/parser3.py` and `src/qnvkit/transpile/`.
All findings below were reproduced with `tools/c2_probe.py` (run it with `.venv312/bin/python -B tools/c2_probe.py`;
that venv has qiskit, qiskit-aer, cirq and cudaq installed). The probe transpiles 16 valid programs to all four
targets, executes the generated code, compares statevectors with the reference simulator, and feeds 11 invalid inputs.

**Goal:** every probe program must end as "status SUCCESS/WARNING, compiles, runs, fidelity 1.0" or an explicit
unsupported report; every invalid input must raise `QASMError` with line and column. Never emit code that does not run.

## Facts about the real QSDK (qniverse 1.0.6, learned in C1-01; do not re-guess)
- Both `import Qniverse` and `import qniverse` work in Qniverse JupyterLab (Python 3.11.6).
- `QniverseCircuit()` takes **no arguments**.
- `qc.add_gate(gate_object, *bit_objects)`: gate objects from `Qniverse.gates` (`h`, `rx(0.5)`), operands `q[i]`. Strings and ints are rejected.
- `barrier`: `add_gate` accepts 1 or 2 qubits, `qasm()` rejects 1. So a barrier is exactly two operands: start and end qubit of a span.
- `qniverse.api` has **no `run`**; never import it in generated code.
- `add_conditional_gate(creg, value, gate, *qubits)` is register-level only; gate cannot be measure/barrier/reset.
- Gate set: the 40 names in `qnvkit.gates.GATE_REGISTRY`. `sx`, `sxdg`, `cu`, `u` are not QSDK gates.
- The local stand-in (`src/qnvkit/shim/Qniverse/`) enforces the same rules. Do not loosen it.

## A. Parser bugs (`parser3.py`)
| # | Finding (probe name) | Fix |
|---|---|---|
| A1 | Custom gate bodies map to wrong qubits (`gatedef`: index out of range). `_inline_custom_gate` uses a fake `__flat__` register but `_qubit_to_flat` adds the offset of all real registers. | In `_qubit_to_flat`, return `idx` directly for `__flat__` (after a range check). |
| A2 | Modifiers are wrong (`mods`). `ctrl @` only renames x, z, cx; any other gate keeps its name and gains a qubit (corrupt op). `pow` returns early and drops other modifiers. Modifiers on custom gates are silently ignored. `negctrl` unhandled. | Rewrite modifier handling as a transformation over a list of ops, applied innermost modifier first: `inv` = reverse the list and invert each op; `pow(k)` = repeat (integer k ≥ 0; negative = inv then repeat; non-integer only by scaling the angle of rx/ry/rz/p/u1/cp/crx/cry/crz); `ctrl(n) @` = prepend control qubits and map to the controlled gate (x→cx→ccx→c3x→c4x→c5x, y→cy, z→cz, h→ch, s→cs, t→ct, sdg→csdg, tdg→ctdg, p→cp, u1→cu1, rx→crx, ry→cry, rz→crz, u3→cu3, swap→cswap); `negctrl` = X on the control before and after. Anything without a controlled/inverse form → `QASMError` with location. For a custom gate: inline into a temporary list, then apply modifiers. Control qubits are the first `n` operands. Inverse table must include: self-inverse (id,x,y,z,h,cx,cy,cz,ch,swap,ccx,cswap,c3x–c5x), s↔sdg, t↔tdg, sx↔sxdg, cs↔csdg, ct↔ctdg, negate angle for single-angle gates, `u3(θ,φ,λ)⁻¹ = u3(−θ,−λ,−φ)` (same for cu3), `u2(φ,λ)⁻¹ = u3(−π/2,−λ,−φ)`, `cu(θ,φ,λ,γ)⁻¹ = cu(−θ,−λ,−φ,−γ)`. |
| A3 | `qubit q;` and `bit c;` without a size fail (`single`). | Treat as size 1. |
| A4 | `gphase(x);` fails (`gphase`). | Accept and ignore (global phase is unobservable); add nothing to the circuit. Reject it under `ctrl @`. |
| A5 | `if (c[0] == 1)` loses the bit index and becomes `c == 1` (wrong for registers larger than 1 bit). `!=` crashes the lexer with a plain `ValueError`. | Keep the index: when an index is given and the register has more than one bit, store an `ir.Condition(register, value, index)` in `op.condition`; otherwise keep the `(name, value)` tuple. Validate value fits the register. Any operator other than `==` → `QASMError` (unsupported, with location). Lexer errors must surface as `QASMError` with line/col. |
| A6 | Invalid input not rejected properly: index out of range and classical index out of range raise `IndexError`; wrong qubit count (`cx q[0];`) and missing parameter (`rx q[0];`) raise `IndexError` from a generator; unknown gate `foo` is accepted by the parser; duplicate operands (`cx q[0], q[0]`) accepted; empty source accepted. | Validate in the parser and raise `QASMError` with line/col for each: known gate (stdgates + QSDK names + user gates), operand count, parameter count, distinct operands, index ranges, non-empty program with at least one statement. |
| A7 | Gate aliases leak into the IR (`u`, `phase`, `cphase`, `cnot`, `toffoli`, `CX`, `U`). | Normalise in the parser: U/u→u3, phase→p, cphase→cp, cnot/CX→cx, toffoli→ccx. |
| A8 | `for` loops with a negative step iterate wrongly. | `range(start, end ± 1, step)` by sign; step 0 → `QASMError`. |
| A9 | `qasm/expr.py` evaluates with `eval`; the character whitelist still allows attribute access such as `(1).__class__`. | Reject any expression containing `__` or an attribute access (`.` followed by a letter). Add `tau`, `euler`, `ln`, `log`, `arcsin/arccos/arctan`, `floor`, `ceiling`, `mod`-free. |

## B. Reference simulator / gate registry
- `allstd`: reference simulation fails for `cu` ("not one of the 40 documented gates"). Add `cu(θ,φ,λ,γ)` to `STDGATES_REGISTRY` with matrix `controlled(e^{iγ}·U3(θ,φ,λ))`. Keep `DOCUMENTED_GATE_NAMES` at exactly the 40 QSDK gates (C1-01 depends on it).
- Add a rule in `decompose/rules.py`: `cu(θ,φ,λ,γ) c,t → p(γ) c; cu3(θ,φ,λ) c,t`. `sx`/`sxdg` already have matrices, so Euler synthesis handles them.
- `sim.compute_statevector` ignores conditions and mid-circuit measurement. That is fine for static circuits only; see D.
- `src/qnvkit/shim/Qniverse/api.py::run` still assumes qubit 0 is the most significant bit of the statevector index, but `sim` now defaults to little-endian (qubit q = bit q). Fix the bit extraction to `(s >> q) & 1` and add a test (`x q[0]` on 2 qubits must give classical bit 0 = 1).

## C. Code generators (`transpile/*.py`)
Shared problems:
1. **Comments emitted as code.** Cirq: `circuit.append(# Barrier on ...)` is a syntax error (`barrier`, `allstd`). Any generator: a conditional whose body is only a comment is a syntax error.
2. **Unsupported gates** produce a comment line and status ERROR, but the rest of the program is still emitted as if valid.
3. Four copies of the same operand/condition formatting.

Fix: add `transpile/_common.py` with
- `prepare_ops(circuit, native_gates, fallback_basis, report)`: returns the op list for a target. A gate not in `native_gates` is expanded with the C1 decomposer (`qnvkit.decompose.decomposer._expand_op_recursive(op, fallback_basis)`); record one note per gate type ("u3 emitted as rz·ry·rz, equal up to global phase"). If it cannot be expanded → `report.add_unsupported(..., line, col)` and the op is skipped.
- `condition_terms(circuit, op)`: returns `[(flat_clbit, required_bit), ...]` for tuple and `Condition` forms.
- `py_name(name)`: safe Python identifier for a register (avoid keywords and names used by the generated code: `qc`, `np`, `circuit`, `cirq`, `cudaq`, `sympy`, `build_circuit`).
- Add a `notes: List[str]` field to `TranspilerReport` (does not change status), for exact-up-to-global-phase rewrites.
- If any unsupported construct was recorded, status is `ERROR` and the generated code must still be valid Python.

Per target:
- **Qiskit (≥ 1.0):** add `cu2` (`qc.cu(np.pi/2, φ, λ, 0, c, t)`); everything else native. Conditions: `with qc.if_test((creg, value)):` or `((creg[i], value))`.
- **Cirq (≥ 1.4):**
  - Barrier → nothing emitted (note in report).
  - `u3`, `u2`, `cu3`, `cu2`, `cu` → via `prepare_ops` with basis `{rz, ry, p, cx}` (currently `cond_u3` crashes: a generator object is passed to `ClassicallyControlledOperation`).
  - Conditions are broken (`cond_bit`, `cond_reg`: "Measurement key c missing"): keys are per bit (`c_0`), and `KeyCondition` only tests truthiness. Use `op.with_classical_controls(sympy.Eq(sympy.Symbol('c_0'), 1), ...)`, one term per bit of the condition. Track which classical bits have been measured so far: an unmeasured bit is 0, so drop a "must be 0" term and skip the op with a warning if a "must be 1" term can never hold.
  - `__main__`: print counts as bitstrings over all keys (document the order), not the histogram of the first key only. Circuits without measurement: print the statevector (already done) and do not call `run`.
- **CUDA-Q (≥ 0.9):** the current output is not valid kernel code. cudaq is installed in `.venv312`, so **execute what you generate**.
  - Inside `@cudaq.kernel`, gates are bare names: `h(q[0])`, `x.ctrl(c, t)`, `mz(q)`, `reset(q)`, `swap(a, b)`; not `cudaq.h(...)`.
  - `p`/`u1` → `r1(angle, q)`; `cp`/`cu1`/`cphase` → `r1.ctrl(angle, c, t)`. **Currently `cp` is emitted as `rz.ctrl`, which is a different gate (wrong relative phase).** `crz` → `rz.ctrl`.
  - `sdg` → `s.adj(q)` (or `sdg`), `tdg` → `t.adj(q)`; `cs`/`ct` → `s.ctrl`/`t.ctrl`; `csdg`/`ctdg` → `r1.ctrl(∓π/2 or ∓π/4, ...)`; `u3` → `u3(θ, φ, λ, q)`; `cu3` → `u3.ctrl(...)`; `cswap` → `swap.ctrl(c, a, b)`; multi-control → `x.ctrl(c0, c1, ..., t)`; `id` → nothing; `sx`, `cu`, `cu2`, `u2` → `prepare_ops`.
  - Measurement: `c_0 = mz(q[0])`. Conditions: nested `if c_0:` / `if not c_0:` (verify which forms the installed cudaq accepts and use those); same measured-bit tracking as Cirq.
  - Remove the `@cudaq.kernel if cudaq is not None else ...` trick; generated code simply imports cudaq.
- **Qniverse QSDK:**
  - `QniverseCircuit()` with no argument (currently passes a name: `TypeError` on every program).
  - Header: `try: from Qniverse... except ImportError: from qniverse...`; import only `QniverseCircuit`, registers and `gates`. No `api` import. No fallback to `qnvkit` (generated code must be standalone).
  - Non-QSDK gates (`sx`, `sxdg`, `cu`) → `prepare_ops` with basis `{u3, cx}`.
  - Bit-level condition on a register larger than 1 bit → unsupported (report with line/col); conditional measure/reset → unsupported.
  - Barrier: two operands (span) per register, one-qubit barrier omitted with a note (already done; keep).

## D. Verification (`transpile/verify.py`)
- **CUDA-Q is reported as `executed: True, "kernel verified"` without running anything.** Replace with a real run: `cudaq.get_state` for static circuits, compare with the reference. Determine CUDA-Q's index order with a one-gate calibration circuit at runtime and say so in the report. If cudaq is missing: `executed: False`.
- Cirq statevector: pass an explicit `qubit_order` built in declaration order; the default order sorts by name and is wrong for registers declared out of alphabetical order.
- Static circuits (no condition, no mid-circuit measurement, no reset): statevector fidelity vs reference for Qiskit, Cirq, CUDA-Q, and for the QSDK route (`build_circuit()` → `qsdk_adapter.from_qniverse` → reference simulator).
- Dynamic circuits: the reference simulator cannot model them. Sample Qiskit (Aer, if installed) and Cirq (and CUDA-Q) with a fixed seed and compare the count distributions pairwise by total variation distance (state the shot count and tolerance in the report). Normalise all to one bitstring convention (classical bit 0 right-most) and document it.
- A framework that is not installed, or a check that was not run, must be reported as not run. `equivalence_verified` stays `None` in that case.
- `transpile()` must never crash because verification failed; record the error in the report.

## E. Tests (add to `tests/`)
- Turn `tools/c2_probe.py` into pytest cases: each valid program × each target compiles; with `pytest.importorskip` for qiskit/cirq/cudaq the generated code is executed and fidelity ≥ 1 − 1e-9 (static) or TVD below tolerance (dynamic).
- Parser unit tests for A1–A9, including: custom gate with parameters on non-zero qubits; `ctrl @ rz`, `inv @ u3`, `pow(3) @ t`, `ctrl @ custom` rejected or correct; each invalid input raises `QASMError` with a line number.
- QSDK generator output executed against the local stand-in for every probe program.
- Shim bit-order test (section B).
- Keep the whole suite green on `.venv39` (frameworks absent → skips, not failures) and `.venv312`.

## F. Demo and docs
- `examples/c2_demo.py` and `notebooks/c2_demo.ipynb`: show (1) one QASM 3 program with a custom gate, a modifier, a loop, measurement and a condition; (2) generated code for the three targets; (3) the structured report; (4) the equivalence table (what was executed, fidelity/TVD, what was not run); (5) two invalid inputs with line:column diagnostics; (6) one unsupported construct.
- Rebuild `notebooks/c2_demo_standalone.ipynb` with `python tools/build_standalone_notebook.py`. In Qniverse JupyterLab (Python 3.11) the first cell may `pip install cirq-core` if cirq is missing; qiskit is expected to be present; cudaq is optional and reported as not run when absent.
- Write `docs/c2-03-user-guide.md`: supported QASM 3 subset, gate mapping table per target, bit-order conventions, framework versions tested (print the actual installed versions), known limitations.
- Update `docs/07-ai-usage.md`.

## Order of work
1. A1, A2, A6, A7 and B (correctness of the IR). 2. C (`_common.py`, then Qniverse, Cirq, CUDA-Q, Qiskit). 3. D. 4. E alongside each step. 5. F.
Run `tools/c2_probe.py` after each step. Do not push; commit locally with clear messages.

## Out of scope
C1-01 behaviour (its 37-gate × 11-basis test must stay green), C3-03, and any live job submission.
